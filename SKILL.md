---
name: dak-revision-movil
description: Revisa tu página o app en 15 dispositivos a la vez — iPhone y Android (chicos, grandes, plegables), iPad y tabletas, laptops Mac/Windows y monitores grandes — y la deja funcionando y viéndose bien en todos. No solo que quepa, también que funcione con el dedo (menús, botones, scroll, carruseles, formularios con teclado, 3D, video). Toma capturas, la usa como una persona (toca, desliza, gira, abre el teclado), arregla lo obvio, te pregunta antes de cambiar tu diseño y compara antes/después. También revisa videos, imágenes y PDFs para celular (9:16, zonas seguras de Reels/TikTok, peso para WhatsApp y web). Incluye una mini guía interactiva de ~5 min. Úsala cuando digan "revísalo/adáptalo para móvil, celular, iPhone, Android, iPad o tablet", "en el celular se ve mal/cortado/encimado/muy grande", "que funcione en el celular", "revisa mi página en todos los dispositivos", "empieza la guía", o manden una captura del celular con algo roto, aunque no la nombren. Y por tu cuenta antes de dar por terminada cualquier web, landing, tienda, app, propuesta HTML, 3D o video que se verá en un celular.
---

# /dak-revision-movil

Construyes en la compu y luego, en el celular, descubres uno por uno lo que está mal: algo cortado, un 3D encimado, un scroll que no deja bajar, un video que no cabe, un botón que no se puede tocar. Esta skill existe para que **eso lo descubra Claude antes que tú (o que tus clientes)**, en todos los dispositivos, y lo arregle.

"Adaptado" no significa "que quepa". Significa que **una persona con el celular en la mano puede usarlo sin pelearse**: lee sin hacer zoom, toca lo que quiere tocar, el scroll la lleva a donde tiene que ir, el teclado no tapa lo que escribe, los gestos hacen lo que espera y carga a tiempo con datos móviles. Y que en un iPad, en una laptop y en un monitor de 27" también se vea pensado, no estirado ni pegado a un lado.

**Habla en español, claro y sin tecnicismos.** Explica qué veía la gente y qué ve ahora, no qué propiedad de CSS cambiaste.

Las rutas de abajo usan `<skill>` = la carpeta donde está instalada esta skill (normalmente `~/.claude/skills/dak-revision-movil`).

## Primera vez · Paso 0 y mini guía

**Paso 0 · ¿Está todo lo que necesita?** Antes del primer uso (y si algo falla), corre:

```bash
python3 <skill>/scripts/paso0.py
```

Revisa Python 3.9+, Playwright, el navegador Chromium de Playwright, Pillow y ffmpeg (este último solo para videos). Si falta algo, **explícale a la persona en una frase qué es y para qué sirve, y pide permiso antes de instalar nada**. Con su sí: `python3 <skill>/scripts/paso0.py --instalar` (instala solo lo que falta: `pip install --user playwright pillow` y `python3 -m playwright install chromium`; para ffmpeg da el comando de su sistema, no lo instala solo). Si dice que no, explica qué partes no van a funcionar y sigue con lo que sí.

**La mini guía (solo se ofrece una vez).** Al empezar, revisa si existe `~/.dakexplica/dak-revision-movil.json`:
- **Si no existe**, es la primera vez (pasa igual si la instalaron con el mensaje de la ficha, con el comando a secas o si te piden algo directo como «revisa mi página»). Antes de cualquier otra cosa, ofrécela **con botones y todo lo importante dentro de la pregunta** (en la app, el texto previo a un botón se resume):
  - Pregunta: "Es la primera vez que usas Revisión en 15 pantallas. ¿Quieres que te enseñe rápido a usarla y sacarle el mayor provecho? Son unos 5 min, mientras revisamos tu primera página."
  - **Sí, enséñame (5 min)** — "3 lecciones cortas con tu página o con una de ejemplo"
  - **No, úsala directo** — "hago lo que me pediste; la guía la abres cuando quieras con «ábreme la guía»"
  - Si no existe la herramienta de botones, el mismo texto con "responde 1 o 2".

  Luego crea el archivo con `{"guia_ofrecida": true}` (crea la carpeta si hace falta). Con **Sí**: abre `guia/leccion-1.md` y síguela (si ya te había dado su página o pedido algo, úsalo en la guía en vez de volver a preguntarlo). Con **No**: haz directo lo que pidió; si solo instaló, dile en una línea qué escribir para usarla («Usando la skill dak-revision-movil, revisa mi página en los 15 dispositivos»).
