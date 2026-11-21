# Changelog

Las fechas de los commits corresponden al campo de autor de Git (`%as`). Las referencias a PR se verificaron en el historial local o en la API de GitHub. Cada enlace apunta al PR correspondiente en el repositorio de origen.

## F1 — Definición y validación del conjunto de datos

| Fecha | Commit | Cambio | Justificación técnica |
|---|---|---|---|
| 2026-11-03 | `37f5d2b` | Incorpora el validador del conjunto de datos. | Comprueba que la fuente cumple los requisitos de tamaño, completitud y variables del proyecto antes de usarla. |
| 2026-11-05 | `c5d65c5` | Crea el cuaderno de definición de F1. [PR #17](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/17) | Vincula la selección del conjunto de datos con el problema y el alcance del análisis. |
| 2026-11-06 | `8d5ca24`, `8c5b783` | Añade pruebas de módulo, ficha del conjunto y verificación del entorno. [PR #23](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/23) · [PR #26](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/26) | Permite reproducir la selección y validar las utilidades y dependencias antes de ejecutar el análisis. |
| 2026-11-15 | `b90443d` | Retira `NoClasificado` de la escala ordinal. | Evita asignar posición en la escala Micro–Grande a proveedores de tamaño desconocido. |
| 2026-11-16 | `c32fb30` | Alinea el problema, los objetivos, las preguntas y las restricciones de F1 y F2. [PR #30](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/30) | Fija las comparaciones que deben responder las fases posteriores y sus condiciones de interpretación. |

## F2 — Preprocesamiento

| Fecha | Commit | Cambio | Justificación técnica |
|---|---|---|---|
| 2026-11-04 | `7c46ba3` | Incorpora el primer avance de preprocesamiento. | Registra la transformación de los datos de entrada en un flujo reproducible. |
| 2026-11-11 | `47d4589` | Retira los CSV con RUT y documenta cómo obtener la fuente. [PR #28](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/28) | Reduce la exposición de identificadores directos y conserva una vía para reproducir el análisis localmente. |
| 2026-11-16 | `19d2a0b` | Integra la revisión de fechas, monedas, categorías y validaciones. [PR #29](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/29) | Centraliza las reglas que permiten comparar sumas ganadoras y montos estimados a nivel de licitación. |
| 2026-11-16 | `0c2298b`, `f1640ea` | Versiona las salidas procesadas compartidas y reorganiza los módulos por responsabilidad. [PR #31](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/31) · [PR #32](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/32) | Permite que F3 contraste resultados con una referencia común e impide que las reglas diverjan entre cuadernos. |
| 2026-11-17 | `51bf258` | Documenta la justificación de las transformaciones y la verificación de las salidas. [PR #42](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/42) | Hace trazables los criterios de limpieza y facilita verificar los archivos generados. |

## F3 — Núcleo algorítmico

| Fecha | Commit | Cambio | Justificación técnica |
|---|---|---|---|
| 2026-11-10 | `94fea53` | Introduce `src/medicion.py` para medir tiempo y memoria. [PR #27](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/27) | Separa el cronometraje de la instrumentación de memoria y verifica equivalencia antes de comparar. |
| 2026-11-16 | `23f3a5a`, `9a6397c` | Implementa transformadores con herencia y estado y registra la arquitectura y las decisiones. [PR #39](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/39) · [PR #40](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/40) | Unifica el contrato de ajuste y transformación para reglas fijas y parámetros aprendidos. |
| 2026-11-16 | `4a097cf`, `32d3f26` | Integra el pipeline en el notebook y actualiza sus cuatro artefactos procesados. [PR #41](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/41) | Conecta las reglas reutilizables con la ejecución reproducible y el contrato de datos consumido en F4. |
| 2026-11-17 | `76c8fa5`, `7316e46` | Añade pruebas del pipeline, evidencia de Observer y comparación con recursividad. [PR #43](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/43) · [PR #44](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/44) | Cubre casos normales, límite y de excepción, registra el paso de las filas por el pipeline y muestra el límite de pila en datos planos. |
| 2026-11-17 | `669b2d0`, `2f19968` | Preserva variables analíticas durante el tratamiento de faltantes y actualiza la ejecución de cierre. [PR #48](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/48) · [PR #49](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/49) | Protege las columnas necesarias para las comparaciones y documenta las cifras de referencia. |
| 2026-11-21 | `8a4fedb` | Etapa 2, tarea 1.7. Mide el control temporal con 1.000, 5.000, 20.000 y 45.741 filas. | Comprueba equivalencia exacta y mide cómo cambia la ventaja al crecer el volumen. |

## F4 — Visualización y comunicación

| Fecha | Commit | Cambio | Justificación técnica |
|---|---|---|---|
| 2026-11-21 | `0e8389b`, `a8b95f8` | Incorpora el módulo de comunicación, la carga selectiva y el notebook de F4. [PR #50](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/50) · [PR #51](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/51) | Reutiliza los artefactos procesados y limita la lectura a las columnas que necesita la comunicación. |
| 2026-11-21 | `7da9fdf` | Añade controles de entorno, esquema y contraste con la fuente, y la copia para graficar. [PR #52](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/52) | Verifica la correspondencia entre ofertas y licitaciones antes de construir indicadores. |
| 2026-11-21 | `efc510b`, `17e7916` | Añade las tres figuras, el control por monto, el registro de hallazgos y las dependencias fijadas. [PR #53](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/53) · [PR #54](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/54) | Vincula cada figura a su objetivo y deja trazables las cifras y el entorno que las produce. |
| 2026-11-21 | `eaead01` | Etapa 2, tareas 2.2 y 2.3. Amplía OE2 y OE3 con el escenario IVA, las tasas con Wilson, las pruebas, la estratificación y la sensibilidad a duplicados. [PR #57](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/pull/57), integrado en `main` el 2026-11-21 con el commit de merge `7bb0e2d`. | Separa 22 copias adicionales de las 44 filas marcadas y cuantifica qué resultados dependen de cada supuesto. |
| 2026-11-21 | `8a4fedb` | Etapa 2, tareas 1.7 y 1.8. Mide la asignación del tamaño ganador y documenta el historial de F1 a F4. | Contrasta el recorrido por filas con el agrupamiento de pandas sobre las mismas ofertas y deja trazabilidad de los cambios. |
| 2026-11-21 | `8a4fedb` | Corrección adicional. Retira los tres diagramas de caja de sensibilidad de la sección 8.2. | Recupera las tres figuras originales de F4 y conserva las tablas y pruebas estadísticas de sensibilidad. |
