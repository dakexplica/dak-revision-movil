# Qué cambió

## 1.0.4
- Más ligera: revisar si hay versión nueva ya no agrega ningún paso (lo hacen los scripts al terminar, máximo una vez al día; si no hay versión nueva, no dice nada).

## 1.0.3
- Más confiable: el aviso de versión nueva sale en cada uso (lo revisan los propios scripts al terminar, no solo la primera vez).
- Las revisiones de imágenes y videos ya no fallan con «falta Pillow» cuando sí está instalado.

## 1.0.2
- El aviso de versión nueva llega al momento: ya no ve la copia de hace unos minutos que guarda GitHub.

## 1.0.1
- Actualizar ahora es un solo paso y más seguro: Claude usa el comando exacto, comprueba que quedó la versión nueva y nunca actualiza encima de la copia original de quien hizo la skill.

## 1.0.0
- Primera versión pública: revisa tu página en 15 dispositivos, la usa con el dedo, arregla lo obvio y te pregunta antes de cambiar tu diseño. Incluye mini guía de ~5 min y aviso silencioso de versiones nuevas.

> Cada vez que subimos una versión, cambian dos cosas: el número en `version.json` y este archivo. La skill avisa de una versión nueva **solo si existe**; si no hay, no dice nada.
