#!/usr/bin/env python3
import site as _site, sys as _sys
if _site.getusersitepackages() not in _sys.path:  # que encuentre lo que instaló el Paso 0, aunque corran python3 -I
    _sys.path.append(_site.getusersitepackages())
import os
"""revisar_archivo.py — revisa VIDEOS, IMÁGENES y PDFs para que se vean bien en el celular.

Lo que mide (sin opinar):
  Video: medida y proporción, códec, color (yuv420p), fps, bitrate, peso, duración,
         si arranca rápido en web (faststart), audio; contra lo que pide CADA destino.
  Imagen: medida, proporción, peso.
  PDF:   tamaño y orientación de página, número de páginas, peso.
Lo que genera para que lo MIRES (tú, con Read):
  - fotogramas.png              un cuadro cada pocos segundos (incluye el primero = portada)
  - zonas-seguras-<destino>.png esos cuadros con lo que tapa la app pintado en rojo
  - en-celular-<destino>.png    cómo se ve en un teléfono de 390×844 (Reels/TikTok llenan la
                                pantalla y recortan los lados; WhatsApp/web lo encajan entero)
  - paginas.png                 (PDF) las primeras páginas a ancho de celular
Y con --version-ligera, copias listas para usar (nunca toca el original):
  - "<nombre> - 1080 para compartir.mp4"  WhatsApp/web: 1080p, H.264, ~2-6 Mbps, arranca al instante
  - "<nombre> - 1080 para subir.mp4" Reels/TikTok/Shorts/Historias: 1080×1920 alta calidad
                                      (para que la app no comprima dos veces algo ya comprimido)

Uso:
  python3 revisar_archivo.py <archivo> [--para reels,whatsapp | tiktok | shorts | historias | feed | web | youtube | auto]
                                       [--salida DIR] [--version-ligera]
  --para acepta varios destinos separados por comas. auto: vertical -> reels; horizontal -> web.
"""
import argparse
import json
import shutil
import struct
import subprocess
from pathlib import Path

# Zonas que tapa la interfaz de cada app, en fracción del alto/ancho (aprox., 2025-2026; cambian
# con cada versión de las apps: si algo queda en el borde, muévelo).
#   der_desde: los botones de la derecha (like, comentar, compartir) solo ocupan desde esa altura hacia abajo.
ZONAS = {
    "reels":     {"arriba": 0.10, "abajo": 0.22, "izq": 0.04, "der": 0.15, "der_desde": 0.45, "nombre": "Instagram Reels"},
    "tiktok":    {"arriba": 0.09, "abajo": 0.25, "izq": 0.04, "der": 0.16, "der_desde": 0.40, "nombre": "TikTok"},
    "shorts":    {"arriba": 0.10, "abajo": 0.22, "izq": 0.04, "der": 0.16, "der_desde": 0.45, "nombre": "YouTube Shorts"},
    "historias": {"arriba": 0.13, "abajo": 0.17, "izq": 0.04, "der": 0.04, "der_desde": 0.0,  "nombre": "Historias IG/FB/WhatsApp"},
    "feed":      {"arriba": 0.0,  "abajo": 0.0,  "izq": 0.0,  "der": 0.0,  "der_desde": 0.0,  "nombre": "Feed de Instagram (4:5)"},
    "whatsapp":  {"arriba": 0.0,  "abajo": 0.0,  "izq": 0.0,  "der": 0.0,  "der_desde": 0.0,  "nombre": "WhatsApp (chat)"},
    "web":       {"arriba": 0.0,  "abajo": 0.0,  "izq": 0.0,  "der": 0.0,  "der_desde": 0.0,  "nombre": "Página web"},
    "youtube":   {"arriba": 0.0,  "abajo": 0.12, "izq": 0.0,  "der": 0.0,  "der_desde": 0.0,  "nombre": "YouTube normal"},
}
VERTICALES = {"reels", "tiktok", "shorts", "historias"}
PROPORCION = {"reels": 9 / 16, "tiktok": 9 / 16, "shorts": 9 / 16, "historias": 9 / 16, "feed": 4 / 5, "youtube": 16 / 9}
DURACION_MAX = {"reels": 180, "tiktok": 600, "shorts": 180, "historias": 60}
PESO_AVISO_MB = {"whatsapp": 64, "web": 15, "reels": 650, "tiktok": 500, "shorts": 1000, "historias": 250,
                 "feed": 650, "youtube": 100000}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".avif"}


