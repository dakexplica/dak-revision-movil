# Revisión en 15 pantallas · dak-revision-movil

Una skill de Claude que abre tu página en **15 dispositivos a la vez** (7 celulares, 4 tabletas y 4 compus), la usa como una persona (toca, desliza, abre el teclado, gira), te marca todo lo que se ve mal o no funciona con el dedo, **arregla lo obvio y te pregunta antes de cambiar tu diseño**.

Incluye una **mini guía interactiva** de unos 5 minutos (3 pasos) que te acompaña mientras revisas tu primera página.

Hecha por [@dakexplica](https://www.tiktok.com/@dakexplica) · Gratis.

## Lo que necesitas
- **Claude Code** (o la app de Claude con skills).
- **Python 3.9 o más nuevo.**
- Playwright y su navegador Chromium, y Pillow. No te preocupes: la skill revisa si los tienes y, **con tu permiso**, instala lo que falte.
- Opcional: **ffmpeg** (para revisar videos) y **Xcode** en Mac (para probar en el Safari real de iPhone y iPad).

## Instálala

**Con Claude Code**, pega esto:

```
Instala la skill dakexplica/dak-revision-movil con `npx skills add dakexplica/dak-revision-movil`, revisa con su Paso 0 si me falta algo (pídeme permiso antes de instalar) y cuando esté lista, pregúntame si quiero la guía.
```

O el comando directo:

```bash
npx skills add dakexplica/dak-revision-movil
```

**En la app de Claude:** descarga el `.zip` de la última versión (Releases, a la derecha) y súbelo en **Configuración → Capacidades → Skills → Subir skill**.

## Actualizaciones
Esta skill **no se actualiza sola**, pero te avisa. Cuando empiezas a usarla, mira (en silencio, máximo una vez al día) si hay una versión nueva en este repositorio. **Si no la hay, no dice nada.** Si la hay, al final de lo que le pediste te avisa en una línea y te pregunta si la actualiza; si dices «ahora no», no vuelve a mencionar esa versión. Nunca descarga nada sin tu permiso. Lo que cambia en cada versión está en [CHANGELOG.md](CHANGELOG.md).

También puedes actualizarla tú cuando quieras: vuelve a correr `npx skills add dakexplica/dak-revision-movil`, o descarga el `.zip` más reciente en **Releases**.

## Comprueba que funciona

```
Usando la skill dak-revision-movil, revisa la página de ejemplo de la skill en los 15 dispositivos.
```

Debes ver una hoja con tu página en 15 pantallas, los problemas marcados en rojo y un resumen de qué se ve mal y dónde.

## Lo que te entrega
- `hoja.png`: tu página en las 15 pantallas, lado a lado.
- Capturas de cada dispositivo con los problemas numerados.
- Un informe en español: qué se ve mal, en qué aparatos y cómo arreglarlo.
- Los arreglos hechos en tu código (lo obvio) y la pregunta para lo que cambia tu diseño.
- Un antes y después.

## Qué es gratis y qué cuesta
La skill es gratis. Corre en tu compu con herramientas gratis (Python, Playwright). Usa tu plan de Claude como cualquier otra conversación.

## ¿Algo falla?
- **"Falta Playwright" o "no se abre el navegador":** dile a Claude «corre el Paso 0» y acepta instalar lo que falta.
- **Mi página tiene login:** dile «la página tiene login»; se abre una ventana para que entres tú (Claude nunca escribe tu contraseña).
- **La revisión tarda:** la completa tarda 1–2 min (con 3D, 3–4). Para ir rápido mientras arreglas: «revísala solo en los rápidos».
- **Quiero la guía otra vez:** «ábreme la guía».

## Licencia
MIT.
