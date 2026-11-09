"""Carga, transformación y controles de las licitaciones de ChileCompra."""

from abc import ABC, abstractmethod

import pandas as pd

FECHAS = ("FechaPublicacion", "FechaCierre", "FechaAdjudicacion")
MONTOS = ("MontoNetoOferta", "MontoTotalOferta")
TAMANO = "TamanoProveedor"
ORDEN = ("Micro", "Pequeña", "Mediana", "Grande", "NoClasificado")


def cargar_licitaciones(ruta):
    """Lee el CSV con las mismas opciones que Fase 2."""
    return pd.read_csv(ruta, sep=None, engine="python", encoding="latin-1")


class Transformador(ABC):
    """Valida columnas y expone la interfaz común de cada transformación."""

    def __init__(self, columnas):
        self._columnas = tuple(columnas)

    def transformar(self, datos):
        faltantes = set(self._columnas) - set(datos.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas para {type(self).__name__}: {sorted(faltantes)}")
        return self._aplicar(datos)

    @abstractmethod
    def _aplicar(self, datos):
        """Devuelve un DataFrame y las observaciones sobre su conversión."""


def _control(columna, original, convertido):
    return {
        "Columna": columna,
        "Nulos originales": int(original.isna().sum()),
        "Fallos de conversión": int((original.notna() & convertido.isna()).sum()),
    }


class ConversorFechas(Transformador):
    def __init__(self, formato="%d-%m-%Y %H:%M"):
        super().__init__(FECHAS)
        self._formato = formato

    def _aplicar(self, datos):
        salida = datos.copy()
        controles = []
        for columna in self._columnas:
            original = datos[columna]
            salida[columna] = pd.to_datetime(original, format=self._formato, errors="coerce")
            controles.append(_control(columna, original, salida[columna]))
        return salida, controles


class ConversorMontos(Transformador):
    def __init__(self):
        super().__init__(MONTOS)

    def _aplicar(self, datos):
        salida = datos.copy()
        controles = []
        for columna in self._columnas:
            original = datos[columna].astype("string").str.strip()
            texto = original.str.replace(",", ".", regex=False)
            salida[columna] = pd.to_numeric(texto, errors="coerce")
            controles.append(_control(columna, original, salida[columna]))
        return salida, controles


class OrdenadorTamano(Transformador):
    def __init__(self, orden=ORDEN):
        super().__init__((TAMANO,))
        self._orden = tuple(orden)

    def _aplicar(self, datos):
        no_incluidos = set(datos[TAMANO].dropna().unique()) - set(self._orden)
        if no_incluidos:
            return datos, [{"Columna": TAMANO, "Detalle": f"Se conservó el tipo original: {sorted(no_incluidos)}"}]
        tipo = pd.CategoricalDtype(categories=self._orden, ordered=True)
        salida = datos.assign(**{TAMANO: datos[TAMANO].astype(tipo)})
        return salida, [{"Columna": TAMANO, "Detalle": "Categoría ordenada"}]


class Bitacora:
    """Recibe los resultados de cada paso y los convierte en evidencia tabular."""

    def __init__(self):
        self._registros = []

    def registrar(self, evento):
        self._registros.append(evento.copy())

    def tabla(self):
        return pd.DataFrame(self._registros)


class Pipeline:
    """Ejecuta los transformadores en orden y notifica a los observadores."""

    def __init__(self, pasos):
        self._pasos = tuple(pasos)
        self._observadores = []

    def suscribir(self, observador):
        self._observadores.append(observador)

    def transformar(self, datos):
        salida = datos
        for paso in self._pasos:
            filas_entrada = len(salida)
            salida, controles = paso.transformar(salida)
            for control in controles:
                evento = {"Paso": type(paso).__name__, "Filas entrada": filas_entrada,
                          "Filas salida": len(salida), **control}
                for observador in self._observadores:
                    observador(evento)
        return salida
