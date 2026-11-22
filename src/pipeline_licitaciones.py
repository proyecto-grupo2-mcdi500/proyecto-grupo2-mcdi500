"""Pipeline de la Fase 3: transformadores ajustables con herencia, polimorfismo y encapsulamiento."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .preprocesamiento import (
    FECHAS, MONTOS, MOTIVOS, LimitesIQR, aplicar_bandera_atipicos, calcular_brecha,
    calcular_limites_iqr, cargar_csv, convertir_tipos, marcar_duplicados,
    ordenar_tamano, tratar_faltantes, validar_procesado,
)


@dataclass
class ResultadoF3:
    """Contenedor con las tablas analíticas validadas y los parámetros IQR aprendidos.

    Atributos
    ---------
    ofertas : pd.DataFrame
        Tabla a nivel de oferta por ítem con las variables analíticas y banderas derivadas.
    licitaciones : pd.DataFrame
        Tabla agregada por licitación con montos ganadores y brechas frente al estimado.
    limites_iqr : LimitesIQR | None
        Parámetros logarítmicos del IQR en CLP ajustados durante el pipeline, o ``None``.
    """

    ofertas: pd.DataFrame
    licitaciones: pd.DataFrame
    limites_iqr: LimitesIQR | None


class Transformador(ABC):
    """Clase base abstracta para los pasos del pipeline sobre filas de oferta.

    Concentra el comportamiento común a todos los transformadores:
    - Control del estado encapsulado ``_ajustado`` antes de transformar.
    - Validación temprana de ``columnas_requeridas`` en ajuste y aplicación.
    - Copia defensiva del ``DataFrame`` de entrada antes de delegar en las subclases.
    """

    nombre: str
    columnas_requeridas: tuple[str, ...] = ()

    def __init__(self, columnas_requeridas: Sequence[str] = ()) -> None:
        """Inicializa el control de ajuste y fija las columnas mínimas exigidas.

        Parámetros
        ----------
        columnas_requeridas : Sequence[str], opcional
            Columnas que deben existir en el ``DataFrame`` de entrada. Si se omite,
            se conservan las declaradas en la subclase.
        """
        if columnas_requeridas:
            self.columnas_requeridas = tuple(columnas_requeridas)
        else:
            self.columnas_requeridas = tuple(getattr(type(self), "columnas_requeridas", ()))
        self._ajustado = False

    @property
    def ajustado(self) -> bool:
        """Indica si el transformador ya completó su paso de ajuste."""
        return self._ajustado

    def _validar_columnas(self, datos: pd.DataFrame) -> None:
        """Comprueba que existan todas las columnas declaradas en ``columnas_requeridas``."""
        faltantes = sorted(set(self.columnas_requeridas).difference(datos.columns))
        if faltantes:
            raise ValueError(f"{self.nombre}: faltan columnas requeridas: {faltantes}.")

    def ajustar(self, datos: pd.DataFrame) -> "Transformador":
        """Valida columnas, aprende parámetros sobre copia defensiva y marca ``_ajustado``.

        Parámetros
        ----------
        datos : pd.DataFrame
            Conjunto de entrada usado para aprender parámetros del paso.

        Retorna
        -------
        Transformador
            La propia instancia ajustada para permitir encadenamiento.

        Lanza
        -----
        ValueError
            Si falta alguna columna declarada en ``columnas_requeridas``.
        """
        self._validar_columnas(datos)
        self._ajustar_en(datos.copy())
        self._ajustado = True
        return self

    def transformar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Valida ajuste previo y columnas requeridas, y aplica la regla sobre copia defensiva.

        Parámetros
        ----------
        datos : pd.DataFrame
            Tabla de ofertas a transformar.

        Retorna
        -------
        pd.DataFrame
            Nueva tabla con las transformaciones del paso aplicadas.

        Lanza
        -----
        RuntimeError
            Si se intenta transformar antes de haber ejecutado ``ajustar``.
        ValueError
            Si falta alguna columna declarada en ``columnas_requeridas``.
        """
        if not self._ajustado:
            raise RuntimeError(f"Ejecuta ajustar antes de aplicar '{self.nombre}'.")
        self._validar_columnas(datos)
        return self._aplicar(datos.copy())

    def _ajustar_en(self, datos: pd.DataFrame) -> None:
        """Hook opcional de aprendizaje sobre copia de datos; sin efecto en reglas fijas."""

    @abstractmethod
    def _aplicar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Ejecuta la transformación específica de la subclase sobre una copia validada."""


class TransformacionFija(Transformador):
    """Adapta una regla determinista de F2 a la interfaz polimórfica ``Transformador``."""

    def __init__(
        self,
        nombre: str,
        regla: Callable[[pd.DataFrame], pd.DataFrame],
        columnas_requeridas: Sequence[str] = (),
    ) -> None:
        """Registra el nombre visible, la regla funcional y sus columnas requeridas.

        Parámetros
        ----------
        nombre : str
            Etiqueta descriptiva reportada en la bitácora del pipeline.
        regla : Callable[[pd.DataFrame], pd.DataFrame]
            Función pura que recibe un ``DataFrame`` y retorna otro transformado.
        columnas_requeridas : Sequence[str], opcional
            Columnas mínimas exigidas antes de invocar ``regla``.
        """
        super().__init__(columnas_requeridas=columnas_requeridas)
        self._nombre = nombre
        self._regla = regla

    @property
    def nombre(self) -> str:
        """Nombre descriptivo del paso dentro del pipeline."""
        return self._nombre

    def _aplicar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Aplica la función registrada sobre la copia defensiva recibida."""
        return self._regla(datos)


