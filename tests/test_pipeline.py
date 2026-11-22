"""Pruebas con resultados esperados para las clases y el pipeline POO de F3."""

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.pipeline_licitaciones import (
    Bitacora, ExtremosLogIQR, Pipeline, ResultadoF3, TransformacionFija,
    Transformador, TratamientoFaltantes, construir_pipeline,
)
from src.preprocesamiento import convertir_tipos, marcar_duplicados, ordenar_tamano
from tests.conftest import crear_filas_ficticias, escribir_csv_temporal


def _esperar_error(
    llamada: Callable[[], object],
    error_esperado: type[Exception],
    texto_esperado: str = "",
) -> str:
    """Comprueba que una llamada lance el tipo de excepción (y fragmento) esperado."""
    try:
        llamada()
    except error_esperado as error:
        if texto_esperado and texto_esperado not in str(error):
            raise AssertionError(
                f"Mensaje inesperado para {error_esperado.__name__}: {error}"
            ) from error
        return f"{type(error).__name__}: {error}"
    raise AssertionError(f"Se esperaba {error_esperado.__name__} y no se lanzó excepción.")


# ============================================================================
# PRUEBAS INDIVIDUALES PYTEST (Casos Normales)
# ============================================================================

def test_pipeline_normal():
    """Pipeline polimórfico sobre conjunto pequeño (6 ofertas) con observadores."""
    with TemporaryDirectory() as carpeta:
        ruta = escribir_csv_temporal(carpeta, crear_filas_ficticias(cantidad=6))
        pipe = construir_pipeline()
        obs_a, obs_b = Bitacora(), Bitacora()
        pipe.suscribir(obs_a.registrar)
        pipe.suscribir(obs_b.registrar)
        res = pipe.ejecutar(ruta)

        assert isinstance(res, ResultadoF3)
        assert res.limites_iqr is not None and res.limites_iqr["ofertas_validas"] == 6
        pd.testing.assert_frame_equal(obs_a.tabla(), obs_b.tabla())


def test_base_copia_defensiva():
    """Copia defensiva y estado ajustado en la clase base Transformador."""
    def regla_mutante(df: pd.DataFrame) -> pd.DataFrame:
        df["TamanoProveedor"] = "Alterado"
        return df.assign(Marca=True)

    paso = TransformacionFija("Mutante controlada", regla_mutante, ("TamanoProveedor",))
    entrada_df = pd.DataFrame({"TamanoProveedor": ["Mediana", "Micro"]})
    assert not paso.ajustado
    salida_df = paso.ajustar(entrada_df).transformar(entrada_df)
    assert paso.ajustado and "Marca" not in entrada_df.columns
    assert list(entrada_df["TamanoProveedor"]) == ["Mediana", "Micro"]
    assert list(salida_df["TamanoProveedor"]) == ["Alterado", "Alterado"]


def test_tfija_normal():
    """Envoltura de regla funcional sin mutar entrada."""
    paso = TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",))
    entrada_df = pd.DataFrame({"TamanoProveedor": ["Mediana", "Micro"]})
    salida_df = paso.ajustar(entrada_df).transformar(entrada_df)
    assert paso.nombre == "Ordenar" and "TamanoProveedorOrdinal" not in entrada_df.columns
    assert list(salida_df["TamanoProveedorOrdinal"]) == ["Mediana", "Micro"]


def test_faltantes_normal():
    """Aprende columnas >90 % en ajustar() y las excluye al transformar()."""
    tf = TratamientoFaltantes(umbral_pct=90.0)
    assert tf.umbral_pct == 90.0
    ajuste_df = pd.DataFrame({
        "ColUtil": ["a", "b", "   ", "d", "e", "f", "g", "h", "i", "j", "k"],
        "ColVacia91": [pd.NA] * 10 + ["unico"],
    })
    tf.ajustar(ajuste_df)
    assert tf.columnas_excluidas == ("ColVacia91",)
    eval_df = pd.DataFrame({"ColUtil": ["  ", "x"], "ColVacia91": ["lleno", "lleno"]})
    salida = tf.transformar(eval_df)
    assert list(salida.columns) == ["ColUtil"] and pd.isna(salida.loc[0, "ColUtil"])


