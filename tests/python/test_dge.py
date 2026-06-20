"""Unit tests for the basic Dynamic General Equilibrium (DGE) model."""

import numpy as np
import pytest
from macroaicomp.models.dge import (
    DGEParameters,
    compute_steady_state,
    solve_blanchard_khan,
    solve_nonlinear_simulation,
)


def test_steady_state_calibration():
    """Verifies that the steady state values match Table 8.2 of the book."""
    params = DGEParameters()
    ss = compute_steady_state(params)

    # Exact analytical values
    assert pytest.approx(ss["K"], 1e-6) == 6.698596
    assert pytest.approx(ss["Y"], 1e-6) == 1.945783
    assert pytest.approx(ss["C"], 1e-6) == 1.543867
    assert pytest.approx(ss["I"], 1e-6) == 0.401916
    assert pytest.approx(ss["R"]) == 0.10166666666666667


def test_blanchard_khan_stability():
    """Verifies that the linearized system has exactly one stable eigenvalue."""
    params = DGEParameters()

    # Blanchard-Khan system matrices
    Omega = 1.0 - params.beta + params.beta * params.delta
    Phi = 1.0 - params.beta + (1.0 - params.alpha) * params.beta * params.delta

    A_static = np.array(
        [[1.0, 0.0], [Omega, -params.alpha * params.beta * params.delta]]
    )
    B = np.array([[0.0, params.alpha], [Phi, 0.0]])
    A_inv = np.linalg.inv(A_static)

    D = np.array([[1.0, Omega], [0.0, 1.0]])
    F = np.array([[-Omega, 0.0], [0.0, 0.0]])
    G = np.array([[1.0, 0.0], [0.0, 1.0 - params.delta]])
    H = np.array([[0.0, 0.0], [0.0, params.delta]])

    D_tilde = D + F @ A_inv @ B
    J = np.linalg.inv(D_tilde) @ (G + H @ A_inv @ B)

    eigenvals = np.linalg.eigvals(J)
    eigenvals = np.sort(np.abs(eigenvals))

    mu_1, mu_2 = eigenvals[0], eigenvals[1]

    # One stable (modulus < 1) and one unstable (modulus > 1) eigenvalue
    assert mu_1 < 1.0
    assert mu_2 > 1.0

    # Check analytical eigenvalues values (exact analytical values)
    assert pytest.approx(mu_1, 1e-5) == 0.90399
    assert pytest.approx(mu_2, 1e-5) == 1.15229


def test_tfp_shock_simulation():
    """Verifies dynamic responses to a temporary TFP shock (1% shock, rho = 0.8)."""
    params = DGEParameters()
    T = 100

    # Initial steady state capital
    ss = compute_steady_state(params)
    K0 = ss["K"]

    # Generate TFP shock path: 1.0 at t=0, 1.01 at t=1, decaying with rho=0.8
    a_hat = np.zeros(T)
    a_hat[0] = 0.0
    a_hat[1] = 0.01
    for t in range(2, T):
        a_hat[t] = params.rho * a_hat[t - 1]
    A_path = np.exp(a_hat)

    # Solve using both solvers
    res_bk = solve_blanchard_khan(params, K0, A_path, T=T)
    res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T=T)

    # 1. Predetermined capital stock: K_1 = K_ss in both simulations
    assert pytest.approx(res_bk["K"][0], 1e-12) == K0
    assert pytest.approx(res_nonlin["K"][0], 1e-12) == K0

    # 2. Consumption, Output, and Investment jump on impact (t=1, index 1)
    assert res_bk["C"][1] > ss["C"]
    assert res_bk["Y"][1] > ss["Y"]
    assert res_bk["I"][1] > ss["I"]

    assert res_nonlin["C"][1] > ss["C"]
    assert res_nonlin["Y"][1] > ss["Y"]
    assert res_nonlin["I"][1] > ss["I"]

    # 3. Capital stock peaks with delay (hump-shape)
    # Capital at index 1 is determined at index 0 (steady state).
    # Capital at index 2 (period 3) should be higher than steady state.
    assert res_bk["K"][2] > K0
    assert res_nonlin["K"][2] > K0

    # Peak in capital should occur in the first few periods (e.g. index 2 to 12)
    bk_k_peak_idx = np.argmax(res_bk["K"])
    nonlin_k_peak_idx = np.argmax(res_nonlin["K"])
    assert 2 <= bk_k_peak_idx <= 12
    assert 2 <= nonlin_k_peak_idx <= 12

    # 4. Long run convergence back to initial steady state
    assert pytest.approx(res_bk["C"][-1], 1e-3) == ss["C"]
    assert pytest.approx(res_bk["K"][-1], 1e-3) == K0
    assert pytest.approx(res_nonlin["C"][-1], 1e-3) == ss["C"]
    assert pytest.approx(res_nonlin["K"][-1], 1e-3) == K0

    # 5. Consistency check: Blanchard-Khan and non-linear simulation must be very close
    np.testing.assert_allclose(res_bk["K"], res_nonlin["K"], rtol=1e-2)
    np.testing.assert_allclose(res_bk["C"], res_nonlin["C"], rtol=1e-2)
