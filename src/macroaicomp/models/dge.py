"""
Basic Dynamic General Equilibrium (DGE) model.

This module implements the basic RBC-like DGE model as presented in Chapter 8 of
"An Introduction to Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).

The model features:
- Representative household with CRRA utility over consumption
- Cobb-Douglas production with capital and TFP
- Capital accumulation (investment)
- Linearization via Blanchard-Khan method
- Non-linear shooting algorithm via scipy.fsolve
"""

from dataclasses import dataclass
from typing import Dict

import numpy as np
from scipy.optimize import fsolve


@dataclass
class DGEParameters:
    """Parámetros de calibración para el modelo básico de Equilibrio General Dinámico (Cap. 8)."""

    alpha: float = 0.35  # Participación del capital en la producción (Cobb-Douglas)
    beta: float = 0.96   # Factor de descuento intertemporal del hogar (paciencia)
    delta: float = 0.06  # Tasa de depreciación física del capital
    rho: float = 0.80    # Persistencia autorregresiva AR(1) del shock tecnológico (TFP)
    A: float = 1.0       # Estado estacionario de la TFP (Productividad Total de los Factores)


def compute_steady_state(params: DGEParameters) -> Dict[str, float]:
    """
    Calcula el estado estacionario determinista del modelo DGE.

    En el estado estacionario:
        R_ss = 1/beta - 1 + delta  [Regla de Euler]
        alpha * A * K_ss^(alpha-1) = R_ss  [Productividad marginal del capital]

    Parameters
    ----------
    params : DGEParameters
        Parámetros del modelo.

    Returns
    -------
    dict
        Diccionario con 'K' (capital), 'Y' (producción), 'C' (consumo), 'I' (inversión) y 'R' (interés) de largo plazo.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    A = params.A

    # 1. Tasa de interés real de largo plazo a partir de la paciencia intertemporal:
    R_ss = 1.0 / beta - 1.0 + delta
    
    # 2. Stock de capital per cápita estacionario:
    K_ss = (alpha * A / R_ss) ** (1.0 / (1.0 - alpha))
    
    # 3. Producción agregada estacionaria:
    Y_ss = A * K_ss**alpha
    
    # 4. Inversión para cubrir la depreciación:
    I_ss = delta * K_ss
    
    # 5. Consumo de equilibrio:
    C_ss = Y_ss - I_ss

    return {"K": K_ss, "Y": Y_ss, "C": C_ss, "I": I_ss, "R": R_ss}


def solve_blanchard_khan(
    params: DGEParameters,
    K0: float,
    A_path: np.ndarray,
    T: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Resuelve el modelo DGE linealizado usando las funciones de política de Blanchard-Khan.

    El sistema dinámico linealizado en desviaciones porcentuales (hat) es:
        [E_t c_hat_{t+1}]   =  J * [c_hat_t] + M * a_hat_t
        [k_hat_{t+1}]              [k_hat_t]

    Parameters
    ----------
    params : DGEParameters
    K0 : float
        Stock de capital inicial.
    A_path : np.ndarray
        Senda de TFP simulada de longitud T.
    T : int
        Horizonte de simulación.

    Returns
    -------
    dict
        Diccionario con las sendas de 'K', 'C', 'Y', 'I' de longitud T.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    rho = params.rho

    ss = compute_steady_state(params)
    K_ss = ss["K"]
    C_ss = ss["C"]
    Y_ss = ss["Y"]
    I_ss = ss["I"]

    # 1. Definimos las matrices de linealización según el Apéndice N del libro:
    Omega = 1.0 - beta + beta * delta
    Phi = 1.0 - beta + (1.0 - alpha) * beta * delta

    A = np.array([[1.0, 0.0], [Omega, -alpha * beta * delta]])
    B = np.array([[0.0, alpha], [Phi, 0.0]])
    C_mat = np.array([[1.0], [0.0]])
    D = np.array([[1.0, Omega], [0.0, 1.0]])
    F = np.array([[-Omega, 0.0], [0.0, 0.0]])
    G = np.array([[1.0, 0.0], [0.0, 1.0 - delta]])
    H = np.array([[0.0, 0.0], [0.0, delta]])

    # 2. Computamos las matrices reducidas J y M de Blanchard-Khan:
    invA = np.linalg.inv(A)
    inv_term = np.linalg.inv(D + F @ invA @ B)
    J = inv_term @ (G + H @ invA @ B)
    M = inv_term @ (H @ invA @ C_mat - F @ invA @ C_mat * rho)

    # 3. Descomposición espectral de la matriz J para aislar autovalores:
    eigenvals, P = np.linalg.eig(J)
    eigenvals = np.real(eigenvals)
    sorted_idx = np.argsort(np.abs(eigenvals))
    mu_s = eigenvals[sorted_idx[0]]  # Autovalor estable (dentro del círculo unitario)
    mu_u = eigenvals[sorted_idx[1]]  # Autovalor inestable (fuera del círculo unitario)

    # 4. Construimos la matriz invertible P y su inversa Q:
    P_sorted = np.zeros_like(P)
    P_sorted[:, 0] = P[:, sorted_idx[0]]
    P_sorted[:, 1] = P[:, sorted_idx[1]]
    Q = np.linalg.inv(P_sorted)

    # Desacoplamiento del componente explosivo:
    QM = Q @ M
    N2 = - QM[1, 0] / (mu_u - rho)

    # Coeficientes óptimos de política económica (reglas de decisión linealizadas):
    eta_ck = - Q[1, 1] / Q[1, 0]
    eta_ca = N2 / Q[1, 0]
    eta_kk = J[1, 0] * eta_ck + J[1, 1]
    eta_ka = J[1, 0] * eta_ca + M[1, 0]

    # 5. Simulamos la trayectoria temporal en desviaciones relativas (hat):
    k_hat = np.zeros(T)
    c_hat = np.zeros(T)
    a_hat = np.log(A_path)

    k_hat[0] = (K0 - K_ss) / K_ss

    for t in range(T - 1):
        c_hat[t] = eta_ck * k_hat[t] + eta_ca * a_hat[t]
        k_hat[t + 1] = eta_kk * k_hat[t] + eta_ka * a_hat[t]
        
    c_hat[-1] = eta_ck * k_hat[-1] + eta_ca * a_hat[-1]

    # 6. Reconvertimos las variables de desviaciones a niveles absolutos de mercado:
    K = K_ss * (1.0 + k_hat)
    C = C_ss * (1.0 + c_hat)
    Y = np.zeros(T)
    I = np.zeros(T)

    for t in range(T):
        Y[t] = A_path[t] * K[t]**alpha
        I[t] = Y[t] - C[t]

    return {"K": K, "C": C, "Y": Y, "I": I}


def solve_nonlinear_simulation(
    params: DGEParameters,
    K0: float,
    A_path: np.ndarray,
    T: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Resuelve el modelo DGE exacto no lineal mediante un solucionador de ecuaciones simultáneas sobre toda la senda.

    Encuentra las sendas completas de K y C que satisfacen conjuntamente la ecuación de Euler no lineal 
    y la ley exacta de acumulación de capital.

    Parameters
    ----------
    params : DGEParameters
    K0 : float
        Capital inicial.
    A_path : np.ndarray
        Senda de TFP de longitud T.
    T : int
        Horizonte de simulación.

    Returns
    -------
    dict
        Diccionario con las sendas 'K', 'C', 'Y', 'I' calculadas sin aproximaciones lineales.
    """
    alpha = params.alpha
    beta = params.beta
    delta = params.delta

    ss = compute_steady_state(params)
    K_ss = ss["K"]

    # 1. Obtenemos una estimación inicial de alta calidad usando Blanchard-Khan linealizado:
    res_bk = solve_blanchard_khan(params, K0, A_path, T=T)
    K_guess = res_bk["K"]
    C_guess = res_bk["C"]

    # 2. Definimos el sistema global de ecuaciones simultáneas no lineales:
    def system_equations(vars_flat):
        K = np.zeros(T)
        C = np.zeros(T)
        K[0] = K0
        K[1:] = vars_flat[:T-1]
        q = len(vars_flat)
        C[:] = vars_flat[T-1:]

        eqs = []

        # A. Ley de acumulación de capital exacta per cápita: K[t+1] = (1-delta)*K[t] + Y_t - C[t]
        for t in range(T - 1):
            A_t = A_path[min(t, len(A_path) - 1)]
            Y_t = A_t * K[t] ** alpha
            eqs.append(K[t+1] - ((1.0 - delta) * K[t] + Y_t - C[t]))

        # B. Ecuación de Euler de Consumo exacta: C[t+1] = beta * (1 + R_{t+1} - delta) * C[t]
        for t in range(T - 1):
            A_t1 = A_path[min(t + 1, len(A_path) - 1)]
            K_next_bounded = np.maximum(K[t+1], 1e-8)
            R_t1 = alpha * A_t1 * K_next_bounded ** (alpha - 1.0)
            eqs.append(C[t+1] - (beta * (1.0 + R_t1 - delta) * C[t]))

        # C. Condición terminal (Transversalidad): K en el último período debe converger a K_ss
        eqs.append(K[-1] - K_ss)

        return eqs

    # 3. fsolve refina numéricamente la senda completa partiendo de la estimación de Blanchard-Khan
    guess_flat = np.concatenate([K_guess[1:], C_guess])
    sol = fsolve(system_equations, guess_flat)

    K = np.zeros(T)
    C = np.zeros(T)
    K[0] = K0
    K[1:] = sol[:T-1]
    C[:] = sol[T-1:]

    Y = np.zeros(T)
    I = np.zeros(T)
    for t in range(T):
        Y[t] = A_path[min(t, len(A_path) - 1)] * K[t]**alpha
        I[t] = Y[t] - C[t]

    return {"K": K, "C": C, "Y": Y, "I": I}