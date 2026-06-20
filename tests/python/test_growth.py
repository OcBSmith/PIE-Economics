import numpy as np
import pytest
from macroaicomp.models.growth import (
    SolowSwanParameters,
    compute_solow_steady_state,
    simulate_solow_swan
)

def test_solow_steady_state_calibration():
    """Verify that steady state calculations match the values in the book Table 9.3."""
    params = SolowSwanParameters()
    ss = compute_solow_steady_state(params)

    # Book values: k = 4.095, y = 1.638, c = 1.310, i = 0.328
    assert ss["k"] == pytest.approx(4.0946, abs=1e-4)
    assert ss["y"] == pytest.approx(1.6378, abs=1e-4)
    assert ss["c"] == pytest.approx(1.3103, abs=1e-4)
    assert ss["i"] == pytest.approx(0.3276, abs=1e-4)


def test_savings_shock_dynamics():
    """Verify transition dynamics after a permanent savings shock (s: 20% -> 25%)."""
    params = SolowSwanParameters()
    ss_init = compute_solow_steady_state(params)

    T = 150
    # Simulate a permanent increase in savings rate from period t=1 onwards
    s_path = np.full(T, 0.25)
    n_path = np.full(T, params.n)
    A_path = np.full(T, 1.00)

    # Initial capital starts at the initial steady state (s = 0.20)
    res = simulate_solow_swan(params, ss_init["k"], s_path, n_path, A_path, T=T)

    # 1. Capital should start at initial steady state and grow monotonically
    assert res["k"][0] == pytest.approx(ss_init["k"])
    for t in range(T - 1):
        assert res["k"][t + 1] > res["k"][t]

    # 2. Output should start at initial steady state and grow monotonically
    assert res["y"][0] == pytest.approx(ss_init["y"])
    for t in range(T - 1):
        assert res["y"][t + 1] > res["y"][t]

    # 3. Consumption must jump down immediately on impact due to higher savings rate:
    # c_0_after_shock = (1 - 0.25) * y_0 < (1 - 0.20) * y_0
    assert res["c"][0] < ss_init["c"]
    assert res["c"][0] == pytest.approx(0.75 * ss_init["y"])

    # 4. Eventually, capital accumulation leads to higher output and consumption
    ss_final = compute_solow_steady_state(params, s=0.25)
    assert res["k"][-1] == pytest.approx(ss_final["k"], abs=1e-2)
    assert res["y"][-1] == pytest.approx(ss_final["y"], abs=1e-2)
    assert res["c"][-1] == pytest.approx(ss_final["c"], abs=1e-2)
    assert res["c"][-1] > ss_init["c"]

    # 5. Output growth rate gy should jump up and then converge back to 0
    assert res["gy"][0] == 0.0
    assert res["gy"][1] > 0.0
    for t in range(2, T - 1):
        assert res["gy"][t] > 0.0
        assert res["gy"][t] < res["gy"][t - 1]  # growth slows down as it approaches steady state
    assert res["gy"][-1] == pytest.approx(0.0, abs=1e-2)


def test_golden_rule_calculation():
    """Verify that steady state consumption is maximized when the savings rate equals alpha."""
    params = SolowSwanParameters()
    alpha = params.alpha  # 0.35

    # Golden rule steady state (s = alpha)
    ss_gold = compute_solow_steady_state(params, s=alpha)
    c_gold = ss_gold["c"]

    # Under-accumulated capital steady state (s < alpha)
    ss_low = compute_solow_steady_state(params, s=0.20)
    assert ss_low["c"] < c_gold

    # Over-accumulated capital steady state (s > alpha - dynamic inefficiency)
    ss_high = compute_solow_steady_state(params, s=0.50)
    assert ss_high["c"] < c_gold

    # Check local neighborhood around alpha
    ss_left = compute_solow_steady_state(params, s=alpha - 0.01)
    ss_right = compute_solow_steady_state(params, s=alpha + 0.01)

    assert c_gold > ss_left["c"]
    assert c_gold > ss_right["c"]
