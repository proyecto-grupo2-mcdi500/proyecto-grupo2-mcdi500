"""Pruebas unitarias de F4 y de casos nuevos derivados del feedback."""

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pytest

from src.comunicacion import (
    ORDEN_TAMANO, asignar_tamano_ganador, asignar_tamano_ganador_iterativo,
    calcular_medianas_iqr, cargar_artefactos, construir_copia_graficar,
    graficar_cajas_brecha_relativa, graficar_razon_escala_log,
    intervalo_wilson, preparar_comparables, pruebas_por_tamano,
    resumen_magnitud_por_moneda, resumen_sentido_por_moneda,
    sensibilidad_iva, tabla_control_confusion, tabla_resumen_por_tamano,
    tasa_por_grupo,
)
from src.pipeline_licitaciones import ExtremosLogIQR


# ============================================================================
# CASOS CONOCIDOS DE F4 (Validación contra artefactos oficiales)
# ============================================================================

def test_casos_conocidos_f4_dimensiones_artefactos(ruta_processed: Path):
    """Verifica dimensiones exactas de los 4 artefactos procesados oficiales."""
    artefactos = cargar_artefactos(ruta_processed)
    assert len(artefactos.ofertas) == 45741
    assert len(artefactos.licitaciones) == 2292
    assert len(artefactos.diccionario) == 41
    assert len(artefactos.parametros) == 8


def test_casos_conocidos_f4_indicadores_globales_y_clp(ruta_processed: Path):
    """Valida los hallazgos de F4 documentados en docs/hallazgos_f4.csv."""
    artefactos = cargar_artefactos(ruta_processed)
    comp = preparar_comparables(artefactos.licitaciones)

    # 1. Total comparables y coincidencia global (OE1)
    assert len(comp) == 2257
    n_coincide = int(comp["CoincideConEstimado"].astype(bool).sum())
    assert n_coincide == 1254
    pct_coincide = (n_coincide / len(comp)) * 100.0
    assert pytest.approx(pct_coincide, abs=0.01) == 55.56

    ic_inf, ic_sup = intervalo_wilson(n_coincide, len(comp))
    assert pytest.approx(ic_inf * 100.0, abs=0.01) == 53.50
    assert pytest.approx(ic_sup * 100.0, abs=0.01) == 57.60

    # 2. Desglose por moneda (OE2)
    res_moneda = resumen_sentido_por_moneda(comp).set_index("MonedaLicitacion")
    assert "CLP" in res_moneda.index
    clp = res_moneda.loc["CLP"]
    assert clp["Licitaciones"] == 2230
    assert clp["Coincide"] == 1252
    assert clp["BajoEstimado"] == 520
    assert clp["SobreEstimado"] == 458
    assert pytest.approx(clp["CoincidePct"], abs=0.01) == 56.14

    # 3. Ventana de compatibilidad con IVA 19 %
    evidencia_iva, _ = sensibilidad_iva(comp)
    assert evidencia_iva.loc[evidencia_iva["MonedaLicitacion"] == "CLP", "CercaIVA"].iloc[0] == 228


def test_casos_conocidos_f4_tasas_por_tamano(ruta_processed: Path):
    """Verifica tasas de coincidencia y brechas relativas por tamaño ganador (OE3)."""
    artefactos = cargar_artefactos(ruta_processed)
    comp_tamano = asignar_tamano_ganador(preparar_comparables(artefactos.licitaciones), artefactos.ofertas)
    # OE3 evalúa la tasa global por tamaño en todas las comparables (moneda=None) tal como en F4
    tabla = tabla_resumen_por_tamano(comp_tamano, moneda=None).set_index("TamanoGanador")

    esperados = {
        "Micro": {"Licitaciones": 405, "Tasa": 71.11, "BrechaRelPct": 0.0},
        "Pequeña": {"Licitaciones": 690, "Tasa": 62.32, "BrechaRelPct": 0.0},
        "Mediana": {"Licitaciones": 273, "Tasa": 58.97, "BrechaRelPct": 0.0},
        "Grande": {"Licitaciones": 365, "Tasa": 49.04, "BrechaRelPct": 0.0},
        "NoClasificado": {"Licitaciones": 284, "Tasa": 63.03, "BrechaRelPct": 0.0},
        "Múltiple": {"Licitaciones": 240, "Tasa": 7.08, "BrechaRelPct": 151.16},
    }
    for tamano, vals in esperados.items():
        assert tamano in tabla.index
        assert tabla.loc[tamano, "Licitaciones"] == vals["Licitaciones"]
        assert pytest.approx(tabla.loc[tamano, "TasaCoincidenciaPct"], abs=0.01) == vals["Tasa"]
        # La mediana de la brecha relativa equivale a (mediana de la razón - 1) × 100.
        brecha_rel = (tabla.loc[tamano, "MedianaRazon"] - 1.0) * 100.0
        assert pytest.approx(brecha_rel, abs=0.01) == vals["BrechaRelPct"]


