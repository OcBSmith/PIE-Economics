import pytest
import numpy as np
from macroaicomp.models.fiscal_policy import (
    FiscalPolicyParameters,
    solve_non_distortionary,
    solve_distortionary_foc,
    solve_distortionary_cvxpy,
    solve_social_security,
)


def test_non_distortionary_ricardian_equivalence():
    """Test Ricardian Equivalence in the non-distortionary tax model (Section 6.2).

    If transfers are returned, the consumption path must be identical to the no-tax case.
    """
    T = 30
    W = np.full(T, 10.0)

    # 1. No tax case
    params_no_tax = FiscalPolicyParameters(tauw=0.0)
    res_no_tax = solve_non_distortionary(params_no_tax, W)

    # 2. Tax with returned transfers (Ricardian Equivalence)
    params_tax_returned = FiscalPolicyParameters(tauw=0.40)
    res_tax_returned = solve_non_distortionary(params_tax_returned, W, return_transfers=True)

    np.testing.assert_allclose(res_no_tax["C"], res_tax_returned["C"], rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(res_no_tax["B"], res_tax_returned["B"], rtol=1e-6, atol=1e-6)

    # 3. Tax without returned transfers (Income effect only, consumption and savings drop)
    res_tax_not_returned = solve_non_distortionary(params_tax_returned, W, return_transfers=False)
    assert np.all(res_tax_not_returned["C"] < res_no_tax["C"])
    assert np.all(np.abs(res_tax_not_returned["B"]) < np.abs(res_no_tax["B"]))


def test_distortionary_equivalence_fsolve_cvxpy():
    """Test that both FOC (fsolve) and Direct Optimization (cvxpy) yield identical results.

    Tests both return_transfers=False and return_transfers=True.
    """
    params = FiscalPolicyParameters()
    W = np.full(params.T, 100.0)

    for ret_trans in [False, True]:
        res_foc = solve_distortionary_foc(params, W, return_transfers=ret_trans)
        res_cvxpy = solve_distortionary_cvxpy(params, W, return_transfers=ret_trans)

        # Numerical equivalence check
        np.testing.assert_allclose(res_foc["C"], res_cvxpy["C"], rtol=1e-4, atol=1e-4)
        np.testing.assert_allclose(res_foc["L"], res_cvxpy["L"], rtol=1e-4, atol=1e-4)
        np.testing.assert_allclose(res_foc["B"], res_cvxpy["B"], rtol=1e-4, atol=1e-4)


def test_labor_supply_distortion():
    """Test that higher labor income tax or consumption tax distorts and reduces labor supply."""
    params_base = FiscalPolicyParameters(tauw=0.10, tauc=0.0)
    params_high_tauw = FiscalPolicyParameters(tauw=0.40, tauc=0.0)
    params_high_tauc = FiscalPolicyParameters(tauw=0.10, tauc=0.30)
    W = np.full(params_base.T, 100.0)

    # Solve with transfers returned (to isolate substitution/distortion effect from wealth effect)
    res_base = solve_distortionary_cvxpy(params_base, W, return_transfers=True)
    res_tauw = solve_distortionary_cvxpy(params_high_tauw, W, return_transfers=True)
    res_tauc = solve_distortionary_cvxpy(params_high_tauc, W, return_transfers=True)

    # Average labor supply must decrease as taxes increase
    assert np.mean(res_tauw["L"]) < np.mean(res_base["L"])
    assert np.mean(res_tauc["L"]) < np.mean(res_base["L"])


def test_capital_tax_distortion():
    """Test that higher capital return tax (taur) reduces savings and flattens consumption path."""
    params_base = FiscalPolicyParameters(taur=0.0)
    params_high_taur = FiscalPolicyParameters(taur=0.50)
    W = np.full(params_base.T, 100.0)

    res_base = solve_distortionary_cvxpy(params_base, W, return_transfers=False)
    res_taur = solve_distortionary_cvxpy(params_high_taur, W, return_transfers=False)

    # Assets/savings should be lower with high capital tax
    assert np.mean(res_taur["B"]) < np.mean(res_base["B"])

    # Flatter slope check: consumption path growth rate (slope) should be flatter (lower)
    slope_base = res_base["C"][-1] / res_base["C"][0]
    slope_taur = res_taur["C"][-1] / res_taur["C"][0]
    assert slope_taur < slope_base


def test_social_security_substitution():
    """Test that Social Security capitalization acts as a perfect substitute for private savings.

    Consumption should remain identical, while private savings become negative during working life
    as voluntary savings are replaced by the pension fund.
    """
    params_ss = FiscalPolicyParameters(tau_ss=0.36, t_star=26)
    W = np.zeros(params_ss.T)
    # Wage profile: constant at 10.0 during working life
    W[:params_ss.t_star] = 10.0

    # 1. Social Security capitalization system
    res_ss = solve_social_security(params_ss, W)

    # 2. No social security but equivalent net income path (Ricardian equivalence)
    # The pension fund is a perfect substitute, so we simulate a lump-sum income model
    params_no_ss = FiscalPolicyParameters(tauw=0.0)
    # Create the exact same net income path manually
    Y_equivalent = np.zeros(params_ss.T)
    for t in range(params_ss.t_star):
        Y_equivalent[t] = 10.0 * (1.0 - params_ss.tau_ss)
    Y_equivalent[params_ss.t_star] = res_ss["Pension"]

    res_no_ss = solve_non_distortionary(params_no_ss, Y_equivalent)

    # Consumption should be exactly identical
    np.testing.assert_allclose(res_ss["C"], res_no_ss["C"], rtol=1e-6, atol=1e-6)

    # Private savings B in Social Security system must be negative during early periods
    # because the agent borrows (or reduces savings) knowing they have a locked pension fund.
    assert np.any(res_ss["B"] < 0.0)