- **Si existe**, no vuelvas a preguntar: haz el trabajo directo.
- **En la app de Claude** (sin archivos entre chats) la pregunta solo sale cuando la persona instala la skill o escribe el mensaje de prueba de la ficha. Después no vuelve a salir sola.
- Frases que abren la guía siempre: «ábreme la guía», «empieza la guía», «quiero la guía» (desde cero), «retoma la guía» (donde se quedó, en `~/.dakexplica/dak-revision-movil.json`), «guía lección 2» (una suelta), «sal de la guía» (volver al uso normal).
- Aunque la abran con «empieza la guía», el primer mensaje es igual la bienvenida de la lección 1.
- La guía son 3 lecciones cortas en `guia/`. Cada una es un guion para Claude (lo que dices, **ACCIÓN** y **ALTO**). **Antes de cada lección lee `guia/estilo.md`**: se da en vivo (saludo con su nombre, reaccionas a lo que dice, seguimiento entre lecciones), nunca seca. Nunca sigas sin que la persona conteste.

## La regla de oro: medir, MIRAR, tocar, arreglar, volver a medir

Los números solos mienten. En una prueba, un 3D de camisetas sacó **0 errores medidos en los 15 dispositivos**, y en las capturas de celular se veía cortado a la derecha, con las camisetas chiquitas y fuera de centro. Lo medible (desbordes, botones chicos, letra chica) lo encuentra el script; lo que "se ve mal" solo lo encuentras **mirando las capturas tú mismo**, y lo que "no funciona" solo lo encuentras **tocando**. Las tres cosas, siempre.

## 0 · ¿Qué te están pidiendo?

| Situación | Qué haces |
|---|---|
| Revisar o adaptar algo que ya existe (web, tienda, app, propuesta, 3D) | Pasos 1 → 8 |
| Estás **construyendo** algo nuevo | Aplica `references/construir-bien.md` mientras lo haces y, antes de decir "listo", pasos 2 → 8 |
| Un **video, imagen o PDF** que se verá en celular (Reels, TikTok, historias, WhatsApp, web) | `references/videos-y-archivos.md` + `scripts/revisar_archivo.py` |
| Una web con videos que "en el celular se ven muy grandes" | Las dos cosas: la página (pasos 1-8) y el archivo de video |
| Te mandan una captura del celular con algo roto | Reprodúcelo primero en ese dispositivo (`--dispositivos iphone` o `android`…) y luego revisa todo: donde hay un error suele haber más |
| "Empieza la guía" | `guia/leccion-1.md` |

## 1 · Contexto antes de tocar nada

1. Lee el `CLAUDE.md` y las notas del proyecto (`README`, `ESTADO`, `PROGRESO`…). Ahí están las reglas que **no** se rompen.
2. Averigua cómo se ve la página y cómo se sirve: `references/stacks.md` (HTML suelto, Next.js/Astro/Vite, Shopify, página con login, 3D, composiciones de video).
3. Reglas de seguridad:
   - **Shopify:** trabaja solo en un **tema de prueba**; nunca en el publicado, y nunca publiques un tema.
   - **Algo en producción:** arreglas en el código, pero **no despliegas** sin que te lo pidan o sin que la regla del proyecto lo diga.
   - No renombres ni muevas carpetas del proyecto.
   - Si otra sesión trabaja el mismo proyecto, no pises sus archivos: revisa y propone, o trabaja en una copia.
   - Antes de preparar algo **para mandarlo a otra persona** (un video por WhatsApp, un PDF a un cliente), revisa en las notas del proyecto si se puede mandar y qué versión.
4. Guarda capturas e informes **fuera del repo**: en el scratchpad de la sesión o en `/tmp/revision-movil/<proyecto>/`. Nunca dentro de una carpeta con git (salvo que esté en `.gitignore`).

## 2 · Medir en todos los dispositivos

```bash
python3 <skill>/scripts/revisar.py <url | archivo.html | carpeta> \
  --salida /tmp/revision-movil/<proyecto>/antes [--ruta / --ruta /productos] [--esperar 3000]
```

