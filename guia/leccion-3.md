# Lección 3 · Que funcione con el dedo (~2 min)

> Guion para Claude. Antes lee `guia/estilo.md` y retoma `nombre`, `pagina` y `objetivo` de `~/.dakexplica/dak-revision-movil.json`. **ACCIÓN** = lo haces tú. **ALTO** = esperas.
>
> **Esta lección no pregunta nada.** La herramienta siempre prueba TODO; la persona nunca tiene que elegir qué revisar. Cuando diga «sigue», haces la prueba completa en silencio y al final mandas UN solo mensaje corto (pasos 2 y 3) que cierra el turno.

## 1 · Probar todo con el dedo (en silencio)

**ACCIÓN:** lee la página y arma un `pasos.json` con **todo lo que una persona haría** en ella (no solo un botón):
- `{"recorrer": true}` — bajar hasta el final (detecta scroll atorado);
- tocar el menú (si hay botón de menú, ábrelo y ciérralo) y el botón o los 2–3 botones principales (`tocar_texto`);
- si hay carrusel: `deslizar`; si hay formulario: `escribir` en un campo (abre el teclado) y revisa que el botón de enviar siga visible;
- `{"rotar": true}` — girar el celular.

```bash
python3 <skill>/scripts/tocar.py <la página> --pasos pasos.json --dispositivos rapido --salida /tmp/revision-movil/guia/tocar
```

Revisa también a dónde llevan los botones (si apuntan a `#` o a nada, es un hallazgo).

## 2 · El mensaje (uno solo, corto, cierra el turno)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REVISIÓN EN 15 PANTALLAS
  ▰▰▰  Lección 3 de 3 · Que funcione con el dedo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **Última, [nombre].** Que se vea bien no basta: también tiene que funcionar con el dedo. [Retoma su `objetivo` en media frase.]
> Ya la usé como una persona en iPhone, Android, iPad y Mac: bajé hasta el final, toqué el menú y los botones[, llené el formulario] y giré el celular.
>
> **Resultado**
> - ✓ [lo que funcionó, agrupado en 1 línea: "el scroll, el menú y girar el celular funcionan en los 4"]
> - ✗ [cada falla en 1 línea, como la vive la gente: "«Agenda una llamada» no lleva a ningún lado: alguien lo toca y se va"]
>
> [Si es una página de práctica o le faltan cosas, dilo en una línea: "Como es una página de prueba, sus botones no llevan a nada; en una página real aquí pondrías tu WhatsApp o tu calendario."]

Máximo ~4 viñetas en Resultado. Nada de detalles técnicos del script (p. ej. "no subió en el iPad"): si no es un problema para la persona, no se menciona.

## 3 · Cierre (en el mismo mensaje)

> **Lo que lograste**
> - Viste tu página como la ve todo el mundo.
> - La arreglaste sin perder tu diseño.
> - Comprobaste que funciona con el dedo.
>
> **De aquí en adelante ya no necesitas la guía.** Todo lo que hicimos en estas 3 lecciones, la herramienta lo hace **sola, sin que le tengas que decir cada paso**. Cuando quieras revisar una página, solo pega esto:

```
Usando la skill dak-revision-movil, revisa mi página en los 15 dispositivos
```

> Esta herramienta es de **@dakexplica**: sígueme para la siguiente. Las demás están gratis en el link de mi perfil. 🙌

**Una sola frase para copiar, no una lista.** Nada de "Para que no te pase", ni lista de mejoras, ni otros comandos: el cierre tiene que sentirse como una despedida, no como un manual. (Si la persona pregunta qué más puede hacer, ahí sí le cuentas lo de videos, capturas y el Safari real.)

**ACCIÓN:** guarda `leccion: 3, terminada: true`. Si usaste copia de práctica, bórrala (`/tmp/revision-movil/guia/`). **ALTO** (fin de la guía).
