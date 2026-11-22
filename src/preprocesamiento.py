"""Reglas del preprocesamiento de licitaciones (Fase 2), reutilizadas por el pipeline de F3."""

from pathlib import Path
from typing import TypedDict
import hashlib
import re
import unicodedata

import numpy as np
import pandas as pd


FECHAS = ("FechaPublicacion", "FechaCierre", "FechaAdjudicacion")
MONTOS = ("MontoNetoOferta", "MontoTotalOferta", "MontoEstimadoLicitacion")
ORDEN_TAMANO = ("Micro", "Pequeña", "Mediana", "Grande")
REQUERIDAS = {
    *FECHAS, *MONTOS, "NroLicitacion", "MonedaLicitacion",
    "MonedaOferta", "TamanoProveedor", "ResultadoOferta",
}
SHA256_RAW_LF = "ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf"
# Archivo público de Mercado Público (04LicitacionesEne.csv dentro de Municipalidades.7z),
# con Proveedor y ProveedorRUT y sin el paso por Excel. Ver decisión 19 en docs/decisiones.md.
SHA256_FUENTE_PUBLICA_LF = "9e1a0589a4baf07909bc04e72a5b026574e02e11203e4908ed75d582526b2909"
URL_FUENTE_PUBLICA = "https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z"


def _mensaje_instrucciones_raw(motivo: str) -> str:
    """Construye un mensaje uniforme con los pasos de descarga y verificación SHA-256."""
    return (
        f"{motivo}\n"
        "Instrucciones de descarga:\n"
        "1. Copia exacta del proyecto (reproduce las salidas versionadas): 04LicitacionesEne.zip "
        "en OneDrive con cuenta UNAB (enlace en data/raw/README.md).\n"
        f"   Fuente pública sin cuenta (Mercado Público, ChileCompra): {URL_FUENTE_PUBLICA}. Tiene otro SHA-256 "
        "y sirve para revisar el origen y comprobar la equivalencia con pytest, no para ejecutar F2 y F3.\n"
        "2. Deja el CSV en data/raw/04LicitacionesEne.csv sin abrirlo ni guardarlo con Excel.\n"
        f"3. Verifica que su SHA-256 sin '\\r' (LF) sea {SHA256_RAW_LF} (ver data/raw/README.md)."
    )


def calcular_sha256_sin_cr(ruta: Path, tamano_bloque: int = 1024 * 1024) -> str:
    """Calcula el SHA-256 del archivo ignorando bytes ``\\r`` para equiparar CRLF y LF."""
    destino = Path(ruta)
    if not destino.is_file():
        raise FileNotFoundError(
            _mensaje_instrucciones_raw(f"No se encontró el archivo de entrada: {destino}")
        )
    digest = hashlib.sha256()
    with destino.open("rb") as archivo:
        while bloque := archivo.read(tamano_bloque):
            digest.update(bloque.replace(b"\r", b""))
    return digest.hexdigest()


def identificar_raw(
    ruta: Path,
    hash_proyecto: str = SHA256_RAW_LF,
    hash_publico: str = SHA256_FUENTE_PUBLICA_LF,
) -> str:
    """Indica qué archivo hay en ``ruta``: ``"proyecto"``, ``"publico"``, ``"otro"`` o ``"ausente"``.

    ``"proyecto"`` es la copia con la que se ejecutan los notebooks (Opción A de
    ``data/raw/README.md``); ``"publico"`` es el archivo de Mercado Público (Opción B).
    """
    destino = Path(ruta)
    if not destino.is_file():
        return "ausente"
    actual = calcular_sha256_sin_cr(destino)
    if actual == hash_proyecto.strip().lower():
        return "proyecto"
    if actual == hash_publico.strip().lower():
        return "publico"
    return "otro"


def verificar_hash_raw(ruta: Path, hash_esperado: str = SHA256_RAW_LF) -> str:
    """Verifica que ``ruta`` exista y su SHA-256 (sin ``\\r``) coincida con ``hash_esperado``."""
    esperado = hash_esperado.strip().lower()
    actual = calcular_sha256_sin_cr(ruta)
    if actual == SHA256_FUENTE_PUBLICA_LF and esperado != actual:
        raise ValueError(
            f"{ruta} es el archivo público de Mercado Público (Opción B en data/raw/README.md), "
            "no la copia del proyecto.\n"
            "El archivo público sirve para revisar el origen de los datos y para comprobar, con "
            "pytest, que entrega las mismas cifras del análisis (tests/test_regresion_f2.py).\n"
            "F2 y F3 se ejecutan con la copia del proyecto (Opción A), cuyo SHA-256 garantiza que "
            "se reproducen byte a byte las salidas versionadas en data/processed/. "
            "Ver la decisión 19 en docs/decisiones.md.\n\n"
            + _mensaje_instrucciones_raw("Para ejecutar F2 y F3:")
        )
    if actual != esperado:
        raise ValueError(
            _mensaje_instrucciones_raw(
                f"El SHA-256 sin '\\r' de {ruta} ({actual}) no coincide con el esperado ({esperado}). "
                "Posible archivo alterado (por ejemplo, guardado en Excel) o versión distinta."
            )
        )
    return actual


