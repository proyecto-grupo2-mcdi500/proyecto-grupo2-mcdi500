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
│   │   ├── 04LicitacionesEne_procesado.csv
│   │   └── README.md
│   └── raw/
│       ├── 04LicitacionesEne.csv
│       └── README.md
├── docs/
│   └── README.md
├── src/
│   ├── README.md
│   ├── utilidades.py
│   └── validar_dataset.py
├── F1/
│   ├── brainstorming/
│   │   └── ideas-dataset.md
│   ├── F1_Definicion.ipynb
│   └── test_verification.ipynb
├── F2/
│   ├── F2_Limpieza.ipynb
│   └── F2_Preprocesamiento.ipynb
├── F3/
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
- `validar_dataset.py` y `src/validar_dataset.py`: scripts y módulos reutilizables para revisar y validar archivos de datos entre fases.
- `data/raw/`: contiene los datos originales (`data/raw/04LicitacionesEne.csv`), almacenados en una única ubicación compartida.
- `data/processed/`: carpeta destinada a almacenar los datos derivados y preparados para el análisis.
- `docs/`: documentación compartida del proyecto.
- `F1/`: reúne la definición del problema y el alcance en `F1/F1_Definicion.ipynb`, ideas iniciales en `F1/brainstorming/ideas-dataset.md` y el chequeo del entorno en `F1/test_verification.ipynb`.
- `F2/`: el cuaderno oficial es `F2/F2_Preprocesamiento.ipynb`, dedicado a la exploración y preprocesamiento de los datos; su salida oficial es `data/processed/04LicitacionesEne_procesado.csv`. `F2/F2_Limpieza.ipynb` es complementario y no oficial: agrega columnas de revisión (fechas fuera de orden, montos negativos y atípicos) y, al ejecutarse, genera `data/processed/04LicitacionesEne_limpio.csv`, que no está incluido en el repositorio.
- `F3/` y `F4/`: carpetas destinadas a los notebooks y entregables específicos de las etapas posteriores.

Las carpetas de fase (`F1/` a `F4/`) no deben contener copias propias de `data/`, `docs/` ni `src/`. Si una fase genera un archivo reutilizable, se guarda en la ubicación compartida correspondiente; sus notebooks permanecen en la carpeta de la fase.

-------------------------------------------------------------------------------------------

## Configurar el entorno

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

En JupyterLab, abra `F1/test_verification.ipynb`, seleccione el kernel **Python (grupo2-mcdi500)** y ejecútelo. Debe cumplirse que:

- la ruta del intérprete contiene `.venv`;
- `numpy`, `pandas`, `matplotlib` y `sklearn` muestran su versión (ninguno aparece como `NO DISPONIBLE`).

| Si ocurre | Causa probable | Qué hacer |
| --- | --- | --- |
| El intérprete no contiene `.venv` | Kernel equivocado | *Kernel → Change Kernel* → Python (grupo2-mcdi500) |
| `ModuleNotFoundError` con un paquete instalado | Se instaló fuera del entorno o falta el paso 3 | Activar `.venv` y repetir los pasos 2 y 3 |
| Falla `pip install -r requirements.txt` | Versión de Python distinta | Usar Python 3.12 |

-------------------------------------------------------------------------------------------

## Validar el dataset

Desde la raíz del repositorio:
Siempre con el entorno activado `source .venv/bin/activate`

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
