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
* **Fuente:** [ChileCompra — Datos Abiertos](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones)

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

* **Entorno:** JupyterLab / Python 3.12 (versión con la que se fijó `requirements.txt`)
* **Procesamiento y Análisis:** `pandas`, `numpy`
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
│   └── README.md
├── src/
│   ├── preprocesamiento.py
│   ├── medicion.py
│   ├── pipeline_licitaciones.py
│   ├── pruebas_preprocesamiento.py
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
│   └── README.md
├── README.md
├── requirements.txt
└── validar_dataset.py
```
<!-- ESTRUCTURA:FIN -->

- `README.md`: presenta el proyecto, su contexto, objetivos, fuente de datos y herramientas utilizadas.
- `requirements.txt`: contiene las dependencias de Python necesarias para ejecutar el proyecto.
- `src/`: módulos compartidos. `preprocesamiento.py` contiene las reglas de F2 (carga, conversión, faltantes, duplicados, brecha, IQR y validación); `pipeline_licitaciones.py`, el pipeline orientado a objetos de F3; `medicion.py`, la comparación de implementaciones; `utilidades.py`, utilidades generales (raíz del proyecto, nombres de columnas y `ProyectoError`). El detalle está en [`src/README.md`](src/README.md).
- `validar_dataset.py` y `src/validar_dataset.py`: scripts y módulos reutilizables para revisar y validar archivos de datos entre fases.
- `data/raw/`: ubicación local de los datos originales (`data/raw/04LicitacionesEne.csv`). El archivo no se versiona porque contiene datos personales; ver *Obtener los datos*.
- `data/processed/`: carpeta destinada a almacenar los datos derivados y preparados para el análisis.
- `docs/`: documentación compartida del proyecto.
- `F1/`: reúne en `F1/F1_Definicion.ipynb` la definición del problema, el alcance y la verificación del entorno, además de las ideas iniciales en `F1/brainstorming/ideas-dataset.md`.
- `F2/`: el cuaderno oficial es `F2/F2_Preprocesamiento.ipynb`, dedicado a la exploración y preprocesamiento de los datos; su salida oficial es `data/processed/04LicitacionesEne_procesado.csv`.
- `F3/` y `F4/`: carpetas destinadas a los notebooks y entregables específicos de las etapas posteriores.

Las carpetas de fase (`F1/` a `F4/`) no deben contener copias propias de `data/`, `docs/` ni `src/`. Si una fase genera un archivo reutilizable, se guarda en la ubicación compartida correspondiente; sus notebooks permanecen en la carpeta de la fase.

-------------------------------------------------------------------------------------------

## Configurar el entorno
-------------------------------------------------------------------------------------------
### macOS / Linux

Estos pasos se hacen **una vez por computador**, desde la terminal y en la raíz del repositorio (en la rama de trabajo). El entorno no se crea desde los cuadernos: los cuadernos solo verifican que se esté usando el entorno correcto.

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

- Análisis: `numpy`, `pandas` (las que importan `src/` y los notebooks)
- Ejecución de los notebooks: `ipykernel`, `jupyterlab`

`pip` instala las dependencias indirectas de cada una. Si el código empieza a importar una librería nueva, se agrega a `requirements.txt` con su versión (`paquete==versión`, la que muestra `python -m pip show paquete`) en el mismo *commit*, y se añade a `LIBRERIAS_PROYECTO` en la sección 8 de `F1/F1_Definicion.ipynb`.

### 3. Registrar el kernel del proyecto

Con el entorno activo y en otra consola ejecutar:

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
| Falla `pip install -r requirements.txt` | Versión de Python distinta | Usar Python 3.12 |

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
| Falla `pip install -r requirements.txt` | Versión de Python distinta | Usar Python 3.12 |

-------------------------------------------------------------------------------------------

## Obtener los datos

El archivo de entrada `data/raw/04LicitacionesEne.csv` no está en el repositorio (está excluido en `.gitignore`). Cada integrante lo descarga una vez, después de configurar el entorno:

1. Descarga [04LicitacionesEne.zip desde OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) con tu cuenta UNAB (acceso solo para el grupo y el docente).
2. Descomprímelo y deja el CSV en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 como se indica en [`data/raw/README.md`](data/raw/README.md).

No abras ni guardes el CSV con Excel: lo reescribe con otro formato y altera el contenido.

-------------------------------------------------------------------------------------------

## Validar el dataset

Desde la raíz del repositorio, siempre con el entorno activado (`source .venv/bin/activate` en macOS/Linux o `source .venv/Scripts/activate` en Git Bash para Windows):

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
