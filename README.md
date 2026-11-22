# proyecto-mcdi500
Proyecto grupal de Programación para la Ciencia de Datos.
Integrantes:    Ernesto Siebert Aguilera
                Oscar Salgado Sanhueza
                Bertgil Gonzalez Olmos
                Daniel Rojas Sánchez

# Análisis de Licitaciones Públicas en Chile (Enero 2025)
> **Asignatura:** Programación para la Ciencia de Datos (MCDI-500)  
> **Grupo:** 2

-------------------------------------------------------------------------------------------

## Introducción y Contexto

Las licitaciones públicas permiten a las instituciones adquirir bienes y servicios mediante procesos diseñados para promover la transparencia, la eficiencia y la libre competencia. El análisis sistemático de estos registros permite describir el comportamiento de las contrataciones del Estado, identificar tendencias de mercado y detectar posibles anomalías o patrones atípicos que ameriten un análisis más exhaustivo.

En este proyecto se analizan los registros de licitaciones de compras públicas correspondientes a **enero de 2025**, obtenidos desde el portal oficial de datos abiertos:
* **Fuente:** Mercado Público (ChileCompra), licitaciones por sector: [`Municipalidades.7z`](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z), primer semestre de 2025

El proyecto mide con qué frecuencia el monto estimado registrado de cada licitación coincide con la suma de sus ofertas ganadoras, cuantifica la brecha cuando difieren (dentro de una misma moneda) y examina si ambas cambian según el tamaño del proveedor ganador. El enfoque es descriptivo y cada hallazgo se interpreta dentro de las restricciones de los datos.

-------------------------------------------------------------------------------------------

## Objetivos del Proyecto

Los objetivos se definen en `F1/F1_Definicion.ipynb`; esta sección los resume.

* **Problema:** En las licitaciones de ChileCompra de enero de 2025, se desconoce con qué frecuencia el monto estimado registrado coincide con la suma de las ofertas ganadoras. El proyecto mide esa coincidencia y, cuando los montos difieren, cuantifica la brecha por licitación en los casos en que ambos están expresados en la misma moneda, y examina si ambas cambian según el tamaño del proveedor ganador.
* **Objetivo General:** Analizar la diferencia entre el monto estimado registrado y el total de las ofertas ganadoras en las licitaciones de ChileCompra de enero de 2025, y su relación con el tamaño del proveedor ganador.
* **Objetivos Específicos:**
  1. Determinar en qué proporción de las licitaciones comparables el monto estimado registrado coincide con el total de las ofertas ganadoras.
  2. Describir la magnitud y el sentido de la brecha por licitación cuando ambos montos difieren, separando por moneda.
  3. Comparar la coincidencia y la brecha según el tamaño del proveedor ganador.

Las preguntas de investigación y las restricciones de los datos están en las secciones 3 y 6 de `F1/F1_Definicion.ipynb`.

-------------------------------------------------------------------------------------------

## Tecnologías y Librerías

El análisis está implementado principalmente en **Python**:

* **Entorno:** Python en `.venv` y JupyterLab. La ejecución guardada de F4 usa Python 3.14.6.
* **Procesamiento, estadística y visualización:** `pandas`, `numpy`, `scipy` y `matplotlib`
* **Entorno de desarrollo:** Git, GitHub, VS Code

-------------------------------------------------------------------------------------------

## Estructura del Repositorio

<!-- ESTRUCTURA:INICIO -->
```text
proyecto-grupo2-mcdi500/
├── data/
│   ├── processed/
│   │   ├── 04LicitacionesEne_brecha_por_licitacion.csv
│   │   ├── 04LicitacionesEne_procesado.csv
│   │   ├── diccionario_f3.csv
│   │   ├── parametros_f3.csv
│   │   └── README.md
│   └── raw/
│       └── README.md
├── docs/
│   ├── arquitectura.md
│   ├── decisiones.md
│   ├── hallazgos_f4.csv
│   ├── metadatos_f4.json
│   └── README.md
├── src/
│   ├── comunicacion.py
│   ├── medicion.py
│   ├── pipeline_licitaciones.py
│   ├── preprocesamiento.py
│   ├── README.md
│   ├── utilidades.py
│   └── validar_dataset.py
├── F1/
│   ├── brainstorming/
│   │   └── ideas-dataset.md
│   └── F1_Definicion.ipynb
├── F2/
│   └── F2_Preprocesamiento.ipynb
├── F3/
│   ├── F3_Nucleo_Algoritmico.ipynb
│   └── README.md
├── F4/
│   ├── figuras/
│   │   ├── 01_coincidencia_por_tamano.png
│   │   ├── 02_razon_ganador_estimado_log.png
│   │   └── 03_cajas_brecha_relativa_tamano.png
│   ├── F4_Visualizacion_Comunicacion.ipynb
│   └── README.md
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_comunicacion.py
│   ├── test_pipeline.py
│   ├── test_preprocesamiento.py
│   └── test_regresion_f2.py
├── .mailmap
├── CHANGELOG.md
├── pytest.ini
├── README.md
├── requirements.txt
└── validar_dataset.py
```
<!-- ESTRUCTURA:FIN -->

