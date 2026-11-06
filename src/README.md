# Código compartido (`src/`)

Esta carpeta contiene los módulos y funciones reutilizables por más de una fase del proyecto:

- **`utilidades.py`**: Módulo de funciones compartidas para normalización de nombres, carga y preprocesamiento:
  - `ProyectoError`: Excepción personalizada para validaciones del proyecto.
  - `obtener_raiz_proyecto()`: Localiza la carpeta raíz del repositorio desde cualquier subdirectorio.
  - `normalizar_nombre(nombre)` y `normalizar_columnas(objeto)`: Estandarizan nombres de columnas a `snake_case` sin tildes ni caracteres especiales y detectan colisiones de nombres duplicados.
  - `cargar_datos_crudos()` y `cargar_datos_procesados()`: Cargan los archivos CSV desde `data/raw/` y `data/processed/`.
  - `convertir_fechas()`, `convertir_montos()` y `ordenar_tamano_proveedor()`: Transformaciones controladas de tipos de datos y categorías ordenadas.
  - `detectar_atipicos_iqr()`: Cálculo de cuartiles ($Q_1$, $Q_3$), rango intercuartílico ($\text{IQR}$) y máscara de valores atípicos.
- **`validar_dataset.py`**: Validador heurístico del conjunto de datos según los umbrales del curso (dimensiones, roles analíticos detectados en crudo, porcentaje de nulos, tamaño en MB y duplicados). El script `validar_dataset.py` en la raíz actúa como punto de entrada por línea de comandos (`python validar_dataset.py ...`).
