# Registro de Decisiones Técnicas — Proyecto Grupo 2 (MCDI-500)

Este registro documenta de forma ordenada las decisiones técnicas, metodológicas y de arquitectura tomadas desde la Fase 1 hasta la Fase 4. Cada entrada expone el problema observado, la decisión adoptada, su justificación, la fuente o evidencia en el repositorio y su impacto medido.

---

## 1. Declarar `sep=";"` (motor C) y usar `usecols` en lecturas selectivas (`cargar_csv`)

- **Problema:** `cargar_csv()` utilizaba `pd.read_csv(..., sep=None, engine="python")` para inferir el separador, obligando a `pandas` a procesar los ~`57 MB` del archivo línea por línea en Python.
- **Decisión:** Declarar explícitamente `sep=";"` en `cargar_csv()` (`src/preprocesamiento.py`) para activar el motor C de `pandas`, y utilizar `usecols` cuando un análisis solo requiera las columnas analíticas.
- **Justificación:** El delimitador `;` es conocido y estable desde la Fase 1. No existe beneficio al inferirlo en cada corrida.
- **Fuente / Evidencia:** [`src/preprocesamiento.py`](../src/preprocesamiento.py) (`cargar_csv`) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `4.3`, celdas `f3-lectura-code` y `f3-lectura-interpretacion`).
- **Impacto medido:**
  - Estrategia **B** (`sep=";"`, motor C) vs. **A** (`sep=None`, motor Python): tiempo mínimo bajó de **`1.269,643 ms` a `301,425 ms`** (**`4,2×` más rápida**) y memoria pico de **`223,130 MB` a `48,654 MB`** (**`4,6×` menos memoria**) con exactamente el mismo `DataFrame` (`45.741 × 71`).
  - Estrategia **C** (`usecols` sobre `14` columnas) vs. **B**: bajó de **`294,177 ms` a `127,483 ms`** (**`2,3×` más rápida**) y de **`48,654 MB` a `10,915 MB`** (**`4,5×` menos memoria**).

---

## 2. Reglas vectorizadas por columna frente a iteración fila a fila

- **Problema:** Los controles lógicos fila por fila en Python (`itertuples` y listas intermedias) crean objetos Python por cada registro y penalizan tiempo y memoria al evaluar `45.741` ofertas.
- **Decisión:** Escribir los controles temporales y reglas de cálculo mediante operaciones vectorizadas por columna en `pandas`/`numpy` (`control_vectorizado`, `calcular_brecha`), manteniendo `control_iterativo` únicamente como oráculo de verificación en F3.
- **Justificación:** La vectorización mantiene complejidad temporal y espacial $O(n)$ pero ejecuta las comparaciones en código C compilado con un arreglo booleano compacto.
- **Fuente / Evidencia:** [`src/pipeline_licitaciones.py`](../src/pipeline_licitaciones.py) (`control_iterativo`, `control_vectorizado`) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Sección `4.2`, celdas `f3-memoria-code` y `f3-memoria-interpretacion`).
- **Impacto medido:** Sobre `45.741` filas (`7` repeticiones): `control_vectorizado` tardó **`0,144 ms`** con **`0,224 MB`** pico frente a **`80,395 ms`** y **`4,003 MB`** de `control_iterativo` (**`559×` más rápida y `18×` menos memoria**), entregando idéntico resultado (`0` alertas).

---

## 3. División funcional e iteración acotada en vez de recursión (Decisión 0.5)

