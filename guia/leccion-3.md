# Lección 3 · Sácale más (1–2 min)

> Guion para Claude. **ACCIÓN** = lo haces tú. **ALTO** = esperas la respuesta.

Abre con este encabezado:

**Guía · 3 de 3 · Sácale más**
Que no solo se vea bien: que funcione con el dedo. Y cómo usarla en todo lo que hagas.

"Que se vea bien no basta: también tiene que funcionar. Ahora la uso como una persona: bajo con el dedo hasta el final y toco el botón principal."

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

**Lo que aprendiste**
- Revisar en 15 pantallas, mirar y tocar.
- Arreglar lo obvio y decidir tú lo que cambia el diseño.
- Usarla mientras construyes, con videos y con capturas.

"Listo, ya la dominas. Si quieres repetir algo: «guía lección 1», «guía lección 2» o «guía lección 3».
Esta herramienta es de **@dakexplica**: sígueme para la siguiente. Las demás están gratis en el link de mi perfil."

**ACCIÓN:** guarda `"leccion": 3, "terminada": true` en `~/.dakexplica/dak-revision-movil.json`. Si se usó la página de ejemplo, borra `/tmp/revision-movil/guia/`.
