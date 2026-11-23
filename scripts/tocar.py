#!/usr/bin/env python3
import site as _site, sys as _sys
if _site.getusersitepackages() not in _sys.path:  # que encuentre lo que instaló el Paso 0, aunque corran python3 -I
    _sys.path.append(_site.getusersitepackages())
import os
"""tocar.py — usa la página como una persona con el dedo (o con ratón en la compu).

revisar.py MIDE; tocar.py PRUEBA QUE FUNCIONE. Cada paso dice si salió bien y, si no, por qué:
  - "tapado por …": el dedo cae encima de otra cosa (banner de cookies, cabecera fija, capa invisible)
  - "sin efecto": se tocó y no pasó nada (no cambió la página, ni la URL, ni el scroll)
  - "scroll atrapado": el dedo baja pero la página no avanza (secciones que secuestran el scroll)
  - "no se mueve": el carrusel/3D no responde al deslizar
Toma una captura después de cada paso importante.

USO RÁPIDO (pasos en JSON, el mismo guion en varios dispositivos):
  python3 tocar.py <url|archivo.html|carpeta> --pasos pasos.json [--dispositivos rapido] [--salida DIR]

  pasos.json es una lista. Cada paso es un objeto con UNA acción (+ opciones):
    {"tocar": "button.menu"}                       tocar un elemento (selector CSS)
    {"tocar_texto": "Comprar"}                     tocar el primer elemento visible con ese texto
    {"tocar_en": [0.62, 0.48]}                     tocar en un punto de la pantalla (fracción 0-1 del ancho/alto,
                                                   o px si es > 1). Para canvas/3D: apunta al objeto, no al centro
    {"ver": ".menu-abierto"}                       comprobar que se ve en pantalla
    {"no_ver": ".cookies"}                         comprobar que ya NO se ve
    {"desplazar": 600}                             scroll con el dedo (negativo = hacia arriba)
    {"recorrer": true}                             bajar con el dedo hasta el final; detecta scroll atrapado
    {"deslizar": ".carrusel", "dx": -280}          deslizar de lado dentro de un elemento (carrusel)
    {"arrastrar": "canvas", "dx": 150, "dy": 0}    arrastrar (girar un 3D, mover un mapa)
        + "pagina_quieta": true                    …y exigir que la PÁGINA no se mueva (el gesto es del 3D)
    {"desplazar_sobre": "canvas", "dy": 400}       subir/bajar con el dedo ENCIMA de un elemento: la página debe
                                                   moverse (si no, el 3D/mapa le está robando el scroll a la página)
    {"rueda_recorre": "canvas", "max": 40}         para un 3D que A PROPÓSITO recorre algo con la rueda/el dedo y
                                                   al final suelta la página: falla solo si la página nunca baja
    {"escribir": "input[name=email]", "texto": "a@b.com"}   toca el campo y escribe (abre teclado)
    {"teclado": true}  / {"teclado": false}        simula el teclado en pantalla (quita ~40% de alto)
    {"rotar": true}                                girar el teléfono (vertical <-> horizontal)
    {"tecla": "Escape"}                            pulsar una tecla
    {"atras": true}                                botón/gesto "atrás" del navegador
    {"esperar": 800}                               milisegundos
    {"captura": "menu-abierto"}                    captura con nombre
    {"ir": "/carrito"}                             abrir otra ruta del mismo sitio
  Cualquier paso acepta "nota": "texto" para explicar qué se está probando.

USO COMO MÓDULO (para pruebas más listas):
  from tocar import Sesion
  with Sesion(url, "iphone", "/tmp/salida") as s:
      s.tocar("button.menu"); s.ver("nav.abierto"); s.recorrer()
      print(s.resumen())
"""
import argparse
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dispositivos import DISPOSITIVOS, resolver, contexto_playwright, args_navegador  # noqa: E402
from revisar import resolver_objetivo, slug, RECHAZAR_COOKIES_JS  # noqa: E402
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout  # noqa: E402

ESTADO_JS = """() => ({
  url: location.href,
  y: Math.round(window.scrollY), x: Math.round(window.scrollX),
  h: document.documentElement.scrollHeight,
  largo: document.body ? document.body.innerHTML.length : 0,
  visibles: [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect();
      return b.width > 0 && b.height > 0 && b.bottom > 0 && b.top < innerHeight && getComputedStyle(e).visibility !== 'hidden'; }).length,
  expandidos: [...document.querySelectorAll('[aria-expanded="true"], [open], .is-open, .open, .active')].length,
  foco: document.activeElement ? document.activeElement.tagName + (document.activeElement.id ? '#' + document.activeElement.id : '') : '',
  clases: document.documentElement.className + '|' + (document.body ? document.body.className : ''),
})"""