- **Problema:** Determinar si convenía modelar recorridos de filas o pasos mediante recursión o mediante descomposición funcional e iteración/vectorización.
- **Decisión:** Adoptar **división funcional** (`preprocesamiento.py` + bucle acotado sobre `5` transformadores en `Pipeline`) y operaciones vectorizadas por columna, descartando la recursividad sobre filas.
- **Justificación:** Los datos conforman una tabla plana sin anidamiento jerárquico y Python impone un límite de pila (~`1.000` marcos) incompatible con `45.741` registros. La recursividad se reserva solo para estructuras de profundidad variable (árboles o grafos).
- **Fuente / Evidencia:** [`docs/arquitectura.md`](./arquitectura.md#6-recursividad-o-división-funcional) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `2` y `4.2`).
- **Impacto medido:** Cero desbordamientos de pila (`RecursionError`), flujo lineal en `5` pasos encapsulados y mejora de **`559×`** en velocidad en el control temporal de `45.741` registros; con `900` filas, la suma recursiva fue `11×` más lenta que la vectorizada.

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
- **Fuente / Evidencia:** Commit `f1640ea`, [`src/README.md`](../src/README.md), [`src/pruebas_preprocesamiento.py`](https://github.com/proyecto-grupo2-mcdi500/proyecto-grupo2-mcdi500/blob/f1640eab066a276914d153d9c33db5d11e6177a6/src/pruebas_preprocesamiento.py) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (Secciones `1`, `4.1` y `7`).
- **Impacto medido:** Ningún duplicado funcional entre F1, F2 y F3; las pruebas unitarias e integrales se ejecutan en cada corrida completa de `F3_Nucleo_Algoritmico.ipynb` con resultado `ok` en todas las celdas.

---

## 11. Copia interpretable para graficar en F4 sin revertir escalamiento ni codificación

- **Problema:** Al diseñar la Fase 4 suele ser necesario mantener una matriz transformada para cálculo y construir una copia interpretable con unidades y etiquetas originales antes de graficar (`Apunte F4`). Sin embargo, aplicar funciones inversas artificiales cuando no hubo escalamiento ni codificación entera agrega complejidad innecesaria.
- **Decisión:** No implementar `revertir_escalamiento()` ni `reconstruir_categorias()` en [`src/comunicacion.py`](../src/comunicacion.py). En la Sección `4` de [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb), construir `copia_graficar` directamente sobre las salidas de `preparar_comparables()` y `asignar_tamano_ganador()`, añadiendo únicamente `EtiquetaCoincidencia` (`Coincide` / `Difiere`), `TramoEstimado` (cuatro rangos legibles en `CLP` más `"Otra moneda (no CLP)"`) y `BrechaRelativaPct` (`(BrechaMonto / MontoEstimadoLicitacion) * 100`), manteniendo `NoClasificado` y `Múltiple` fuera del eje ordinal `TamanoGanadorOrdinal`.
- **Justificación:** Las fases `F2` y `F3` conservaron los montos en su unidad monetaria original y las etiquetas en texto (`Micro < Pequeña < Mediana < Grande`). Dejar `NoClasificado` (`284`) y `Múltiple` (`240`) fuera del eje ordinal evita introducir un orden ficticio en las tendencias por tamaño sin ocultar esas `524` licitaciones.
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py), [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Sección `4`) y [`docs/metadatos_f4.json`](./metadatos_f4.json).
- **Impacto medido:** Copia `copia_graficar` verificada de **`2.257 × 19`** (`Hasta 1 M CLP`: `350`, `1 a 10 M CLP`: `739`, `10 a 50 M CLP`: `783`, `Más de 50 M CLP`: `358`, `Otra moneda (no CLP)`: `27`) con `100 %` de registros `NoClasificado` y `Múltiple` preservados como `NA` en `TamanoGanadorOrdinal`.

---

## 12. Lectura selectiva (`usecols`), contrato contra `diccionario_f3.csv` y verificación contra `data/raw`

- **Problema:** Cargar todas las columnas de los CSV procesados sin validar contrato ni contrastar contra la fuente original expone la Fase 4 a rupturas silenciosas de esquema, tipos ambiguos en `pandas` (`object` en booleanos con faltantes) o errores de arrastre.
- **Decisión:** Implementar `cargar_artefactos()` en [`src/comunicacion.py`](../src/comunicacion.py) con `sep=";"` y `usecols` en los cuatro archivos (`9` de `17` columnas en `ofertas`, `8` de `24` en `licitaciones`, `3` en `diccionario` y `2` en `parametros`), tipar columnas booleanas con `<NA>` como `boolean`, exigir contrato mediante `assert` frente a [`diccionario_f3.csv`](../data/processed/diccionario_f3.csv) y [`parametros_f3.csv`](../data/processed/parametros_f3.csv), y ejecutar en la Sección `3` de F4 una verificación muestral independiente recalculada directamente desde `data/raw/04LicitacionesEne.csv` (con validación SHA-256 LF automática cuando está disponible localmente).
- **Justificación:** Garantiza consistencia estricta entre entrada, procesamiento y salida antes de graficar, reduciendo además el uso de memoria conforme a la medición `4.3` de F3.
- **Fuente / Evidencia:** [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Secciones `2`, `3` y `5`) y [`docs/metadatos_f4.json`](./metadatos_f4.json).
- **Impacto medido:** Contrato aprobado sobre las **`41` columnas** del diccionario (`45.741` ofertas, `2.292` licitaciones únicas, `45.603` ofertas CLP válidas) y diferencia máxima absoluta de **`0,0`** frente a `data/raw` en la muestra de `7` licitaciones comparables (`1` a `114` ítems ganadores en `CLP`, `CLF` y `USD`).

---

## 13. Métricas adimensionales (`RazonMonto`, `LogRazonMonto`), medianas/IQR e intervalos de Wilson en F4

- **Problema:** Los montos entre monedas distintas no son conmensurables en una sola unidad y dentro de cada moneda las distribuciones de brecha presentan asimetría y valores extremos que distorsionan medias aritméticas o porcentajes puntuales sin tamaño muestral.
- **Decisión:** Incorporar en [`src/comunicacion.py`](../src/comunicacion.py) la razón multiplicativa (`RazonMonto`), su logaritmo natural (`LogRazonMonto`) y `BrechaRelativaPct`, resumir magnitudes con **mediana y rango intercuartílico (`IQR`)** sin mezclar monedas, y reportar tasas de coincidencia con **intervalos de confianza de Wilson al `95 %`** (`intervalo_wilson`, `tasa_por_grupo`).
- **Justificación:** La razón y la log-razón permiten comparar proporcionalmente desviaciones relativas, la mediana e `IQR` resisten valores extremos y el intervalo de Wilson evita intervalos fuera de `[0 %, 100 %]` en grupos con tamaño muestral pequeño (como `CLF`, `UTM` o `USD`).
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py) (`preparar_comparables`, `intervalo_wilson`, `tasa_por_grupo`, `resumen_sentido_por_moneda`, `resumen_magnitud_por_moneda`, `tabla_resumen_por_tamano`) y [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Sección `4.1`).
- **Impacto medido:** Trazabilidad explícita de cada objetivo e indicador (`P1` y `P2` de `F1`) antes del graficado, con cobertura completa de las `2.257` licitaciones comparables (`CLP`: `2.230`, `CLF`: `20`, `UTM`: `4`, `USD`: `3`).

