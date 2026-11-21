#!/usr/bin/env python3
"""Paso 0 de dak-revision-movil: revisa que esté todo lo que la skill necesita.

  python3 paso0.py              → solo revisa y explica qué falta (no instala nada)
  python3 paso0.py --instalar   → instala lo que falta (solo con permiso de la persona)

Necesita: Python 3.9+, Playwright (para abrir la página como cada dispositivo), su navegador
Chromium y Pillow (para las capturas). ffmpeg solo hace falta para revisar videos. Xcode solo
para la prueba opcional en Safari real (Mac).
"""
import importlib.util, shutil, subprocess, sys

instalar = '--instalar' in sys.argv
faltan = []

def ok(t): print(f'  ✓ {t}')
def no(t, por): print(f'  ✗ {t} — {por}'); faltan.append(t)

print('Revisando lo que necesita la skill dak-revision-movil:\n')
v = sys.version_info
ok(f'Python {v.major}.{v.minor}') if v >= (3, 9) else no('Python 3.9 o más nuevo', 'tienes ' + f'{v.major}.{v.minor}; instálalo desde python.org')

tiene_pw = importlib.util.find_spec('playwright') is not None
ok('Playwright') if tiene_pw else no('Playwright', 'abre tu página como si fuera cada celular, tableta o compu')
ok('Pillow') if importlib.util.find_spec('PIL') else no('Pillow', 'arma las capturas y las marca en rojo')

chromium = False
if tiene_pw:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close(); chromium = True
    except Exception:
        pass
ok('Navegador Chromium de Playwright') if chromium else no('Navegador Chromium de Playwright', 'es el navegador que usa para revisar (unos 150 MB)')

ok('ffmpeg (para videos)') if shutil.which('ffmpeg') else print('  · ffmpeg no está: solo hace falta si quieres revisar videos (macOS: brew install ffmpeg · Windows: winget install ffmpeg · Linux: sudo apt install ffmpeg)')
if sys.platform == 'darwin':
    print('  ✓ Xcode (Safari real, opcional)' if shutil.which('xcrun') and subprocess.run(['xcrun', 'simctl', 'help'], capture_output=True).returncode == 0
          else '  · Xcode no está: es opcional, solo para probar en Safari real de iPhone/iPad')

if not faltan:
    print('\nTodo listo. Ya puedes revisar tu página.'); sys.exit(0)
if not instalar:
    print('\nFalta: ' + ', '.join(faltan) + '.\nPara instalarlo (con tu permiso): python3 paso0.py --instalar'); sys.exit(1)

print('\nInstalando lo que falta…')
pkgs = [p for p, n in [('playwright', 'Playwright'), ('pillow', 'Pillow')] if n in faltan]
if pkgs:
    r = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', *pkgs])
    if r.returncode: print('No se pudo instalar con pip. Prueba: python3 -m pip install --user ' + ' '.join(pkgs)); sys.exit(1)
if 'Navegador Chromium de Playwright' in faltan or 'Playwright' in faltan:
    r = subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'])
    if r.returncode: print('No se pudo bajar Chromium. Prueba: python3 -m playwright install chromium'); sys.exit(1)
print('\nListo. Vuelve a correr python3 paso0.py para confirmar.')
