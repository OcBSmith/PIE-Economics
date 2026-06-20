"""
Fiscal Policy model (non-distortionary and distortionary taxes + social security).

This module implements the fiscal policy models as presented in Chapter 6 of
"An Introduction to Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).

Three policy regimes are modelled:
1. Non-distortionary taxes (lump-sum): Ricardian equivalence holds.
2. Distortionary taxes (income tax tauw, consumption tax tauc, capital tax taur).
3. Social Security / Pension capitalization system.
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
class FiscalPolicyParameters:
    """Parámetros de calibración para el modelo de política fiscal (Cap. 6)."""

    T: int = 30  # Horizonte temporal (duración de la vida activa/jubilación)
    beta: float = 0.97  # Factor de descuento del consumidor (paciencia)
    R: float = 0.02  # Tipo de interés real neto
    gamma: float = 0.5  # Peso del consumo en la función de utilidad (el resto es ocio)
    B0: float = 0.0  # Riqueza o activos financieros iniciales
    tauw: float = 0.0  # Tasa impositiva sobre las rentas del trabajo (impuesto directo)
    tauc: float = 0.0  # Tasa impositiva sobre el consumo (impuesto indirecto / IVA)
    taur: float = 0.0  # Tasa impositiva sobre los rendimientos del capital (ahorro)
    tau_ss: float = 0.0  # Tasa de cotización a la Seguridad Social (pensiones)
    t_star: int = 26  # Período de jubilación (comienzo del retiro de la vida laboral)


def solve_non_distortionary(
    params: FiscalPolicyParameters,
    W: np.ndarray,
    return_transfers: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema de consumo-ahorro con impuestos de suma fija (no distorsionadores).

    Parameters
    ----------
    params : FiscalPolicyParameters
    W : np.ndarray
        Senda salarial antes de impuestos de longitud T.
    return_transfers : bool
        Si es True, la recaudación fiscal se devuelve íntegramente como transferencias de suma fija.

    Returns
    -------
    dict
        Diccionario con las sendas óptimas de consumo 'C' y riqueza 'B'.
    """
    T = params.T
    beta = params.beta
    R = params.R
    tauw = params.tauw
    B0 = params.B0
    growth = beta * (1.0 + R)

    # 1. Determinamos la renta neta efectiva (si se devuelven las transferencias se produce equivalencia ricardiana)
    if return_transfers:
        Y_eff = W.copy()  # tauw * W se detrae pero se reinyecta => neto es igual a W
    else:
        Y_eff = W * (1.0 - tauw)

    def _build_path(C0):
        # 2. El consumo evoluciona según la ecuación de Euler clásica
        C = np.array([C0 * (growth**t) for t in range(T)])
        # 3. La riqueza private se acumula con la renta neta efectiva
        B = np.zeros(T)
        B[0] = (1.0 + R) * B0 + Y_eff[0] - C[0]
        for t in range(1, T):
            B[t] = (1.0 + R) * B[t - 1] + Y_eff[t] - C[t]
        return C, B

    def _residuals(C0_arr):
        # 4. Condición de transversalidad de final de vida (riqueza final es 0)
        _, B = _build_path(C0_arr[0])
        return [B[-1]]

    # 5. fsolve busca el consumo óptimo inicial C0
    C0_guess = [np.mean(Y_eff)]
    sol = fsolve(_residuals, C0_guess)
    C, B = _build_path(sol[0])
    return {"C": C, "B": B}


