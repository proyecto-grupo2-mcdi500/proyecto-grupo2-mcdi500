"""Indicadores y gráficos de la Fase 4 para visualizar y comunicar los resultados del proyecto."""

from collections.abc import Sequence
from dataclasses import dataclass
import math
from pathlib import Path

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, spearmanr

from .preprocesamiento import ORDEN_TAMANO, calcular_brecha, normalizar_codigo

ARCHIVOS_PROCESADOS: dict[str, str] = {
    "ofertas": "04LicitacionesEne_procesado.csv",
    "licitaciones": "04LicitacionesEne_brecha_por_licitacion.csv",
    "diccionario": "diccionario_f3.csv",
    "parametros": "parametros_f3.csv",
}

COLUMNAS_OFERTAS_F4: tuple[str, ...] = (
    "NroLicitacion",
    "MonedaOferta",
    "MontoTotalOferta",
    "ResultadoOferta",
    "TamanoProveedor",
    "TamanoProveedorOrdinal",
    "EsExtremoLogIQR_CLP",
    "EsDuplicadoPotencial",
    "MontoEstimadoLicitacion",
    "MonedaLicitacion",
)

COLUMNAS_LICITACIONES_F4: tuple[str, ...] = (
    "NroLicitacion",
    "FilasOferta",
    "OfertasGanadoras",
    "MontoEstimadoLicitacion",
    "MonedaLicitacion",
    "GanadoraDuplicada",
    "MontoTotalGanadoras",
    "BrechaMonto",
    "EstadoBrecha",
    "CoincideConEstimado",
    "VisibilidadEstimado",
)

ORDEN_SENTIDO: tuple[str, ...] = ("Bajo el estimado", "Coincide", "Sobre el estimado")
ORDEN_TAMANOS_TABLA: tuple[str, ...] = (*ORDEN_TAMANO, "NoClasificado", "Múltiple")
ORDEN_TRAMOS_ESTIMADO: tuple[str, ...] = (
    "Hasta 1 M CLP",
    "1 a 10 M CLP",
    "10 a 50 M CLP",
    "Más de 50 M CLP",
    "Otra moneda (no CLP)",
)
FUENTE_DATOS_F4: str = "Fuente: ChileCompra, datos abiertos, municipalidades, enero de 2025"


@dataclass(frozen=True)
class ArtefactosF4:
    """Contenedor inmutable con las cuatro tablas versionadas de ``data/processed/``.

    Atributos
    ---------
    ofertas : pd.DataFrame
        Tabla de ofertas por ítem leída selectivamente desde ``04LicitacionesEne_procesado.csv``.
    licitaciones : pd.DataFrame
        Tabla agregada por licitación desde ``04LicitacionesEne_brecha_por_licitacion.csv``.
    diccionario : pd.DataFrame
        Diccionario técnico de variables generado en F3 (``diccionario_f3.csv``).
    parametros : pd.DataFrame
        Parámetros fijos y ajustados de ``parametros_f3.csv``.
    """

    ofertas: pd.DataFrame
    licitaciones: pd.DataFrame
    diccionario: pd.DataFrame
    parametros: pd.DataFrame


def _validar_columnas(datos: pd.DataFrame, requeridas: Sequence[str], contexto: str) -> None:
    """Verifica que ``datos`` contenga todas las columnas necesarias antes de calcular."""
    faltantes = sorted(set(requeridas).difference(datos.columns))
    if faltantes:
        raise ValueError(f"{contexto}: faltan columnas requeridas: {faltantes}.")


def _leer_csv_procesado(
    ruta: Path,
    columnas: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Lee un CSV procesado con ``sep=';'`` y ``utf-8-sig`` aplicando ``usecols`` opcional."""
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo procesado: {ruta}")
    lectura_cols = None if columnas is None else list(columnas)
    try:
        return pd.read_csv(
            ruta,
            sep=";",
            encoding="utf-8-sig",
            usecols=lectura_cols,
        )
    except ValueError as error:
        raise ValueError(
            f"Algunas columnas pedidas en usecols no existen en {ruta.name}: {lectura_cols}"
        ) from error


def cargar_artefactos(
    carpeta_procesados: Path | str,
    columnas_ofertas: Sequence[str] | None = COLUMNAS_OFERTAS_F4,
    columnas_licitaciones: Sequence[str] | None = COLUMNAS_LICITACIONES_F4,
) -> ArtefactosF4:
    """Carga los cuatro artefactos de ``data/processed/`` con ``sep=';'`` y ``usecols``.

    A diferencia del proyecto modelo, no implementa ``revertir_escalamiento`` ni
    ``reconstruir_categorias``: F2 y F3 conservan los montos en su moneda original y
    ``TamanoProveedorOrdinal`` conserva sus categorías explícitas en texto.

    Parámetros
    ----------
    carpeta_procesados : Path | str
        Ruta al directorio ``data/processed`` del repositorio.
    columnas_ofertas : Sequence[str] | None, opcional
        Subconjunto de columnas a leer en ofertas mediante ``usecols`` (``None`` lee todas).
    columnas_licitaciones : Sequence[str] | None, opcional
        Subconjunto de columnas a leer en licitaciones mediante ``usecols`` (``None`` lee todas).

    Retorna
    -------
    ArtefactosF4
        Contenedor con ``ofertas``, ``licitaciones``, ``diccionario`` y ``parametros``.
    """
    raiz_proc = Path(carpeta_procesados)
    ofertas = _leer_csv_procesado(raiz_proc / ARCHIVOS_PROCESADOS["ofertas"], columnas_ofertas)
    if "TamanoProveedorOrdinal" in ofertas.columns:
        ofertas["TamanoProveedorOrdinal"] = pd.Categorical(
            ofertas["TamanoProveedorOrdinal"], categories=ORDEN_TAMANO, ordered=True
        )
    licitaciones = _leer_csv_procesado(
        raiz_proc / ARCHIVOS_PROCESADOS["licitaciones"], columnas_licitaciones
    )
    diccionario = _leer_csv_procesado(raiz_proc / ARCHIVOS_PROCESADOS["diccionario"])
    parametros = _leer_csv_procesado(raiz_proc / ARCHIVOS_PROCESADOS["parametros"])
    return ArtefactosF4(
        ofertas=ofertas,
        licitaciones=licitaciones,
        diccionario=diccionario,
        parametros=parametros,
    )


def intervalo_wilson(exitos: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Calcula el intervalo de confianza de Wilson para una proporción binomial.

    Parámetros
    ----------
    exitos : int
        Cantidad de observaciones favorables.
    total : int
        Cantidad total de observaciones evaluadas.
    z : float, opcional
        Valor crítico normal estándar (por defecto ``1.96`` para 95 % de confianza).

    Retorna
    -------
    tuple[float, float]
        Límites ``(inferior, superior)`` en ``[0.0, 1.0]``, o ``(nan, nan)`` si ``total == 0``.
    """
    if total < 0 or exitos < 0 or exitos > total:
        raise ValueError(f"Conteos inválidos para Wilson: exitos={exitos}, total={total}.")
    if z <= 0:
        raise ValueError("El cuantil z debe ser estrictamente positivo.")
    if total == 0:
        return (math.nan, math.nan)

    p = exitos / total
    z2 = z * z
    denom = 1.0 + z2 / total
    centro = (p + z2 / (2.0 * total)) / denom
    margen = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)) / denom
    return (max(0.0, centro - margen), min(1.0, centro + margen))


