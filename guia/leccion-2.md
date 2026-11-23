# Lección 2 · Arréglala sin que toque tu diseño (~2 min)

> Guion para Claude. Antes lee `guia/estilo.md` y retoma `nombre`, `pagina` y `puede_editar` de `~/.dakexplica/dak-revision-movil.json`. **ACCIÓN** = lo haces tú. **BOTONES** = `AskUserQuestion`. **ALTO** = esperas.

## 1 · Abre (pasos 1, 2 y 3 van en UN solo mensaje que cierra el turno)

Cuando diga «sigue»: copia la página de práctica y prepara los arreglos obvios **en silencio**, y después escribe un solo mensaje con el banner, lo que retomas, las dos reglas, los arreglos con ✓ y la pregunta de diseño como **lista numerada** ("responde 1 o 2"). Así nada se resume. **ALTO** (fin del turno).

**ACCIÓN:** banner:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REVISIÓN EN 15 PANTALLAS
  ▰▰▱  Lección 2 de 3 · Arréglala sin que toque tu diseño
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

"Bien, [nombre]. Ya vimos que [lo más grave de la lección 1]. [Retoma su `objetivo`: "Y como lo que más te preocupaba era que se viera cortado, empezamos por ahí."] Vamos a arreglarlo."

**Si su página salió bien en las 15** (0 problemas en la lección 1): no inventes arreglos. Celébralo y avisa en una línea: **"Tu página ya se ve bien en las 15 pantallas, ¡bien hecha! Para que veas cómo arregla cuando algo falla, lo hacemos con la de ejemplo; la tuya no la toco."** y sigue con la de ejemplo.

Si `puede_editar` es false (solo link): "Con el link no puedo cambiar tu página. Te dejo la lista de cambios para quien la lleve y seguimos con la de ejemplo para que veas cómo se arregla." Entrega la lista (corta) y sigue con el ejemplo.

## 2 · Las dos reglas de la herramienta

"La herramienta separa lo que encuentra en dos:
- **Lo obvio** (letra chica, botones difíciles de tocar, algo que se sale): lo arregla sola, sin cambiar tu diseño.
- **Lo que cambia tu diseño** (mover el menú, reordenar, quitar algo): siempre te pregunta antes."

## 3 · Arreglar

**Página de ejemplo:** copia `<skill>/guia/ejemplo/` a `/tmp/revision-movil/guia/pagina/` y trabaja ahí (la de la skill no se toca). El arreglo ya está preparado en `<skill>/guia/ejemplo-arreglado/index.html`: no lo inventes desde cero, así es rápido.
- **ACCIÓN:** di lo obvio que arreglas, una línea cada uno, con ✓ (letra de "TOSTADORES" más grande, botones del menú más fáciles de tocar, título y botones que ya no se salen, tarjetas que bajan a una columna).
- **Pregunta al final del mensaje (lista numerada)** · "Esto sí cambia tu diseño: en el celular el menú no cabe en una línea. ¿Qué hago? Responde 1 o 2."
  1. **Ponerlo en dos líneas bajo el logo (recomendado)**
  2. **Dejarlo en una línea con letra más chica**
- **ALTO.** Copia `ejemplo-arreglado/index.html` sobre la copia de práctica (si eligió la otra opción, ajusta solo el menú).

**Página suya (con carpeta):** sigue los pasos 5–6 de `SKILL.md` de verdad: arregla lo obvio (una línea por arreglo, con ✓) y junta lo que cambia el diseño al final del mismo mensaje como lista numerada (máx. 4 preguntas, tu recomendación primero; "responde por ejemplo 1A 2B"). **ALTO** y aplica lo que elija.

## 4 · Comprobar

**Antes, avisa:** "Ya arreglé. Ahora la vuelvo a medir en 4 aparatos (iPhone, Android, iPad y Mac) para comprobar que quedó bien. Son unos segundos."

**ACCIÓN:** vuelve a medir en los 4 aparatos clave (rápido) y compara:

```bash
python3 <skill>/scripts/revisar.py <la página> --dispositivos rapido --salida /tmp/revision-movil/guia/despues
python3 <skill>/scripts/comparar.py /tmp/revision-movil/guia/antes /tmp/revision-movil/guia/despues
```

**ACCIÓN:** muestra **`antes-despues-claro.png`** (Read): cada aparato en pareja, ANTES y DESPUÉS, en rojo si tiene errores y en verde si quedó bien. (No uses `antes-despues.png` para explicar: es la versión completa y no se entiende de un vistazo.)

**Resultado**
- iPhone: [N errores] → bien · Android: … · iPad: … · Mac: …
- Lo que vas a notar: [lo más visible, en una frase, conectado con lo que le preocupaba]

Si salió algo **NUEVO** (un arreglo que rompió otra cosa), dilo y arréglalo antes de seguir.

## 5 · Cierre (MENSAJE obligatorio que CIERRA el turno, sin botones)

Junta en este mismo mensaje el **Resultado** del paso 4 (con la imagen ya mostrada) y el cierre: si pones botones después, la app lo resume en una línea.

> **Lo que lograste, [nombre]**
> - Arreglaste lo obvio sin tocar tu diseño: [los arreglos, en una línea].
> - Decidiste tú lo que sí lo cambiaba: [lo que eligió].
>
> **Lo que sigue:** en la lección 3 la uso como una persona con el dedo (bajo hasta el final, toco el botón principal, giro el celular). Ahí es donde casi todas fallan sin que nadie se dé cuenta.

> **¿Vamos a la última?** Escríbeme **«sigue»** y pasamos a la lección 3.

**ALTO** (fin del turno).

**ACCIÓN:** guarda `leccion: 2`.
