"""Unit tests for Tobin's Q model."""

import numpy as np
import pytest
from macroaicomp.models.tobin_q import (
    TobinQParameters,
    compute_linearized_system,
    compute_steady_state,
    solve_linearized_simulation,
    solve_nonlinear_simulation,
)


def test_steady_state():
    """Verifies the steady state calculations for default calibration."""
    params = TobinQParameters()
    ss = compute_steady_state(params)

    assert pytest.approx(ss["q"], 1e-6) == 1.0
    assert pytest.approx(ss["K"], 1e-6) == 6.8711236
    assert pytest.approx(ss["I"], 1e-6) == 0.06 * 6.8711236
    assert pytest.approx(ss["Y"], 1e-6) == 6.8711236**0.35


def test_eigenvalues_saddle_point():
    """Verifies that the eigenvalues confirm a saddle point."""
    params = TobinQParameters()
    lin_sys = compute_linearized_system(params)

    lambda_1 = lin_sys["lambda_1"]
    lambda_2 = lin_sys["lambda_2"]

    # Stable eigenvalue lambda_1 should be negative, unstable lambda_2 positive
    assert lambda_1 < 0.0
    assert lambda_2 > 0.0

    # Values matching Chapter 7 text (exact analytical values)
    assert pytest.approx(lambda_1, 1e-6) == -0.060658
    assert pytest.approx(lambda_2, 1e-6) == 0.107158

    # In discrete time, the modules in levels are 1 + lambda
    assert pytest.approx(1.0 + lambda_1, 1e-6) == 0.939342
    assert pytest.approx(1.0 + lambda_2, 1e-6) == 1.107158

    # Check stability condition: stable root must be inside unit circle in levels
    assert abs(1.0 + lambda_1) < 1.0
    assert abs(1.0 + lambda_2) > 1.0


def test_jump_formula_identity():
    """Verifies the algebraic identity of the simplified and book jump formulas."""
    params = TobinQParameters()

    # Test under different calibrations to ensure identity holds generally
    for R_val in [0.02, 0.03, 0.04, 0.05]:
        for phi_val in [5.0, 10.0, 15.0]:
            params.R = R_val
            params.phi = phi_val
            lin_sys = compute_linearized_system(params)

            # Both formulas for theta must be numerically identical
            assert pytest.approx(lin_sys["theta"], 1e-12) == lin_sys["theta_book"]


def test_simulation_interest_rate_shock():
    """Verifies simulation dynamics under a permanent interest rate shock (4% -> 3%)."""
    params = TobinQParameters()
    T = 100

    # Initial steady state capital at R = 4%
    ss_init = compute_steady_state(params, R=0.04)
    K0 = ss_init["K"]

    # Permanent shock to R: 4% at t=0, drops to 3% for t >= 1
    R_path = np.zeros(T)
    R_path[0] = 0.04
    R_path[1:] = 0.03

    # Solve using both solvers
    res_lin = solve_linearized_simulation(params, K0, R_path, T=T)
    res_nonlin = solve_nonlinear_simulation(params, K0, R_path, T=T)

    # 1. Predetermined capital stock: K_1 = K0 in both simulations
    assert pytest.approx(res_lin["K"][0], 1e-12) == K0
    assert pytest.approx(res_nonlin["K"][0], 1e-12) == K0

    # 2. Convergence to new steady state (R = 3%)
    ss_final = compute_steady_state(params, R=0.03)
    K_ss_final = ss_final["K"]

    assert pytest.approx(res_lin["K"][-1], 1e-3) == K_ss_final
    assert pytest.approx(res_nonlin["K"][-1], 1e-3) == K_ss_final

    # 3. Q ratio dynamics: jumps above 1.0 initially, then converges back to 1.0
    assert res_lin["q"][0] > 1.0
    assert res_nonlin["q"][0] > 1.0

    # Analytical jump value for q_1 should be ~1.1033
    assert pytest.approx(res_lin["q"][0], 1e-4) == 1.1033

    # Q must converge to 1.0 in the long run
    assert pytest.approx(res_lin["q"][-1], 1e-3) == 1.0
    assert pytest.approx(res_nonlin["q"][-1], 1e-3) == 1.0

    # 4. Consistency: linearized and non-linear simulation should be very close
    # since the shock is small (1 percentage point drop)
    np.testing.assert_allclose(res_lin["K"], res_nonlin["K"], rtol=1e-2)
    np.testing.assert_allclose(res_lin["q"], res_nonlin["q"], rtol=1e-2)
