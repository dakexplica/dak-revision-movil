#!/usr/bin/env python3
"""revisar.py — mide una página web en muchos dispositivos a la vez.

Abre la página como la abriría un iPhone, un Android, un plegable, un iPad, una
tableta Android y varias compus (Mac y Windows), y en cada uno:
  1. baja hasta el final (para que carguen las fotos "lazy") y vuelve arriba,
  2. toma captura de lo que se ve al abrir (pantalla.png) y de la página entera (completa.png),
  3. corre auditoria.js (desbordes, textos cortados, botones chicos, letra chica,
     campos que hacen zoom en iPhone, barras fijas que tapan, 100vh, hover, fotos, video, 3D…),
  4. apunta errores de consola, archivos que no cargan y el peso de la página,
  5. marca en rojo sobre la captura completa dónde está cada error (marcado.png).
Al final arma hoja.png (todas las pantallas lado a lado) e informe.md en español.

Uso:
  python3 revisar.py <url | archivo.html | carpeta> [opciones]

  --dispositivos completo|rapido|telefonos|tabletas|compus|mac|moviles|iphone,android,...
                         (por defecto: completo = 15 dispositivos)
  --salida DIR           carpeta donde guardar todo (por defecto: ./revision-movil/<fecha>)
  --ruta /productos      página dentro del sitio (se puede repetir: --ruta / --ruta /tienda)
  --esperar 1500         milisegundos extra tras cargar (animaciones de entrada, 3D)
  --red-lenta            simula 4G lento en los teléfonos (mide si carga a tiempo)
  --motor auto|chromium|webkit   auto = webkit (motor de Safari) para iPhone/iPad si está instalado
  --sin-scroll           no bajar la página antes de capturar (páginas con scroll secuestrado)
  --alto-max 14000       corta la captura completa a este alto (px CSS)
  --estado sesion.json   entrar con la sesión guardada por sesion.py (login, tienda privada, preview)
  --cookies rechazar     pulsar "Rechazar" en el banner de cookies antes de medir (míralo primero CON banner)
  --esperar-a "<js>"     esperar a que esa expresión sea verdadera (3D o CDN lentos), además de --esperar

Siempre termina con código 0: un "error" aquí es un hallazgo, no una falla del script.
"""
import argparse
import datetime as dt
import functools
import http.server
import json
import os
import re
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urljoin, quote

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dispositivos import DISPOSITIVOS, resolver, contexto_playwright, args_navegador  # noqa: E402

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    raise SystemExit("Falta Playwright para Python: pip3 install playwright && python3 -m playwright install chromium")

AUDITORIA_JS = (AQUI / "auditoria.js").read_text(encoding="utf-8")

# Botones de "rechazar" de los banners de cookies más comunes (Shopify, OneTrust, Cookiebot, CookieYes,
# Complianz, Iubenda) + textos genéricos. Siempre la opción más privada.
RECHAZAR_COOKIES_JS = """() => {
  const sels = ['#shopify-pc__banner__btn-decline', '#onetrust-reject-all-handler', '#CybotCookiebotDialogBodyButtonDecline',
    '.cky-btn-reject', '.cmplz-deny', '.iubenda-cs-reject-btn', '[data-cookie-reject]', '[data-action="reject"]'];
  for (const s of sels) { const b = document.querySelector(s); if (b && b.offsetParent !== null) { b.click(); return s; } }
  const textos = /^(rechazar( todas?| todo| cookies)?|denegar|no aceptar|solo (las )?necesarias|reject( all)?|decline( all)?|only necessary)$/i;
  for (const b of document.querySelectorAll('button, a, [role="button"]')) {
    if (b.offsetParent !== null && textos.test((b.innerText || '').trim())) { b.click(); return (b.innerText || '').trim(); }
  }
  return null;
}"""


def esperar_listo(page, args, consola):
    """--esperar-a: espera a que una expresión JS sea verdadera (más fiable que un tiempo fijo con 3D/CDN lentos)."""
    if not getattr(args, "esperar_a", None):
        return
    try:
        page.wait_for_function(args.esperar_a, timeout=args.timeout * 1000)
    except Exception:
        consola.append(f"--esperar-a no se cumplió en {args.timeout}s: {args.esperar_a}")


def manejar_cookies(page, args):
    if getattr(args, "cookies", "dejar") != "rechazar":
        return None
    try:
        r = page.evaluate(RECHAZAR_COOKIES_JS)
        if r:
            page.wait_for_timeout(600)
        return r
    except Exception:
        return None

