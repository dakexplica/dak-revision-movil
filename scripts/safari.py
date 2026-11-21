#!/usr/bin/env python3
"""safari.py — abre la página en el Safari REAL de los simuladores de iPhone/iPad y saca captura.

El motor de Chrome (revisar.py) es el mismo que Chrome en Android, pero Safari tiene sus manías:
la barra de direcciones flotante de iOS 26 tapa la parte de abajo, el teclado empuja las barras
fijas, 100vh mide otra cosa, el video y el 3D se comportan distinto. Esto lo enseña tal cual.

Uso:
  python3 safari.py <url> [--salida DIR] [--simuladores "iPhone 17e,iPhone 17 Pro Max,iPad mini (A17 Pro)"]
                         [--esperar 6] [--apagar]

- La URL puede ser localhost: el simulador comparte la red de la Mac.
- Un archivo local (.html) se sirve solo por http.
- Saca la PRIMERA PANTALLA de cada simulador. Para tocar, deslizar o bajar en Safari real usa la
  herramienta del Simulador de iOS (mcp__Claude_Code_iOS_Simulator__control: tap, swipe, screenshot)
  o pide al usuario que lo abra en su teléfono.
- --apagar apaga al terminar SOLO los simuladores que este script prendió (los que ya estaban
  prendidos, quizá por otra sesión, se quedan como estaban).
- Safari del simulador guarda sus pestañas entre sesiones: puede haber pestañas de otro proyecto.
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

POR_DEFECTO = ["iPhone 17e", "iPhone 17 Pro Max", "iPad mini (A17 Pro)", "iPad Air 11-inch (M4)"]


def sh(*a, check=False):
    return subprocess.run(list(a), capture_output=True, text=True, check=check)


def disponibles():
    """nombre -> (udid, estado). estado: Booted | Shutdown"""
    out = sh("xcrun", "simctl", "list", "devices", "available").stdout
    return {m.group(1).strip(): (m.group(2), m.group(3)) for m in
            re.finditer(r"^\s+(.+?) \(([0-9A-F-]{36})\) \((\w+)\)", out, re.M)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("objetivo")
    ap.add_argument("--salida", default="revision-movil/safari")
    ap.add_argument("--simuladores", default=",".join(POR_DEFECTO))
    ap.add_argument("--esperar", type=float, default=6)
    ap.add_argument("--apagar", action="store_true")
    a = ap.parse_args()

    if sh("xcrun", "simctl", "help").returncode:
        raise SystemExit("No hay Xcode / simctl en esta Mac: no se puede usar Safari real. Usa revisar.py.")
    url = a.objetivo
    if not re.match(r"^https?://", url):
        from revisar import resolver_objetivo
        url, _ = resolver_objetivo(url)
        url = url.replace("127.0.0.1", "localhost")
    salida = Path(a.salida).expanduser().resolve()
    salida.mkdir(parents=True, exist_ok=True)
    disp = disponibles()
    pedidos = [s.strip() for s in a.simuladores.split(",") if s.strip()]
    usados, prendidos_por_mi = [], []
    for nombre in pedidos:
        udid, estado = disp.get(nombre, (None, None))
        if not udid:
            print(f"  · '{nombre}' no está instalado. Disponibles: {', '.join(k for k in disp if 'iPhone' in k or 'iPad' in k)}")
            continue
        if estado != "Booted":
            sh("xcrun", "simctl", "boot", udid)
            prendidos_por_mi.append(udid)
        sh("xcrun", "simctl", "bootstatus", udid, "-b")
        sh("xcrun", "simctl", "openurl", udid, url)
        usados.append((nombre, udid))
    if not usados:
        raise SystemExit("Ningún simulador disponible.")
    time.sleep(a.esperar)
    for nombre, udid in usados:
        f = salida / (re.sub(r"[^a-zA-Z0-9]+", "-", nombre).strip("-").lower() + ".png")
        r = sh("xcrun", "simctl", "io", udid, "screenshot", str(f))
        print(f"  {'✓' if r.returncode == 0 else '✗'} {nombre}: {f if r.returncode == 0 else r.stderr.strip()[:200]}")
    if a.apagar:
        # Solo apaga los que prendió este script: otro simulador puede estar usándolo otra sesión.
        for udid in prendidos_por_mi:
            sh("xcrun", "simctl", "shutdown", udid)
    print(f"\nCapturas de Safari real en {salida}. Míralas: ojo con la barra flotante de abajo, la muesca y el teclado.")


if __name__ == "__main__":
    main()