def solve_distortionary_foc(
    params: FiscalPolicyParameters,
    W: np.ndarray,
    return_transfers: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema con impuestos distorsionadores (tauw, tauc, taur) mediante FOCs.

    Parameters
    ----------
    params : FiscalPolicyParameters
    W : np.ndarray
        Senda salarial antes de impuestos de longitud T.
    return_transfers : bool
        Si es True, la recaudación se devuelve como transferencias.

    Returns
    -------
    dict
        Diccionario con las sendas óptimas de 'C', 'L' y 'B'.
    """
    T = params.T
    beta = params.beta
    R_net = params.R * (1.0 - params.taur)  # Rendimiento del ahorro neto de impuestos
    R_gross = 1.0 + R_net
    tauw = params.tauw
    tauc = params.tauc
    gamma = params.gamma
    B0 = params.B0

    # Crecimiento del consumo considerando los impuestos al capital
    growth = beta * R_gross

    def _build_path(C0):
        # 1. Trayectoria óptima de consumo intertemporal
        C = np.array([C0 * (growth**t) for t in range(T)])
        # 2. Decisión de oferta de trabajo L que se distorsiona por los impuestos directos e indirectos
        net_wage = W * (1.0 - tauw) / (1.0 + tauc)
        net_wage = np.where(net_wage < 1e-12, 1e-12, net_wage)
        L = np.clip(1.0 - (1.0 - gamma) * C / (gamma * net_wage), 0.0, 1.0 - 1e-9)

        # 3. Transferencias fiscales (si se devuelven)
        if return_transfers:
            transfer = tauw * W * L + tauc * C + params.taur * params.R * np.maximum(0.0, np.concatenate([[B0], np.zeros(T - 1)]))
        else:
            transfer = np.zeros(T)

        # 4. Acumulación intertemporal de activos privados
        B = np.zeros(T)
        B[0] = (1.0 + params.R) * B0 + W[0] * L[0] * (1.0 - tauw) - C[0] * (1.0 + tauc) + transfer[0]
        for t in range(1, T):
            R_asset = params.R * (1.0 - params.taur)
            B[t] = (1.0 + R_asset) * B[t - 1] + W[t] * L[t] * (1.0 - tauw) - C[t] * (1.0 + tauc) + transfer[t]
        return C, L, B

    def _residuals(C0_arr):
        _, _, B = _build_path(C0_arr[0])
        return [B[-1]]

    # 5. Hallamos la condición inicial exacta C0
    C0_guess = [np.mean(W) * gamma * 0.5]
    sol = fsolve(_residuals, C0_guess)
    C, L, B = _build_path(sol[0])
    return {"C": C, "L": L, "B": B}


def solve_distortionary_cvxpy(
    params: FiscalPolicyParameters,
    W: np.ndarray,
    return_transfers: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Resuelve el problema con impuestos distorsionadores mediante optimización convexa directa (cvxpy).

    Parameters
    ----------
    params : FiscalPolicyParameters
    W : np.ndarray
        Senda de salarios de longitud T.
    return_transfers : bool
        Si es True, la recaudación se devuelve como transferencias de suma fija.

    Returns
    -------
    dict
        Diccionario con las sendas óptimas de 'C', 'L' y 'B'.
    """
    if not _CVXPY_AVAILABLE:
        raise ImportError("Se requiere cvxpy.")

    T = params.T
    beta = params.beta
    R = params.R
    tauw = params.tauw
    tauc = params.tauc
    taur = params.taur
    gamma = params.gamma
    B0 = params.B0
    R_asset = R * (1.0 - taur)

    C = cp.Variable(T, nonneg=True)
    L = cp.Variable(T)
    B = cp.Variable(T)

    constraints = [C >= 1e-8, L >= 0.0, L <= 1.0 - 1e-8]

    # 1. Definimos las restricciones presupuestarias intertemporales
    if return_transfers:
        # En caso de devolución de impuestos neutra, los impuestos y transferencias se cancelan netos
        constraints.append(
            B[0] == (1.0 + R_asset) * B0 + W[0] * L[0] - C[0]
        )
        for t in range(1, T):
            constraints.append(
                B[t] == (1.0 + R_asset) * B[t - 1] + W[t] * L[t] - C[t]
            )
    else:
        constraints.append(
            B[0] == (1.0 + R_asset) * B0 + W[0] * (1.0 - tauw) * L[0] - (1.0 + tauc) * C[0]
        )
        for t in range(1, T):
            constraints.append(
                B[t] == (1.0 + R_asset) * B[t - 1] + W[t] * (1.0 - tauw) * L[t] - (1.0 + tauc) * C[t]
            )

    constraints.append(B[T - 1] == 0.0)

    # 2. Factor de penalización por distorsión sobre las preferencias (sustitución trabajo-ocio)
    if return_transfers:
        tauw_capped = min(tauw, 1.0 - 1e-9)
        ratio = ((1.0 - gamma) / gamma) * (1.0 + tauc) / (1.0 - tauw_capped)
        gamma_eff = 1.0 / (1.0 + ratio)
    else:
        gamma_eff = gamma

    # 3. Maximización de utilidad agregada
    discount = np.array([beta**t for t in range(T)])
    objective = cp.Maximize(
        discount @ (gamma_eff * cp.log(C) + (1.0 - gamma_eff) * cp.log(1.0 - L))
    )
    prob = cp.Problem(objective, constraints)
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

    return {"C": C.value, "L": L.value, "B": B.value}


def solve_social_security(
    params: FiscalPolicyParameters, W: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Resuelve el sistema de pensiones/Seguridad Social mediante capitalización.

    Parameters
    ----------
    params : FiscalPolicyParameters
        tau_ss: Tasa de contribución.
        t_star: Período de jubilación.
    W : np.ndarray
        Senda salarial de longitud T (cero durante el retiro).

    Returns
    -------
    dict
        Diccionario con 'C', 'B' y el valor de la 'Pension' devuelta.
    """
    T = params.T
    beta = params.beta
    R = params.R
    tau_ss = params.tau_ss
    t_star = params.t_star
    B0 = params.B0
    growth = beta * (1.0 + R)

    # 1. Calculamos la pensión acumulada capitalizada por las aportaciones realizadas durante la vida activa
    pension = 0.0
    for t in range(t_star):
        pension += tau_ss * W[t] * (1.0 + R) ** (t_star - 1 - t)

    # 2. Senda de renta efectiva neta de cotizaciones
    Y_eff = np.zeros(T)
    for t in range(t_star):
        Y_eff[t] = W[t] * (1.0 - tau_ss)
    # Se reinyecta la pensión en el periodo de jubilación t_star
    if t_star < T:
        Y_eff[t_star] += pension

    def _build_path(C0):
        C = np.array([C0 * (growth**t) for t in range(T)])
        B = np.zeros(T)
        B[0] = (1.0 + R) * B0 + Y_eff[0] - C[0]
        for t in range(1, T):
            B[t] = (1.0 + R) * B[t - 1] + Y_eff[t] - C[t]
        return C, B

    def _residuals(C0_arr):
        _, B = _build_path(C0_arr[0])
        return [B[-1]]

    # 3. fsolve busca el consumo inicial C0 óptimo
    C0_guess = [np.mean(W[W > 0]) * (1.0 - tau_ss) if np.any(W > 0) else 1.0]
    sol = fsolve(_residuals, C0_guess)
    C, B = _build_path(sol[0])

    return {"C": C, "B": B, "Pension": pension}