- `README.md`: presenta el proyecto, su contexto, objetivos, fuente de datos, cómo configurar el entorno y cómo ejecutar los notebooks.
- `requirements.txt`: contiene las dependencias de Python necesarias para ejecutar el proyecto.
- `src/`: módulos compartidos (detalle en [`src/README.md`](src/README.md)):
  - `preprocesamiento.py`: reglas de F2 (carga, conversión de tipos, faltantes, duplicados, brecha, IQR y validación).
  - `pipeline_licitaciones.py`: clases del núcleo algorítmico de F3 (`Transformador`, `TransformacionFija`, `TratamientoFaltantes`, `ExtremosLogIQR`, `Pipeline` y `Bitacora`).
  - `medicion.py`: medición de tiempo (`timeit`) y memoria (`tracemalloc`) para comparar implementaciones.
  - `comunicacion.py`: carga de artefactos, indicadores y figuras de F4.
  - `utilidades.py`: utilidades generales (raíz del proyecto, nombres de columnas y `ProyectoError`).
- `tests/`: suite unificada de pruebas con `pytest` (`test_preprocesamiento.py`, `test_pipeline.py`, `test_regresion_f2.py` y `test_comunicacion.py`).
- `validar_dataset.py` y `src/validar_dataset.py`: scripts y módulos reutilizables para revisar y validar archivos de datos entre fases.
- `data/raw/`: ubicación local de los datos originales (`data/raw/04LicitacionesEne.csv`). El archivo no se versiona porque contiene datos personales; ver *Obtener los datos*.
- `data/processed/`: salidas de F2 y documentación generada por F3 (detalle en [`data/processed/README.md`](data/processed/README.md)).
- `docs/`: documentación compartida del proyecto.
- `F1/`: reúne en `F1/F1_Definicion.ipynb` la definición del problema, el alcance y la verificación del entorno, además de las ideas iniciales en `F1/brainstorming/ideas-dataset.md`.
- `F2/`: el cuaderno oficial es `F2/F2_Preprocesamiento.ipynb`, dedicado al preprocesamiento de los datos; sus salidas son `data/processed/04LicitacionesEne_procesado.csv` y `data/processed/04LicitacionesEne_brecha_por_licitacion.csv`.
- `F3/`: contiene `F3/F3_Nucleo_Algoritmico.ipynb` y su [`README.md`](F3/README.md), que describe la carpeta, los módulos que usa y cómo ejecutarlo.
- `F4/`: contiene `F4/F4_Visualizacion_Comunicacion.ipynb` y la [guía de ejecución de F4](F4/README.md).

Las carpetas de fase (`F1/` a `F4/`) no deben contener copias propias de `data/`, `docs/` ni `src/`. Si una fase genera un archivo reutilizable, se guarda en la ubicación compartida correspondiente; sus notebooks permanecen en la carpeta de la fase.

-------------------------------------------------------------------------------------------

## Configurar el entorno
-------------------------------------------------------------------------------------------
### macOS / Linux

Ejecuta los comandos desde la **raíz del repositorio**, donde está `requirements.txt`. Usa Python 3.14 si necesitas reproducir el entorno de la ejecución guardada de F4.

### 1. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
```

Cuando el entorno está activo, la terminal muestra `(.venv)`. Para salir del entorno: `deactivate`.

### 2. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check              # debe indicar: No broken requirements found
```

`requirements.txt` declara solo las dependencias directas del proyecto, con versión fija:

- Análisis, estadística y visualización: `numpy`, `pandas`, `scipy`, `matplotlib`
- Pruebas: `pytest`
- Ejecución de los notebooks: `ipykernel`, `jupyterlab`

`pip` instala las dependencias indirectas de cada una. Si el código empieza a importar una librería nueva, se agrega a `requirements.txt` con su versión (`paquete==versión`, la que muestra `python -m pip show paquete`) en el mismo *commit*, y se añade a `LIBRERIAS_PROYECTO` en la sección 8 de `F1/F1_Definicion.ipynb`.

