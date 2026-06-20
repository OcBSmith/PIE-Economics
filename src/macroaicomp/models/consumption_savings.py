"""
Consumption-Savings model (finite horizon).

This module implements the life-cycle consumption-savings model as presented
in Chapter 4 of "An Introduction to Computational Macroeconomics"
(Bongers, Gómez, Torres, 2019).

Two solvers are provided:
1. solve_foc_fsolve: Solves the Euler equation system of first-order conditions via scipy.fsolve.
2. solve_direct_cvxpy: Solves the consumer problem directly via cvxpy convex optimization.
"""

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from scipy.optimize import fsolve

try:
    import cvxpy as cp

    _CVXPY_AVAILABLE = True
except ImportError:
    _CVXPY_AVAILABLE = False


@dataclass
class ConsumptionSavingParameters:
    """Parámetros de calibración para el modelo de consumo-ahorro en horizonte finito (Cap. 4)."""

    T: int = 30  # Horizonte temporal (duración de la vida del consumidor)
    beta: float = 0.97  # Factor de descuento del consumidor (paciencia)
    R: float = 0.02  # Tipo de interés real neto
    B0: float = 0.0  # Riqueza o activos financieros iniciales


def generate_income_profile(profile: str, T: int) -> np.ndarray:
    """
    Genera un perfil de ingresos de longitud T según el caso de estudio.

    Parameters
    ----------
    profile : str
        Perfil deseado ('constant', 'increasing', 'retirement').
    T : int
        Número de períodos.

    Returns
    -------
    np.ndarray
        Vector de ingresos a lo largo del tiempo.
    """
    W = np.zeros(T)
    if profile == "constant":
        # Ingreso constante de 10 unidades
        W[:] = 10.0
    elif profile == "increasing":
        # El ingreso comienza bajo (10) y crece linealmente hasta 20
        W = np.linspace(10.0, 20.0, T)
    elif profile == "retirement":
        # Trabaja los primeros 20 periodos (ingreso = 10), luego se jubila (ingreso = 0)
        working = min(20, T)
        W[:working] = 10.0
        W[working:] = 0.0
    else:
        raise ValueError(f"Perfil de ingresos desconocido: {profile}")
    return W


def solve_foc_fsolve(
    params: ConsumptionSavingParameters, W: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema óptimo de consumo-ahorro mediante la ecuación de Euler (fsolve).

    La ecuación de Euler es:
        C_{t+1} = beta * (1 + R) * C_t

    Sujeto a:
        B_{t+1} = (1 + R) * B_t + W_t - C_t
        B_0 = B0,  B_T = 0

    Parameters
    ----------
    params : ConsumptionSavingParameters
    W : np.ndarray
        Senda de ingresos de longitud T.

    Returns
    -------
    dict
        Diccionario con los vectores de consumo 'C' y riqueza/activos 'B' de longitud T.
    """
    T = params.T
    beta = params.beta
    R = params.R
    B0 = params.B0
    growth = beta * (1.0 + R)

    def _residuals(C0_guess):
        C0 = C0_guess[0]
        # 1. El consumo evoluciona según la ecuación de Euler
        C = np.array([C0 * (growth**t) for t in range(T)])
        # 2. La riqueza B se acumula dinámicamente con los intereses y la brecha ingreso-consumo
        B = np.zeros(T)
        B[0] = (1.0 + R) * B0 + W[0] - C[0]
        for t in range(1, T):
            B[t] = (1.0 + R) * B[t - 1] + W[t] - C[t]
        # 3. Al final de la vida del consumidor (periodo T), los activos deben ser exactamente 0
        return [B[-1]]

    # 4. Solucionador numérico para encontrar el consumo inicial C0 óptimo
    C0_guess = [np.mean(W)]
    sol = fsolve(_residuals, C0_guess, full_output=True)
    C0 = sol[0][0]
    C = np.array([C0 * (growth**t) for t in range(T)])

    B = np.zeros(T)
    B[0] = (1.0 + R) * B0 + W[0] - C[0]
    for t in range(1, T):
        B[t] = (1.0 + R) * B[t - 1] + W[t] - C[t]

    return {"C": C, "B": B}


def solve_direct_cvxpy(
    params: ConsumptionSavingParameters, W: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema óptimo de consumo-ahorro mediante optimización convexa directa (cvxpy).

    Maximiza:
        sum_{t=0}^{T-1} beta^t * log(C_t)

    Sujeto a:
        B_{t+1} = (1 + R) * B_t + W_t - C_t,  t = 0, ..., T-1
        B_0 = B0
        B_{T-1} = 0
        C_t >= 1e-8

    Parameters
    ----------
    params : ConsumptionSavingParameters
    W : np.ndarray
        Senda de ingresos de longitud T.

    Returns
    -------
    dict
        Diccionario con las trayectorias óptimas de 'C' y 'B'.
    """
    if not _CVXPY_AVAILABLE:
        raise ImportError("Se requiere cvxpy para ejecutar solve_direct_cvxpy.")

    T = params.T
    beta = params.beta
    R = params.R
    B0 = params.B0

    C = cp.Variable(T, name="C", nonneg=True)
    B = cp.Variable(T, name="B")

    # 1. Definimos las restricciones del modelo
    constraints = []
    constraints.append(B[0] == (1.0 + R) * B0 + W[0] - C[0])
    for t in range(1, T):
        constraints.append(B[t] == (1.0 + R) * B[t - 1] + W[t] - C[t])
    constraints.append(B[T - 1] == 0.0)
    constraints.append(C >= 1e-8)

    # 2. Función objetivo intertemporal (utilidad logarítmica sumada y descontada)
    discount = np.array([beta**t for t in range(T)])
    objective = cp.Maximize(discount @ cp.log(C))

    prob = cp.Problem(objective, constraints)
    
    # 3. Resolvedor numérico convexo
    for solver_name in ['CLARABEL', 'SCS', None]:
        try:
            if solver_name == 'CLARABEL':
                prob.solve(solver=cp.CLARABEL, tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11, verbose=False)
            elif solver_name == 'SCS':
                prob.solve(solver=cp.SCS, eps_abs=1e-9, eps_rel=1e-9, verbose=False)
            else:
                prob.solve(verbose=False)
            if prob.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                break
        except Exception:
            continue

    return {
        "C": C.value,
        "B": B.value,
    }