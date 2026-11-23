#!/usr/bin/env python3
import site as _site, sys as _sys
if _site.getusersitepackages() not in _sys.path:  # que encuentre lo que instaló el Paso 0, aunque corran python3 -I
    _sys.path.append(_site.getusersitepackages())
import os
"""comparar.py — antes vs después de arreglar, dispositivo por dispositivo.

Uso:
  python3 comparar.py <carpeta-antes> <carpeta-despues> [--salida DIR]

Las dos carpetas son salidas de revisar.py. Genera:
  - comparacion.md   tabla de errores/avisos antes → después, y qué problemas desaparecieron,
                     cuáles siguen y cuáles son NUEVOS (¡ojo: un arreglo rompió otra cosa!)
  - antes-despues.png  pantalla de cada dispositivo: arriba antes, abajo después
"""
import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from revisar import fuente  # noqa: E402


def cargar(carp: Path):
    datos = {}
    for d in sorted(carp.iterdir()):
        f = d / "datos.json"
        if f.exists():
            datos[d.name] = json.loads(f.read_text(encoding="utf-8"))
    return datos


def claves(d):
    return {(h["id"], h.get("selector", "")): h for h in d.get("hallazgos", []) if h["gravedad"] != "info"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("antes")
    ap.add_argument("despues")
    ap.add_argument("--salida")
    a = ap.parse_args()
    A, D = Path(a.antes).resolve(), Path(a.despues).resolve()
    salida = Path(a.salida).resolve() if a.salida else D
    salida.mkdir(parents=True, exist_ok=True)
    da, dd = cargar(A), cargar(D)
    comunes = [k for k in da if k in dd]
    if not comunes:
        raise SystemExit("No hay dispositivos en común entre las dos carpetas.")

    lin = ["# Antes → después", "", "| Dispositivo | Errores | Avisos | Consola |", "|---|---|---|---|"]
    nuevos_total = 0
    detalle = []
    for k in comunes:
        ea = sum(1 for h in da[k]["hallazgos"] if h["gravedad"] == "error")
        ed = sum(1 for h in dd[k]["hallazgos"] if h["gravedad"] == "error")
        aa = sum(1 for h in da[k]["hallazgos"] if h["gravedad"] == "aviso")
        ad = sum(1 for h in dd[k]["hallazgos"] if h["gravedad"] == "aviso")
        ca, cd = len(da[k].get("consola", [])), len(dd[k].get("consola", []))
        flecha = lambda x, y: f"{x} → **{y}**" + (" ✅" if y < x else " ⚠️" if y > x else "")  # noqa: E731
        lin.append(f"| {dd[k].get('nombre', k)} | {flecha(ea, ed)} | {flecha(aa, ad)} | {flecha(ca, cd)} |")
        ka, kd = claves(da[k]), claves(dd[k])
        resueltos = sorted({ka[x]["titulo"] for x in ka if x not in kd})
        siguen = sorted({kd[x]["titulo"] + (f" `{x[1]}`" if x[1] else "") for x in kd if x in ka})
        nuevos = sorted({kd[x]["titulo"] + (f" `{x[1]}`" if x[1] else "") for x in kd if x not in ka})
        # Errores de consola / archivos rotos: esconder una imagen rota no la arregla
        norm = lambda d: {re.sub(r"https?://(127\.0\.0\.1|localhost):\d+", "", c) for c in d.get("consola", []) + d.get("fallidas", [])}  # noqa: E731
        cons_siguen = sorted(norm(dd[k]) & norm(da[k]))
        cons_nuevos = sorted(norm(dd[k]) - norm(da[k]))
        nuevos_total += len(nuevos) + len(cons_nuevos)
        nom = dd[k].get("nombre", k)
        if da[k].get("carga_fallida") or dd[k].get("carga_fallida"):
            detalle.append(f"### {nom}\n- [{k}] ⚠️ NO COMPARABLE: la página no cargó bien en el " +
                           ("antes" if da[k].get("carga_fallida") else "después") + ". Vuelve a medir este dispositivo.\n")
            continue
        if resueltos or siguen or nuevos or cons_siguen or cons_nuevos:
            detalle.append(f"### {nom}")
            if resueltos:
                detalle.append(f"- [{k}] ✅ Resueltos ({len(resueltos)} tipos): " + "; ".join(resueltos))
            if siguen:
                detalle.append(f"- [{k}] ⏳ Siguen ({len(siguen)}): " + "; ".join(siguen))
            if nuevos:
                detalle.append(f"- [{k}] 🆕 NUEVOS ({len(nuevos)}) — el arreglo pudo romper algo: " + "; ".join(nuevos))
            if cons_siguen:
                detalle.append(f"- [{k}] ⚠️ Siguen en consola / sin cargar ({len(cons_siguen)}): " + "; ".join(c[:90] for c in cons_siguen[:5])
                               + " — si escondiste algo roto, sigue roto: dilo en la entrega")
            if cons_nuevos:
                detalle.append(f"- [{k}] 🆕 Errores de consola NUEVOS ({len(cons_nuevos)}): " + "; ".join(c[:90] for c in cons_nuevos[:5]))
            detalle.append("")
    lin += ["", f"**Problemas nuevos tras el arreglo: {nuevos_total}**" + (" — hay que revisarlos antes de entregar." if nuevos_total else " ✅"), ""]
    lin += detalle
    (salida / "comparacion.md").write_text("\n".join(lin), encoding="utf-8")
    print("\n".join(lin))

    # Imagen antes/después
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    alto = 520
    columnas = []
    for k in comunes:
        fa, fd = A / k / "pantalla.png", D / k / "pantalla.png"
        if not (fa.exists() and fd.exists()):
            continue
        ims = []
        for f in (fa, fd):
            im = Image.open(f).convert("RGB")
            e = alto / im.height
            ims.append(im.resize((max(1, int(im.width * e)), alto)))
        columnas.append((k, ims))
    if not columnas:
        return
    # repartir en filas de máx ~2600 px
    filas, fila, ancho = [], [], 0
    for c in columnas:
        w = max(i.width for i in c[1]) + 20
        if fila and ancho + w > 2600:
            filas.append(fila)
            fila, ancho = [], 0
        fila.append(c)
        ancho += w
    filas.append(fila)
    W = max(sum(max(i.width for i in c[1]) + 20 for c in f) for f in filas) + 120
    H = len(filas) * (alto * 2 + 70) + 20
    lienzo = Image.new("RGB", (W, H), (236, 236, 240))
    d = ImageDraw.Draw(lienzo)
    ft = fuente(16)
    y = 10
    for f in filas:
        d.text((10, y + 30 + alto // 2), "ANTES", fill=(200, 30, 30), font=ft)
        d.text((10, y + 50 + alto + alto // 2), "DESPUÉS", fill=(20, 140, 60), font=ft)
        x = 110
        for k, (ia, idp) in f:
            d.text((x, y), k, fill=(20, 20, 20), font=ft)
            lienzo.paste(ia, (x, y + 24))
            lienzo.paste(idp, (x, y + 44 + alto))
            x += max(ia.width, idp.width) + 20
        y += alto * 2 + 70
    lienzo.save(salida / "antes-despues.png")
    print(f"\nImagen: {salida / 'antes-despues.png'}")

    # Imagen clara para explicar a una persona: 4 aparatos clave, cada uno en pareja ANTES | DESPUÉS
    import json as _j
    def errores(carp, k):
        try: return sum(1 for h in _j.loads((carp / k / "datos.json").read_text())["hallazgos"] if h.get("gravedad") == "error")
        except Exception: return None
    clave = [k for k in ("iphone", "android-chico", "ipad", "macbook-air") if k in comunes] or comunes[:4]
    nombres = {"iphone": "iPhone", "android-chico": "Android chico", "ipad": "iPad", "macbook-air": "MacBook Air"}
    AL, PAD, CAB = 620, 40, 70
    pares = []
    for k in clave:
        fa, fd = A / k / "pantalla.png", D / k / "pantalla.png"
        if fa.exists() and fd.exists():
            ims = [Image.open(f).convert("RGB") for f in (fa, fd)]
            ims = [im.resize((max(1, int(im.width * AL / im.height)), AL)) for im in ims]
            pares.append((k, ims))
    if pares:
        ancho_par = lambda ims: ims[0].width + ims[1].width + 30
        W2 = max(ancho_par(ims) for _, ims in pares) + PAD * 2
        H2 = 110 + len(pares) * (AL + CAB + 50)
        cl = Image.new("RGB", (W2, H2), (244, 245, 247)); d2 = ImageDraw.Draw(cl)
        d2.text((PAD, 30), "Antes y después", fill=(11, 13, 18), font=fuente(44))
        y = 110
        for k, (ia, idp) in pares:
            d2.text((PAD, y), nombres.get(k, k), fill=(11, 13, 18), font=fuente(30)); y += 44
            x = PAD
            for im, txt, col, n in ((ia, "ANTES", (226, 61, 46), errores(A, k)), (idp, "DESPUÉS", (22, 163, 74), errores(D, k))):
                if n is not None: col = (22, 163, 74) if n == 0 else (226, 61, 46)   # el color dice el resultado, no si es antes o después
                d2.rounded_rectangle([x - 6, y - 6, x + im.width + 6, y + CAB + im.height + 6], 18, fill=col)
                etiqueta = f"{txt} · " + ("bien" if n == 0 else f"{n} error" + ("es" if n != 1 else "")) if n is not None else txt
                tam = 30
                while tam > 16 and d2.textlength(etiqueta, font=fuente(tam)) > im.width - 24: tam -= 2
                d2.text((x + 12, y + 18 + (30 - tam) // 2), etiqueta, fill=(255, 255, 255), font=fuente(tam))
                cl.paste(im, (x, y + CAB)); x += im.width + 30
            y += AL + CAB + 50
        cl.save(salida / "antes-despues-claro.png")
        print(f"Imagen clara (4 aparatos): {salida / 'antes-despues-claro.png'}")


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
