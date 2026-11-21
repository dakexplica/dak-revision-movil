# Recetas de arreglo

Una receta por problema, ordenadas como salen en `informe.md`. Adáptalas al sistema del proyecto (Tailwind, CSS Modules, variables del tema de Shopify…), no las pegues tal cual si el proyecto ya tiene su forma.

## Índice
- Se sale de lado / contenido cortado
- Texto cortado
- Botones chicos o pegados
- Letra chica / campos que hacen zoom
- Barras fijas que tapan / muesca y barra de gestos
- 100vh
- Hover que no existe en el celular
- Fotos deformadas, pesadas o recortando lo importante
- Video en la web
- Medios más altos que la pantalla
- 3D / canvas
- 3D o carrusel dentro de un bloque (encaje, soltar al final) · animaciones que se atraviesan · 3D lento en el celular · panel que se aprieta · celular acostado
- Scroll secuestrado que atrapa
- Menú de hamburguesa
- Tablas
- Tableta (el "hueco" de 744-1024 px)
- Monitor grande
- Formularios y teclado

---

### Se sale de lado / contenido cortado (`scroll-horizontal`, `desborda-ancho`, `contenido-cortado`)
Busca el culpable con el selector del informe y mira su CSS. Causas típicas y su arreglo:
```css
/* ancho fijo → ancho fluido con tope */
.precios { width: 1100px; }                       /* ✗ */
.precios { width: 100%; max-width: 1100px; }      /* ✓ */

/* fila que no se acomoda → que baje de línea o pase a columna */
.fila { display: flex; flex-wrap: wrap; gap: 16px; }
.fila > * { flex: 1 1 260px; min-width: 0; }      /* min-width:0 evita que el contenido empuje */

/* grid fluido sin media queries */
.tarjetas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr)); gap: 16px; }

/* palabras o links largos */
.texto { overflow-wrap: anywhere; }

/* título enorme */
h1 { font-size: clamp(2rem, 6vw + 0.5rem, 4rem); }

/* 100vw incluye la barra de scroll (Windows) */
.full { width: 100%; }  /* en vez de 100vw */
```
Si el body ya tiene `overflow-x: hidden`, **no lo uses de excusa**: el contenido sigue cortado. Arregla el elemento y deja el `overflow-x: clip` en el body solo como red de seguridad.

### Texto cortado (`texto-recortado`)
Una caja de alto fijo con `overflow: hidden`. Quita el `height` y usa `min-height`. Si de verdad debe recortarse (resúmenes), hazlo a propósito con puntos suspensivos:
```css
.resena { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
```

### Botones chicos o pegados (`toque-chico`, `toque-muy-chico`, `toques-pegados`)
Agranda el **área tocable** sin agrandar el dibujo:
```css
.icono-link { display: inline-grid; place-items: center; min-width: 44px; min-height: 44px; }   /* 48px si es app Android */
.iconos { display: flex; gap: 8px; }
/* o ampliar el área con un pseudo-elemento */
.x-cerrar { position: relative; }
.x-cerrar::after { content: ""; position: absolute; inset: -12px; }
```
Los links dentro de un párrafo están exentos; los de un menú o un pie de página **no**.

### Letra chica (`letra-diminuta`, `parrafo-chico`) / campos que hacen zoom (`input-zoom-ios`)
```css
body { font-size: 16px; line-height: 1.5; }
small, .legal { font-size: max(12px, 0.8rem); }
input, select, textarea { font-size: max(16px, 1rem); }   /* evita el zoom automático de iPhone */
```
**No** arregles el zoom con `maximum-scale=1` en el viewport: bloquea el zoom a quien lo necesita.

### Barras fijas que tapan (`fijos-tapan`) / muesca y barra de gestos (`safe-area`)
- Cabecera: más baja en teléfono (56-64 px) y, si es larga, que se esconda al bajar y vuelva al subir.
- Banner de cookies: compacto (una línea + botón) y que **no tape el botón principal**. Con "Aceptar" se va para siempre.
- Botón flotante (WhatsApp): de 56 px, con margen, y que no tape el botón de comprar ni el pie.
- Barras fijas abajo y pantallas completas:
```css
.barra-abajo { padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
.cabecera { padding-top: env(safe-area-inset-top); }
/* requiere <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"> */
```
- Que las anclas no queden debajo de la cabecera: `html { scroll-padding-top: 72px; }`.

