# Registro de Decisiones Técnicas — Proyecto Grupo 2 (MCDI-500)

Este registro documenta de forma ordenada las decisiones técnicas, metodológicas y de arquitectura tomadas desde la Fase 1 hasta la Fase 3. Cada entrada expone el problema observado, la decisión adoptada, su justificación, la fuente o evidencia en el repositorio y su impacto medido.

---

## 1. Declarar `sep=";"` (motor C) y usar `usecols` en lecturas selectivas (`cargar_csv`)

- **Problema:** `cargar_csv()` utilizaba `pd.read_csv(..., sep=None, engine="python")` para inferir el separador, obligando a `pandas` a procesar los ~`57 MB` del archivo línea por línea en Python.
- **Decisión:** Declarar explícitamente `sep=";"` en `cargar_csv()` (`src/preprocesamiento.py`) para activar el motor C de `pandas`, y utilizar `usecols` cuando un análisis solo requiera las columnas analíticas.
- **Justificación:** El delimitador `;` es conocido y estable desde la Fase 1. No existe beneficio al inferirlo en cada corrida.
- **Fuente / Evidencia:** [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`cargar_csv`) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `4.3`, celdas `f3-lectura-code` y `f3-lectura-interpretacion`).
- **Impacto medido:**
  - Estrategia **B** (`sep=";"`, motor C) vs. **A** (`sep=None`, motor Python): tiempo mínimo bajó de **`2.150,390 ms` a `890,905 ms`** (**`2,4×` más rápida**) y memoria pico de **`223,249 MB` a `48,781 MB`** (**`4,6×` menos memoria**) con exactamente el mismo `DataFrame` (`45.741 × 71`).
  - Estrategia **C** (`usecols` sobre `14` columnas) vs. **B**: bajó de **`781,207 ms` a `367,375 ms`** (**`2,1×` más rápida**) y de **`48,779 MB` a `11,037 MB`** (**`4,4×` menos memoria**).

---

## 2. Reglas vectorizadas por columna frente a iteración fila a fila

- **Problema:** Los controles lógicos fila por fila en Python (`itertuples` y listas intermedias) crean objetos Python por cada registro y penalizan tiempo y memoria al evaluar `45.741` ofertas.
- **Decisión:** Escribir los controles temporales y reglas de cálculo mediante operaciones vectorizadas por columna en `pandas`/`numpy` (`control_vectorizado`, `calcular_brecha`), manteniendo `control_iterativo` únicamente como oráculo de verificación en F3.
- **Justificación:** La vectorización mantiene complejidad temporal y espacial $O(n)$ pero ejecuta las comparaciones en código C compilado con un arreglo booleano compacto.
- **Fuente / Evidencia:** [`src/pipeline_licitaciones.py`](../src/pipeline_licitaciones.py) (`control_iterativo`, `control_vectorizado`) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `4.2`, celdas `f3-memoria-code` y `f3-memoria-interpretacion`).
- **Impacto medido:** Sobre `45.741` filas (`7` repeticiones): `control_vectorizado` tardó **`0,447 ms`** con **`0,223 MB`** pico frente a **`153,990 ms`** y **`4,684 MB`** de `control_iterativo` (**`344×` más rápida y `21×` menos memoria**), entregando idéntico resultado (`0` alertas).

---

## 3. División funcional e iteración acotada en vez de recursión (Decisión 0.5)