def test_extremos_normal():
    """Ajuste, copia defensiva de .limites y detección log-IQR."""
    detector = ExtremosLogIQR()
    assert detector.limites is None and not detector.ajustado
    detector.ajustar(
        pd.DataFrame({"MonedaOferta": ["CLP"] * 5, "MontoTotalOferta": [10, 20, 30, 40, 50]})
    )
    assert detector.ajustado
    copia = detector.limites
    assert copia is not None
    copia["superior_log"] = -999.0
    assert detector.limites is not None and detector.limites["superior_log"] != -999.0
    res_df = detector.transformar(
        pd.DataFrame({"MonedaOferta": ["CLP", "CLP", "USD"], "MontoTotalOferta": [30, 10000, 10000]})
    )
    assert res_df["EsExtremoLogIQR_CLP"].tolist()[:2] == [False, True]
    assert pd.isna(res_df["EsExtremoLogIQR_CLP"].iloc[2])


# ============================================================================
# PRUEBAS INDIVIDUALES PYTEST (Casos Límite)
# ============================================================================

def test_pipeline_una_fila():
    """Una sola fila en el archivo de entrada."""
    with TemporaryDirectory() as carpeta:
        ruta = escribir_csv_temporal(carpeta, crear_filas_ficticias(cantidad=1))
        res = construir_pipeline().ejecutar(ruta)
        assert len(res.ofertas) == 1 and len(res.licitaciones) == 1
        assert not bool(res.ofertas["EsDuplicadoPotencial"].iloc[0])
        assert res.limites_iqr is None and res.ofertas["EsExtremoLogIQR_CLP"].isna().all()


def test_pipeline_sin_clp():
    """Ninguna oferta en CLP (0 filas CLP, 4 en USD)."""
    with TemporaryDirectory() as carpeta:
        ruta = escribir_csv_temporal(
            carpeta, crear_filas_ficticias(cantidad=4, moneda_oferta="USD", moneda_lic="USD")
        )
        res = construir_pipeline().ejecutar(ruta)
        assert res.limites_iqr is None and res.ofertas["EsExtremoLogIQR_CLP"].isna().all()
        assert res.licitaciones["EstadoBrecha"].eq("Calculada").all()


def test_columna_sin_nulos():
    """Columna sin nulos (0 nulos antes y después, 0 excluidas)."""
    df_sin_nulos = pd.DataFrame(crear_filas_ficticias(cantidad=4))
    tf = TratamientoFaltantes(umbral_pct=90.0)
    salida = tf.ajustar(df_sin_nulos).transformar(df_sin_nulos)
    assert tf.columnas_excluidas == ()
    assert tf.resumen is not None
    assert int(tf.resumen["Nulos después de convertir y normalizar"].sum()) == 0
    assert list(salida.columns) == list(df_sin_nulos.columns)


def test_faltantes_variable_analitica():
    """Variable del análisis con más del 90 % de faltantes se conserva."""
    tf = TratamientoFaltantes(umbral_pct=90.0)
    datos = pd.DataFrame({
        "FechaAdjudicacion": [pd.NA] * 10 + ["10-01-2025 10:00"],
        "ColAdministrativa": [pd.NA] * 10 + ["x"],
    })
    salida = tf.ajustar(datos).transformar(datos)
    assert tf.columnas_excluidas == ("ColAdministrativa",)
    assert list(salida.columns) == ["FechaAdjudicacion"]


def test_pipeline_sin_observadores():
    """Ejecución sin observadores suscritos (<4 CLP)."""
    with TemporaryDirectory() as carpeta:
        ruta = escribir_csv_temporal(carpeta, crear_filas_ficticias(cantidad=2))
        res = construir_pipeline().ejecutar(ruta)
        assert isinstance(res, ResultadoF3) and res.limites_iqr is None