class TratamientoFaltantes(Transformador):
    """Aprende qué columnas superan un umbral de valores faltantes y las excluye al transformar.

    Las variables del análisis (``MOTIVOS``) nunca se excluyen: F2 conserva sus faltantes
    sin imputar, aunque superen el umbral.
    """

    nombre = "Tratar faltantes (>90 %)"

    def __init__(
        self,
        umbral_pct: float = 90.0,
        columnas_requeridas: Sequence[str] = (),
    ) -> None:
        """Configura el umbral porcentual de exclusión y el estado inicial encapsulado.

        Parámetros
        ----------
        umbral_pct : float, opcional
            Porcentaje de faltantes (entre 0 y 100) a partir del cual una columna se excluye.
        columnas_requeridas : Sequence[str], opcional
            Columnas mínimas exigidas antes de ajustar o transformar.

        Lanza
        -----
        ValueError
            Si ``umbral_pct`` está fuera del intervalo ``[0, 100]``.
        """
        if not 0.0 <= umbral_pct <= 100.0:
            raise ValueError("El umbral de faltantes debe estar entre 0 y 100.")
        super().__init__(columnas_requeridas=columnas_requeridas)
        self._umbral_pct = float(umbral_pct)
        self._columnas_excluidas: tuple[str, ...] = ()
        self._resumen_faltantes: pd.DataFrame | None = None

    @property
    def umbral_pct(self) -> float:
        """Porcentaje de faltantes utilizado como umbral de exclusión."""
        return self._umbral_pct

    @property
    def columnas_excluidas(self) -> tuple[str, ...]:
        """Tupla inmutable con las columnas aprendidas que superan el umbral."""
        return self._columnas_excluidas

    @property
    def resumen(self) -> pd.DataFrame | None:
        """Copia defensiva de la tabla de diagnóstico calculada durante ``ajustar``."""
        return None if self._resumen_faltantes is None else self._resumen_faltantes.copy()

    def _ajustar_en(self, datos: pd.DataFrame) -> None:
        """Normaliza blancos e identifica las columnas fuera del análisis con más de ``umbral_pct`` de faltantes."""
        _, control = tratar_faltantes(datos, datos.isna().sum())
        self._resumen_faltantes = control
        self._columnas_excluidas = tuple(
            columna
            for columna in control.index[control["% faltantes"].gt(self._umbral_pct)]
            if columna not in MOTIVOS
        )

    def _aplicar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Reemplaza cadenas en blanco por ``pd.NA`` y retira las columnas excluidas."""
        resultado = datos.replace(r"^\s*$", pd.NA, regex=True)
        if not self._columnas_excluidas:
            return resultado
        return resultado.drop(columns=list(self._columnas_excluidas), errors="ignore")


class ExtremosLogIQR(Transformador):
    """Ajusta límites logarítmicos IQR en CLP y marca ofertas extremas al transformar."""

    nombre = "Marcar valores extremos CLP"
    columnas_requeridas = ("MonedaOferta", "MontoTotalOferta")

    def __init__(self) -> None:
        """Inicializa el transformador sin límites aprendidos."""
        super().__init__()
        self._limites: LimitesIQR | None = None

    @property
    def limites(self) -> LimitesIQR | None:
        """Copia defensiva de los límites IQR aprendidos, o ``None`` si no hubo muestra suficiente."""
        return None if self._limites is None else dict(self._limites)

    def _ajustar_en(self, datos: pd.DataFrame) -> None:
        """Calcula los cuartiles y límites IQR sobre el logaritmo de montos positivos en CLP."""
        self._limites = calcular_limites_iqr(datos)

    def _aplicar(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Agrega la bandera booleana ``EsExtremoLogIQR_CLP`` usando los límites aprendidos."""
        return aplicar_bandera_atipicos(datos, self._limites)


