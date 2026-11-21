# Lección 1 · Mírala como la ve todo el mundo (~2 min)

> Guion para Claude. Antes lee `guia/estilo.md`. Entre comillas va la idea de lo que dices (con tus palabras). **ACCIÓN** = lo haces tú. **BOTONES** = pregunta con `AskUserQuestion` (opciones para hacer clic; si no existe la herramienta, una lista numerada corta). **ALTO** = esperas. Nunca sigas sin respuesta.

## 1 · Bienvenida (tu PRIMER mensaje, antes de cualquier botón o comando)

**Regla dura:** lo primero que ve la persona es esta bienvenida, como mensaje propio. Primero escribes el mensaje y **después** abres los botones. Nada de narrar lo que haces ni hablar de la persona en tercera persona ("Llevo la revisión…", "ya confirmé que…", "para Derek"). El Paso 0 corre después y en silencio.

**ACCIÓN:** escribe este mensaje (con tus palabras, sin quitar ninguna parte):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REVISIÓN EN 15 PANTALLAS
  ▰▱▱  Lección 1 de 3 · Mírala como la ve todo el mundo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **¡Hola, [nombre]! Bienvenido a la guía 👋**
> Qué bueno que estás aquí. En unos 5 minutos vas a ver tu página en 15 pantallas, arreglarla y probarla con el dedo.
>
> *"La hice porque me pasaba siempre: algo se veía perfecto en la compu y en el celular estaba todo cortado. Ahora no entrego nada sin pasarlo por aquí." — @dakexplica*
>
> Son 3 lecciones cortas. Te enseño lo que hace la herramienta por dentro; cuando la uses normal, hace todo esto **sola**.

- **El nombre:** si lo sabes (`~/.dakexplica/dak-revision-movil.json` o el sistema), úsalo. Si no, el saludo es "¡Hola! Bienvenido a la guía 👋" y al final del mensaje: "Antes de empezar, ¿cómo te llamo?" **ALTO** y guárdalo. Después ya sí los botones.

**BOTONES** (dos preguntas en la misma ventana):
1. "¿Qué quieres revisar?"
   - **Una página mía** — "la reviso y, si me das la carpeta, la arreglo"
   - **La de ejemplo** — "una cafetería inventada con errores puestos, para practicar sin tocar lo tuyo"
2. "¿Qué te preocupa más de cómo se ve en el celular?" (esto es para darle seguimiento)
   - **Que se vea cortado o encimado**
   - **Que los botones y el menú no funcionen con el dedo**
   - **Que se vea bien en todo (todo lo anterior)**

**ALTO.** Reacciona en una línea a lo que eligió antes de seguir ("Perfecto, eso es justo lo que más se le escapa a la gente; lo vamos a revisar con lupa"). Guarda `objetivo`.

## 2 · Si eligió una página suya: revisar el acceso (no te lo saltes)

**BOTONES** · "¿Tienes el proyecto en esta compu?"
- **Sí, tengo la carpeta** — "así la reviso y la arreglo"
- **Solo tengo el link** — "la reviso completa, pero no puedo cambiarla"

Con **link**: pídelo en una línea y avisa: "Con el link veo todo lo que ve un visitante. Para arreglar necesito la carpeta del proyecto; no necesito contraseñas ni tu cuenta donde la publicas."

Con **carpeta**: pide la ruta con un ejemplo genérico (nunca una ruta real de quien hizo la skill): "Arrastra la carpeta aquí al chat o pega su ruta, por ejemplo `/Users/tu-nombre/Documents/mi-pagina`." **ACCIÓN** — compruébalo tú antes de seguir y dilo en una lista corta:
- ✓/✗ la carpeta existe y la puedo leer;
- ✓/✗ encontré la página (el `index.html`, o el proyecto Next/Astro/Vite/Shopify y cómo se abre: `references/stacks.md`);
- ✓/✗ puedo guardar cambios ahí (crea y borra un archivo de prueba);
- si tiene git: ¿hay cambios sin guardar? Si sí, **BOTONES** "¿Guardo un respaldo antes de tocar nada? · Sí (recomendado) · No, sigue".
- si la página tiene login: avisa que se abre una ventana para que entre la persona (nunca escribes su contraseña).
Si algo falla, dile qué y cómo resolverlo; si no se puede, sigue solo con el link.

**ALTO.**

## 3 · Paso 0 (en silencio si todo está bien)

**ACCIÓN:** `python3 <skill>/scripts/paso0.py`. Si todo ✓: "Ya tienes todo lo que necesita." Si falta algo: una frase de qué es y **BOTONES** "¿Lo instalo? · Sí · No". **ALTO** solo si hubo que preguntar.

## 4 · La primera revisión

"Todo listo, [nombre]. Ahora pídemelo tú, una sola vez, para que veas lo fácil que es. Copia y pega esto:"

```
Usando la skill dak-revision-movil, revisa mi página en los 15 dispositivos
```

"Así se lo pides siempre que quieras revisar una página, aunque no estés en la guía."

**ALTO.** (Es el único momento de la guía donde se escribe; lo demás es con botones.)

**ACCIÓN:** revisión completa (ejemplo: `<skill>/guia/ejemplo`):

```bash
python3 <skill>/scripts/revisar.py <link o carpeta> --salida /tmp/revision-movil/guia/antes
```

**Antes de correrla, avisa** (texto visible): "Va. La estoy abriendo en 7 celulares, 4 tabletas y 4 compus, y tomo una captura de cada una. Tarda como un minuto."

**ACCIÓN:** muestra `hoja.png` (Read) y, si hay errores, `iphone/marcado.png`.

## 5 · Lo que encontré (MENSAJE obligatorio, antes de cualquier botón)

**Regla dura:** después de la revisión SIEMPRE escribes este mensaje. Nunca pases de los comandos directo a los botones: la persona tiene que saber qué hiciste y qué encontraste.

> **Listo, [nombre]. Ya revisé tu página en las 15 pantallas.**
>
> **Resultado**
> - Lo que te preocupaba ([objetivo]): [cómo salió eso, primero que nada]
> - ✓ [N] pantallas bien: [dónde, en una línea: "en las compus y en el iPad se ve perfecta"]
> - ✗ [N] con problemas: [dónde: "en los 7 celulares y en la tableta chica"]
> - Lo más grave: [como lo vive la gente: "en el iPhone el título se corta y el botón no se ve completo"]
> - Lo que vi yo mirando (el script no lo marca): [1 cosa, si hay]
>
> Por eso miro las capturas además de los números.
>
> **Lo que lograste**
> - Viste tu página como la ve todo el mundo.
> - Ya sabes qué falla y en qué aparatos.
>
> **Lo que sigue:** en la lección 2 arreglo [lo más grave, con sus palabras] sin tocar tu diseño, te pregunto lo que sí lo cambiaría, y te enseño el antes y después lado a lado.

**BOTONES** (después del mensaje) · "¿Seguimos con la 2?"
- **Sí, vamos a la 2**
- **Lo dejo aquí** — "cuando quieras: «retoma la guía»"

**ACCIÓN:** guarda en `~/.dakexplica/dak-revision-movil.json`: `nombre`, `leccion: 1`, `pagina` (ruta o link, o "ejemplo"), `puede_editar` (true/false), `objetivo` (si lo dijo).