### 100vh (`100vh`)
```css
.hero { min-height: 100vh; min-height: 100svh; }   /* svh = alto con las barras del navegador visibles: no brinca */
.app-pantalla-completa { height: 100dvh; }          /* dvh = se ajusta cuando las barras se esconden */
```
En la laptop de 650 px de alto un hero de `100svh` con mucho contenido se corta: usa `min-height` (nunca `height`) para que crezca.

### Hover que no existe en el celular (`solo-hover`)
```css
/* el efecto bonito solo donde hay ratón */
@media (hover: hover) and (pointer: fine) { .tarjeta:hover { transform: translateY(-4px); } }

/* menú que abría con hover: que también abra al tocar */
.menu:focus-within .sub, .menu.abierto .sub { display: block; }
```
```js
boton.addEventListener('click', () => {
  const abierto = menu.classList.toggle('abierto');
  boton.setAttribute('aria-expanded', abierto);
});
```
Lo que en la compu aparece al pasar el ratón (precio, botón "ver más" sobre una foto) en teléfono debe estar **visible siempre**.

### Fotos (`imagen-deformada`, `imagen-pesada`, `imagen-rota`)
```css
img { max-width: 100%; height: auto; }
.galeria img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; object-position: 50% 30%; }  /* 30% = más arriba, para no cortar caras/cuellos */
```
```html
<img src="foto-800.webp" srcset="foto-480.webp 480w, foto-800.webp 800w, foto-1600.webp 1600w"
     sizes="(min-width: 1024px) 50vw, 100vw" width="1600" height="1200" loading="lazy" alt="…">
```
Para fotos que en el teléfono necesitan **otro encuadre** (vertical en lugar de horizontal), usa `<picture>` con `<source media="(max-width: 767px)" srcset="foto-vertical.webp">`. Eso cambia lo que se ve: en caso de duda, pregunta.

### Video en la web (`video-playsinline`, `video-sin-muted`)
```html
<video autoplay muted loop playsinline preload="metadata" poster="poster.webp">
  <source src="video-vertical-720.mp4" media="(max-width: 767px)" type="video/mp4">
  <source src="video-1080.mp4" type="video/mp4">
</video>
```
(`<source media>` solo lo respetan algunos navegadores; para elegir de forma segura, cambia el `src` con JS según `matchMedia`.) El archivo: `revisar_archivo.py --para web --version-ligera` lo deja en 1080p, H.264 y con faststart.

### Medios más altos que la pantalla (`media-mas-alta-que-pantalla`)
Caso típico: un video vertical 9:16 a todo el ancho de un teléfono mide 1.8 veces el ancho, o sea más que la pantalla.
```css
/* alto útil = pantalla menos las barras fijas (cabecera, barra de pagar) */
:root { --barras: 140px; }                       /* mide las de tu página */
.muestra video, .muestra iframe, .muestra img {
  width: 100%; max-height: calc(100svh - var(--barras)); object-fit: contain; background: #000;
}
/* mejor aún: limitar el ANCHO para que la altura quepa (sin franjas negras) */
.muestra-vertical { width: min(100%, calc((100svh - var(--barras)) * 9 / 16)); margin-inline: auto; aspect-ratio: 9 / 16; }
```
Pasa también en la compu: un video vertical en una columna de 1000 px de ancho mide ~1800 px de alto. El mismo límite lo arregla.
Para YouTube/Vimeo usa `aspect-ratio: 16 / 9; width: 100%; height: auto;` en el iframe.

