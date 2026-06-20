"""
Ramsey-Cass-Koopmans optimal growth model.

This module implements the Ramsey model as presented in Chapter 10 of
"An Introduction to Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).

The model features:
- Infinitely-lived household maximizing discounted utility
- CRRA utility: u(c) = c^(1-sigma)/(1-sigma) with sigma -> 1 (log utility)
- Cobb-Douglas production: y = A * k^alpha
- Population growth n, technology growth g
- Saddle-path stability: one stable, one unstable eigenvalue
"""

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from scipy.optimize import fsolve


@dataclass
class RamseyParameters:
    """Parameters for the Ramsey optimal growth model.

    Calibration consistent with Table 10.2 of the book:
    k_ss = 7.954, y_ss = 2.066, c_ss = 1.430, i_ss = 0.636, R_ss = 0.091
    """

    alpha: float = 0.35  # Capital income share
    beta: float = 0.97  # Household discount factor (per period)
    delta: float = 0.06  # Capital depreciation rate
    n: float = 0.02  # Population growth rate
    A: float = 1.0  # TFP


def compute_ramsey_steady_state(params: RamseyParameters) -> Dict[str, float]:
    """
    Computes the steady state of the Ramsey model.

    At steady state:
        f'(k) = R_ss = (1/beta) - 1 + delta + n  [modified golden rule]
        alpha * A * k_ss^(alpha-1) = R_ss
        => k_ss = (alpha * A / R_ss)^(1/(1-alpha))
        y_ss = A * k_ss^alpha
        i_ss = (delta + n) * k_ss
        c_ss = y_ss - i_ss

    Parameters
    ----------
    params : RamseyParameters

    Returns
    -------
    dict with 'k', 'y', 'c', 'i', 'R'.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    n = params.n
    A = params.A

    # 1. En el estado estacionario de largo plazo:
    #    La tasa de interés real (R_ss) se iguala a la tasa de descuento intertemporal modificada por la depreciación:
    #    Por la regla de oro modificada, 1/beta = 1 + R_ss - delta
    R_ss = 1.0 / beta - 1.0 + delta
    
    # 2. El capital per cápita estacionario (k_ss) despejado de la productividad marginal del capital:
    #    f'(k) = alpha * A * k^(alpha - 1) = R_ss
    k_ss = (alpha * A / R_ss) ** (1.0 / (1.0 - alpha))
    
    # 3. Producción per cápita estacionaria y de pleno empleo (y_ss):
    y_ss = A * k_ss**alpha
    
    # 4. Inversión bruta per cápita estacionaria para reponer depreciación y absorber crecimiento poblacional:
    i_ss = (delta + n) * k_ss  # Gross investment includes population growth
    
    # 5. Consumo per cápita de equilibrio estacionario (c_ss) a partir de la restricción agregada:
    c_ss = y_ss - i_ss

    return {"k": k_ss, "y": y_ss, "c": c_ss, "i": i_ss, "R": R_ss}


def compute_ramsey_transition_matrix(
    params: RamseyParameters,
) -> Tuple[np.ndarray, float, float, float]:
    """
    Computes the linearized transition matrix and saddle-path coefficients.

    The 2x2 linearized system around (k_ss, c_ss) in log deviations:
        [c_hat_{t+1}]   =  (I + J) * [c_hat_t]
        [k_hat_{t+1}]                [k_hat_t]

    where hat denotes log-deviation from steady state.

    The Jacobian is:
        J_11 = - (alpha - 1)*Omega*Gamma / (alpha*beta*(1+n))
        J_12 = (alpha - 1)*Omega / (beta*(1+n))
        J_21 = - Gamma / (alpha*beta*(1+n))
        J_22 = (1 - beta*(1+n)) / (beta*(1+n))

    where Omega = 1 - beta + beta*delta and Gamma = Omega - alpha*beta*(delta + n).

    Parameters
    ----------
    params : RamseyParameters

    Returns
    -------
    Tuple of (J matrix, lambda_stable, lambda_unstable, theta)
    where lambda_stable = stable eigenvalue < 0, lambda_unstable = unstable eigenvalue > 0,
    and theta is the log-linear saddle-path slope.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    n = params.n

    # Parámetros agregados de linealización de primer orden alrededor del steady state:
    Omega = 1.0 - beta + beta * delta
    Gamma = Omega - alpha * beta * (delta + n)

    # Elementos de la matriz Jacobiana J para el sistema en diferencias logarítmicas [c_hat, k_hat]':
    J11 = - (alpha - 1.0) * Omega * Gamma / (alpha * beta * (1.0 + n))
    J12 = (alpha - 1.0) * Omega / (beta * (1.0 + n))
    J21 = - Gamma / (alpha * beta * (1.0 + n))
    J22 = (1.0 - beta * (1.0 + n)) / (beta * (1.0 + n))

    J = np.array([[J11, J12], [J21, J22]])

    # Obtenemos los dos autovalores del Jacobiano J
    eigenvals = np.linalg.eigvals(J)
    eigenvals = np.real(eigenvals)

    # Ordenamos de menor a mayor para separar el autovalor estable del inestable
    sorted_idx = np.argsort(eigenvals)
    lambda_1 = eigenvals[sorted_idx[0]]  # Autovalor estable (negativo, menor que 0)
    lambda_2 = eigenvals[sorted_idx[1]]  # Autovalor inestable (positivo, mayor que 0)

    # Pendiente analítica (theta) de la senda estable o saddle path para el consumo (c_hat = theta * k_hat)
    theta = alpha * (alpha - 1.0) * Omega / ((alpha - 1.0) * Omega * Gamma + alpha * beta * (1.0 + n) * lambda_1)

    return J, lambda_1, lambda_2, theta