def es_columna_privada(columna: str) -> bool:
    """Recibe un encabezado y devuelve si coincide con identificadores directos conocidos."""
    nombre = unicodedata.normalize("NFKD", columna).encode("ascii", "ignore").decode()
    nombre = re.sub(r"[^a-z0-9]", "", nombre.lower())
    return nombre in {"proveedor", "rut", "nombreproveedor", "razonsocial"} or (
        "proveedor" in nombre
        and any(campo in nombre for campo in (
            "rut", "nombre", "razonsocial", "correo", "email", "telefono",
            "direccion", "especificaciones",
        ))
    )


def cargar_csv(ruta: Path, verificar_hash: bool = False) -> pd.DataFrame:
    """Lee el CSV local sin identificadores directos y devuelve las filas con esquema validado.

    Declara el separador `;` en vez de detectarlo: la medición de F3 (sección 4.3)
    mostró que entrega el mismo resultado con menos tiempo y memoria. Si ``verificar_hash``
    es ``True``, comprueba previamente el SHA-256 sin ``\\r`` mediante ``verificar_hash_raw()``.
    """
    if verificar_hash:
        verificar_hash_raw(ruta)
    datos = pd.read_csv(
        ruta, sep=";", encoding="latin-1",
        usecols=lambda columna: not es_columna_privada(columna),
        dtype={"NroLicitacion": "string"},
    )
    faltan = REQUERIDAS.difference(datos.columns)
    if faltan:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltan)}")
    return datos


def perfilar_columnas(datos: pd.DataFrame) -> pd.DataFrame:
    """Recibe las filas y devuelve un perfil agregado por columna sin mostrar valores."""
    return pd.DataFrame({
        "Tipo": datos.dtypes.astype(str),
        "Nulos": datos.isna().sum(),
        "% nulos": (datos.isna().mean() * 100).round(2),
        "Valores distintos": datos.nunique(),
    })


