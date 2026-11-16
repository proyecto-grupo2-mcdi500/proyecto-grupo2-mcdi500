# Código compartido (`src/`)

Esta carpeta contiene los módulos y funciones reutilizables por más de una fase del proyecto:

- **`utilidades.py`**: Módulo de funciones compartidas para normalización de nombres, carga y preprocesamiento:
  - `ProyectoError`: Excepción personalizada para validaciones del proyecto.
  - `obtener_raiz_proyecto()`: Localiza la carpeta raíz del repositorio desde cualquier subdirectorio.
  - `normalizar_nombre(nombre)` y `normalizar_columnas(objeto)`: Estandarizan nombres de columnas a `snake_case` sin tildes ni caracteres especiales y detectan colisiones de nombres duplicados.
  - `cargar_datos_crudos()` y `cargar_datos_procesados()`: Cargan los archivos CSV desde `data/raw/` y `data/processed/`.
  - `convertir_fechas()`, `convertir_montos()` y `ordenar_tamano_proveedor()`: Transformaciones controladas de tipos de datos y categorías ordenadas.
  - `detectar_atipicos_iqr()`: Cálculo de cuartiles ($Q_1$, $Q_3$), rango intercuartílico ($\text{IQR}$) y máscara de valores atípicos.
- **`funciones_f2_revision.py`**: Reglas del preprocesamiento de la Fase 2, usadas por F2 y por el pipeline de F3:
  - `cargar_csv(ruta)`: lee el archivo de entrada con `sep=";"`, excluye los identificadores directos del proveedor y valida las columnas requeridas.
  - `convertir_tipos()`, `tratar_faltantes()`, `marcar_duplicados()` y `ordenar_tamano()`: conversiones, regla por columna para los faltantes, duplicados potenciales y tamaño ordinal sin `NoClasificado`.
  - `calcular_brecha()`: brecha por licitación entre la suma de ofertas ganadoras y el monto estimado.
  - `calcular_limites_iqr()` y `aplicar_bandera_atipicos()`: valores extremos en CLP con IQR sobre logaritmos.
  - `validar_procesado()`: comprobaciones finales antes de exportar.
- **`pruebas_f2.py`**: `ejecutar_pruebas_f2()` prueba las reglas anteriores con datos ficticios (casos normal, límite y de error).
- **`pipeline_licitaciones.py`**: Pipeline orientado a objetos de la Fase 3: `Transformador` (clase base), `TransformacionFija`, `ExtremosLogIQR` (ajusta y reutiliza los límites IQR), `Pipeline` con observadores y `Bitacora`; además, `control_iterativo()` y `control_vectorizado()` para el control temporal.
- **`medicion.py`**: Comparación de implementaciones de un mismo cálculo (Fase 3):
  - `medir_tiempo(funcion, repeticiones)`: menor tiempo de varias ejecuciones con `timeit`.
  - `medir_memoria(funcion)`: memoria pico en MB con `tracemalloc`, en una ejecución aparte de la de tiempo.
  - `comparar(implementaciones)`: mide cada versión, verifica que todas entreguen el mismo resultado y devuelve una tabla comparativa.
- **`validar_dataset.py`**: Validador heurístico del conjunto de datos según los umbrales del curso (dimensiones, roles analíticos detectados en crudo, porcentaje de nulos, tamaño en MB y duplicados). El script `validar_dataset.py` en la raíz actúa como punto de entrada por línea de comandos (`python validar_dataset.py ...`).
