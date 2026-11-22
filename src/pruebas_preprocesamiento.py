"""Módulo de pruebas migrado a tests/test_preprocesamiento.py.

Se mantiene este archivo con fines de compatibilidad hacia atrás para cuadernos
y scripts que aún importen `ejecutar_pruebas_preprocesamiento` desde `src.pruebas_preprocesamiento`.
La suite oficial se ejecuta mediante `pytest` en la raíz del proyecto.
"""

from tests.test_preprocesamiento import ejecutar_pruebas_preprocesamiento

__all__ = ["ejecutar_pruebas_preprocesamiento"]

if __name__ == "__main__":
    ejecutar_pruebas_preprocesamiento()
