"""Richardson's arms race model.

Reference: Bongers, A., Gómez, T. and Torres, J.L. (2019), "An Introduction
to Computational Macroeconomics", Chapter 1. Vernon Press.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class ArmsRaceParams:
    """Calibration of Richardson's arms race model (eq. 1.9-1.11).

    Parameters
    ----------
    alpha : float
        Elasticity of dx1 with respect to x1.
    beta : float
        Elasticity of dx1 with respect to x2.
    gamma : float
        Elasticity of dx2 with respect to x1.
    delta : float
        Elasticity of dx2 with respect to x2.
    theta : float
        Elasticity of dx1 with respect to z1.
    eta : float
        Elasticity of dx2 with respect to z2.
    """

    alpha: float
    beta: float
    gamma: float
    delta: float
    theta: float
    eta: float


def coefficient_matrices(params: ArmsRaceParams) -> tuple[np.ndarray, np.ndarray]:
    """Build the A and B matrices of the dynamic system (eq. 1.7-1.8).

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Matrix A (2x2, coefficients of the endogenous variables) and
        matrix B (2x2, coefficients of the exogenous variables).
    """
    a = np.array([[-params.alpha, params.beta], [params.gamma, -params.delta]])
    b = np.array([[params.theta, 0.0], [0.0, params.eta]])
    return a, b


def steady_state(params: ArmsRaceParams, z: np.ndarray) -> np.ndarray:
    """Compute the steady state of the system (eq. 1.14).

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration.
    z : np.ndarray
        Exogenous variables (z1, z2).

    Returns
    -------
    np.ndarray
        Steady-state values (x1_bar, x2_bar).

    Examples
    --------
    >>> params = ArmsRaceParams(0.5, 0.25, 0.25, 0.5, 1.0, 1.0)
    >>> steady_state(params, np.array([1.0, 1.0]))
    array([4., 4.])
    """
    a, b = coefficient_matrices(params)
    return -np.linalg.inv(a) @ b @ z


def eigenvalues(params: ArmsRaceParams) -> np.ndarray:
    """Compute the eigenvalues of matrix A (eq. 1.20-1.25).

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration.

    Returns
    -------
    np.ndarray
        Eigenvalues (lambda1, lambda2) of matrix A.

    Examples
    --------
    >>> params = ArmsRaceParams(0.5, 0.25, 0.25, 0.5, 1.0, 1.0)
    >>> sorted(np.round(eigenvalues(params), 2))
    [-0.75, -0.25]
    """
    a, _ = coefficient_matrices(params)
    return np.linalg.eigvals(a)


def is_saddle_path(params: ArmsRaceParams) -> bool:
    """Classify the steady state as a saddle point or globally stable.

    Following the stability criterion of Appendix A, a real eigenvalue
    lambda is stable if |lambda + 1| < 1. The steady state is a saddle
    point if exactly one of the two eigenvalues is stable.

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration.

    Returns
    -------
    bool
        True if the steady state is a saddle point, False if it is
        globally stable (or globally unstable).
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
    """Simulate the transition dynamics after a shock (Section 1.5).

    Reproduces the recursion used in the spreadsheet "ICM-1-1.xls":
    starting from the initial steady state, x_(t+1) = x_t + dx_t, where
    dx_t is evaluated with z_initial for t < shock_period and with
    z_final from shock_period onward. Valid for globally stable
    calibrations; for saddle-point calibrations use
    `simulate_saddle_path` instead.

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration.
    z_initial : np.ndarray
        Exogenous variables before the shock.
    z_final : np.ndarray
        Exogenous variables from the shock period onward.
    periods : int
        Number of periods to simulate (the book uses 30).
    shock_period : int
        Period at which z switches from z_initial to z_final.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Time paths (x1, x2), each of length `periods`.
    """
    a, b = coefficient_matrices(params)
    x = np.zeros((periods, 2))
    x[0] = steady_state(params, z_initial)
    for t in range(periods - 1):
        z_t = z_final if t + 1 >= shock_period else z_initial
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
    """Simulate transition dynamics when the steady state is a saddle point.

    Reproduces the spreadsheet "ICM-1-2.xls": the forward-looking
    `jump_variable` readjusts instantaneously, at `shock_period`, onto
    the stable saddle path (eq. 1.39), while the other variable still
    evolves through the standard backward recursion for that period.
    From `shock_period` onward both variables follow the model's
    difference equations evaluated at z_final.

    Parameters
    ----------
    params : ArmsRaceParams
        Model calibration. Must produce a saddle-point steady state
        (check with `is_saddle_path`).
    z_initial : np.ndarray
        Exogenous variables before the shock.
    z_final : np.ndarray
        Exogenous variables from the shock period onward.
    periods : int
        Number of periods to simulate.
    shock_period : int
        Period at which the disturbance occurs and the jump variable
        readjusts onto the stable path.
    jump_variable : int
        Index (0 or 1) of the forward-looking variable that jumps.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Time paths (x1, x2), each of length `periods`.

    Raises
    ------
    ValueError
        If the calibration does not produce a saddle-point steady state.
    """
    if not is_saddle_path(params):
        raise ValueError("Calibration does not produce a saddle-point steady state.")

    a, b = coefficient_matrices(params)
    lambdas = eigenvalues(params)
    stable_lambda = lambdas[np.argmin(np.abs(lambdas + 1))]
    other_variable = 1 - jump_variable
    x_bar_final = steady_state(params, z_final)

    x = np.zeros((periods, 2))
    x[0] = steady_state(params, z_initial)
    for t in range(periods - 1):
        if t + 1 == shock_period:
            x[t + 1, other_variable] = x[t, other_variable] + (
                a[other_variable] @ x[t] + b[other_variable] @ z_initial
            )
            row = a[jump_variable]
            x[t + 1, jump_variable] = (
                row[other_variable] * x[t + 1, other_variable]
                + b[jump_variable, jump_variable] * z_final[jump_variable]
                + stable_lambda * x_bar_final[jump_variable]
            ) / (stable_lambda - row[jump_variable])
        else:
            z_t = z_final if t + 1 > shock_period else z_initial
            x[t + 1] = x[t] + (a @ x[t] + b @ z_t)
    return x[:, 0], x[:, 1]
