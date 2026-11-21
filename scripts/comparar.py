#!/usr/bin/env python3
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


if __name__ == "__main__":
    main()
