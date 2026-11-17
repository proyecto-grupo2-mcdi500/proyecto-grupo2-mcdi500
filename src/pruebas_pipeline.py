"""Pruebas con resultados esperados para las clases y el pipeline POO de F3."""

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from .pipeline_licitaciones import (
    Bitacora, ExtremosLogIQR, Pipeline, ResultadoF3, TransformacionFija,
    Transformador, TratamientoFaltantes, construir_pipeline,
)
from .preprocesamiento import convertir_tipos, marcar_duplicados, ordenar_tamano


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


def _escribir_csv_temporal(carpeta: str, filas: list[dict[str, str]]) -> Path:
    """Crea un CSV temporal con el delimitador ``;`` y codificación ``latin-1`` de entrada."""
    ruta = Path(carpeta) / "licitaciones_prueba.csv"
    pd.DataFrame(filas).to_csv(ruta, sep=";", encoding="latin-1", index=False)
    return ruta


def _filas_ficticias(
    cantidad: int = 6,
    moneda_oferta: str = "CLP",
    moneda_lic: str = "CLP",
    nro_prefijo: str = "LIC",
) -> list[dict[str, str]]:
    """Construye filas sintéticas válidas que cumplen ``REQUERIDAS`` de ``cargar_csv``."""
    base = {
        "NroLicitacion": f"{nro_prefijo}-001",
        "FechaPublicacion": "01-01-2025 10:00",
        "FechaCierre": "05-01-2025 10:00",
        "FechaAdjudicacion": "10-01-2025 10:00",
        "MontoEstimadoLicitacion": "1000",
        "MontoNetoOferta": "500",
        "MontoTotalOferta": "500",
        "MonedaLicitacion": moneda_lic,
        "MonedaOferta": moneda_oferta,
        "TamanoProveedor": "Micro",
        "ResultadoOferta": "Ganadora",
    }
    return [{**base, "MontoTotalOferta": str(500 + i)} for i in range(cantidad)]