def test_casos_conocidos_f4_coinciden_con_hallazgos_csv(ruta_processed: Path, ruta_hallazgos_f4: Path):
    """Recalcula desde src/ las cifras de OE1, OE2 y OE3 exportadas por F4 en docs/hallazgos_f4.csv.

    Si alguien cambia el notebook y no el módulo (o al revés), esta prueba falla.
    """
    hallazgos = pd.read_csv(ruta_hallazgos_f4, sep=";", encoding="utf-8-sig").set_index("Id")
    artefactos = cargar_artefactos(ruta_processed)
    comp = preparar_comparables(artefactos.licitaciones)

    def esperado(id_hallazgo: str) -> tuple[float, int]:
        fila = hallazgos.loc[id_hallazgo]
        return float(fila["Valor"]), int(fila["N"])

    # OE1: comparables y coincidencia global
    assert esperado("OE1_comparables") == (len(comp), len(artefactos.licitaciones))
    n_coincide = int(comp["CoincideConEstimado"].astype(bool).sum())
    assert esperado("OE1_coincidencia_n") == (n_coincide, len(comp))
    valor, n = esperado("OE1_coincidencia_pct")
    assert n == len(comp) and pytest.approx(100.0 * n_coincide / len(comp), abs=0.005) == valor

    # OE2: coincidencia por moneda y ventana compatible con IVA en CLP
    por_moneda = resumen_sentido_por_moneda(comp).set_index("MonedaLicitacion")
    for moneda, fila in por_moneda.iterrows():
        valor, n = esperado(f"OE2_coincidencia_{moneda}")
        assert n == fila["Licitaciones"]
        assert pytest.approx(fila["CoincidePct"], abs=0.005) == valor
    evidencia_iva, _ = sensibilidad_iva(comp)
    valor, n = esperado("OE2_razon_iva_1_19")
    assert valor == evidencia_iva.set_index("MonedaLicitacion").loc["CLP", "CercaIVA"]
    assert n == por_moneda.loc["CLP", "BajoEstimado"]

    # OE3: tasa y mediana de brecha relativa por tamaño ganador
    tabla = tabla_resumen_por_tamano(
        asignar_tamano_ganador(comp, artefactos.ofertas), moneda=None
    ).set_index("TamanoGanador")
    for tamano, fila in tabla.iterrows():
        valor, n = esperado(f"OE3_coincidencia_{tamano}")
        assert n == fila["Licitaciones"]
        assert pytest.approx(fila["TasaCoincidenciaPct"], abs=0.005) == valor
        valor, n = esperado(f"OE3_brecha_rel_{tamano}")
        assert n == fila["Licitaciones"]
        assert pytest.approx((fila["MedianaRazon"] - 1.0) * 100.0, abs=0.005) == valor


def test_asignar_tamano_ganador_vectorizado_vs_iterativo(ruta_processed: Path):
    """Comprueba que la versión vectorizada e iterativa entreguen exactamente el mismo resultado."""
    artefactos = cargar_artefactos(ruta_processed)
    vectorizado = asignar_tamano_ganador(artefactos.licitaciones, artefactos.ofertas)
    iterativo = asignar_tamano_ganador_iterativo(artefactos.licitaciones, artefactos.ofertas)
    pd.testing.assert_frame_equal(vectorizado, iterativo)