- Por defecto revisa **15 dispositivos**: 7 teléfonos (iPhone SE, iPhone, Pro Max, Android chico de 360 px, Android grande, Galaxy Fold cerrado de 344 px, iPhone acostado), 4 tabletas (iPad mini, iPad vertical, iPad horizontal, Galaxy Tab) y 4 compus (laptop Windows 1366, MacBook Air, MacBook Pro 16", monitor 2560). Lista y medidas: `python3 <skill>/scripts/dispositivos.py`.
- Grupos: `--dispositivos rapido` (iPhone, Android chico, iPad, MacBook Air) para ir y venir mientras arreglas; `completo` para la revisión inicial y la final. También `telefonos`, `tabletas`, `compus`, `mac` o claves sueltas separadas por comas.
- Un archivo o carpeta local lo sirve solo por http (con `file://` se rompen módulos JS, fuentes y fetch).
- `--esperar 3000` para páginas con animaciones de entrada o 3D; mejor aún `--esperar-a "<expresión JS>"` cuando el 3D o la CDN tardan distinto cada vez. `--sin-scroll` si la página secuestra el scroll; `--red-lenta` para ver cuánto tarda en 4G.
- **Banner de cookies:** mira primero la página CON el banner (es lo que ve la gente al entrar: ¿tapa el botón principal?) y luego mide con `--cookies rechazar`.
- Lo que el visitante no ve se ignora solo: la barra de vista previa de Shopify, la de admin y los textos solo para lectores de pantalla.
- Revisa **cada página importante**, no solo la portada: producto, carrito, formulario, ficha (`--ruta` repetido).

Sale: `hoja.png` (todas las pantallas lado a lado), `informe.md` (problemas agrupados por gravedad y en qué dispositivos), y por dispositivo `pantalla.png`, `completa.png`, `marcado.png` (la completa con los problemas numerados en rojo/naranja) y `datos.json`.

## 3 · MIRAR las capturas (no te lo saltes)

Abre con Read: `hoja.png` y, como mínimo, `pantalla.png` y `completa.png` de **iphone-se, android-chico, plegable, iphone-acostado, ipad, ipad-acostado, macbook-air y monitor**, además de `marcado.png` donde haya errores. Pregúntate lo de `references/checklist.md` § "Lo que se ve". Lo esencial:

- ¿Lo más importante (título, producto, precio, botón principal) se ve **sin hacer scroll** en un teléfono?
- ¿Algo se ve **cortado, encimado, chiquito, deformado o fuera de centro**? ¿Hay **huecos raros**?
- ¿El texto **se lee** a ese tamaño? ¿Contrasta con el fondo?
- ¿En el iPhone acostado sigue usable, o la cabecera fija se come media pantalla?
- ¿En el iPad parece una versión pensada, o un celular estirado / una compu encogida?
- ¿En el monitor grande el contenido queda **centrado** con un ancho razonable, o pegado a un lado / estirado de orilla a orilla? (el script lo marca como `contenido-pegado-a-un-lado`, pero míralo igual).

Apunta cada cosa que veas; el informe del script no la tiene.

## 4 · Tocar: que FUNCIONE

El informe trae al final "Qué hay que probar a mano" (menús, carruseles, formularios, diálogos, canvas, videos). Escribe un guion de pasos y córrelo:

```bash
python3 <skill>/scripts/tocar.py <url|archivo> --pasos pasos.json \
  --dispositivos rapido --salida /tmp/revision-movil/<proyecto>/tocar
```

Formato de los pasos y todas las acciones en la cabecera de `scripts/tocar.py` (`tocar`, `tocar_texto`, `tocar_en` (un punto: para canvas/3D apunta al objeto, no al centro), `ver`, `no_ver`, `desplazar`, `recorrer`, `deslizar`, `arrastrar`, `escribir`, `teclado`, `rotar`, `tecla`, `atras`, `ir`, `captura`). Usa gestos de dedo reales (eventos touch) en teléfono y tableta, y ratón/trackpad en compu. Cada paso dice ✓/✗ y por qué: **tapado por** otra cosa, **sin efecto**, **scroll atrapado**, **no se mueve**, **el teclado lo tapa**, **se sale al girar**.

Prueba siempre, en al menos un teléfono, una tableta y la compu:
- `{"recorrer": true}`: que con el dedo se llegue **de arriba a abajo**.
- El menú: abrir, ver que se ve, tocar un link y cerrar.
- **Cada botón que vende o convierte** (Comprar, Reservar, WhatsApp, Enviar): que no esté tapado y que haga algo.
- Formularios: `escribir` con el teclado abierto, que el campo no quede tapado y que el botón de enviar se alcance.
- Carruseles: `deslizar`. 3D/mapas: `{"arrastrar": "canvas", "dx": -200, "pagina_quieta": true}` y `{"desplazar_sobre": "canvas", "dy": 400}` (hacia abajo mueve la página: el 3D no se roba el scroll). Si el 3D **a propósito** usa la rueda o el dedo para recorrer algo y luego suelta la página, usa `{"rueda_recorre": "canvas"}`.
- Diálogos/pop-ups: que se cierren (la X visible y tocable) y que no tapen todo.
- `{"rotar": true}` en un teléfono.

Para casos más finos usa `Sesion` como módulo de Python (ejemplo en el docstring de `tocar.py`). Para revisar un estado concreto (una ficha abierta, un modal), si la página acepta parámetros en la URL (`?abrir=…`), pásalos con `revisar.py --ruta "/?abrir=…"`.

**Secciones 3D o interactivas:** recetas y casos reales en `references/arreglos.md`. Lo más importante: prueba la rueda **con el bloque cortado** (medio fuera de la pantalla); prueba **dentro y fuera** del bloque; desliza **rápido** con el dedo; abre la ficha y mira que el botón de compra se vea también acostado y en una laptop de 768 px de alto; mide `renderer.info` (la Mac siempre va rápido y no te va a avisar); revisa las animaciones **cuadro a cuadro**; abre y cierra varias veces y comprueba que todo vuelve a su sitio. Y **nunca subas si la revisión de sintaxis falla** (en un `for … && subir`, el `&&` solo mira el último archivo: usa `node --check a.mjs || exit 1` por archivo), ni pongas un comentario `//` a media línea.

## 5 · Clasificar: arreglo directo o preguntar

**Lo obvio se arregla sin preguntar; lo que cambia el diseño o la función, se pregunta.** En el celular algunas cosas no pueden ser iguales que en la compu, y eso lo decide la persona.

**Arreglas directo** (mismo diseño y misma intención, solo adaptado al tamaño): textos o elementos cortados o que se salen; scroll de lado; botones chicos o pegados; letra ilegible; campos que hacen zoom en iPhone; fotos deformadas; `100vh` que brinca; barras fijas que tapan; muesca y barra de gestos; video sin `playsinline`/`muted`; medios más altos que la pantalla; banner de cookies que tapa el botón principal; espaciado y tamaños por dispositivo; ancho máximo y centrado en monitores; cosas que solo funcionaban con hover; imágenes pesadas; errores de JS.

**Preguntas** (cambia lo que la gente ve o hace): quitar o esconder contenido o una función en móvil; cambiar el patrón de interacción (un scroll vertical que pasa a carrusel, una tabla que pasa a tarjetas, un 3D que se cambia por foto en celulares lentos); reordenar secciones o poner el menú en otra forma; cambiar textos; cambiar el formato de un video; todo lo que no se pueda deshacer fácil.

Cómo preguntar: **una sola vez, todo junto** (con `AskUserQuestion` si está disponible; máx. 4 preguntas), cada una con la captura o la descripción concreta, tu recomendación como primera opción y por qué. **Mientras esperas, sigue arreglando lo obvio.** Si la persona no está, aplica tu recomendación solo si es fácil de revertir y déjalo apuntado como "decidí X, se cambia en 1 minuto si prefieres Y".

## 6 · Arreglar bien (no a parches)

Recetas probadas en `references/arreglos.md`. Principios:
- **Arregla la causa, no el síntoma**: un ancho fijo en px, un `100vh`, un contenedor sin `max-width`, un `flex` sin `flex-wrap`, un `min-width` olvidado. Nada de `overflow-x: hidden` en el body para esconder un desborde: eso corta contenido en vez de arreglarlo.
- Usa los **breakpoints y variables que el proyecto ya tiene**. Si no hay, mobile-first: estilos base para teléfono y `@media (min-width: 768px)` / `(min-width: 1024px)` / `(min-width: 1440px)` hacia arriba.
- Prefiere lo fluido a los saltos: `clamp()` para letra y espacios, `min()`, `max-width`, `aspect-ratio`, grid con `auto-fit/minmax`.
- Distingue **tamaño** (`width`) de **forma de uso** (`@media (hover: hover)`, `(pointer: coarse)`): un iPad horizontal mide como laptop pero se usa con el dedo.
- **No rompas la compu**: cada arreglo se comprueba también en macbook-air y monitor.
- En Shopify edita las secciones/snippets/CSS del tema de prueba; en Next.js/Astro, los componentes y estilos del proyecto.

## 7 · Volver a medir y comparar

```bash
python3 <skill>/scripts/revisar.py <lo mismo> --salida /tmp/revision-movil/<proyecto>/despues
python3 <skill>/scripts/comparar.py /tmp/revision-movil/<proyecto>/antes /tmp/revision-movil/<proyecto>/despues
python3 <skill>/scripts/tocar.py <lo mismo> --pasos pasos.json --dispositivos rapido,plegable,iphone-acostado,ipad-acostado --salida …/tocar-despues
```

Tiempos aproximados en una Mac reciente: `revisar.py` completo, 1-2 min (3D: 3-4 min); `tocar.py` ~20-40 s **por dispositivo**. Mientras iteras usa `rapido`; para el pase final, los 8 de arriba, y en segundo plano si dura más de 2 minutos.

`comparar.py` dice qué se resolvió, qué sigue y qué es **NUEVO** (un arreglo que rompió otra cosa: arréglalo antes de entregar) y arma `antes-despues.png`. Vuelve a **mirar** las capturas del después.

**Safari de verdad (iPhone/iPad, solo en Mac con Xcode):** el script usa el motor de Chrome. Safari tiene sus manías (barras que se esconden, teclado, `position: fixed`, video, 3D). Si la página tiene formularios, barras fijas, secciones a pantalla completa, video o 3D, o si el problema era de iPhone, haz el pase final en el **Simulador de iOS con Safari real**: `scripts/safari.py <url> --apagar` y, para tocar ahí, `references/safari-real.md`. Si no hay Xcode, dilo en la entrega como "no probado en Safari real".

## 8 · Entregar

Termina cuando:
- 0 errores rojos en los 15 dispositivos (o cada uno que quede está justificado);
- todos los pasos de `tocar.py` en ✓ en teléfono, tableta y compu;
- miraste el después en las capturas y nada se ve cortado, encimado, pegado a un lado ni perdido;
- la compu se ve igual o mejor que antes.

Mensaje corto y claro:

```
Listo: [proyecto] ya funciona en celular, tableta y compu.

Arreglé (lo vas a notar en el celular):
- [qué veía la gente antes → qué ve ahora], uno por línea, lo más importante primero

Necesito que decidas: (solo si hay)
- [pregunta con mi recomendación]

Lo que no pude comprobar: (si aplica — p. ej. "no lo probé en Safari real, solo en el motor de Chrome")

Antes / después: [ruta de antes-despues.png o hoja.png]
```

Si un aviso viene del tema o de la plantilla base y no de lo que se construyó, dilo aparte: arreglarlo podría tocar todo el sitio. Si escondiste algo que estaba roto (una imagen o un video que no existe), dilo: esconderlo no lo arregla. Si el proyecto se despliega, vuelve a correr `revisar.py --dispositivos rapido` contra la URL de producción: un cambio no está hecho hasta verse bien ahí.

## Archivos de la skill

| Archivo | Para qué |
|---|---|
| `scripts/paso0.py` | Revisa lo que necesita la skill y, con permiso, instala lo que falta |
| `scripts/revisar.py` | Medir en 15 dispositivos: capturas, problemas, informe |
| `scripts/auditoria.js` | Lo que se mide dentro de la página (lo usa revisar.py) |
| `scripts/tocar.py` | Usar la página con el dedo / ratón y ver qué falla |
| `scripts/comparar.py` | Antes vs después |
| `scripts/revisar_archivo.py` | Videos, imágenes y PDFs para celular (+ versión ligera) |
| `scripts/safari.py` | Primera pantalla en Safari REAL (simuladores de iPhone/iPad, Mac con Xcode) |
| `scripts/sesion.py` | Guardar la sesión de una página con login (la persona entra ella misma) para `--estado` |
| `scripts/dispositivos.py` | La lista de dispositivos (añadir uno = una línea) |
| `guia/estilo.md` | Cómo se da la guía (en vivo, cercana, con seguimiento) |
| `guia/leccion-1.md` … `leccion-3.md` | La mini guía interactiva (~5 min) |
| `guia/ejemplo/` | Página de ejemplo con errores, para la guía si la persona no tiene una a la mano |
| `references/checklist.md` | Qué mirar y qué probar, por tipo de dispositivo |
| `references/arreglos.md` | Recetas para cada problema típico |
| `references/construir-bien.md` | Reglas para construir ya adaptado desde el principio |
| `references/stacks.md` | Cómo servir/probar cada tipo de proyecto |
| `references/safari-real.md` | Pase final en Safari real con el Simulador de iOS |
| `references/videos-y-archivos.md` | Videos, imágenes y PDFs para celular |