SCROLL_JS = """async () => {
  const paso = Math.max(300, Math.floor(window.innerHeight * 0.8));
  let y = 0, vueltas = 0;
  while (vueltas < 40) {
    y += paso; window.scrollTo(0, y); vueltas++;
    await new Promise(r => setTimeout(r, 140));
    if (y >= document.documentElement.scrollHeight - window.innerHeight) break;
  }
  await new Promise(r => setTimeout(r, 300));
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 450));
}"""

PESO_JS = """() => {
  const rs = performance.getEntriesByType('resource');
  const nav = performance.getEntriesByType('navigation')[0];
  let bytes = (nav && nav.transferSize) || 0;
  const porTipo = {};
  for (const r of rs) {
    const b = r.transferSize || r.encodedBodySize || 0;
    bytes += b;
    const t = r.initiatorType || 'otro';
    porTipo[t] = (porTipo[t] || 0) + b;
  }
  return { bytes, peticiones: rs.length + 1, porTipo,
           cargaMs: nav ? Math.round(nav.loadEventEnd - nav.startTime) : null };
}"""


# ---------------------------------------------------------------- servidor local
class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def _puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def servir(carpeta: Path) -> str:
    """Sirve una carpeta local por http (file:// rompe módulos JS, fetch y fuentes)."""
    puerto = _puerto_libre()
    handler = functools.partial(_Silencioso, directory=str(carpeta))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", puerto), handler)
    srv.handle_error = lambda *a: None  # el navegador corta descargas de video a medias: no es un error
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{puerto}/"


def resolver_objetivo(objetivo: str):
    if re.match(r"^https?://", objetivo):
        return objetivo, None
    p = Path(objetivo).expanduser().resolve()
    if p.is_dir():
        return servir(p), p
    if p.is_file():
        base = servir(p.parent)
        return base + quote(p.name), p.parent
    raise SystemExit(f"No encuentro '{objetivo}' (ni URL, ni archivo, ni carpeta).")