### 3. Registrar el kernel del proyecto

Con el entorno activo en la misma terminal:

```bash
python -m ipykernel install --user --name grupo2_mcdi500 --display-name "Python (grupo2-mcdi500)"
```

`--name` es el identificador interno; `--display-name` es el nombre que aparece en JupyterLab. Los cuadernos del proyecto usan este kernel.

### 4. Abrir JupyterLab

```bash
python -m jupyter lab
```

La terminal queda ocupada mientras JupyterLab esté abierto. Para seguir usando la terminal, abra una segunda ventana, vuelva a la carpeta del proyecto y active el entorno con `source .venv/bin/activate`.

### 5. Verificar el entorno

En JupyterLab, abra `F1/F1_Definicion.ipynb`, seleccione el kernel **Python (grupo2-mcdi500)** y ejecute todas las celdas (*Run → Run All Cells*). En la sección 8 (*Verificación del Entorno*) debe cumplirse que:

- el entorno virtual aparece como `[OK] activo` y la ruta del intérprete contiene `.venv`;
- `numpy` y `pandas` aparecen con `[OK]` y su versión (ninguna como `[FALTA]`).

Si alguna de estas condiciones no se cumple, el cuaderno se detiene en el PASO 5.

| Si ocurre | Causa probable | Qué hacer |
| --- | --- | --- |
| El intérprete no contiene `.venv` | Kernel equivocado | *Kernel → Change Kernel* → Python (grupo2-mcdi500) |
| `ModuleNotFoundError` con un paquete instalado | Se instaló fuera del entorno o falta el paso 3 | Activar `.venv` y repetir los pasos 2 y 3 |
| Falla `pip install -r requirements.txt` | No hay una distribución compatible con el intérprete | Comprueba `python --version` y vuelve a crear `.venv` con Python 3.14 |

-------------------------------------------------------------------------------------------
### Windows

Estos pasos se realizan desde **Git Bash** (o la terminal integrada de **VS Code** con Git Bash) ubicados en la raíz del repositorio:

### 1. Crear y activar el entorno virtual

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows (Git Bash)
```

Cuando el entorno está activo, la terminal de Git Bash muestra `(.venv)`. Para salir del entorno: `deactivate`.

### 2. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check              # debe indicar: No broken requirements found
```

### 3. Registrar el kernel del proyecto

Con el entorno activo en Git Bash, ejecutar:

```bash
python -m ipykernel install --user --name grupo2_mcdi500 --display-name "Python (grupo2-mcdi500)"
```

### 4. Abrir el proyecto en VS Code

Desde Git Bash en la raíz del repositorio:

```bash
code .
```

Dentro de **VS Code**, al abrir cualquier cuaderno (`.ipynb`), hacer clic en **Select Kernel** (esquina superior derecha) → **Jupyter Kernel...** (o **Python Environments...**) y seleccionar **Python (grupo2-mcdi500)**.

### 5. Verificar el entorno en VS Code

Abrir `F1/F1_Definicion.ipynb` en VS Code, seleccionar el kernel **Python (grupo2-mcdi500)** y ejecutar todas las celdas (*Run All*). En la sección 8 (*Verificación del Entorno*) debe comprobarse que:

- el entorno virtual aparezca como `[OK] activo` y la ruta del intérprete apunte al entorno configurado;
- `numpy` y `pandas` aparezcan con `[OK]` y su versión instalada (ninguna como `[FALTA]`).

| Si ocurre | Causa probable | Qué hacer |
| --- | --- | --- |
| VS Code pide seleccionar un kernel | Primera vez que se abre el cuaderno | Hacer clic en *Select Kernel* → *Python (grupo2-mcdi500)* |
| `ModuleNotFoundError` al ejecutar una celda | Librerías instaladas en otro intérprete o kernel sin reiniciar | Ejecutar los pasos 2 y 3 en Git Bash y presionar *Restart* en la barra superior del notebook |
| Falla `pip install -r requirements.txt` | No hay una distribución compatible con el intérprete | Comprueba `python --version` y vuelve a crear `.venv` con Python 3.14 |

### Windows con PowerShell

