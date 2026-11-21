"""Pruebas con resultados esperados para el preprocesamiento de F2."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from .preprocesamiento import (
    SHA256_RAW_LF, aplicar_bandera_atipicos, calcular_brecha, calcular_limites_iqr,
    calcular_sha256_sin_cr, cargar_csv, marcar_duplicados, ordenar_tamano,
    verificar_hash_raw,
)


def ejecutar_pruebas_preprocesamiento() -> None:
    """Construye datos ficticios y comprueba los casos normales, límite y de error."""
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
    filas, duplicados = marcar_duplicados(filas)
    r = calcular_brecha(filas).set_index("NroLicitacion")
    assert len(r) == 10 and r.index.is_unique
    assert r.loc["A", "BrechaMonto"] == 20
    assert r.loc["B", "MontoTotalGanadoras"] == 100
    assert r.loc["B", "BrechaMonto"] == 0 and r.loc["B", "CoincideConEstimado"]
    assert r.loc[list("CDEFGHJ"), "BrechaMonto"].isna().all()
    assert r.loc["H", "EstadoBrecha"] == "Ganadora con monto inválido"
    assert r.loc["I", "GanadoraDuplicada"] and r.loc["I", "MontoTotalGanadoras"] == 100
    assert duplicados["FilasAdicionales"].sum() == 1

    tallas = ordenar_tamano(pd.DataFrame({"TamanoProveedor": ["Grande", "NoClasificado"]}))
    assert tallas.loc[0, "TamanoProveedorOrdinal"] == "Grande"
    assert pd.isna(tallas.loc[1, "TamanoProveedorOrdinal"])
    try:
        ordenar_tamano(pd.DataFrame({"TamanoProveedor": ["Extra"]}))
    except ValueError as error:
        assert "Extra" in str(error)
    else:
        raise AssertionError("Faltó rechazar una categoría desconocida.")

    with TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "entrada.csv"
        ruta.write_text("NroLicitacion;MonedaOferta\nA;CLP\n")
        try:
            cargar_csv(ruta)
        except ValueError as error:
            assert "ResultadoOferta" in str(error)
        else:
            raise AssertionError("Faltó rechazar una columna requerida ausente.")

    ofertas = pd.DataFrame({
        "MonedaOferta": ["CLP"] * 7 + ["USD"],
        "MontoTotalOferta": [1, 100, 100, 100, 100, 10000, 0, 100000],
    })
    limites = calcular_limites_iqr(ofertas)
    bandera = aplicar_bandera_atipicos(ofertas, limites)["EsExtremoLogIQR_CLP"]
    assert bandera.iloc[:6].tolist() == [True, False, False, False, False, True]
    assert bandera.iloc[6:].isna().all()

    with TemporaryDirectory() as carpeta:
        ruta_crlf = Path(carpeta) / "crlf.csv"
        ruta_lf = Path(carpeta) / "lf.csv"
        ruta_crlf.write_bytes(b"a;b\r\n1;2\r\n")
        ruta_lf.write_bytes(b"a;b\n1;2\n")
        hash_crlf = calcular_sha256_sin_cr(ruta_crlf)
        hash_lf = calcular_sha256_sin_cr(ruta_lf)
        assert hash_crlf == hash_lf
        assert verificar_hash_raw(ruta_crlf, hash_esperado=hash_lf) == hash_lf

        try:
            verificar_hash_raw(Path(carpeta) / "no_existe.csv")
        except FileNotFoundError as error:
            assert "ChileCompra" in str(error) and SHA256_RAW_LF in str(error)
        else:
            raise AssertionError("Faltó lanzar FileNotFoundError con instrucciones.")

        try:
            verificar_hash_raw(ruta_lf)
        except ValueError as error:
            assert SHA256_RAW_LF in str(error) and "data/raw/README.md" in str(error)
        else:
            raise AssertionError("Faltó rechazar un SHA-256 distinto al esperado.")
