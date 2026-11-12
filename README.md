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

A partir de este conjunto de datos, se examinan variables clave como instituciones compradoras, montos asignados, tipología de licitación, oferentes adjudicados y dispersión de las ofertas. El propósito es identificar patrones sistemáticos y eventuales señales de concentración o sesgo, manteniendo un enfoque exploratorio riguroso donde cualquier hallazgo se evalúe dentro del alcance y las limitaciones intrínsecas de los datos.

-------------------------------------------------------------------------------------------

## Objetivos del Proyecto

Los objetivos se definen en `F1/F1_Definicion.ipynb`; esta sección los resume.

* **Objetivo General:** Analizar los procesos de compras y licitaciones públicas registrados en ChileCompra durante enero de 2025 para describir las dinámicas de participación y adjudicación, caracterizar el comportamiento de los montos ofertados e identificar eventuales patrones de concentración o valores atípicos.
* **Objetivos Específicos:**
  1. Estructurar, limpiar y validar el dataset de licitaciones públicas descargado desde ChileCompra, documentando el tratamiento de fechas, montos, monedas, valores nulos y categorías.
  2. Realizar un Análisis Exploratorio de Datos (EDA) sobre montos ofertados, modalidades de licitación, rubros e instituciones públicas compradoras más activas.
  3. Estudiar la distribución de ofertas y adjudicaciones según el tamaño del proveedor (Micro, Pequeña, Mediana, Grande, NoClasificado) y detectar posibles concentraciones por sector o rubro.
  4. Evaluar el comportamiento de los plazos del proceso licitatorio y la presencia de valores extremos en los montos mediante el criterio del rango intercuartílico (IQR).

-------------------------------------------------------------------------------------------

## Tecnologías y Librerías

El análisis está implementado principalmente en **Python**:

* **Entorno:** JupyterLab / Python 3.12 (versión con la que se generó `requirements.txt`)
* **Procesamiento y Análisis:** `pandas`, `numpy`
* **Visualización:** `matplotlib`, `seaborn`
* **Entorno de desarrollo:** Git, GitHub, VS Code

-------------------------------------------------------------------------------------------

## Estructura del Repositorio

<!-- ESTRUCTURA:INICIO -->
```text
proyecto-grupo2-mcdi500/
├── data/
│   ├── processed/
│   │   ├── diccionario_f3.csv
│   │   ├── parametros_f3.csv
│   │   └── README.md
│   └── raw/
│       └── README.md
├── docs/
│   └── README.md
├── src/
│   ├── medicion.py
│   ├── pipeline_licitaciones.py
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
- `src/utilidades.py`: módulo compartido con funciones reutilizables de normalización de nombres (`normalizar_nombre`, `normalizar_columnas`), carga de datos (`cargar_datos_crudos`, `cargar_datos_procesados`), conversión de fechas y montos, ordenamiento de categorías y detección de valores atípicos (IQR), además de la excepción `ProyectoError`.
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

`requirements.txt` fija la versión exacta de cada paquete. Incluye la base de trabajo con la que se configuró el proyecto:

- Jupyter: `jupyterlab`, `notebook`, `ipykernel`
- Análisis: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`
- Integración con Git: `jupyterlab-git`, `jupytext`, `nbstripout`

El archivo se generó con `pip freeze`, por lo que también lista las dependencias indirectas de esos paquetes (unos 120 en total). Si un integrante instala o elimina una librería, debe regenerarlo con el entorno activo y subirlo en el mismo *commit*:

```bash
python -m pip freeze > requirements.txt
```

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

> **Nota sobre `nbstripout`:** está instalado, pero **no** debe activarse en el repositorio (`nbstripout --install`), porque borraría las salidas de los cuadernos al hacer *commit* y los entregables deben quedar ejecutados.

### 5. Verificar el entorno

En JupyterLab, abra `F1/F1_Definicion.ipynb`, seleccione el kernel **Python (grupo2-mcdi500)** y ejecute todas las celdas (*Run → Run All Cells*). En la sección 8 (*Verificación del Entorno*) debe cumplirse que:

- el entorno virtual aparece como `[OK] activo` y la ruta del intérprete contiene `.venv`;
- `numpy`, `pandas`, `matplotlib`, `seaborn` y `sklearn` aparecen con `[OK]` y su versión (ninguna como `[FALTA]`).

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
python -m pip install pandas numpy matplotlib seaborn scikit-learn scipy ipykernel
python -m pip check              # debe indicar: No broken requirements found
```

> **Nota para Windows:** Como `requirements.txt` fue generado con `pip freeze` en macOS, contiene dependencias exclusivas de sistemas Unix (`appnope`, `pexpect`, `ptyprocess`). Por ello, en Windows se instalan directamente las librerías principales de análisis y el kernel de Jupyter con el comando anterior.

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
- `numpy`, `pandas`, `matplotlib`, `seaborn` y `sklearn` aparezcan con `[OK]` y su versión instalada (ninguna como `[FALTA]`).

| Si ocurre | Causa probable | Qué hacer |
| --- | --- | --- |
| VS Code pide seleccionar un kernel | Primera vez que se abre el cuaderno | Hacer clic en *Select Kernel* → *Python (grupo2-mcdi500)* |
| `ModuleNotFoundError` al ejecutar una celda | Librerías instaladas en otro intérprete o kernel sin reiniciar | Ejecutar los pasos 2 y 3 en Git Bash y presionar *Restart* en la barra superior del notebook |
| Falla `pip install -r requirements.txt` en Windows | Paquetes exclusivos de macOS (`appnope`, `ptyprocess`) | Instalar los paquetes principales con `python -m pip install pandas numpy matplotlib seaborn scikit-learn scipy ipykernel` |

-------------------------------------------------------------------------------------------

## Obtener los datos

El archivo original `data/raw/04LicitacionesEne.csv` **no está en el repositorio**: contiene el nombre y el RUT de los proveedores, por lo que está excluido en `.gitignore`. Cada integrante lo descarga una vez, después de configurar el entorno:

1. Descarga [04LicitacionesEne.zip desde OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQC4FsRVSA7FQZ_vVtA7HW9gAXYbDcGX6o_MVfe2-Uywd70?e=cu6AXI) con tu cuenta UNAB (acceso solo para el grupo y el docente).
2. Descomprímelo y deja el CSV en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 como se indica en [`data/raw/README.md`](data/raw/README.md).

No abras ni guardes el CSV con Excel: lo reescribe con otro formato y altera el contenido.

-------------------------------------------------------------------------------------------

## Validar el dataset

Desde la raíz del repositorio:
Siempre con el entorno activado (`source .venv/bin/activate` en macOS/Linux o `source .venv/Scripts/activate` en Git Bash para Windows):

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
