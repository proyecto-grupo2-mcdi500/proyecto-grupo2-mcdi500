# Fase 3

Ubicación para los notebooks y entregables propios de la Fase 3. Los datos y módulos compartidos del proyecto se mantienen en `data/` y `src/` en la raíz.
###
# Fase 3 · Núcleo algorítmico, eficiencia y POO
## Licitaciones públicas de ChileCompra · MCDI500 · Grupo 2

### 1. ¿Qué contiene esta carpeta?
La carpeta `F3/` alberga el notebook analítico y técnico de la tercera fase del proyecto (`F3_Nucleo_Algoritmico.ipynb`), diseñado para estructurar el preprocesamiento de datos bajo un paradigma de Programación Orientada a Objetos (POO), evaluar el rendimiento algorítmico y garantizar robustez frente a casos límite y excepciones.

### 2. Módulos de `src/` utilizados por el notebook
El notebook de F3 importa y coordina directamente los siguientes componentes desarrollados en la carpeta raíz `src/`:
* **`src/preprocesamiento.py`**: Contiene las funciones puras y reglas de negocio heredadas de la Fase 2 (conversión de fechas, normalización de textos, tipado de montos y cálculo de brechas).
* **`src/pipeline_licitaciones.py`**: Implementa el núcleo algorítmico orientado a objetos, incluyendo la clase abstracta `Transformador`, la envoltura `TransformacionFija`, el detector ajustable de valores extremos `ExtremosLogIQR`, el patrón Observer con `Bitacora` y el orquestador `Pipeline`.
* **`src/medicion.py`**: Proveedor de utilidades estandarizadas para medir tiempos mínimos de ejecución (`timeit`) y consumo pico de memoria (`tracemalloc`).
* **`src/pruebas_preprocesamiento.py`**: Validador automático de las reglas funcionales básicas del preprocesamiento.

### 3. Mejoras y características respecto a la Fase 2
* **Arquitectura Modular y POO:** Transición desde scripts y funciones aisladas hacia un diseño basado en clases con contratos explícitos (`fit`/`transform`), encapsulamiento de parámetros aprendidos y desacoplamiento de responsabilidades.
* **Patrón de Diseño (Observer):** Incorporación de una bitácora desacoplada que registra automáticamente el estado y cardinalidad de los datos tras cada paso del pipeline sin alterar la lógica de transformación.
* **Optimización de Rendimiento:** Demostración empírica de la superioridad de enfoques vectorizados frente a iterativos en el control temporal, y del uso del motor nativo en C (`sep=";"`) junto con `usecols` para la lectura eficiente de archivos grandes de datos.
* **Trazabilidad y Pruebas Unitarias:** Cobertura sistemática de escenarios normales, casos límite (datos vacíos, conjuntos mínimos, ausencia de monedas CLP) y manejo explícito de excepciones técnicas.
