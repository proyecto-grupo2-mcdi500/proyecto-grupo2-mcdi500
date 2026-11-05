# proyecto-mcdi500
Proyecto grupal de Programación para la Ciencia de Datos.
Integrantes:    Ernesto Siebert Aguilera
                Oscar Salgado Sanhueza
                Bertgil Gonzalez Olmos
                Daniel Rojas Sánchez

# Análisis de Licitaciones Públicas en Chile (Primer Semestre 2025)
> **Asignatura:** Programación para la Ciencia de Datos (MCDI-500)  
> **Grupo:** 2

-------------------------------------------------------------------------------------------

## Introducción y Contexto

Las licitaciones públicas permiten a las instituciones adquirir bienes y servicios mediante procesos diseñados para promover la transparencia, la eficiencia y la libre competencia. El análisis sistemático de estos registros permite describir el comportamiento de las contrataciones del Estado, identificar tendencias de mercado y detectar posibles anomalías o patrones atípicos que ameriten un análisis más exhaustivo.

En este proyecto se analizan los registros de licitaciones de compras públicas correspondientes al **primer semestre de 2025**, obtenidos desde el portal oficial de datos abiertos:
* **Fuente:** [ChileCompra — Datos Abiertos](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones)

A partir de este conjunto de datos, se examinan variables clave como instituciones compradoras, montos asignados, tipología de licitación, oferentes adjudicados y dispersión de las ofertas. El propósito es identificar patrones sistemáticos y eventuales señales de concentración o sesgo, manteniendo un enfoque exploratorio riguroso donde cualquier hallazgo se evalúe dentro del alcance y las limitaciones intrínsecas de los datos.

-------------------------------------------------------------------------------------------

## Objetivos del Proyecto

* **Objetivo General:** Analizar los procesos de compras y licitaciones públicas durante el 1er semestre de 2025 para describir dinámicas de adjudicación y detectar patrones de concentración o sesgo.
* **Objetivos Específicos:**
  * Limpiar, estructurar y validar el dataset descargado de ChileCompra.
  * Realizar un Análisis Exploratorio de Datos (EDA) sobre montos, rubros e instituciones públicas más activas.
  * Estudiar la distribución de adjudicaciones a proveedores y detectar posibles concentraciones por mercado o sector.
  * Evaluar el impacto de las variables temporales y geográficas en el éxito de las ofertas.

-------------------------------------------------------------------------------------------

## Tecnologías y Librerías

El análisis está implementado principalmente en **Python**:

* **Entorno:** Jupyter Notebook / Python 3.10+
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
│   └── validar_dataset.py
├── F1/
│   ├── brainstorming/
│   │   └── ideas-dataset.md
│   └── test_verification.ipynb
├── F2/
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
- `F1/`: reúne materiales de la primera etapa del proyecto, incluyendo ideas iniciales en `F1/brainstorming/ideas-dataset.md` y el cuaderno de verificación `F1/test_verification.ipynb`.
- `F2/`: contiene el cuaderno `F2/F2_Preprocesamiento.ipynb`, dedicado a la exploración y preprocesamiento de los datos.
- `F3/` y `F4/`: carpetas destinadas a los notebooks y entregables específicos de las etapas posteriores.

Las carpetas de fase (`F1/` a `F4/`) no deben contener copias propias de `data/`, `docs/` ni `src/`. Si una fase genera un archivo reutilizable, se guarda en la ubicación compartida correspondiente; sus notebooks permanecen en la carpeta de la fase.

-------------------------------------------------------------------------------------------

## Validar el dataset

Desde la raíz del repositorio:

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