- **Problema:** Determinar si convenía modelar recorridos de filas o pasos mediante recursión o mediante descomposición funcional e iteración/vectorización.
- **Decisión:** Adoptar **división funcional** (`preprocesamiento.py` + bucle acotado sobre `5` transformadores en `Pipeline`) y operaciones vectorizadas por columna, descartando la recursividad sobre filas.
- **Justificación:** Los datos conforman una tabla plana sin anidamiento jerárquico y Python impone un límite de pila (~`1.000` marcos) incompatible con `45.741` registros. La recursividad se reserva solo para estructuras de profundidad variable (árboles o grafos).
- **Fuente / Evidencia:** [`docs/arquitectura.md`](./arquitectura.md#6-recursividad-o-división-funcional) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `2` y `4.2`).
- **Impacto medido:** Cero desbordamientos de pila (`RecursionError`), flujo lineal en `5` pasos encapsulados y mejora de **`344×`** en velocidad en el control temporal de `45.741` registros.

---

## 4. Estudio descriptivo sobre el conjunto completo (sin partición entrenamiento / prueba)

- **Problema:** Decidir si el flujo analítico debía dividir el dataset en subconjuntos de entrenamiento y prueba.
- **Decisión:** Ejecutar el estudio principal sobre el **universo completo del corte mensual** (`45.741` ofertas y `2.292` licitaciones) sin partición `train/test`, pero diseñar los transformadores con estado (`TratamientoFaltantes`, `ExtremosLogIQR`) con interfaz explícita `ajustar()` / `transformar()`.
- **Justificación:** El objetivo y alcance del proyecto son descriptivos (cuantificar coincidencia y brecha entre monto estimado y ofertas ganadoras), no predictivos ni de *machine learning*. Separar la interfaz en ajuste y aplicación permite reutilizar límites aprendidos sobre datos nuevos sin fuga de información (*data leakage*) si el proyecto se extiende en el futuro.
- **Fuente / Evidencia:** [`F1/F1_Definicion.ipynb`](../F1/F1_Definicion.ipynb) (alcance), [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `2`, `5` y `7`) y [`src/pipeline_licitaciones.py`](../src/pipeline_licitaciones.py).
- **Impacto medido:** Se analizan las `45.741` ofertas del mes; `2.257` de `2.292` licitaciones (`98,5 %`) son comparables y verificación explícita de no-fuga en pruebas unitarias de `ExtremosLogIQR` y `TratamientoFaltantes`.

---

## 5. Excluir `NoClasificado` de la escala ordinal `TamanoProveedorOrdinal`

- **Problema:** La columna `TamanoProveedor` contiene `Micro`, `Pequeña`, `Mediana`, `Grande` y la etiqueta administrativa `NoClasificado` (`5.274` ofertas). Tratar `NoClasificado` como un nivel ordinal distorsionaría cualquier comparación de tendencia por tamaño.
- **Decisión:** Definir `ORDEN_TAMANO = ("Micro", "Pequeña", "Mediana", "Grande")` y mapear `NoClasificado` a `pd.NA` (sin rango ordinal) en `TamanoProveedorOrdinal`, rechazando con `ValueError` cualquier categoría desconocida.
- **Justificación:** `NoClasificado` indica ausencia de clasificación empresarial, no un tamaño menor que `Micro` ni mayor que `Grande`.
- **Fuente / Evidencia:** Commit `b90443d`, [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`ordenar_tamano`, `validar_procesado`) y [`F1/F1_Definicion.ipynb`](../F1/F1_Definicion.ipynb) (Sección `11`).
- **Impacto medido:** Las `40.467` ofertas clasificadas conservan orden estricto (`Micro < Pequeña < Mediana < Grande`) y las `5.274` filas `NoClasificado` quedan explícitamente como faltantes ordinales (`-1` en códigos categóricos), verificado automáticamente en cada corrida por `validar_procesado()`.

---

## 6. Comparación estricta dentro de una misma moneda (sin conversión externa)

- **Problema:** Coexisten `4` monedas (`CLP`, `CLF`, `USD`, `UTM`) y el dataset no incluye el tipo de cambio vigente al día de apertura/cierre de cada proceso.
- **Decisión:** Restringir el cálculo de `BrechaMonto` únicamente a licitaciones donde todas las ofertas ganadoras y el monto estimado compartan exactamente la misma moneda, excluyendo casos mixtos con etiqueta explícita (`"Ganadora con moneda distinta o faltante"`) y reportando cada moneda por separado.
- **Justificación:** Aplicar tipos de cambio promedio o externos sin fecha de referencia exacta introduciría errores artificiales en la brecha calculada.
- **Fuente / Evidencia:** [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`calcular_brecha`), [`F2/F2_Preprocesamiento.ipynb`](../F2/F2_Preprocesamiento.ipynb) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `6`).
- **Impacto medido:** De `2.292` licitaciones, **`2.257` (`98,5 %`)** resultan comparables en igualdad monetaria (`CLP`: `2.230`, `CLF`: `20`, `UTM`: `4`, `USD`: `3`), documentando explícitamente cada exclusión en `EstadoBrecha`.

---

## 7. Filtrado temprano de privacidad (`es_columna_privada`) y exclusión de datos crudos en Git

- **Problema:** El CSV crudo de ChileCompra incluye nombre y RUT de proveedores, los cuales no deben versionarse ni propagarse a archivos derivados en el repositorio público.
- **Decisión:** Excluir identificadores directos al momento de leer en `cargar_csv()` mediante `es_columna_privada()`, exportar en `04LicitacionesEne_procesado.csv` únicamente una lista autorizada de `17` columnas (`MOTIVOS` + `3` derivadas) y bloquear `data/raw/*.csv` y `data/raw/*.zip` en `.gitignore`.
- **Justificación:** Minimiza exposición de datos personales desde la entrada en memoria y asegura cumplimiento de buenas prácticas de privacidad y límites de GitHub (`< 100 MB`).
- **Fuente / Evidencia:** Commit `47d4589`, [`.gitignore`](../.gitignore), [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`es_columna_privada`, `validar_procesado`) y [`data/processed/README.md`](../data/processed/README.md).
- **Impacto medido:** Reducción inmediata de `72` columnas crudas a `71` en memoria (retirando el campo privado al leer) y a **`17` columnas** en el CSV procesado (`~7,0 MB` frente a `56,8 MB` del crudo), con `0` datos personales en `data/processed/`.

---

