"""Tests for the Richardson arms race model (practica P0, Chapter 1).

Expected values are taken directly from the worked examples in the book
(Sections 1.4, 1.5, 1.6) and from the MATLAB code in Appendix B, which
act as the numerical oracle for this practice.
"""

import numpy as np
import pytest

from macroaicomp.models.arms_race import (
    ArmsRaceParams,
    eigenvalues,
    is_saddle_path,
    simulate,
    simulate_saddle_path,
    steady_state,
)

GLOBAL_STABILITY_PARAMS = ArmsRaceParams(
    alpha=0.50, beta=0.25, gamma=0.25, delta=0.50, theta=1.00, eta=1.00
)
SADDLE_PATH_PARAMS = ArmsRaceParams(
    alpha=0.25, beta=0.50, gamma=0.50, delta=0.25, theta=1.00, eta=1.00
)


def test_steady_state_matches_book_table_1_1():
    result = steady_state(GLOBAL_STABILITY_PARAMS, np.array([1.0, 1.0]))
    assert result == pytest.approx([4.0, 4.0])


def test_eigenvalues_match_book_section_1_3_2():
    result = sorted(eigenvalues(GLOBAL_STABILITY_PARAMS))
    assert result == pytest.approx([-0.75, -0.25])


def test_global_stability_calibration_is_not_a_saddle_path():
    assert is_saddle_path(GLOBAL_STABILITY_PARAMS) is False


def test_sensitivity_analysis_alpha_0_7_matches_book_section_1_6_1():
    params = ArmsRaceParams(
        alpha=0.70, beta=0.25, gamma=0.25, delta=0.50, theta=1.00, eta=1.00
    )
    assert steady_state(params, np.array([1.0, 1.0])) == pytest.approx(
        [2.61, 3.30], abs=1e-2
    )
    assert sorted(eigenvalues(params)) == pytest.approx([-0.87, -0.33], abs=1e-2)
    assert is_saddle_path(params) is False


def test_shock_analysis_new_steady_state_matches_book_section_1_5():
    x1, x2 = simulate(
        GLOBAL_STABILITY_PARAMS,
        z_initial=np.array([1.0, 1.0]),
        z_final=np.array([2.0, 1.0]),
        periods=200,
    )
    assert [x1[-1], x2[-1]] == pytest.approx([6.67, 5.33], abs=1e-2)


def test_shock_analysis_starts_at_initial_steady_state():
    x1, x2 = simulate(
        GLOBAL_STABILITY_PARAMS,
        z_initial=np.array([1.0, 1.0]),
        z_final=np.array([2.0, 1.0]),
        periods=30,
    )
    assert [x1[0], x2[0]] == pytest.approx([4.0, 4.0])


def test_saddle_path_calibration_is_detected():
    assert is_saddle_path(SADDLE_PATH_PARAMS) is True


def test_saddle_path_steady_states_match_book_section_1_6_2():
    initial = steady_state(SADDLE_PATH_PARAMS, np.array([-1.0, -1.0]))
    final = steady_state(SADDLE_PATH_PARAMS, np.array([-0.5, -1.0]))
    assert initial == pytest.approx([4.0, 4.0])
    assert final == pytest.approx([3.33, 2.67], abs=1e-2)


def test_saddle_path_jump_matches_book_section_1_6_2():
    x1, x2 = simulate_saddle_path(
        SADDLE_PATH_PARAMS,
        z_initial=np.array([-1.0, -1.0]),
        z_final=np.array([-0.5, -1.0]),
        periods=200,
        jump_variable=0,
    )
    # The book reports an instantaneous jump of x1 to 2 at the shock period.
    assert x1[1] == pytest.approx(2.0, abs=1e-2)
    # And convergence to the new steady state (3.33, 2.67) in the long run.
    assert [x1[-1], x2[-1]] == pytest.approx([3.33, 2.67], abs=1e-2)


def test_simulate_saddle_path_raises_for_non_saddle_calibration():
    with pytest.raises(ValueError):
        simulate_saddle_path(
            GLOBAL_STABILITY_PARAMS,
            z_initial=np.array([1.0, 1.0]),
            z_final=np.array([2.0, 1.0]),
        )
