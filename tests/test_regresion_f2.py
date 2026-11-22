"""Pruebas de regresión y equivalencia contra F2 mediante pd.testing.assert_frame_equal (Guía S3)."""

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.pipeline_licitaciones import TratamientoFaltantes, construir_pipeline
from src.preprocesamiento import (
    MOTIVOS, aplicar_bandera_atipicos, calcular_brecha, calcular_limites_iqr,
    cargar_csv, convertir_tipos, marcar_duplicados, ordenar_tamano,
    validar_procesado,
)
from tests.conftest import escribir_csv_temporal


def test_assert_frame_equal_f3_contra_f2_oficial(ruta_raw: Path, ruta_processed: Path):
    """Guía S3: Compara la salida del pipeline actual contra las dos entregadas en F2."""
    if not ruta_raw.is_file():
        pytest.skip(f"No se encontró {ruta_raw}: requiere el CSV original de 385 MB para comparar datos completos.")

    pipe = construir_pipeline()
    resultado = pipe.ejecutar(ruta_raw)

    referencias = {
        "ofertas": ruta_processed / "04LicitacionesEne_procesado.csv",
        "licitaciones": ruta_processed / "04LicitacionesEne_brecha_por_licitacion.csv",
    }
    tablas = {"ofertas": resultado.ofertas, "licitaciones": resultado.licitaciones}

    for nombre, tabla in tablas.items():
        ruta_f2 = referencias[nombre]
        referencia = pd.read_csv(
            ruta_f2, sep=";", encoding="utf-8-sig", dtype="string", keep_default_na=False
        )
        exportada = pd.read_csv(
            StringIO(tabla.to_csv(sep=";", index=False)), sep=";", dtype="string", keep_default_na=False
        )
        pd.testing.assert_frame_equal(referencia, exportada, check_exact=True)


def test_assert_frame_equal_pipeline_contra_reglas_f2_sintetico():
    """Guía S3 en datos sintéticos: Compara el pipeline POO contra las funciones F2 paso a paso."""
    filas = [
        # Licitación 1: Ganadora CLP coincide
        {
            "NroLicitacion": "LIC-001",
            "FechaPublicacion": "01-01-2025 10:00",
            "FechaCierre": "05-01-2025 10:00",
            "FechaAdjudicacion": "10-01-2025 10:00",
            "MontoEstimadoLicitacion": "1000",
            "MontoNetoOferta": "1000",
            "MontoTotalOferta": "1000",
            "MonedaLicitacion": "CLP",
            "MonedaOferta": "CLP",
            "TamanoProveedor": "Micro",
            "ResultadoOferta": "Ganadora",
        },
        # Licitación 1: Perdedora
        {
            "NroLicitacion": "LIC-001",
            "FechaPublicacion": "01-01-2025 10:00",
            "FechaCierre": "05-01-2025 10:00",
            "FechaAdjudicacion": "10-01-2025 10:00",
            "MontoEstimadoLicitacion": "1000",
            "MontoNetoOferta": "1200",
            "MontoTotalOferta": "1200",
            "MonedaLicitacion": "CLP",
            "MonedaOferta": "CLP",
            "TamanoProveedor": "Grande",
            "ResultadoOferta": "Perdedora",
        },
        # Licitación 2: Ganadora con brecha (2 ganadoras en Micro y Pequeña)
        {
            "NroLicitacion": "LIC-002",
            "FechaPublicacion": "02-01-2025 11:00",
            "FechaCierre": "06-01-2025 11:00",
            "FechaAdjudicacion": "12-01-2025 11:00",
            "MontoEstimadoLicitacion": "5000",
            "MontoNetoOferta": "2000",
            "MontoTotalOferta": "2000",
            "MonedaLicitacion": "CLP",
            "MonedaOferta": "CLP",
            "TamanoProveedor": "Micro",
            "ResultadoOferta": "Ganadora",
        },
        {
            "NroLicitacion": "LIC-002",
            "FechaPublicacion": "02-01-2025 11:00",
            "FechaCierre": "06-01-2025 11:00",
            "FechaAdjudicacion": "12-01-2025 11:00",
            "MontoEstimadoLicitacion": "5000",
            "MontoNetoOferta": "2500",
            "MontoTotalOferta": "2500",
            "MonedaLicitacion": "CLP",
            "MonedaOferta": "CLP",
            "TamanoProveedor": "Pequeña",
            "ResultadoOferta": "Ganadora",
        },
        # Licitación 3: Moneda extranjera USD
        {
            "NroLicitacion": "LIC-003",
            "FechaPublicacion": "03-01-2025 12:00",
            "FechaCierre": "07-01-2025 12:00",
            "FechaAdjudicacion": "15-01-2025 12:00",
            "MontoEstimadoLicitacion": "100",
            "MontoNetoOferta": "90",
            "MontoTotalOferta": "90",
            "MonedaLicitacion": "USD",
            "MonedaOferta": "USD",
            "TamanoProveedor": "Mediana",
            "ResultadoOferta": "Ganadora",
        },
        # Licitación 4: Ofertas adicionales para tener >= 4 CLP válidas
        {
            "NroLicitacion": "LIC-004",
            "FechaPublicacion": "04-01-2025 13:00",
            "FechaCierre": "08-01-2025 13:00",
            "FechaAdjudicacion": "16-01-2025 13:00",
            "MontoEstimadoLicitacion": "800",
            "MontoNetoOferta": "800",
            "MontoTotalOferta": "800",
            "MonedaLicitacion": "CLP",
            "MonedaOferta": "CLP",
            "TamanoProveedor": "Grande",
            "ResultadoOferta": "Ganadora",
        },
    ]

    with TemporaryDirectory() as carpeta:
        ruta_csv = escribir_csv_temporal(carpeta, filas)

        # 1. Ejecutar pipeline POO de F3
        pipe = construir_pipeline()
        resultado_f3 = pipe.ejecutar(ruta_csv)

        # 2. Ejecutar reglas procedurales de F2 paso a paso
        datos_f2 = cargar_csv(ruta_csv)
        filas_orig = len(datos_f2)
        datos_f2, _ = marcar_duplicados(datos_f2)
        datos_f2, _ = convertir_tipos(datos_f2)
        tf = TratamientoFaltantes(umbral_pct=90.0)
        datos_f2 = tf.ajustar(datos_f2).transformar(datos_f2)
        datos_f2 = ordenar_tamano(datos_f2)
        limites_f2 = calcular_limites_iqr(datos_f2)
        datos_f2 = aplicar_bandera_atipicos(datos_f2, limites_f2)
        licitaciones_f2 = calcular_brecha(datos_f2)

        columnas = [col for col in MOTIVOS if col in datos_f2] + [
            "EsDuplicadoPotencial", "TamanoProveedorOrdinal", "EsExtremoLogIQR_CLP"
        ]
        ofertas_f2 = datos_f2[columnas]
        validar_procesado(ofertas_f2, licitaciones_f2, filas_orig, limites_f2)

        # 3. Comprobar igualdad exacta con assert_frame_equal
        pd.testing.assert_frame_equal(resultado_f3.ofertas, ofertas_f2, check_exact=True)
        pd.testing.assert_frame_equal(resultado_f3.licitaciones, licitaciones_f2, check_exact=True)
