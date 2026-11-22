"""Pruebas de regresión y equivalencia contra F2 mediante pd.testing.assert_frame_equal (Guía S3).

Según el archivo que haya en data/raw/04LicitacionesEne.csv (ver data/raw/README.md):

- copia del proyecto (Opción A): igualdad exacta con las salidas versionadas de F2;
- archivo público de Mercado Público (Opción B): equivalencia de las cifras del análisis
  (decisión 19 en docs/decisiones.md);
- sin archivo u otro archivo: ambas pruebas se omiten con un mensaje.
"""

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pytest

from src.pipeline_licitaciones import TratamientoFaltantes, construir_pipeline
from src.preprocesamiento import (
    MOTIVOS, aplicar_bandera_atipicos, calcular_brecha, calcular_limites_iqr,
    cargar_csv, convertir_tipos, identificar_raw, marcar_duplicados, ordenar_tamano,
    validar_procesado,
)
from tests.conftest import escribir_csv_temporal


def test_assert_frame_equal_f3_contra_f2_oficial(ruta_raw: Path, ruta_processed: Path):
    """Guía S3: Compara la salida del pipeline actual contra las dos entregadas en F2."""
    tipo = identificar_raw(ruta_raw)
    if tipo != "proyecto":
        pytest.skip(
            f"data/raw/04LicitacionesEne.csv es '{tipo}': la igualdad exacta con F2 requiere la copia "
            "del proyecto (Opción A en data/raw/README.md)."
        )

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


def _exportar_como_f2(tabla: pd.DataFrame) -> pd.DataFrame:
    """Devuelve la tabla tal como quedaría al exportarla y releerla igual que en F2."""
    return pd.read_csv(
        StringIO(tabla.to_csv(sep=";", index=False)), sep=";", dtype="string", keep_default_na=False
    )


def test_fuente_publica_entrega_las_mismas_cifras(ruta_raw: Path, ruta_processed: Path):
    """Decisión 19: el archivo público de Mercado Público entrega las mismas cifras del análisis.

    La copia del proyecto se obtuvo del archivo público quitando Proveedor y ProveedorRUT en
    Excel, que además redondeó algunos montos y quitó los segundos a las fechas. Esta prueba
    pasa el archivo público por el mismo pipeline y comprueba que:

    - la tabla por licitación es idéntica salvo MontoTotalGanadoras en 7 licitaciones
      (diferencias relativas menores a 1e-9) y BrechaMonto en esas mismas licitaciones
      (diferencias menores a 0,01 en la moneda de la licitación);
    - se mantienen las 2.257 licitaciones comparables y las 1.254 coincidencias;
    - la tabla por oferta es idéntica salvo montos (diferencias relativas menores a 1e-9) y las
      tres fechas. Las fechas del archivo público incluyen segundos (11:07:00), formato que el
      lector actual no interpreta; no intervienen en la brecha (trabajo futuro, decisión 19).
    """
    tipo = identificar_raw(ruta_raw)
    if tipo != "publico":
        pytest.skip(
            f"data/raw/04LicitacionesEne.csv es '{tipo}': esta prueba se ejecuta con el archivo "
            "público de Mercado Público (Opción B en data/raw/README.md)."
        )

    resultado = construir_pipeline().ejecutar(ruta_raw)
    pares = {
        "licitaciones": (
            "04LicitacionesEne_brecha_por_licitacion.csv", resultado.licitaciones,
            {"MontoTotalGanadoras": (1e-9, 0.0), "BrechaMonto": (0.0, 0.01)}, (),
        ),
        "ofertas": (
            "04LicitacionesEne_procesado.csv", resultado.ofertas,
            {"MontoTotalOferta": (1e-9, 0.0), "MontoNetoOferta": (1e-9, 0.0)},
            ("FechaPublicacion", "FechaCierre", "FechaAdjudicacion"),
        ),
    }
    for nombre, (archivo, tabla, montos, fechas) in pares.items():
        referencia = pd.read_csv(
            ruta_processed / archivo, sep=";", encoding="utf-8-sig", dtype="string",
            keep_default_na=False,
        )
        publica = _exportar_como_f2(tabla)
        assert list(publica.columns) == list(referencia.columns), nombre

        exactas = [c for c in referencia.columns if c not in (*montos, *fechas)]
        pd.testing.assert_frame_equal(publica[exactas], referencia[exactas], check_exact=True)
        for columna, (rtol, atol) in montos.items():
            ref = pd.to_numeric(referencia[columna].replace("", np.nan))
            pub = pd.to_numeric(publica[columna].replace("", np.nan))
            assert ref.isna().equals(pub.isna()), (nombre, columna)
            assert np.allclose(pub, ref, rtol=rtol, atol=atol, equal_nan=True), (nombre, columna)

    licitaciones = _exportar_como_f2(resultado.licitaciones)
    referencia = pd.read_csv(
        ruta_processed / "04LicitacionesEne_brecha_por_licitacion.csv", sep=";",
        encoding="utf-8-sig", dtype="string", keep_default_na=False,
    )
    distintas = licitaciones["MontoTotalGanadoras"].ne(referencia["MontoTotalGanadoras"])
    assert int(distintas.sum()) == 7
    assert not licitaciones["BrechaMonto"].ne(referencia["BrechaMonto"])[~distintas].any()
    comparables = licitaciones["EstadoBrecha"].eq("Calculada")
    assert int(comparables.sum()) == 2257
    assert int((comparables & licitaciones["CoincideConEstimado"].eq("True")).sum()) == 1254


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
