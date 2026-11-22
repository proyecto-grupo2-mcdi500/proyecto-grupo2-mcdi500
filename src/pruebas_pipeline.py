"""Módulo de pruebas migrado a tests/test_pipeline.py.

Se mantiene este archivo con fines de compatibilidad hacia atrás para cuadernos
y scripts que aún importen `ejecutar_pruebas_pipeline` desde `src.pruebas_pipeline`.
La suite oficial se ejecuta mediante `pytest` en la raíz del proyecto.
"""

from tests.test_pipeline import ejecutar_pruebas_pipeline

__all__ = ["ejecutar_pruebas_pipeline"]

if __name__ == "__main__":
    ejecutar_pruebas_pipeline()