### 3D / canvas (`canvas-touch-action`, `canvas-resolucion`)
```js
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
// Encuadra AL PROTAGONISTA según la forma de la pantalla. En vertical el límite es el ANCHO:
// calcula la distancia para que el protagonista (no toda la escena) llene ~85% del ancho.
function encuadrar() {
  const aspecto = innerWidth / innerHeight;
  camera.aspect = aspecto;
  const vfov = THREE.MathUtils.degToRad(camera.fov);
  const hfov = 2 * Math.atan(Math.tan(vfov / 2) * aspecto);
  const ancho = protagonista.ancho / 0.85, alto = protagonista.alto / 0.85;   // en metros de la escena
  const dist = Math.max((alto / 2) / Math.tan(vfov / 2), (ancho / 2) / Math.tan(hfov / 2));
  camera.position.copy(protagonista.centro).add(new THREE.Vector3(0, 0, dist));
  camera.lookAt(protagonista.centro);
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
}
addEventListener('resize', encuadrar);
```
Ojo: "alejar la cámara" en vertical para que quepa **toda la escena** deja al protagonista chiquito (error típico con productos en 3D). Lo correcto suele ser lo contrario: en vertical, encuadrar más cerca **lo importante** (una camiseta, un producto) y empezar el recorrido ahí, no en la pared vacía. Mezcla suave entre el encuadre vertical y el original a partir de una proporción ~1.2 para no cambiar la compu.
```css
canvas { touch-action: pan-y; }  /* deja subir/bajar la página; el 3D se gira en horizontal */
```
- En teléfono, ajusta **qué** se ve: menos objetos a la vez, el protagonista más grande, la escena centrada en él, y **el punto de inicio** del recorrido sobre lo importante.
- Paneles y fichas encima del 3D (tarjeta de producto, selector de estilos): mide su hueco real y encaja el protagonista en el espacio que queda; en tableta vertical suele convenir el mismo "panel desde abajo" que en teléfono. Si eso cambia la experiencia (otro recorrido, menos objetos), pregunta.
- Pausa el render cuando el canvas no se ve (`IntersectionObserver`) y cuando la pestaña está oculta.
- Plan B: si el teléfono no da (pocos FPS o falla WebGL), muestra una imagen fija con el mismo encuadre.

### Scroll secuestrado que atrapa (`recorrer` → "scroll atrapado")
Una sección fijada (pin) que convierte el scroll vertical en movimiento horizontal o en animación **tiene que soltar** al final:
- Con GSAP ScrollTrigger: `pin: true, end: "+=" + distancia` (que el `end` sea finito) y `anticipatePin: 1`; en móvil suele bastar con `ScrollTrigger.normalizeScroll(true)` y probar con el dedo.
- Si es un carrusel horizontal con el dedo: hazlo con **scroll nativo** (`overflow-x: auto; scroll-snap-type: x mandatory`), que el sistema ya sabe soltar en el borde, en lugar de `wheel`/`touchmove` con `preventDefault`.
- Si la sección escucha `touchmove` con `preventDefault()`, solo debe hacerlo para el gesto horizontal: si `|dy| > |dx|`, deja pasar el evento.
La regla en una frase: *en el iPhone el scroll va hacia la derecha y, al llegar al final, puedes seguir a la siguiente sección.*

### 3D o carrusel dentro de un bloque de la página (rueda dentro = zona, fuera = página)
Caso real (un vestuario 3D con camisetas colgadas): *"a veces se ve cortado arriba o abajo y ya empezó la animación"* y *"nunca llega a las últimas"*. Lo que funcionó:
- **Encaje antes de capturar:** si la rueda llega con el bloque cortado y se ve más del ~55 %, `preventDefault` y `scrollTo({behavior:'smooth'})` hasta dejarlo **entero y centrado** bajo la cabecera. Durante ~0,5 s la rueda no mueve nada, porque si no la zona arranca a medias. Solo después la rueda mueve la zona.
- **Soltar en los extremos con una pausa corta:** al llegar al final, durante ~0,4 s se tragan los golpes de la rueda (la inercia del trackpad no se salta la sección) y luego la página sigue. Al revés igual: al principio del recorrido, la rueda hacia arriba sube la página.
- **Recorrido hasta centrar lo último:** el límite no es "hasta que entre la orilla", sino hasta que la **última sección quede centrada** (y la primera al inicio). Se ve un poco más de fondo en las orillas, y eso está bien.
- **Fuera del bloque (márgenes blancos) la rueda siempre baja la página.** El trackpad de lado sí mueve la zona.
- En la ficha que se abre encima: al abrirla, si el bloque no está entero, encájalo; si no, el botón de compra queda fuera de la pantalla.
- Antes de cambiar un comportamiento que el usuario ya vio, **guarda la versión** (`versiones/<fecha> <qué>/` con un LEEME de cómo volver).

