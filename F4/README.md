# Fase 4 · Visualización y comunicación

El notebook [F4_Visualizacion_Comunicacion.ipynb](F4_Visualizacion_Comunicacion.ipynb) calcula y presenta la coincidencia con el monto estimado, la brecha por licitación y los resultados según el tamaño ganador.

## Ejecutar F4 desde cero

1. Abre una terminal en la **raíz del repositorio**, donde está `requirements.txt`. Crea `.venv`, instala las dependencias y registra el kernel según la [guía de configuración](../README.md#configurar-el-entorno).
2. Para regenerar los datos desde la fuente, coloca el CSV crudo en la ruta de la tabla de entradas y ejecuta **F1 → F2 → F3** siguiendo el [orden de ejecución](../README.md#ejecutar-los-notebooks). Si los cuatro CSV versionados de `data/processed/` ya están disponibles, puedes abrir F4 directamente.
3. Desde la raíz, inicia JupyterLab con `python -m jupyter lab` en el entorno activo. En PowerShell puedes usar `.\.venv\Scripts\python.exe -m jupyterlab`. También puedes abrir la raíz como carpeta de trabajo en VS Code.
4. Abre `F4/F4_Visualizacion_Comunicacion.ipynb`, selecciona **Python (grupo2-mcdi500)** (identificador `grupo2_mcdi500`) y elige **Restart Kernel and Run All Cells**. Guarda el notebook si quieres conservar las tablas y figuras visibles.

## Entradas

Las rutas se indican desde la raíz del repositorio.

| Archivo | Uso |
| --- | --- |
| `data/processed/04LicitacionesEne_procesado.csv` | Tabla de ofertas por ítem generada en F2. Aporta las filas ganadoras y el tamaño del proveedor. |
| `data/processed/04LicitacionesEne_brecha_por_licitacion.csv` | Tabla por licitación generada en F2. Aporta el estimado, el total ganador, la moneda y la brecha. |
| `data/processed/diccionario_f3.csv` | Diccionario generado en F3 para verificar el esquema y los tipos. |
| `data/processed/parametros_f3.csv` | Parámetros y conteos de referencia generados en F3. |
| `data/raw/04LicitacionesEne.csv` | CSV que se descarga por separado. Es necesario para regenerar F2 y F3 y, en F4, para contrastar con la fuente y ejecutar el escenario que retira solo las copias adicionales. |

Descarga y descomprime `04LicitacionesEne.zip`. Coloca el archivo **`04LicitacionesEne.csv`** directamente en **`data/raw/`**. Las opciones de descarga y la comprobación SHA-256 están en la [guía de datos originales](../data/raw/README.md). F4 puede abrir y ejecutar el análisis con los cuatro CSV procesados aunque falte el crudo. En ese caso registra las comprobaciones y el escenario que omite.

## Salidas

| Ruta | Contenido |
| --- | --- |
| `F4/figuras/01_coincidencia_por_tamano.png` | Tasas de coincidencia por tamaño ganador, intervalos de Wilson y referencia global. |
| `F4/figuras/02_razon_ganador_estimado_log.png` | Histograma de la razón entre total ganador y estimado en escala logarítmica. |
| `F4/figuras/03_cajas_brecha_relativa_tamano.png` | Diagramas de caja de la brecha relativa por tamaño ganador. |
| `docs/hallazgos_f4.csv` | Registro de indicadores y secciones del notebook que los producen. |
| `docs/metadatos_f4.json` | Entorno de ejecución, entradas, verificaciones y configuración de las figuras. |

Los PNG se exportan a 200 ppp y `F4/figuras/` está excluida de Git.
