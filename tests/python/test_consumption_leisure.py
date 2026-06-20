import numpy as np
from macroaicomp.models.consumption_leisure import (
    ConsumptionLeisureParameters,
    solve_foc_fsolve,
    solve_direct_cvxpy,
)


def test_equivalence_fsolve_cvxpy():
    """Test that both fsolve and cvxpy solvers yield the same results."""
    params = ConsumptionLeisureParameters()
    W = np.full(params.T, 30.0)

    res_fsolve = solve_foc_fsolve(params, W)
    res_cvxpy = solve_direct_cvxpy(params, W)

    # Check that consumption, labor, and savings paths are identical within tolerances
    np.testing.assert_allclose(res_fsolve["C"], res_cvxpy["C"], rtol=1e-4, atol=1e-4)
    np.testing.assert_allclose(res_fsolve["L"], res_cvxpy["L"], rtol=1e-4, atol=1e-4)
    np.testing.assert_allclose(res_fsolve["B"], res_cvxpy["B"], rtol=1e-4, atol=1e-4)


def test_terminal_condition():
    """Test that the terminal stock of assets is exactly 0.0."""
    params = ConsumptionLeisureParameters()
    W = np.full(params.T, 30.0)

    res_fsolve = solve_foc_fsolve(params, W)
    res_cvxpy = solve_direct_cvxpy(params, W)

    assert abs(res_fsolve["B"][-1]) < 1e-6
    assert abs(res_cvxpy["B"][-1]) < 1e-6


def test_leisure_consumption_tradeoff():
    """Test that labor supply lies within rational boundaries (0 to 1)."""
    params = ConsumptionLeisureParameters()
    W = np.full(params.T, 30.0)

    res = solve_foc_fsolve(params, W)

    assert np.all(res["L"] >= 0.0)
    assert np.all(res["L"] < 1.0)
    assert np.all(res["O"] > 0.0)
    assert np.all(res["O"] <= 1.0)


def test_preference_sensitivity():
    """Test that a higher consumption weight (gamma) increases labor supply."""
    params_low = ConsumptionLeisureParameters(gamma=0.40)
    params_high = ConsumptionLeisureParameters(gamma=0.60)
    W = np.full(params_low.T, 30.0)

    res_low = solve_foc_fsolve(params_low, W)
    res_high = solve_foc_fsolve(params_high, W)

    # Average labor supply should be higher when consumption has a higher weight in utility
    assert np.mean(res_high["L"]) > np.mean(res_low["L"])


def test_interest_rate_slope():
    """Test that a high interest rate yields a positive consumption path slope."""
    # beta = 0.97, R = 0.05 => beta*(1+R) = 0.97 * 1.05 = 1.0185 > 1.0
    params = ConsumptionLeisureParameters(beta=0.97, R=0.05)
    W = np.full(params.T, 30.0)

    res = solve_foc_fsolve(params, W)

    # Consumption should have a positive slope
    for t in range(params.T - 1):
        assert res["C"][t + 1] > res["C"][t]