QUIEN_EN_PUNTO_JS = """([x, y, sel]) => {
  const el = document.querySelector(sel);
  const enc = document.elementFromPoint(x, y);
  const nombre = (e) => !e ? 'nada' : e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
      (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : '');
  return { ok: !!(el && enc && (el === enc || el.contains(enc) || enc.contains(el) && enc !== document.body)),
           encima: nombre(enc) };
}"""


class Sesion:
    def __init__(self, url, clave, salida, pw=None, navegador=None, estado=None, cookies="dejar", esperar_a=None):
        self.estado = estado
        self.cookies, self.esperar_a = cookies, esperar_a
        self.url, self.clave, self.salida = url, clave, Path(salida)
        self.salida.mkdir(parents=True, exist_ok=True)
        self._pw_propio = pw is None
        self.pw, self.navegador = pw, navegador
        self.pasos, self.n = [], 0
        nombre, w, h, dpr, plat, tipo, _ = DISPOSITIVOS[clave]
        self.nombre, self.w, self.h, self.plat, self.tipo = nombre, w, h, plat, tipo
        self.tactil = tipo != "compu"
        self.teclado_abierto = False
        self.consola = []

    # ------------------------------------------------ ciclo de vida
    def __enter__(self):
        if self._pw_propio:
            self._cm = sync_playwright()
            self.pw = self._cm.__enter__()
            self.navegador = self.pw.chromium.launch(args=args_navegador())
        opts = contexto_playwright(self.clave)
        if self.estado:
            opts["storage_state"] = self.estado
        self.ctx = self.navegador.new_context(**opts)
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.consola.append(str(e)[:200]))
        self.cdp = self.ctx.new_cdp_session(self.page)
        try:
            self.page.goto(self.url, wait_until="load", timeout=45000)
        except PWTimeout:
            self._log("abrir", False, "la página no terminó de cargar en 45 s")
        try:
            self.page.wait_for_load_state("networkidle", timeout=6000)
        except PWTimeout:
            pass
        if self.esperar_a:
            try:
                self.page.wait_for_function(self.esperar_a, timeout=45000)
            except Exception:
                self._log("esperar a que cargue", False, f"no se cumplió en 45 s: {self.esperar_a}")
        self.page.wait_for_timeout(1200)
        self.captura("00-inicio")
        if self.cookies == "rechazar":
            r = self.page.evaluate(RECHAZAR_COOKIES_JS)
            self._log("rechazar cookies", True, f"pulsado: {r}" if r else "no había banner (o no lo reconocí)")
            self.page.wait_for_timeout(500)
        ancho = self.page.evaluate("() => window.innerWidth")
        if self.tactil and ancho > self.w + 2:
            self._log("la página cabe en la pantalla", False,
                      f"la página mide {ancho}px y la pantalla {self.w}px: el teléfono la encoge (zoom out). "
                      "Arregla eso primero; con la página encogida, 'tapado' y 'scroll atrapado' pueden ser falsos.")
        return self

    def __exit__(self, *a):
        self.ctx.close()
        if self._pw_propio:
            self.navegador.close()
            self._cm.__exit__(*a)

    # ------------------------------------------------ utilidades
    def _log(self, accion, ok, detalle="", captura=None, nota=None):
        self.pasos.append({"paso": len(self.pasos) + 1, "accion": accion, "ok": ok, "detalle": detalle,
                           "captura": captura, "nota": nota})
        marca = "✓" if ok else "✗"
        print(f"    {marca} {accion:38.38} {detalle}", flush=True)
        return ok

    def _estado(self):
        try:
            return self.page.evaluate(ESTADO_JS)
        except Exception:
            return {}

    def _cambio(self, antes, despues, contar_foco=False):
        if not antes or not despues:
            return "?"
        cambios = []
        if antes["url"] != despues["url"]:
            cambios.append("cambió la URL")
        if abs(antes["y"] - despues["y"]) > 20 or abs(antes["x"] - despues["x"]) > 20:
            cambios.append("se movió la página")
        if antes["expandidos"] != despues["expandidos"]:
            cambios.append("se abrió/cerró algo")
        if abs(antes["visibles"] - despues["visibles"]) > 2 or abs(antes["largo"] - despues["largo"]) > 40:
            cambios.append("cambió lo que se ve")
        if antes["clases"] != despues["clases"]:
            cambios.append("cambió el estado de la página")
        if contar_foco and antes["foco"] != despues["foco"]:
            cambios.append("el campo quedó activo")
        return ", ".join(cambios)

    def _pixeles_distintos(self, a: bytes, b: bytes):
        try:
            from PIL import Image, ImageChops
            import io
            ia, ib = Image.open(io.BytesIO(a)).convert("L"), Image.open(io.BytesIO(b)).convert("L")
            if ia.size != ib.size:
                return 1.0
            dif = ImageChops.difference(ia, ib).point(lambda p: 255 if p > 18 else 0)
            return sum(dif.histogram()[255:]) / (ia.width * ia.height)
        except Exception:
            return None

    def _centro(self, sel):
        loc = self.page.locator(sel).first
        loc.wait_for(state="attached", timeout=5000)
        try:
            # Como haría una persona: llevar el elemento al centro de la pantalla antes de tocarlo
            # (si se toca pegado al borde, cualquier barra fija lo taparía y sería injusto).
            loc.evaluate("e => e.scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'})")
            self.page.wait_for_timeout(250)
        except Exception:
            try:
                loc.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass
        b = loc.bounding_box()
        if not b:
            raise RuntimeError("no se ve (display:none o tamaño 0)")
        x = min(max(b["x"] + b["width"] / 2, 2), self.page.viewport_size["width"] - 2)
        y = min(max(b["y"] + b["height"] / 2, 2), self.page.viewport_size["height"] - 2)
        return x, y, b

    def _gesto_scroll(self, x, y, dx=0, dy=0, velocidad=900):
        """Gesto real de dedo (eventos touch del navegador). dy>0 = bajar la página."""
        if self.tactil:
            self.cdp.send("Input.synthesizeScrollGesture", {
                "x": x, "y": y, "xDistance": -dx, "yDistance": -dy,
                "gestureSourceType": "touch", "speed": velocidad, "preventFling": False})
        else:
            self.page.mouse.move(x, y)
            self.page.mouse.wheel(dx, dy)
        self.page.wait_for_timeout(450 if self.tactil else 900)

    def _arrastre(self, x, y, dx, dy, pasos=12):
        if self.tactil:
            pts = lambda px, py: [{"x": px, "y": py, "id": 1}]  # noqa: E731
            self.cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": pts(x, y)})
            for i in range(1, pasos + 1):
                self.cdp.send("Input.dispatchTouchEvent", {"type": "touchMove",
                              "touchPoints": pts(x + dx * i / pasos, y + dy * i / pasos)})
                time.sleep(0.016)
            self.cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        else:
            self.page.mouse.move(x, y)
            self.page.mouse.down()
            self.page.mouse.move(x + dx, y + dy, steps=pasos)
            self.page.mouse.up()
        self.page.wait_for_timeout(500)

    # ------------------------------------------------ acciones
    def captura(self, nombre, nota=None):
        self.n += 1
        f = self.salida / f"{self.n:02d}-{slug(nombre)}.png"
        try:
            self.page.screenshot(path=str(f), scale="css", timeout=20000)
        except Exception:
            return None
        return f.name

    def tocar(self, sel, nota=None, esperar=700, etiqueta=None):
        et = etiqueta or sel
        try:
            x, y, _ = self._centro(sel)
        except Exception as e:
            return self._log(f"tocar {et}", False, f"no lo encuentro: {e}", nota=nota)
        quien = self.page.evaluate(QUIEN_EN_PUNTO_JS, [x, y, sel])
        if not quien["ok"]:
            cap = self.captura(f"tapado-{et}")
            return self._log(f"tocar {et}", False, f"tapado por {quien['encima']} (el dedo/ratón cae ahí)", cap, nota)
        es_campo = self.page.locator(sel).first.evaluate("e => ['INPUT','TEXTAREA','SELECT'].includes(e.tagName) || e.isContentEditable")
        antes = self._estado()
        img_antes = self.page.screenshot(scale="css")
        deriva = 0.0
        if self.page.evaluate("() => !!document.querySelector('canvas, video, model-viewer')"):
            # La página se mueve sola (3D girando, video): medimos cuánto cambia SIN tocar,
            # para no confundir esa animación con una respuesta al toque.
            self.page.wait_for_timeout(esperar)
            img_ref = self.page.screenshot(scale="css")
            deriva = self._pixeles_distintos(img_antes, img_ref) or 0.0
            img_antes = img_ref
        if self.tactil:
            self.page.touchscreen.tap(x, y)
        else:
            self.page.mouse.click(x, y)
        self.page.wait_for_timeout(esperar)
        cambio = self._cambio(antes, self._estado(), contar_foco=es_campo)
        if not cambio:
            # Lo que se dibuja en canvas/3D/video no cambia el HTML: comparamos la imagen.
            dif = self._pixeles_distintos(img_antes, self.page.screenshot(scale="css"))
            if dif and dif > max(0.02, deriva * 1.8 + 0.01):
                cambio = f"cambió la imagen ({dif*100:.0f}% de la pantalla; sola se mueve {deriva*100:.0f}%)"
        cap = self.captura(f"tras-tocar-{et}")
        if not cambio:
            return self._log(f"tocar {et}", False, "sin efecto: se tocó y no cambió nada en la página", cap, nota)
        return self._log(f"tocar {et}", True, cambio, cap, nota)

    def tocar_en(self, x, y, nota=None, esperar=700):
        vp = self.page.viewport_size
        px = x * vp["width"] if x <= 1 else x
        py = y * vp["height"] if y <= 1 else y
        antes = self._estado()
        img_antes = self.page.screenshot(scale="css")
        if self.tactil:
            self.page.touchscreen.tap(px, py)
        else:
            self.page.mouse.click(px, py)
        self.page.wait_for_timeout(esperar)
        cambio = self._cambio(antes, self._estado())
        if not cambio:
            dif = self._pixeles_distintos(img_antes, self.page.screenshot(scale="css"))
            if dif and dif > 0.03:
                cambio = f"cambió la imagen ({dif*100:.0f}% de la pantalla)"
        cap = self.captura(f"tocar-en-{int(px)}-{int(py)}")
        return self._log(f"tocar en ({int(px)},{int(py)})", bool(cambio), cambio or "sin efecto", cap, nota)

    def tocar_texto(self, texto, nota=None):
        loc = self.page.get_by_text(texto, exact=False)
        n = loc.count()
        for i in range(n):
            el = loc.nth(i)
            if el.is_visible():
                h = el.evaluate("e => { e.setAttribute('data-tocar', '1'); return true }")
                if h:
                    r = self.tocar('[data-tocar="1"]', nota=nota, etiqueta=f'"{texto}"')
                    self.page.evaluate("() => document.querySelectorAll('[data-tocar]').forEach(e => e.removeAttribute('data-tocar'))")
                    return r
        return self._log(f'tocar "{texto}"', False, "no hay ningún elemento visible con ese texto", nota=nota)

    def ver(self, sel, nota=None, debe=True):
        try:
            loc = self.page.locator(sel).first
            visible = loc.count() > 0 and loc.is_visible()
            if visible:
                b = loc.bounding_box()
                vp = self.page.viewport_size
                en_pantalla = b and b["y"] < vp["height"] and b["y"] + b["height"] > 0 and b["x"] < vp["width"] and b["x"] + b["width"] > 0
                visible = bool(en_pantalla)
        except Exception:
            visible = False
        ok = visible == debe
        det = ("se ve" if visible else "no se ve en pantalla")
        return self._log(("ver " if debe else "no ver ") + sel, ok, det, nota=nota)

    def desplazar(self, dy, nota=None):
        antes = self._estado()
        vp = self.page.viewport_size
        self._gesto_scroll(vp["width"] / 2, vp["height"] * (0.7 if dy > 0 else 0.3), dy=dy)
        despues = self._estado()
        movido = despues.get("y", 0) - antes.get("y", 0)
        cap = self.captura(f"desplazar-{dy}")
        if abs(movido) < 10 and not self._cambio(antes, despues):
            return self._log(f"desplazar {dy}px con el dedo", False, "la página no se movió", cap, nota)
        txt = (f"bajó {movido}px" if movido > 0 else f"subió {-movido}px") if movido else "la página reaccionó (sin mover el scroll)"
        return self._log(f"desplazar {dy}px con el dedo", True, txt, cap, nota)

    def recorrer(self, max_gestos=40, nota=None):
        """Baja con el dedo hasta el final. Si en 3 gestos seguidos no avanza y no está al final -> atrapado."""
        vp = self.page.viewport_size
        self.page.evaluate("() => window.scrollTo(0, 0)")
        self.page.wait_for_timeout(400)
        quieto, capturas, gesto = 0, 0, 0
        for gesto in range(max_gestos):
            antes = self._estado()
            self._gesto_scroll(vp["width"] / 2, vp["height"] * 0.75, dy=vp["height"] * 0.6, velocidad=1400)
            d = self._estado()
            final = d.get("y", 0) + vp["height"] >= d.get("h", 0) - 4
            if final:
                break
            if abs(d.get("y", 0) - antes.get("y", 0)) < 8:
                quieto += 1
                if quieto >= 3:
                    cap = self.captura("scroll-atrapado")
                    return self._log("recorrer la página con el dedo", False,
                                     f"scroll atrapado en y={d.get('y')} de {d.get('h')}px: el dedo baja pero la página no avanza",
                                     cap, nota)
            else:
                quieto = 0
            if (gesto < 3 or gesto % 3 == 0) and capturas < 8:
                capturas += 1
                self.captura(f"recorrido-{gesto:02d}")
        cap = self.captura("recorrido-final")
        d = self._estado()
        ok = d.get("y", 0) + vp["height"] >= d.get("h", 0) - 4
        return self._log("recorrer la página con el dedo", ok,
                         f"llegó al final en {gesto + 1} gestos" if ok else f"tras {max_gestos} gestos sigue en y={d.get('y')} de {d.get('h')}",
                         cap, nota)

    def deslizar(self, sel, dx=-280, dy=0, nota=None):
        try:
            x, y, _ = self._centro(sel)
        except Exception as e:
            return self._log(f"deslizar {sel}", False, f"no lo encuentro: {e}", nota=nota)
        quien = self.page.evaluate(QUIEN_EN_PUNTO_JS, [x, y, sel])
        if not quien["ok"]:
            return self._log(f"deslizar {sel}", False, f"tapado por {quien['encima']}", self.captura(f"tapado-{sel}"), nota)
        pos = lambda: self.page.locator(sel).first.evaluate(  # noqa: E731
            "e => [e.scrollLeft, e.scrollTop, getComputedStyle(e).transform, (e.firstElementChild && getComputedStyle(e.firstElementChild).transform) || '', window.scrollY]")
        a_img = self.page.screenshot(scale="css")
        antes = pos()
        if not self.tactil:
            # Con trackpad/ratón: gesto más largo (con scroll-snap uno corto rebota a donde estaba)
            ancho = self.page.locator(sel).first.bounding_box()["width"]
            dx = -max(abs(dx), ancho * 0.6) if dx <= 0 else max(dx, ancho * 0.6)
        self._gesto_scroll(x, y, dx=-dx, dy=-dy, velocidad=700)
        despues = pos()
        d_img = self.page.screenshot(scale="css")
        dif = self._pixeles_distintos(a_img, d_img)
        cap = self.captura(f"deslizar-{sel}")
        se_movio = antes[:4] != despues[:4] or (dif is not None and dif > 0.03)
        detalle = f"se movió ({'scroll ' + str(despues[0] - antes[0]) + 'px' if despues[0] != antes[0] else f'{(dif or 0)*100:.0f}% de la pantalla cambió'})"
        if despues[4] != antes[4] and not antes[:4] != despues[:4]:
            detalle += " — ojo: también se movió la página entera de arriba a abajo"
        return self._log(f"deslizar {sel} {dx:+}px", se_movio, detalle if se_movio else "no se mueve: el deslizamiento no hace nada", cap, nota)

    def desplazar_sobre(self, sel, dy=400, nota=None):
        try:
            x, y, _ = self._centro(sel)
        except Exception as e:
            return self._log(f"desplazar sobre {sel}", False, f"no lo encuentro: {e}", nota=nota)
        e0 = self._estado()
        y0 = e0.get("y", 0)
        vp_h = self.page.viewport_size["height"]
        if e0.get("h", 0) <= vp_h + 5:
            return self._log(f"desplazar sobre {sel}", True, "no aplica: la página no tiene más contenido abajo (ocupa una sola pantalla)", nota=nota)
        if dy > 0 and y0 + vp_h >= e0.get("h", 0) - 5:
            self.page.evaluate("() => window.scrollTo(0, 0)")
            self.page.wait_for_timeout(300)
            x, y, _ = self._centro(sel)
            y0 = self._estado().get("y", 0)
        self._gesto_scroll(x, y, dy=dy)
        y1 = self._estado().get("y", 0)
        cap = self.captura(f"desplazar-sobre-{sel}")
        if abs(y1 - y0) < 10:
            return self._log(f"desplazar {dy:+}px sobre {sel}", False,
                             "la página NO se movió: este elemento le roba el scroll vertical a la página (touch-action / preventDefault)", cap, nota)
        return self._log(f"desplazar {dy:+}px sobre {sel}", True, f"la página bajó {y1 - y0}px", cap, nota)

    def rueda_recorre(self, sel, max_vueltas=40, nota=None):
        """Para 3D/carruseles que a propósito usan la rueda (o el dedo hacia abajo) para recorrer algo
        y, al llegar al final, SUELTAN la página. Da vueltas sobre el elemento: primero debe cambiar
        el elemento y, en algún momento, la página debe seguir bajando. Si nunca baja: scroll atrapado."""
        try:
            x, y, _ = self._centro(sel)
        except Exception as e:
            return self._log(f"rueda recorre {sel}", False, f"no lo encuentro: {e}", nota=nota)
        e0 = self._estado()
        if e0.get("h", 0) <= self.page.viewport_size["height"] + 5:
            return self._log(f"rueda recorre {sel}", True, "no aplica: la página ocupa una sola pantalla", nota=nota)
        y_inicio = e0.get("y", 0)
        img_ant = self.page.screenshot(scale="css")
        vueltas_elemento = 0
        for i in range(max_vueltas):
            antes_y = self._estado().get("y", 0)
            self._gesto_scroll(x, y, dy=250, velocidad=1200)
            ahora_y = self._estado().get("y", 0)
            if ahora_y - antes_y > 10 or ahora_y - y_inicio > 40:
                cap = self.captura(f"rueda-suelta-{sel}")
                return self._log(f"rueda recorre {sel}", True,
                                 f"el elemento consumió {vueltas_elemento} vuelta(s) y luego la página siguió bajando (vuelta {i + 1})", cap, nota)
            img = self.page.screenshot(scale="css")
            if (self._pixeles_distintos(img_ant, img) or 0) > 0.002:
                vueltas_elemento += 1
            img_ant = img
            try:
                x, y, _ = self._centro(sel)
            except Exception:
                pass
        cap = self.captura(f"rueda-atrapada-{sel}")
        return self._log(f"rueda recorre {sel}", False,
                         f"tras {max_vueltas} vueltas la página nunca bajó (el elemento cambió en {vueltas_elemento}): scroll atrapado", cap, nota)

    def arrastrar(self, sel, dx=150, dy=0, nota=None, pagina_quieta=False):
        try:
            x, y, _ = self._centro(sel)
        except Exception as e:
            return self._log(f"arrastrar {sel}", False, f"no lo encuentro: {e}", nota=nota)
        a_img = self.page.screenshot(scale="css")
        y0 = self._estado().get("y", 0)
        self._arrastre(x, y, dx, dy)
        d_img = self.page.screenshot(scale="css")
        dif = self._pixeles_distintos(a_img, d_img) or 0
        y1 = self._estado().get("y", 0)
        cap = self.captura(f"arrastrar-{sel}")
        det = f"{dif*100:.0f}% de la pantalla cambió"
        if abs(y1 - y0) > 20:
            det += f"; la página también se movió {y1 - y0}px (¿el gesto lo roba el scroll?)"
        if pagina_quieta and abs(y1 - y0) > 20:
            return self._log(f"arrastrar {sel} ({dx},{dy})", False, f"la página se movió {y1 - y0}px: el gesto se lo quedó la página, no el 3D", cap, nota)
        return self._log(f"arrastrar {sel} ({dx},{dy})", dif > 0.02, det if dif > 0.02 else "no responde al arrastre", cap, nota)

    def escribir(self, sel, texto, nota=None):
        ok = self.tocar(sel, nota=nota, esperar=300)
        if not ok and "sin efecto" not in self.pasos[-1]["detalle"]:
            return False
        self.pasos.pop()  # el tocar es parte de escribir
        if self.tactil and not self.teclado_abierto:
            self.teclado(True)
        # El navegador real sube el campo para que quede encima del teclado; lo imitamos.
        loc = self.page.locator(sel).first
        try:
            loc.evaluate("e => e.scrollIntoView({block: 'center', behavior: 'instant'})")
        except Exception:
            pass
        self.page.wait_for_timeout(250)
        self.page.keyboard.type(texto, delay=20)
        valor = loc.input_value() if self.page.locator(sel).count() else ""
        b = loc.bounding_box()
        vp = self.page.viewport_size
        tapado_por = None
        if b:
            cx, cy = b["x"] + b["width"] / 2, min(max(b["y"] + b["height"] / 2, 1), vp["height"] - 1)
            q = self.page.evaluate(QUIEN_EN_PUNTO_JS, [cx, cy, sel])
            if not q["ok"]:
                tapado_por = q["encima"]
        cap = self.captura(f"escribir-{sel}")
        if not b or b["y"] + b["height"] > vp["height"] or b["y"] < 0:
            return self._log(f"escribir en {sel}", False, "con el teclado abierto el campo no cabe en lo que queda de pantalla", cap, nota)
        if tapado_por:
            return self._log(f"escribir en {sel}", False, f"con el teclado abierto el campo queda tapado por {tapado_por} (barra/banner fijo)", cap, nota)
        return self._log(f"escribir en {sel}", valor == texto, f'quedó "{valor}"', cap, nota)

    def teclado(self, abierto=True, nota=None):
        """Simula el teclado en pantalla: le quita ~40% de alto a lo visible (iPhone ~ 336px, Android ~ 300px)."""
        if not self.tactil:
            return self._log("teclado", True, "en compu no aplica", nota=nota)
        vp = self.page.viewport_size
        if abierto and not self.teclado_abierto:
            alto_tec = 336 if self.plat == "ios" else 300
            if self.tipo == "tableta":
                alto_tec = 400
            self.page.set_viewport_size({"width": vp["width"], "height": max(200, vp["height"] - alto_tec)})
            self.teclado_abierto = True
        elif not abierto and self.teclado_abierto:
            self.page.set_viewport_size({"width": self.w, "height": self.h})
            self.teclado_abierto = False
        self.page.wait_for_timeout(400)
        cap = self.captura("teclado-abierto" if abierto else "teclado-cerrado")
        return self._log("teclado " + ("abierto" if abierto else "cerrado"), True, f"alto visible {self.page.viewport_size['height']}px", cap, nota)

    def rotar(self, nota=None):
        if not self.tactil:
            return self._log("girar", True, "en compu no aplica (prueba otra medida de ventana con revisar.py)", nota=nota)
        vp = self.page.viewport_size
        self.page.set_viewport_size({"width": vp["height"], "height": vp["width"]})
        self.page.evaluate("() => window.dispatchEvent(new Event('orientationchange'))")
        self.page.wait_for_timeout(900)
        ancho = self.page.evaluate("() => document.documentElement.scrollWidth")
        cap = self.captura("rotado")
        nuevo = self.page.viewport_size
        if ancho > nuevo["width"] + 1:
            return self._log("girar el teléfono", False, f"tras girar la página mide {ancho}px en {nuevo['width']}px: se sale de lado", cap, nota)
        return self._log("girar el teléfono", True, f"ahora {nuevo['width']}×{nuevo['height']}", cap, nota)

    def tecla(self, k, nota=None):
        antes = self._estado()
        self.page.keyboard.press(k)
        self.page.wait_for_timeout(400)
        return self._log(f"tecla {k}", True, self._cambio(antes, self._estado()) or "sin cambio", nota=nota)

    def atras(self, nota=None):
        antes = self._estado()
        try:
            self.page.go_back(timeout=8000)
        except Exception:
            pass
        self.page.wait_for_timeout(600)
        d = self._estado()
        cap = self.captura("atras")
        return self._log("atrás", bool(self._cambio(antes, d)), self._cambio(antes, d) or "no hizo nada", cap, nota)

    def ir(self, ruta, nota=None):
        from urllib.parse import urljoin
        try:
            self.page.goto(urljoin(self.url, ruta), wait_until="load", timeout=45000)
            self.page.wait_for_timeout(900)
            return self._log(f"abrir {ruta}", True, "", self.captura(f"ir-{ruta}"), nota)
        except Exception as e:
            return self._log(f"abrir {ruta}", False, str(e)[:120], nota=nota)

    def esperar(self, ms, nota=None):
        self.page.wait_for_timeout(ms)
        return True

    # ------------------------------------------------ resultados
    def resumen(self):
        fallos = [p for p in self.pasos if not p["ok"]]
        return {"dispositivo": self.clave, "nombre": self.nombre, "pasos": self.pasos,
                "fallos": len(fallos), "errores_js": self.consola[:10]}

    def ejecutar(self, pasos):
        for p in pasos:
            nota = p.get("nota")
            if "tocar" in p: self.tocar(p["tocar"], nota)
            elif "tocar_texto" in p: self.tocar_texto(p["tocar_texto"], nota)
            elif "tocar_en" in p: self.tocar_en(p["tocar_en"][0], p["tocar_en"][1], nota)
            elif "ver" in p: self.ver(p["ver"], nota)
            elif "no_ver" in p: self.ver(p["no_ver"], nota, debe=False)
            elif "desplazar" in p: self.desplazar(p["desplazar"], nota)
            elif "recorrer" in p: self.recorrer(nota=nota)
            elif "deslizar" in p: self.deslizar(p["deslizar"], p.get("dx", -280), p.get("dy", 0), nota)
            elif "arrastrar" in p: self.arrastrar(p["arrastrar"], p.get("dx", 150), p.get("dy", 0), nota, p.get("pagina_quieta", False))
            elif "desplazar_sobre" in p: self.desplazar_sobre(p["desplazar_sobre"], p.get("dy", 400), nota)
            elif "rueda_recorre" in p: self.rueda_recorre(p["rueda_recorre"], p.get("max", 40), nota)
            elif "escribir" in p: self.escribir(p["escribir"], p.get("texto", "prueba"), nota)
            elif "teclado" in p: self.teclado(bool(p["teclado"]), nota)
            elif "rotar" in p: self.rotar(nota)
            elif "tecla" in p: self.tecla(p["tecla"], nota)
            elif "atras" in p: self.atras(nota)
            elif "ir" in p: self.ir(p["ir"], nota)
            elif "esperar" in p: self.esperar(p["esperar"])
            elif "captura" in p: self._log("captura", True, self.captura(p["captura"]) or "", nota=nota)
            else: self._log(f"paso desconocido {p}", False, "revisa el JSON")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("objetivo")
    ap.add_argument("--pasos", required=True, help="archivo JSON con la lista de pasos")
    ap.add_argument("--dispositivos", default="rapido")
    ap.add_argument("--salida", default="revision-movil/interaccion")
    ap.add_argument("--estado", help="cookies de sesión guardadas con sesion.py")
    ap.add_argument("--cookies", default="dejar", choices=["dejar", "rechazar"])
    ap.add_argument("--esperar-a", dest="esperar_a", help="expresión JS que debe ser verdadera antes de empezar")
    args = ap.parse_args()

    url, _ = resolver_objetivo(args.objetivo)
    pasos = json.loads(Path(args.pasos).read_text(encoding="utf-8"))
    salida = Path(args.salida).expanduser().resolve()
    resultados = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=args_navegador())
        for clave in resolver(args.dispositivos):
            print(f"\n▶ {DISPOSITIVOS[clave][0]} ({clave})", flush=True)
            with Sesion(url, clave, salida / clave, pw=pw, navegador=nav, estado=args.estado,
                        cookies=args.cookies, esperar_a=args.esperar_a) as s:
                s.ejecutar(pasos)
                resultados.append(s.resumen())
        nav.close()
    lineas = ["# Prueba de funcionamiento con el dedo", "", f"- Página: {url}", ""]
    for r in resultados:
        estado = "✅ todo bien" if not r["fallos"] else f"❌ {r['fallos']} fallo(s)"
        lineas.append(f"## {r['nombre']} — {estado}")
        for p in r["pasos"]:
            lineas.append(f"- {'✓' if p['ok'] else '✗'} {p['accion']} — {p['detalle']}" + (f" ({p['nota']})" if p.get("nota") else "")
                          + (f" → `{r['dispositivo']}/{p['captura']}`" if p.get("captura") else ""))
        if r["errores_js"]:
            lineas.append(f"- Errores JS: {r['errores_js']}")
        lineas.append("")
    (salida / "interaccion.md").write_text("\n".join(lineas), encoding="utf-8")
    (salida / "interaccion.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(r["fallos"] for r in resultados)
    print(f"\n{'✅ Sin fallos' if not total else f'❌ {total} fallo(s)'} — informe: {salida / 'interaccion.md'}")


def _aviso_version():
    """Al terminar, revisa en silencio si hay versión nueva de la skill (máx. 1 vez al día)."""
    try:
        import importlib.util
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.py")
        spec = importlib.util.spec_from_file_location("dak_version", ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulo.avisar()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        _aviso_version()
