# Lección 3 · Que funcione con el dedo (~2 min)

> Guion para Claude. Antes lee `guia/estilo.md` y retoma `nombre` y `pagina` de `~/.dakexplica/dak-revision-movil.json`. **ACCIÓN** = lo haces tú. **BOTONES** = `AskUserQuestion`. **ALTO** = esperas.

## 1 · Abre (un solo mensaje que cierra el turno)

**ACCIÓN:** banner:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REVISIÓN EN 15 PANTALLAS
  ▰▰▰  Lección 3 de 3 · Que funcione con el dedo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

"Última, [nombre]. [Retoma su `objetivo` en una frase: "Me dijiste que te preocupaban los botones: aquí es donde lo comprobamos"]. Que se vea bien no basta: también tiene que funcionar con el dedo. Ahí es donde casi todas fallan."

Cierra el mensaje con la pregunta como **lista numerada** · "¿Qué pruebo como si fuera una persona? Responde 1 o 2."
1. **Todo: bajar hasta el final, tocar el botón principal y girar el celular (recomendado)**
2. **Solo bajar hasta el final**

**ALTO** (fin del turno).

## 2 · Probar con el dedo

**Antes, avisa:** "Va. Ahora la uso como una persona en 4 aparatos: [lo que eligió]. Tarda unos segundos."

**ACCIÓN:** arma un `pasos.json` corto con lo que eligió y córrelo en los 4 rápidos:

```json
[{"recorrer": true}, {"tocar_texto": "<botón principal>"}, {"rotar": true}]
```

```bash
python3 <skill>/scripts/tocar.py <la página> --pasos pasos.json --dispositivos rapido --salida /tmp/revision-movil/guia/tocar
```

**Después, el mensaje (obligatorio):** "Listo, la probé con el dedo. Esto pasó:" — va en el mismo mensaje que el paso 3 ("Así la usas") y ese mensaje cierra con la pregunta de mejoras como lista numerada ("responde 1, 2 o 3"), no con botones, para que nada se resuma.

**Resultado** (una línea por aparato, ✓ o qué falló y por qué: "tapado por el banner", "el scroll se atora").

Si es la de ejemplo: "Aquí los botones son de mentira; en tu página real esta prueba también te dice si un botón quedó tapado o si el scroll se atora a media página. Eso nadie lo ve desde la compu."

## 3 · Así la usas de aquí en adelante (lo más importante)

"Todo lo que hicimos paso a paso, la herramienta lo hace **sola**. No tienes que pedirle cada cosa. Le dices una frase y ella:
1. abre tu página en las 15 pantallas,
2. mira las capturas (no solo los números),
3. la prueba con el dedo,
4. arregla lo obvio,
5. te pregunta lo que cambia tu diseño,
6. y te enseña el antes y después."

**Frases para usarla** (cada una en su bloque para copiar, siempre con el nombre de la skill para que Claude la use seguro):

```
Usando la skill dak-revision-movil, revisa mi página en los 15 dispositivos
```
→ lo de arriba, completo

```
Usando la skill dak-revision-movil, revísalo antes de terminar
```
→ mientras construyes algo

```
Usando la skill dak-revision-movil, revisa este video para Reels
```
→ formato, lo que tapa la app y el peso

```
Usando la skill dak-revision-movil, esto se ve mal en mi celular, arréglalo
```
→ junto con una captura de tu celular

**Para que no te pase:**
- Revisa también las otras páginas, no solo la portada ("revisa también /contacto").
- Después de publicar, revisa el link real ("revísalo en el link de producción").

**Pregunta al final del mensaje (lista numerada, no botones)** · "¿Quieres alguna mejora opcional? Responde 1, 2 o 3" (solo las que no tenga; pregunta antes de instalar). **ALTO** (fin del turno).
- **Safari de verdad** — en Mac con Xcode: el iPhone y el iPad del Simulador con el Safari real
- **Revisar videos** — necesita ffmpeg
- **No, así está bien**

## 4 · Cierre

**Lo que lograste, [nombre]**
- Ver tu página como la ve todo el mundo.
- Arreglarla sin perder tu diseño.
- Comprobar que funcione con el dedo.

Despídete con energía y retoma su `objetivo` y su página de la lección 1 ("Tu [tienda] ya se ve bien en todos lados, y ahora con una frase la revisas cada vez que cambies algo").

"Esta herramienta es de **@dakexplica**: sígueme para la siguiente. Las demás están gratis en el link de mi perfil. ¿Quieres repetir algo? «guía lección 1», «2» o «3»."

**ACCIÓN:** guarda `leccion: 3, terminada: true`. Si usaste copia de práctica, bórrala (`/tmp/revision-movil/guia/`).
