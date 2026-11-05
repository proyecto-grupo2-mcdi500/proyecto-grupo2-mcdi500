# Documentación Compartida: Metadatos y Diccionario de Variables

Esta carpeta reúne la documentación técnica compartida del proyecto **Análisis de Licitaciones Públicas en Chile (Primer Semestre 2025 — MCDI-500, Grupo 2)**, incluyendo los metadatos del conjunto de datos, las reglas y hallazgos del preprocesamiento (Fase 2) y el diccionario completo de las **74 variables** de la base.

---

## 1. Metadatos del Conjunto de Datos

| Atributo | Detalle |
| :--- | :--- |
| **Fuente oficial** | [ChileCompra — Portal de Datos Abiertos](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones) |
| **Periodo cubierto** | Enero de 2025 (procesos publicados/cerrados en el periodo e historial asociado) |
| **Archivo original (`raw`)** | `data/raw/04LicitacionesEne.csv` |
| **Formato y codificación original** | Texto plano CSV delimitado por punto y coma (`;`), codificación `latin-1` (ISO-8859-1) |
| **Archivo procesado (`processed`)** | `data/processed/04LicitacionesEne_procesado.csv` |
| **Formato y codificación procesada** | CSV delimitado por punto y coma (`;`), codificación `utf-8-sig` (UTF-8 con BOM) |
| **Cantidad de registros (filas)** | **45.741** filas |
| **Cantidad de variables (columnas)** | **74** columnas |
| **Filas completamente duplicadas** | **0** duplicados exactos |
| **Unidad de análisis (granularidad)** | Cada fila representa la **oferta de un proveedor (`ProveedorRUT`) para un ítem o línea de producto específico (`CodigoProductoONU` / `NombreItem`) dentro de una licitación (`NroLicitacion`)**. |

---

## 2. Resumen de Metadatos y Reglas de Preprocesamiento (Fase 2)

En el cuaderno `F2/F2_Preprocesamiento.ipynb` se aplicaron transformaciones controladas sobre la copia de trabajo `df_trabajo` (manteniendo intacto el archivo original en `data/raw/`):

### 2.1. Conversión de variables temporales (`datetime64[ns]`)
- **Columnas transformadas:** `FechaPublicacion`, `FechaCierre` y `FechaAdjudicacion`.
- **Formato de entrada:** `%d-%m-%Y %H:%M` (ejemplo: `27-12-2024 11:07`).
- **Resultado de validación:**
  - `FechaPublicacion`: 0 nulos originales, **0 fallos de conversión**.
  - `FechaCierre`: 0 nulos originales, **0 fallos de conversión**.
  - `FechaAdjudicacion`: 91 nulos originales (0,20%, correspondientes a licitaciones en estado `Cerrada`, `Desierta` o `Suspendida`), **0 fallos de conversión**.

### 2.2. Limpieza y conversión de montos de oferta (`Float64`)
- **Columnas transformadas:** `MontoNetoOferta` y `MontoTotalOferta`.
- **Problema detectado en crudo:** Ambas columnas eran leídas como texto (`str`) debido a la presencia de comas decimales (`1.123` casos en `MontoNetoOferta` y `193` casos en `MontoTotalOferta`, como `32773109,24` o `10504,202`).
- **Regla aplicada:** Eliminación de espacios laterales (`.str.strip()`), reemplazo de coma decimal `,` por punto `.` sin eliminar dígitos ni redondear, y conversión a tipo numérico `Float64`.
- **Resultado de validación:** **0 nulos originales y 0 fallos de conversión** en ambas variables.

### 2.3. Separación por moneda (`MonedaOferta`)
Los montos están expresados en 4 unidades monetarias distintas que **no deben mezclarse** directamente en cálculos estadísticos sin conversión previa:

| Moneda (`MonedaOferta`) | Descripción | Cantidad de Ofertas | Mínimo (`MontoTotalOferta`) | Mediana (`MontoTotalOferta`) | Promedio (`MontoTotalOferta`) | Máximo (`MontoTotalOferta`) |
| :---: | :--- | ---: | ---: | ---: | ---: | ---: |
| **`CLP`** | Peso chileno | 45.604 (99,70%) | -1,00 | 259.200,00 | 9.211.294,13 | 61.725.500.000,00 |
| **`CLF`** | Unidad de Fomento (UF) | 105 (0,23%) | 1,00 | 449,16 | 104.762.480.262,24 | 10.000.000.000.000,00 |
| **`USD`** | Dólar estadounidense | 23 (0,05%) | 0,176 | 30.906,00 | 52.443,72 | 474.798,00 |
| **`UTM`** | Unidad Tributaria Mensual | 9 (0,02%) | 2,8924 | 556,80 | 21.708,93 | 48.617,65 |

