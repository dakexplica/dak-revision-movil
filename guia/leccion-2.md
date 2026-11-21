# Lección 2 · Arréglala con lo tuyo (1–2 min)

> Guion para Claude. Antes, lee `guia/estilo.md`. Retoma el nombre, la página y lo que le preocupaba de `~/.dakexplica/dak-revision-movil.json`. **ACCIÓN** = lo haces tú. **ALTO** = esperas la respuesta. Usa la página que eligió en la lección 1 (está en `~/.dakexplica/dak-revision-movil.json`). Si usaron la de ejemplo, **cópiala primero** a `/tmp/revision-movil/guia/pagina/` y trabaja sobre la copia: la de la skill no se toca.
>
> **Si solo dio el link** (sin la carpeta del proyecto): no se puede editar. Dile: "Con el link ya vimos qué falla; para arreglarlo necesito la carpeta del proyecto en tu compu. ¿Me dices dónde está? Si no la tienes a la mano, te dejo la lista de cambios para quien lleve tu página y seguimos la lección con la de ejemplo." **ALTO.**

**ACCIÓN:** muestra este banner en un bloque de código:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   REVISIÓN EN 15 PANTALLAS  ·  guía 2 de 3
   Arreglarla sin que toque tu diseño
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Retoma con su nombre y lo de la lección 1: "Bien, [nombre]. Ya vimos que en el celular [lo más grave]. Vamos a arreglarlo."

"La skill separa los problemas en dos:
- **lo obvio** (letra chica, botones difíciles de tocar, algo que se sale de la pantalla), que arregla sola sin cambiar tu diseño;
- **lo que cambia tu diseño** (mover el menú, reordenar, quitar algo), que siempre te pregunta antes."

"Pídemelo tú: escríbeme **«Arregla lo obvio y pregúntame lo que cambie mi diseño»**." **ALTO.**

**ACCIÓN:** arregla lo obvio en el código (pasos 5 y 6 de SKILL.md). Mientras lo haces, di en una línea cada cosa: "Pongo la letra de 'TOSTADORES' más grande para que se lea en celular".

**ACCIÓN:** si hay algo que cambia el diseño, pregúntalo con `AskUserQuestion` (o con una pregunta corta si no está disponible), con tu recomendación primero. Ejemplo con la página de ejemplo:
> "En el celular el menú no cabe en una línea y se corta. ¿Lo paso a dos líneas debajo del logo? (recomendado) · ¿Lo dejo en una línea y achico las letras?"

**ALTO.**

**ACCIÓN:** aplica lo que eligió, vuelve a medir y compara:

```bash
python3 <skill>/scripts/revisar.py <la misma página> --salida /tmp/revision-movil/guia/despues
python3 <skill>/scripts/comparar.py /tmp/revision-movil/guia/antes /tmp/revision-movil/guia/despues
```

**ACCIÓN:** muéstrale `antes-despues.png` con Read.

"Antes: [X] pantallas con problemas. Ahora: [Y]. Lo que vas a notar en el celular: [lo más visible, en una frase]." Celébralo y conéctalo con lo que le preocupaba ("Lo que te preocupaba de tu tienda ya no pasa").

Si algo quedó o salió algo **NUEVO** (un arreglo que rompió otra cosa), dilo y arréglalo antes de seguir.

"Tip: para pedir cambios no necesitas saber de código. Dime lo que ves, por ejemplo «en el iPad el botón queda muy abajo» o «en el celular quiero la foto primero»."

Cierra con el resumen:

**Lo que lograste, [nombre]**
- Arreglaste lo obvio sin tocar tu diseño.
- Decidiste tú lo que cambiaba el diseño.
- Comprobaste el antes y el después en las 15 pantallas.

"Ya está bien hecha. En la última (2 minutos) vas a ver que también funcione con el dedo, que es donde la mayoría falla sin saberlo. ¿Vamos?"

**ALTO.** Guarda `"leccion": 2`.
