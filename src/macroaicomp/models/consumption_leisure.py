"""
Consumption-Leisure model (finite horizon).

This module implements the life-cycle consumption-leisure (labor supply) model
as presented in Chapter 5 of "An Introduction to Computational Macroeconomics"
(Bongers, Gómez, Torres, 2019).

The household has preferences over consumption (C) and leisure (O = 1 - L),
where L is the labor supply. Utility is:
    u(C, O) = gamma * log(C) + (1 - gamma) * log(1 - L)

Two solvers are provided:
1. solve_foc_fsolve: Euler equations + intratemporal FOC via scipy.fsolve.
2. solve_direct_cvxpy: Direct convex optimization via cvxpy.
"""

from dataclasses import dataclass
from typing import Dict

import numpy as np
from scipy.optimize import fsolve

try:
    import cvxpy as cp

    _CVXPY_AVAILABLE = True
except ImportError:
    _CVXPY_AVAILABLE = False


@dataclass
class ConsumptionLeisureParameters:
    """Parámetros de calibración para el modelo de ciclo vital consumo-ocio (Cap. 5)."""

    T: int = 30  # Horizonte temporal (número de períodos)
    beta: float = 0.97  # Factor de descuento del hogar (paciencia)
    R: float = 0.02  # Tipo de interés real neto
    gamma: float = (
        0.5  # Peso del consumo en la función de utilidad Cobb-Douglas (el resto es ocio)
    )
    B0: float = 0.0  # Riqueza o activos financieros iniciales


def solve_foc_fsolve(
    params: ConsumptionLeisureParameters, W: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema óptimo de consumo-ocio mediante condiciones de primer orden (FOCs) usando fsolve.

    Las condiciones de optimalidad son:
        - Ecuación de Euler: gamma / C_{t+1} = beta * (1+R) * gamma / C_t
          => C_{t+1} = beta * (1+R) * C_t
        - FOC intratemporal (Consumo-Trabajo): (1-gamma)/(1-L_t) = (gamma/C_t) * W_t
          => L_t = 1 - (1-gamma) * C_t / (gamma * W_t)     (acotado en [0, 1))
        - Restricción presupuestaria: B_{t+1} = (1+R)*B_t + W_t*L_t - C_t
        - Condición terminal (Transversalidad): B_T = 0

    Parameters
    ----------
    params : ConsumptionLeisureParameters
    W : np.ndarray
        Senda salarial (ingreso por unidad de trabajo) de longitud T.

    Returns
    -------
    dict
        Diccionario con los vectores de consumo 'C', trabajo 'L', ocio 'O' y riqueza 'B'.
    """
    T = params.T
    beta = params.beta
    R = params.R
    gamma = params.gamma
    B0 = params.B0
    growth = beta * (1.0 + R)

    def _build_path(C0):
        # 1. El consumo crece a tasa constante según la ecuación de Euler
        C = np.array([C0 * (growth**t) for t in range(T)])
        # 2. La oferta de trabajo L se ajusta intratemporalmente según el salario relativo y el consumo
        L = np.clip(1.0 - (1.0 - gamma) * C / (gamma * W), 0.0, 1.0 - 1e-9)
        # 3. Calculamos la evolución de la riqueza (activos acumulados) periodo a periodo
        B = np.zeros(T)
        B[0] = (1.0 + R) * B0 + W[0] * L[0] - C[0]
        for t in range(1, T):
            B[t] = (1.0 + R) * B[t - 1] + W[t] * L[t] - C[t]
        return C, L, B

    def _residuals(C0_arr):
        # 4. Condición residual: al final del horizonte T, la riqueza B[-1] debe ser exactamente 0
        _, _, B = _build_path(C0_arr[0])
        return [B[-1]]

    # 5. fsolve busca el consumo inicial C0 óptimo que satisface la condición terminal
    C0_guess = [np.mean(W) * gamma]
    sol = fsolve(_residuals, C0_guess, full_output=True)
    C0 = sol[0][0]

    C, L, B = _build_path(C0)
    O = 1.0 - L

    return {"C": C, "L": L, "O": O, "B": B}


def solve_direct_cvxpy(
    params: ConsumptionLeisureParameters, W: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema de optimización óptima de consumo-ocio mediante optimización convexa directa (cvxpy).

    Maximiza:
        sum_{t=0}^{T-1} beta^t * [gamma * log(C_t) + (1-gamma) * log(1 - L_t)]

    Sujeto a:
        B_{t+1} = (1+R)*B_t + W_t*L_t - C_t
        B_0 = B0,  B_{T-1} = 0
        C_t >= 1e-8,  0 <= L_t < 1

    Parameters
    ----------
    params : ConsumptionLeisureParameters
    W : np.ndarray
        Senda de salarios de longitud T.

    Returns
    -------
    dict
        Diccionario con las trayectorias óptimas de 'C', 'L', 'O' y 'B'.
    """
    if not _CVXPY_AVAILABLE:
        raise ImportError("Se requiere cvxpy para ejecutar solve_direct_cvxpy.")

    T = params.T
    beta = params.beta
    R = params.R
    gamma = params.gamma
    B0 = params.B0

    C = cp.Variable(T, nonneg=True)
    L = cp.Variable(T)
    B = cp.Variable(T)

    # 1. Definimos las restricciones del problema de optimización intertemporal
    constraints = [C >= 1e-8, L >= 0.0, L <= 1.0 - 1e-8]
    constraints.append(B[0] == (1.0 + R) * B0 + W[0] * L[0] - C[0])
    for t in range(1, T):
        constraints.append(B[t] == (1.0 + R) * B[t - 1] + W[t] * L[t] - C[t])
    constraints.append(B[T - 1] == 0.0)

    # 2. Función de utilidad agregada descontada a maximizar
    discount = np.array([beta**t for t in range(T)])
    objective = cp.Maximize(
        discount @ (gamma * cp.log(C) + (1.0 - gamma) * cp.log(1.0 - L))
    )
    prob = cp.Problem(objective, constraints)

    # 3. Intentamos resolver con resolvedores convexos de alta precisión
    for solver_name in ["CLARABEL", "SCS", None]:
        try:
            if solver_name == "CLARABEL":
                prob.solve(
                    solver=cp.CLARABEL,
                    tol_gap_abs=1e-11,
                    tol_gap_rel=1e-11,
                    tol_feas=1e-11,
                    verbose=False,
                )
            elif solver_name == "SCS":
                prob.solve(solver=cp.SCS, eps_abs=1e-9, eps_rel=1e-9, verbose=False)
            else:
                prob.solve(verbose=False)
            if prob.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                break
        except Exception:
            continue

    L_val = L.value
    O_val = 1.0 - L_val

    return {"C": C.value, "L": L_val, "O": O_val, "B": B.value}