def test_tfija_vacio():
    """DataFrame vacío (0 filas) conserva esquema y genera TamanoProveedorOrdinal."""
    paso = TransformacionFija("Ordenar vacío", ordenar_tamano, ("TamanoProveedor",))
    vacio = pd.DataFrame({"TamanoProveedor": pd.Series([], dtype="string")})
    salida_df = paso.ajustar(vacio).transformar(vacio)
    assert len(salida_df) == 0 and "TamanoProveedorOrdinal" in salida_df.columns


def test_extremos_limite():
    """Muestra <4 CLP válidas e IQR=0 con 4 ofertas iguales."""
    det_pocos = ExtremosLogIQR()
    pocos = pd.DataFrame({
        "MonedaOferta": ["CLP", "CLP", "CLP", "USD", "CLP"],
        "MontoTotalOferta": [100, 200, 300, 400, 0],
    })
    det_pocos.ajustar(pocos)
    assert det_pocos.limites is None
    assert det_pocos.transformar(pocos)["EsExtremoLogIQR_CLP"].isna().all()

    det_iguales = ExtremosLogIQR()
    iguales = pd.DataFrame({"MonedaOferta": ["CLP"] * 4, "MontoTotalOferta": [500, 500, 500, 500]})
    det_iguales.ajustar(iguales)
    assert det_iguales.limites is not None
    assert not det_iguales.transformar(iguales)["EsExtremoLogIQR_CLP"].any()


def test_bitacora_limite():
    """Bitácora vacía y registro sin datos sensibles."""
    bitacora = Bitacora()
    assert bitacora.tabla().empty and len(bitacora.tabla()) == 0
    bitacora.registrar("Paso 1", 10, 10)
    assert list(bitacora.tabla().columns) == ["Paso", "Filas de entrada", "Filas de salida"]


# ============================================================================
# PRUEBAS INDIVIDUALES PYTEST (Casos de Excepción)
# ============================================================================

def test_sin_ajustar_comun():
    """Control común de _ajustado al llamar transformar() sin ajustar()."""
    with pytest.raises(RuntimeError, match="ajustar"):
        ExtremosLogIQR().transformar(pd.DataFrame({"MonedaOferta": ["CLP"], "MontoTotalOferta": [100]}))

    with pytest.raises(RuntimeError, match="ajustar"):
        TratamientoFaltantes().transformar(pd.DataFrame({"A": [1]}))

    with pytest.raises(RuntimeError, match="ajustar"):
        TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",)).transformar(
            pd.DataFrame({"TamanoProveedor": ["Micro"]})
        )


def test_pipeline_excepciones():
    """Archivo inexistente, columna requerida ausente y fallo por pérdida de filas."""
    pipe = construir_pipeline()
    with TemporaryDirectory() as carpeta:
        with pytest.raises(FileNotFoundError):
            pipe.ejecutar(Path(carpeta) / "no_existe_f3.csv")

        ruta_incompleta = escribir_csv_temporal(
            carpeta, [{"NroLicitacion": "A", "MonedaOferta": "CLP"}]
        )
        with pytest.raises(ValueError, match="Faltan columnas requeridas"):
            pipe.ejecutar(ruta_incompleta)

        ruta_ok = escribir_csv_temporal(carpeta, crear_filas_ficticias(cantidad=4))
        pipe_roto = Pipeline([
            TransformacionFija(
                "Marcar duplicados potenciales",
                lambda d: marcar_duplicados(d)[0],
                ("ResultadoOferta",),
            ),
            TransformacionFija("Convertir fechas y montos", lambda d: convertir_tipos(d)[0]),
            TratamientoFaltantes(),
            TransformacionFija("Ordenar tamaño de proveedor", ordenar_tamano, ("TamanoProveedor",)),
            ExtremosLogIQR(),
            TransformacionFija("Recortar fila (fallo controlado)", lambda d: d.iloc[:-1]),
        ])
        with pytest.raises(AssertionError, match="filas"):
            pipe_roto.ejecutar(ruta_ok)