### Animaciones: que nada atraviese nada y que vaya en UN solo movimiento
- Objetos colgados o apilados (camisetas en un tubo): mide cuánto sobresalen los vecinos hacia la cámara (en el vestuario, las mangas llegaban a ~0,31 m). El que sale tiene que pasar **más adelante** que eso.
- **Nunca en dos pasos** ("primero sale, luego gira"): la gente lo nota al instante. Ata el giro a lo que ya avanzó (`giro = smoothstep(z, 0.10, salida·0.88)`) y, al volver, deja que entre a la vez que recupera su ángulo (`z ≤ salida·√(lo que le falta girar)`).
- El momento del giro importa: si empieza apenas se despega (`z ≈ 0,10`), a medio camino ya gira y la manga del vecino se le mete. Que salga primero de costado y gire en el **último tramo** (`smoothstep(z, salida·0,45, salida·0,97)`), con la salida un poco más rápida que el giro: sigue siendo un solo movimiento.
- **Si los objetos están inclinados, "salir recto" no basta:** al avanzar se acercan al plano del vecino. No lo arregles con horarios ("sale y luego gira"): mide. Modela cada objeto visto desde arriba (segmento + margen) y busca una **ruta** sin choques en una rejilla (desplazamiento lateral, salida y giro), donde salida y giro solo avancen. Al volver se recorre la misma ruta hacia atrás, así queda igual en los dos sentidos. El que sale espera si se metería en el camino del que vuelve. Mide el mínimo de distancia **en movimiento**, barriendo con el ratón de izquierda a derecha, al revés y en zigzag, y en todas las variantes; no solo en reposo.
- Cuidado con un colchón de margen demasiado grande: la búsqueda puede no encontrar ruta y la animación se queda atorada. Prueba márgenes de mayor a menor y comprueba con capturas que el objeto **llega**.
- **La suavidad gana a la exactitud.** En el vestuario, una ruta calculada que garantizaba cero roces se veía "rápida y mal", y un tope que frenaba cada paso que chocaba dejaba camisetas **atoradas** fuera de su sitio. El usuario prefirió el movimiento suave con algún roce mínimo. Antes de cambiar un movimiento que ya le gusta: guárdalo, pon lo nuevo como **opción con botón** para comparar y compruébalo en video (también que todo vuelve a su sitio al soltar: mide "las que no están en su sitio" tras retirar el ratón).
- Cuando el usuario dude de una colocación o distribución, dale **opciones reales en la página** (botones solo en la copia con `?opciones`) y una imagen comparativa compu + celular con nombres. Decide mejor viéndolo que leyéndolo.
- Mientras el recorrido se mueve rápido con el ratón, no adelantes objetos bajo el cursor: si no, se apartan y se amontonan. En el teléfono es al revés: **sí** debe salir el del centro mientras deslizas. Si solo sale al pararse, se siente "muerto" y "no me las agarra".
- Verifícalo **cuadro a cuadro** (capturas cada ~60 ms en Playwright) y mándale al usuario un video corto (`record_video_dir` de Playwright → mp4 con calidad media).