---

## 14. Tratamiento del IVA (`1/1,19`) como análisis de sensibilidad condicional sin modificar la base registrada

- **Problema:** El [diccionario del proyecto](./README.md) describe `MontoTotalOferta` como total neto de la línea y `MontoEstimadoLicitacion` como presupuesto total sin una etiqueta tributaria por registro. En la Figura 2 aparece un agrupamiento nítido en torno a `RazonMonto = 1/1,19 ≈ 0,840` (`234` licitaciones en `[0,835; 0,845]`, `228` de ellas en `CLP`). Ajustar de oficio los montos principales impondría un supuesto tributario no verificado en la fuente original.
- **Decisión:** Conservar los montos registrados como base oficial en F2, F3 y F4 y evaluar la hipótesis de IVA mediante una función separada de sensibilidad (`sensibilidad_iva()` en [`src/comunicacion.py`](../src/comunicacion.py), Sección `8.1` de F4). El escenario ajustado multiplica `MontoTotalGanadoras` por `1,19` únicamente en `CLP` dentro de la ventana `[0,835; 0,845]` cuando `|MontoTotalGanadoras × 1,19 − MontoEstimadoLicitacion| <= 1` peso, contrastando además la concentración frente a las bandas inmediatas (`[0,825; 0,835)` y `(0,845; 0,855]`) y la tolerancia estricta `|razón − 1/1,19| <= 0,0001`.
- **Justificación:** Evita alterar los registros originales con una regla inferida, restringe la reclasificación solo a casos compatibles con redondeo exacto a un peso chileno y comprueba empíricamente si el agrupamiento es un pico estrecho atribuible a diferencias de base tributaria.
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py) (`sensibilidad_iva`), [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Secciones `5.2`, `8.1` y `8.3`, celdas `d796d7a0` y `fe22a4ee`) y [`docs/hallazgos_f4.csv`](./hallazgos_f4.csv).
- **Impacto medido:** En `CLP` (`n = 2.230`), `219` de los `228` casos de la ventana caen dentro de `±0,0001` alrededor de `1/1,19` frente a apenas `2` y `1` casos en las bandas vecinas; el escenario ajusta **`213` licitaciones `CLP`**, elevando la tasa de coincidencia en `CLP` de **`56,14 %` (`1.252/2.230`) a `65,70 %` (`1.465/2.230`)** y reduciendo el grupo bajo el estimado de `23,32 %` (`520`) a `13,77 %` (`307`).

