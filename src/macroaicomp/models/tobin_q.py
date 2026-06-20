"""
Tobin's Q investment model.

This module implements the model presented in Chapter 7 of "An Introduction to
Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).
It includes steady state calculations, log-linearization around the steady state,
analytical stable path (saddle-path) solver, and a numerical non-linear solver
using SciPy's fsolve.
"""

from dataclasses import dataclass
from typing import Dict, Union

import numpy as np
from scipy.optimize import fsolve


@dataclass
class TobinQParameters:
    """Parámetros y variables exógenas para el modelo Q de Tobin (Cap. 7).

    Parámetros
    ----------
    alpha : float
        Elasticidad de producción respecto al capital físico (por defecto: 0.35).
    delta : float
        Tasa de depreciación física del capital (por defecto: 0.06).
    phi : float
        Parámetro de costes de ajuste de la inversión (por defecto: 10.0).
    R : float
        Tasa de interés real neta (por defecto: 0.04).
    """

    alpha: float = 0.35
    delta: float = 0.06
    phi: float = 10.0
    R: float = 0.04


def compute_steady_state(
    params: TobinQParameters, R: Union[float, None] = None
) -> Dict[str, float]:
    """Calcula los valores de estado estacionario para el modelo de la Q de Tobin.

    Parameters
    ----------
    params : TobinQParameters
        Parámetros de calibración.
    R : float, opcional
        Tasa de interés real a usar si difiere de la calibración por defecto.

    Returns
    -------
    Dict[str, float]
        Valores de estado de largo plazo de 'q' (Q ratio), 'K' (capital), 'I' (inversión) e 'Y' (producción).
    """
    R_val = R if R is not None else params.R
    delta = params.delta
    alpha = params.alpha

    # 1. En el estado estacionario de largo plazo, el ratio Q de Tobin es exactamente 1.0
    q_ss = 1.0
    # 2. El stock de capital estacionario K_ss se deriva igualando la productividad marginal al tipo de interés real neto
    K_ss = ((R_val + delta) / alpha) ** (1.0 / (alpha - 1.0))
    # 3. La inversión bruta (I_ss) cubre exactamente la depreciación del capital (delta * K_ss)
    I_ss = delta * K_ss
    # 4. La producción agregada Y_ss se calcula con la función de producción Cobb-Douglas
    Y_ss = K_ss**alpha

    return {"q": q_ss, "K": K_ss, "I": I_ss, "Y": Y_ss}


def compute_linearized_system(params: TobinQParameters) -> Dict[str, float]:
    """
    Calcula la matriz de transición linealizada y los autovalores estables para el modelo.

    El sistema dinámico linealizado 2x2 en log-desviaciones (hat) es:
        [dq_t] = A * [q_hat_t]
        [dk_t]       [k_hat_t]

    Parameters
    ----------
    params : TobinQParameters

    Returns
    -------
    dict
        Contiene autovalores ('lambda_1', 'lambda_2'), multiplicadores dinámicos ('mu_1', 'mu_2'),
        la pendiente de la senda estable o saddle-path ('theta') y la matriz J ('A').
    """
    alpha = params.alpha
    delta = params.delta
    phi = params.phi
    R = params.R

    # Coeficientes de la matriz de transición A del sistema dinámico linealizado:
    A11 = (R * phi - (alpha - 1.0) * (R + delta)) / phi
    A12 = - (alpha - 1.0) * (R + delta)
    A21 = 1.0 / phi
    A22 = 0.0

    A = np.array([[A11, A12], [A21, A22]])

    # Obtenemos los autovalores para clasificar la estabilidad
    eigenvals = np.linalg.eigvals(A)
    eigenvals = np.real(eigenvals)

    sorted_idx = np.argsort(eigenvals)
    lambda_1 = eigenvals[sorted_idx[0]]  # Autovalor estable (negativo)
    lambda_2 = eigenvals[sorted_idx[1]]  # Autovalor inestable (positivo)

    mu_1 = 1.0 + lambda_1
    mu_2 = 1.0 + lambda_2

    # Pendiente analítica (theta) de la senda estable: q_hat_t = theta * k_hat_t
    theta = phi * lambda_1
    theta_book = theta

    return {
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "mu_1": mu_1,
        "mu_2": mu_2,
        "theta": theta,
        "theta_book": theta_book,
        "A": A,
    }