### 3D lento en el celular (aunque en la Mac vuele)
La gráfica de la Mac esconde la lentitud: en Playwright, el 3D va a más de 100 fps aunque en un iPhone se arrastre. No midas fps: mide **cuánto se dibuja** con `renderer.info.render.calls` y `.triangles` en la vista del teléfono.
- Capas transparentes que cubren todo el objeto y no se ven (por ejemplo, un dibujo de tela que la foto ya trae) cuestan el doble de pintar: ocúltalas en el teléfono y deja solo la del objeto abierto. En el vestuario bajó de 624 000 a 297 000 triángulos.
- `MeshPhysicalMaterial` (sheen, clearcoat) → `MeshStandardMaterial` en táctiles, para los objetos repetidos (`MeshStandardMaterial.prototype.copy.call(new MeshStandardMaterial(), fisico)`). Cambia también `customProgramCacheKey`.
- Baja la resolución sola si no llega a ~46 fps (2× → 1,75× → 1,5×, nunca menos: se nota borroso).
- Con el dedo, gira más por píxel que con el ratón (el objeto se ve más chico): en el vestuario, ×2.
- Compara antes y después **mirando** la captura del teléfono: tiene que verse igual.

### Deslizar con el dedo que se sienta "de iPhone" (carrusel, tubo 3D, galería)
Pedido típico: *"ya está mejor, pero hazlo aún más fluido al deslizar"*. Lo que funcionó en el vestuario:
- **Pegado al dedo:** mientras el dedo toca, lo que se mueve lo sigue casi sin retraso (suavizado alto, ~30). Un suavizado bajo (~9) se siente "de goma", ~0,1 s detrás.
- **Al soltar, un muelle crítico sin rebote**, no "inercia que frena + acomodo": `v += (w²·(destino−x) − 2w·v)·dt; x += v·dt` con `w≈8`. Arranca con la velocidad real del dedo, así que no hay salto.
- **Velocidad real:** guarda (tiempo, posición) de los últimos ~100 ms y calcula con eso; un promedio móvil de cada evento da tirones. Si el dedo se paró más de 90 ms antes de soltar, la velocidad es 0.
- **Destino = donde caería** (`x + v·0,22`), redondeado al elemento más cercano y con tope (máx. 5 elementos por gesto). Sin tope, un gesto rápido se lleva la sección entera.
- Las pestañas o los botones de "ir a" usan **el mismo muelle**, para que todo se mueva igual.
- Si el dedo toca mientras el muelle se mueve, el muelle se cancela y el dedo manda.
- Objeto abierto que se gira con el dedo: que el giro siga al dedo casi al instante (suavizado ~18), no a ~5.
- Para medirlo en Playwright: eventos `PointerEvent` sintéticos de tipo touch con `requestAnimationFrame` entre cada uno. Apunta el retraso entre lo que pide el dedo y lo que se pinta, y la trayectoria al soltar: tiene que ir siempre en la misma dirección (sin rebote) y terminar justo en un elemento.

### Variantes de un mismo producto en 3D (colores, equipaciones): una sola plantilla
- Si una variante se ve "más falsa" que otra, no se rehace desde cero: se usa la buena como **molde** (misma geometría, mismas coordenadas de textura) y la foto de la variante se **encaja píxel a píxel** sobre la imagen final de la buena (silueta + flujo óptico denso guiado por la estructura, muy alisado). Así los logos caen en el mismo sitio y la calidad es igual. Elige siempre las fotos **derechas** (no las giradas).
- Cambiar de variante en vivo traba si descargas, subes texturas y compilas al tocar el botón: **precalienta** (descarga, `renderer.initTexture`, `renderer.compileAsync`) un momento después de abrir la ficha. Mide el peor salto entre cuadros al cambiar (objetivo: menos de ~40 ms).

- **Nunca prepares algo pesado justo cuando el usuario va a tocar** (al abrir una ficha, al hacer clic): 1,3 s después de abrir es justo cuando gira la camiseta y se traba. Precalienta en ratos de calma (sin tocar, sin animación) y a trozos, abre imágenes grandes con `createImageBitmap`, y reutiliza los mismos programas (mismo texto de shader + valores por uniform) para no compilar. Mide los saltos de cuadro durante el primer gesto.
- Antes de un cambio grande que el usuario no ha visto, **guarda la versión** y ofrece lo nuevo como opción (`?opcion=`), con botones solo en la copia.