## 8. Detección de extremos mediante IQR sobre logaritmo natural en CLP positivos

- **Problema:** Los montos ofertados en compras públicas abarcan desde adquisiciones menores (`< 100 UTM`) hasta grandes obras (`> 1.000 UTM`), generando fuerte asimetría positiva donde el IQR lineal marca un exceso de falsos extremos superiores y arroja límites inferiores negativos sin sentido físico.
- **Decisión:** Calcular cuartiles y rango intercuartílico ($1,5 \times \text{IQR}$) sobre $\ln(\text{MontoTotalOferta})$ restringido exclusivamente a ofertas en `CLP` con monto estrictamente positivo (`ofertas_clp_validas()`), dejando en `pd.NA` las ofertas en otras monedas o con montos `<= 0` y sin eliminar registros automáticamente.
- **Justificación:** La transformación logarítmica estabiliza la escala multiplicativa de los montos en pesos chilenos y acota la detección a valores proporcionalmente extremos sin mezclar monedas.
- **Fuente / Evidencia:** [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`calcular_limites_iqr`, `aplicar_bandera_atipicos`), [`data/processed/parametros_f3.csv`](../data/processed/parametros_f3.csv) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `6`).
- **Impacto medido:** Sobre `45.603` ofertas CLP positivas evaluadas (`Q1_log = 10,6832`, `Q3_log = 14,4043`, límites `[5,1015 ; 19,9860]`), identifica **`887` ofertas extremas** (`44.716` normales y `138` `<NA>` sin evaluar), conservando `45.741` filas íntegras.

---

## 9. Jerarquía POO unificada (`Transformador`, `TratamientoFaltantes`, `ExtremosLogIQR`) y patrón Observer

- **Problema:** Inicialmente la clase base `Transformador` solo declaraba el método `transformar()`, `ExtremosLogIQR` se ejecutaba fuera de la lista de pasos de `Pipeline` como caso especial y los faltantes eran una regla fija sin ajuste; además, la trazabilidad de ejecución requería evitar duplicación y no acoplarse a `print()`.
- **Decisión:**
  1. Concentrar en `Transformador(ABC)` el control de `_ajustado`, la validación de `columnas_requeridas` y la copia defensiva (`datos.copy()`).
  2. Convertir los faltantes en `TratamientoFaltantes(Transformador)` (aprende qué columnas superan el `90 %` de faltantes en `ajustar()` y las excluye en `transformar()`, sin excluir nunca las variables del análisis de `MOTIVOS`).
  3. Integrar `ExtremosLogIQR` y `TratamientoFaltantes` en la lista única `pasos` para que `Pipeline.ejecutar()` ejecute polimórficamente `paso.ajustar(datos)` y `paso.transformar(datos)` sobre todos los pasos.
  4. Mantener el patrón Observer (`Pipeline.suscribir` + `Bitacora`).
- **Justificación:** Elimina código repetido en subclases, materializa herencia, polimorfismo y encapsulamiento reales (Rúbrica III.a / comentario Sumativa 1) y desacopla la auditoría de conteos.
- **Fuente / Evidencia:** Commit `23f3a5a`, [`src/pipeline_licitaciones.py`](../src/pipeline_licitaciones.py) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `2`, `3` y `7`).
- **Impacto medido:** `100 %` de clases y métodos públicos con docstring, **`17/17` pruebas aprobadas** en `ejecutar_pruebas_pipeline()` (`5` normales, `8` límite, `4` de excepción), `9` eventos uniformes en `Bitacora` y equivalencia exacta (`check_exact=True`) con F2 (`45.741 × 17` en `ofertas` y `2.292 × 24` en `licitaciones`).

---

## 10. Separación modular en `src/` por responsabilidad y validación automatizada

- **Problema:** Mantener funciones de F1 (`utilidades`), reglas de F2 (`preprocesamiento`), orquestación POO (`pipeline_licitaciones`) y medición (`medicion`) mezcladas en un único archivo dificultaba la comprensión, el trabajo en paralelo y la verificación por capas.
- **Decisión:** Separar cada responsabilidad en su propio módulo dentro de `src/` y acompañar tanto las reglas puras (`pruebas_preprocesamiento.py`) como el flujo POO (`ejecutar_pruebas_pipeline()`) con baterías automatizadas sobre datos ficticios antes de procesar el archivo real.
- **Justificación:** Favorece alta cohesión, bajo acoplamiento y detección temprana de regresiones ante cambios de esquema o código.
- **Fuente / Evidencia:** Commit `f1640ea`, [`src/README.md`](../src/README.md), [`src/pruebas_preprocesamiento.py`](../src/pruebas_preprocesamiento.py) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `1`, `4.1` y `7`).
- **Impacto medido:** Ningún duplicado funcional entre F1, F2 y F3; las pruebas unitarias e integrales se ejecutan en cada corrida completa de `F3_Nucleo_Algoritmico.ipynb` con resultado `ok` en todas las celdas.
