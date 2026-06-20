import numpy as np
import pytest
from macroaicomp.models.ramsey import (
    RamseyParameters,
    compute_ramsey_steady_state,
    compute_ramsey_transition_matrix,
    solve_ramsey_linearized,
    solve_ramsey_nonlinear
)

def test_ramsey_steady_state_calibration():
    """Verify that steady state values match Table 10.2 of the book."""
    params = RamseyParameters()
    ss = compute_ramsey_steady_state(params)

    # Book values: k = 7.954, y = 2.066, c = 1.430, i = 0.636, R = 0.091
    assert ss["k"] == pytest.approx(7.9537, abs=1e-4)
    assert ss["y"] == pytest.approx(2.0663, abs=1e-4)
    assert ss["c"] == pytest.approx(1.4300, abs=1e-4)
    assert ss["i"] == pytest.approx(0.6363, abs=1e-4)
    assert ss["R"] == pytest.approx(0.0909, abs=1e-4)


def test_ramsey_linearized_eigenvalues():
    """Verify that the model has a unique stable saddle path."""
    params = RamseyParameters()
    _, r_stable, r_unstable, theta = compute_ramsey_transition_matrix(params)

    # Roots: lambda_1 = -0.091, lambda_2 = 0.111
    # Modules of eigenvalues: 1 + lambda_1 = 0.909 (stable), 1 + lambda_2 = 1.111 (unstable)
    assert r_stable == pytest.approx(-0.0907, abs=1e-4)
    assert r_unstable == pytest.approx(0.1115, abs=1e-4)
    assert (1.0 + r_stable) == pytest.approx(0.9093, abs=1e-4)
    assert (1.0 + r_unstable) == pytest.approx(1.1115, abs=1e-4)
    assert theta == pytest.approx(0.5751, abs=1e-4)


def test_ramsey_tfp_shock_simulation():
    """Verify transition dynamics and solver equivalence for a permanent 5% TFP shock."""
    params = RamseyParameters()
    ss_init = compute_ramsey_steady_state(params)

    T = 100
    t_shock = 5

    # Exogenous paths for non-linear solver
    A_path = np.full(T, 1.00)
    A_path[t_shock:] = 1.05
    n_path = np.full(T, 0.02)

    # 1. Solve using linearized stable saddle path
    res_lin = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_final=1.05,
        n_final=0.02,
        beta_final=params.beta,
        T=T,
        t_shock=t_shock
    )

    # Capital cannot jump at shock period
    assert res_lin["k"][t_shock] == pytest.approx(ss_init["k"])
    # Deviation at shock period must be on saddle path
    assert res_lin["c_hat"][t_shock] == pytest.approx(res_lin["k_hat"][t_shock] * 0.5751, abs=1e-3)

    # 2. Solve using non-linear fsolve
    res_nonlin = solve_ramsey_nonlinear(
        params,
        ss_init["k"],
        A_path,
        n_path,
        T=T,
        t_shock=t_shock
    )

    # Verify initial and final values match
    ss_final = compute_ramsey_steady_state(
        RamseyParameters(alpha=params.alpha, beta=params.beta, delta=params.delta, n=0.02, A=1.05)
    )

    # Capital transition is slow
    assert res_nonlin["k"][0] == pytest.approx(ss_init["k"])
    assert res_nonlin["k"][-1] == pytest.approx(ss_final["k"], abs=1e-2)
    assert res_nonlin["c"][-1] == pytest.approx(ss_final["c"], abs=1e-2)

    # Compare solvers: they should be very close for a 5% TFP shock
    assert np.allclose(res_lin["k"], res_nonlin["k"], atol=5e-2, rtol=1e-2)
    assert np.allclose(res_lin["c"], res_nonlin["c"], atol=5e-2, rtol=1e-2)
