"""
Dornbusch exchange rate overshooting model.

This module implements the exchange rate overshooting model as presented in Chapter 3 of
"An Introduction to Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).
It uses a discrete-time formulation with saddle-path expectations readjustment.
"""

from dataclasses import dataclass
import numpy as np
from typing import Dict, Tuple, List


@dataclass
class DornbuschParameters:
    """Parameters and exogenous variables for the Dornbusch overshooting model.

    Parameters
    ----------
    psi : float
        Income sensitivity of money demand (default: 0.05).
    theta : float
        Interest rate sensitivity of money demand (default: 0.5).
    beta1 : float
        Real exchange rate sensitivity of aggregate demand (default: 20.0).
    beta2 : float
        Nominal interest rate sensitivity of aggregate demand (default: 0.1).
    mi : float
        Speed of price adjustment (default: 0.01).
    beta0 : float
        Autonomous aggregate demand (default: 500.0).
    m0 : float
        Log of money supply (default: 100.0).
    ypot0 : float
        Potential output (default: 2000.0).
    pstar0 : float
        Log of foreign price level (default: 0.0).
    istar0 : float
        Foreign nominal interest rate (default: 3.0).
    """

    psi: float = 0.05
    theta: float = 0.5
    beta1: float = 20.0
    beta2: float = 0.1
    mi: float = 0.01
    beta0: float = 500.0
    m0: float = 100.0
    ypot0: float = 2000.0
    pstar0: float = 0.0
    istar0: float = 3.0


def default_calibration() -> DornbuschParameters:
    """Devuelve la calibración por defecto basada en las tablas del Capítulo 3."""
    return DornbuschParameters()


def steady_state(params: DornbuschParameters) -> Dict[str, float]:
    """Calcula el estado estacionario analítico del modelo de overshooting de Dornbusch.

    Parameters
    ----------
    params : DornbuschParameters
        Parámetros de calibración.

    Returns
    -------
    Dict[str, float]
        Valores de estado estacionario de 'p', 's', 'i', 'yd', 'dp', 'ds'.
    """
    # 1. Los precios nacionales (p_ss) se derivan del equilibrio del mercado monetario (LM).
    #    Cuando la producción está en su nivel potencial (ypot0) y el interés nacional iguala al extranjero (istar0):
    #    p = m - psi * ypot + theta * istar
    p_ss = params.m0 - params.psi * params.ypot0 + params.theta * params.istar0

    # 2. El tipo de cambio nominal de largo plazo (s_ss) equilibra la demanda agregada (IS).
    #    Despejando s de la ecuación IS cuando yd = ypot:
    s_ss = (
        p_ss
        + (params.ypot0 - params.beta0 + params.beta2 * params.istar0) / params.beta1
        - params.pstar0
    )

    return {
        "p": p_ss,
        "s": s_ss,
        "i": params.istar0,  # Por la condición de paridad de intereses (UIP), i = istar
        "yd": params.ypot0,  # En el largo plazo la demanda agregada coincide con el producto potencial
        "dp": 0.0,  # En el estado estacionario, los precios no varían (dp = 0)
        "ds": 0.0,  # Tampoco varía el tipo de cambio nominal (ds = 0)
    }


def coefficient_matrices(params: DornbuschParameters) -> Tuple[np.ndarray, np.ndarray]:
    """Construye las matrices de coeficientes A y B para el sistema continuo.

    Parameters
    ----------
    params : DornbuschParameters

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Las matrices A (2x2) y B (2x5).
    """
    mi = params.mi
    beta1 = params.beta1
    beta2 = params.beta2
    theta = params.theta
    psi = params.psi

    # Matriz A (2x2): Matriz de coeficientes del sistema dinámico lineal para las variables
    # endógenas de estado y expectativa: [p_t, s_t]'.
    # Modela el efecto cruzado de los precios nacionales y el tipo de cambio.
    A = np.array([[-mi * (beta1 + beta2 / theta), mi * beta1], [1.0 / theta, 0.0]])

    # Matriz B (2x5): Matriz de impacto de los shocks exógenos.
    # El vector de variables exógenas z_t se compone de: [beta0, m_t, ypot0, istar0, pstar0]'
    B = np.array(
        [
            [
                mi,
                mi * beta2 / theta,
                -mi * (1.0 + psi * beta2 / theta),
                0.0,
                mi * beta1,
            ],
            [0.0, -1.0 / theta, psi / theta, -1.0, 0.0],
        ]
    )

    return A, B


def _build_system_matrix(params: DornbuschParameters) -> np.ndarray:
    """Construye la matriz del sistema A."""
    A, _ = coefficient_matrices(params)
    return A


