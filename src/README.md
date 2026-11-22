# Código compartido (`src/`)

Esta carpeta contiene los módulos y funciones reutilizables por más de una fase del proyecto:

- **`utilidades.py`**: Utilidades generales, usadas por F1:
  - `ProyectoError`: Excepción personalizada para validaciones del proyecto.
  - `obtener_raiz_proyecto()`: Localiza la carpeta raíz del repositorio desde cualquier subdirectorio.
  - `normalizar_nombre(nombre)` y `normalizar_columnas(objeto)`: Estandarizan nombres de columnas a `snake_case` sin tildes ni caracteres especiales y detectan colisiones de nombres duplicados.
- **`preprocesamiento.py`**: Reglas del preprocesamiento de la Fase 2, usadas por F2 y por el pipeline de F3:
  - `calcular_sha256_sin_cr(ruta)` y `verificar_hash_raw(ruta)`: calculan el SHA-256 ignorando `\r` y validan `data/raw/04LicitacionesEne.csv` frente al hash LF `ec308de2...`, lanzando error con instrucciones si falta o no coincide (con un mensaje propio si es el archivo público de Mercado Público).
  - `identificar_raw(ruta)`: indica si `data/raw/04LicitacionesEne.csv` es la copia del proyecto, el archivo público, otro archivo o si falta; F1, F4 y `pytest` lo usan para decidir qué comprobaciones ejecutar (decisión 19).
  - `cargar_csv(ruta, verificar_hash=False)`: lee el archivo de entrada con `sep=";"`, excluye los identificadores directos del proveedor y valida las columnas requeridas (opcionalmente verificando el SHA-256).
  - `convertir_tipos()`, `tratar_faltantes()`, `marcar_duplicados()` y `ordenar_tamano()`: conversiones, regla por columna para los faltantes, duplicados potenciales y tamaño ordinal sin `NoClasificado`.
  - `calcular_brecha()`: brecha por licitación entre la suma de ofertas ganadoras y el monto estimado.
  - `calcular_limites_iqr()` y `aplicar_bandera_atipicos()`: valores extremos en CLP con IQR sobre logaritmos.
  - `validar_procesado()`: comprobaciones finales antes de exportar.
- **`pipeline_licitaciones.py`**: Pipeline orientado a objetos de la Fase 3: `Transformador` (clase base), `TransformacionFija`, `TratamientoFaltantes` (aprende qué columnas superan el 90 % de faltantes), `ExtremosLogIQR` (ajusta y reutiliza los límites IQR), `Pipeline` con observadores y `Bitacora`; además, `control_iterativo()` y `control_vectorizado()` para el control temporal.
- **`medicion.py`**: Comparación de implementaciones de un mismo cálculo (Fase 3):
  - `medir_tiempo(funcion, repeticiones)`: menor tiempo de varias ejecuciones con `timeit`.
  - `medir_memoria(funcion)`: memoria pico en MB con `tracemalloc`, en una ejecución aparte de la de tiempo.
  - `comparar(implementaciones)`: mide cada versión, verifica que todas entreguen el mismo resultado y devuelve una tabla comparativa.
- **`comunicacion.py`**: Carga selectiva de artefactos de `data/processed/`, cálculo de indicadores (intervalos de Wilson, razón, log-razón, tasas por tamaño, sensibilidad de IVA) y generación de figuras de la Fase 4.
- **`validar_dataset.py`**: Validador heurístico del conjunto de datos según los umbrales del curso (dimensiones, roles analíticos detectados en crudo, porcentaje de nulos, tamaño en MB y duplicados). El script `validar_dataset.py` en la raíz actúa como punto de entrada por línea de comandos (`python validar_dataset.py ...`).