def test_transformador_abc():
    """Instanciación directa y subclase sin implementar _aplicar."""
    with pytest.raises(TypeError, match="abstract"):
        Transformador()

    class PasoIncompleto(Transformador):
        nombre = "Incompleto"

    with pytest.raises(TypeError, match="abstract"):
        PasoIncompleto()


def test_validacion_columnas_y_reglas():
    """Validación común de columnas requeridas, umbral y categoría desconocida."""
    paso = TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",))
    with pytest.raises(ValueError, match="faltan columnas requeridas"):
        paso.ajustar(pd.DataFrame({"Otro": [1]}))

    with pytest.raises(ValueError, match="MontoTotalOferta"):
        ExtremosLogIQR().ajustar(pd.DataFrame({"MonedaOferta": ["CLP"]}))

    with pytest.raises(ValueError, match="0 y 100"):
        TratamientoFaltantes(umbral_pct=150.0)

    with pytest.raises(ValueError, match="Gigante"):
        paso.ajustar(pd.DataFrame({"TamanoProveedor": ["Gigante"]})).transformar(
            pd.DataFrame({"TamanoProveedor": ["Gigante"]})
        )


# ============================================================================
# FUNCIÓN COMPATIBILIDAD CON CUADERNOS DE F3 (Retorna tabla de 17 casos)
# ============================================================================