def fuente(t):
    from PIL import ImageFont
    for f in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(f, t)
        except Exception:
            pass
    return ImageFont.load_default()


def hallazgo(lista, grav, titulo, detalle, destino=None):
    lista.append({"gravedad": grav, "titulo": titulo, "detalle": detalle, "destino": destino})


def ffprobe(p: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(p)],
                         capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"ffprobe no pudo leer el archivo: {out.stderr[:300]}")
    return json.loads(out.stdout)


def faststart(p: Path):
    """True si el índice (moov) va antes que los datos (mdat): el video arranca sin descargarse entero."""
    try:
        with open(p, "rb") as f:
            for _ in range(50):
                cab = f.read(8)
                if len(cab) < 8:
                    return None
                tam, tipo = struct.unpack(">I4s", cab)
                tipo = tipo.decode("latin1")
                if tipo == "moov":
                    return True
                if tipo == "mdat":
                    return False
                if tam == 1:
                    tam = struct.unpack(">Q", f.read(8))[0]
                    f.seek(tam - 16, 1)
                elif tam == 0:
                    return None
                else:
                    f.seek(tam - 8, 1)
    except Exception:
        return None
    return None


# ---------------------------------------------------------------- dibujo
def dibujar_zonas(img, destino):
    from PIL import Image, ImageDraw
    z = ZONAS[destino]
    if not any(z[k] for k in ("arriba", "abajo", "izq", "der")):
        return img
    img = img.convert("RGBA")
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    W, H = img.size
    rojo = (230, 40, 40, 85)
    d.rectangle([0, 0, W, int(H * z["arriba"])], fill=rojo)
    d.rectangle([0, int(H * (1 - z["abajo"])), W, H], fill=rojo)
    d.rectangle([0, int(H * z["arriba"]), int(W * z["izq"]), int(H * (1 - z["abajo"]))], fill=rojo)
    d.rectangle([int(W * (1 - z["der"])), int(H * max(z["arriba"], z["der_desde"])), W, int(H * (1 - z["abajo"]))], fill=rojo)
    out = Image.alpha_composite(img, capa)
    d2 = ImageDraw.Draw(out)
    g = (40, 220, 90, 255)
    x0, y0, x1, y1 = int(W * z["izq"]), int(H * z["arriba"]), int(W * (1 - z["izq"])), int(H * (1 - z["abajo"]))
    xd, yd = int(W * (1 - z["der"])), int(H * max(z["arriba"], z["der_desde"]))
    grosor = max(2, W // 300)
    # contorno de la zona segura (con el escalón de los botones de la derecha)
    d2.line([(x0, y0), (x1, y0), (x1, yd), (xd, yd), (xd, y1), (x0, y1), (x0, y0)], fill=g, width=grosor)
    return out.convert("RGB")


def lamina(imagenes, etiquetas, destino, alto=620, por_fila=6):
    from PIL import Image, ImageDraw
    piezas = []
    for im in imagenes:
        e = alto / im.height
        piezas.append(im.resize((max(1, int(im.width * e)), alto)))
    filas = [list(zip(piezas[i:i + por_fila], etiquetas[i:i + por_fila])) for i in range(0, len(piezas), por_fila)]
    W = max(sum(p.width for p, _ in f) + 24 * (len(f) + 1) for f in filas)
    H = len(filas) * (alto + 60) + 16
    lienzo = Image.new("RGB", (W, H), (236, 236, 240))
    d = ImageDraw.Draw(lienzo)
    y = 10
    for f in filas:
        x = 24
        for p, et in f:
            d.text((x, y), et, fill=(20, 20, 20), font=fuente(18))
            lienzo.paste(p, (x, y + 32))
            x += p.width + 24
        y += alto + 60
    lienzo.save(destino)
    return destino


def a_tamano_celular(im, destino):
    """Cómo se ve en un teléfono de 390×844 px.
    Reels/TikTok/Shorts/Historias LLENAN la pantalla (recortan los lados si sobra);
    WhatsApp, web y feed encajan el video entero (con franjas si no coincide la forma)."""
    from PIL import Image, ImageDraw
    W, H = 390, 844
    tel = Image.new("RGB", (W + 24, H + 24), (25, 25, 28))
    fondo = (0, 0, 0) if destino not in ("web",) else (245, 245, 245)
    pantalla = Image.new("RGB", (W, H), fondo)
    if destino in VERTICALES:
        e = max(W / im.width, H / im.height)            # llenar
    else:
        e = min(W / im.width, H / im.height)            # encajar
    nueva = im.resize((max(1, int(im.width * e)), max(1, int(im.height * e))))
    pantalla.paste(nueva, ((W - nueva.width) // 2, (H - nueva.height) // 2))
    if destino in VERTICALES:
        pantalla = dibujar_zonas(pantalla, destino)
    tel.paste(pantalla, (12, 12))
    ImageDraw.Draw(tel).rounded_rectangle([2, 2, W + 21, H + 21], radius=40, outline=(80, 80, 85), width=3)
    return tel


# ---------------------------------------------------------------- video
def revisar_video(p: Path, destinos, salida: Path, ligera: bool):
    info = ffprobe(p)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        raise SystemExit("El archivo no tiene pista de video.")
    w, h = int(v["width"]), int(v["height"])
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd and abs(int(sd["rotation"])) in (90, 270):
            w, h = h, w
    dur = float(info["format"].get("duration", 0))
    peso = int(info["format"].get("size", p.stat().st_size))
    br = int(info["format"].get("bit_rate", 0) or 0)
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(int(num) / int(den), 2) if int(den) else 0
    prop = w / h
    mb = peso / 1024 / 1024
    if destinos == ["auto"]:
        destinos = ["reels"] if prop < 0.8 else (["feed"] if prop < 1.1 else ["web"])
    H = []
    hallazgo(H, "info", "Datos", f"{w}×{h} ({'vertical' if prop < 1 else 'horizontal' if prop > 1 else 'cuadrado'}), "
             f"{dur:.1f} s, {fps} fps, {v['codec_name']}, {v.get('pix_fmt')}, {br/1e6:.1f} Mbps, {mb:.1f} MB, "
             f"audio: {a['codec_name'] if a else 'NO'}")

    # Problemas que valen para cualquier destino
    if v["codec_name"] not in ("h264", "hevc", "vp9", "av1"):
        hallazgo(H, "error", "Códec que muchos celulares no reproducen", f"{v['codec_name']}: exporta en H.264.")
    if v.get("pix_fmt") not in ("yuv420p", "yuvj420p"):
        hallazgo(H, "error", "Formato de color que falla en celulares",
                 f"pix_fmt={v.get('pix_fmt')}: muchos iPhone/Android lo ven negro, verde o no lo abren. Debe ser yuv420p.")
    if fps > 60:
        hallazgo(H, "aviso", "Demasiados fotogramas", f"{fps} fps: las apps lo bajan a 30/60 y pesa de más.")

    for dst in destinos:
        nom = ZONAS[dst]["nombre"]
        esperado = PROPORCION.get(dst)
        if esperado and abs(prop - esperado) / esperado > 0.04:
            if esperado < 1 and prop > 1:
                hallazgo(H, "error", "Video horizontal para un destino vertical",
                         f"{nom} es 9:16: un 16:9 ahí sale como una franja chiquita con barras negras. Hace falta una versión "
                         "vertical COMPUESTA en vertical (no recortada). Busca si ya existe una en la misma carpeta.", dst)
            else:
                hallazgo(H, "aviso", "Proporción distinta a la del destino",
                         f"Es {w}:{h} ({prop:.3f}) y {nom} espera {esperado:.3f}: la app lo recortará o pondrá barras.", dst)
        if dst in VERTICALES and prop < 1 and max(w, h) < 1920:
            hallazgo(H, "aviso", "Resolución baja para vertical", f"{w}×{h}; lo ideal es 1080×1920.", dst)
        if v["codec_name"] == "hevc" and dst in ("web", "whatsapp"):
            hallazgo(H, "aviso", "HEVC/H.265", f"Algunos Android y navegadores no lo reproducen. Para {nom}, H.264.", dst)
        if v["codec_name"] in ("vp9", "av1") and dst not in ("web",):
            hallazgo(H, "aviso", v["codec_name"].upper(), f"Para {nom}, mejor H.264 .mp4.", dst)
        if dst in DURACION_MAX and dur > DURACION_MAX[dst]:
            hallazgo(H, "aviso", "Más largo de lo que admite el destino", f"{dur:.0f} s; {nom}: máx. {DURACION_MAX[dst]} s.", dst)
        if mb > PESO_AVISO_MB.get(dst, 200):
            razon = {"web": "tarda en cargar con datos móviles y gasta el plan; para web lo sano es < 5-15 MB por video",
                     "whatsapp": "WhatsApp lo recomprime (pierde calidad) o lo manda como documento, que no se reproduce en el chat"}.get(dst, "se sube lento con datos")
            hallazgo(H, "error" if dst in ("web", "whatsapp") else "aviso", "Archivo muy pesado para el celular",
                     f"{mb:.0f} MB en {nom}: {razon}. Usa --version-ligera.", dst)
        if dst in ("web", "whatsapp") and max(w, h) > 1920:
            hallazgo(H, "aviso", "4K no se aprovecha en el celular",
                     f"{w}×{h}: un teléfono muestra como mucho ~1080 px de ancho; 1080p pesa unas 5-10 veces menos.", dst)
        if br > 16e6 and dst == "web":
            hallazgo(H, "aviso", "Bitrate muy alto para datos móviles", f"{br/1e6:.0f} Mbps; para web, 2-6 Mbps en 1080p.", dst)
        if dst == "web" and p.suffix.lower() in (".mp4", ".mov", ".m4v") and faststart(p) is False:
            hallazgo(H, "error", "El video no arranca hasta descargarse entero (sin faststart)",
                     "En la web el teléfono baja todo el archivo antes de empezar. Arreglo: ffmpeg -i x.mp4 -c copy -movflags +faststart y.mp4", dst)
        if not a and dst in ("reels", "tiktok", "shorts"):
            hallazgo(H, "info", "Sin audio", f"En {nom} los videos con sonido/música funcionan mejor.", dst)

    # Fotogramas: el primero (portada) + uno cada ~dur/11 (mín. 2 s), máx. 12
    salida.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    paso = max(2.0, dur / 11)
    tiempos = [0.05] + [round(paso * i, 2) for i in range(1, 12) if paso * i < dur - 0.2]
    marcos = []
    for i, t in enumerate(tiempos[:12]):
        f = salida / f"cuadro-{i:02d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(p), "-frames:v", "1",
                        "-vf", "scale='min(1080,iw)':-2", str(f)], capture_output=True)
        if f.exists():
            marcos.append((Image.open(f).convert("RGB"), f"{t:.1f} s" + (" (portada)" if i == 0 else "")))
    if marcos:
        lamina([m for m, _ in marcos], [e for _, e in marcos], salida / "fotogramas.png")
        for dst in destinos:
            if dst in VERTICALES or ZONAS[dst]["abajo"]:
                lamina([dibujar_zonas(m, dst) for m, _ in marcos], [e for _, e in marcos], salida / f"zonas-seguras-{dst}.png")
            lamina([a_tamano_celular(m, dst) for m, _ in marcos[:6]], [e for _, e in marcos[:6]],
                   salida / f"en-celular-{dst}.png", alto=868)

    if ligera:
        def codificar(nombre, filtro, crf, maxrate, buf, audio):
            destino = salida / nombre
            r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", filtro + ",format=yuv420p",
                                "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-maxrate", maxrate, "-bufsize", buf,
                                "-profile:v", "high", "-c:a", "aac", "-b:a", audio, "-movflags", "+faststart", str(destino)],
                               capture_output=True, text=True)
            if r.returncode == 0:
                i2 = ffprobe(destino)
                b2 = int(i2["format"].get("bit_rate", 0) or 0)
                hallazgo(H, "info", "Versión creada", f"{destino.name}: {destino.stat().st_size/1024/1024:.1f} MB "
                         f"(antes {mb:.0f} MB), {b2/1e6:.1f} Mbps, H.264, arranca al instante.")
            else:
                hallazgo(H, "aviso", f"No se pudo crear {nombre}", r.stderr[:300])
        import re as _re
        base = _re.sub(r"\s*[-_ ]?\b(4k|2160p|uhd)\b", "", p.stem, flags=_re.I).strip(" -_") or p.stem
        lado = "scale=-2:'min(1920,ih)'" if prop < 1 else "scale='min(1920,iw)':-2"
        if any(d in ("whatsapp", "web", "feed", "youtube") for d in destinos):
            codificar(f"{base} - 1080 para compartir.mp4", lado, 23, "6M", "12M", "128k")
        if any(d in VERTICALES for d in destinos):
            if prop < 1:
                codificar(f"{base} - 1080 para subir.mp4", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                          18, "16M", "32M", "192k")
            else:
                hallazgo(H, "info", "No se creó versión para subir a Reels/TikTok",
                         "El video es horizontal: primero hace falta una versión compuesta en vertical.")
    return destinos, H


