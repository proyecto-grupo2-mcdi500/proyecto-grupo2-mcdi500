# Fase 3 · Núcleo algorítmico, eficiencia y POO
## Licitaciones públicas de ChileCompra · MCDI500 · Grupo 2

### 1. ¿Qué contiene esta carpeta?
La carpeta `F3/` contiene el notebook de la tercera fase del proyecto, `F3_Nucleo_Algoritmico.ipynb`. Organiza el preprocesamiento de F2 en un pipeline orientado a objetos (POO), comprueba que reproduce las salidas de F2, mide el rendimiento de dos decisiones del código y valida las clases en casos normales, límite y de excepción.

Los datos y módulos compartidos del proyecto se mantienen en `data/` y `src/`, en la raíz del repositorio.

### 2. Cómo ejecutarlo
1. Descarga el archivo de entrada en `data/raw/04LicitacionesEne.csv` (ver *Obtener los datos* en el [`README.md`](../README.md) de la raíz).
2. Ejecuta `F2/F2_Preprocesamiento.ipynb`: genera las dos salidas de `data/processed/` que F3 usa como referencia.
3. Abre `F3_Nucleo_Algoritmico.ipynb` con el kernel **Python (grupo2-mcdi500)** y ejecuta todas las celdas con *Restart Kernel and Run All Cells* (unos 20 segundos).

F3 escribe `data/processed/diccionario_f3.csv` y `data/processed/parametros_f3.csv`.

### 3. Módulos de `src/` utilizados por el notebook
* **`src/preprocesamiento.py`**: reglas del preprocesamiento heredadas de la Fase 2: carga, conversión de fechas y montos, faltantes, duplicados potenciales, cálculo de la brecha, IQR y validación.
* **`src/pipeline_licitaciones.py`**: núcleo algorítmico orientado a objetos: la clase abstracta `Transformador`, la envoltura `TransformacionFija`, el detector ajustable de valores extremos `ExtremosLogIQR`, el orquestador `Pipeline` y la `Bitacora` del patrón Observer.
* **`src/medicion.py`**: medición del tiempo mínimo de ejecución (`timeit`) y de la memoria pico (`tracemalloc`).
* **`src/pruebas_preprocesamiento.py`**: pruebas automáticas de las reglas de preprocesamiento con datos ficticios.

### 4. Mejoras respecto de la Fase 2
* **Arquitectura modular y POO:** las reglas pasan de celdas y funciones sueltas a clases con un contrato común (`transformar`; `ajustar` en las que aprenden de los datos) y con los parámetros aprendidos encapsulados.
* **Patrón de diseño Observer:** la bitácora registra la cantidad de filas tras cada paso del pipeline sin que el pipeline sepa quién la escucha.
* **Optimización del rendimiento:** la medición mostró que el control de fechas vectorizado es más rápido que el iterativo y que leer con `sep=";"` (motor C) es más rápido y usa menos memoria que detectar el separador. `usecols` reduce aún más el costo cuando se necesitan pocas columnas.
* **Trazabilidad y pruebas:** la sección 7 prueba las clases en escenarios normales, casos límite (una fila, conjuntos vacíos, sin ofertas en CLP) y excepciones (transformar antes de ajustar, columna ausente, archivo inexistente).
