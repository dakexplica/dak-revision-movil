# Checklist: qué mirar y qué probar

Úsalo en el paso 3 (mirar capturas) y el paso 4 (tocar). Lo que ya mide `revisar.py` está marcado con ⚙️: igual míralo en la captura, pero no hace falta buscarlo a ojo.

## Índice
1. Lo que se ve (todas las pantallas)
2. Teléfonos: lo que siempre falla
3. iPhone / Safari en particular
4. Android en particular
5. Tabletas (iPad y Android)
6. Compus: MacBook, laptop Windows, monitor grande
7. Funcionamiento (con el dedo)
8. Velocidad y datos móviles

---

## 1. Lo que se ve (en todas las pantallas)

- [ ] **Primera pantalla**: sin hacer scroll se entiende qué es, y se ve el título, el producto o la oferta y el botón principal. En teléfono, el botón principal está en la mitad de abajo, donde llega el pulgar.
- [ ] ⚙️ Nada **se sale de lado** ni se **corta** en el borde. Ojo con los títulos largos en letra grande: una palabra como "especialidad" a 64 px no cabe en 360 px.
- [ ] Nada **encimado**: texto sobre texto, botón sobre foto importante, cabecera fija sobre el título.
- [ ] **Proporciones**: el protagonista (producto, cara, logo) ocupa un tamaño digno. Si en la compu llena la pantalla y en el teléfono queda como estampilla, está mal aunque "quepa".
- [ ] **Centrado**: lo que debe estar centrado lo está en todos los anchos. Escenas 3D y fotos con `object-fit: cover` suelen recortar al protagonista en vertical; revisa el `object-position` o el encuadre de la cámara.
- [ ] ⚙️ **Letra legible**: cuerpo de 16 px en teléfono y nada informativo por debajo de 12 px. El texto sobre una foto debe contrastar (capa oscura o sombra).
- [ ] **Jerarquía**: en teléfono, título, subtítulo y cuerpo siguen viéndose distintos. Si el `h1` baja a 22 px y el cuerpo es de 16 px, se pierde.
- [ ] **Espacios**: ni pegado a los bordes (mínimo 16 px a los lados en teléfono) ni con huecos enormes entre secciones, que pasa cuando un padding de compu de 120 px se queda igual en el teléfono.
- [ ] ⚙️ **Fotos**: no deformadas, no pixeladas, no rotas, y que no recorten justo lo importante.
- [ ] **Tablas y comparativas**: en teléfono se leen sin scroll lateral, o tienen un scroll lateral obvio con una sombra que indique que hay más.
- [ ] **Modo oscuro del sistema**: si la página no lo maneja, que al menos no salga texto negro sobre fondo negro. Samsung Internet oscurece páginas por su cuenta.

## 2. Teléfonos: lo que siempre falla

- [ ] ⚙️ Barras fijas (cabecera, botón de WhatsApp, banner de cookies, barra de "comprar") que juntas tapan demasiado. Con el teléfono **acostado** la cabecera fija puede comerse la mitad de la pantalla: escóndela al bajar o redúcela.
- [ ] ⚙️ Secciones de `100vh`: en el celular brincan o se cortan abajo. Usa `svh`/`dvh`.
- [ ] El menú de hamburguesa abre, tiene un área tocable grande, se ve encima de todo (`z-index`), se cierra con X y al tocar un link, y no deja la página de atrás moviéndose.
- [ ] Pop-ups y diálogos: caben en la pantalla, la X se ve y se toca, y se puede hacer scroll dentro si son largos.
- [ ] El **plegable cerrado (344 px)** es la prueba más dura de ancho. Si ahí aguanta, aguanta en cualquier parte.
- [ ] **Muesca, Isla Dinámica y barra de gestos**: nada importante pegado arriba ni abajo del todo en una página a pantalla completa (`env(safe-area-inset-*)`).

## 3. iPhone / Safari en particular

- [ ] ⚙️ Campos de formulario con letra **< 16 px**: Safari hace zoom al tocarlos y la página queda descuadrada.
- [ ] ⚙️ Video: `autoplay` solo funciona con `muted playsinline`. Sin `playsinline` se abre a pantalla completa.
- [ ] `position: fixed` y el teclado: en Safari una barra fija de abajo puede subirse encima del teclado o quedarse flotando en medio.
- [ ] Hover pegajoso: en iPhone el primer toque activa el `:hover` y a veces hay que tocar dos veces. Los menús que abren con hover deben abrir también al tocar.
- [ ] `background-attachment: fixed` no funciona en iOS (el fondo se ve estirado o borroso).
- [ ] Pase final en **Safari real** con el Simulador (`safari-real.md`) cuando la página tenga formularios, barras fijas, pantalla completa, video o 3D.

## 4. Android en particular

- [ ] El ancho más común en Android es **360 px** (Galaxy A, Motorola, Xiaomi): más angosto que cualquier iPhone actual. Lo que en el iPhone apenas cabe, aquí se sale.
- [ ] Mínimo tocable de **48 px** (Material Design), un poco más que el de iPhone.
- [ ] El botón o gesto **"atrás"** del sistema se usa muchísimo: si abres un modal, una galería o un menú, que "atrás" lo cierre en vez de sacar a la persona de la página (si es fácil: `history.pushState` al abrir y `popstate` para cerrar).
- [ ] El teclado de Android **encoge la pantalla** (cambia el alto visible). Un diseño que depende del alto exacto se aplasta.
- [ ] Fuentes: si no se carga la fuente web, Android usa Roboto, que es más ancha. Revisa que nada dependa de que el texto "quepa justo".
- [ ] Rendimiento: un Android de gama media es **3-5 veces más lento** que un iPhone. El 3D, los videos de fondo y las animaciones pesadas se sienten primero aquí.