---

## 15. Pruebas estadísticas elegidas (`intervalo_wilson`, Chi-cuadrado `4 × 2` y correlación de Spearman)

- **Problema:** Los grupos por moneda y tamaño presentan denominadores muy desiguales (`CLF` `n=20`, `UTM` `n=4`, `USD` `n=3`) y la variable `BrechaRelativaPct` exhibe fuerte asimetría, empates masivos en `0 %` y valores extremos por estimados simbólicos, incumpliendo los supuestos de normalidad y homocedasticidad de pruebas paramétricas.
- **Decisión:** Estandarizar en [`src/comunicacion.py`](../src/comunicacion.py) tres métodos complementarios: (1) intervalos de confianza binomiales de **Wilson al `95 %`** (`intervalo_wilson`, `z = 1,96`); (2) prueba **Chi-cuadrado de Pearson `4 × 2`** sin corrección de continuidad (`chi2_contingency(..., correction=False)`) sobre `TamanoGanadorOrdinal × CoincideConEstimado`, exigiendo frecuencia esperada mínima `>= 5` (`pruebas_por_tamano`); y (3) **correlación de rangos de Spearman bilateral (`spearmanr`)** entre el código ordinal del tamaño ganador y `BrechaRelativaPct` incluyendo los extremos, reportando ambos contrastes como exploratorios dada la posible recurrencia de organismos o proveedores. Se complementan además con escenarios de sensibilidad frente a `EsDuplicadoPotencial` (`comparar_muestras_feedback`).
- **Justificación:** El método de Wilson garantiza cotas válidas dentro de `[0 %, 100 %]` en muestras pequeñas; Chi-cuadrado contrasta independencia de proporciones sobre los `4` niveles ordinales (`gl = 3`); y Spearman evalúa asociación monótona mediante rangos sin verse distorsionada por valores extremos.
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py) (`intervalo_wilson`, `tasa_por_grupo`, `pruebas_por_tamano`, `comparar_muestras_feedback`) y [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Secciones `5.1`, `8.2` y `8.3`, celdas `326503cf`, `6aea47c6` y `fe22a4ee`).
- **Impacto medido:** Sobre las **`1.733` licitaciones** con tamaño ordinal clasificado: Chi-cuadrado arroja **`χ² = 40,34` (`p = 9,03 × 10⁻⁹`)** con frecuencia esperada mínima de **`106,33`** (`>= 5`), confirmando asociación fuerte entre tamaño y tasa de coincidencia; Spearman obtiene **`ρ = +0,021` (`p = 0,380`)** entre los cuatro tamaños individuales, coherente con mediana `0 %` en los cuatro grupos y cambios focalizados en los cuartiles extremos (`Q1 = -16,0 %` en `Pequeña`/`Mediana` y `Q3 = +4,2 %` en `Grande`). Al retirar copias/filas duplicadas (`22`/`44`), los resultados (`p = 9,03 × 10⁻⁹`, `ρ = +0,021`) se mantienen invariantes.

