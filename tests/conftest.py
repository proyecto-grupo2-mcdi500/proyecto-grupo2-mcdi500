"""Configuración global y fixtures compartidas para la suite de pruebas con pytest."""

from pathlib import Path
import sys
from typing import Any

import pandas as pd
import pytest

# Asegurar que la raíz del proyecto esté en sys.path para importar src/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def ruta_raiz() -> Path:
    """Devuelve la ruta raíz del repositorio."""
    return ROOT


@pytest.fixture(scope="session")
def ruta_processed(ruta_raiz: Path) -> Path:
    """Devuelve la ruta a la carpeta data/processed."""
    return ruta_raiz / "data" / "processed"


@pytest.fixture(scope="session")
def ruta_raw(ruta_raiz: Path) -> Path:
    """Devuelve la ruta al archivo crudo en data/raw."""
    return ruta_raiz / "data" / "raw" / "04LicitacionesEne.csv"


@pytest.fixture(scope="session")
def ruta_hallazgos_f4(ruta_raiz: Path) -> Path:
    """Devuelve la ruta a docs/hallazgos_f4.csv."""
    return ruta_raiz / "docs" / "hallazgos_f4.csv"


@pytest.fixture(scope="session")
def ruta_metadatos_f4(ruta_raiz: Path) -> Path:
    """Devuelve la ruta a docs/metadatos_f4.json."""
    return ruta_raiz / "docs" / "metadatos_f4.json"


def crear_filas_ficticias(
    cantidad: int = 6,
    moneda_oferta: str = "CLP",
    moneda_lic: str = "CLP",
    nro_prefijo: str = "LIC",
    resultado_oferta: str = "Ganadora",
    tamano_proveedor: str = "Micro",
    monto_estimado: str = "1000",
    monto_base_oferta: int = 500,
) -> list[dict[str, str]]:
    """Construye filas sintéticas válidas que cumplen REQUERIDAS de cargar_csv."""
    base = {
        "NroLicitacion": f"{nro_prefijo}-001",
        "FechaPublicacion": "01-01-2025 10:00",
        "FechaCierre": "05-01-2025 10:00",
        "FechaAdjudicacion": "10-01-2025 10:00",
        "MontoEstimadoLicitacion": str(monto_estimado),
        "MontoNetoOferta": str(monto_base_oferta),
        "MontoTotalOferta": str(monto_base_oferta),
        "MonedaLicitacion": moneda_lic,
        "MonedaOferta": moneda_oferta,
        "TamanoProveedor": tamano_proveedor,
        "ResultadoOferta": resultado_oferta,
    }
    return [{**base, "MontoTotalOferta": str(monto_base_oferta + i)} for i in range(cantidad)]


def escribir_csv_temporal(carpeta: Path | str, filas: list[dict[str, Any]]) -> Path:
    """Escribe un CSV de prueba con delimitador ';' y codificación 'latin-1'."""
    ruta = Path(carpeta) / "licitaciones_prueba.csv"
    pd.DataFrame(filas).to_csv(ruta, sep=";", encoding="latin-1", index=False)
    return ruta
