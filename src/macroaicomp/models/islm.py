"""
Dynamic IS-LM model.

This module implements the dynamic IS-LM model as presented in Chapter 2 of
"An Introduction to Computational Macroeconomics" (Bongers, Gómez, Torres, 2019).
It uses a continuous-time ODE formulation solvable with scipy.integrate.solve_ivp.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple

import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class ISLMParameters:
    """Parámetros de calibración para el modelo IS-LM dinámico.
    
    Campos:
    - theta: Sensibilidad de la demanda de dinero al tipo de interés [θ] (cuánto cae la demanda si sube el interés)
    - psi: Sensibilidad de la demanda de dinero a la renta [ψ] (cuánto sube la demanda por motivo transacción)
    - beta1: Sensibilidad de la demanda agregada (Inversión/Consumo) al tipo de interés real [β1]
    - mi: Parámetro de la Curva de Phillips [μ]: sensibilidad de la inflación a la brecha de producción (output gap)
    - ni: Velocidad de ajuste de la producción en el mercado de bienes [ν]
    - beta0: Demanda agregada autónoma [β0] (Gasto público, consumo autónomo)
    - m0: Oferta monetaria inicial dictada por el Banco Central [M0]
    - ypot0: Producción potencial o de pleno empleo [Y_barra]
    """

    theta: float = 0.5
    psi: float = 0.01
    beta1: float = 50.0
    mi: float = 0.01
    ni: float = 0.2
    beta0: float = 2100.0
    m0: float = 100.0
    ypot0: float = 2000.0


def default_calibration() -> ISLMParameters:
    """
    Devuelve una instancia de `ISLMParameters` con los valores por defecto. 
    Estos valores coinciden con el oráculo de MATLAB provisto en los apéndices.
    """
    return ISLMParameters()


def steady_state(params: ISLMParameters) -> Dict[str, float]:
    """
    Calcula el Estado Estacionario (Steady State) analítico del modelo IS-LM dinámico.
    En estado estacionario, las variaciones (derivadas) de la producción (dY) y los precios (dP) son exactamente cero.

    Parameters
    ----------
    params : ISLMParameters
        La calibración del modelo.

    Returns
    -------
    dict
        Un diccionario que contiene los valores de equilibrio de 'Y', 'P', 'i', 'Yd', 'dP', 'dY'.
    """
    # 1. En el equilibrio de largo plazo, la producción es igual a la potencial por la Curva de Phillips.
    y_bar = params.ypot0
    
    # 2. Despejamos el nivel de precios P igualando la oferta y demanda de bienes y dinero.
    p_bar = (
        (params.theta * params.beta0) / params.beta1
        + params.m0
        - (params.psi + params.theta / params.beta1) * y_bar
    )
    
    # 3. Sustituyendo P en la ecuación de la LM, obtenemos el tipo de interés de equilibrio.
    i_bar = (p_bar - params.m0 + params.psi * y_bar) / params.theta
    
    # 4. La demanda agregada es la parte autónoma menos la parte sensible al interés.
    yd_bar = params.beta0 - params.beta1 * i_bar

    return {
        "Y": y_bar,
        "P": p_bar,
        "i": i_bar,
        "Yd": yd_bar,
        "dP": 0.0,
        "dY": 0.0,
    }


def system_dynamics(t: float, state: np.ndarray, params: ISLMParameters) -> np.ndarray:
    """
    Define el campo vectorial del sistema de ecuaciones diferenciales continuas.
    Calcula las derivadas [dY/dt, dP/dt] para el sistema dinámico IS-LM.

    Parameters
    ----------
    t : float
        Tiempo (necesario para el solver de ODEs aunque sea autónomo).
    state : np.ndarray
        [Y, P] vector de estado actual.
    params : ISLMParameters
        Parámetros del modelo.

    Returns
    -------
    np.ndarray
        [dY/dt, dP/dt]
    """
    Y, P = state

    # 1. Equilibrio instantáneo en el mercado de dinero (Curva LM).
    # Suponemos ajuste instantáneo, por lo que despejamos el tipo de interés `i`.
    i = (P - params.m0 + params.psi * Y) / params.theta

    # 2. Demanda Agregada (Curva IS)
    Yd = params.beta0 - params.beta1 * i

    # 3. Leyes de Movimiento (Derivadas temporales)
    # Ajuste gradual de la producción según exceso de demanda (mercado de bienes)
    dY = params.ni * (Yd - Y)
    
    # Ajuste gradual de los precios (inflación) según la brecha de producción (Curva de Phillips)
    dP = params.mi * (Y - params.ypot0)

    return np.array([dY, dP])


def simulate(
    params: ISLMParameters,
    Y0: float,
    P0: float,
    T: float = 50.0,
    n_points: int = 500,
) -> Dict[str, Any]:
    """
    Simula el sistema IS-LM desde condiciones iniciales usando solve_ivp.

    Parameters
    ----------
    params : ISLMParameters
        Parámetros del modelo.
    Y0 : float
        Producción inicial.
    P0 : float
        Nivel de precios inicial.
    T : float
        Horizonte temporal.
    n_points : int
        Número de puntos de evaluación.

    Returns
    -------
    dict
        Diccionario con las trayectorias de 't', 'Y', 'P', 'i', 'Yd'.
    """
    t_span = (0.0, T)
    t_eval = np.linspace(0.0, T, n_points)
    sol = solve_ivp(
        system_dynamics,
        t_span,
        [Y0, P0],
        args=(params,),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )

    Y_path = sol.y[0]
    P_path = sol.y[1]
    i_path = (P_path - params.m0 + params.psi * Y_path) / params.theta
    Yd_path = params.beta0 - params.beta1 * i_path

    return {
        "t": sol.t,
        "Y": Y_path,
        "P": P_path,
        "i": i_path,
        "Yd": Yd_path,
    }


def simulate_shock(
    params: ISLMParameters,
    initial_state: np.ndarray,
    t_span: Tuple[float, float],
    t_eval: np.ndarray,
) -> Any:
    """
    Simula la dinámica del modelo IS-LM tras un shock partiendo de unas condiciones iniciales.
    Utiliza el algoritmo Runge-Kutta de orden 5 (RK45) con tolerancias estrictas para alta precisión.
    """
    return solve_ivp(
        system_dynamics,
        t_span,
        initial_state,
        args=(params,),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )