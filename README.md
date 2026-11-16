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
│   ├── medicion.py
│   ├── pipeline_licitaciones.py
│   ├── preprocesamiento.py
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
- `src/`: módulos compartidos organizados para la Fase 3:
  - `preprocesamiento.py`: reglas de F2 y funciones base de transformación.
  - `pipeline_licitaciones.py`: clases del núcleo algorítmico y orquestación POO (`Transformador`, `Pipeline`, `Bitacora`, `ExtremosLogIQR`).
  - `medicion.py`: utilidades de medición de tiempo y memoria (`timeit` / `tracemalloc`).
  - `pruebas_preprocesamiento.py`: validador de reglas de F2.
  - `utilidades.py` y `validar_dataset.py`: soporte y validación general.
- `validar_dataset.py` y `src/validar_dataset.py`: scripts y módulos reutilizables para revisar y validar archivos de datos entre fases.
- `data/raw/`: ubicación local de los datos originales (`data/raw/04LicitacionesEne.csv`). El archivo no se versiona porque contiene datos personales; ver *Obtener los datos*.
- `data/processed/`: carpeta destinada a almacenar los datos derivados y preparados para el análisis.
- `docs/`: documentación compartida del proyecto.
- `F1/`: reúne en `F1/F1_Definicion.ipynb` la definición del problema, el alcance y la verificación del entorno.
- `F2/`: el cuaderno oficial es `F2/F2_Preprocesamiento.ipynb`.
- `F3/`: contiene `F3/F3_Nucleo_Algoritmico.ipynb` y su respectivo `README.md`.

Las carpetas de fase (`F1/` a `F4/`) no deben contener copias propias de `data/`, `docs/` ni `src/`.

-------------------------------------------------------------------------------------------

## Configurar el entorno
-------------------------------------------------------------------------------------------
### macOS / Linux

Estos pasos se hacen **una vez por computador**, desde la terminal y en la raíz del repositorio (en la rama de trabajo).

### 1. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
```

### 2. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check              # debe indicar: No broken requirements found
```

### 3. Registrar el kernel del proyecto

```bash
python -m ipykernel install --user --name grupo2_mcdi500 --display-name "Python (grupo2-mcdi500)"
```

### 4. Abrir JupyterLab

```bash
python -m jupyter lab
```

-------------------------------------------------------------------------------------------
### Windows

Estos pasos se realizan desde **Git Bash** o la terminal integrada de **VS Code**:

### 1. Crear y activar el entorno virtual

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows (Git Bash)
```

### 2. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check              # debe indicar: No broken requirements found
```

### 3. Registrar el kernel del proyecto

```bash
python -m ipykernel install --user --name grupo2_mcdi500 --display-name "Python (grupo2-mcdi500)"
```

-------------------------------------------------------------------------------------------

## Ejecutar los notebooks

El proyecto se ejecuta de forma secuencial a través de tres fases metodológicas. Asegúrate de activar tu entorno virtual (`.venv`) y utilizar el kernel correspondiente en Jupyter (`Python (grupo2-mcdi500)`).

| Fase y Notebook | Qué genera / Objetivo | Tiempo aproximado |
| :--- | :--- | :--- |
| **F1** (`F1/F1_Definicion.ipynb`) | Análisis exploratorio inicial, definición del problema, validación del entorno y diagnóstico de calidad de datos. | ~2 - 3 minutos |
| **F2** (`F2/F2_Preprocesamiento.ipynb`) | Limpieza de datos, tipado, reglas funcionales de transformación y exportación de las dos salidas oficiales en `data/processed/`. | ~3 - 5 minutos |
| **F3** (`F3/F3_Nucleo_Algoritmico.ipynb`) | Núcleo algorítmico orientado a objetos (`src/`), pipeline con patrón Observer, medición de eficiencia (tiempo/memoria) y pruebas unitarias. | ~2 - 4 minutos |

> **Nota:** Recuerda colocar el archivo de entrada original en `data/raw/04LicitacionesEne.csv` antes de iniciar la ejecución de F1 y F2.

-------------------------------------------------------------------------------------------

## Obtener los datos

El archivo de entrada `data/raw/04LicitacionesEne.csv` no está en el repositorio. Cada integrante lo descarga una vez:

1. Descarga [04LicitacionesEne.zip desde OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) con tu cuenta UNAB.
2. Descomprímelo y deja el CSV en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 como se indica en [`data/raw/README.md`](data/raw/README.md).

-------------------------------------------------------------------------------------------

## Validar el dataset

Desde la raíz del repositorio, con el entorno activado:

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