### Superficies a "puntitos" o "camuflaje" en 3D (sobre todo en el teléfono)
Dos piezas casi en el mismo sitio se pelean por quién se dibuja (z-fighting); en el teléfono, sin antialias, se nota más. Para encontrar la culpable: esconde pieza por pieza en la página (por rol o por tipo de geometría) hasta que sale limpio, **en la vista del teléfono**. Arreglo: `polygonOffset` en el material (hacia delante la que debe verse, hacia atrás la de dentro). En el vestuario era la barrita transparente de la percha detrás de la V del cuello. Si deformas un molde (p. ej. rellenar el pecho), lo que se calculó midiendo el molde (percha, accesorios) mídelo con el **original**, y deja fuera las piezas finas (ribetes) con una transición suave.

### Medidas en pantalla: siempre desde el contenedor, no desde la ventana
`getBoundingClientRect().left` es relativo a la **ventana**. Si un 3D o un canvas está dentro de un bloque con margen (la cápsula de la portada), réstale el `left` del bloque. Si no, todo lo que se centre "en el hueco libre" queda corrido por el margen. En el vestuario, la camiseta abierta se metía debajo de la tarjeta. Para comprobarlo, expón una función de revisión que dé la **caja en pantalla** del objeto (proyecta su `Box3` con la cámara) y mide los px de aire a cada lado en varias pantallas.

### Panel con alto máximo que se aprieta, y espacios que desaparecen
- Panel `display:flex; flex-direction:column; max-height; overflow:auto`: si no cabe, los hijos **se encogen** y la cabecera se sale por arriba. Pon `.panel > * { flex-shrink: 0 }` y deja que el panel se desplace.
- En compu, una ficha que se corta abajo se ve "rota": haz que quepa sin desplazarse (datos en casillas de 2 columnas, enlaces en una fila, versión compacta para `max-height: 880px`) y escala el objeto 3D con su **medida real proyectada** (px por metro a su profundidad) para que no se encime con la tarjeta de al lado.
- Texto suelto dentro de un botón `display:flex`: el espacio antes de un `<span>` se pierde ("cesta ·92"). Usa `&nbsp;`.

### Celular acostado
- Un `min-height: 520px` en un bloque hace que no quepa en 390 px de alto: usa `min-height: min(520px, calc(100svh - var(--header-height) - 16px))`.
- Lo que va junto al protagonista (una tarjeta, una foto) muchas veces no cabe acostado: escóndelo con `@media (max-height:520px) and (orientation:landscape)` y deja al protagonista grande.

### Menú de hamburguesa
```css
.nav-movil { position: fixed; inset: 0; z-index: 1000; overflow-y: auto; overscroll-behavior: contain; }
body.menu-abierto { overflow: hidden; }   /* que no se mueva la página de atrás */
.nav-movil a { display: block; padding: 14px 20px; font-size: 18px; }
```
Que se cierre con X, al tocar un link, con Escape y (en Android) con "atrás".

### Tablas
En teléfono, o bien un scroll lateral obvio:
```css
.tabla-envoltura { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tabla-envoltura table { min-width: 560px; }
```
o filas convertidas en tarjetas con `display: block` y `td::before { content: attr(data-label); }`. Pasar a tarjetas cambia cómo se lee la información: en caso de duda, pregunta.

### Tableta: el "hueco" de 744-1024 px
```css
@media (min-width: 744px) and (max-width: 1023px) {
  .tarjetas { grid-template-columns: repeat(2, 1fr); }   /* ni 1 columna estirada ni 4 apretadas */
  .contenido { padding-inline: 32px; }
}
@media (hover: none) and (pointer: coarse) { /* tableta o teléfono, sin importar el ancho */
  .boton { min-height: 48px; }
}
```

### Monitor grande
```css
.contenedor { width: min(100% - 32px, 1280px); margin-inline: auto; }
.texto-largo { max-width: 65ch; }
@media (min-width: 1920px) { :root { font-size: 18px; } }   /* opcional: que respire en pantallas enormes */
```