### 2.4. Estandarización y ordenamiento de variables categóricas
- **Revisión de nombres equivalentes (`.str.strip().str.upper()`):**
  - `TamanoProveedor`, `Institucion`, `UnidadMedida` y `NombreItem`: **0 diferencias** entre valores originales y normalizados.
  - `Proveedor`: 4.700 nombres originales vs. 4.699 normalizados (**1 variante** por mayúsculas/minúsculas). Además, se verificó que **0 RUTs (`ProveedorRUT`)** tienen más de un nombre de proveedor asociado.
  - `UnidadCompra`: 419 nombres originales vs. 368 normalizados (**51 variantes** por diferencias de mayúsculas/minúsculas o espacios).
- **Ordenamiento lógico de `TamanoProveedor` (`CategoricalDtype`):**
  Se transformó `TamanoProveedor` en una categoría ordenada (`ordered=True`) con la siguiente jerarquía y distribución:
  1. `Micro`: **6.539** ofertas (14,30%)
  2. `Pequeña`: **13.510** ofertas (29,54%)
  3. `Mediana`: **8.570** ofertas (18,74%)
  4. `Grande`: **11.848** ofertas (25,90%)
  5. `NoClasificado`: **5.274** ofertas (11,53%)

### 2.5. Detección de valores anómalos y atípicos (Criterio IQR en CLP)
- **Valores negativos o cero:** Se identificó **1 oferta con monto negativo (`-1,0` en CLP)** tanto en `MontoNetoOferta` como en `MontoTotalOferta` y **0 ofertas con monto igual a cero**.
- **Rango Intercuartílico (IQR) para `MontoTotalOferta` en `CLP` ($n = 45.604$):**
  - Primer cuartil ($Q_1$, 25%): **$43.600,00**
  - Tercer cuartil ($Q_3$, 75%): **$1.801.754,50**
  - Rango intercuartílico ($\text{IQR} = Q_3 - Q_1$): **$1.758.154,50**
  - Límite inferior ($Q_1 - 1,5 \times \text{IQR}$): **-$2.593.631,75**
  - Límite superior ($Q_3 + 1,5 \times \text{IQR}$): **$4.438.986,25**
  - **Valores atípicos detectados:** **7.636 ofertas (16,74% de las ofertas en CLP)**. No se eliminan automáticamente ya que en compras públicas coexisten licitaciones menores (`L1`, `< 100 UTM`) con grandes licitaciones de obras y equipamiento (`LP`, `LQ`, `LR`, `> 1.000 UTM`).

### 2.6. Columnas vacías (100% nulos) y columnas constantes (1 solo valor)
- **Columnas con 100% de valores nulos (3 columnas):** `LicitacionBaseTipo`, `ContratoRenovable` y `UnidadTiempoRenovacion`.
- **Columnas constantes en toda la base (4 columnas):** `LicitacionInformada` (`1` valor único), `TipoAdjudicacion` (`1` valor único), `ValorTiempoRenovacion` (`1` valor único) y `Sector` (`1` valor único).

---

## 3. Diccionario Completo de Variables (74 Columnas)

### 3.1. Identificación, Clasificación y Montos Estimados de la Licitación (Columnas 1 a 10)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 1 | `NroLicitacion` | `str` | `str` | 0 | 0,00% | 2.292 | Código identificador único de la licitación en Mercado Público (ej. `2366-129-L124`). |
| 2 | `NombreLicitacion` | `str` | `str` | 0 | 0,00% | 2.282 | Título o nombre asignado al proceso licitatorio por la institución compradora. |
| 3 | `TipoLicitacion` | `str` | `str` | 0 | 0,00% | 9 | Modalidad y tramo en UTM de la licitación (`L1`, `LE`, `LP`, `LQ`, `LR`, `LS` o privada). |
| 4 | `Descripcion` | `str` | `str` | 0 | 0,00% | 2.222 | Descripción general del requerimiento o alcance de la licitación. |
| 5 | `MonedaLicitacion` | `str` | `str` | 0 | 0,00% | 4 | Moneda en la que se define el presupuesto de la licitación (`CLP`, `CLF`, `USD`, `UTM`). |
| 6 | `MontoEstimadoLicitacion` | `int64` | `int64` | 0 | 0,00% | 1.786 | Presupuesto o monto total estimado para la licitación completa. |
| 7 | `MontoEstimadoVisible` | `str` | `str` | 0 | 0,00% | 2 | Indica si el monto estimado fue visible para los oferentes (`Si` / `No`). |
| 8 | `BaseEstimacionMontoLicitacion` | `str` | `str` | 0 | 0,00% | 3 | Criterio empleado para estimar el monto (ej. `Precio Referencial`, `Presupuesto Disponible`). |
| 9 | `FuenteFinanciamiento` | `str` | `str` | 20.012 | 43,75% | 609 | Origen de los fondos con que se financia la compra pública. |
| 10 | `JustificacionMontoEstimado` | `str` | `str` | 29.854 | 65,27% | 495 | Glosa o código de justificación del presupuesto estimado de la licitación. |