def tasa_por_grupo(
    datos: pd.DataFrame,
    grupo: str,
    indicador: str,
    z: float = 1.96,
    orden: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Resume conteos, porcentaje de éxito e intervalo de Wilson por categoría de ``grupo``.

    Parámetros
    ----------
    datos : pd.DataFrame
        Tabla con las columnas ``grupo`` e ``indicador``.
    grupo : str
        Nombre de la columna categórica de agrupación.
    indicador : str
        Nombre de la columna booleana de éxito (p. ej. ``CoincideConEstimado``).
    z : float, opcional
        Valor crítico normal para el intervalo de Wilson (``1.96`` por defecto).
    orden : Sequence[str] | None, opcional
        Orden explícito de filas del grupo resultante.

    Retorna
    -------
    pd.DataFrame
        Tabla con ``grupo``, ``N``, ``Exitos``, ``Tasa``, ``TasaPct``, ``IC_Inf``,
        ``IC_Sup``, ``IC_InfPct`` e ``IC_SupPct``.
    """
    _validar_columnas(datos, (grupo, indicador), "tasa_por_grupo")
    limpia = datos.dropna(subset=[grupo, indicador]).copy()
    limpia["_ind"] = limpia[indicador].astype(bool)

    agrupado = limpia.groupby(grupo, observed=True)["_ind"].agg(N="size", Exitos="sum")
    if orden is not None:
        presentes = [cat for cat in orden if cat in agrupado.index]
        restantes = [cat for cat in agrupado.index if cat not in presentes]
        agrupado = agrupado.reindex(presentes + restantes)

    filas = []
    for nombre_grupo, fila in agrupado.iterrows():
        n = int(fila["N"])
        exitos = int(fila["Exitos"])
        tasa = exitos / n if n > 0 else math.nan
        ic_inf, ic_sup = intervalo_wilson(exitos, n, z=z)
        filas.append({
            grupo: nombre_grupo,
            "N": n,
            "Exitos": exitos,
            "Tasa": tasa,
            "TasaPct": tasa * 100.0 if pd.notna(tasa) else math.nan,
            "IC_Inf": ic_inf,
            "IC_Sup": ic_sup,
            "IC_InfPct": ic_inf * 100.0 if pd.notna(ic_inf) else math.nan,
            "IC_SupPct": ic_sup * 100.0 if pd.notna(ic_sup) else math.nan,
        })
    return pd.DataFrame(filas)


def guardar_figura(figura: Figure, ruta: Path | str, dpi: int = 200, cerrar: bool = True) -> Path:
    """Guarda una figura ``matplotlib`` creando directorios padres y devolviendo su ruta."""
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=dpi, bbox_inches="tight")
    if cerrar:
        plt.close(figura)
    return destino


def _agregar_pie_fuente(figura: Figure, nota: str = "") -> None:
    """Agrega la fuente oficial estandarizada (y una nota breve opcional) al pie de la figura."""
    texto = FUENTE_DATOS_F4 if not nota else f"{FUENTE_DATOS_F4} · {nota}"
    figura.text(0.01, -0.02, texto, fontsize=8.5, color="#4a5568", ha="left", va="top")


def calcular_medianas_iqr(serie: pd.Series) -> dict[str, float | int]:
    """Devuelve tamaño muestral, mediana, cuartiles, rango intercuartílico y extremos."""
    limpia = pd.to_numeric(serie, errors="coerce").dropna()
    n = int(len(limpia))
    if n == 0:
        return {
            "N": 0, "Mediana": math.nan, "Q1": math.nan, "Q3": math.nan,
            "IQR": math.nan, "Min": math.nan, "Max": math.nan,
        }
    q1 = float(limpia.quantile(0.25))
    mediana = float(limpia.median())
    q3 = float(limpia.quantile(0.75))
    return {
        "N": n,
        "Mediana": mediana,
        "Q1": q1,
        "Q3": q3,
        "IQR": q3 - q1,
        "Min": float(limpia.min()),
        "Max": float(limpia.max()),
    }


def preparar_comparables(licitaciones: pd.DataFrame, moneda: str | None = None) -> pd.DataFrame:
    """Filtra licitaciones comparables y agrega ``RazonMonto``, ``LogRazonMonto`` y ``SentidoBrecha``.

    Parámetros
    ----------
    licitaciones : pd.DataFrame
        Tabla agregada por licitación generada por F2/F3.
    moneda : str | None, opcional
        Código de moneda a filtrar (por ejemplo ``'CLP'``). Si es ``None``, conserva todas.

    Retorna
    -------
    pd.DataFrame
        Copia de las licitaciones con ``EstadoBrecha == 'Calculada'`` y las tres columnas nuevas.
    """
    requeridas = (
        "EstadoBrecha", "MonedaLicitacion", "MontoEstimadoLicitacion",
        "MontoTotalGanadoras", "BrechaMonto", "CoincideConEstimado",
    )
    _validar_columnas(licitaciones, requeridas, "preparar_comparables")

    comp = licitaciones.loc[licitaciones["EstadoBrecha"].eq("Calculada")].copy()
    if moneda is not None:
        comp = comp.loc[comp["MonedaLicitacion"].eq(moneda)].copy()
    if comp.empty:
        return comp.assign(RazonMonto=pd.Series(dtype="float64"),
                           LogRazonMonto=pd.Series(dtype="float64"),
                           SentidoBrecha=pd.Series(dtype="object"))

    est = pd.to_numeric(comp["MontoEstimadoLicitacion"], errors="coerce")
    gan = pd.to_numeric(comp["MontoTotalGanadoras"], errors="coerce")
    if not (est.gt(0).all() and gan.gt(0).all()):
        raise ValueError("Las licitaciones comparables deben tener montos positivos.")

    razon = gan / est
    coincide = comp["CoincideConEstimado"].astype(bool)
    brecha = pd.to_numeric(comp["BrechaMonto"], errors="coerce")
    sentido = np.where(
        coincide,
        "Coincide",
        np.where(brecha > 0, "Sobre el estimado", "Bajo el estimado"),
    )
    return comp.assign(
        RazonMonto=razon,
        LogRazonMonto=np.log(razon),
        SentidoBrecha=pd.Categorical(sentido, categories=ORDEN_SENTIDO, ordered=True),
    )


def asignar_tamano_ganador(licitaciones: pd.DataFrame, ofertas: pd.DataFrame) -> pd.DataFrame:
    """Agrega ``TamanoGanador`` por licitación desde las ofertas marcadas como ``Ganadora``.

    Si todas las filas ganadoras de una licitación comparten el mismo tamaño se conserva esa
    etiqueta (``Micro``, ``Pequeña``, ``Mediana``, ``Grande`` o ``NoClasificado``). Si concurren
    ganadoras de tamaños distintos en la misma licitación, se asigna explícitamente ``'Múltiple'``.
    """
    _validar_columnas(licitaciones, ("NroLicitacion",), "asignar_tamano_ganador (licitaciones)")
    _validar_columnas(
        ofertas, ("NroLicitacion", "ResultadoOferta", "TamanoProveedor"), "asignar_tamano_ganador (ofertas)"
    )

    gan = ofertas.loc[normalizar_codigo(ofertas["ResultadoOferta"]).eq("GANADORA")].copy()
    gan["NroLicitacion"] = normalizar_codigo(gan["NroLicitacion"])
    gan["TamanoProveedor"] = gan["TamanoProveedor"].astype("string").str.strip()

    resumen_tam = gan.groupby("NroLicitacion")["TamanoProveedor"].agg(
        unicos="nunique", primero="first"
    )
    etiquetas = np.where(resumen_tam["unicos"].gt(1), "Múltiple", resumen_tam["primero"])
    mapa = pd.Series(etiquetas, index=resumen_tam.index, name="TamanoGanador")

    codigos_lic = normalizar_codigo(licitaciones["NroLicitacion"])
    tamano_ganador = codigos_lic.map(mapa).fillna("Sin ganadora")
    tamano_ordinal = pd.Categorical(
        tamano_ganador.where(tamano_ganador.isin(ORDEN_TAMANO)),
        categories=ORDEN_TAMANO,
        ordered=True,
    )
    return licitaciones.assign(
        TamanoGanador=tamano_ganador,
        TamanoGanadorOrdinal=tamano_ordinal,
    )


def asignar_tamano_ganador_iterativo(
    licitaciones: pd.DataFrame, ofertas: pd.DataFrame,
) -> pd.DataFrame:
    """Referencia de F4 que reúne tamaños y asigna etiquetas fila por fila."""
    filas = zip(
        normalizar_codigo(ofertas["NroLicitacion"]),
        normalizar_codigo(ofertas["ResultadoOferta"]),
        ofertas["TamanoProveedor"].astype("string").str.strip(),
    )
    tamanos_por_codigo: dict[str, set[str]] = {}
    for codigo, resultado, tamano in filas:
        if pd.notna(codigo) and pd.notna(resultado) and resultado == "GANADORA" and pd.notna(tamano):
            tamanos_por_codigo.setdefault(codigo, set()).add(tamano)

    etiquetas = []
    for codigo in normalizar_codigo(licitaciones["NroLicitacion"]):
        tamanos = tamanos_por_codigo.get(codigo, ())
        etiquetas.append("Múltiple" if len(tamanos) > 1 else next(iter(tamanos), "Sin ganadora"))
    asignadas = pd.Series(np.asarray(etiquetas, dtype=object), index=licitaciones.index)
    return licitaciones.assign(
        TamanoGanador=asignadas,
        TamanoGanadorOrdinal=pd.Categorical(asignadas, categories=ORDEN_TAMANO, ordered=True),
    )


def resumen_sentido_por_moneda(comparables: pd.DataFrame, z: float = 1.96) -> pd.DataFrame:
    """Resume conteos y porcentajes de ``SentidoBrecha`` e IC Wilson de coincidencia por moneda."""
    _validar_columnas(
        comparables, ("MonedaLicitacion", "SentidoBrecha", "CoincideConEstimado"), "resumen_sentido_por_moneda"
    )
    tasas = tasa_por_grupo(comparables, "MonedaLicitacion", "CoincideConEstimado", z=z)
    conteos = (
        pd.crosstab(comparables["MonedaLicitacion"], comparables["SentidoBrecha"])
        .reindex(columns=ORDEN_SENTIDO, fill_value=0)
    )
    filas = []
    for _, fila in tasas.iterrows():
        moneda = fila["MonedaLicitacion"]
        n = int(fila["N"])
        c = conteos.loc[moneda] if moneda in conteos.index else pd.Series(0, index=ORDEN_SENTIDO)
        filas.append({
            "MonedaLicitacion": moneda,
            "Licitaciones": n,
            "BajoEstimado": int(c["Bajo el estimado"]),
            "BajoEstimadoPct": (int(c["Bajo el estimado"]) / n) * 100.0,
            "Coincide": int(c["Coincide"]),
            "CoincidePct": fila["TasaPct"],
            "IC95_InfPct": fila["IC_InfPct"],
            "IC95_SupPct": fila["IC_SupPct"],
            "SobreEstimado": int(c["Sobre el estimado"]),
            "SobreEstimadoPct": (int(c["Sobre el estimado"]) / n) * 100.0,
        })
    return pd.DataFrame(filas).sort_values("Licitaciones", ascending=False).reset_index(drop=True)


def resumen_magnitud_por_moneda(comparables: pd.DataFrame) -> pd.DataFrame:
    """Calcula mediana e IQR de ``BrechaMonto``, ``RazonMonto`` y ``LogRazonMonto`` por moneda."""
    _validar_columnas(
        comparables,
        ("MonedaLicitacion", "BrechaMonto", "RazonMonto", "LogRazonMonto", "CoincideConEstimado"),
        "resumen_magnitud_por_moneda",
    )
    filas = []
    for moneda, sub in comparables.groupby("MonedaLicitacion", observed=True):
        m_brecha = calcular_medianas_iqr(sub["BrechaMonto"])
        m_razon = calcular_medianas_iqr(sub["RazonMonto"])
        m_log = calcular_medianas_iqr(sub["LogRazonMonto"])
        filas.append({
            "MonedaLicitacion": moneda,
            "Licitaciones": int(len(sub)),
            "CoincidePct": float(sub["CoincideConEstimado"].astype(bool).mean() * 100.0),
            "MedianaBrecha": m_brecha["Mediana"],
            "Q1_Brecha": m_brecha["Q1"],
            "Q3_Brecha": m_brecha["Q3"],
            "IQR_Brecha": m_brecha["IQR"],
            "MedianaRazon": m_razon["Mediana"],
            "IQR_Razon": m_razon["IQR"],
            "MedianaLogRazon": m_log["Mediana"],
            "Q1_LogRazon": m_log["Q1"],
            "Q3_LogRazon": m_log["Q3"],
            "IQR_LogRazon": m_log["IQR"],
        })
    return pd.DataFrame(filas).sort_values("Licitaciones", ascending=False).reset_index(drop=True)


def tabla_resumen_por_tamano(
    comparables_con_tamano: pd.DataFrame,
    moneda: str | None = "CLP",
    incluir_especiales: bool = True,
    z: float = 1.96,
) -> pd.DataFrame:
    """Construye la tabla comparativa de coincidencia, brecha, razón y log-razón por tamaño ganador.

    Parámetros
    ----------
    comparables_con_tamano : pd.DataFrame
        Resultado de aplicar ``preparar_comparables`` y ``asignar_tamano_ganador``.
    moneda : str | None, opcional
        Moneda sobre la que se calculan las métricas de brecha en unidad monetaria
        (``'CLP'`` por defecto para evitar mezclar monedas).
    incluir_especiales : bool, opcional
        Si es ``True``, incluye ``NoClasificado`` y ``Múltiple`` junto a los cuatro tamaños ordinales.
    z : float, opcional
        Valor crítico normal para intervalos de Wilson (``1.96`` por defecto).

    Retorna
    -------
    pd.DataFrame
        Tabla ordenada con tasas, intervalos de Wilson, sentido, medianas e IQR por tamaño.
    """
    _validar_columnas(
        comparables_con_tamano,
        ("MonedaLicitacion", "TamanoGanador", "CoincideConEstimado", "BrechaMonto", "RazonMonto", "LogRazonMonto", "SentidoBrecha"),
        "tabla_resumen_por_tamano",
    )
    sub = comparables_con_tamano.copy()
    if moneda is not None:
        sub = sub.loc[sub["MonedaLicitacion"].eq(moneda)].copy()
    orden_grupos = ORDEN_TAMANOS_TABLA if incluir_especiales else ORDEN_TAMANO
    sub = sub.loc[sub["TamanoGanador"].isin(orden_grupos)].copy()
    if sub.empty:
        return pd.DataFrame()

    tasas = tasa_por_grupo(sub, "TamanoGanador", "CoincideConEstimado", z=z, orden=orden_grupos)
    sentidos = pd.crosstab(sub["TamanoGanador"], sub["SentidoBrecha"]).reindex(columns=ORDEN_SENTIDO, fill_value=0)
    filas = []
    for _, fila in tasas.iterrows():
        tam = fila["TamanoGanador"]
        grupo_df = sub.loc[sub["TamanoGanador"].eq(tam)]
        m_brecha = calcular_medianas_iqr(grupo_df["BrechaMonto"])
        m_razon = calcular_medianas_iqr(grupo_df["RazonMonto"])
        m_log = calcular_medianas_iqr(grupo_df["LogRazonMonto"])
        n = int(fila["N"])
        c_sent = sentidos.loc[tam] if tam in sentidos.index else pd.Series(0, index=ORDEN_SENTIDO)
        filas.append({
            "TamanoGanador": tam,
            "Licitaciones": n,
            "Coinciden": int(fila["Exitos"]),
            "TasaCoincidenciaPct": fila["TasaPct"],
            "IC95_InfPct": fila["IC_InfPct"],
            "IC95_SupPct": fila["IC_SupPct"],
            "BajoEstimadoPct": (int(c_sent["Bajo el estimado"]) / n) * 100.0,
            "SobreEstimadoPct": (int(c_sent["Sobre el estimado"]) / n) * 100.0,
            "MedianaBrecha": m_brecha["Mediana"],
            "IQR_Brecha": m_brecha["IQR"],
            "MedianaRazon": m_razon["Mediana"],
            "IQR_Razon": m_razon["IQR"],
            "MedianaLogRazon": m_log["Mediana"],
            "Q1_LogRazon": m_log["Q1"],
            "Q3_LogRazon": m_log["Q3"],
            "IQR_LogRazon": m_log["IQR"],
        })
    return pd.DataFrame(filas)


def graficar_coincidencia_y_sentido(comparables: pd.DataFrame) -> Figure:
    """Genera una figura con tasa de coincidencia (IC 95 % Wilson) y sentido de la brecha por moneda."""
    resumen = resumen_sentido_por_moneda(comparables)
    fig, (ax_izq, ax_der) = plt.subplots(1, 2, figsize=(12.5, 4.6), constrained_layout=True)

    etiquetas = [f"{m}\n(n={n:,})" for m, n in zip(resumen["MonedaLicitacion"], resumen["Licitaciones"])]
    y_pos = np.arange(len(resumen))
    tasas = resumen["CoincidePct"].to_numpy()
    err_inf = tasas - resumen["IC95_InfPct"].to_numpy()
    err_sup = resumen["IC95_SupPct"].to_numpy() - tasas

    ax_izq.barh(y_pos, tasas, xerr=[err_inf, err_sup], color="#2b6cb0", alpha=0.88, capsize=4)
    ax_izq.set_yticks(y_pos, etiquetas)
    ax_izq.invert_yaxis()
    ax_izq.set_xlim(0, 114)
    ax_izq.set_xlabel("Coincidencia con monto estimado (%) ± IC 95 % Wilson")
    ax_izq.set_title("Tasa de coincidencia por moneda")
    ax_izq.grid(axis="x", linestyle="--", alpha=0.35)
    for y, pct, e_sup in zip(y_pos, tasas, err_sup):
        ax_izq.text(min(pct + e_sup + 2.0, 102.0), y, f"{pct:.1f}%", va="center", fontsize=9)

    bajo = resumen["BajoEstimadoPct"].to_numpy()
    coincide = resumen["CoincidePct"].to_numpy()
    sobre = resumen["SobreEstimadoPct"].to_numpy()
    ax_der.barh(y_pos, bajo, label="Bajo el estimado", color="#2f855a")
    ax_der.barh(y_pos, coincide, left=bajo, label="Coincide", color="#2b6cb0")
    ax_der.barh(y_pos, sobre, left=bajo + coincide, label="Sobre el estimado", color="#c53030")
    ax_der.set_yticks(y_pos, etiquetas)
    ax_der.invert_yaxis()
    ax_der.set_xlim(0, 100)
    ax_der.set_xlabel("Participación (%)")
    ax_der.set_title("Sentido de la brecha por moneda")
    ax_der.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=True, fontsize=8.5)
    ax_der.grid(axis="x", linestyle="--", alpha=0.35)

    fig.suptitle("Objetivos 1 y 2 · Coincidencia y sentido de la brecha (separado por moneda)", fontsize=12)
    return fig


def graficar_distribucion_brecha(comparables: pd.DataFrame, moneda: str = "CLP") -> Figure:
    """Grafica la distribución de ``LogRazonMonto`` destacando coincidencia, mediana y cuartiles IQR."""
    _validar_columnas(comparables, ("MonedaLicitacion", "LogRazonMonto"), "graficar_distribucion_brecha")
    sub = comparables.loc[comparables["MonedaLicitacion"].eq(moneda), "LogRazonMonto"].dropna()
    if sub.empty:
        raise ValueError(f"No hay licitaciones comparables para la moneda '{moneda}'.")

    stats = calcular_medianas_iqr(sub)
    fig, ax = plt.subplots(figsize=(9.5, 4.4), constrained_layout=True)
    ax.hist(sub, bins=45, color="#3182ce", edgecolor="white", alpha=0.82)
    ax.axvline(0.0, color="#1a202c", linestyle="-", linewidth=1.6, label="Coincidencia exacta (log-razón = 0)")
    ax.axvline(stats["Mediana"], color="#dd6b20", linestyle="--", linewidth=1.6,
               label=f"Mediana = {stats['Mediana']:.3f}")
    ax.axvspan(stats["Q1"], stats["Q3"], color="#ecc94b", alpha=0.22,
               label=f"IQR [{stats['Q1']:.3f}, {stats['Q3']:.3f}] (amplitud {stats['IQR']:.3f})")
    ax.set_xlabel("Logaritmo natural de la razón (ln(MontoTotalGanadoras / MontoEstimadoLicitacion))")
    ax.set_ylabel("Cantidad de licitaciones")
    ax.set_title(f"Distribución de ln(razón) en {moneda} (n={stats['N']:,})")
    ax.legend(loc="upper left", frameon=True, fontsize=8.5)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    return fig


def graficar_resultados_por_tamano(tabla_tamano: pd.DataFrame, moneda: str = "CLP") -> Figure:
    """Genera una figura con tasa de coincidencia (Wilson) e intervalo [Q1, Q3] de ``LogRazonMonto``."""
    requeridas = (
        "TamanoGanador", "Licitaciones", "TasaCoincidenciaPct",
        "IC95_InfPct", "IC95_SupPct", "MedianaLogRazon", "Q1_LogRazon", "Q3_LogRazon",
    )
    _validar_columnas(tabla_tamano, requeridas, "graficar_resultados_por_tamano")
    if tabla_tamano.empty:
        raise ValueError("La tabla por tamaño está vacía.")

    fig, (ax_izq, ax_der) = plt.subplots(1, 2, figsize=(13.0, 4.8), constrained_layout=True)
    x_pos = np.arange(len(tabla_tamano))
    etiquetas = [f"{t}\n(n={n:,})" for t, n in zip(tabla_tamano["TamanoGanador"], tabla_tamano["Licitaciones"])]

    tasas = tabla_tamano["TasaCoincidenciaPct"].to_numpy()
    err_inf = tasas - tabla_tamano["IC95_InfPct"].to_numpy()
    err_sup = tabla_tamano["IC95_SupPct"].to_numpy() - tasas
    colores = ["#2b6cb0" if t in ORDEN_TAMANO else "#718096" for t in tabla_tamano["TamanoGanador"]]

    ax_izq.bar(x_pos, tasas, yerr=[err_inf, err_sup], color=colores, alpha=0.9, capsize=4)
    ax_izq.set_xticks(x_pos, etiquetas)
    ax_izq.set_ylim(0, 100)
    ax_izq.set_ylabel("Coincidencia (%) ± IC 95 % Wilson")
    ax_izq.set_title(f"Tasa de coincidencia por tamaño ganador ({moneda})")
    ax_izq.grid(axis="y", linestyle="--", alpha=0.35)
    for x, pct, e_sup in zip(x_pos, tasas, err_sup):
        ax_izq.text(x, pct + e_sup + 2.0, f"{pct:.1f}%", ha="center", va="bottom", fontsize=8.5)

    medianas = tabla_tamano["MedianaLogRazon"].to_numpy()
    err_q1 = medianas - tabla_tamano["Q1_LogRazon"].to_numpy()
    err_q3 = tabla_tamano["Q3_LogRazon"].to_numpy() - medianas
    ax_der.errorbar(x_pos, medianas, yerr=[err_q1, err_q3], fmt="o", color="#c53030",
                    ecolor="#e53e3e", elinewidth=2.0, capsize=5, markersize=7,
                    label="Mediana y rango IQR [Q1, Q3]")
    ax_der.axhline(0.0, color="#1a202c", linestyle="--", linewidth=1.2, label="Sin brecha (0)")
    ax_der.set_xticks(x_pos, etiquetas)
    ax_der.set_ylabel("ln(MontoTotalGanadoras / MontoEstimado)")
    ax_der.set_title(f"Mediana y rango intercuartílico de log-razón ({moneda})")
    ax_der.legend(loc="best", frameon=True, fontsize=8.5)
    ax_der.grid(axis="y", linestyle="--", alpha=0.35)

    fig.suptitle(f"Objetivo 3 · Coincidencia y magnitud relativa según tamaño ganador ({moneda})", fontsize=12)
    return fig


def construir_copia_graficar(licitaciones: pd.DataFrame, ofertas: pd.DataFrame) -> pd.DataFrame:
    """Construye la copia interpretable para F4 sin revertir escalamiento ni codificación.

    Agrega etiquetas legibles (``EtiquetaCoincidencia``), brecha relativa porcentual
    (``BrechaRelativaPct``), tramos interpretables en CLP (``TramoEstimado``) y el tamaño
    ganador por licitación manteniendo ``NoClasificado`` y ``Múltiple`` fuera de
    ``TamanoGanadorOrdinal``.
    """
    comparables = asignar_tamano_ganador(preparar_comparables(licitaciones), ofertas)
    etiqueta_coinc = comparables["CoincideConEstimado"].astype(bool).map({True: "Coincide", False: "Difiere"})
    brecha_rel_pct = (comparables["RazonMonto"] - 1.0) * 100.0

    es_clp = comparables["MonedaLicitacion"].eq("CLP")
    tramos_clp = pd.cut(
        comparables.loc[es_clp, "MontoEstimadoLicitacion"],
        bins=[0.0, 1_000_000.0, 10_000_000.0, 50_000_000.0, float("inf")],
        labels=ORDEN_TRAMOS_ESTIMADO[:4],
    ).astype(str)
    tramo_estimado = pd.Series("Otra moneda (no CLP)", index=comparables.index, dtype="string")
    tramo_estimado.loc[es_clp] = tramos_clp
    tramo_cat = pd.Categorical(tramo_estimado, categories=ORDEN_TRAMOS_ESTIMADO, ordered=True)

    return comparables.assign(
        EtiquetaCoincidencia=etiqueta_coinc,
        BrechaRelativaPct=brecha_rel_pct,
        TramoEstimado=tramo_cat,
    )


def tabla_control_confusion(
    copia_graficar: pd.DataFrame,
    moneda: str = "CLP",
    z: float = 1.96,
) -> pd.DataFrame:
    """Evalúa coincidencia por ``TamanoGanador`` estratificada dentro de ``TramoEstimado``."""
    _validar_columnas(
        copia_graficar,
        ("MonedaLicitacion", "TramoEstimado", "TamanoGanador", "CoincideConEstimado"),
        "tabla_control_confusion",
    )
    sub = copia_graficar.loc[
        copia_graficar["MonedaLicitacion"].eq(moneda)
        & copia_graficar["TamanoGanador"].isin(ORDEN_TAMANO)
    ].copy()
    if sub.empty:
        return pd.DataFrame()

    filas = []
    for tramo in ORDEN_TRAMOS_ESTIMADO[:4]:
        sub_tramo = sub.loc[sub["TramoEstimado"].eq(tramo)]
        if sub_tramo.empty:
            continue
        tasas = tasa_por_grupo(sub_tramo, "TamanoGanador", "CoincideConEstimado", z=z, orden=ORDEN_TAMANO)
        tasas_idx = tasas.set_index("TamanoGanador")
        tasa_micro = float(tasas_idx.loc["Micro", "TasaPct"]) if "Micro" in tasas_idx.index else math.nan
        tasa_grande = float(tasas_idx.loc["Grande", "TasaPct"]) if "Grande" in tasas_idx.index else math.nan
        brecha_pp = tasa_micro - tasa_grande
        for _, fila in tasas.iterrows():
            filas.append({
                "TramoEstimado": tramo,
                "TamanoGanador": fila["TamanoGanador"],
                "Licitaciones": int(fila["N"]),
                "Coinciden": int(fila["Exitos"]),
                "TasaCoincidenciaPct": fila["TasaPct"],
                "IC95_InfPct": fila["IC_InfPct"],
                "IC95_SupPct": fila["IC_SupPct"],
                "Brecha_Micro_vs_Grande_pp": brecha_pp,
                "MedianaBrechaRelativaPct": sub_tramo.loc[
                    sub_tramo["TamanoGanador"].eq(fila["TamanoGanador"]), "BrechaRelativaPct"
                ].median() if "BrechaRelativaPct" in sub_tramo else math.nan,
            })
    return pd.DataFrame(filas)


def comparar_muestras_feedback(
    licitaciones: pd.DataFrame,
    ofertas: pd.DataFrame,
    copias_adicionales: pd.Series | None = None,
) -> dict[str, pd.DataFrame]:
    """Reconstruye los totales ganadores a partir de las filas conservadas."""
    assert normalizar_codigo(licitaciones["NroLicitacion"]).is_unique
    assert ofertas["EsDuplicadoPotencial"].notna().all()
    marcas = ofertas["EsDuplicadoPotencial"]
    exclusiones = {}
    if copias_adicionales is not None:
        assert copias_adicionales.index.equals(ofertas.index)
        assert not (copias_adicionales & ~marcas).any()
        exclusiones["Sin copias adicionales"] = copias_adicionales
    exclusiones["Sin filas marcadas"] = marcas
    muestras = {"Original": construir_copia_graficar(licitaciones, ofertas)}
    for nombre, excluir in exclusiones.items():
        limpias = ofertas.loc[~excluir]
        muestras[nombre] = construir_copia_graficar(calcular_brecha(limpias), limpias)
    return muestras


def sensibilidad_iva(comparables: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Mide el pico y simula IVA solo en los casos CLP compatibles con redondeo a un peso."""
    razon = comparables["RazonMonto"]
    est = comparables["MontoEstimadoLicitacion"]
    diferencia = comparables["MontoTotalGanadoras"] * 1.19 - est
    centro = 1 / 1.19
    ventana = razon.between(0.835, 0.845)
    ajustables = ventana & diferencia.abs().le(1) & comparables["MonedaLicitacion"].eq("CLP")
    evidencia = comparables.assign(
        Ventana=ventana,
        BandaInferior=razon.ge(0.825) & razon.lt(0.835),
        BandaSuperior=razon.gt(0.845) & razon.le(0.855),
        ErrorRazonMenor1e4=(razon - centro).abs().le(0.0001),
        AjustablesCLP=ajustables,
    ).groupby("MonedaLicitacion", observed=True).agg(
        N=("RazonMonto", "size"),
        CercaIVA=("Ventana", "sum"),
        BandaInferior=("BandaInferior", "sum"),
        BandaSuperior=("BandaSuperior", "sum"),
        CercaIVAEstricta=("ErrorRazonMenor1e4", "sum"),
        AjustablesCLP=("AjustablesCLP", "sum"),
    )
    evidencia["CercaIVAPct"] = 100 * evidencia["CercaIVA"] / evidencia["N"]
    brecha = comparables["BrechaMonto"].mask(ajustables, diferencia)
    coincide = comparables["CoincideConEstimado"].astype(bool) | ajustables
    ajustada = razon.mask(ajustables, razon * 1.19)
    return evidencia.reset_index(), comparables.assign(
        RazonMonto=ajustada,
        LogRazonMonto=np.log(ajustada),
        BrechaMonto=brecha,
        BrechaRelativaPct=100 * (ajustada - 1),
        EtiquetaCoincidencia=coincide.map({True: "Coincide", False: "Difiere"}),
        CoincideConEstimado=coincide,
        SentidoBrecha=comparables["SentidoBrecha"].mask(ajustables, "Coincide"),
    )


def magnitud_por_sentido(comparables: pd.DataFrame) -> pd.DataFrame:
    """Describe la brecha por moneda y sentido usando la moneda como denominador."""
    filas = []
    for moneda, sub in comparables.groupby("MonedaLicitacion", observed=True):
        for sentido in ORDEN_SENTIDO:
            grupo = sub.loc[sub["SentidoBrecha"].eq(sentido)]
            fila = {"Moneda": moneda, "Sentido": sentido, "N": len(grupo),
                    "PctMoneda": 100 * len(grupo) / len(sub)}
            for columna in ("BrechaMonto", "RazonMonto", "LogRazonMonto"):
                estadisticos = calcular_medianas_iqr(grupo[columna])
                for medida in ("Mediana", "IQR"):
                    fila[f"{medida}_{columna}"] = estadisticos[medida]
            filas.append(fila)
    return pd.DataFrame(filas)


def tasas_exclusion_tamano(comparables: pd.DataFrame) -> pd.DataFrame:
    """Da las tasas globales para las exclusiones individuales y conjuntas."""
    tamano = comparables["TamanoGanador"]
    escenarios = {
        "Todas las comparables": tamano.notna(),
        "Sin Múltiple": tamano.ne("Múltiple"),
        "Sin NoClasificado": tamano.ne("NoClasificado"),
        "Solo tamaños ordinales": tamano.isin(ORDEN_TAMANO),
    }
    filas = []
    for escenario, incluir in escenarios.items():
        grupo = comparables.loc[incluir, "CoincideConEstimado"].astype(bool)
        tasa = 100 * grupo.mean()
        filas.append({"Filtro": escenario, "N": len(grupo), "Excluidas": len(tamano) - len(grupo),
                      "Coinciden": int(grupo.sum()), "TasaPct": tasa,
                      "Diferencia_vs_55_6_pp": tasa - 55.6})
    return pd.DataFrame(filas)


def pruebas_por_tamano(comparables: pd.DataFrame) -> pd.DataFrame:
    """Contrasta coincidencia y brecha relativa entre los cuatro tamaños ordinales."""
    assert normalizar_codigo(comparables["NroLicitacion"]).is_unique
    sub = comparables.loc[comparables["TamanoGanadorOrdinal"].notna()]
    tabla = pd.crosstab(sub["TamanoGanadorOrdinal"], sub["CoincideConEstimado"])
    esperado_minimo = estadistico = p_chi = math.nan
    if tabla.shape == (len(ORDEN_TAMANO), 2):
        chi = chi2_contingency(tabla, correction=False)
        esperado_minimo = chi.expected_freq.min()
        if esperado_minimo >= 5:
            estadistico, p_chi = chi.statistic, chi.pvalue

    ordinal = sub["TamanoGanadorOrdinal"].cat.codes
    brecha = sub["BrechaRelativaPct"]
    rho = p_spearman = math.nan
    if len(sub) > 2 and ordinal.nunique() > 1 and brecha.nunique() > 1:
        rho, p_spearman = spearmanr(ordinal, brecha)
    return pd.DataFrame([
        {"Prueba": "Chi-cuadrado de Pearson", "N": len(sub), "Estadístico": estadistico,
         "p": p_chi, "Mínimo esperado": esperado_minimo},
        {"Prueba": "Spearman", "N": len(sub), "Estadístico": rho, "p": p_spearman},
    ])


def graficar_coincidencia_por_tamano(
    tabla_tamano: pd.DataFrame,
    tasa_global_pct: float = 55.56047851129818,
    n_global: tuple[int, int] = (1254, 2257),
) -> Figure:
    """Figura 1 (OE1/OE3): barras de coincidencia por tamaño con IC de Wilson y referencia global."""
    requeridas = ("TamanoGanador", "Licitaciones", "TasaCoincidenciaPct", "IC95_InfPct", "IC95_SupPct")
    _validar_columnas(tabla_tamano, requeridas, "graficar_coincidencia_por_tamano")
    if tabla_tamano.empty:
        raise ValueError("La tabla por tamaño está vacía.")

    fig, ax = plt.subplots(figsize=(10.5, 5.0), constrained_layout=True)
    x_pos = np.arange(len(tabla_tamano))
    etiquetas = [f"{t}\n(n={n:,})" for t, n in zip(tabla_tamano["TamanoGanador"], tabla_tamano["Licitaciones"])]

    tasas = tabla_tamano["TasaCoincidenciaPct"].to_numpy()
    err_inf = tasas - tabla_tamano["IC95_InfPct"].to_numpy()
    err_sup = tabla_tamano["IC95_SupPct"].to_numpy() - tasas
    colores = ["#2b6cb0" if t in ORDEN_TAMANO else "#718096" for t in tabla_tamano["TamanoGanador"]]

    ax.bar(x_pos, tasas, yerr=[err_inf, err_sup], color=colores, alpha=0.9, capsize=5, width=0.62)
    ax.axhline(
        tasa_global_pct,
        color="#dd6b20",
        linestyle="--",
        linewidth=1.8,
        label=f"Tasa global OE1: {tasa_global_pct:.1f}% ({n_global[0]:,} de {n_global[1]:,} comparables)",
    )
    ax.set_xticks(x_pos, etiquetas)
    ax.set_ylim(0, 95)
    ax.set_ylabel("Tasa de coincidencia con monto estimado (%)")
    ax.set_xlabel("Tamaño del proveedor ganador (eje ordinal: Micro–Grande; grupos aparte en gris)")
    tasa_txt = f"{tasa_global_pct:.1f}".replace(".", ",")
    ax.set_title(
        f"El monto estimado coincide con el total de las ofertas ganadoras en el {tasa_txt} % de las licitaciones comparables",
        fontsize=10.8,
        fontweight="bold",
        pad=10,
    )
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    for x, pct, e_sup in zip(x_pos, tasas, err_sup):
        ax.text(x, pct + e_sup + 2.0, f"{pct:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    _agregar_pie_fuente(fig, "Barras de error: IC 95 % método Wilson")
    return fig


def graficar_razon_escala_log(
    comparables: pd.DataFrame,
    rango: tuple[float, float] = (0.05, 20.0),
) -> Figure:
    """Figura 2 (OE2): histograma de la razón ganador/estimado en escala log con marcas en 1 y 1/1,19."""
    _validar_columnas(comparables, ("RazonMonto",), "graficar_razon_escala_log")
    razon = pd.to_numeric(comparables["RazonMonto"], errors="coerce").dropna()
    razon = razon[razon > 0]
    if razon.empty:
        raise ValueError("No hay razones positivas para graficar.")

    en_rango = razon[(razon >= rango[0]) & (razon <= rango[1])]
    fuera = int(len(razon) - len(en_rango))
    n_exacto = int(comparables["CoincideConEstimado"].astype(bool).sum()) if "CoincideConEstimado" in comparables else int((razon == 1.0).sum())
    n_iva = int(((razon >= 0.835) & (razon <= 0.845)).sum())
    marca_iva = 1.0 / 1.19

    bins = np.logspace(np.log10(rango[0]), np.log10(rango[1]), 45)
    fig, ax = plt.subplots(figsize=(10.5, 5.0), constrained_layout=True)
    ax.hist(en_rango, bins=bins, color="#3182ce", edgecolor="white", alpha=0.84)
    ax.set_xscale("log")
    ax.set_xlim(rango[0], rango[1])

    ticks = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
    ax.set_xticks(ticks, [f"{t:g}" for t in ticks])

    ax.axvline(1.0, color="#1a202c", linestyle="-", linewidth=1.8, label=f"Razón = 1 (coincidencia exacta, n={n_exacto:,})")
    ax.axvline(marca_iva, color="#c53030", linestyle="--", linewidth=1.8,
               label=f"Razón = 1/1,19 ≈ 0,840 (n={n_iva:,} en [0,835; 0,845])")

    y_max = ax.get_ylim()[1]
    ax.set_ylim(0, y_max * 1.15)
    ax.annotate(
        f"1/1,19 ≈ 0,840\n(n={n_iva:,})",
        xy=(marca_iva, y_max * 0.62),
        xytext=(0.24, y_max * 0.78),
        arrowprops={"arrowstyle": "->", "color": "#c53030", "lw": 1.3},
        ha="center",
        fontsize=9,
        color="#9b2c2c",
        fontweight="bold",
    )
    ax.annotate(
        f"Razón = 1\n(n={n_exacto:,})",
        xy=(1.0, y_max * 0.94),
        xytext=(2.3, y_max * 0.96),
        arrowprops={"arrowstyle": "->", "color": "#1a202c", "lw": 1.3},
        ha="left",
        va="top",
        fontsize=9,
        color="#1a202c",
        fontweight="bold",
    )

    ax.set_xlabel("Razón MontoTotalGanadoras / MontoEstimadoLicitacion (adimensional, escala logarítmica)")
    ax.set_ylabel("Cantidad de licitaciones (n)")
    ax.set_title(
        f"Coinciden {n_exacto:,} licitaciones y {n_iva:,} se concentran cerca de 1/1,19",
        fontsize=11.5,
        fontweight="bold",
        pad=10,
    )
    ax.legend(loc="upper right", frameon=True, fontsize=8.8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    _agregar_pie_fuente(
        fig,
        f"Ventana [{rango[0]:g}; {rango[1]:g}]: {len(en_rango):,} de {len(razon):,} comparables ({fuera:,} casos extremos omitidos)",
    )
    return fig


def graficar_cajas_brecha_relativa(
    copia_graficar: pd.DataFrame,
    y_lim: tuple[float, float] = (-115.0, 520.0),
) -> Figure:
    """Figura 3 (OE3): cajas de la brecha relativa (%) por tamaño ganador con n por categoría."""
    _validar_columnas(
        copia_graficar,
        ("TamanoGanador", "BrechaRelativaPct"),
        "graficar_cajas_brecha_relativa",
    )
    categorias = [c for c in ORDEN_TAMANOS_TABLA if c in set(copia_graficar["TamanoGanador"])]
    series = [
        copia_graficar.loc[copia_graficar["TamanoGanador"].eq(cat), "BrechaRelativaPct"].dropna().to_numpy()
        for cat in categorias
    ]
    if not series:
        raise ValueError("No hay datos de BrechaRelativaPct para graficar.")

    etiquetas = [f"{cat}\n(n={len(arr):,})" for cat, arr in zip(categorias, series)]
    fig, ax = plt.subplots(figsize=(10.5, 5.0), constrained_layout=True)

    caja = ax.boxplot(
        series,
        tick_labels=etiquetas,
        showfliers=False,
        patch_artist=True,
        medianprops={"color": "#1a202c", "linewidth": 2.0},
        whiskerprops={"color": "#4a5568", "linewidth": 1.3},
        capprops={"color": "#4a5568", "linewidth": 1.3},
    )
    for patch, cat in zip(caja["boxes"], categorias):
        patch.set_facecolor("#63b3ed" if cat in ORDEN_TAMANO else "#cbd5e0")
        patch.set_edgecolor("#2c5282" if cat in ORDEN_TAMANO else "#4a5568")
        patch.set_alpha(0.85)

    ax.axhline(0.0, color="#dd6b20", linestyle="--", linewidth=1.6, label="Sin brecha (0 %)")
    ax.set_ylim(y_lim[0], y_lim[1])
    ax.set_ylabel("Brecha relativa respecto al estimado (%)")
    ax.set_xlabel("Tamaño del proveedor ganador (NoClasificado y Múltiple fuera del eje ordinal)")
    ax.set_title(
        "Mediana en 0 % para tamaños individuales y sesgo positivo marcado en adjudicaciones Múltiples (+151,2 %)",
        fontsize=11.0,
        fontweight="bold",
        pad=10,
    )
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    if "Múltiple" in categorias:
        idx_mult = categorias.index("Múltiple") + 1
        med_mult = float(np.median(series[idx_mult - 1]))
        med_txt = f"+{med_mult:.1f} %".replace(".", ",")
        ax.annotate(
            f"Mediana: {med_txt}\n(bigote sup. +1.084,6 %)",
            xy=(idx_mult - 0.18, med_mult),
            xytext=(idx_mult - 1.35, med_mult + 45.0),
            arrowprops={"arrowstyle": "->", "color": "#1a202c", "lw": 1.4},
            fontsize=8.8,
            fontweight="bold",
            ha="center",
            va="center",
            color="#1a202c",
        )

    _agregar_pie_fuente(fig, "Cajas [Q1, Q3] y bigotes 1,5×IQR (showfliers=False por estimados simbólicos)")
    return fig
