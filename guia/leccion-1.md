# Lección 1 · Déjala lista y pruébala (1–2 min)

> Guion para Claude. Lo que va entre comillas se dice (con tus palabras, en español claro, tuteando). **ACCIÓN** = lo haces tú. **ALTO** = esperas la respuesta. Nunca sigas sin que conteste. Máximo 3–4 frases seguidas sin que la persona haga o conteste algo.

Abre con este encabezado:

**Guía · 1 de 3 · Déjala lista y pruébala**
Vas a ver tu página en 15 pantallas a la vez en menos de 2 minutos.

"Primero reviso que tengas todo lo que necesita la skill."

**ACCIÓN:** corre `python3 <skill>/scripts/paso0.py`.
- Si todo sale ✓, sigue.
- Si falta algo: explícalo en una frase ("Falta Playwright: es lo que abre tu página como si fuera cada celular") y pide permiso para instalarlo. Con su sí, corre `paso0.py --instalar`.

**ALTO** (solo si hubo que pedir permiso).

"Listo. ¿Qué página revisamos? Puede ser:
1. **la tuya con el link**: la reviso completa (15 pantallas, capturas, la toco con el dedo) sin acceso a nada más, igual que la ve cualquier visitante. Te digo qué se ve mal, pero no puedo cambiarla;
2. **la tuya con la carpeta del proyecto** (en tu compu): la reviso y además puedo **arreglarla**, porque los cambios se hacen en el código. Nunca necesito tus contraseñas ni tu cuenta donde la publicas;
3. **una de ejemplo** que trae la skill (una cafetería inventada con errores a propósito), para practicar sin tocar lo tuyo."

Si dice "la mía" sin dar nada, pregunta en una línea: "¿Me pasas el link, la carpeta o las dos? Con la carpeta, además de revisarla, la arreglo."

**ALTO.**

**ACCIÓN:** corre la revisión completa sobre lo que eligió (si es la de ejemplo, `<skill>/guia/ejemplo`):

```bash
python3 <skill>/scripts/revisar.py <su link o carpeta> --salida /tmp/revision-movil/guia/antes
```

Mientras corre (1–2 min): "La estoy abriendo en 7 celulares, 4 tabletas y 4 compus, como lo haría cada uno."

**ACCIÓN:** abre `hoja.png` con Read y muéstrale la ruta. Si hay errores, abre también `marcado.png` del iPhone (`iphone/marcado.png`).

"Esto es tu página en las 15 pantallas. Cada recuadro rojo es algo que ve mal la gente en ese aparato (está numerado y explicado en el informe)."

Dile, en una frase cada uno:
- cuántas pantallas salieron bien y cuántas con problemas (de la línea final de la revisión);
- el problema más grave, dicho como lo vive la gente ("en el iPhone el título se corta y el botón de reservar no se ve completo");
- que en la siguiente lección lo arreglan.

"Una cosa importante: los números no lo ven todo. Por eso yo también miro las capturas, como lo haría una persona."

Cierra con el resumen:

**Lo que hiciste**
- Dejaste la skill lista.
- Viste tu página en 15 pantallas.
- Ya sabes qué se ve mal y dónde.

"¿Seguimos con la lección 2 para arreglarlo? (o dime «sal de la guía» y lo dejamos aquí)"

**ALTO.** Guarda el avance en `~/.dakexplica/dak-revision-movil.json`: `{"guia_ofrecida": true, "leccion": 1, "pagina": "<lo que eligió>"}`.
