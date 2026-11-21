"""Medición de tiempo y memoria para comparar implementaciones de un mismo cálculo.

Se usan funciones porque cada medición es independiente.
"""

from collections.abc import Callable
import timeit
import tracemalloc
from typing import Any

import pandas as pd


def medir_tiempo(funcion: Callable[[], Any], repeticiones: int = 7) -> float:
    """Ejecuta la función varias veces y devuelve el menor tiempo, en segundos.

    Se conserva el mínimo y no el promedio: los tiempos altos suelen deberse a
    otros procesos del equipo, no al código que se mide.
    """
    if repeticiones < 1:
        raise ValueError("Se necesita al menos una repetición.")
    return min(timeit.repeat(funcion, number=1, repeat=repeticiones))


def medir_memoria(funcion: Callable[[], Any]) -> tuple[Any, float]:
    """Ejecuta la función una vez y devuelve su resultado y la memoria pico en MB.

    tracemalloc registra la memoria que se reserva a través de Python durante la
    ejecución. Como el registro hace más lenta la función, la memoria se mide en
    una ejecución separada de la que mide el tiempo.
    """
    if tracemalloc.is_tracing():
        raise RuntimeError("tracemalloc ya está activo: no se pueden anidar mediciones.")
    tracemalloc.start()
    try:
        resultado = funcion()
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return resultado, pico / (1024 * 1024)


def verificar_iguales(referencia: Any, candidato: Any, nombre: str) -> None:
    """Comprueba que dos resultados sean idénticos o lanza AssertionError.

    Una versión más rápida que entrega otra respuesta no es una optimización.
    """
    if isinstance(referencia, pd.DataFrame):
        pd.testing.assert_frame_equal(referencia, candidato, check_exact=True)
    elif isinstance(referencia, pd.Series):
        pd.testing.assert_series_equal(referencia, candidato, check_exact=True)
    elif referencia != candidato:
        raise AssertionError(f"{nombre} entrega un resultado distinto al de la referencia.")


def comparar(
    implementaciones: dict[str, Callable[[], Any]], repeticiones: int = 7,
    *, repeticiones_memoria: int = 1,
) -> pd.DataFrame:
    """Mide tiempo y memoria de cada implementación y verifica que coincidan.

    Recibe un diccionario {nombre: función sin argumentos}. La primera
    implementación es la referencia: todas las demás deben entregar exactamente
    el mismo resultado; si no, se detiene con AssertionError antes de reportar.
    Para memoria conserva el menor pico de las ejecuciones independientes.
    """
    if len(implementaciones) < 2:
        raise ValueError("Se necesitan al menos dos implementaciones para comparar.")
    if repeticiones_memoria < 1:
        raise ValueError("Se necesita al menos una repetición para medir memoria.")

    filas = []
    referencia = None
    for posicion, (nombre, funcion) in enumerate(implementaciones.items()):
        resultado, memoria_mb = medir_memoria(funcion)
        for _ in range(repeticiones_memoria - 1):
            _, pico = medir_memoria(funcion)
            memoria_mb = min(memoria_mb, pico)
        if posicion == 0:
            referencia = resultado
        else:
            verificar_iguales(referencia, resultado, nombre)
        filas.append({
            "Implementación": nombre,
            "Tiempo mínimo (ms)": medir_tiempo(funcion, repeticiones) * 1000,
            "Memoria pico (MB)": memoria_mb,
        })

    tabla = pd.DataFrame(filas)
    tabla["Veces el tiempo de la más rápida"] = (
        tabla["Tiempo mínimo (ms)"] / tabla["Tiempo mínimo (ms)"].min()
    )
    tabla["Repeticiones"] = repeticiones
    return tabla.round(3)


def medir_contraste(
    iterativa: Callable[[], pd.DataFrame], vectorizada: Callable[[], pd.DataFrame],
    repeticiones: int = 7,
) -> dict[str, float]:
    """Resume el contraste con el mismo número de repeticiones de tiempo y memoria."""
    tabla = comparar(
        {"Iterativa": iterativa, "Vectorizada": vectorizada},
        repeticiones=repeticiones, repeticiones_memoria=repeticiones,
    ).set_index("Implementación")
    return {
        "Iterativa (ms)": tabla.loc["Iterativa", "Tiempo mínimo (ms)"],
        "Vectorizada (ms)": tabla.loc["Vectorizada", "Tiempo mínimo (ms)"],
        "Iterativa (MiB)": tabla.loc["Iterativa", "Memoria pico (MB)"],
        "Vectorizada (MiB)": tabla.loc["Vectorizada", "Memoria pico (MB)"],
        "Tiempo iterativa / vectorizada": (
            tabla.loc["Iterativa", "Veces el tiempo de la más rápida"]
            / tabla.loc["Vectorizada", "Veces el tiempo de la más rápida"]
        ),
    }
