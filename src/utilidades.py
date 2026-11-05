"""Funciones reutilizables de carga, preprocesamiento y validación de datos."""

from pathlib import Path
import pandas as pd


ORDEN_TAMANO_PROVEEDOR = [
    "Micro",
    "Pequeña",
    "Mediana",
    "Grande",
    "NoClasificado",
]

COLUMNAS_FECHA_PRINCIPALES = [
    "FechaPublicacion",
    "FechaCierre",
    "FechaAdjudicacion",
]

COLUMNAS_MONTO_OFERTA = [
    "MontoNetoOferta",
    "MontoTotalOferta",
]


def obtener_raiz_proyecto(inicio: Path | None = None) -> Path:
    """Busca y retorna la carpeta raíz del repositorio a partir del directorio actual."""
    actual = (inicio or Path.cwd()).resolve()
    for directorio in [actual, *actual.parents]:
        if (directorio / "data").is_dir():
            return directorio
    return actual


def cargar_datos_crudos(
    nombre_archivo: str = "04LicitacionesEne.csv",
    sep: str = ";",
    encoding: str = "latin-1",
) -> pd.DataFrame:
    """Carga el archivo CSV original desde data/raw/."""
    raiz = obtener_raiz_proyecto()
    ruta = raiz / "data" / "raw" / nombre_archivo
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo original en: {ruta}")
    return pd.read_csv(ruta, sep=sep, encoding=encoding, low_memory=False)


def cargar_datos_procesados(
    nombre_archivo: str = "04LicitacionesEne_procesado.csv",
    sep: str = ";",
    encoding: str = "utf-8-sig",
) -> pd.DataFrame:
    """Carga el archivo CSV preprocesado desde data/processed/."""
    raiz = obtener_raiz_proyecto()
    ruta = raiz / "data" / "processed" / nombre_archivo
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo procesado en: {ruta}")
    df = pd.read_csv(ruta, sep=sep, encoding=encoding, low_memory=False)
    return ordenar_tamano_proveedor(df)


def convertir_fechas(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
    formato: str = "%d-%m-%Y %H:%M",
) -> pd.DataFrame:
    """Convierte las columnas de fecha indicadas a tipo datetime64."""
    df_out = df.copy()
    for col in columnas or COLUMNAS_FECHA_PRINCIPALES:
        if col in df_out.columns:
            df_out[col] = pd.to_datetime(df_out[col], format=formato, errors="coerce")
    return df_out


def convertir_montos(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
) -> pd.DataFrame:
    """Reemplaza la coma decimal por punto y convierte los montos a valores numéricos."""
    df_out = df.copy()
    for col in columnas or COLUMNAS_MONTO_OFERTA:
        if col in df_out.columns:
            texto = (
                df_out[col]
                .astype("string")
                .str.strip()
                .str.replace(",", ".", regex=False)
            )
            df_out[col] = pd.to_numeric(texto, errors="coerce")
    return df_out


def ordenar_tamano_proveedor(
    df: pd.DataFrame,
    columna: str = "TamanoProveedor",
    orden: list[str] | None = None,
) -> pd.DataFrame:
    """Convierte la columna TamanoProveedor en una categoría ordenada."""
    df_out = df.copy()
    if columna in df_out.columns:
        categorias = orden or ORDEN_TAMANO_PROVEEDOR
        tipo_cat = pd.CategoricalDtype(categories=categorias, ordered=True)
        df_out[columna] = df_out[columna].astype(tipo_cat)
    return df_out


def detectar_atipicos_iqr(
    serie: pd.Series,
    factor: float = 1.5,
) -> tuple[pd.Series, dict[str, float]]:
    """Retorna una máscara booleana de valores atípicos y el diccionario con Q1, Q3, IQR y límites."""
    q1 = float(serie.quantile(0.25))
    q3 = float(serie.quantile(0.75))
    iqr = q3 - q1
    limite_inferior = q1 - (factor * iqr)
    limite_superior = q3 + (factor * iqr)
    es_atipico = (serie < limite_inferior) | (serie > limite_superior)
    metricas = {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
    }
    return es_atipico, metricas

