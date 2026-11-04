# Proyecto MCDI500

Proyecto grupal de Programación para la Ciencia de Datos.

## Estructura

- `data/raw/`: datos originales, almacenados una sola vez.
- `data/processed/`: datos derivados y preparados para el análisis.
- `docs/`: documentación compartida del proyecto.
- `src/`: funciones y módulos reutilizables entre fases.
- `F1/` a `F4/`: notebooks y entregables específicos de cada fase.

Las carpetas de fase no deben contener copias propias de `data/`, `docs/` ni `src/`. Si una fase genera un archivo reutilizable, se guarda en la ubicación compartida correspondiente; sus notebooks permanecen en la carpeta de la fase.

## Validar el dataset

Desde la raíz del repositorio:

```bash
python validar_dataset.py data/raw/04LicitacionesEne.csv --sep ";" --encoding latin-1
```
