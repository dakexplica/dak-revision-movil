// auditoria.js — se ejecuta DENTRO de la página (page.evaluate) en cada dispositivo.
// Devuelve una lista de hallazgos medidos, no opiniones. Cada hallazgo:
//   { id, gravedad: "error"|"aviso"|"info", titulo, detalle, selector, rect }
// Todo lo que sea "se ve encimado / feo" lo juzga quien mira las capturas; aquí solo
// va lo que se puede medir con números.
(opts) => {
  // Medidas del DISPOSITIVO (las que le pasamos), no las de la ventana: si la página es más ancha
  // que la pantalla, el celular "encoge" todo (zoom out) e innerWidth crece; con innerWidth no se vería el problema.
  const W = (opts && opts.ancho) || window.innerWidth;
  const H = (opts && opts.alto) || window.innerHeight;
  const plataforma = (opts && opts.plataforma) || "desconocida"; // ios | android | escritorio
  const esTactil = plataforma !== "escritorio";
  const hallazgos = [];
  const MAX_ELEMENTOS = 6000;
  const MAX_POR_TIPO = 12;
  const conteo = {};

  const add = (h) => {
    conteo[h.id] = (conteo[h.id] || 0) + 1;
    if (conteo[h.id] > MAX_POR_TIPO) return;
    hallazgos.push(h);
  };

  // ---------- utilidades ----------
  const selectorDe = (el) => {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) return `#${CSS.escape(el.id)}`;
    const partes = [];
    let n = el;
    for (let i = 0; n && n.nodeType === 1 && i < 4; i++) {
      let p = n.tagName.toLowerCase();
      const clases = [...n.classList].filter((c) => !/^(is-|has-|js-)/.test(c)).slice(0, 2);
      if (clases.length) p += "." + clases.map((c) => CSS.escape(c)).join(".");
      const padre = n.parentElement;
      if (padre) {
        const hermanos = [...padre.children].filter((x) => x.tagName === n.tagName);
        if (hermanos.length > 1) p += `:nth-of-type(${hermanos.indexOf(n) + 1})`;
      }
      partes.unshift(p);
      if (n.id) { partes[0] = `#${CSS.escape(n.id)}`; break; }
      n = padre;
    }
    return partes.join(" > ");
  };
  const r = (el) => {
    const b = el.getBoundingClientRect();
    return { x: Math.round(b.left), y: Math.round(b.top + window.scrollY), w: Math.round(b.width), h: Math.round(b.height) };
  };
  // Herramientas que NO ve el visitante (barra de vista previa de Shopify, barra de admin): se ignoran.
  const HERRAMIENTAS = "#PBarNextFrameWrapper, #PBarNextFrame, #preview-bar-iframe, #admin-bar-iframe, #wpadminbar, [data-vercel-toolbar], vercel-live-feedback, nextjs-portal";
  // Texto solo para lectores de pantalla (sr-only / visually-hidden): invisible a propósito, no es un error.
  const soloLector = (el) => {
    if (el.closest && el.closest(".sr-only, .visually-hidden, .screen-reader-text, .screenreader, .a11y-hidden, [class*='visually-hidden']")) return true;
    const cs = getComputedStyle(el);
    if (/rect\(\s*0/.test(cs.clip) || /inset\(\s*50%|circle\(\s*0/.test(cs.clipPath)) return true;
    const b = el.getBoundingClientRect();
    return b.width <= 1.5 && b.height <= 1.5 && /(hidden|clip)/.test(cs.overflow);
  };
  const visible = (el) => {
    if (el.closest && el.closest(HERRAMIENTAS)) return false;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0) return false;
    const b = el.getBoundingClientRect();
    if (!(b.width > 0 && b.height > 0)) return false;
    return !soloLector(el);
  };
  const textoPropio = (el) =>
    [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").trim();
  const recortaTexto = (t, n = 60) => (t.length > n ? t.slice(0, n) + "…" : t);

  // ¿Algún ancestro recorta o hace scroll horizontal? (carrusel, contenedor con overflow)
  const ancestroQueContiene = (el) => {
    let p = el.parentElement;
    while (p && p !== document.body && p !== document.documentElement) {
      const cs = getComputedStyle(p);
      if (/(auto|scroll|hidden|clip)/.test(cs.overflowX)) return { el: p, tipo: cs.overflowX };
      p = p.parentElement;
    }
    return null;
  };

  const todos = [...document.body.querySelectorAll("*")].slice(0, MAX_ELEMENTOS);

  // ---------- 1. Meta viewport ----------
  const meta = document.querySelector('meta[name="viewport"]');
  const metaTxt = meta ? meta.getAttribute("content") || "" : "";
  if (!meta) {
    add({ id: "viewport-falta", gravedad: "error", titulo: "Falta la etiqueta viewport",
      detalle: 'Sin <meta name="viewport" content="width=device-width, initial-scale=1"> el celular dibuja la página como si fuera una compu de 980 px y la encoge: todo se ve diminuto.' });
  } else {
    if (!/width\s*=\s*device-width/.test(metaTxt))
      add({ id: "viewport-ancho", gravedad: "error", titulo: "El viewport no usa width=device-width", detalle: `content="${metaTxt}"` });
    if (esTactil && /user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b/.test(metaTxt))
      add({ id: "viewport-sin-zoom", gravedad: "aviso", titulo: "La página bloquea el zoom con los dedos",
        detalle: `content="${metaTxt}". Molesta a quien ve poco y Android lo ignora a veces. Solo se justifica en experiencias tipo app (3D, juegos) y entonces hay que asegurar textos grandes.` });
    if (/viewport-fit\s*=\s*cover/.test(metaTxt)) {
      const usaSafeArea = [...document.styleSheets].some((s) => {
        try { return [...s.cssRules].some((ru) => /safe-area-inset/.test(ru.cssText)); } catch (e) { return false; }
      }) || /safe-area-inset/.test(document.documentElement.innerHTML.slice(0, 200000));
      if (!usaSafeArea)
        add({ id: "safe-area", gravedad: "aviso", titulo: "viewport-fit=cover sin respetar la muesca/barra",
          detalle: "Con viewport-fit=cover el contenido se mete debajo de la Isla Dinámica y de la barra de gestos. Hay que usar env(safe-area-inset-*) en cabeceras, barras fijas y botones de abajo." });
    }
  }

  // ---------- 1b. La página encogida (zoom out) ----------
  if (window.innerWidth > W + 2) {
    add({ id: "pagina-encogida", gravedad: "error", titulo: "La página es más ancha que la pantalla y el celular la encoge",
      detalle: `El contenido mide ${window.innerWidth}px y la pantalla ${W}px: el navegador aleja el zoom y TODO se ve más chico (letra, botones, videos). Casi siempre es un elemento con ancho mínimo grande (una imagen/video sin max-width, un grid de varias columnas que no baja a una, un ancho fijo).` });
  }

  // ---------- 2. Desborde horizontal (lo que hace que la página "baile" de lado o se vea cortada) ----------
  const docAncho = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
  const bodyCs = getComputedStyle(document.body);
  const htmlCs = getComputedStyle(document.documentElement);
  const escondeDesborde = /(hidden|clip)/.test(bodyCs.overflowX) || /(hidden|clip)/.test(htmlCs.overflowX);
  if (docAncho > W + 1) {
    add({ id: "scroll-horizontal", gravedad: "error", titulo: "La página se mueve de lado (scroll horizontal)",
      detalle: `La página mide ${docAncho}px de ancho en una pantalla de ${W}px. Al deslizar con el dedo la página se va de lado.` });
  }
  const culpables = [];
  for (const el of todos) {
    if (!visible(el)) continue;
    const b = el.getBoundingClientRect();
    if (b.right <= W + 1 && b.left >= -1) continue;
    if (b.width < 2) continue;
    const anc = ancestroQueContiene(el);
    if (anc) continue; // está dentro de un carrusel o caja que recorta: es intencional
    const cs = getComputedStyle(el);
    if (cs.position === "fixed" && (b.right < 0 || b.left > W)) continue; // menú fuera de pantalla a propósito
    if (b.right < 0 || b.left > W) continue; // totalmente fuera (off-canvas)
    if (culpables.some((c) => c.contains(el))) continue;
    culpables.push(el);
  }
  culpables.slice(0, MAX_POR_TIPO).forEach((el) => {
    const b = el.getBoundingClientRect();
    add({ id: escondeDesborde ? "contenido-cortado" : "desborda-ancho", gravedad: "error",
      titulo: escondeDesborde ? "Contenido cortado por el borde de la pantalla" : "Elemento más ancho que la pantalla",
      detalle: `Va de ${Math.round(b.left)}px a ${Math.round(b.right)}px en una pantalla de ${W}px` +
        (escondeDesborde ? " (el body tiene overflow-x:hidden, así que no hay scroll: simplemente se corta)." : "."),
      selector: selectorDe(el), rect: r(el) });
  });

  // ---------- 3. Texto recortado o cortado a la mitad ----------
  for (const el of todos) {
    const t = textoPropio(el);
    if (t.length < 2 || !visible(el)) continue;
    const cs = getComputedStyle(el);
    const recortaX = /(hidden|clip)/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 2 && cs.textOverflow !== "ellipsis";
    const recortaY = /(hidden|clip)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 4 && !cs.webkitLineClamp?.match(/\d/);
    if (recortaX || recortaY) {
      add({ id: "texto-recortado", gravedad: "error", titulo: "Texto cortado",
        detalle: `"${recortaTexto(t)}" no cabe en su caja (${el.clientWidth}×${el.clientHeight}px, necesita ${el.scrollWidth}×${el.scrollHeight}px).`,
        selector: selectorDe(el), rect: r(el) });
    }
  }

  // ---------- 4. Botones y links demasiado chicos para el dedo ----------
  const interactivos = [...document.querySelectorAll(
    'a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [role="link"], [role="tab"], [onclick], label[for]'
  )].filter(visible);
  const objetivos = [];
  for (const el of interactivos) {
    const b = el.getBoundingClientRect();
    // Links dentro de un párrafo de texto están exentos (WCAG): el usuario los ve como texto.
    if (el.tagName === "A" && getComputedStyle(el).display === "inline") {
      const padre = el.parentElement;
      if (padre && textoPropio(padre).length > 20) continue;
    }
    if (el.type === "checkbox" || el.type === "radio") {
      const lab = el.labels && el.labels[0];
      if (lab && visible(lab)) continue; // el label agranda el área tocable
    }
    objetivos.push({ el, b });
    if (!esTactil) continue;
    const minimo = plataforma === "android" ? 48 : 44;
    if (b.width < 24 || b.height < 24) {
      add({ id: "toque-muy-chico", gravedad: "error", titulo: "Botón/link/campo casi imposible de tocar",
        detalle: `${Math.round(b.width)}×${Math.round(b.height)}px (mínimo cómodo ${minimo}×${minimo}px). "${recortaTexto((el.innerText || el.getAttribute("aria-label") || el.value || "").trim(), 40)}"`,
        selector: selectorDe(el), rect: r(el) });
    } else if (b.width < minimo - 4 || b.height < minimo - 4) {
      add({ id: "toque-chico", gravedad: "aviso", titulo: "Botón/link/campo chico para el dedo",
        detalle: `${Math.round(b.width)}×${Math.round(b.height)}px; en ${plataforma === "android" ? "Android" : "iPhone"} lo cómodo es ${minimo}×${minimo}px. "${recortaTexto((el.innerText || el.getAttribute("aria-label") || el.value || "").trim(), 40)}"`,
        selector: selectorDe(el), rect: r(el) });
    }
  }
  if (esTactil) {
    // Botones pegados: el dedo toca el equivocado
    let pegados = 0;
    for (let i = 0; i < objetivos.length && pegados < MAX_POR_TIPO; i++) {
      for (let j = i + 1; j < objetivos.length; j++) {
        const a = objetivos[i].b, c = objetivos[j].b;
        if (objetivos[i].el.contains(objetivos[j].el) || objetivos[j].el.contains(objetivos[i].el)) continue;
        if (a.width >= 44 && a.height >= 44 && c.width >= 44 && c.height >= 44) continue;
        const dx = Math.max(0, Math.max(a.left, c.left) - Math.min(a.right, c.right));
        const dy = Math.max(0, Math.max(a.top, c.top) - Math.min(a.bottom, c.bottom));
        if (dx < 4 && dy < 4) {
          pegados++;
          add({ id: "toques-pegados", gravedad: "aviso", titulo: "Dos botones/links chicos casi pegados",
            detalle: `Separación ${Math.round(Math.max(dx, dy))}px: con el dedo es fácil tocar el equivocado.`,
            selector: `${selectorDe(objetivos[i].el)}  ↔  ${selectorDe(objetivos[j].el)}`, rect: r(objetivos[i].el) });
          break;
        }
      }
    }
  }

  // ---------- 5. Tamaños de letra ----------
  for (const el of todos) {
    const t = textoPropio(el);
    if (t.length < 3 || !visible(el)) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (esTactil && fs < 12) {
      add({ id: "letra-diminuta", gravedad: "error", titulo: "Letra demasiado chica para leer en celular",
        detalle: `${fs}px: "${recortaTexto(t)}". En celular el mínimo legible es ~12px para notas y 16px para texto normal.`,
        selector: selectorDe(el), rect: r(el) });
    } else if (esTactil && fs < 14 && t.length > 80) {
      add({ id: "parrafo-chico", gravedad: "aviso", titulo: "Párrafo con letra chica",
        detalle: `${fs}px en un texto largo: "${recortaTexto(t)}". Para leer cómodo en celular, 16px.`,
        selector: selectorDe(el), rect: r(el) });
    }
  }
  // Campos de formulario < 16px: el iPhone hace zoom solo al tocarlos y descuadra la página.
  document.querySelectorAll("input, select, textarea").forEach((el) => {
    if (!visible(el) || ["checkbox", "radio", "range", "color", "file", "submit", "button", "image", "hidden"].includes(el.type)) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 16 && plataforma !== "escritorio") {
      add({ id: "input-zoom-ios", gravedad: plataforma === "ios" ? "error" : "aviso", titulo: "Campo de texto con letra < 16px (el iPhone hace zoom solo)",
        detalle: `${fs}px. Al tocarlo, Safari hace zoom y la página queda descuadrada. Solución: font-size: 16px (o max(16px, 1rem)) en móvil.`,
        selector: selectorDe(el), rect: r(el) });
    }
  });

  // ---------- 6. Cosas fijas que tapan la pantalla ----------
  let areaFija = 0;
  const fijos = [];
  for (const el of todos) {
    const cs = getComputedStyle(el);
    if (cs.position !== "fixed" && cs.position !== "sticky") continue;
    if (!visible(el)) continue;
    if (fijos.some((f) => f.contains(el))) continue;
    const b = el.getBoundingClientRect();
    const ancho = Math.max(0, Math.min(b.right, W) - Math.max(b.left, 0));
    const alto = Math.max(0, Math.min(b.bottom, H) - Math.max(b.top, 0));
    if (ancho * alto <= 0) continue;
    // Fondos/overlays a pantalla completa intencionales (menús abiertos, intros) no cuentan
    if (ancho * alto > W * H * 0.9) continue;
    fijos.push(el);
    areaFija += ancho * alto;
  }
  if (esTactil && areaFija > W * H * 0.28) {
    add({ id: "fijos-tapan", gravedad: "aviso", titulo: "Barras/botones fijos tapan mucha pantalla",
      detalle: `Los elementos fijos ocupan el ${Math.round((areaFija / (W * H)) * 100)}% de la pantalla (${fijos.map(selectorDe).slice(0, 4).join(", ")}). En celular lo sano es < 20-25%.` });
  }

  // ---------- 7. Reglas CSS problemáticas en móvil ----------
  let usa100vh = 0, hoverRevela = 0, hojasBloqueadas = 0;
  const reglasHover = [];
  const recorre = (reglas, dentroDeHover) => {
    for (const ru of reglas) {
      if (ru.type === CSSRule.MEDIA_RULE) {
        const esHover = /\(\s*hover\s*:\s*hover\s*\)|\(\s*pointer\s*:\s*fine\s*\)|\(\s*any-hover/.test(ru.conditionText || ru.media.mediaText);
        recorre(ru.cssRules, dentroDeHover || esHover);
        continue;
      }
      if (ru.cssRules && ru.cssRules.length && ru.type !== CSSRule.STYLE_RULE) { recorre(ru.cssRules, dentroDeHover); continue; }
      if (ru.type !== CSSRule.STYLE_RULE) continue;
      const css = ru.style.cssText;
      if (/(^|[^d|s|l])100vh/.test(css) && /(height|min-height|max-height)\s*:\s*100vh/.test(css)) usa100vh++;
      if (!dentroDeHover && /:hover/.test(ru.selectorText) &&
          (/(display\s*:\s*(block|flex|grid))|visibility\s*:\s*visible|opacity\s*:\s*1|max-height|transform/.test(css))) {
        hoverRevela++;
        if (reglasHover.length < 5) reglasHover.push(ru.selectorText.slice(0, 80));
      }
    }
  };
  for (const s of document.styleSheets) {
    try { recorre(s.cssRules, false); } catch (e) { hojasBloqueadas++; }
  }
  if (esTactil && usa100vh) {
    add({ id: "100vh", gravedad: "aviso", titulo: "Usa height: 100vh",
      detalle: `${usa100vh} regla(s). En Safari y Chrome móviles 100vh mide la pantalla SIN contar las barras del navegador: el bloque queda más alto que lo visible, se corta abajo o "brinca" al hacer scroll. Usa 100svh/100dvh (con 100vh antes como respaldo).` });
  }
  if (esTactil && hoverRevela) {
    add({ id: "solo-hover", gravedad: "aviso", titulo: "Cosas que solo aparecen al pasar el ratón",
      detalle: `${hoverRevela} regla(s) :hover muestran o mueven contenido fuera de @media (hover:hover) — p.ej. ${reglasHover.join(" | ")}. En celular no hay ratón: ese contenido no se ve o se queda "pegado" tras tocar. Verifica que haya otra forma de llegar a él.` });
  }

  // ---------- 8. Imágenes y video ----------
  const dpr = window.devicePixelRatio || 1;
  document.querySelectorAll("img").forEach((img) => {
    if (!visible(img)) return;
    const b = img.getBoundingClientRect();
    if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) {
      add({ id: "imagen-rota", gravedad: "error", titulo: "Imagen que no carga", detalle: img.currentSrc || img.src, selector: selectorDe(img), rect: r(img) });
      return;
    }
    if (!img.naturalWidth) return;
    const fit = getComputedStyle(img).objectFit;
    const rn = img.naturalWidth / img.naturalHeight, rv = b.width / b.height;
    if ((fit === "fill" || fit === "") && Math.abs(rn - rv) / rn > 0.06 && b.width > 40) {
      add({ id: "imagen-deformada", gravedad: "error", titulo: "Foto estirada/aplastada",
        detalle: `Proporción original ${rn.toFixed(2)}, mostrada ${rv.toFixed(2)}. Falta object-fit: cover/contain o height:auto.`, selector: selectorDe(img), rect: r(img) });
    }
    if (img.naturalWidth > b.width * dpr * 2.5 && img.naturalWidth > 1200) {
      add({ id: "imagen-pesada", gravedad: "info", titulo: "Foto mucho más grande de lo necesario",
        detalle: `Se descarga de ${img.naturalWidth}px para mostrarse a ${Math.round(b.width)}px. En datos móviles tarda; usa srcset/sizes o una versión más chica.`, selector: selectorDe(img), rect: r(img) });
    }
  });
  document.querySelectorAll("video").forEach((v) => {
    if (!visible(v)) return;
    if (v.autoplay && !v.hasAttribute("playsinline"))
      add({ id: "video-playsinline", gravedad: "error", titulo: "Video autoplay sin playsinline",
        detalle: "En iPhone, un video sin playsinline se abre a pantalla completa o no arranca. Debe llevar autoplay muted playsinline.", selector: selectorDe(v), rect: r(v) });
    if (v.autoplay && !v.muted)
      add({ id: "video-sin-muted", gravedad: "error", titulo: "Video autoplay con sonido",
        detalle: "Los celulares bloquean el autoplay con sonido: el video se queda congelado. Debe ir muted.", selector: selectorDe(v), rect: r(v) });
  });

  // Video, iframe (YouTube, Vimeo, mapas) o foto principal MÁS ALTO que la pantalla:
  // en celular no se ve entero sin hacer scroll (caso típico: video vertical 9:16 a todo el ancho).
  // Alto ÚTIL: la pantalla menos las barras fijas de arriba/abajo (cabecera, barra de pagar…).
  let barras = 0;
  for (const el of todos) {
    const cs = getComputedStyle(el);
    if (cs.position !== "fixed" && cs.position !== "sticky") continue;
    if (!visible(el)) continue;
    const b = el.getBoundingClientRect();
    if (b.width < W * 0.5 || b.height > H * 0.5) continue;
    if (b.top <= 1 || b.bottom >= H - 1) barras += Math.min(b.height, H * 0.4);
  }
  const Hutil = Math.max(H * 0.5, H - barras);
  document.querySelectorAll("video, iframe, img, canvas, model-viewer").forEach((m) => {
    if (!visible(m)) return;
    const b = m.getBoundingClientRect();
    // lo protagonista: ocupa buena parte del ancho, o es un video/iframe (lo que la gente quiere ver entero)
    const protagonista = b.width >= W * 0.4 || ((m.tagName === "VIDEO" || m.tagName === "IFRAME") && b.width >= 200);
    if (!protagonista) return;
    if (b.height > Hutil * 1.02) {
      add({ id: "media-mas-alta-que-pantalla", gravedad: (m.tagName === "IMG" || !esTactil) ? "aviso" : "error",
        titulo: `${m.tagName === "VIDEO" ? "Video" : m.tagName === "IFRAME" ? "Video/mapa incrustado" : m.tagName === "CANVAS" ? "3D/canvas" : "Imagen"} más alto que la pantalla`,
        detalle: `Mide ${Math.round(b.width)}×${Math.round(b.height)}px y el alto útil es de ${Math.round(Hutil)}px (pantalla ${H}px${barras ? ` menos ${Math.round(barras)}px de barras fijas` : ""}): no se ve entero sin hacer scroll. Limita su alto al alto útil (p. ej. max-height: calc(100svh - barras) y object-fit: contain) o usa un formato más bajo.`,
        selector: selectorDe(m), rect: r(m) });
    }
  });

  // ---------- 9. Canvas / 3D ----------
  document.querySelectorAll("canvas").forEach((c) => {
    if (!visible(c)) return;
    const b = c.getBoundingClientRect();
    if (b.width * b.height < 20000) return;
    const ta = getComputedStyle(c).touchAction;
    if (esTactil && (ta === "auto" || ta === "")) {
      add({ id: "canvas-touch-action", gravedad: "info", titulo: "Canvas sin touch-action definido",
        detalle: "Si este canvas responde a arrastrar (3D, mapas), decide qué gesto es de la página y cuál del canvas: touch-action: pan-y deja hacer scroll vertical sobre él; none lo bloquea. Pruébalo con el dedo.", selector: selectorDe(c), rect: r(c) });
    }
    if (c.width > b.width * Math.min(dpr, 2) * 1.3 && esTactil) {
      add({ id: "canvas-resolucion", gravedad: "info", titulo: "Canvas a resolución muy alta",
        detalle: `Dibuja ${c.width}px para ${Math.round(b.width)}px visibles (DPR ${dpr}). En celulares limita el pixelRatio a 2 para no calentar el teléfono ni bajar los FPS.`, selector: selectorDe(c), rect: r(c) });
    }
  });

  // ---------- 9b. Pantallas anchas: contenido pegado a un lado (lo vio la gente en un monitor de 2560 px) ----------
  if (!esTactil && W >= 1500) {
    const piezas = [...document.querySelectorAll("h1,h2,h3,p,img,video,canvas,button,a,li,label,input")]
      .filter((el) => visible(el) && !el.closest("nav,header,footer,[role=navigation],[role=banner]") && getComputedStyle(el).position !== "fixed")
      .map((el) => { if (/^(H1|H2|H3|P|LI|LABEL)$/.test(el.tagName)) { const rg = document.createRange(); rg.selectNodeContents(el); return rg.getBoundingClientRect(); } return el.getBoundingClientRect(); })
      .filter((b) => b.width > 8 && b.height > 8 && b.top < H * 2 && b.width < W * 0.98);
    if (piezas.length >= 4) {
      // por franjas de 160 px de alto: en cada una, cuánto aire queda a cada lado
      const franjas = {};
      piezas.forEach((b) => { for (let y = Math.max(0, Math.floor(b.top / 160)); y <= Math.floor(Math.min(b.bottom, H * 2) / 160); y++) {
        const f = franjas[y] || (franjas[y] = { izq: W, der: 0 }); f.izq = Math.min(f.izq, b.left); f.der = Math.max(f.der, b.right); } });
      const fs = Object.values(franjas);
      const chuecas = fs.filter((f) => f.der - f.izq > W * 0.25 && Math.abs(f.izq - (W - f.der)) > W * 0.15);
      if (fs.length && chuecas.length / fs.length >= 0.25) {
        const f = chuecas[0]; const lado = (W - f.der) > f.izq ? "izquierda" : "derecha";
        add({ id: "contenido-pegado-a-un-lado", gravedad: "aviso",
          titulo: `En esta pantalla tan ancha parte del contenido se queda pegado a la ${lado}`,
          detalle: `En ${chuecas.length} de ${fs.length} franjas de la pantalla queda mucho más aire de un lado que del otro (por ejemplo ${Math.round(f.izq)}px a la izquierda y ${Math.round(W - f.der)}px a la derecha, en una pantalla de ${W}px). Se ve "mal cortado": centra el contenido con un ancho máximo (max-width: 1280px; margin: 0 auto, o padding lateral que crezca con la pantalla).`,
          rect: { x: Math.round(f.izq), y: 0, w: Math.round(f.der - f.izq), h: Math.round(Math.min(H, document.documentElement.scrollHeight)) } });
      }
    }
  }

  // ---------- 10. Inventario de interacción (para que quien revisa sepa qué probar con el dedo) ----------
  const carruseles = todos.filter((el) => {
    const cs = getComputedStyle(el);
    return /(auto|scroll)/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 10 && visible(el);
  });
  const inventario = {
    carruseles: carruseles.slice(0, 8).map(selectorDe),
    formularios: document.querySelectorAll("form").length,
    campos: document.querySelectorAll("input:not([type=hidden]), select, textarea").length,
    dialogos: document.querySelectorAll('dialog, [role="dialog"], [aria-modal="true"]').length,
    botonesMenu: [...document.querySelectorAll('[aria-expanded], [aria-controls], .hamburger, .menu-toggle, [class*="burger"], [class*="menu-btn"]')].filter(visible).slice(0, 6).map(selectorDe),
    canvas: document.querySelectorAll("canvas").length,
    videos: document.querySelectorAll("video").length,
    iframes: document.querySelectorAll("iframe").length,
    scrollSnap: todos.filter((el) => getComputedStyle(el).scrollSnapType !== "none").length,
    hojasCssNoLeidas: hojasBloqueadas,
  };

  return {
    ancho: W, alto: H, dpr,
    altoPagina: document.documentElement.scrollHeight,
    titulo: document.title,
    hallazgos,
    omitidos: Object.fromEntries(Object.entries(conteo).filter(([, n]) => n > MAX_POR_TIPO).map(([k, n]) => [k, n - MAX_POR_TIPO])),
    inventario,
  };
}