---

## 16. Control de variable de confusión por tramos fijos de monto estimado (`TramoEstimado` en `CLP`)

- **Problema:** La caída continua de la tasa de coincidencia desde `Micro` (`71,1 %`) hasta `Grande` (`49,0 %`) podría explicarse por una variable de confusión: las empresas grandes tienden a adjudicar licitaciones de mayor monto, donde coincidir exactamente con el presupuesto estimado podría ser menos frecuente.
- **Decisión:** Estratificar las licitaciones comparables en `CLP` con tamaño ordinal clasificado (`n = 1.710`) dentro de cuatro tramos fijos de `MontoEstimadoLicitacion` definidos en `construir_copia_graficar()` y `ORDEN_TRAMOS_ESTIMADO` (`"Hasta 1 M CLP"`, `"1 a 10 M CLP"`, `"10 a 50 M CLP"`, `"Más de 50 M CLP"`, con límite superior incluido en cada tramo; separando las `27` no-CLP en `"Otra moneda (no CLP)"`), y calcular tasas de coincidencia, IC de Wilson y mediana de `BrechaRelativaPct` por celda mediante `tabla_control_confusion()`.
- **Justificación:** Usar cortes monetarios fijos del dominio en `CLP` evita mezclar monedas, no depende de parámetros aprendidos de los datos (por lo que no requiere un `Transformador` ajustable) y permite contrastar si la brecha `Micro − Grande` se mantiene a nivel de presupuesto comparable (reconociendo posible confusión residual dentro de cada tramo).
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py) (`ORDEN_TRAMOS_ESTIMADO`, `construir_copia_graficar`, `tabla_control_confusion`), [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Secciones `4`, `6` y `8.2`, celdas `f4-6-code`, `f4-6-resumen` y `6aea47c6`), [`docs/hallazgos_f4.csv`](./hallazgos_f4.csv) y [`docs/metadatos_f4.json`](./metadatos_f4.json).
- **Impacto medido:** La mayor tasa de coincidencia de `Micro` frente a `Grande` **persiste en los cuatro tramos** (`n = 1.710`): **`+41,52 pp`** en `Hasta 1 M CLP` (`87,7 %` vs. `46,2 %`, `n = 267`), **`+19,55 pp`** en `1 a 10 M CLP` (`65,4 %` vs. `45,8 %`, `n = 555`), **`+14,92 pp`** en `10 a 50 M CLP` (`71,0 %` vs. `56,1 %`, `n = 590`) y **`+13,47 pp`** en `Más de 50 M CLP` (`67,4 %` vs. `54,0 %`, `n = 298`), descartando que el tamaño del presupuesto explique por sí solo el patrón observado.

---

## 17. Regla para licitaciones con ganadoras de distinto tamaño (`Múltiple` fuera del eje ordinal)