# ============================================================================
# CASOS NUEVOS DEL FEEDBACK
# ============================================================================

def test_feedback_razon_exactamente_uno():
    """Caso Feedback 1: Razón exactamente 1 (MontoTotalGanadoras == MontoEstimadoLicitacion)."""
    licitaciones = pd.DataFrame([{
        "NroLicitacion": "LIC-R1",
        "EstadoBrecha": "Calculada",
        "MonedaLicitacion": "CLP",
        "MontoEstimadoLicitacion": 150000.0,
        "MontoTotalGanadoras": 150000.0,
        "BrechaMonto": 0.0,
        "CoincideConEstimado": True,
    }])
    comp = preparar_comparables(licitaciones)
    assert len(comp) == 1
    assert comp["RazonMonto"].iloc[0] == 1.0
    assert comp["LogRazonMonto"].iloc[0] == 0.0
    assert comp["SentidoBrecha"].iloc[0] == "Coincide"

    # En copia graficar
    ofertas = pd.DataFrame([{
        "NroLicitacion": "LIC-R1",
        "ResultadoOferta": "Ganadora",
        "TamanoProveedor": "Micro",
    }])
    copia = construir_copia_graficar(licitaciones, ofertas)
    assert copia["BrechaRelativaPct"].iloc[0] == 0.0
    assert copia["EtiquetaCoincidencia"].iloc[0] == "Coincide"


def test_feedback_todas_las_licitaciones_coinciden():
    """Caso Feedback 2: 100 % de coincidencia en todas las licitaciones evaluadas."""
    n_casos = 8
    licitaciones = pd.DataFrame([
        {
            "NroLicitacion": f"LIC-ALL-{i}",
            "EstadoBrecha": "Calculada",
            "MonedaLicitacion": "CLP",
            "MontoEstimadoLicitacion": float(1000 * (i + 1)),
            "MontoTotalGanadoras": float(1000 * (i + 1)),
            "BrechaMonto": 0.0,
            "CoincideConEstimado": True,
        }
        for i in range(n_casos)
    ])
    tamanos = ["Micro", "Pequeña", "Mediana", "Grande"] * 2
    ofertas = pd.DataFrame([
        {
            "NroLicitacion": f"LIC-ALL-{i}",
            "ResultadoOferta": "Ganadora",
            "TamanoProveedor": tamanos[i],
        }
        for i in range(n_casos)
    ])

    comp = preparar_comparables(licitaciones)
    tasas = tasa_por_grupo(comp, "MonedaLicitacion", "CoincideConEstimado")
    assert tasas.loc[0, "Tasa"] == 1.0
    assert tasas.loc[0, "TasaPct"] == 100.0
    assert tasas.loc[0, "IC_Sup"] == 1.0

    res_sentido = resumen_sentido_por_moneda(comp)
    assert res_sentido.loc[0, "Coincide"] == n_casos
    assert res_sentido.loc[0, "BajoEstimado"] == 0
    assert res_sentido.loc[0, "SobreEstimado"] == 0

    res_mag = resumen_magnitud_por_moneda(comp)
    assert res_mag.loc[0, "MedianaBrecha"] == 0.0
    assert res_mag.loc[0, "MedianaRazon"] == 1.0
    assert res_mag.loc[0, "MedianaLogRazon"] == 0.0

    # Pruebas estadísticas: Chi-cuadrado y Spearman no deben romperse por falta de variación
    copia = construir_copia_graficar(licitaciones, ofertas)
    pruebas = pruebas_por_tamano(copia).set_index("Prueba")
    assert math.isnan(pruebas.loc["Chi-cuadrado de Pearson", "Estadístico"])
    assert math.isnan(pruebas.loc["Spearman", "Estadístico"])


