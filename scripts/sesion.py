#!/usr/bin/env python3
"""sesion.py — para revisar páginas que piden entrar (login, tienda en modo privado, vista previa).

Abre una ventana de navegador VISIBLE en esa página. El usuario entra él mismo (escribe su contraseña
él: Claude nunca teclea contraseñas reales) y cierra la ventana. Se guardan las cookies en un
archivo que luego usan revisar.py y tocar.py con --estado.

Uso:
  python3 sesion.py <url> <archivo-estado.json>
  python3 revisar.py <url> --estado <archivo-estado.json>

El archivo de estado contiene cookies de sesión: guárdalo fuera de cualquier repo
(p. ej. /tmp/revision-movil/<proyecto>/estado.json) y bórralo al terminar.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    url, destino = sys.argv[1], Path(sys.argv[2]).expanduser().resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False)
        ctx = nav.new_context(viewport={"width": 1280, "height": 860})
        page = ctx.new_page()
        page.goto(url)
        print("Entra en la ventana que se abrió y CIÉRRALA cuando ya veas la página. Esperando…")
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        ctx.storage_state(path=str(destino))
        nav.close()
    print(f"Sesión guardada en {destino}")


if __name__ == "__main__":
    main()
