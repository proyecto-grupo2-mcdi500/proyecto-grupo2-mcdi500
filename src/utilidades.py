"""Utilidades generales del proyecto: raíz del repositorio, nombres de columnas y excepción propia.

Las reglas del preprocesamiento están en preprocesamiento.py."""

from pathlib import Path
import re
import unicodedata
import pandas as pd


class ProyectoError(Exception):
    """Excepción personalizada para errores de validación y procesamiento del proyecto."""


def obtener_raiz_proyecto(inicio: Path | None = None) -> Path:
    """Busca y retorna la carpeta raíz del repositorio a partir del directorio actual."""
    actual = (inicio or Path.cwd()).resolve()
    for directorio in [actual, *actual.parents]:
        if (directorio / "data").is_dir():
            return directorio
    return actual


def normalizar_nombre(nombre: str) -> str:
    """
    Normaliza un nombre de columna a formato snake_case sin tildes ni signos especiales.

    Lanza ProyectoError si la entrada no es de tipo str o resulta vacía.
    """
    if not isinstance(nombre, str):
        raise ProyectoError(
            f"Se esperaba un nombre de tipo 'str', pero se recibió '{type(nombre).__name__}'."
        )
    texto = unicodedata.normalize("NFKD", nombre.strip())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", texto)
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    if not texto:
        raise ProyectoError(f"El nombre '{nombre}' queda vacío tras normalizar.")
    return texto


def normalizar_columnas(
    objeto: pd.DataFrame | list[str] | tuple[str, ...] | pd.Index,
) -> pd.DataFrame | list[str]:
    """
    Normaliza una colección de nombres de columnas (o las columnas de un DataFrame).

    Lanza ProyectoError si algún elemento no es válido o si dos nombres colapsan
    en el mismo identificador normalizado.
    """
    if isinstance(objeto, pd.DataFrame):
        nombres_origen = list(objeto.columns)
    elif isinstance(objeto, (list, tuple, pd.Index)):
        nombres_origen = list(objeto)
    else:
        raise ProyectoError(
            f"Se esperaba una lista, Index o DataFrame, pero se recibió '{type(objeto).__name__}'."
        )

    normalizados = [normalizar_nombre(col) for col in nombres_origen]

    vistos: set[str] = set()
    duplicados: list[str] = []
    for col in normalizados:
        if col in vistos and col not in duplicados:
            duplicados.append(col)
        vistos.add(col)

    if duplicados:
        raise ProyectoError(
            f"La normalización colapsa múltiples columnas en el mismo nombre: {duplicados}"
        )

    if isinstance(objeto, pd.DataFrame):
        df_out = objeto.copy()
        df_out.columns = normalizados
        return df_out
    return normalizados