### 3.2. Cronograma e Hitos Temporales de la Licitación (Columnas 11 a 21)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 11 | `FechaPublicacion` | `str` | `datetime64[ns]` | 0 | 0,00% | 2.015 | Fecha y hora de publicación del llamado a licitación *(convertida en Paso 14)*. |
| 12 | `FechaInicioPreguntas` | `str` | `str` | 0 | 0,00% | 1.715 | Fecha y hora de apertura del foro de consultas de los proveedores. |
| 13 | `FechaFinalPreguntas` | `str` | `str` | 0 | 0,00% | 1.232 | Fecha y hora de cierre para la recepción de preguntas. |
| 14 | `FechaPublicacionRespuestas` | `str` | `str` | 0 | 0,00% | 1.125 | Fecha y hora comprometida para publicar el acta de respuestas y aclaraciones. |
| 15 | `FechaActoAperturaTecnica` | `str` | `str` | 0 | 0,00% | 1.100 | Fecha y hora de apertura de las ofertas técnicas. |
| 16 | `FechaActoAperturaEconomica` | `str` | `str` | 0 | 0,00% | 1.104 | Fecha y hora de apertura de las ofertas económicas. |
| 17 | `FechaCierre` | `str` | `datetime64[ns]` | 0 | 0,00% | 810 | Fecha y hora límite para presentar ofertas en la licitación *(convertida en Paso 14)*. |
| 18 | `FechaAdjudicacion` | `str` | `datetime64[ns]` | 91 | 0,20% | 2.144 | Fecha y hora efectiva de adjudicación de la licitación *(convertida en Paso 14)*. |
| 19 | `FechaEntregaEnSoporteFisico` | `str` | `str` | 45.457 | 99,38% | 22 | Fecha límite de entrega de antecedentes físicos (cuando aplica). |
| 20 | `FechaEstimadaEvaluacionOfertas` | `str` | `str` | 43.489 | 95,08% | 22 | Fecha estimada de evaluación de las ofertas recibidas. |
| 21 | `UnidadTiempoEvaluacion` | `str` | `str` | 88 | 0,19% | 3 | Unidad de medida del plazo de evaluación (ej. horas, días). |