def eigenvalues(params: DornbuschParameters) -> List[float]:
    """Calcula los autovalores de la matriz del sistema A.

    Parameters
    ----------
    params : DornbuschParameters

    Returns
    -------
    List[float]
        Autovalores reales ordenados.
    """
    A = _build_system_matrix(params)
    eigs = np.linalg.eigvals(A)
    return list(np.real(eigs))


def is_saddle_path(params: DornbuschParameters) -> bool:
    """Comprueba si el sistema tiene estabilidad de punto de silla (un autovalor estable y uno inestable).

    Parameters
    ----------
    params : DornbuschParameters

    Returns
    -------
    bool
    """
    eigs = eigenvalues(params)
    # Un autovalor es estable si |1 + lambda| < 1 (es decir, cae dentro del círculo unitario)
    stable_count = sum(1 for lam in eigs if abs(1.0 + lam) < 1.0)
    return stable_count == 1


def simulate_shock(
    params: DornbuschParameters,
    z_initial: np.ndarray,
    z_final: np.ndarray,
    periods: int = 30,
    shock_period: int = 1,
) -> Dict[str, np.ndarray]:
    """Simula un shock permanente de política económica usando paridad de expectativas de punto de silla.

    Parameters
    ----------
    params : DornbuschParameters
    z_initial : np.ndarray
        Vector de variables exógenas iniciales.
    z_final : np.ndarray
        Vector de variables exógenas post-shock.
    periods : int
        Número de períodos a simular.
    shock_period : int
        Período del shock.

    Returns
    -------
    Dict[str, np.ndarray]
        Trayectorias simuladas.
    """
    # 1. Estado estacionario inicial previo al shock
    params_pre = DornbuschParameters(
        psi=params.psi,
        theta=params.theta,
        beta1=params.beta1,
        beta2=params.beta2,
        mi=params.mi,
        beta0=float(z_initial[0]),
        m0=float(z_initial[1]),
        ypot0=float(z_initial[2]),
        istar0=float(z_initial[3]),
        pstar0=float(z_initial[4]),
    )
    ss_pre = steady_state(params_pre)

    # 2. Estado estacionario final post-shock
    params_post = DornbuschParameters(
        psi=params.psi,
        theta=params.theta,
        beta1=params.beta1,
        beta2=params.beta2,
        mi=params.mi,
        beta0=float(z_final[0]),
        m0=float(z_final[1]),
        ypot0=float(z_final[2]),
        istar0=float(z_final[3]),
        pstar0=float(z_final[4]),
    )
    ss_post = steady_state(params_post)

    # 3. Matriz A y autovector estable para determinar la senda de salto
    A, _ = coefficient_matrices(params_post)
    eigs, V = np.linalg.eig(A)

    # Buscamos el índice del autovalor estable
    stable_idx = np.argmin(np.abs(eigs + 1.0))
    v_s = np.real(V[:, stable_idx])

    # 4. Dimensionamos los arrays de trayectorias
    t = np.arange(periods)
    p_path = np.zeros(periods)
    s_path = np.zeros(periods)
    i_path = np.zeros(periods)
    yd_path = np.zeros(periods)

    # Períodos previos al shock: la economía está en equilibrio inicial
    for tt in range(shock_period):
        p_path[tt] = ss_pre["p"]
        s_path[tt] = ss_pre["s"]
        i_path[tt] = ss_pre["i"]
        yd_path[tt] = ss_pre["yd"]

    # Período de impacto del shock (t=shock_period):
    # Los precios (p) son rígidos/predeterminados, pero el tipo de cambio (s) salta a la senda estable
    p_path[shock_period] = ss_pre["p"]
    s_path[shock_period] = ss_post["s"] + (v_s[1] / v_s[0]) * (
        p_path[shock_period] - ss_post["p"]
    )

    # Simulación temporal periodo a periodo a partir de la ley lineal
    for tt in range(shock_period + 1, periods):
        dp = A[0, 0] * (p_path[tt - 1] - ss_post["p"]) + A[0, 1] * (
            s_path[tt - 1] - ss_post["s"]
        )
        ds = A[1, 0] * (p_path[tt - 1] - ss_post["p"]) + A[1, 1] * (
            s_path[tt - 1] - ss_post["s"]
        )
        p_path[tt] = p_path[tt - 1] + dp
        s_path[tt] = s_path[tt - 1] + ds

    # Reconstrucción de variables secundarias de interés y demanda agregada post-shock
    for tt in range(shock_period, periods):
        i_path[tt] = (
            p_path[tt] - params_post.m0 + params_post.psi * params_post.ypot0
        ) / params_post.theta
        yd_path[tt] = (
            params_post.beta0
            + params_post.beta1 * (s_path[tt] - p_path[tt] + params_post.pstar0)
            - params_post.beta2 * i_path[tt]
        )

    return {
        "t": t,
        "p": p_path,
        "s": s_path,
        "i": i_path,
        "yd": yd_path,
    }