def solve_ramsey_linearized(
    params: RamseyParameters,
    k0: float,
    A_final: float = 1.0,
    n_final: float = 0.02,
    beta_final: float = 0.97,
    T: int = 100,
    t_shock: int = 0,
) -> Dict[str, np.ndarray]:
    """
    Solves the Ramsey model using the linearized saddle-path solution in log-deviations.

    At the shock period t_shock, consumption jumps onto the new saddle path
    towards the new steady state (defined by A_final, n_final, beta_final).
    Capital is predetermined and cannot jump.

    Parameters
    ----------
    params : RamseyParameters
        Pre-shock calibration.
    k0 : float
        Initial capital stock (= pre-shock steady state capital).
    A_final : float
        Post-shock TFP.
    n_final : float
        Post-shock population growth.
    beta_final : float
        Post-shock discount factor.
    T : int
        Simulation horizon.
    t_shock : int
        Period at which the shock occurs.

    Returns
    -------
    dict with 'k', 'c', 'y', 'i', 'k_hat', 'c_hat' arrays of length T.
    """
    # 1. Definimos y calculamos el nuevo steady state post-shock
    params_post = RamseyParameters(
        alpha=params.alpha, beta=beta_final, delta=params.delta, n=n_final, A=A_final
    )
    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_new = ss_post["k"]
    c_ss_new = ss_post["c"]

    # 2. Obtenemos el autovalor estable y la pendiente theta post-shock
    _, r_stable, _, theta = compute_ramsey_transition_matrix(params_post)
    mu_s = 1.0 + r_stable  # Multiplicador estable en diferencias finitas (1 + lambda)

    k = np.zeros(T)
    c = np.zeros(T)
    y = np.zeros(T)
    i = np.zeros(T)
    k_hat = np.zeros(T)
    c_hat = np.zeros(T)

    # 3. Estado estacionario inicial previo al shock
    ss_pre = compute_ramsey_steady_state(params)
    k_ss_pre = ss_pre["k"]
    c_ss_pre = ss_pre["c"]
    y_ss_pre = ss_pre["y"]
    i_ss_pre = ss_pre["i"]

    # 4. Periodos previos al shock: la economía se mantiene estable en su equilibrio inicial
    for t in range(t_shock):
        k[t] = k_ss_pre
        c[t] = c_ss_pre
        y[t] = y_ss_pre
        i[t] = i_ss_pre
        k_hat[t] = 0.0
        c_hat[t] = 0.0

    # 5. Periodo de impacto del shock (t_shock):
    #    El capital (k) es rígido y no puede cambiar en t=t_shock (predeterminado por el pasado).
    k[t_shock] = k0  # predetermined
    k_hat[t_shock] = np.log(k0 / k_ss_new)
    #    El consumo (c) es flexible y salta de inmediato a la senda estable del nuevo steady state:
    c_hat[t_shock] = theta * k_hat[t_shock]
    c[t_shock] = c_ss_new * np.exp(c_hat[t_shock])
    y[t_shock] = A_final * k[t_shock]**params.alpha
    i[t_shock] = y[t_shock] - c[t_shock]

    # 6. Evolución temporal sobre la senda estable post-shock
    for t in range(t_shock + 1, T):
        k_hat[t] = mu_s * k_hat[t - 1]
        c_hat[t] = theta * k_hat[t]
        k[t] = k_ss_new * np.exp(k_hat[t])
        c[t] = c_ss_new * np.exp(c_hat[t])
        y[t] = A_final * k[t]**params.alpha
        i[t] = y[t] - c[t]

    return {"k": k, "c": c, "y": y, "i": i, "k_hat": k_hat, "c_hat": c_hat}


