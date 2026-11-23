#!/usr/bin/env python3
"""Aviso SILENCIOSO de versión nueva para skills de @dakexplica.

  python3 version.py              → revisa (máx. 1 vez al día). NO imprime nada si: está al día, no hay internet,
                                    ya revisó hoy o la persona dijo «ahora no» a esa versión. Solo imprime
                                    cuando hay una versión nueva:  NUEVA <versión> | <qué cambió>
  python3 version.py --omitir X   → la persona dijo «ahora no» a la versión X: no se vuelve a avisar de X
  python3 version.py --estado     → muestra la versión instalada (para depurar; imprime siempre)
  python3 version.py --forzar     → ignora el «máx. 1 vez al día» (para probar)

Solo mira el repo oficial indicado en version.json (raw.githubusercontent.com). No descarga ni instala nada:
actualizar lo decide la persona. Sin dependencias (solo librería estándar de Python).
Para probar sin internet: DAK_VERSION_URL=file:///ruta/version.json
"""
import json, os, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def num(v):
    try:
        return tuple(int(x) for x in str(v).strip().lstrip('v').split('.'))
    except ValueError:
        return None


def main():
    try:
        local = json.load(open(os.path.join(RAIZ, 'version.json'), encoding='utf-8'))
    except (OSError, ValueError):
        return                                   # sin version.json no hay nada que revisar
    if '--estado' in sys.argv:
        print(f"{local.get('skill')} {local.get('version')}"); return
    if os.path.isdir(os.path.join(RAIZ, '.git')) and not os.environ.get('DAK_VERSION_URL'):
        return                                   # copia del autor (es el repo): nunca se avisa ni se actualiza encima
    ruta = os.path.expanduser(f"~/.dakexplica/{local['skill']}.json")
    try:
        est = json.load(open(ruta, encoding='utf-8'))
    except (OSError, ValueError):
        est = {}
    if '--omitir' in sys.argv:
        est['version_omitida'] = sys.argv[sys.argv.index('--omitir') + 1]
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        json.dump(est, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False); return
    hoy = time.strftime('%Y-%m-%d')
    if est.get('ultima_revision') == hoy and '--forzar' not in sys.argv:
        return
    url = os.environ.get('DAK_VERSION_URL') or f"https://raw.githubusercontent.com/{local['repo']}/main/version.json"
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            remoto = json.loads(r.read().decode('utf-8'))
    except Exception:
        return                                   # sin internet o GitHub no responde: silencio, y se reintenta mañana
    est['ultima_revision'] = hoy
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        json.dump(est, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False)
    except OSError:
        pass
    nueva, actual = num(remoto.get('version')), num(local.get('version'))
    if not nueva or not actual or nueva <= actual:
        return                                   # al día: no se dice nada
    if est.get('version_omitida') == str(remoto.get('version')):
        return                                   # dijo «ahora no» a esta versión
    print(f"NUEVA {remoto['version']} | {str(remoto.get('novedades', '')).strip()[:200]}")


if __name__ == '__main__':
    main()