### 3.3. Condiciones Administrativas, Adjudicación y Contrato (Columnas 22 a 48)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 22 | `EstadoLicitacion` | `str` | `str` | 0 | 0,00% | 4 | Estado del proceso (`Adjudicada`: 45.570, `Cerrada`: 95, `Desierta`: 72, `Suspendida`: 4). |
| 23 | `ContemplaObrasPublicas` | `str` | `str` | 4.929 | 10,78% | 2 | Indica si la licitación contempla ejecución de obras públicas (`Si` / `No`). |
| 24 | `LicitacionInformada` | `str` | `str` | 0 | 0,00% | 1 | Indicador constante en la muestra (`1` valor único). |
| 25 | `LicitacionBaseTipo` | `float64` | `float64` | 45.741 | 100,00% | 0 | Indicador de uso de Bases Tipo de Contraloría *(columna 100% nula)*. |
| 26 | `TipoAdjudicacion` | `str` | `str` | 0 | 0,00% | 1 | Modalidad de adjudicación *(columna constante en la muestra)*. |
| 27 | `TipoAprobacionAdjudicacion` | `str` | `str` | 0 | 0,00% | 5 | Tipo de acto administrativo que aprueba la adjudicación (Resolución, Decreto, etc.). |
| 28 | `NumeroActaAprobacion` | `str` | `str` | 0 | 0,00% | 1.207 | Número o folio del acto administrativo que aprueba la adjudicación. |
| 29 | `FechaActaAprobacion` | `str` | `str` | 0 | 0,00% | 94 | Fecha del acto o resolución de aprobación de la adjudicación. |
| 30 | `TipoConvocatoria` | `str` | `str` | 0 | 0,00% | 2 | Carácter de la convocatoria (`Abierta` / `Cerrada`). |
| 31 | `NroEtapasLicitacion` | `str` | `str` | 0 | 0,00% | 2 | Cantidad de etapas de apertura (`1` etapa simultánea o `2` etapas). |
| 32 | `SubContratacion` | `str` | `str` | 0 | 0,00% | 2 | Indica si las bases permiten subcontratación (`Si` / `No`). |
| 33 | `ProhibicionSubContratacion` | `str` | `str` | 32.845 | 71,81% | 289 | Motivo o detalle de restricciones a la subcontratación. |
| 34 | `TomaRazonContraloria` | `str` | `str` | 3.206 | 7,01% | 2 | Indica si el contrato requiere Toma de Razón por la Contraloría General de la República. |
| 35 | `PublicidadOfertasTecnicas` | `str` | `str` | 3.206 | 7,01% | 1 | Indica si las ofertas técnicas son públicas tras el cierre. |
| 36 | `RazonPublicidadOfertasTecnicas` | `str` | `str` | 44.018 | 96,23% | 1 | Justificación en caso de reserva de las ofertas técnicas. |
| 37 | `Contrato` | `str` | `str` | 3.206 | 7,01% | 3 | Indica si la adquisición requiere formalización de contrato o se formaliza vía Orden de Compra. |
| 38 | `TiempoDuracionContrato` | `int64` | `int64` | 0 | 0,00% | 67 | Valor numérico de la duración del contrato. |
| 39 | `UnidadTiempoDuracionContrato` | `str` | `str` | 1.748 | 3,82% | 4 | Unidad de tiempo de la duración del contrato (horas, días, meses, años). |
| 40 | `ContratoRenovable` | `float64` | `float64` | 45.741 | 100,00% | 0 | Indica si el contrato es renovable *(columna 100% nula)*. |
| 41 | `ValorTiempoRenovacion` | `int64` | `int64` | 0 | 0,00% | 1 | Plazo de renovación del contrato *(columna constante en `0`)*. |
| 42 | `UnidadTiempoRenovacion` | `float64` | `float64` | 45.741 | 100,00% | 0 | Unidad de tiempo de renovación *(columna 100% nula)*. |
| 43 | `FechaEstimadaFirmaContrato` | `str` | `str` | 45.270 | 98,97% | 40 | Fecha estimada para la suscripción del contrato. |
| 44 | `TipoEjecucion` | `str` | `str` | 1.936 | 4,23% | 2 | Modalidad de ejecución del contrato (ej. ejecución inmediata o en el tiempo). |
| 45 | `PlazoPagoContrato` | `str` | `str` | 1.748 | 3,82% | 2 | Plazo establecido para el pago de facturas (ej. a 30 días). |
| 46 | `TipoPago` | `str` | `str` | 4.929 | 10,78% | 3 | Modalidad de pago definida en las bases. |
| 47 | `ObservacionContrato` | `str` | `str` | 30.817 | 67,37% | 377 | Observaciones adicionales sobre las condiciones contractuales. |
| 48 | `ExtensionPlazo` | `str` | `str` | 3.211 | 7,02% | 2 | Indica si la licitación tuvo extensión del plazo de cierre (`Si` / `No`). |

### 3.4. Organismo Comprador (Columnas 49 a 53)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 49 | `UnidadCompra` | `str` | `str` | 0 | 0,00% | 419 | Nombre de la unidad de compra específica dentro de la institución *(368 tras normalizar mayúsculas/espacios)*. |
| 50 | `UnidadCompraRUT` | `str` | `str` | 0 | 0,00% | 363 | RUT de la entidad o unidad compradora. |
| 51 | `entCode` | `int64` | `int64` | 0 | 0,00% | 326 | Código numérico único de la institución compradora en ChileCompra. |
| 52 | `Institucion` | `str` | `str` | 0 | 0,00% | 326 | Nombre oficial de la institución u organismo público comprador. |
| 53 | `Sector` | `str` | `str` | 0 | 0,00% | 1 | Sector del Estado al que pertenece el comprador *(constante en este archivo)*. |