def ejecutar_pruebas_pipeline(mostrar_log: bool = True) -> pd.DataFrame:
    """Ejecuta pruebas de las clases de F3 en casos normales, límite y de excepción.

    Retorna
    -------
    pd.DataFrame
        Tabla de trazabilidad con columnas ``Clase``, ``Escenario``, ``Caso``,
        ``Estado`` y ``Evidencia`` (17 filas aprobadas).
    """
    registros: list[dict[str, str]] = []

    def registrar(clase: str, escenario: str, caso: str, funcion: Callable[[], str]) -> None:
        evidencia = funcion()
        registros.append({
            "Clase": clase,
            "Escenario": escenario,
            "Caso": caso,
            "Estado": "APROBADA",
            "Evidencia": evidencia,
        })
        if mostrar_log:
            print(f"[OK] {clase:<20} | {escenario:<9} | {caso} -> {evidencia}")

    # Ejecuciones con evidencias
    def p_pipeline_normal() -> str:
        test_pipeline_normal()
        return "ResultadoF3 válido (6 ofertas, eventos polimórficos idénticos)"

    def p_base_copia_defensiva() -> str:
        test_base_copia_defensiva()
        return "Transformador protege DataFrame original mediante copia defensiva y controla ajustado"

    def p_tfija_normal() -> str:
        test_tfija_normal()
        return "nombre='Ordenar', entrada intacta, columna ordinal asignada"

    def p_faltantes_normal() -> str:
        test_faltantes_normal()
        return "Aprende ColVacia91 (>90 %) en ajustar() y la excluye al transformar()"

    def p_extremos_normal() -> str:
        test_extremos_normal()
        return "Copia defensiva en .limites intacta y bandera [False, True, <NA>]"

    def p_pipeline_una_fila() -> str:
        test_pipeline_una_fila()
        return "1 oferta -> 1 licitación, EsDuplicadoPotencial=False, limites_iqr=None"

    def p_pipeline_sin_clp() -> str:
        test_pipeline_sin_clp()
        return "0 ofertas CLP (4 en USD) -> limites_iqr=None, bandera NA y brecha USD calculada"

    def p_columna_sin_nulos() -> str:
        test_columna_sin_nulos()
        return "4 columnas con 0 nulos: 0 excluidas tras ajustar y transformar"

    def p_faltantes_variable_analitica() -> str:
        test_faltantes_variable_analitica()
        return "FechaAdjudicacion (variable del análisis) se conserva con 91 % de faltantes; ColAdministrativa se excluye"

    def p_pipeline_sin_observadores() -> str:
        test_pipeline_sin_observadores()
        return "Ejecución sin observadores suscritos completada (<4 CLP -> limites None)"

    def p_tfija_vacio() -> str:
        test_tfija_vacio()
        return "DataFrame de 0 filas conserva esquema y genera TamanoProveedorOrdinal"

    def p_extremos_limite() -> str:
        test_extremos_limite()
        return "<4 CLP válidas -> None/NA; 4 ofertas iguales (IQR=0) -> 0 extremos"

    def p_bitacora_limite() -> str:
        test_bitacora_limite()
        return "Instancia vacía retorna DataFrame vacío; tabla guarda solo conteos"

    def p_sin_ajustar_comun() -> str:
        test_sin_ajustar_comun()
        return "Control común de _ajustado detiene las 3 subclases (RuntimeError)"

    def p_pipeline_excepciones() -> str:
        test_pipeline_excepciones()
        return "FileNotFoundError | ValueError | AssertionError: filas"

    def p_transformador_abc() -> str:
        test_transformador_abc()
        return "Contrato ABC bloquea instanciación directa e incompleta (TypeError)"

    def p_validacion_columnas_y_reglas() -> str:
        test_validacion_columnas_y_reglas()
        return "ValueError | ValueError | ValueError | ValueError"

    casos = [
        ("Pipeline", "Normal", "Pipeline polimórfico sobre conjunto pequeño (6 ofertas) con observadores", p_pipeline_normal),
        ("Transformador", "Normal", "Copia defensiva y estado ajustado en la clase base", p_base_copia_defensiva),
        ("TransformacionFija", "Normal", "Envoltura de regla funcional sin mutar entrada", p_tfija_normal),
        ("TratamientoFaltantes", "Normal", "Aprende columnas >90 % en ajustar() y las excluye al transformar()", p_faltantes_normal),
        ("ExtremosLogIQR", "Normal", "Ajuste, copia defensiva de .limites y detección", p_extremos_normal),
        ("Pipeline", "Límite", "Una sola fila en el archivo de entrada", p_pipeline_una_fila),
        ("Pipeline", "Límite", "Ninguna oferta en CLP (0 filas CLP)", p_pipeline_sin_clp),
        ("TratamientoFaltantes", "Límite", "Columna sin nulos (0 nulos antes y después, 0 excluidas)", p_columna_sin_nulos),
        ("TratamientoFaltantes", "Límite", "Variable del análisis con más del 90 % de faltantes se conserva", p_faltantes_variable_analitica),
        ("Pipeline", "Límite", "Ejecución sin observadores suscritos (<4 CLP)", p_pipeline_sin_observadores),
        ("TransformacionFija", "Límite", "DataFrame vacío (0 filas) conserva esquema", p_tfija_vacio),
        ("ExtremosLogIQR", "Límite", "Muestra <4 CLP válidas e IQR=0 con 4 iguales", p_extremos_limite),
        ("Bitacora", "Límite", "Bitácora vacía y registro sin datos sensibles", p_bitacora_limite),
        ("Transformador", "Excepción", "Control común de _ajustado al llamar transformar() sin ajustar()", p_sin_ajustar_comun),
        ("Pipeline", "Excepción", "Archivo inexistente, columna requerida ausente y pérdida de filas", p_pipeline_excepciones),
        ("Transformador", "Excepción", "Instanciación directa y subclase sin implementar _aplicar", p_transformador_abc),
        ("Transformador / Reglas", "Excepción", "Validación común de columnas requeridas, umbral y categoría", p_validacion_columnas_y_reglas),
    ]

    for clase, escenario, caso, fn in casos:
        registrar(clase, escenario, caso, fn)
    return pd.DataFrame(registros)


if __name__ == "__main__":
    ejecutar_pruebas_pipeline()