### Formularios y teclado
```html
<input type="email" autocomplete="email" inputmode="email" enterkeyhint="send">
<input type="tel" autocomplete="tel" inputmode="tel">
<input type="text" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
```
- El botón de enviar visible con el teclado abierto: evita barras fijas abajo mientras se escribe (`:focus-within` en el formulario para esconderlas).
- `scroll-margin-bottom` en los campos para que, al enfocarlos, no queden pegados al teclado.

## Lecciones de un vestuario 3D (personalizar camiseta y objetos bajo el banco)
- **Campos dentro de una hoja/ficha que se repinta:** al escribir, NO repintes la ficha entera (innerHTML): se pierde el foco y en el celular el teclado se cierra. Actualiza solo los textos que cambian (nombre, dorsal, botón). Inputs con `font-size:16px` o más (si no, iPhone hace zoom al tocar) y los campos arriba de la hoja (el teclado tapa la mitad de abajo).
- **Teclas de flecha globales** (pasar de producto con ← →): ignóralas si el foco está en un input, o el cliente cambia de ficha mientras escribe.
- **Probar en el tema de vista previa de Shopify:** la barra negra de "preview" (iframe abajo) se come los clics de Playwright cerca del borde inferior → usa `element.click()` por JS en esos botones.
- **3D: antes de colocar algo, mide dónde cae en pantalla** (`vector.project(camera)`): con una cámara casi horizontal, el suelo bajo un banco ocupa ~30 px y el borde de la tabla tapa lo que hay detrás. Ahí nada se ve "apoyado": parece pegado a la pared.
- **Zona para tocar en 3D:** si eliges "el objeto más cercano" con un umbral fijo (p. ej. ±0,14 en coordenadas de pantalla), en el teléfono el objeto ocupa medio ancho y casi todo toque se pierde. El umbral tiene que ser el ancho proyectado del objeto (proyecta su borde y mide).
- **Foto de carga de un 3D (cartel):** sácala del MISMO contenedor y tamaño que verá la gente (la cápsula de la portada, no una página a 2400 px): con otra proporción la cámara mira desde otro sitio y al aparecer el 3D se lee doble. Comprueba superponiendo foto y 3D al 50 %.
- **Shopify + Cloudflare:** tras muchas cargas automáticas, la 2ª carga en la misma sesión de Playwright devuelve "Just a moment…" (y /cart.js da 429). Contexto nuevo por carga, pausas, y la cesta pruébala a mano si hace falta.
- **Teclas globales:** un `keydown` en window que hace `preventDefault()` de Enter/espacio rompe botones, enlaces y textareas de TODA la página. Filtra por destino (`input,textarea,select,button,a,[contenteditable]`).

## Lecciones del pase final de un 3D en una tienda Shopify
- **Banner de cookies de Shopify:** en `tocar.py` usa `{"tocar": "#shopify-pc__banner__btn-decline"}`; `tocar_texto "Rechazar"` no entra y TODOS los pasos siguientes fallan en teléfono (el banner tapa la pantalla). En vista previa, la barra de Shopify (`iframe#PBarNextFrame`) puede tapar ese botón en tableta/compu: es falso positivo.
- **Teclado simulado ≠ teclado real:** `tocar.py` encoge la pantalla al 60 %; en un iPhone chico eso deja 217 px y marca "campo tapado". Antes de darlo por malo, compruébalo en Safari real (simulador: `tap` en el campo → `set_keyboard show` → `text`). El primer `text` a veces no entra: repítelo.
- **Zoom atrapado sobre un canvas:** si la sección frena la rueda (`preventDefault`), deja pasar `ctrlKey`/`metaKey` (pellizco del trackpad y Ctrl/Cmd + rueda) y usa `touch-action: … pinch-zoom`. Se verifica de verdad con CDP: `Input.synthesizePinchGesture` (acercar a 3x y alejar con el dedo ENCIMA del canvas; mira `visualViewport.scale`).
- **3D: "es del molde" se demuestra, no se supone.** Aísla el objeto sobre un color chillón y mira la silueta ampliada: el "pico del hombro" que parecía imposible era un escalón de 5 mm fácil de bajar.