def convertir_tipos(datos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convierte fechas y montos; devuelve una copia y los conteos de fallos por campo."""
    resultado = datos.copy()
    controles = []
    for columna in (*FECHAS, *MONTOS):
        original = datos[columna].astype("string").str.strip()
        if columna in FECHAS:
            convertido = pd.to_datetime(
                original, format="%d-%m-%Y %H:%M", errors="coerce"
            )
        else:
            convertido = pd.to_numeric(
                original.str.replace(",", ".", regex=False), errors="coerce"
            ).astype("Float64")
            convertido = convertido.where(np.isfinite(convertido).fillna(False))
        resultado[columna] = convertido
        controles.append({
            "Columna": columna,
            "Nulos en entrada": int(datos[columna].isna().sum()),
            "Fallos de conversión": int(
                (original.notna() & original.ne("") & convertido.isna()).sum()
            ),
        })
    return resultado, pd.DataFrame(controles).set_index("Columna")


def ordenar_tamano(datos: pd.DataFrame) -> pd.DataFrame:
    """Añade el tamaño ordinal a una copia y rechaza etiquetas fuera de las reglas."""
    tamano = datos["TamanoProveedor"].astype("string").str.strip()
    categorias = {valor.casefold(): valor for valor in (*ORDEN_TAMANO, "NoClasificado")}
    normalizado = tamano.str.casefold().map(categorias)
    inesperados = tamano[tamano.notna() & normalizado.isna()].unique().tolist()
    if inesperados:
        raise ValueError(f"Categorías de TamanoProveedor sin regla: {inesperados}")
    ordinal = normalizado.where(normalizado.isin(ORDEN_TAMANO))
    return datos.assign(
        TamanoProveedorOrdinal=pd.Categorical(ordinal, categories=ORDEN_TAMANO, ordered=True)
    )


def ofertas_clp_validas(datos: pd.DataFrame) -> pd.Series:
    """Devuelve la máscara de ofertas en CLP con monto positivo."""
    moneda = datos["MonedaOferta"].astype("string").str.strip().str.upper()
    return (moneda.eq("CLP") & datos["MontoTotalOferta"].gt(0)).fillna(False)


class LimitesIQR(TypedDict):
    """Parámetros del IQR ajustado para los montos CLP."""

    ofertas_validas: int
    q1_log: float
    q3_log: float
    inferior_log: float
    superior_log: float


def calcular_limites_iqr(datos: pd.DataFrame) -> LimitesIQR | None:
    """Ajusta límites IQR sobre el log natural de montos CLP positivos; requiere cuatro ofertas."""
    montos = datos.loc[ofertas_clp_validas(datos), "MontoTotalOferta"]
    if len(montos) < 4:
        return None
    q1, q3 = np.log(montos).quantile([0.25, 0.75])
    iqr = q3 - q1
    return {
        "ofertas_validas": len(montos), "q1_log": float(q1), "q3_log": float(q3),
        "inferior_log": float(q1 - 1.5 * iqr), "superior_log": float(q3 + 1.5 * iqr),
    }


def aplicar_bandera_atipicos(datos: pd.DataFrame, limites: LimitesIQR | None) -> pd.DataFrame:
    """Devuelve las ofertas con una bandera extrema; deja vacías las filas sin evaluación."""
    bandera = pd.Series(pd.NA, index=datos.index, dtype="boolean")
    if limites is not None:
        evaluadas = ofertas_clp_validas(datos)
        monto = np.log(datos.loc[evaluadas, "MontoTotalOferta"])
        bandera.loc[evaluadas] = (
            monto.lt(limites["inferior_log"]) | monto.gt(limites["superior_log"])
        )
    return datos.assign(EsExtremoLogIQR_CLP=bandera)


MOTIVOS = {
    "NroLicitacion": "Identifica la licitación. Sin código, la fila queda fuera de la agregación.",
    "FechaPublicacion": "Permite describir cuándo se publicó. Se desconoce la fecha si falta.",
    "FechaCierre": "Permite describir el plazo de recepción cuando existe.",
    "FechaAdjudicacion": "Permite estudiar fechas de adjudicación observadas.",
    "MontoEstimadoLicitacion": "Referencia de comparación. Sin monto válido se excluye la licitación.",
    "MontoTotalOferta": "Importe por oferta e ítem. Si falta en una ganadora, la suma sería parcial.",
    "MontoNetoOferta": "Permite revisar el precio informado antes de multiplicar por cantidad.",
    "CantidadOferta": "Permite contrastar el cálculo del monto total cuando está informada.",
    "MonedaLicitacion": "Unidad del estimado. Si falta, no puede verificarse la compatibilidad.",
    "MonedaOferta": "Unidad de la oferta. Si falta en una ganadora, no se comparan los montos.",
    "ResultadoOferta": "Identifica las ofertas ganadoras. Si falta, puede faltar parte del total.",
    "TamanoProveedor": "Describe tamaño. Una ausencia queda sin rango ordinal.",
    "CodigoProductoONU": "Permite segmentar por producto cuando hay código.",
    "MontoEstimadoVisible": "Distingue visibilidad pública del monto; vacío significa desconocido.",
}

CONTEXTO_ESTIMADO = ("BaseEstimacionMontoLicitacion", "JustificacionMontoEstimado")


def tratar_faltantes(
    datos: pd.DataFrame, nulos_entrada: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normaliza blancos y devuelve los datos y una decisión de uso/exportación por columna."""
    resultado = datos.replace(r"^\s*$", pd.NA, regex=True)
    control = pd.DataFrame({
        "Nulos al leer": nulos_entrada,
        "Nulos después de convertir y normalizar": resultado.isna().sum(),
        "% faltantes": resultado.isna().mean().mul(100),
    })
    control["Regla"] = "Excluir del CSV analítico"
    control["Motivo"] = "Columna fuera del conjunto de variables del análisis."
    for columna in control.index.intersection(MOTIVOS):
        control.loc[columna, ["Regla", "Motivo"]] = [
            "Conservar faltantes", MOTIVOS[columna],
        ]
    for columna in control.index.intersection(CONTEXTO_ESTIMADO):
        control.loc[columna, ["Regla", "Motivo"]] = [
            "Usar solo para indicadores agregados",
            "Aporta contexto sobre el origen del estimado; se omite el texto en el CSV.",
        ]
    vacias_no_usadas = control["% faltantes"].eq(100) & control["Regla"].eq(
        "Excluir del CSV analítico"
    )
    control.loc[vacias_no_usadas, "Motivo"] = "Sin observaciones y fuera del análisis."
    return resultado, control


def marcar_duplicados(datos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Marca coincidencias exactas sin eliminar filas y devuelve el resumen por resultado."""
    duplicado = datos.duplicated(keep=False)
    extra = datos.duplicated()
    resumen = (
        datos.assign(FilasEnGrupoIdentico=duplicado, FilasAdicionales=extra)
        .groupby("ResultadoOferta", dropna=False)[["FilasEnGrupoIdentico", "FilasAdicionales"]]
        .sum()
    )
    return datos.assign(EsDuplicadoPotencial=duplicado), resumen


def normalizar_codigo(valores: pd.Series) -> pd.Series:
    """Devuelve los valores de código en mayúsculas y sin espacios exteriores."""
    return valores.astype("string").str.strip().str.upper().replace("", pd.NA)


def calcular_brecha(datos: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por licitación y devuelve la diferencia entre la suma ganadora y el estimado válido."""
    filas = datos.assign(
        NroLicitacion=normalizar_codigo(datos["NroLicitacion"]),
        MonedaLicitacion=normalizar_codigo(datos["MonedaLicitacion"]),
        MonedaOferta=normalizar_codigo(datos["MonedaOferta"]),
        ResultadoOferta=normalizar_codigo(datos["ResultadoOferta"]),
    ).dropna(subset=["NroLicitacion"])
    ganadora = filas["ResultadoOferta"].eq("GANADORA").fillna(False)
    estimado = filas["MontoEstimadoLicitacion"]
    monto = filas["MontoTotalOferta"]
    moneda_distinta = ~filas["MonedaOferta"].eq(filas["MonedaLicitacion"]).fillna(False)
    ganador_invalido = ganadora & (~monto.gt(0).fillna(False) | ~np.isfinite(monto).fillna(False))
    estimado_invalido = ~estimado.gt(0).fillna(False) | ~np.isfinite(estimado).fillna(False)
    filas = filas.assign(
        EsGanadora=ganadora,
        MontoGanadora=monto.where(ganadora),
        GanadoraInvalida=ganador_invalido,
        GanadoraMonedaDistinta=ganadora & moneda_distinta,
        GanadoraDuplicada=ganadora & filas["EsDuplicadoPotencial"],
        ResultadoFaltante=filas["ResultadoOferta"].isna(),
        EstimadoInvalido=estimado_invalido,
        MonedaEstimadaFaltante=filas["MonedaLicitacion"].isna(),
    )
    grupos = filas.groupby("NroLicitacion", sort=False)
    resumen = grupos.agg(
        FilasOferta=("EsGanadora", "size"),
        OfertasGanadoras=("EsGanadora", "sum"),
        MontoEstimadoLicitacion=("MontoEstimadoLicitacion", "first"),
        MonedaLicitacion=("MonedaLicitacion", "first"),
        EstimadosDistintos=("MontoEstimadoLicitacion", "nunique"),
        MonedasEstimadasDistintas=("MonedaLicitacion", "nunique"),
        EstimadoInvalido=("EstimadoInvalido", "any"),
        MonedaEstimadaFaltante=("MonedaEstimadaFaltante", "any"),
        ResultadoFaltante=("ResultadoFaltante", "any"),
        GanadoraInvalida=("GanadoraInvalida", "any"),
        GanadoraMonedaDistinta=("GanadoraMonedaDistinta", "any"),
        GanadoraDuplicada=("GanadoraDuplicada", "any"),
    )
    criterios = {
        "Ganadora con moneda distinta o faltante": resumen["GanadoraMonedaDistinta"],
        "Ganadora con monto inválido": resumen["GanadoraInvalida"],
        "Estimado inválido o inconsistente": resumen["EstimadoInvalido"] | resumen["EstimadosDistintos"].ne(1),
        "Moneda estimada faltante o inconsistente": (
            resumen["MonedaEstimadaFaltante"] | resumen["MonedasEstimadasDistintas"].ne(1)
        ),
        "Sin ofertas ganadoras": resumen["OfertasGanadoras"].eq(0),
        "Resultado de oferta faltante": resumen["ResultadoFaltante"],
    }
    estado = pd.Series("Calculada", index=resumen.index, dtype="string")
    for motivo, condicion in criterios.items():
        estado = estado.mask(condicion, motivo)
    comparables = estado.eq("Calculada")
    resumen["MontoTotalGanadoras"] = grupos["MontoGanadora"].sum(min_count=1).where(comparables)
    resumen["BrechaMonto"] = resumen["MontoTotalGanadoras"] - resumen["MontoEstimadoLicitacion"]
    resumen["EstadoBrecha"] = estado
    resumen["CoincideConEstimado"] = (
        resumen["BrechaMonto"].abs().le(1e-8).where(comparables)
    )
    if "MontoEstimadoVisible" in filas:
        visibles = normalizar_codigo(filas["MontoEstimadoVisible"]).str.replace("Í", "I")
        por_licitacion = visibles.groupby(filas["NroLicitacion"])
        visibilidad = por_licitacion.first().fillna("SIN DATO")
        visibilidad = visibilidad.where(visibilidad.isin(["SI", "NO", "SIN DATO"]), "OTRO")
        resumen["VisibilidadEstimado"] = visibilidad.mask(
            por_licitacion.nunique().gt(1), "INCONSISTENTE"
        )
    for columna in CONTEXTO_ESTIMADO:
        if columna in filas:
            texto = filas[columna].astype("string")
            indicios = pd.DataFrame({
                "Informada": texto.notna(),
                "MencionaAdjudicacion": texto.str.contains(
                    r"adjudic|ganador|monto ofertado", case=False, regex=True, na=False
                ),
                "MencionaPresupuesto": texto.str.contains(
                    r"presupuesto|cotizaci|mercado", case=False, regex=True, na=False
                ),
            })
            resumen = resumen.join(
                indicios.groupby(filas["NroLicitacion"]).any().add_prefix(columna + "_")
            )
    return resumen.reset_index()


def validar_procesado(
    ofertas: pd.DataFrame, licitaciones: pd.DataFrame, filas_originales: int,
    limites: LimitesIQR | None,
) -> list[str]:
    """Comprueba cardinalidad, columnas permitidas y consistencia de los indicadores exportados.

    Lanza AssertionError en la primera comprobación que falla. Si todas pasan,
    devuelve su descripción, para dejar evidencia en el notebook.
    """
    aprobadas = []
    assert len(ofertas) == filas_originales, "Cambió la cantidad de filas de ofertas."
    aprobadas.append(f"Ofertas: se conservan las {filas_originales:,} filas de entrada")
    permitidas = set(MOTIVOS) | {
        "EsDuplicadoPotencial", "TamanoProveedorOrdinal", "EsExtremoLogIQR_CLP",
    }
    assert set(ofertas.columns) <= permitidas, "Hay columnas fuera del conjunto autorizado."
    aprobadas.append(f"Ofertas: las {ofertas.shape[1]} columnas pertenecen al conjunto autorizado")
    ids = normalizar_codigo(ofertas["NroLicitacion"]).dropna()
    assert licitaciones["NroLicitacion"].is_unique, "Se repiten licitaciones."
    assert set(licitaciones["NroLicitacion"]) == set(ids), "Faltan licitaciones con código."
    aprobadas.append(f"Licitaciones: {len(licitaciones):,} códigos únicos, los mismos de las ofertas")
    ordinal = ofertas["TamanoProveedorOrdinal"]
    assert ordinal.cat.ordered and tuple(ordinal.cat.categories) == ORDEN_TAMANO
    sin_clasificar = normalizar_codigo(ofertas["TamanoProveedor"]).eq("NOCLASIFICADO").fillna(False)
    assert ordinal[sin_clasificar].isna().all(), "NoClasificado tiene rango."
    aprobadas.append("Tamaño: escala " + " < ".join(ORDEN_TAMANO) + "; NoClasificado sin rango")
    comparable = licitaciones["EstadoBrecha"].eq("Calculada")
    assert np.array_equal(licitaciones["BrechaMonto"].notna(), comparable)
    aprobadas.append("Brecha: existe solo en las licitaciones con estado Calculada")
    validas = licitaciones.loc[comparable]
    assert validas["MontoTotalGanadoras"].gt(0).all() and validas["MontoEstimadoLicitacion"].gt(0).all()
    assert validas["OfertasGanadoras"].gt(0).all() and not validas["GanadoraMonedaDistinta"].any()
    aprobadas.append("Brecha: montos ganadores y estimados positivos, en la misma moneda")
    evaluadas = ofertas_clp_validas(ofertas) if limites is not None else pd.Series(False, index=ofertas.index)
    assert np.array_equal(ofertas["EsExtremoLogIQR_CLP"].notna(), evaluadas)
    aprobadas.append("Extremos: la bandera existe solo en ofertas CLP con monto positivo")
    return aprobadas
