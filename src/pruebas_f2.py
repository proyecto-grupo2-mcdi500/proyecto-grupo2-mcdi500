"""Pruebas con resultados esperados para el preprocesamiento de F2."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from .funciones_f2_revision import (
    aplicar_bandera_atipicos, calcular_brecha, calcular_limites_iqr, cargar_csv,
    marcar_duplicados, ordenar_tamano,
)


def ejecutar_pruebas_f2() -> None:
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
