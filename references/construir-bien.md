# Construir ya adaptado (modo "desde el principio")

Arreglar al final cuesta el triple que construir bien desde el principio. Mientras creas cualquier cosa visual (landing, tienda, app, propuesta HTML, 3D, video), aplica esto **desde el primer borrador**, y antes de decir "listo" corre la revisión (pasos 2-8 del SKILL.md).

## Las 12 reglas

1. **Empieza por el teléfono de 360 px.** Si el diseño funciona a 360, se agranda con gusto; al revés casi nunca sale bien. Estilos base = teléfono; `@media (min-width: …)` hacia arriba.
2. **Nada de anchos fijos en px** para contenedores, filas ni tarjetas: `width: 100%` + `max-width`, `minmax()`, `clamp()`.
3. **Tipografía fluida**: `font-size: clamp(min, preferido, max)` en títulos; cuerpo de 16 px; campos de formulario de 16 px o más.
4. **Alturas con `svh`/`dvh` y `min-height`**, nunca `height: 100vh`.
5. **Todo lo tocable de 44 px como mínimo** (48 en Android), con 8 px de separación.
6. **El hover es un extra, nunca el camino.** Lo que aparece con hover también debe aparecer al tocar (o estar visible en táctil).
7. **Imágenes con `width`/`height` o `aspect-ratio`** (para que no brinque la carga), `object-fit` y `srcset`. Video con `muted playsinline` y póster.
8. **Barras fijas mínimas**: una cabecera baja y, como mucho, un botón flotante. Con `env(safe-area-inset-*)` si van a pantalla completa.
9. **Gestos claros**: si algo se arrastra (3D, carrusel, mapa), solo en un eje, y la página sigue pudiendo bajar.
10. **Tableta y monitor también existen**: un breakpoint pensado para 744-1023 px y un `max-width` para pantallas de 1440 px o más.
11. **Medios que caben**: ningún video, iframe ni imagen principal más alto que `80svh` en teléfono.
12. **Ligero**: fotos en WebP/AVIF a la medida, el 3D con `pixelRatio ≤ 2`, y los videos de fondo en versión móvil.

## Mientras construyes
- Cada vez que termines una sección, corre `revisar.py --dispositivos rapido` (unos 15 segundos) y mira la hoja. Detectar un problema en una sección cuesta un minuto; detectarlo al final cuesta una tarde.
- Si el diseño viene de una referencia de escritorio (captura de compu, web de Awwwards), **decide tú la versión de teléfono antes de programar**: qué se apila, qué se esconde, qué se vuelve carrusel. Si eso cambia el contenido, pregúntale al usuario al principio, no al final.

## Para video (HyperFrames / Remotion / otras herramientas de video)
- Si va a verse en celular (Reels, TikTok, historias, WhatsApp), **compón en 9:16 desde el principio**. No recortes un 16:9.
- Deja lo importante dentro de las zonas seguras (`videos-y-archivos.md`).
- Texto: mínimo ~48 px de alto de letra en un lienzo de 1080×1920 (se ve a 390 px de ancho en el teléfono, o sea 2.8 veces más chico).
- Al terminar: `revisar_archivo.py <video> --para <destino>` y mira `zonas-seguras.png` y `en-celular.png`.
