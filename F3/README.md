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
* **`src/pipeline_licitaciones.py`**: núcleo algorítmico orientado a objetos: la clase abstracta `Transformador`, la envoltura `TransformacionFija`, el tratamiento ajustable de faltantes `TratamientoFaltantes`, el detector ajustable de valores extremos `ExtremosLogIQR`, el orquestador `Pipeline` y la `Bitacora` del patrón Observer.
* **`src/medicion.py`**: medición del tiempo mínimo de ejecución (`timeit`) y de la memoria pico (`tracemalloc`).
* **`src/pruebas_preprocesamiento.py`**: pruebas automáticas de las reglas de preprocesamiento con datos ficticios.
* **`src/pruebas_pipeline.py`**: pruebas automáticas de las clases del pipeline POO (`Transformador`, `TransformacionFija`, `TratamientoFaltantes`, `ExtremosLogIQR`, `Bitacora`, `Pipeline` y `ResultadoF3`) y de `validar_procesado()` con datos ficticios (16 casos: normales, límite y de excepción).

### 4. Mejoras respecto de la Fase 2
* **Arquitectura modular y POO:** las reglas pasan de celdas y funciones sueltas a clases con un contrato común (`ajustar` y luego `transformar` en todos los pasos) y con los parámetros aprendidos encapsulados.
* **Patrón de diseño Observer:** la sección 8 documenta su función en la arquitectura y muestra la tabla emitida por `Bitacora`, que registra conteos tras cada paso del pipeline sin exponer datos originales ni acoplar la auditoría a `Pipeline`.
* **División funcional frente a recursividad (Decisión 0.5):** la sección 9 verifica `suma_recursiva(valores, i=0)` en `100` ofertas, captura `RecursionError` frente a `sys.getrecursionlimit()` sobre las `45.741` filas y compara el costo con `900` filas frente a la suma vectorizada.
* **Optimización del rendimiento:** la medición mostró que el control de fechas vectorizado es más rápido que el iterativo y que leer con `sep=";"` (motor C) es más rápido y usa menos memoria que detectar el separador. `usecols` reduce aún más el costo cuando se necesitan pocas columnas.
* **Trazabilidad y pruebas:** la sección 7 ejecuta `src/pruebas_pipeline.py` para probar las clases en escenarios normales, casos límite (una fila, conjuntos vacíos, sin ofertas en CLP) y excepciones (transformar antes de ajustar, columna ausente, archivo inexistente).
* **Integración formativa y cierre a la Fase 4:** el avance formativo (scripts y mediciones de complejidad) se integró dentro de F3 en `src/medicion.py` y la sección 4; la sección 10 consolida la evolución desde F2, los resultados verificados y la proyección hacia la Fase 4.
