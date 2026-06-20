import numpy as np
from macroaicomp.models.consumption_savings import (
    ConsumptionSavingParameters,
    generate_income_profile,
    solve_foc_fsolve,
    solve_direct_cvxpy,
)


def test_equivalence_fsolve_cvxpy():
    """Test that both fsolve and cvxpy solvers yield the same results."""
    params = ConsumptionSavingParameters()
    W = generate_income_profile("constant", params.T)

    res_fsolve = solve_foc_fsolve(params, W)
    res_cvxpy = solve_direct_cvxpy(params, W)

    # Check that consumption and savings paths are identical within tolerances
    np.testing.assert_allclose(res_fsolve["C"], res_cvxpy["C"], rtol=1e-4, atol=1e-4)
    np.testing.assert_allclose(res_fsolve["B"], res_cvxpy["B"], rtol=1e-4, atol=1e-4)


def test_terminal_condition():
    """Test that the terminal stock of assets is exactly 0.0."""
    params = ConsumptionSavingParameters()

    # Test for all three income profiles
    for profile in ["constant", "increasing", "retirement"]:
        W = generate_income_profile(profile, params.T)

        res_fsolve = solve_foc_fsolve(params, W)
        res_cvxpy = solve_direct_cvxpy(params, W)

        # Terminal assets B_T (index T-1 in Python) must be 0.0
        assert abs(res_fsolve["B"][-1]) < 1e-6
        assert abs(res_cvxpy["B"][-1]) < 1e-6


def test_increasing_income_borrowing():
    """Test borrowing dynamics when income is increasing over the life cycle."""
    params = ConsumptionSavingParameters()
    W = generate_income_profile("increasing", params.T)

    res = solve_foc_fsolve(params, W)

    # Because income starts low (10) and grows, the consumer borrows in early periods
    # So savings/assets B should be negative for initial periods
    assert np.any(res["B"] < 0.0)
    assert res["B"][0] < 0.0

    # Because beta * (1 + R) = 0.97 * 1.02 = 0.9894 < 1.0,
    # the optimal consumption path should have a negative slope
    for t in range(params.T - 1):
        assert res["C"][t + 1] < res["C"][t]


def test_retirement_savings_peak():
    """Test that asset accumulation peaks at retirement age and decumulates to 0."""
    params = ConsumptionSavingParameters()
    W = generate_income_profile("retirement", params.T)

    res = solve_foc_fsolve(params, W)

    # Assets must be accumulated during working years (first 20 periods, indices 0..19)
    # The peak of savings should occur at the end of the working life, i.e., index 19
    peak_idx = np.argmax(res["B"])
    assert peak_idx == 19

    # Assets should be positive during working life
    assert np.all(res["B"][:20] > 0.0)

    # During retirement (indices 20..29), assets are decumulated (slope is negative)
    for t in range(20, params.T - 1):
        assert res["B"][t + 1] < res["B"][t]


def test_discount_factor_sensitivity():
    """Test that a higher discount factor (patience) flips the consumption path slope."""
    # If beta = 0.99 and R = 0.02, beta*(1+R) = 0.99 * 1.02 = 1.0098 > 1.0
    params = ConsumptionSavingParameters(beta=0.99, R=0.02)
    W = generate_income_profile("constant", params.T)

    res = solve_foc_fsolve(params, W)

    # The optimal consumption path should have a positive slope
    for t in range(params.T - 1):
        assert res["C"][t + 1] > res["C"][t]
