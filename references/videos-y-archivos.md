# Videos, imágenes y PDFs para el celular

Casi todo lo que se manda hoy (videos de lanzamiento, propuestas, carruseles, PDFs) **se ve en un celular**: por WhatsApp, Instagram, TikTok o una web abierta desde el teléfono. Que "se vea bien en la compu" no sirve de nada si en el teléfono el texto no se lee o los botones de la app lo tapan.

## El script
```bash
python3 ~/.claude/skills/dak-revision-movil/scripts/revisar_archivo.py <archivo> \
  --para reels,whatsapp \
  --salida /tmp/revision-movil/<proyecto>/<archivo> [--version-ligera]
```
`--para` acepta uno o varios destinos separados por comas: `reels`, `tiktok`, `shorts`, `historias`, `feed`, `whatsapp`, `web`, `youtube` (o `auto`).
- **Video**: comprueba la proporción contra cada destino, el códec, el color (`yuv420p`, sin el cual muchos teléfonos lo ven negro o verde), los fps, el bitrate, el peso, la duración, faststart (solo importa en la web) y el audio. Genera:
  - `fotogramas.png`: hasta 12 cuadros, empezando por el **primero** (es la portada);
  - `zonas-seguras-<destino>.png`: los mismos cuadros con lo que tapa la app pintado en rojo (los botones de la derecha solo ocupan la mitad de abajo). Lo importante debe quedar dentro del contorno verde;
  - `en-celular-<destino>.png`: el video en un teléfono de 390×844. Reels, TikTok y Shorts **llenan la pantalla y recortan los lados**; WhatsApp y la web lo encajan entero. Aquí ves qué se pierde y si el texto se lee.
  Si un texto aparece entre dos fotogramas (una dirección a los 32 s, el titular del primer segundo), saca cuadros extra con `ffmpeg -ss <segundo> -i video -frames:v 1 cuadro.jpg`: los 12 cuadros son una muestra, no el video completo.
- **Imagen**: medida, proporción, peso, zonas seguras y vista en el teléfono.
- **PDF**: tamaño y orientación de página, peso, y las primeras páginas a ancho de teléfono (`paginas.png`).
- `--version-ligera` crea copias en la carpeta de salida; **nunca reemplaza el original**:
  - `… - 1080 para compartir.mp4` (si el destino es WhatsApp, web, feed o YouTube): 1080p, H.264, unos 2-6 Mbps y arranca al instante. Pesa unas 10 veces menos que un 4K.
  - `… - 1080 para subir.mp4` (si el destino es Reels, TikTok, Shorts o Historias y el video es vertical): 1080×1920 de alta calidad. Para subir no se usa la de compartir, porque la app la volvería a comprimir y se vería peor.

**Antes de preparar algo para mandarlo a otra persona**, revisa en el estado del proyecto **si se puede mandar**. Ejemplo: hay proyectos donde el cliente solo recibe la versión limpia cuando paga, y antes recibe la muestra con marca de agua. Si no está claro, prepara las dos versiones, nómbralas sin ambigüedad ("SIN marca de agua" / "muestra") y pregunta cuál mandar.

Mira **siempre** las imágenes que genera: el script no lee el texto del video; tú sí.

## Destinos (lo que importa de cada uno)

| Destino | Formato | Lo que tapa la app (aprox.) | Notas |
|---|---|---|---|
| Reels | 9:16, 1080×1920 | arriba ~12 %, abajo ~22 % (texto y audio), derecha ~15 % (botones) | En el feed se ve recortado a 4:5: lo importante, en el centro |
| TikTok | 9:16, 1080×1920 | arriba ~9 %, abajo ~25 %, derecha ~16 % | La zona de abajo es la más grande de todas |
| Shorts | 9:16 | arriba ~10 %, abajo ~22 %, derecha ~16 % | ≤ 3 min |
| Historias (IG/FB/WhatsApp) | 9:16 | arriba ~13 %, abajo ~17 % | 60 s por historia |
| Feed IG | 4:5, 1080×1350 | — | Un 9:16 se recorta |
| WhatsApp (chat) | el que sea; mejor vertical | — | Más de ~64 MB se recomprime o llega como documento que no se reproduce en el chat |
| Web | depende del hueco | — | ≤ 5-15 MB por video, faststart, póster, `muted playsinline` |

(Las zonas son aproximadas y cambian con cada versión de las apps; si un elemento queda en el borde, muévelo.)

## Reglas para que se vea bien en el teléfono
- **Componer en vertical, no recortar.** Pasar un 16:9 a 9:16 recortando corta textos y logos. Hay que recomponer: apilar los elementos, texto más grande y protagonista centrado. Si te pidieron 16:9 y el destino es vertical, **pregunta** antes de rehacerlo (cambia el video).
- **Texto**: un lienzo de 1080 px de ancho se ve a ~390 px en el teléfono, o sea 2.8 veces más chico. Títulos de 80 px o más; textos secundarios de 48 px o más; nada informativo por debajo de 40 px. Con contraste: sombra o placa detrás si va sobre una foto.
- **Subtítulos**: dentro de la zona segura, nunca en el 20-25 % de abajo de Reels o TikTok.
- **4K no sirve en el teléfono**: un teléfono muestra como mucho ~1080 px de ancho. Entrega el 4K como "máster" si lo quieren, pero para ver, mandar y subir a la web, la versión ligera en 1080p (pesa unas 5-10 veces menos).
- **Primer segundo**: en el teléfono la gente decide en 1-2 s. Que el primer fotograma ya diga algo (sirve de miniatura).

## Videos dentro de una web ("en el móvil se ven muy grandes y no entran bien")
Son dos problemas distintos, revisa los dos:
1. **La página**: un video vertical a todo el ancho mide ~1.8 veces el ancho de alto y **no cabe en la pantalla**. `revisar.py` lo marca como `media-mas-alta-que-pantalla`. Arreglo en `arreglos.md` § "Medios más altos que la pantalla" (`max-height: 80svh` + `object-fit: contain`, o limitar el ancho).
2. **El archivo**: 4K de 120 MB para ver en el teléfono gasta los datos y tarda. `revisar_archivo.py --para web --version-ligera`, y en la web usa la versión ligera (el 4K solo como descarga del cliente que paga, si es el producto).

## Imágenes (carruseles, posts, flyers)
- Carrusel de Instagram: 4:5 (1080×1350) o 1:1; texto grande y nada importante pegado a los bordes.
- Para la web: WebP o AVIF, ≤ 300-500 KB, ancho ≤ 2000 px, con `srcset`.
- Una imagen con mucho texto pequeño (infografía, tabla) no se lee en el teléfono: divídela en varias láminas.

## PDFs (propuestas, dossiers)
- Un PDF horizontal tipo presentación se ve diminuto en el teléfono: cada página ocupa un tercio de la pantalla. Si la persona lo va a leer en el teléfono (casi siempre que llega por WhatsApp), conviene una versión vertical o letra de 24 pt o más en las diapositivas.
- Peso: menos de 10-20 MB. Comprime las fotos antes de exportar.
- Si existe una versión web (una propuesta en HTML), revísala con `revisar.py`: en el teléfono suele ser mejor que el PDF.