def test_feedback_categoria_tamano_sin_casos():
    """Caso Feedback 3: Una categoría de tamaño (ej. 'Grande') no tiene casos observados."""
    licitaciones = pd.DataFrame([
        {
            "NroLicitacion": f"LIC-T-{i}",
            "EstadoBrecha": "Calculada",
            "MonedaLicitacion": "CLP",
            "MontoEstimadoLicitacion": 1000.0,
            "MontoTotalGanadoras": 1000.0 if i % 2 == 0 else 800.0,
            "BrechaMonto": 0.0 if i % 2 == 0 else -200.0,
            "CoincideConEstimado": (i % 2 == 0),
        }
        for i in range(6)
    ])
    # Sin ofertas en 'Grande' ni 'Mediana'
    tamanos = ["Micro", "Micro", "Pequeña", "Pequeña", "Micro", "Pequeña"]
    ofertas = pd.DataFrame([
        {
            "NroLicitacion": f"LIC-T-{i}",
            "ResultadoOferta": "Ganadora",
            "TamanoProveedor": tamanos[i],
        }
        for i in range(6)
    ])

    copia = construir_copia_graficar(licitaciones, ofertas)
    tabla = tabla_resumen_por_tamano(copia, moneda="CLP")
    assert "Grande" not in tabla["TamanoGanador"].values
    assert set(tabla["TamanoGanador"].values).issubset({"Micro", "Pequeña"})

    # Graficar cajas con categorías faltantes no debe lanzar excepción
    fig = graficar_cajas_brecha_relativa(copia)
    assert fig is not None


def test_feedback_moneda_distinta_de_clp_excluida():
    """Caso Feedback 4: Monedas distintas a CLP (USD, EUR, CLF) deben ser excluidas al filtrar."""
    licitaciones = pd.DataFrame([
        {"NroLicitacion": "LIC-CLP", "EstadoBrecha": "Calculada", "MonedaLicitacion": "CLP",
         "MontoEstimadoLicitacion": 1000.0, "MontoTotalGanadoras": 1000.0, "BrechaMonto": 0.0, "CoincideConEstimado": True},
        {"NroLicitacion": "LIC-USD", "EstadoBrecha": "Calculada", "MonedaLicitacion": "USD",
         "MontoEstimadoLicitacion": 100.0, "MontoTotalGanadoras": 90.0, "BrechaMonto": -10.0, "CoincideConEstimado": False},
        {"NroLicitacion": "LIC-EUR", "EstadoBrecha": "Calculada", "MonedaLicitacion": "EUR",
         "MontoEstimadoLicitacion": 80.0, "MontoTotalGanadoras": 80.0, "BrechaMonto": 0.0, "CoincideConEstimado": True},
        {"NroLicitacion": "LIC-CLF", "EstadoBrecha": "Calculada", "MonedaLicitacion": "CLF",
         "MontoEstimadoLicitacion": 50.0, "MontoTotalGanadoras": 50.0, "BrechaMonto": 0.0, "CoincideConEstimado": True},
    ])
    # 1. Filtro en preparar_comparables
    comp_clp = preparar_comparables(licitaciones, moneda="CLP")
    assert len(comp_clp) == 1
    assert comp_clp["MonedaLicitacion"].iloc[0] == "CLP"

    # 2. Exclusión en ExtremosLogIQR
    ofertas = pd.DataFrame({
        "MonedaOferta": ["CLP", "CLP", "CLP", "CLP", "USD", "EUR"],
        "MontoTotalOferta": [1000, 2000, 3000, 4000, 100, 100],
    })
    detector = ExtremosLogIQR().ajustar(ofertas)
    trans = detector.transformar(ofertas)
    assert trans.loc[trans["MonedaOferta"] == "USD", "EsExtremoLogIQR_CLP"].isna().all()
    assert trans.loc[trans["MonedaOferta"] == "EUR", "EsExtremoLogIQR_CLP"].isna().all()


def test_feedback_artefacto_faltante_error():
    """Caso Feedback 5: Lanzamiento controlado de FileNotFoundError ante artefacto ausente."""
    with TemporaryDirectory() as carpeta:
        carpeta_path = Path(carpeta)

        # Directorio vacío: falta primer archivo
        with pytest.raises(FileNotFoundError, match="No se encontró el archivo procesado"):
            cargar_artefactos(carpeta_path)

        # Crear primer archivo pero omitir el segundo
        (carpeta_path / "04LicitacionesEne_procesado.csv").write_text("a;b\n1;2\n", encoding="utf-8-sig")
        with pytest.raises(FileNotFoundError, match="04LicitacionesEne_brecha_por_licitacion.csv"):
            cargar_artefactos(carpeta_path, columnas_ofertas=None, columnas_licitaciones=None)


