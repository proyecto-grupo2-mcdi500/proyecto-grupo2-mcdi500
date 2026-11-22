"""Pruebas unitarias con pytest para las reglas de preprocesamiento de F2."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.preprocesamiento import (
    SHA256_RAW_LF, aplicar_bandera_atipicos, calcular_brecha, calcular_limites_iqr,
    calcular_sha256_sin_cr, cargar_csv, marcar_duplicados, ordenar_tamano,
    verificar_hash_raw,
)


def test_marcar_duplicados_y_calcular_brecha():
    """Verifica detección de duplicados, cálculo de brecha y estados de adjudicación."""
    filas = pd.DataFrame([
        ("A", "Ganadora", 120, 100, "CLP", "CLP"),
        ("B", "Ganadora", 30, 100, "CLP", "CLP"),
        ("B", "Ganadora", 70, 100, "CLP", "CLP"),
        ("B", "Perdedora", 500, 100, "USD", "CLP"),
        ("C", "Ganadora", 0, 100, "CLP", "CLP"),
        ("D", "Ganadora", 100, 0, "CLP", "CLP"),
        ("E", "Ganadora", 100, 100, "USD", "CLP"),
        ("F", "Perdedora", 100, 100, "CLP", "CLP"),
        ("G", "Ganadora", 50, 100, "CLP", "CLP"),
        ("G", "Ganadora", 50, 120, "CLP", "CLP"),
        ("H", "Ganadora", 50, 100, "CLP", "CLP"),
        ("H", "Ganadora", None, 100, "CLP", "CLP"),
        ("I", "Ganadora", 50, 100, "CLP", "CLP"),
        ("I", "Ganadora", 50, 100, "CLP", "CLP"),
        ("J", "Ganadora", 50, 100, "CLP", "CLP"),
        ("J", None, 50, 100, "CLP", "CLP"),
    ], columns=[
        "NroLicitacion", "ResultadoOferta", "MontoTotalOferta",
        "MontoEstimadoLicitacion", "MonedaOferta", "MonedaLicitacion",
    ])
    filas_marcadas, duplicados = marcar_duplicados(filas)
    r = calcular_brecha(filas_marcadas).set_index("NroLicitacion")

    assert len(r) == 10 and r.index.is_unique
    assert r.loc["A", "BrechaMonto"] == 20
    assert r.loc["B", "MontoTotalGanadoras"] == 100
    assert r.loc["B", "BrechaMonto"] == 0 and r.loc["B", "CoincideConEstimado"]
    assert r.loc[list("CDEFGHJ"), "BrechaMonto"].isna().all()
    assert r.loc["H", "EstadoBrecha"] == "Ganadora con monto inválido"
    assert r.loc["I", "GanadoraDuplicada"] and r.loc["I", "MontoTotalGanadoras"] == 100
    assert duplicados["FilasAdicionales"].sum() == 1


def test_ordenar_tamano_proveedor():
    """Comprueba la escala ordinal de tamaño y el rechazo de etiquetas desconocidas."""
    tallas = ordenar_tamano(pd.DataFrame({"TamanoProveedor": ["Grande", "NoClasificado"]}))
    assert tallas.loc[0, "TamanoProveedorOrdinal"] == "Grande"
    assert pd.isna(tallas.loc[1, "TamanoProveedorOrdinal"])

    with pytest.raises(ValueError, match="Extra"):
        ordenar_tamano(pd.DataFrame({"TamanoProveedor": ["Extra"]}))


def test_cargar_csv_esquema_invalido():
    """Valida que cargar_csv rechace archivos que carecen de columnas requeridas."""
    with TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "entrada.csv"
        ruta.write_text("NroLicitacion;MonedaOferta\nA;CLP\n", encoding="latin-1")
        with pytest.raises(ValueError, match="ResultadoOferta"):
            cargar_csv(ruta)


def test_limites_iqr_y_bandera_atipicos():
    """Comprueba el cálculo de cuartiles log-IQR y la asignación de bandera atípica."""
    ofertas = pd.DataFrame({
        "MonedaOferta": ["CLP"] * 7 + ["USD"],
        "MontoTotalOferta": [1, 100, 100, 100, 100, 10000, 0, 100000],
    })
    limites = calcular_limites_iqr(ofertas)
    assert limites is not None
    assert limites["ofertas_validas"] == 6

    bandera = aplicar_bandera_atipicos(ofertas, limites)["EsExtremoLogIQR_CLP"]
    assert bandera.iloc[:6].tolist() == [True, False, False, False, False, True]
    assert bandera.iloc[6:].isna().all()


def test_verificar_hash_raw_crlf_lf_y_errores():
    """Verifica equivalencia de hash entre CRLF y LF y manejo de excepciones."""
    with TemporaryDirectory() as carpeta:
        ruta_crlf = Path(carpeta) / "crlf.csv"
        ruta_lf = Path(carpeta) / "lf.csv"
        ruta_crlf.write_bytes(b"a;b\r\n1;2\r\n")
        ruta_lf.write_bytes(b"a;b\n1;2\n")

        hash_crlf = calcular_sha256_sin_cr(ruta_crlf)
        hash_lf = calcular_sha256_sin_cr(ruta_lf)
        assert hash_crlf == hash_lf
        assert verificar_hash_raw(ruta_crlf, hash_esperado=hash_lf) == hash_lf

        with pytest.raises(FileNotFoundError, match="ChileCompra") as falta:
            verificar_hash_raw(Path(carpeta) / "no_existe.csv")
        assert SHA256_RAW_LF in str(falta.value)

        with pytest.raises(ValueError, match="data/raw/README.md") as distinto:
            verificar_hash_raw(ruta_lf)
        assert SHA256_RAW_LF in str(distinto.value)


def ejecutar_pruebas_preprocesamiento() -> None:
    """Función de compatibilidad directa para ejecutar las pruebas sin runner de pytest."""
    test_marcar_duplicados_y_calcular_brecha()
    test_ordenar_tamano_proveedor()
    test_cargar_csv_esquema_invalido()
    test_limites_iqr_y_bandera_atipicos()
    test_verificar_hash_raw_crlf_lf_y_errores()