# ---------------------------------------------------------------- utilidades
def slug(t: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "inicio"


def kb(n):
    if n is None:
        return "?"
    return f"{n/1024/1024:.1f} MB" if n > 1024 * 1024 else f"{n/1024:.0f} KB"


def webkit_disponible(pw):
    try:
        b = pw.webkit.launch()
        b.close()
        return True
    except Exception:
        return False


def fuente(tam):
    from PIL import ImageFont
    for f in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"]:
        try:
            return ImageFont.truetype(f, tam)
        except Exception:
            pass
    return ImageFont.load_default()


COMPLETA_PREP_JS = """() => {
  const fijos = [...document.querySelectorAll('body *')].filter(e => {
    const p = getComputedStyle(e).position; return p === 'fixed' || p === 'sticky'; });
  fijos.forEach(e => e.setAttribute('data-rm-fijo', e.style.visibility || '__'));
  return { alto: document.documentElement.scrollHeight, vista: window.innerHeight, ancho: window.innerWidth };
}"""
COMPLETA_FIJOS_JS = """(ocultar) => document.querySelectorAll('[data-rm-fijo]').forEach(e => {
  if (ocultar) e.style.visibility = 'hidden';
  else { const v = e.getAttribute('data-rm-fijo'); e.style.visibility = v === '__' ? '' : v; e.removeAttribute('data-rm-fijo'); }
})"""


def captura_completa(page, destino: Path, alto_max: int, sin_scroll=False):
    """Página entera pegando capturas de pantalla una debajo de otra.
    NO se usa full_page de Playwright: en modo celular de Chromium, full_page apaga la emulación táctil
    (después de la captura (hover: hover) pasa a ser true) y la imagen enseña estilos de compu.
    Las barras fijas solo aparecen en el primer tramo (si no, se repetirían en cada pantalla)."""
    from PIL import Image
    import io
    if sin_scroll:
        page.screenshot(path=str(destino), scale="css", timeout=30000)
        return
    info = page.evaluate(COMPLETA_PREP_JS)
    alto = min(int(info["alto"]), alto_max)
    vista = max(1, int(info["vista"]))
    lienzo = None
    y, n = 0, 0
    try:
        while y < alto and n < 60:
            page.evaluate(f"() => window.scrollTo(0, {y})")
            page.wait_for_timeout(160)
            real = int(page.evaluate("() => Math.round(window.scrollY)"))
            img = Image.open(io.BytesIO(page.screenshot(scale="css", timeout=30000))).convert("RGB")
            if lienzo is None:
                lienzo = Image.new("RGB", (img.width, alto), (255, 255, 255))
            lienzo.paste(img, (0, real))
            if n == 0:
                page.evaluate(COMPLETA_FIJOS_JS, True)
            n += 1
            if real + vista >= alto:
                break
            y = real + vista
    finally:
        page.evaluate(COMPLETA_FIJOS_JS, False)
        page.evaluate("() => window.scrollTo(0, 0)")
    if lienzo is not None:
        lienzo.save(destino)


# ---------------------------------------------------------------- una revisión
def revisar_dispositivo(pw, navegadores, clave, url, carpeta: Path, args):
    nombre, w, h, dpr, plat, tipo, _ = DISPOSITIVOS[clave]
    motor = "chromium"
    if plat == "ios" and args.motor in ("auto", "webkit") and navegadores.get("webkit"):
        motor = "webkit"
    if args.motor == "chromium":
        motor = "chromium"
    nav = navegadores[motor]
    ctx_opts = contexto_playwright(clave)
    if motor == "webkit":
        ctx_opts.pop("is_mobile", None) if tipo == "compu" else None
    if args.estado:
        ctx_opts["storage_state"] = args.estado
    ctx = nav.new_context(**ctx_opts)
    page = ctx.new_page()
    consola, fallidas = [], []
    from urllib.parse import urlparse
    host_pagina = urlparse(url).hostname or ""
    def _consola(m):
        if m.type != "error":
            return
        origen = urlparse((m.location or {}).get("url") or "").hostname or host_pagina
        tercero = origen and host_pagina and not (origen == host_pagina or origen.endswith("." + ".".join(host_pagina.split(".")[-2:])))
        consola.append(("[terceros: " + origen + "] " if tercero else "") + m.text[:300])
    page.on("console", _consola)
    page.on("pageerror", lambda e: consola.append(f"JS: {str(e)[:300]}"))
    criticas = []
    from urllib.parse import urlparse as _up
    _host = _up(url).hostname or ""
    _base = ".".join(_host.split(".")[-2:])
    CDN_PROPIOS = ("cdn.shopify.com", "cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com", "esm.sh", "ga.jspm.io")
    def _fallo(r):
        fallidas.append(f"{r.failure or 'falló'} {r.url[:160]}")
        h = _up(r.url).hostname or ""
        propio = h == _host or (_base and h.endswith("." + _base)) or h in ("127.0.0.1", "localhost") or h in CDN_PROPIOS
        # Esencial = el documento principal, o un script/CSS de la propia página o de su CDN.
        # Iframes de terceros (Shop Pay, Google, Facebook…) que el navegador bloquea NO son esenciales.
        es_doc_principal = r.resource_type == "document" and r.frame == page.main_frame
        if es_doc_principal or (r.resource_type in ("script", "stylesheet") and propio):
            criticas.append(f"{r.resource_type}: {r.url[:160]} ({r.failure or 'falló'})")
    page.on("requestfailed", _fallo)
    page.on("response", lambda r: fallidas.append(f"{r.status} {r.url[:160]}") if r.status >= 400 else None)

    if args.red_lenta and tipo == "telefono" and motor == "chromium":
        cdp = ctx.new_cdp_session(page)
        cdp.send("Network.enable")
        # "4G lento": ~1.6 Mbps bajada, 150 ms de latencia
        cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150,
                 "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})

    t0 = time.time()
    try:
        page.goto(url, wait_until="load", timeout=args.timeout * 1000)
    except PWTimeout:
        consola.append(f"La página no terminó de cargar en {args.timeout}s")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except PWTimeout:
        pass
    esperar_listo(page, args, consola)
    carga_s = round(time.time() - t0, 1)
    page.wait_for_timeout(args.esperar)
    manejar_cookies(page, args)
    if not args.sin_scroll:
        try:
            page.evaluate(SCROLL_JS)
        except Exception as e:
            consola.append(f"No se pudo recorrer la página: {e}")

    carpeta.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(carpeta / "pantalla.png"), scale="css", animations="disabled", timeout=30000)
    except Exception as e:
        consola.append(f"Captura de pantalla falló: {e}")

    try:
        datos = page.evaluate(AUDITORIA_JS, {"plataforma": plat, "ancho": w, "alto": h})
    except Exception as e:
        datos = {"hallazgos": [], "inventario": {}, "error": str(e), "ancho": w, "alto": h, "altoPagina": h}

    try:
        captura_completa(page, carpeta / "completa.png", args.alto_max, args.sin_scroll)
    except Exception as e:
        consola.append(f"Captura completa falló: {e}")

    try:
        peso = page.evaluate(PESO_JS)
    except Exception:
        peso = {}
    ctx.close()

    vacia = pantalla_vacia(carpeta / "pantalla.png")
    if criticas:
        datos.setdefault("hallazgos", []).insert(0, {"id": "carga-fallida", "gravedad": "error",
            "titulo": "No cargó un archivo esencial (script/estilos)",
            "detalle": "; ".join(criticas[:3]) + ". Lo demás de esta revisión NO es confiable en este dispositivo: vuelve a correrlo."})
    if vacia:
        datos.setdefault("hallazgos", []).insert(0, {"id": "pantalla-vacia", "gravedad": "error",
            "titulo": "La pantalla salió vacía (toda de un color)",
            "detalle": "Puede ser que la página no cargó (red, error de JS) o que tarda más: prueba con --esperar más alto. Si en los demás dispositivos sí se ve, es un problema SOLO de este tamaño."})
    datos.update({
        "carga_fallida": bool(criticas or vacia),
        "clave": clave, "nombre": nombre, "plataforma": plat, "tipo": tipo, "motor": motor,
        "consola": list(dict.fromkeys(consola))[:15],
        "fallidas": list(dict.fromkeys(f for f in fallidas if "favicon" not in f))[:15],
        "peso": peso, "carga_s": carga_s, "url": url,
    })
    (carpeta / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    marcar(carpeta, datos)
    return datos


def pantalla_vacia(f: Path):
    """True si la captura es prácticamente de un solo color (página que no cargó)."""
    try:
        from PIL import Image, ImageStat
        im = Image.open(f).convert("L").resize((80, 160))
        return ImageStat.Stat(im).stddev[0] < 3
    except Exception:
        return False


def marcar(carpeta: Path, datos):
    """Dibuja recuadros numerados sobre completa.png donde hay errores/avisos."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    f = carpeta / "completa.png"
    if not f.exists():
        return
    img = Image.open(f).convert("RGB")
    d = ImageDraw.Draw(img)
    ft = fuente(14)
    n = 0
    for hz in datos.get("hallazgos", []):
        rc = hz.get("rect")
        if not rc or hz["gravedad"] == "info":
            continue
        n += 1
        hz["marca"] = n
        color = (230, 30, 30) if hz["gravedad"] == "error" else (240, 150, 0)
        x0, y0 = max(0, rc["x"]), max(0, rc["y"])
        x1, y1 = min(img.width - 1, rc["x"] + rc["w"]), min(img.height - 1, rc["y"] + rc["h"])
        if x1 <= x0 or y1 <= y0:
            continue
        d.rectangle([x0, y0, x1, y1], outline=color, width=3)
        d.rectangle([x0, max(0, y0 - 18), x0 + 26, max(18, y0)], fill=color)
        d.text((x0 + 4, max(0, y0 - 17)), str(n), fill="white", font=ft)
    if n:
        img.save(carpeta / "marcado.png")
        (carpeta / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def hoja(resultados, salida: Path, nombre_archivo="hoja.png", alto_obj=640):
    """Todas las capturas 'pantalla.png' lado a lado, misma altura, con su nombre."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    piezas = []
    for carp, dat in resultados:
        f = carp / "pantalla.png"
        if not f.exists():
            continue
        im = Image.open(f).convert("RGB")
        esc = alto_obj / im.height
        im = im.resize((max(1, int(im.width * esc)), alto_obj))
        errores = sum(1 for x in dat.get("hallazgos", []) if x["gravedad"] == "error")
        piezas.append((im, (dat['nombre'], f"{dat['ancho']}×{dat['alto']}"), errores))
    if not piezas:
        return None
    ancho_max = 2600
    filas, fila, ancho = [], [], 0
    for p in piezas:
        if fila and ancho + p[0].width + 24 > ancho_max:
            filas.append(fila)
            fila, ancho = [], 0
        fila.append(p)
        ancho += p[0].width + 24
    if fila:
        filas.append(fila)
    W = max(sum(p[0].width + 24 for p in fl) for fl in filas) + 24
    H = len(filas) * (alto_obj + 84) + 24
    lienzo = Image.new("RGB", (W, H), (236, 236, 240))
    d = ImageDraw.Draw(lienzo)
    ft = fuente(16)
    fc = fuente(14)
    y = 24
    for fl in filas:
        x = 24
        for im, (nombre, medida), err in fl:
            # el nombre se corta al ancho de su captura para que no se encime con la de al lado
            n = nombre
            while n and d.textlength(n, font=ft) > im.width:
                n = n[:-2]
            d.text((x, y), n if n == nombre else n.rstrip() + "…", fill=(20, 20, 20), font=ft)
            d.text((x, y + 20), medida + (f"  ·  {err} error(es)" if err else ""), fill=(200, 20, 20) if err else (90, 90, 95), font=fc)
            lienzo.paste(im, (x, y + 62))
            d.rectangle([x - 1, y + 61, x + im.width, y + 62 + im.height], outline=(160, 160, 170))
            x += im.width + 24
        y += alto_obj + 84
    destino = salida / nombre_archivo
    lienzo.save(destino)
    return destino


# ---------------------------------------------------------------- informe
ORDEN = {"error": 0, "aviso": 1, "info": 2}


def informe(resultados, salida: Path, url, ruta):
    lineas = [f"# Revisión multi-dispositivo — {ruta or '/'}", "",
              f"- Página: {url}", f"- Fecha: {dt.datetime.now():%Y-%m-%d %H:%M}",
              f"- Dispositivos: {len(resultados)}", ""]
    # Resumen por dispositivo
    lineas += ["## Resumen por dispositivo", "",
               "| Dispositivo | Medida | Motor | Errores | Avisos | Peso | Consola |", "|---|---|---|---|---|---|---|"]
    for carp, d in resultados:
        e = sum(1 for x in d["hallazgos"] if x["gravedad"] == "error")
        a = sum(1 for x in d["hallazgos"] if x["gravedad"] == "aviso")
        lineas.append(f"| {d['nombre']} | {d['ancho']}×{d['alto']} | {d['motor']} | {e} | {a} | "
                      f"{kb((d.get('peso') or {}).get('bytes'))} | {len(d['consola'])} |")
    lineas.append("")
    # Agrupar mismo problema en varios dispositivos
    grupos = {}
    for carp, d in resultados:
        for hz in d["hallazgos"]:
            k = (hz["id"], hz.get("selector", ""))
            g = grupos.setdefault(k, {"hz": hz, "disp": []})
            g["disp"].append(d["clave"] + (f" [#{hz['marca']}]" if hz.get("marca") else ""))
    for grav in ("error", "aviso", "info"):
        items = [g for g in grupos.values() if g["hz"]["gravedad"] == grav]
        if not items:
            continue
        titulo = {"error": "🔴 Errores (arreglar)", "aviso": "🟠 Avisos (revisar)", "info": "🔵 Para saber"}[grav]
        lineas += [f"## {titulo}", ""]
        items.sort(key=lambda g: (-len(g["disp"]), g["hz"]["id"]))
        for g in items:
            hz = g["hz"]
            sel = f" — `{hz['selector']}`" if hz.get("selector") else ""
            lineas.append(f"- **{hz['titulo']}**{sel}")
            lineas.append(f"  - {hz['detalle']}")
            lineas.append(f"  - En: {', '.join(g['disp'])}")
        lineas.append("")
    # Consola y archivos rotos
    errs = {}
    for carp, d in resultados:
        for c in d["consola"] + d["fallidas"]:
            errs.setdefault(c, []).append(d["clave"])
    if errs:
        propios = {c: d for c, d in errs.items() if not c.startswith("[terceros")}
        ajenos = {c: d for c, d in errs.items() if c.startswith("[terceros")}
        if propios:
            lineas += ["## ⚠️ Errores de consola / archivos que no cargan (de la página)", ""]
            for c, ds in list(propios.items())[:25]:
                lineas.append(f"- `{c}` — en {len(ds)} dispositivo(s)")
            lineas.append("")
        if ajenos:
            lineas += ["## Errores de scripts de terceros (Shopify, apps, analítica): normalmente no son nuestros", ""]
            for c, ds in list(ajenos.items())[:10]:
                lineas.append(f"- `{c}` — en {len(ds)} dispositivo(s)")
            lineas.append("")
    # Qué probar con el dedo
    inv = resultados[0][1].get("inventario", {}) if resultados else {}
    lineas += ["## 👆 Qué hay que probar a mano (funcionamiento)", "",
               "El script mide; no toca. Esto es lo interactivo que encontró en la página:", ""]
    for k, v in inv.items():
        if v:
            lineas.append(f"- {k}: {v}")
    lineas += ["", "Pruébalo con `scripts/tocar.py` en un teléfono, una tableta y la compu.", "",
               "## 📁 Archivos", "", "- `hoja.png` — todas las pantallas lado a lado",
               "- `<dispositivo>/pantalla.png` — lo que se ve al abrir",
               "- `<dispositivo>/completa.png` — la página entera",
               "- `<dispositivo>/marcado.png` — la página entera con los problemas numerados",
               "- `<dispositivo>/datos.json` — todo lo medido", ""]
    (salida / "informe.md").write_text("\n".join(lineas), encoding="utf-8")
    resumen = {d["clave"]: {"errores": sum(1 for x in d["hallazgos"] if x["gravedad"] == "error"),
                            "avisos": sum(1 for x in d["hallazgos"] if x["gravedad"] == "aviso"),
                            "ids": sorted({x["id"] for x in d["hallazgos"]})} for _, d in resultados}
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return salida / "informe.md"


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("objetivo")
    ap.add_argument("--dispositivos", default="completo")
    ap.add_argument("--salida")
    ap.add_argument("--ruta", action="append")
    ap.add_argument("--esperar", type=int, default=1200)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--red-lenta", action="store_true")
    ap.add_argument("--motor", default="auto", choices=["auto", "chromium", "webkit"])
    ap.add_argument("--sin-scroll", action="store_true")
    ap.add_argument("--alto-max", type=int, default=14000)
    ap.add_argument("--estado", help="cookies de sesión guardadas con sesion.py (páginas con login / tienda privada)")
    ap.add_argument("--cookies", default="dejar", choices=["dejar", "rechazar"],
                    help="rechazar = pulsa 'Rechazar' en el banner de cookies antes de medir (la opción más privada)")
    ap.add_argument("--esperar-a", dest="esperar_a", help="expresión JS que debe ser verdadera antes de medir, p. ej. \"window.escenaLista === true\"")
    args = ap.parse_args()

    base, _ = resolver_objetivo(args.objetivo)
    claves = resolver(args.dispositivos)
    salida_raiz = Path(args.salida or f"revision-movil/{dt.datetime.now():%Y-%m-%d_%H%M%S}").expanduser().resolve()
    rutas = args.ruta or [None]

    with sync_playwright() as pw:
        navegadores = {"chromium": pw.chromium.launch(args=args_navegador())}
        if args.motor in ("auto", "webkit") and any(DISPOSITIVOS[c][4] == "ios" for c in claves):
            if webkit_disponible(pw):
                navegadores["webkit"] = pw.webkit.launch()
            elif args.motor == "webkit":
                raise SystemExit("WebKit no está instalado: python3 -m playwright install webkit")
            else:
                print("  (iPhone/iPad se miden con el motor de Chrome: WebKit de Playwright no está instalado. "
                      "Para Safari real usa safari.py.)", flush=True)
        informes = []
        for ruta in rutas:
            url = urljoin(base, ruta.lstrip("/")) if ruta else base
            salida = salida_raiz / slug(ruta) if len(rutas) > 1 else salida_raiz
            salida.mkdir(parents=True, exist_ok=True)
            print(f"\n▶ {url}\n  guardando en {salida}", flush=True)
            resultados = []
            for c in claves:
                t = time.time()
                try:
                    d = revisar_dispositivo(pw, navegadores, c, url, salida / c, args)
                    if d.get("carga_fallida"):
                        print(f"  ↻ {c}: la carga falló o la pantalla salió vacía; reintento una vez…", flush=True)
                        d = revisar_dispositivo(pw, navegadores, c, url, salida / c, args)
                except Exception as e:
                    print(f"  ✗ {c}: {e}", flush=True)
                    continue
                resultados.append((salida / c, d))
                e = sum(1 for x in d["hallazgos"] if x["gravedad"] == "error")
                a = sum(1 for x in d["hallazgos"] if x["gravedad"] == "aviso")
                print(f"  {'✓' if not e else '✗'} {c:16} {d['ancho']}×{d['alto']:<5} {d['motor']:8} "
                      f"errores {e:2}  avisos {a:2}  consola {len(d['consola'])}  ({time.time()-t:.1f}s)", flush=True)
            h = hoja(resultados, salida)
            inf = informe(resultados, salida, url, ruta)
            informes.append(inf)
            print(f"  hoja:    {h}\n  informe: {inf}")
        for b in navegadores.values():
            b.close()
    print("\nListo. Lee el informe y MIRA las capturas: los números no ven si algo se ve encimado o feo.")


if __name__ == "__main__":
    main()