Desde la raíz, puedes usar directamente el intérprete de `.venv`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ipykernel install --user --name grupo2_mcdi500 --display-name "Python (grupo2-mcdi500)"
.\.venv\Scripts\python.exe -m jupyterlab
```

-------------------------------------------------------------------------------------------

## Obtener los datos

El archivo fuente del proyecto (raw), `data/raw/04LicitacionesEne.csv`, no está en el repositorio (está excluido en `.gitignore`). Proviene de la fuente pública [`Municipalidades.7z`](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z) de Mercado Público, sin las columnas `Proveedor` y `ProveedorRUT`. El detalle está en [`data/raw/README.md`](data/raw/README.md).

1. Para reproducir byte a byte las salidas versionadas, descarga la copia exacta del proyecto desde [04LicitacionesEne.zip en OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) (cuenta UNAB). Sin cuenta UNAB, el archivo público permite comprobar las mismas cifras del análisis, con otro SHA-256.
2. Descomprímelo y deja el CSV en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 (ver [`data/raw/README.md`](data/raw/README.md)) o en Python mediante `verificar_hash_raw()` de `src/preprocesamiento.py` (compara automáticamente contra `ec308de2...` ignorando `\r`).

Sin el raw, F4 igual corre completo a partir de las salidas versionadas en `data/processed/`, y `pytest` solo omite la prueba de regresión contra F2.

No abras ni guardes el CSV con Excel: lo reescribe con otro formato y altera el contenido.

-------------------------------------------------------------------------------------------

## Ejecutar los notebooks

Los notebooks se ejecutan en este orden, con el entorno activado y el kernel **Python (grupo2-mcdi500)**, usando *Restart Kernel and Run All Cells*. Antes, descarga el archivo de entrada como se indica en *Obtener los datos*.

| Fase | Qué ejecutar | Entradas y salidas |
| --- | --- | --- |
| F1 | [F1_Definicion.ipynb](F1/F1_Definicion.ipynb) | Define el problema, los objetivos y las restricciones, y verifica el entorno. Si está disponible, consulta el CSV crudo para contrastar su encabezado. F2 usa la definición de F1 y no requiere archivos generados por esta fase. |
| F2 | [F2_Preprocesamiento.ipynb](F2/F2_Preprocesamiento.ipynb) | Lee `data/raw/04LicitacionesEne.csv`. Genera `data/processed/04LicitacionesEne_procesado.csv` (ofertas por ítem) y `data/processed/04LicitacionesEne_brecha_por_licitacion.csv` (una fila por licitación), que usan F3 y F4. |
| F3 | [F3_Nucleo_Algoritmico.ipynb](F3/F3_Nucleo_Algoritmico.ipynb) | Ejecuta el pipeline sobre el mismo CSV crudo y comprueba la igualdad con los dos CSV de F2. Genera `data/processed/diccionario_f3.csv` y `data/processed/parametros_f3.csv`, requeridos por F4. |
| F4 | [F4_Visualizacion_Comunicacion.ipynb](F4/F4_Visualizacion_Comunicacion.ipynb) | Lee los cuatro CSV de F2 y F3. Si está disponible, usa el crudo para contrastar las cifras y evaluar duplicados. Guarda tres PNG en `F4/figuras/`, los hallazgos en `docs/hallazgos_f4.csv` y los metadatos en `docs/metadatos_f4.json`. Consulta la [guía de F4](F4/README.md). |

-------------------------------------------------------------------------------------------

## Validar el dataset

El script raíz `validar_dataset.py` ejecuta el validador de `src/validar_dataset.py`. Es una comprobación adicional del CSV que puedes ejecutar desde la raíz con el entorno activado:

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```

-------------------------------------------------------------------------------------------

## Ejecutar las pruebas automatizadas (`pytest`)

Toda la suite de pruebas del proyecto se ejecuta con un único comando desde la raíz del repositorio, con el entorno virtual activo:

```bash
pytest
```
o alternativamente:
```bash
python -m pytest
```

La suite (`tests/`) incluye 36 pruebas automatizadas organizadas en:
- `tests/test_preprocesamiento.py`: reglas de preprocesamiento de F2 (esquema, tipos, nulos, duplicados, hash SHA-256 e IQR).
- `tests/test_pipeline.py`: 17 casos unitarios y de integración del pipeline orientado a objetos de F3 (normales, límite y de excepción).
- `tests/test_regresion_f2.py`: comparación del pipeline contra F2 mediante `pd.testing.assert_frame_equal` (Guía S3).
- `tests/test_comunicacion.py`: casos conocidos de F4 recalculados desde `src/` y comparados con `docs/hallazgos_f4.csv` y casos de robustez del feedback (razón 1,0, 100 % de coincidencia, tamaño sin observaciones, exclusión de monedas no CLP, artefacto faltante, Wilson con 0 éxitos o grupo vacío, y rechazo de contratos rotos).

