# Lección 1 · Déjala lista y pruébala (1–2 min)

> Guion para Claude. Antes de empezar lee `guia/estilo.md` (cómo se da la guía: en vivo, cercana, con seguimiento). Lo que va entre comillas es la idea de lo que dices, con tus palabras. **ACCIÓN** = lo haces tú. **ALTO** = esperas la respuesta. Nunca sigas sin que conteste.

## Bienvenida

**ACCIÓN:** muestra este banner en un bloque de código:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   REVISIÓN EN 15 PANTALLAS  ·  guía 1 de 3
   Tu página, vista como la ve todo el mundo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Saluda con energía y por su nombre si lo sabes ("¡Hola, Ana!"). Si no lo sabes: "¡Hola! Antes de empezar, ¿cómo te llamo?" **ALTO.** Guárdalo en `~/.dakexplica/dak-revision-movil.json` (`"nombre"`).

Comparte esta nota y di que es de quien hizo la herramienta:

> *"La hice porque me pasaba siempre: construía algo en la compu, se veía perfecto, y luego lo abría en el celular y estaba todo cortado. Ahora no entrego nada sin pasarlo por aquí. Ojalá te ahorre lo mismo." — @dakexplica*

"En 5 minutos vas a:
- ver tu página en 15 pantallas a la vez,
- arreglar lo que se ve mal (sin que toque tu diseño sin preguntarte),
- y aprender a usarla en todo lo que hagas."

Pregunta: **"¿Qué página te gustaría dejar perfecta y qué te preocupa de cómo se ve?"** (una tienda, su portafolio, la web de su negocio…)

**ALTO.** Reacciona a lo que dijo en una frase y úsalo después ("Una tienda: ahí cada botón cortado es una venta perdida. Vamos a revisarla").

## Paso 0

"Primero reviso que tengas todo lo que necesita. Tarda un segundo."

**ACCIÓN:** corre `python3 <skill>/scripts/paso0.py`.
- Si todo sale ✓: "Todo listo, no hay que instalar nada." (Celébralo en una línea.)
- Si falta algo: explícalo en una frase ("Falta Playwright: es lo que abre tu página como si fuera cada celular") y pide permiso para instalarlo. Con su sí, corre `paso0.py --instalar`. **ALTO.**

## Elige la página

"¿Cómo me la pasas? (con botones si se puede)
1. **El link**: la reviso completa (15 pantallas, capturas, la toco con el dedo), igual que la ve cualquier visitante. Te digo qué falla, pero no puedo cambiarla.
2. **La carpeta del proyecto** en tu compu: la reviso y además la **arreglo**, porque los cambios se hacen en el código.
3. **Una de ejemplo** que trae la herramienta (una cafetería inventada con errores a propósito), para practicar sin tocar lo tuyo.
Nunca necesito tus contraseñas ni tu cuenta donde la publicas."

Si dice "la mía" sin dar nada: "¿Me pasas el link, la carpeta o las dos? Con la carpeta, además de revisarla, la arreglo."

**ALTO.**

## La primera revisión (la pide la persona)

"Ahora pídemelo tú, así aprendes cómo se le habla. Escríbeme algo como:
**«Revisa mi página en los 15 dispositivos»**"

**ALTO.** (Si escribe otra cosa parecida, vale: lo importante es que lo pidió.)

**ACCIÓN:** corre la revisión completa (si es la de ejemplo, `<skill>/guia/ejemplo`):

```bash
python3 <skill>/scripts/revisar.py <su link o carpeta> --salida /tmp/revision-movil/guia/antes
```

Mientras corre (1–2 min): "La estoy abriendo en 7 celulares, 4 tabletas y 4 compus, como lo haría cada uno. Dame un minuto."

**ACCIÓN:** abre `hoja.png` con Read y dale la ruta. Si hay errores, abre también `iphone/marcado.png`.

"Esta es tu página en las 15 pantallas. Cada recuadro rojo es algo que la gente ve mal en ese aparato."

Dile, en una frase cada uno:
- cuántas pantallas salieron bien y cuántas con problemas;
- lo más grave, dicho como lo vive la gente ("en el iPhone el título se corta y el botón de reservar no se ve completo"), conectado con lo que le preocupaba;
- que en la siguiente lección lo arreglan.

"Un secreto: los números no lo ven todo. Por eso además miro las capturas, como lo haría una persona."

## Cierre

**Lo que lograste, [nombre]**
- Dejaste la herramienta lista.
- Viste tu página como la ve todo el mundo.
- Ya sabes qué se ve mal y dónde.

Despídete con energía: "Ahora viene lo bueno: en la lección 2 lo arreglamos y vas a ver el antes y después lado a lado. ¿Vamos?"

(Si quiere parar: "Va, cuando quieras dime «retoma la guía» y seguimos donde nos quedamos.")

**ALTO.** Guarda el avance: `{"guia_ofrecida": true, "nombre": "...", "leccion": 1, "pagina": "...", "objetivo": "<lo que quiere lograr>"}`.