- **Problema:** Una licitación puede adjudicar varias líneas u ofertas en `04LicitacionesEne_procesado.csv` a proveedores de distinto tamaño empresarial (por ejemplo, una oferta `Micro` y otra `Grande`). Elegir arbitrariamente la primera fila, la moda o el mayor monto ocultaría la naturaleza mixta de la adjudicación y distorsionaría la escala ordinal por tamaño.
- **Decisión:** En `asignar_tamano_ganador()` ([`src/comunicacion.py`](../src/comunicacion.py)), normalizar `NroLicitacion` y `ResultadoOferta`, filtrar las filas `"GANADORA"` y asignar la etiqueta por licitación así: si todas las ganadoras comparten un único valor en `TamanoProveedor`, se conserva esa categoría (`Micro`, `Pequeña`, `Mediana`, `Grande` o `NoClasificado`); si concurren **`2` o más tamaños distintos**, se etiqueta explícitamente como **`"Múltiple"`** (y `"Sin ganadora"` si no hubiese filas ganadoras). En `TamanoGanadorOrdinal` solo permanecen los cuatro niveles de `ORDEN_TAMANO`, dejando tanto `"Múltiple"` como `"NoClasificado"` como `<NA>` fuera del eje ordinal, y se reporta el análisis de sensibilidad con y sin exclusiones mediante `tasas_exclusion_tamano()`.
- **Justificación:** Preserva transparencia metodológica sin inventar un tamaño dominante artificial, evita sesgar las pruebas ordinales (`Chi-cuadrado` y `Spearman`) ni el control estratificado, y visibiliza por separado el comportamiento propio de las adjudicaciones con múltiples proveedores ganadores.
- **Fuente / Evidencia:** [`src/comunicacion.py`](../src/comunicacion.py) (`asignar_tamano_ganador`, `tasas_exclusion_tamano`), [`F4/F4_Visualizacion_Comunicacion.ipynb`](../F4/F4_Visualizacion_Comunicacion.ipynb) (Secciones `4`, `5.1`, `5.3`, `8.2` y `8.3`) y [`docs/hallazgos_f4.csv`](./hallazgos_f4.csv).
- **Impacto medido:** Identifica **`240` licitaciones `"Múltiple"`** (frente a `1.733` con tamaño único ordinal y `284` `"NoClasificado"`), las cuales presentan solo **`7,08 %`** de coincidencia exacta (IC `95 %` Wilson `[4,47 %; 11,05 %]`) y una mediana de brecha relativa de **`+151,16 %`** (`IQR = 424,36 pp`); excluirlas explica que la coincidencia global comparable suba de **`55,56 %` (`1.254/2.257`) a `61,33 %` (`1.237/2.017`, `+5,73 pp`)**.

---

## 18. Pruebas unificadas en `tests/` con `pytest`

- **Problema:** Las pruebas de F2 y F3 vivían en `src/pruebas_preprocesamiento.py` y `src/pruebas_pipeline.py` como funciones que solo se ejecutaban desde los notebooks, sin un comando único para verificar el proyecto completo. Además, F4 no tenía pruebas propias y la retroalimentación de la Sumativa 2 pidió un módulo de pruebas en `tests/` con casos conocidos y casos nuevos.
- **Decisión:** Trasladar las pruebas a `tests/`, ejecutadas con `pytest` desde la raíz (`pytest.ini`), y eliminar los módulos `src/pruebas_*.py` para que `src/` no dependa de las pruebas. La suite queda en cuatro archivos:
  1. `test_preprocesamiento.py`: reglas de F2 (duplicados, brecha, tamaño, esquema, IQR y SHA-256).
  2. `test_pipeline.py`: los `17` casos de las clases de F3; `ejecutar_pruebas_pipeline()` se mantiene para la tabla de la sección `7` de F3.
  3. `test_regresion_f2.py`: igualdad exacta del pipeline frente a las salidas de F2 con `pd.testing.assert_frame_equal`, sobre el raw y sobre datos sintéticos.
  4. `test_comunicacion.py`: casos conocidos de F4 comparados con `docs/hallazgos_f4.csv` y siete casos nuevos de la retroalimentación (razón igual a `1`, coincidencia del `100 %`, tamaño sin casos, monedas distintas de `CLP`, artefacto faltante, Wilson con `0` éxitos o grupo vacío, y contrato roto).