## 5. Tabletas (iPad y Android)

- [ ] **No es un celular grande ni una compu chica.** En vertical (744-834 px) suele caer justo en el "hueco" entre el diseño de teléfono y el de compu: revisa que no quede una columna de teléfono estirada a 800 px con letras enormes, ni el diseño de compu apretado.
- [ ] iPad horizontal (1180 px) recibe el diseño de compu, **pero se usa con el dedo**: los menús de hover tienen que funcionar al tocar y los botones deben ser grandes. Para eso es `@media (hover: none)` / `(pointer: coarse)`, no el ancho.
- [ ] El iPad pide por defecto la "versión de escritorio" (se presenta como Mac): si la página detecta el "móvil" por el user-agent, al iPad le toca la experiencia de compu sin hover. Detecta por **capacidades**, no por marca.
- [ ] Textos largos: en tableta no deben ir de borde a borde. Máximo unos 70 caracteres por línea (`max-width: 65ch`).
- [ ] Rotar: lo que se veía bien en vertical debe seguir funcionando en horizontal y al revés.

## 6. Compus: MacBook, laptop Windows, monitor grande

- [ ] **Laptop Windows de 1366×650 de alto útil**: la pantalla más corta de todas. Los heros de `100vh` con mucho contenido se cortan; el botón principal queda debajo del pliegue.
- [ ] **MacBook (1470-1728 px, pantalla Retina)**: fotos y logos nítidos (al doble de resolución o en SVG).
- [ ] **Monitor de 2560 px**: el contenido no se estira de lado a lado (usa `max-width` de 1200-1440 px para el contenido y deja que los fondos sí lleguen al borde). Los textos no quedan diminutos en medio de un mar vacío y las imágenes de fondo no se pixelan.
- [ ] El **hover existe** aquí: está bien usarlo, siempre que no sea la única forma de llegar a algo.
- [ ] Barra de scroll de Windows: `100vw` incluye la barra, así que un elemento de `100vw` provoca scroll horizontal en Windows (en Mac no se nota).

## 7. Funcionamiento (con el dedo)

- [ ] `recorrer`: de arriba abajo con el dedo, sin quedarse atrapado. Las secciones con scroll secuestrado (pin, scroll horizontal, 3D que roba el gesto) deben **soltar** al llegar a su final.
- [ ] Gestos: si una zona se arrastra (3D, mapa, carrusel), deja claro qué gesto es de la zona y cuál de la página. Patrón sano: horizontal para la zona y vertical para la página (`touch-action: pan-y`). Un 3D que bloquea el scroll vertical atrapa a la gente.
- [ ] Cada botón que convierte (Comprar, Reservar, WhatsApp, Enviar) responde **al primer toque**, no está tapado y tiene respuesta visual (cambia de color o se carga).
- [ ] Formularios: el teclado correcto (`type="email"`, `type="tel"`, `inputmode="numeric"`), el campo visible con el teclado abierto, el botón de enviar alcanzable, los errores visibles y el autocompletado activado (`autocomplete`).
- [ ] Links de teléfono y WhatsApp: `tel:` y `https://wa.me/…` abren la app.
- [ ] El botón "atrás" del navegador funciona (en una sola página con estados, no saca a la persona).
- [ ] Carruseles: se pueden deslizar con el dedo **y** tienen otra forma de avanzar (puntos o flechas grandes) para quien no sabe que se desliza.
- [ ] Nada depende solo de **hover** ni de **doble clic** ni de **clic derecho**.

## 8. Velocidad y datos móviles

- [ ] Con `--red-lenta` (4G lento) lo de arriba aparece en menos de ~3 s y no "brinca" al cargar (las fotos llevan `width`/`height` o `aspect-ratio`).
- [ ] ⚙️ Fotos a la medida (`srcset`/`sizes`, WebP/AVIF), nada de JPG de 2400 px y 2 MB para mostrarlo a 375 px.
- [ ] Videos de fondo: versión ligera para móvil (≤ 2-4 MB) o un póster. En datos móviles, que no bajen 100 MB.
- [ ] 3D: limita `pixelRatio` a 2 en móvil, carga los modelos comprimidos (Draco/meshopt, KTX2) y ten un plan B (foto) si el teléfono no da.
- [ ] 3D en el teléfono: mide `renderer.info.render.calls`/`.triangles` en la vista del teléfono (la Mac no muestra la lentitud). Material estándar en vez de físico para lo repetido; nada de capas transparentes que no se ven.
- [ ] 3D dentro de un bloque: que la rueda **encaje** el bloque entero antes de mover nada, que suelte al final y que el recorrido llegue a centrar la última sección.
- [ ] Animaciones de "sale y gira": en un solo movimiento y sin atravesar a los vecinos (revisado cuadro a cuadro).
- [ ] Deslizar con el dedo: pegado al dedo, y al soltar frena suave (muelle sin rebote) justo en un elemento, con tope por gesto.
- [ ] Lo que se centra "en el hueco libre" se mide desde el contenedor, no desde la ventana (si no, el margen de la página lo corre).
- [ ] ⚙️ Cero errores de JavaScript en consola: un error en móvil puede dejar muerta toda la interacción.
