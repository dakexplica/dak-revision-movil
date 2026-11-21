# Lección 3 · Sácale más (1–2 min)

> Guion para Claude. Antes, lee `guia/estilo.md`. Retoma nombre y página de `~/.dakexplica/dak-revision-movil.json`. **ACCIÓN** = lo haces tú. **ALTO** = esperas la respuesta.

**ACCIÓN:** muestra este banner en un bloque de código:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   REVISIÓN EN 15 PANTALLAS  ·  guía 3 de 3
   Que funcione con el dedo (y usarla en todo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

"Última, [nombre], y es la que más me gusta."

"Que se vea bien no basta: también tiene que funcionar con el dedo. Ahí es donde la mayoría de las páginas falla sin que nadie se dé cuenta."

"Escríbeme: **«Úsala como una persona: baja hasta el final y toca el botón principal»**." **ALTO.**

**ACCIÓN:** escribe un `pasos.json` corto para su página (o la de ejemplo) y córrelo en el grupo rápido:

```json
[{"recorrer": true}, {"tocar_texto": "<el botón principal, p. ej. Pedir en línea ahora>"}, {"rotar": true}]
```

```bash
python3 <skill>/scripts/tocar.py <la página> --pasos pasos.json --dispositivos rapido --salida /tmp/revision-movil/guia/tocar
```

Cuéntale el resultado en una frase por dispositivo (✓ o qué falló y por qué: "tapado por el banner", "el scroll se atora").

"Tres usos que vale la pena conocer:"
1. **Mientras construyes:** dile a Claude «antes de terminar, revísalo con dak-revision-movil». Así lo descubre él y no tus clientes.
2. **Videos e imágenes:** «revisa este video para Reels» revisa formato 9:16, zonas que tapa la app, peso para WhatsApp y web.
3. **Una pantalla concreta:** si en tu celular algo se ve raro, mándale la captura y dile «arréglalo»: lo reproduce en ese mismo aparato.

"Errores comunes, para que no te pasen:"
- Revisar solo la portada: revisa también producto, carrito o formulario (se pide así: «revisa también /contacto»).
- Creerle solo a los números: la skill mira las capturas porque hay cosas que solo se ven mirando.
- Publicar sin volver a revisar en el link real: después de subir, pide «revísalo en el link de producción».

**Mejoras opcionales** (la skill funciona sin ellas; pregunta antes de instalar nada):
- **Safari de verdad (solo Mac con Xcode):** prueba en el iPhone y iPad del Simulador, con el Safari real. «Pruébalo en Safari real.»
- **ffmpeg:** para revisar videos. Si no lo tiene, dale el comando de su sistema (macOS `brew install ffmpeg` · Windows `winget install ffmpeg`).

Cierra con:

**Lo que lograste, [nombre]**
- Revisar en 15 pantallas, mirar y tocar.
- Arreglar lo obvio y decidir tú lo que cambia el diseño.
- Usarla mientras construyes, con videos y con capturas.

Despídete con cariño y energía, retomando lo de la lección 1 ("Tu [tienda] ya se ve bien en los 15, y ahora sabes revisarla tú cuando cambies algo").

"Listo, ya la dominas. Si quieres repetir algo: «guía lección 1», «guía lección 2» o «guía lección 3».
Esta herramienta es de **@dakexplica**: sígueme para la siguiente. Las demás están gratis en el link de mi perfil."

**ACCIÓN:** guarda `"leccion": 3, "terminada": true` en `~/.dakexplica/dak-revision-movil.json`. Si se usó la página de ejemplo, borra `/tmp/revision-movil/guia/`.