class Bitacora:
    """Observador que conserva conteos por paso y evita registrar valores originales."""

    def __init__(self) -> None:
        """Inicializa una lista vacía de eventos registrados."""
        self._eventos: list[dict[str, str | int]] = []

    def registrar(self, paso: str, filas_entrada: int, filas_salida: int) -> None:
        """Almacena un evento de paso con los conteos de filas de entrada y salida.

        Parámetros
        ----------
        paso : str
            Nombre del paso ejecutado.
        filas_entrada : int
            Cantidad de registros antes de ejecutar el paso.
        filas_salida : int
            Cantidad de registros después de ejecutar el paso.
        """
        self._eventos.append({
            "Paso": paso, "Filas de entrada": filas_entrada, "Filas de salida": filas_salida,
        })

    def tabla(self) -> pd.DataFrame:
        """Devuelve un ``DataFrame`` con el historial completo de pasos registrados."""
        return pd.DataFrame(self._eventos)


class Pipeline:
    """Ejecuta una secuencia polimórfica de ``Transformador`` y notifica a sus observadores."""

    def __init__(self, pasos: Sequence[Transformador]) -> None:
        """Inicializa el pipeline con los pasos a ejecutar en orden.

        Parámetros
        ----------
        pasos : Sequence[Transformador]
            Secuencia ordenada de transformadores que implementan ``ajustar`` y ``transformar``.
        """
        self._pasos = tuple(pasos)
        self._observadores: list[Callable[[str, int, int], None]] = []

    def suscribir(self, observador: Callable[[str, int, int], None]) -> None:
        """Registra una función observadora para recibir ``(paso, entrada, salida)``.

        Parámetros
        ----------
        observador : Callable[[str, int, int], None]
            Función o método compatible que registra el avance de cada etapa.
        """
        self._observadores.append(observador)

    def _notificar(self, paso: str, entrada: int, salida: int) -> None:
        """Informa a todos los observadores suscritos los conteos de un paso."""
        for observador in self._observadores:
            observador(paso, entrada, salida)

    def ejecutar(self, ruta: Path) -> ResultadoF3:
        """Lee el CSV de entrada, ajusta/transforma todos los pasos y valida las salidas.

        Parámetros
        ----------
        ruta : Path
            Ruta al archivo fuente (raw) de licitaciones.

        Retorna
        -------
        ResultadoF3
            Tablas ``ofertas`` y ``licitaciones`` validadas junto con ``limites_iqr``.
        """
        datos = cargar_csv(ruta)
        filas_originales = len(datos)
        self._notificar("Cargar CSV", filas_originales, filas_originales)
        for paso in self._pasos:
            entrada = len(datos)
            paso.ajustar(datos)
            datos = paso.transformar(datos)
            self._notificar(paso.nombre, entrada, len(datos))

        licitaciones = calcular_brecha(datos)
        self._notificar("Calcular brecha por licitación", len(datos), len(licitaciones))

        columnas = [columna for columna in MOTIVOS if columna in datos]
        columnas += ["EsDuplicadoPotencial", "TamanoProveedorOrdinal", "EsExtremoLogIQR_CLP"]
        ofertas = datos[columnas]
        limites = next(
            (paso.limites for paso in self._pasos if isinstance(paso, ExtremosLogIQR)),
            None,
        )
        validar_procesado(ofertas, licitaciones, filas_originales, limites)
        self._notificar("Validar ofertas", len(ofertas), len(ofertas))
        self._notificar("Validar licitaciones", len(licitaciones), len(licitaciones))
        return ResultadoF3(ofertas, licitaciones, limites)


def construir_pipeline() -> Pipeline:
    """Construye el pipeline oficial de F3 con todas las reglas ordenadas de F2."""
    return Pipeline([
        TransformacionFija(
            "Marcar duplicados potenciales",
            lambda d: marcar_duplicados(d)[0],
            ("ResultadoOferta",),
        ),
        TransformacionFija(
            "Convertir fechas y montos",
            lambda d: convertir_tipos(d)[0],
            (*FECHAS, *MONTOS),
        ),
        TratamientoFaltantes(),
        TransformacionFija(
            "Ordenar tamaño de proveedor",
            ordenar_tamano,
            ("TamanoProveedor",),
        ),
        ExtremosLogIQR(),
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
    """Marca las mismas alertas mediante comparaciones vectorizadas por columna."""
    publicacion, cierre, adjudicacion = (datos[columna] for columna in FECHAS)
    return (cierre < publicacion) | (adjudicacion < cierre)