def solve_linearized_simulation(
    params: TobinQParameters,
    K0: float,
    R_path: np.ndarray,
    T: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Simula la dinámica linealizada de la Q de Tobin a lo largo del saddle path.

    Parameters
    ----------
    params : TobinQParameters
    K0 : float
        Stock de capital inicial.
    R_path : np.ndarray
        Senda del tipo de interés real de longitud T.
    T : int
        Horizonte de simulación.

    Returns
    -------
    dict
        Trayectorias simuladas de 'K', 'q', 'I', 'Y'.
    """
    # 1. Definimos y calculamos el nuevo steady state post-shock
    params_post = TobinQParameters(
        alpha=params.alpha, delta=params.delta, phi=params.phi, R=R_path[-1]
    )
    ss_final = compute_steady_state(params_post)
    K_ss = ss_final["K"]

    # 2. Obtenemos el sistema linealizado post-shock
    lin = compute_linearized_system(params_post)
    lambda_1 = lin["lambda_1"]
    theta = lin["theta"]

    K = np.zeros(T)
    q = np.zeros(T)
    k_hat = np.zeros(T)
    q_hat = np.zeros(T)

    # 3. Inicialización usando desviaciones logarítmicas (hat) respecto al nuevo steady state:
    k_hat[0] = np.log(K0 / K_ss)
    q_hat[0] = theta * k_hat[0]  # El ratio Q salta inmediatamente a la senda de silla estable

    K[0] = K0
    q[0] = np.exp(q_hat[0])

    # 4. Transición temporal a lo largo de la senda estable
    for t in range(1, T):
        k_hat[t] = (1.0 + lambda_1) * k_hat[t - 1]
        q_hat[t] = theta * k_hat[t]
        
        K[t] = K_ss * np.exp(k_hat[t])
        q[t] = np.exp(q_hat[t])

    # 5. Reconstrucción de variables reales de inversión y output
    # Ley de inversión con costes de ajuste cuadráticos: I_t = delta * K_t + K_t * (q_t - 1) / phi
    I = params.delta * K + K * (q - 1.0) / params.phi
    Y = K**params.alpha

    return {"K": K, "q": q, "I": I, "Y": Y}


def solve_nonlinear_simulation(
    params: TobinQParameters,
    K0: float,
    R_path: np.ndarray,
    T: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Simula la dinámica no lineal exacta del modelo mediante un resolvedor de ecuaciones simultáneas sobre toda la senda.

    Encuentra las sendas de K y q que satisfacen conjuntamente la ecuación de Euler no lineal 
    y la ley exacta de acumulación de capital.

    Parameters
    ----------
    params : TobinQParameters
    K0 : float
        Capital inicial.
    R_path : np.ndarray
        Senda del tipo de interés real de longitud T.
    T : int
        Horizonte de simulación.

    Returns
    -------
    dict
        Trayectorias simuladas de 'K', 'q', 'I', 'Y' calculadas sin aproximaciones lineales.
    """
    alpha = params.alpha
    delta = params.delta
    phi = params.phi

    # 1. Obtenemos una estimación inicial de alta calidad usando el modelo linealizado
    res_lin = solve_linearized_simulation(params, K0, R_path, T=T)
    K_guess = res_lin["K"]
    q_guess = res_lin["q"]

    # 2. Definimos el sistema global de ecuaciones simultáneas no lineales:
    def system_equations(vars_flat):
        K = np.zeros(T)
        q = np.zeros(T)
        K[0] = K0
        K[1:] = vars_flat[:T-1]
        q[:] = vars_flat[T-1:]

        eqs = []

        # A. Acumulación exacta de capital: K[t+1] = (1-delta)*K[t] + I_t, donde I_t considera costes de ajuste
        for t in range(T - 1):
            I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
            eqs.append(K[t+1] - ((1.0 - delta) * K[t] + I_t))

        # B. Dinámica temporal de la Q de Euler: q[t+1] = (1+R_t)*q[t] - PMK_t + delta - (q[t]-1)^2 / (2*phi)
        for t in range(T - 1):
            R_t = R_path[min(t, len(R_path) - 1)]
            mpk = alpha * K[t] ** (alpha - 1.0)
            eqs.append(q[t+1] - ((1.0 + R_t) * q[t] - mpk + delta - (q[t] - 1.0) ** 2 / (2.0 * phi)))

        # C. Condición terminal (Condición de Transversalidad aproximada en T):
        eqs.append(q[-1] - 1.0)

        return eqs

    # 3. fsolve busca numéricamente la senda exacta resolviendo el sistema
    guess_flat = np.concatenate([K_guess[1:], q_guess])
    sol = fsolve(system_equations, guess_flat)

    K = np.zeros(T)
    q = np.zeros(T)
    K[0] = K0
    K[1:] = sol[:T-1]
    q[:] = sol[T-1:]

    I = delta * K + K * (q - 1.0) / phi
    Y = K**alpha

    return {"K": K, "q": q, "I": I, "Y": Y}