# ---------------------------------------------------------------- imagen
def revisar_imagen(p: Path, destinos, salida: Path):
    from PIL import Image
    im = Image.open(p)
    w, h = im.size
    prop = w / h
    if destinos == ["auto"]:
        destinos = ["historias"] if prop < 0.7 else (["feed"] if prop < 1.1 else ["web"])
    mb = p.stat().st_size / 1024 / 1024
    H = []
    hallazgo(H, "info", "Datos", f"{w}×{h}, {mb:.2f} MB, {im.format}")
    salida.mkdir(parents=True, exist_ok=True)
    rgb = im.convert("RGB")
    for dst in destinos:
        esperado = PROPORCION.get(dst)
        if esperado and abs(prop - esperado) / esperado > 0.04:
            hallazgo(H, "aviso", "Proporción distinta a la del destino", f"{prop:.3f} vs {esperado:.3f} ({ZONAS[dst]['nombre']}).", dst)
        if dst == "web" and mb > 0.5:
            hallazgo(H, "aviso" if mb < 2 else "error", "Imagen pesada para web en celular",
                     f"{mb:.1f} MB. Para web: WebP/AVIF o JPG calidad 80, ≤ 300-500 KB y ancho ≤ 2000 px.", dst)
        if dst == "web" and w > 2600:
            hallazgo(H, "aviso", "Más ancha de lo necesario", f"{w}px; ningún teléfono ni laptop necesita más de ~2000-2600 px.", dst)
        lamina([dibujar_zonas(rgb, dst), a_tamano_celular(rgb, dst)], ["zonas seguras", "en un celular"],
               salida / f"en-celular-{dst}.png", alto=868)
    return destinos, H