- **Justificación:** Un solo comando verifica F2, F3 y F4, y cualquier cambio en `src/` que altere una cifra publicada falla antes de llegar al informe. La prueba que necesita el raw se omite con un mensaje claro cuando el archivo no está, de modo que la suite también corre en un clon sin datos.
- **Fuente / Evidencia:** [`tests/`](../tests/), [`pytest.ini`](../pytest.ini), [`F2/F2_Preprocesamiento.ipynb`](../F2/F2_Preprocesamiento.ipynb) y [`F3/F3_Nucleo_Algoritmico.ipynb`](../F3/F3_Nucleo_Algoritmico.ipynb) (secciones `1` y `7`), que importan las pruebas desde `tests/`.
- **Impacto medido:** `36` pruebas aprobadas con `pytest` en unos `6 s` cuando está el raw; sin el raw, `35` aprobadas y `1` omitida en unos `2 s`. La regresión confirma igualdad exacta (`check_exact=True`) con `45.741` ofertas y `2.292` licitaciones de F2, y los casos conocidos reproducen desde `src/` las cifras de `docs/hallazgos_f4.csv` (por ejemplo, `1.254` de `2.257` en OE1 y `228` de `520` en OE2). `data/processed/` y las figuras de F4 no cambian.

---

## 19. Mantener la copia del proyecto como entrada y documentar su procedencia frente a la fuente pública

- **Problema:** La retroalimentación de la Sumativa 2 sugirió documentar la descarga desde el portal público de ChileCompra «con el mismo SHA-256 esperado». Al localizar la fuente pública ([`Municipalidades.7z`](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z) de Mercado Público, publicado el 23 de abril de 2025) se constató que la copia del proyecto no es idéntica: al inicio del proyecto el grupo quitó las columnas `Proveedor` y `ProveedorRUT` usando Excel, que además reescribió el formato de algunos valores (fechas sin segundos, montos redondeados, códigos largos en notación científica). El SHA-256 del archivo público no puede coincidir con el documentado.
- **Decisión:** Mantener la copia del proyecto (SHA-256 sin `\r` `ec308de2…41bf`) como entrada de F2–F4, sin regenerar salidas. Documentar en [`data/raw/README.md`](../data/raw/README.md) la fuente pública con su propio SHA-256, las diferencias con la copia y la equivalencia de resultados. No versionar el crudo ni una muestra seudonimizada.
- **Justificación:** El paso manual no altera los resultados del análisis, por lo que cambiar la entrada a pocos días de la entrega solo modificaría los SHA-256 de todas las salidas sin mejorar las conclusiones. El crudo no se versiona porque su texto libre contiene datos de terceros (en `NombreOferta`: razones sociales en 4.672 filas, RUT en 272, correos en 134 y teléfonos en 194; en `Descripcion`: nombres de funcionarios). Una copia seudonimizada reproduce las salidas byte a byte, pero se descartó para no cambiar la entrada en la etapa de cierre.
- **Fuente / Evidencia:** Comparación de ambos archivos (45.741 filas en el mismo orden; 74 frente a 72 columnas) y ejecución de `construir_pipeline()` ([`src/pipeline_licitaciones.py`](../src/pipeline_licitaciones.py)) sobre cada uno; [`data/raw/README.md`](../data/raw/README.md) con la tabla de SHA-256 de ambas versiones.
- **Impacto medido:** Con el archivo público el pipeline entrega las mismas **`2.257`** licitaciones comparables y las mismas **`1.254`** coincidencias, y los mismos duplicados potenciales; solo **`7` de `2.292`** licitaciones difieren en `MontoTotalGanadoras`, en menos de una parte en `10⁻⁹`, sin cambiar ninguna clasificación de coincidencia. Las figuras y `docs/hallazgos_f4.csv` no cambian. Riesgo declarado: con el archivo público, las fechas con segundos no se convierten con el formato actual (`%d-%m-%Y %H:%M`) y quedan vacías; no afecta los resultados de la brecha, que no usan fechas, y se registra como trabajo futuro.
