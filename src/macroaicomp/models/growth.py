"""
Solow-Swan growth model.

This module implements the Solow-Swan exogenous growth model as presented in
Chapter 9 of "An Introduction to Computational Macroeconomics"
(Bongers, Gómez, Torres, 2019).

The model:
    - Production function: Y = A * K^alpha * N^(1-alpha)  (Cobb-Douglas)
    - In per-worker terms: y = A * k^alpha
    - Capital accumulation: k_{t+1} = (1 - delta - n) * k_t + s * y_t
    - Steady state: s * A * k_ss^alpha = (delta + n) * k_ss
      => k_ss = (s * A / (delta + n))^(1/(1-alpha))
"""

from dataclasses import dataclass
from typing import Dict, Union

import numpy as np


@dataclass
class SolowSwanParameters:
    """Parámetros de calibración para el modelo de crecimiento de Solow-Swan.

    Parámetros
    ----------
    alpha : float
        Participación del capital en la renta / elasticidad de producción respecto al capital (por defecto: 0.35).
    delta : float
        Tasa de depreciación física del capital (por defecto: 0.08).
    s : float
        Tasa de ahorro exógena de la economía (por defecto: 0.20).
    n : float
        Tasa de crecimiento de la población (por defecto: 0.00).
    A : float
        Productividad Total de los Factores (TFP) estacionaria (por defecto: 1.0).
    """

    alpha: float = 0.35
    delta: float = 0.08
    s: float = 0.20
    n: float = 0.0  # Sin crecimiento poblacional por defecto (línea base del Capítulo 9)
    A: float = 1.0


def compute_solow_steady_state(
    params: SolowSwanParameters,
    s: Union[float, None] = None,
    n: Union[float, None] = None,
    A: Union[float, None] = None,
) -> Dict[str, float]:
    """
    Calcula los valores de estado estacionario del modelo de Solow-Swan.

    En el estado estacionario:
        s * A * k^alpha = (delta + n) * k
        => k_ss = (s * A / (delta + n))^(1/(1-alpha))

    Parameters
    ----------
    params : SolowSwanParameters
    s : float, opcional
        Sobrescribe la tasa de ahorro.
    n : float, opcional
        Sobrescribe la tasa de crecimiento poblacional.
    A : float, opcional
        Sobrescribe la TFP.

    Returns
    -------
    dict
        Diccionario con 'k' (capital por trabajador), 'y' (producción por trabajador),
        'c' (consumo por trabajador) e 'i' (inversión por trabajador).
    """
    s_val = s if s is not None else params.s
    n_val = n if n is not None else params.n
    A_val = A if A is not None else params.A
    alpha = params.alpha
    delta = params.delta

    # 1. Capital por trabajador estacionario de largo plazo
    k_ss = (s_val * A_val / (delta + n_val)) ** (1.0 / (1.0 - alpha))
    
    # 2. Producción per cápita estacionaria
    y_ss = A_val * k_ss**alpha
    
    # 3. Inversión per cápita estacionaria (reproduce la depreciación y la dilución)
    i_ss = s_val * y_ss
    
    # 4. Consumo per cápita estacionario de equilibrio
    c_ss = (1.0 - s_val) * y_ss

    return {"k": k_ss, "y": y_ss, "c": c_ss, "i": i_ss}


def simulate_solow_swan(
    params: SolowSwanParameters,
    k0: float,
    s_path: np.ndarray,
    n_path: np.ndarray,
    A_path: np.ndarray,
    T: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Simula la dinámica temporal del modelo de Solow-Swan dadas las sendas exógenas de s, n, A.

    Acumulación de capital:
        k_{t+1} = (1 - delta - n_t) * k_t + s_t * A_t * k_t^alpha

    Parameters
    ----------
    params : SolowSwanParameters
    k0 : float
        Capital per cápita inicial.
    s_path : np.ndarray
        Senda de tasa de ahorro de longitud T.
    n_path : np.ndarray
        Senda de crecimiento poblacional de longitud T.
    A_path : np.ndarray
        Senda de TFP de longitud T.
    T : int
        Horizonte de simulación.

    Returns
    -------
    dict
        Diccionario con las sendas 'k', 'y', 'c', 'i', 'gy' (tasa de crecimiento de y) de longitud T.
    """
    alpha = params.alpha
    delta = params.delta

    k = np.zeros(T)
    y = np.zeros(T)
    c = np.zeros(T)
    inv = np.zeros(T)
    gy = np.zeros(T)

    # Inicialización del período 0
    k[0] = k0
    y[0] = A_path[0] * k[0] ** alpha
    c[0] = (1.0 - s_path[0]) * y[0]
    inv[0] = s_path[0] * y[0]
    gy[0] = 0.0  # no hay período anterior

    # Simulación paso a paso periodo a periodo
    for t in range(1, T):
        # Ley de movimiento del capital por trabajador (considera depreciación y crecimiento poblacional)
        k[t] = (1.0 - delta - n_path[t - 1]) * k[t - 1] + s_path[t - 1] * A_path[t - 1] * k[t - 1] ** alpha
        y[t] = A_path[t] * k[t] ** alpha
        c[t] = (1.0 - s_path[t]) * y[t]
        inv[t] = s_path[t] * y[t]
        gy[t] = (y[t] - y[t - 1]) / y[t - 1] if y[t - 1] > 0 else 0.0

    return {"k": k, "y": y, "c": c, "i": inv, "gy": gy}