### 3.5. Rubro e Ítem Licitado — Clasificador ONU (Columnas 54 a 62)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 54 | `RubroN1` | `str` | `str` | 0 | 0,00% | 55 | Categoría de rubro de nivel 1 (general) según clasificador UNSPSC/ONU. |
| 55 | `RubroN2` | `str` | `str` | 0 | 0,00% | 249 | Categoría de rubro de nivel 2 (familia de productos/servicios). |
| 56 | `RubroN3` | `str` | `str` | 0 | 0,00% | 782 | Categoría de rubro de nivel 3 (clase de productos/servicios). |
| 57 | `CodigoProductoONU` | `int64` | `int64` | 0 | 0,00% | 1.706 | Código numérico UNSPSC de 8 dígitos del producto o servicio licitado. |
| 58 | `ONUProducto` | `str` | `str` | 0 | 0,00% | 1.697 | Glosa estándar del producto según el clasificador de las Naciones Unidas. |
| 59 | `NombreItem` | `str` | `str` | 0 | 0,00% | 1.697 | Nombre del ítem o línea de producto solicitado en la licitación. |
| 60 | `DescripcionItem` | `str` | `str` | 92 | 0,20% | 7.729 | Especificación técnica detallada solicitada por el comprador para el ítem. |
| 61 | `UnidadMedida` | `str` | `str` | 0 | 0,00% | 47 | Unidad de medida del ítem requerido (Unidad, Global, Mes, Caja, Litro, etc.). |
| 62 | `CantidadItem` | `int64` | `int64` | 0 | 0,00% | 358 | Cantidad de unidades solicitadas por el organismo comprador en esa línea de ítem. |

### 3.6. Proveedor y Detalle de la Oferta Presentada (Columnas 63 a 74)

| # | Variable | Tipo Original | Tipo Procesado | Nulos | % Nulos | Valores Distintos | Descripción |
| :---: | :--- | :---: | :---: | ---: | ---: | ---: | :--- |
| 63 | `Proveedor` | `str` | `str` | 0 | 0,00% | 4.700 | Razón social o nombre del proveedor oferente *(4.699 tras normalizar mayúsculas/espacios)*. |
| 64 | `ProveedorRUT` | `str` | `str` | 0 | 0,00% | 4.701 | Rol Único Tributario (RUT) del proveedor oferente. |
| 65 | `ActividadProveedor` | `str` | `str` | 10.155 | 22,20% | 2.374 | Giro o actividad económica declarada por el proveedor. |
| 66 | `TamanoProveedor` | `str` | `category (ordered)` | 0 | 0,00% | 5 | Tamaño de empresa ordenado en Paso 27: `Micro` < `Pequeña` < `Mediana` < `Grande` < `NoClasificado`. |
| 67 | `NombreOferta` | `str` | `str` | 0 | 0,00% | 8.003 | Título dado por el proveedor a su propuesta comercial. |
| 68 | `EspecificacionesProveedor` | `str` | `str` | 0 | 0,00% | 34.028 | Detalle técnico de lo ofertado por el proveedor para ese ítem específico. |
| 69 | `EstadoOferta` | `str` | `str` | 0 | 0,00% | 2 | Admisibilidad de la oferta en el acto de apertura (`Aceptada`: 41.860, `Rechazada`: 3.881). |
| 70 | `CantidadOferta` | `int64` | `int64` | 0 | 0,00% | 358 | Cantidad de unidades ofertadas por el proveedor para el ítem. |
| 71 | `MonedaOferta` | `str` | `str` | 0 | 0,00% | 4 | Moneda de la oferta (`CLP`: 45.604, `CLF`: 105, `USD`: 23, `UTM`: 9). |
| 72 | `MontoNetoOferta` | `str` | `Float64` | 0 | 0,00% | 16.765 | Precio unitario neto ofertado por el proveedor *(limpiado de coma decimal y convertido en Paso 18)*. |
| 73 | `MontoTotalOferta` | `str` | `Float64` | 0 | 0,00% | 21.376 | Monto total neto de la línea ofertada *(limpiado de coma decimal y convertido en Paso 18)*. |
| 74 | `ResultadoOferta` | `str` | `str` | 0 | 0,00% | 2 | Resultado final de la línea ofertada (`Ganadora`: 19.888 [43,48%], `Perdedora`: 25.853 [56,52%]). |