# ---------------------------------------------------------------- pdf
def revisar_pdf(p: Path, salida: Path):
    H = []
    salida.mkdir(parents=True, exist_ok=True)
    info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout if shutil.which("pdfinfo") else ""
    paginas = next((int(l.split()[-1]) for l in info.splitlines() if l.startswith("Pages:")), None)
    tam = next((l.split(":", 1)[1].strip() for l in info.splitlines() if l.startswith("Page size:")), "")
    hallazgo(H, "info", "Datos", f"{paginas} páginas, tamaño {tam}, {p.stat().st_size/1024/1024:.1f} MB")
    try:
        nums = [float(x) for x in tam.split()[0:3:2]]
        if nums[0] > nums[1]:
            hallazgo(H, "aviso", "PDF horizontal (tipo presentación)",
                     "En el teléfono cada página se ve chiquita: el texto de menos de ~24 pt no se lee sin zoom. "
                     "Si se va a leer en el teléfono, haz una versión vertical o sube la letra.")
    except Exception:
        pass
    if p.stat().st_size > 20 * 1024 * 1024:
        hallazgo(H, "aviso", "PDF pesado", "Más de 20 MB: por WhatsApp/correo tarda y algunos correos lo rebotan. Comprime las fotos.")
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", "60", "-f", "1", "-l", "3", str(p), str(salida / "pagina")], capture_output=True)
        from PIL import Image
        imgs = sorted(salida.glob("pagina*.png"))
        if imgs:
            lamina([a_tamano_celular(Image.open(i).convert("RGB"), "whatsapp") for i in imgs],
                   [i.stem for i in imgs], salida / "paginas.png", alto=868)
    return ["pdf"], H


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo")
    ap.add_argument("--para", default="auto", help="uno o varios separados por comas: " + ", ".join(ZONAS) + ", auto")
    ap.add_argument("--salida")
    ap.add_argument("--version-ligera", action="store_true")
    a = ap.parse_args()
    destinos = [d.strip() for d in a.para.split(",") if d.strip()]
    for d in destinos:
        if d != "auto" and d not in ZONAS:
            raise SystemExit(f"Destino desconocido '{d}'. Opciones: {', '.join(ZONAS)}, auto")
    p = Path(a.archivo).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"No existe: {p}")
    salida = Path(a.salida).expanduser().resolve() if a.salida else Path("revision-movil") / p.stem
    ext = p.suffix.lower()
    if ext in VIDEO_EXT:
        destinos, H = revisar_video(p, destinos, salida, a.version_ligera)
    elif ext in IMG_EXT:
        destinos, H = revisar_imagen(p, destinos, salida)
    elif ext == ".pdf":
        destinos, H = revisar_pdf(p, salida)
    else:
        raise SystemExit(f"No sé revisar archivos {ext}")
    icon = {"error": "🔴", "aviso": "🟠", "info": "🔵"}
    nombres = ", ".join(ZONAS[d]["nombre"] if d in ZONAS else d for d in destinos)
    lineas = [f"# Revisión para celular — {p.name}", "", f"Destino(s): **{nombres}**", ""]
    for x in sorted(H, key=lambda x: {"error": 0, "aviso": 1, "info": 2}[x["gravedad"]]):
        tag = f" [{ZONAS[x['destino']]['nombre']}]" if x.get("destino") in ZONAS and len(destinos) > 1 else ""
        lineas.append(f"- {icon[x['gravedad']]} **{x['titulo']}**{tag} — {x['detalle']}")
    if ext in VIDEO_EXT:
        lineas += ["", "MIRA (con Read): `fotogramas.png` (¿el primer cuadro sirve de portada?), "
                   "`zonas-seguras-<destino>.png` (lo importante dentro del contorno verde) y "
                   "`en-celular-<destino>.png` (¿se lee el texto a tamaño de teléfono?). "
                   "El script no lee el texto del video: eso lo juzgas tú."]
    else:
        lineas += ["", "MIRA `en-celular-*.png` / `paginas.png`: ¿se lee a tamaño de celular?"]
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "informe.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    print(f"\nArchivos en: {salida}")


def _aviso_version():
    """Al terminar, revisa en silencio si hay versión nueva de la skill (máx. 1 vez al día)."""
    try:
        import importlib.util
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.py")
        spec = importlib.util.spec_from_file_location("dak_version", ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulo.avisar()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        _aviso_version()
