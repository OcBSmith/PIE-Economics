import pytest
import numpy as np
from macroaicomp.models.islm import default_calibration, steady_state, system_dynamics


def test_steady_state_default_calibration():
    """Test that the steady state matches the Oracle values for default calibration."""
    params = default_calibration()
    ss = steady_state(params)

    # Values from Appendix D (MATLAB) and Oracle
    assert pytest.approx(ss["Y"], 1e-6) == 2000.0
    assert pytest.approx(ss["P"], 1e-6) == 81.0
    assert pytest.approx(ss["i"], 1e-6) == 2.0
    assert pytest.approx(ss["Yd"], 1e-6) == 2000.0
    assert pytest.approx(ss["dP"], 1e-6) == 0.0
    assert pytest.approx(ss["dY"], 1e-6) == 0.0


def test_system_dynamics_at_steady_state():
    """Derivatives should be zero at the steady state."""
    params = default_calibration()
    ss = steady_state(params)
    state = np.array([ss["Y"], ss["P"]])

    derivatives = system_dynamics(0.0, state, params)

    assert pytest.approx(derivatives[0], 1e-6) == 0.0  # dY/dt
    assert pytest.approx(derivatives[1], 1e-6) == 0.0  # dP/dt


def test_shock_monetary():
    """Test that after a monetary shock, the new steady state is correct."""
    params = default_calibration()
    # Shock: money supply increases from 100 to 101
    params.m0 = 101.0

    ss_new = steady_state(params)

    # Output and interest rate shouldn't change in the long run (money neutrality)
    assert pytest.approx(ss_new["Y"], 1e-6) == 2000.0
    assert pytest.approx(ss_new["i"], 1e-6) == 2.0

    # Prices should increase by the same amount as money supply (101 - 100 = 1) -> 81 + 1 = 82
    assert pytest.approx(ss_new["P"], 1e-6) == 82.0
