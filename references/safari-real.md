# Pase final en Safari real (iPhone y iPad)

`revisar.py` y `tocar.py` usan el motor de Chrome. Para Android es lo mismo que Chrome en Android, pero **Safari de iPhone y de iPad es otro motor** con sus propias manías. Si tienes una Mac con Xcode, trae simuladores de iPhone y iPad con el Safari de verdad, gratis.

## Cuándo hacerlo
Siempre que la página tenga **formularios, barras fijas, secciones a pantalla completa, video, 3D/WebGL o animaciones de scroll**, o cuando el problema que reportaron fuera de iPhone. Para una landing simple sin nada de eso, basta con `revisar.py`.

## 1. Primera pantalla en varios simuladores (automático)
```bash
python3 ~/.claude/skills/dak-revision-movil/scripts/safari.py <url|archivo.html> \
  --salida /tmp/revision-movil/<proyecto>/safari --esperar 8 --apagar
```
Por defecto abre iPhone 17e, iPhone 17 Pro Max, iPad mini e iPad Air 11". La primera vez que arranca, el simulador tarda 1-3 minutos; luego, segundos. `localhost` funciona tal cual (el simulador comparte la red de la Mac).

Qué mirar en las capturas:
- **La barra de direcciones flotante de iOS 26** (abajo) tapa unos 80 px: ¿queda debajo un botón, un precio o el banner de cookies?
- La muesca o Isla Dinámica arriba, en páginas a pantalla completa.
- Diferencias contra la captura de Chrome del mismo tamaño: fuentes, `backdrop-filter`, sombras, 3D y video.
- La primera vez Safari puede mostrar una burbuja de ayuda ("Accede a tus marcadores…"): no es de la página, ignórala o ciérrala.

## 2. Tocar en Safari real
Usa la herramienta del Simulador de iOS (`mcp__Claude_Code_iOS_Simulator__control`):
- `attach` para abrir el panel en vivo (si el usuario quiere mirar),
- `tap` / `swipe` / `text` / `press_key` / `rotate` / `screenshot` en puntos del dispositivo,
- `open_url` para abrir otra URL.

Guion mínimo: bajar con `swipe` de abajo hacia arriba hasta el final, tocar el menú y el botón principal, tocar un campo de texto (¿hace zoom? ¿el teclado tapa el campo o la barra fija se sube encima?) y girar con `rotate`.

Si esa herramienta no está disponible, usa `xcrun simctl openurl <udid> <url>` y `xcrun simctl io <udid> screenshot archivo.png`, y deja anotado que la parte táctil en Safari no se pudo probar.

## 3. Android de verdad
No hay emulador de Android instalado (haría falta Android Studio, ~10 GB). Chrome emulado con las medidas y el user-agent de Android cubre el 95 %, porque es el mismo motor. Lo que **no** cubre: Samsung Internet (oscurece páginas por su cuenta), los teclados de Samsung y el rendimiento real de un teléfono de gama media. Si la página es crítica (tienda, 3D), dilo en la entrega: "probado en Android emulado; conviene abrirlo una vez en un Android físico".

## 4. Apagar
`--apagar` apaga los simuladores al final. Si los dejaste prendidos: `xcrun simctl shutdown all`. Cada simulador prendido ocupa 1-2 GB de RAM: si la Mac va justa de memoria, apágalos en cuanto termines.