def ejecutar_pruebas_pipeline(mostrar_log: bool = True) -> pd.DataFrame:
    """Ejecuta pruebas de las clases de F3 en casos normales, límite y de excepción.

    Parámetros
    ----------
    mostrar_log : bool, opcional
        Si es ``True``, imprime por consola una traza ``[OK]`` por cada caso aprobado.

    Retorna
    -------
    pd.DataFrame
        Tabla de trazabilidad con columnas ``Clase``, ``Escenario``, ``Caso``,
        ``Estado`` y ``Evidencia``.
    """
    registros: list[dict[str, str]] = []

    def registrar(
        clase: str,
        escenario: str,
        caso: str,
        funcion: Callable[[], str],
    ) -> None:
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

    # --- CASOS NORMALES ---
    def p_pipeline_normal() -> str:
        with TemporaryDirectory() as carpeta:
            ruta = _escribir_csv_temporal(carpeta, _filas_ficticias(cantidad=6))
            pipe = construir_pipeline()
            obs_a, obs_b = Bitacora(), Bitacora()
            pipe.suscribir(obs_a.registrar)
            pipe.suscribir(obs_b.registrar)
            res = pipe.ejecutar(ruta)
            assert isinstance(res, ResultadoF3)
            assert res.limites_iqr is not None and res.limites_iqr["ofertas_validas"] == 6
            pd.testing.assert_frame_equal(obs_a.tabla(), obs_b.tabla())
            return (
                f"ResultadoF3 válido (6 ofertas, {len(obs_a.tabla())} eventos polimórficos idénticos)"
            )

    def p_base_copia_defensiva() -> str:
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
        return "Transformador protege DataFrame original mediante copia defensiva y controla ajustado"

    def p_tfija_normal() -> str:
        paso = TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",))
        entrada_df = pd.DataFrame({"TamanoProveedor": ["Mediana", "Micro"]})
        salida_df = paso.ajustar(entrada_df).transformar(entrada_df)
        assert paso.nombre == "Ordenar" and "TamanoProveedorOrdinal" not in entrada_df.columns
        assert list(salida_df["TamanoProveedorOrdinal"]) == ["Mediana", "Micro"]
        return "nombre='Ordenar', entrada intacta, columna ordinal asignada"

    def p_faltantes_normal() -> str:
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
        return "Aprende ColVacia91 (>90 %) en ajustar() y la excluye al transformar()"

    def p_extremos_normal() -> str:
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
        return "Copia defensiva en .limites intacta y bandera [False, True, <NA>]"

    # --- CASOS LÍMITE ---
    def p_pipeline_una_fila() -> str:
        with TemporaryDirectory() as carpeta:
            ruta = _escribir_csv_temporal(carpeta, _filas_ficticias(cantidad=1))
            res = construir_pipeline().ejecutar(ruta)
            assert len(res.ofertas) == 1 and len(res.licitaciones) == 1
            assert not bool(res.ofertas["EsDuplicadoPotencial"].iloc[0])
            assert res.limites_iqr is None and res.ofertas["EsExtremoLogIQR_CLP"].isna().all()
            return "1 oferta -> 1 licitación, EsDuplicadoPotencial=False, limites_iqr=None"

    def p_pipeline_sin_clp() -> str:
        with TemporaryDirectory() as carpeta:
            ruta = _escribir_csv_temporal(
                carpeta, _filas_ficticias(cantidad=4, moneda_oferta="USD", moneda_lic="USD")
            )
            res = construir_pipeline().ejecutar(ruta)
            assert res.limites_iqr is None and res.ofertas["EsExtremoLogIQR_CLP"].isna().all()
            assert res.licitaciones["EstadoBrecha"].eq("Calculada").all()
            return "0 ofertas CLP (4 en USD) -> limites_iqr=None, bandera NA y brecha USD calculada"

    def p_columna_sin_nulos() -> str:
        df_sin_nulos = pd.DataFrame(_filas_ficticias(cantidad=4))
        tf = TratamientoFaltantes(umbral_pct=90.0)
        salida = tf.ajustar(df_sin_nulos).transformar(df_sin_nulos)
        assert tf.columnas_excluidas == ()
        assert tf.resumen is not None
        assert int(tf.resumen["Nulos después de convertir y normalizar"].sum()) == 0
        assert list(salida.columns) == list(df_sin_nulos.columns)
        return f"{len(df_sin_nulos.columns)} columnas con 0 nulos: 0 excluidas tras ajustar y transformar"

    def p_pipeline_sin_observadores() -> str:
        with TemporaryDirectory() as carpeta:
            ruta = _escribir_csv_temporal(carpeta, _filas_ficticias(cantidad=2))
            res = construir_pipeline().ejecutar(ruta)
            assert isinstance(res, ResultadoF3) and res.limites_iqr is None
            return "Ejecución sin observadores suscritos completada (<4 CLP -> limites None)"

    def p_tfija_vacio() -> str:
        paso = TransformacionFija("Ordenar vacío", ordenar_tamano, ("TamanoProveedor",))
        vacio = pd.DataFrame({"TamanoProveedor": pd.Series([], dtype="string")})
        salida_df = paso.ajustar(vacio).transformar(vacio)
        assert len(salida_df) == 0 and "TamanoProveedorOrdinal" in salida_df.columns
        return "DataFrame de 0 filas conserva esquema y genera TamanoProveedorOrdinal"

    def p_extremos_limite() -> str:
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
        return "<4 CLP válidas -> None/NA; 4 ofertas iguales (IQR=0) -> 0 extremos"

    def p_bitacora_limite() -> str:
        bitacora = Bitacora()
        assert bitacora.tabla().empty and len(bitacora.tabla()) == 0
        bitacora.registrar("Paso 1", 10, 10)
        assert list(bitacora.tabla().columns) == ["Paso", "Filas de entrada", "Filas de salida"]
        return "Instancia vacía retorna DataFrame vacío; tabla guarda solo conteos"

    # --- CASOS DE EXCEPCIÓN ---
    def p_sin_ajustar_comun() -> str:
        err_iqr = _esperar_error(
            lambda: ExtremosLogIQR().transformar(
                pd.DataFrame({"MonedaOferta": ["CLP"], "MontoTotalOferta": [100]})
            ),
            RuntimeError,
            "ajustar",
        )
        _esperar_error(
            lambda: TratamientoFaltantes().transformar(pd.DataFrame({"A": [1]})),
            RuntimeError,
            "ajustar",
        )
        _esperar_error(
            lambda: TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",)).transformar(
                pd.DataFrame({"TamanoProveedor": ["Micro"]})
            ),
            RuntimeError,
            "ajustar",
        )
        return f"Control común de _ajustado detiene las 3 subclases ({err_iqr.split(':', 1)[0]})"

    def p_pipeline_excepciones() -> str:
        pipe = construir_pipeline()
        with TemporaryDirectory() as carpeta:
            err_arch = _esperar_error(
                lambda: pipe.ejecutar(Path(carpeta) / "no_existe_f3.csv"),
                FileNotFoundError,
            )
            ruta_incompleta = _escribir_csv_temporal(
                carpeta, [{"NroLicitacion": "A", "MonedaOferta": "CLP"}]
            )
            err_esq = _esperar_error(
                lambda: pipe.ejecutar(ruta_incompleta), ValueError, "Faltan columnas requeridas"
            )
            ruta_ok = _escribir_csv_temporal(carpeta, _filas_ficticias(cantidad=4))
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
            err_inv = _esperar_error(lambda: pipe_roto.ejecutar(ruta_ok), AssertionError, "filas")
        return f"{err_arch.split(':', 1)[0]} | {err_esq.split(':', 1)[0]} | {err_inv}"

    def p_transformador_abc() -> str:
        err_dir = _esperar_error(lambda: Transformador(), TypeError, "abstract")

        class PasoIncompleto(Transformador):
            nombre = "Incompleto"

        _esperar_error(lambda: PasoIncompleto(), TypeError, "abstract")
        return f"Contrato ABC bloquea instanciación directa e incompleta ({err_dir.split(':', 1)[0]})"

    def p_validacion_columnas_y_reglas() -> str:
        paso = TransformacionFija("Ordenar", ordenar_tamano, ("TamanoProveedor",))
        err_col = _esperar_error(
            lambda: paso.ajustar(pd.DataFrame({"Otro": [1]})),
            ValueError,
            "faltan columnas requeridas",
        )
        err_iqr_col = _esperar_error(
            lambda: ExtremosLogIQR().ajustar(pd.DataFrame({"MonedaOferta": ["CLP"]})),
            ValueError,
            "MontoTotalOferta",
        )
        err_umbral = _esperar_error(lambda: TratamientoFaltantes(umbral_pct=150.0), ValueError, "0 y 100")
        err_cat = _esperar_error(
            lambda: paso.ajustar(pd.DataFrame({"TamanoProveedor": ["Gigante"]})).transformar(
                pd.DataFrame({"TamanoProveedor": ["Gigante"]})
            ),
            ValueError,
            "Gigante",
        )
        return (
            f"{err_col.split(':', 1)[0]} | {err_iqr_col.split(':', 1)[0]} | "
            f"{err_umbral.split(':', 1)[0]} | {err_cat}"
        )

    casos = [
        (
            "Pipeline",
            "Normal",
            "Pipeline polimórfico sobre conjunto pequeño (6 ofertas) con observadores",
            p_pipeline_normal,
        ),
        (
            "Transformador",
            "Normal",
            "Copia defensiva y estado ajustado en la clase base",
            p_base_copia_defensiva,
        ),
        (
            "TransformacionFija",
            "Normal",
            "Envoltura de regla funcional sin mutar entrada",
            p_tfija_normal,
        ),
        (
            "TratamientoFaltantes",
            "Normal",
            "Aprende columnas >90 % en ajustar() y las excluye al transformar()",
            p_faltantes_normal,
        ),
        (
            "ExtremosLogIQR",
            "Normal",
            "Ajuste, copia defensiva de .limites y detección",
            p_extremos_normal,
        ),
        ("Pipeline", "Límite", "Una sola fila en el archivo de entrada", p_pipeline_una_fila),
        ("Pipeline", "Límite", "Ninguna oferta en CLP (0 filas CLP)", p_pipeline_sin_clp),
        (
            "TratamientoFaltantes",
            "Límite",
            "Columna sin nulos (0 nulos antes y después, 0 excluidas)",
            p_columna_sin_nulos,
        ),
        (
            "Pipeline",
            "Límite",
            "Ejecución sin observadores suscritos (<4 CLP)",
            p_pipeline_sin_observadores,
        ),
        ("TransformacionFija", "Límite", "DataFrame vacío (0 filas) conserva esquema", p_tfija_vacio),
        (
            "ExtremosLogIQR",
            "Límite",
            "Muestra <4 CLP válidas e IQR=0 con 4 iguales",
            p_extremos_limite,
        ),
        ("Bitacora", "Límite", "Bitácora vacía y registro sin datos sensibles", p_bitacora_limite),
        (
            "Transformador",
            "Excepción",
            "Control común de _ajustado al llamar transformar() sin ajustar()",
            p_sin_ajustar_comun,
        ),
        (
            "Pipeline",
            "Excepción",
            "Archivo inexistente, columna requerida ausente y pérdida de filas",
            p_pipeline_excepciones,
        ),
        (
            "Transformador",
            "Excepción",
            "Instanciación directa y subclase sin implementar _aplicar",
            p_transformador_abc,
        ),
        (
            "Transformador / Reglas",
            "Excepción",
            "Validación común de columnas requeridas, umbral y categoría",
            p_validacion_columnas_y_reglas,
        ),
    ]

    for clase, escenario, caso, fn in casos:
        registrar(clase, escenario, caso, fn)
    return pd.DataFrame(registros)


if __name__ == "__main__":
    ejecutar_pruebas_pipeline()
