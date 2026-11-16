"""Pipeline F3 que reutiliza las reglas del preprocesamiento revisado de F2."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .funciones_f2_revision import (
    FECHAS, MOTIVOS, LimitesIQR, aplicar_bandera_atipicos, calcular_brecha,
    calcular_limites_iqr, cargar_csv, convertir_tipos, marcar_duplicados,
    ordenar_tamano, tratar_faltantes, validar_procesado,
)


@dataclass
class ResultadoF3:
    """Tablas analíticas y parámetros calculados a partir de la entrada."""

    ofertas: pd.DataFrame
    licitaciones: pd.DataFrame
    limites_iqr: LimitesIQR | None


class Transformador(ABC):
    """Contrato común para las operaciones sobre filas de oferta."""

    @abstractmethod
    def transformar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Devuelve las ofertas después de aplicar la regla del paso."""


class TransformacionFija(Transformador):
    """Adapta una regla funcional de F2 a la interfaz del pipeline."""

    def __init__(self, nombre: str, regla: Callable[[pd.DataFrame], pd.DataFrame]):
        self._nombre = nombre
        self._regla = regla

    @property
    def nombre(self) -> str:
        return self._nombre

    def transformar(self, datos: pd.DataFrame) -> pd.DataFrame:
        return self._regla(datos)


class ExtremosLogIQR(Transformador):
    """Ajusta límites en CLP y los reutiliza al transformar otras ofertas."""

    nombre = "Marcar valores extremos CLP"

    def __init__(self):
        self._limites: LimitesIQR | None = None
        self._ajustado = False

    @property
    def limites(self) -> LimitesIQR | None:
        return None if self._limites is None else dict(self._limites)

    def ajustar(self, datos: pd.DataFrame) -> None:
        self._limites = calcular_limites_iqr(datos)
        self._ajustado = True

    def transformar(self, datos: pd.DataFrame) -> pd.DataFrame:
        if not self._ajustado:
            raise RuntimeError("Ejecuta ajustar antes de aplicar los límites IQR.")
        return aplicar_bandera_atipicos(datos, self._limites)


class Bitacora:
    """Observador que conserva conteos por paso y evita registrar valores originales."""

    def __init__(self):
        self._eventos: list[dict[str, str | int]] = []

    def registrar(self, paso: str, filas_entrada: int, filas_salida: int) -> None:
        self._eventos.append({
            "Paso": paso, "Filas de entrada": filas_entrada, "Filas de salida": filas_salida,
        })

    def tabla(self) -> pd.DataFrame:
        return pd.DataFrame(self._eventos)


class Pipeline:
    """Ejecuta las operaciones en orden y notifica a los observadores suscritos."""

    def __init__(self, pasos: Sequence[TransformacionFija]):
        self._pasos = tuple(pasos)
        self._extremos = ExtremosLogIQR()
        self._observadores: list[Callable[[str, int, int], None]] = []

    def suscribir(self, observador: Callable[[str, int, int], None]) -> None:
        self._observadores.append(observador)

    def _notificar(self, paso: str, entrada: int, salida: int) -> None:
        for observador in self._observadores:
            observador(paso, entrada, salida)

    def ejecutar(self, ruta: Path) -> ResultadoF3:
        """Lee un CSV y devuelve ambas tablas validadas para el análisis descriptivo."""
        datos = cargar_csv(ruta)
        filas_originales = len(datos)
        self._notificar("Cargar CSV", filas_originales, filas_originales)
        for paso in self._pasos:
            entrada = len(datos)
            datos = paso.transformar(datos)
            self._notificar(paso.nombre, entrada, len(datos))

        licitaciones = calcular_brecha(datos)
        self._notificar("Calcular brecha por licitación", len(datos), len(licitaciones))
        self._extremos.ajustar(datos)
        datos = self._extremos.transformar(datos)
        self._notificar(self._extremos.nombre, len(datos), len(datos))

        columnas = [columna for columna in MOTIVOS if columna in datos]
        columnas += ["EsDuplicadoPotencial", "TamanoProveedorOrdinal", "EsExtremoLogIQR_CLP"]
        ofertas = datos[columnas]
        limites = self._extremos.limites
        validar_procesado(ofertas, licitaciones, filas_originales, limites)
        self._notificar("Validar ofertas", len(ofertas), len(ofertas))
        self._notificar("Validar licitaciones", len(licitaciones), len(licitaciones))
        return ResultadoF3(ofertas, licitaciones, limites)


def construir_pipeline() -> Pipeline:
    """Ordena las reglas de F2, desde duplicados potenciales hasta el tamaño ordinal."""
    return Pipeline([
        TransformacionFija("Marcar duplicados potenciales", lambda d: marcar_duplicados(d)[0]),
        TransformacionFija("Convertir fechas y montos", lambda d: convertir_tipos(d)[0]),
        TransformacionFija("Normalizar faltantes", lambda d: tratar_faltantes(d, d.isna().sum())[0]),
        TransformacionFija("Ordenar tamaño de proveedor", ordenar_tamano),
    ])


def control_iterativo(datos: pd.DataFrame) -> pd.Series:
    """Marca cierres o adjudicaciones fuera de secuencia, recorriendo cada fila."""
    marcas = []
    for publicacion, cierre, adjudicacion in datos[list(FECHAS)].itertuples(index=False, name=None):
        cierre_anticipado = pd.notna(publicacion) and pd.notna(cierre) and cierre < publicacion
        adjudicacion_anticipada = pd.notna(cierre) and pd.notna(adjudicacion) and adjudicacion < cierre
        marcas.append(cierre_anticipado or adjudicacion_anticipada)
    return pd.Series(marcas, index=datos.index, dtype=bool)


def control_vectorizado(datos: pd.DataFrame) -> pd.Series:
    """Marca las mismas alertas mediante comparaciones por columna."""
    publicacion, cierre, adjudicacion = (datos[columna] for columna in FECHAS)
    return (cierre < publicacion) | (adjudicacion < cierre)
