# Cómo servir y probar cada tipo de proyecto

`revisar.py` y `tocar.py` reciben una **URL**, un **archivo .html** o una **carpeta**. Para todo lo que no sea HTML suelto, levanta el servidor del proyecto y pásales la URL de localhost.

Para levantar servidores usa la herramienta de vista previa del entorno (`preview_start` con `.claude/launch.json`) si está disponible; si no, Bash con `run_in_background`. Apaga lo que levantes al terminar.

## HTML suelto (landings de una página, propuestas en HTML, prototipos)
Pasa el archivo directamente: `revisar.py ruta/index.html`. El script lo sirve por http (con `file://` fallan los módulos, `fetch` y algunas fuentes). Si hay varias páginas: `revisar.py carpeta --ruta / --ruta /otra.html`.

## Next.js, Astro, Vite y parecidos
- `npm run dev` (o `pnpm dev`) en segundo plano, espera a que diga "Ready"/"Local:", y revisa `http://localhost:<puerto>` con varias `--ruta`.
- Para ver el resultado real (sin la capa de desarrollo): `npm run build && npm start` o la **URL de producción**.
- **Si el proyecto está en producción:** revisar, sí; arreglar en el código, sí; desplegar, solo si el usuario lo pide o la regla del proyecto lo dice. Las páginas con login: `sesion.py` (el usuario entra él) y luego `--estado`.
- Tras desplegar, revisa la URL de producción con `--dispositivos rapido`.

## Shopify
- Lee primero las notas del proyecto. **Trabaja solo en un tema de prueba**; nunca en el tema publicado, y nunca publiques un tema.
- Prototipos locales (una sección 3D, por ejemplo): se revisan como HTML suelto o con el servidor local que use el proyecto.
- Dentro de la tienda: la vista previa del tema es `https://<tienda>/<ruta>?preview_theme_id=<id>`. Si la tienda está en modo privado, guarda una sesión con `sesion.py <url de preview> /tmp/revision-movil/tienda/estado.json` (el usuario escribe la contraseña él mismo) y usa `--estado`.
- Tras subir un cambio, la vista previa tarda unos 5-8 s en cargar el CSS nuevo: usa `--esperar 8000` en la primera pasada; para un 3D pesado desde la CDN, `--esperar-a` con la señal de "listo" de la escena.
- Usa `--cookies rechazar` (pulsa "Rechazar" del banner) después de haber mirado una vez la página con el banner. La barra de vista previa de Shopify (`#PBarNextFrameWrapper`) se ignora sola.
- Los errores de consola de scripts de Shopify o de apps salen aparte, como "terceros": normalmente no son del proyecto.
- Lo que va **dentro** de la tienda se prueba **en la tienda**, no solo suelto: la cabecera, el anuncio de arriba y el pie cambian el alto disponible y el scroll.

## Composiciones de video (HyperFrames / Remotion) y páginas que reproducen video
- La composición en sí es un video: revisa el **MP4 renderizado** con `revisar_archivo.py`.
- La página que muestra los videos es una web: `revisar.py` (detecta `media-mas-alta-que-pantalla`, `playsinline`, peso).

## 3D / WebGL / three.js
- Usa `--esperar 3000-5000` para que cargue la escena.
- En Mac el script usa la GPU real (Metal): las capturas y los gestos salen a la velocidad real. Ten en cuenta que **un teléfono es mucho más lento que una Mac**: si el 3D es el centro de la página, pruébalo también en Safari real o en un teléfono físico de gama media.
- `tocar.py`: `arrastrar` sobre el `canvas` (¿gira?), `recorrer` (¿la página sigue bajando o el 3D se come el gesto?) y `tocar` sobre el protagonista (¿abre la ficha?). El script compara la imagen antes y después y descuenta lo que la escena se mueve sola.

## Páginas con login o detrás de contraseña
`python3 scripts/sesion.py <url> /tmp/revision-movil/<proyecto>/estado.json` abre una ventana visible; **el usuario entra él mismo** (Claude nunca escribe contraseñas reales) y la cierra. Después usa `--estado` con ese archivo en `revisar.py` y `tocar.py`. Borra el archivo al terminar: contiene cookies de sesión. Si el usuario no está, revisa lo que sea público y deja anotado lo que faltó por revisar.