def test_feedback_wilson_cero_exitos_o_grupo_vacio():
    """Caso Feedback 6: Comportamiento de Wilson y tasas con 0 éxitos o grupo vacío."""
    # 0 éxitos de 10: límite inferior es 0.0, superior es estrictamente positivo
    inf, sup = intervalo_wilson(0, 10)
    assert inf == 0.0
    assert 0.0 < sup < 1.0

    # Total 0: retorna (nan, nan)
    inf_0, sup_0 = intervalo_wilson(0, 0)
    assert math.isnan(inf_0) and math.isnan(sup_0)

    # 10 éxitos de 10: límite superior es 1.0
    inf_full, sup_full = intervalo_wilson(10, 10)
    assert sup_full == 1.0
    assert 0.0 < inf_full < 1.0

    # Validaciones de argumentos inválidos
    with pytest.raises(ValueError, match="Conteos inválidos"):
        intervalo_wilson(-1, 5)

    with pytest.raises(ValueError, match="Conteos inválidos"):
        intervalo_wilson(6, 5)

    with pytest.raises(ValueError, match="cuantil z"):
        intervalo_wilson(5, 10, z=-1.0)

    # DataFrame vacío en tasa_por_grupo
    df_vacio = pd.DataFrame(columns=["Grupo", "Indicador"])
    res_vacio = tasa_por_grupo(df_vacio, "Grupo", "Indicador")
    assert res_vacio.empty

    # Grupo con 0 éxitos
    df_cero_exitos = pd.DataFrame({"Grupo": ["A", "A", "B"], "Indicador": [False, False, True]})
    res_cero = tasa_por_grupo(df_cero_exitos, "Grupo", "Indicador").set_index("Grupo")
    assert res_cero.loc["A", "Exitos"] == 0
    assert res_cero.loc["A", "Tasa"] == 0.0
    assert res_cero.loc["A", "IC_Inf"] == 0.0
    assert res_cero.loc["A", "IC_Sup"] > 0.0


def test_feedback_contrato_roto():
    """Caso Feedback 7: Detección y rechazo de contratos de esquema o datos rotos."""
    # 1. Columnas faltantes en preparar_comparables
    df_incompleto = pd.DataFrame({"MonedaLicitacion": ["CLP"]})
    with pytest.raises(ValueError, match="faltan columnas requeridas"):
        preparar_comparables(df_incompleto)

    # 2. Montos negativos o cero en licitaciones comparables
    df_monto_cero = pd.DataFrame([{
        "EstadoBrecha": "Calculada",
        "MonedaLicitacion": "CLP",
        "MontoEstimadoLicitacion": 0.0,
        "MontoTotalGanadoras": 100.0,
        "BrechaMonto": 100.0,
        "CoincideConEstimado": False,
    }])
    with pytest.raises(ValueError, match="montos positivos"):
        preparar_comparables(df_monto_cero)

    # 3. Columnas solicitadas que no existen en CSV procesado
    with TemporaryDirectory() as carpeta:
        (Path(carpeta) / "04LicitacionesEne_procesado.csv").write_text("a;b\n1;2\n", encoding="utf-8-sig")
        (Path(carpeta) / "04LicitacionesEne_brecha_por_licitacion.csv").write_text("a;b\n1;2\n", encoding="utf-8-sig")
        (Path(carpeta) / "diccionario_f3.csv").write_text("Tabla;Columna;Tipo en Python\na;b;c\n", encoding="utf-8-sig")
        (Path(carpeta) / "parametros_f3.csv").write_text("Parámetro;Valor\na;b\n", encoding="utf-8-sig")

        with pytest.raises(ValueError, match="usecols no existen"):
            cargar_artefactos(Path(carpeta), columnas_licitaciones=["ColumnaInexistente"])