def solve_ramsey_nonlinear(
    params: RamseyParameters,
    k0: float,
    A_path: np.ndarray,
    n_path: np.ndarray,
    T: int = 100,
    t_shock: int = 0,
) -> Dict[str, np.ndarray]:
    """
    Solves the Ramsey model non-linearly via shooting algorithm (fsolve).

    Finds the initial consumption c_0 at t_shock such that capital converges
    to the new post-shock steady state.

    Parameters
    ----------
    params : RamseyParameters
    k0 : float
        Capital at t_shock (predetermined, = pre-shock steady state).
    A_path : np.ndarray
        TFP path of length T.
    n_path : np.ndarray
        Population growth path of length T.
    T : int
        Simulation horizon.
    t_shock : int
        Shock period.

    Returns
    -------
    dict with 'k', 'c' arrays of length T.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta

    # Nuevo steady state de largo plazo para la condición terminal de convergencia
    params_post = RamseyParameters(
        alpha=alpha, beta=beta, delta=delta, n=n_path[-1], A=A_path[-1]
    )
    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_final = ss_post["k"]
    c_ss_final = ss_post["c"]

    ss_pre = compute_ramsey_steady_state(params)
    k_pre = ss_pre["k"]
    c_pre = ss_pre["c"]

    # Simulación temporal no lineal paso a paso dado un valor de consumo inicial (c_shock) en t_shock
    def _simulate_from_shock(c_shock):
        k_sim = np.zeros(T - t_shock)
        c_sim = np.zeros(T - t_shock)
        k_sim[0] = k0
        c_sim[0] = c_shock
        for t in range(T - t_shock - 1):
            idx = t + t_shock
            A_t = A_path[min(idx, len(A_path) - 1)]
            n_t = n_path[min(idx, len(n_path) - 1)]
            A_t1 = A_path[min(idx + 1, len(A_path) - 1)]

            y_t = A_t * k_sim[t] ** alpha
            # Ley de acumulación de capital exacta per cápita:
            k_sim[t + 1] = ((1.0 - delta) * k_sim[t] + y_t - c_sim[t]) / (1.0 + n_t)
            if k_sim[t + 1] <= 0:
                k_sim[t + 1] = 1e-8
            # Regla de Keynes-Ramsey exacta para el consumo en el siguiente periodo:
            mpk_t1 = alpha * A_t1 * k_sim[t + 1] ** (alpha - 1.0)
            c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
        return k_sim, c_sim

    # Función residual: mide la distancia entre el capital acumulado al final y el steady state final
    def _residuals(c_shock_arr):
        k_sim, _ = _simulate_from_shock(c_shock_arr[0])
        return [k_sim[-1] - k_ss_final]

    # Método de Disparo (Shooting) mediante Búsqueda de fsolve:
    # 1. Obtenemos una estimación inicial usando la aproximación lineal
    _, _, _, theta = compute_ramsey_transition_matrix(params_post)
    c_shock_guess = c_ss_final * np.exp(theta * np.log(k0 / k_ss_final))
    c0_guess = [c_shock_guess]
    # 2. fsolve busca el valor exacto de consumo inicial (c_shock) que satisface la convergencia terminal
    sol = fsolve(_residuals, c0_guess)
    c_shock = sol[0]

    k_full = np.zeros(T)
    c_full = np.zeros(T)

    # 3. Reconstruimos los vectores de la simulación pre-shock
    for t in range(t_shock):
        k_full[t] = k_pre
        c_full[t] = c_pre

    # 4. Acoplamos los resultados post-shock simulados con el consumo inicial corregido
    k_sim, c_sim = _simulate_from_shock(c_shock)
    n_post = T - t_shock
    k_full[t_shock:] = k_sim[:n_post]
    c_full[t_shock:] = c_sim[:n_post]

    return {"k": k_full, "c": c_full}