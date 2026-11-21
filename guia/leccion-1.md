# Lección 1 · Mírala como la ve todo el mundo (~2 min)

> Guion para Claude. Antes lee `guia/estilo.md`. Entre comillas va la idea de lo que dices (con tus palabras). **ACCIÓN** = lo haces tú. **BOTONES** = pregunta con `AskUserQuestion` (opciones para hacer clic; si no existe la herramienta, una lista numerada corta). **ALTO** = esperas. Nunca sigas sin respuesta.

## 1 · Bienvenida

**ACCIÓN:** banner en bloque de código:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REVISIÓN EN 15 PANTALLAS
  ▰▱▱  Lección 1 de 3 · Mírala como la ve todo el mundo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

"¡Hola, [nombre]!" (si no sabes el nombre: "¡Hola! ¿Cómo te llamo?" **ALTO**, y guárdalo).

Nota de quien la hizo (dila como suya):
> *"La hice porque me pasaba siempre: algo se veía perfecto en la compu y en el celular estaba todo cortado. Ahora no entrego nada sin pasarlo por aquí." — @dakexplica*

"Son 3 lecciones cortas. Te voy enseñando lo que hace la herramienta por dentro; cuando la uses normal, hace todo esto **sola**."

**BOTONES** · "¿Qué quieres revisar?"
- **Una página mía** — "la reviso y, si me das la carpeta, la arreglo"
- **La de ejemplo** — "una cafetería inventada con errores puestos, para practicar sin tocar lo tuyo"

**ALTO.**

## 2 · Si eligió una página suya: revisar el acceso (no te lo saltes)

**BOTONES** · "¿Tienes el proyecto en esta compu?"
- **Sí, tengo la carpeta** — "así la reviso y la arreglo"
- **Solo tengo el link** — "la reviso completa, pero no puedo cambiarla"

Con **link**: pídelo en una línea y avisa: "Con el link veo todo lo que ve un visitante. Para arreglar necesito la carpeta del proyecto; no necesito contraseñas ni tu cuenta donde la publicas."

Con **carpeta**: pide la ruta y **ACCIÓN** — compruébalo tú antes de seguir y dilo en una lista corta:
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

"Ahora pídemelo tú, una sola vez, para que veas lo fácil que es. Escribe:
**revisa mi página en los 15**"

**ALTO.** (Es el único momento de la guía donde se escribe; lo demás es con botones.)

**ACCIÓN:** revisión completa (ejemplo: `<skill>/guia/ejemplo`):

```bash
python3 <skill>/scripts/revisar.py <link o carpeta> --salida /tmp/revision-movil/guia/antes
```

Mientras corre: "La estoy abriendo en 7 celulares, 4 tabletas y 4 compus. Tarda como un minuto."

**ACCIÓN:** muestra `hoja.png` (Read) y, si hay errores, `iphone/marcado.png`.

Resume así (corto, con estos títulos):

**Resultado**
- ✓ [N] pantallas bien · ✗ [N] con problemas
- Lo más grave: [como lo vive la gente: "en el iPhone el título se corta y el botón no se ve completo"]
- Lo que vi yo mirando (el script no lo marca): [1 cosa, si hay]

"Por eso miro las capturas además de los números."

## 5 · Cierre

**Lo que lograste, [nombre]**
- Viste tu página como la ve todo el mundo.
- Sabes qué falla y en qué aparatos.

**BOTONES** · "¿Seguimos? En la 2 lo arreglamos y ves el antes y después lado a lado."
- **Sí, vamos a la 2**
- **Lo dejo aquí** — "cuando quieras: «retoma la guía»"

**ACCIÓN:** guarda en `~/.dakexplica/dak-revision-movil.json`: `nombre`, `leccion: 1`, `pagina` (ruta o link, o "ejemplo"), `puede_editar` (true/false), `objetivo` (si lo dijo).
