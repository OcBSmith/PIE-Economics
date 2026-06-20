"""Richardson's arms race model.

Reference: Bongers, A., Gómez, T. and Torres, J.L. (2019), "An Introduction
to Computational Macroeconomics", Chapter 1. Vernon Press.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class ArmsRaceParams:
    """Calibración del modelo de carrera armamentística de Richardson (eq. 1.9-1.11).

    Parámetros
    ----------
    alpha : float
        Elasticidad de dx1 respecto a x1 (coeficiente de fatiga/gasto).
    beta : float
        Elasticidad de dx1 respecto a x2 (coeficiente de defensa/reacción).
    gamma : float
        Elasticidad de dx2 respecto a x1 (coeficiente de defensa/reacción).
    delta : float
        Elasticidad de dx2 respecto a x2 (coeficiente de fatiga/gasto).
    theta : float
        Elasticidad de dx1 respecto a z1 (coeficiente de agravio/hostilidad).
    eta : float
        Elasticidad de dx2 respecto a z2 (coeficiente de agravio/hostilidad).
    """

    alpha: float
    beta: float
    gamma: float
    delta: float
    theta: float
    eta: float


def coefficient_matrices(params: ArmsRaceParams) -> tuple[np.ndarray, np.ndarray]:
    """Construye las matrices de coeficientes A y B del sistema dinámico (eq. 1.7-1.8).

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Matriz A (2x2, coeficientes de las variables endógenas) y
        matriz B (2x2, coeficientes de las variables exógenas).
    """
    a = np.array([[-params.alpha, params.beta], [params.gamma, -params.delta]])
    b = np.array([[params.theta, 0.0], [0.0, params.eta]])
    return a, b


def steady_state(params: ArmsRaceParams, z: np.ndarray) -> np.ndarray:
    """Calcula el estado estacionario del sistema (eq. 1.14).

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo.
    z : np.ndarray
        Variables exógenas (z1, z2).

    Returns
    -------
    np.ndarray
        Valores de estado estacionario (x1_bar, x2_bar).
    """
    a, b = coefficient_matrices(params)
    return -np.linalg.inv(a) @ b @ z


def eigenvalues(params: ArmsRaceParams) -> np.ndarray:
    """Calcula los autovalores de la matriz A (eq. 1.20-1.25).

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo.

    Returns
    -------
    np.ndarray
        Autovalores (lambda1, lambda2) de la matriz A.
    """
    a, _ = coefficient_matrices(params)
    return np.linalg.eigvals(a)


def is_saddle_path(params: ArmsRaceParams) -> bool:
    """Clasifica el estado estacionario como un punto de silla o globalmente estable.

    Siguiendo el criterio de estabilidad del Apéndice A, un autovalor real
    lambda es estable si |lambda + 1| < 1. El estado estacionario es un punto
    de silla si exactamente uno de los dos autovalores es estable.

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo.

    Returns
    -------
    bool
        True si el estado estacionario es un punto de silla, False en caso contrario.
    """
    moduli = np.abs(eigenvalues(params) + 1)
    return bool((moduli < 1).sum() == 1)


def simulate(
    params: ArmsRaceParams,
    z_initial: np.ndarray,
    z_final: np.ndarray,
    periods: int = 30,
    shock_period: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Simula la dinámica de transición tras un shock (Sección 1.5).

    Reproduce la recursión de la hoja de cálculo "ICM-1-1.xls":
    comenzando desde el estado estacionario inicial, x_(t+1) = x_t + dx_t, donde
    dx_t se evalúa con z_initial para t < shock_period y con z_final
    a partir de shock_period en adelante. Válido para calibraciones globalmente
    estables.

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo.
    z_initial : np.ndarray
        Variables exógenas antes del shock.
    z_final : np.ndarray
        Variables exógenas a partir del shock.
    periods : int
        Número de períodos a simular (el libro usa 30).
    shock_period : int
        Período en el que z cambia de z_initial a z_final.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Trayectorias temporales (x1, x2), ambas de longitud `periods`.
    """
    a, b = coefficient_matrices(params)
    x = np.zeros((periods, 2))
    x[0] = steady_state(params, z_initial)
    for t in range(periods - 1):
        z_t = z_final if t + 1 >= shock_period else z_initial
        # Ecuación de recurrencia exacta periodo a periodo:
        x[t + 1] = x[t] + (a @ x[t] + b @ z_t)
    return x[:, 0], x[:, 1]


def simulate_saddle_path(
    params: ArmsRaceParams,
    z_initial: np.ndarray,
    z_final: np.ndarray,
    periods: int = 30,
    shock_period: int = 1,
    jump_variable: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Simula la dinámica de transición cuando el estado estacionario es un punto de silla.

    Reproduce la hoja de cálculo "ICM-1-2.xls": la variable de expectativa
    (jump_variable) se reajusta instantáneamente en el periodo del shock para
    situarse sobre la senda estable, mientras que la otra variable continúa su
    dinámica histórica en ese periodo.

    Parameters
    ----------
    params : ArmsRaceParams
        Calibración del modelo (debe producir un punto de silla).
    z_initial : np.ndarray
        Variables exógenas antes del shock.
    z_final : np.ndarray
        Variables exógenas a partir del shock.
    periods : int
        Número de períodos a simular.
    shock_period : int
        Período en el que ocurre la perturbación.
    jump_variable : int
        Índice (0 o 1) de la variable flexible que salta.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Trayectorias temporales (x1, x2), ambas de longitud `periods`.
    """
    if not is_saddle_path(params):
        raise ValueError(
            "La calibración no produce un estado estacionario de punto de silla."
        )

    a, b = coefficient_matrices(params)
    lambdas = eigenvalues(params)
    # Encontramos el autovalor estable (el más cercano al límite de estabilidad)
    stable_lambda = lambdas[np.argmin(np.abs(lambdas + 1))]
    other_variable = 1 - jump_variable
    x_bar_final = steady_state(params, z_final)

    x = np.zeros((periods, 2))
    x[0] = steady_state(params, z_initial)
    for t in range(periods - 1):
        if t + 1 == shock_period:
            # 1. La variable predeterminada evoluciona hacia atrás con las variables previas
            x[t + 1, other_variable] = x[t, other_variable] + (
                a[other_variable] @ x[t] + b[other_variable] @ z_initial
            )
            # 2. La variable flexible (jump) da un salto inmediato para caer en la senda estable (saddle path)
            row = a[jump_variable]
            x[t + 1, jump_variable] = (
                row[other_variable] * x[t + 1, other_variable]
                + b[jump_variable, jump_variable] * z_final[jump_variable]
                + stable_lambda * x_bar_final[jump_variable]
            ) / (stable_lambda - row[jump_variable])
        else:
            # 3. Resto de periodos: evolución normal según el nuevo estado de la economía
            z_t = z_final if t + 1 > shock_period else z_initial
            x[t + 1] = x[t] + (a @ x[t] + b @ z_t)
    return x[:, 0], x[:, 1]
