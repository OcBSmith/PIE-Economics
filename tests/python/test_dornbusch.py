import pytest
import numpy as np
from macroaicomp.models.dornbusch import (
    default_calibration,
    steady_state,
    eigenvalues,
    is_saddle_path,
    simulate_shock,
)


def test_steady_state_default_calibration():
    """Test that the steady state matches the book's numerical values."""
    params = default_calibration()
    ss = steady_state(params)

    assert pytest.approx(ss["p"], 1e-4) == 1.5
    assert pytest.approx(ss["s"], 1e-4) == 76.515
    assert pytest.approx(ss["i"], 1e-4) == 3.0
    assert pytest.approx(ss["yd"], 1e-4) == 2000.0
    assert pytest.approx(ss["dp"], 1e-4) == 0.0
    assert pytest.approx(ss["ds"], 1e-4) == 0.0


def test_eigenvalues_stability():
    """Test that the system exhibits saddle-point stability with correct eigenvalues."""
    params = default_calibration()
    lambdas = sorted(eigenvalues(params))

    # Expected eigenvalues for mu = 0.01:
    # lambda1 ≈ -0.7415, lambda2 ≈ 0.5395
    assert pytest.approx(lambdas[0], 1e-4) == -0.7415
    assert pytest.approx(lambdas[1], 1e-4) == 0.5395

    # Check that it is correctly classified as a saddle path
    # |lambda1 + 1| = |0.2585| < 1 (stable)
    # |lambda2 + 1| = |1.5395| > 1 (unstable)
    assert is_saddle_path(params) is True


def test_monetary_shock_simulation():
    """Test a monetary shock (m0 goes from 100 to 101 at t=1)."""
    params = default_calibration()
    z_initial = np.array([500.0, 100.0, 2000.0, 3.0, 0.0])
    z_final = np.array([500.0, 101.0, 2000.0, 3.0, 0.0])

    # Simulate over 30 periods with shock at t=1
    res = simulate_shock(params, z_initial, z_final, periods=30, shock_period=1)

    # Pre-shock (t=0) should be at initial steady state
    assert pytest.approx(res["p"][0], 1e-4) == 1.5
    assert pytest.approx(res["s"][0], 1e-4) == 76.515
    assert pytest.approx(res["i"][0], 1e-4) == 3.0

    # Shock period (t=1):
    # Prices are sticky: p_1 = 1.5
    assert pytest.approx(res["p"][1], 1e-4) == 1.5

    # Exchange rate s_1 jumps to 80.215 (overshooting)
    assert pytest.approx(res["s"][1], 1e-3) == 80.215

    # Interest rate drops to 1.0% (from 3.0%)
    assert pytest.approx(res["i"][1], 1e-4) == 1.0

    # Long-run convergence (t=29):
    # Should be close to new steady state: p* = 2.5, s* = 77.515
    assert pytest.approx(res["p"][-1], 1e-2) == 2.5
    assert pytest.approx(res["s"][-1], 1e-2) == 77.515
    assert pytest.approx(res["i"][-1], 1e-2) == 3.0
