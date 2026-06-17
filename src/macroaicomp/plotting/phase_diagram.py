"""Plotting helpers for two-variable linear dynamic systems.

Reference: Bongers, Gómez and Torres (2019), "An Introduction to
Computational Macroeconomics", Chapter 1, Appendix B.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


def plot_irf(
    x1: np.ndarray,
    x2: np.ndarray,
    labels: tuple[str, str] = ("x1", "x2"),
    ylabel: str = "Value",
) -> Figure:
    """Plot the impulse-response (transition dynamics) of two variables.

    Parameters
    ----------
    x1 : np.ndarray
        Time path of the first endogenous variable.
    x2 : np.ndarray
        Time path of the second endogenous variable.
    labels : tuple[str, str]
        Titles for each subplot.
    ylabel : str
        Shared y-axis label (with units).

    Returns
    -------
    matplotlib.figure.Figure
        The created figure, with one subplot per variable.
    """
    periods = np.arange(len(x1))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, x, label in zip(axes, (x1, x2), labels):
        ax.plot(periods, x, color="0.25", linewidth=2.5)
        ax.set_title(f"Variable {label}")
        ax.set_xlabel("Periods")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_phase_diagram(
    a: np.ndarray,
    b: np.ndarray,
    z: np.ndarray,
    steady_state_point: np.ndarray,
    x1_range: tuple[float, float] = (0, 10),
    x2_range: tuple[float, float] = (0, 10),
    grid_size: int = 11,
    labels: tuple[str, str] = ("x1", "x2"),
) -> Figure:
    """Plot the phase diagram of a two-variable linear dynamic system.

    Reproduces the MATLAB `quiver` phase diagram of Appendix B: arrows
    show the direction of adjustment (dx1, dx2) at each point of the
    (x1, x2) plane, given dx = A @ x + B @ z.

    Parameters
    ----------
    a : np.ndarray
        2x2 matrix of coefficients of the endogenous variables.
    b : np.ndarray
        2x2 matrix of coefficients of the exogenous variables.
    z : np.ndarray
        Exogenous variables (z1, z2) at which the diagram is drawn.
    steady_state_point : np.ndarray
        Coordinates (x1_bar, x2_bar) marked on the diagram.
    x1_range : tuple[float, float]
        Plotting range for the first variable.
    x2_range : tuple[float, float]
        Plotting range for the second variable.
    grid_size : int
        Number of grid points per axis.
    labels : tuple[str, str]
        Axis labels.

    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    x1_grid, x2_grid = np.meshgrid(
        np.linspace(*x1_range, grid_size), np.linspace(*x2_range, grid_size)
    )
    dx1 = a[0, 0] * x1_grid + a[0, 1] * x2_grid + b[0] @ z
    dx2 = a[1, 0] * x1_grid + a[1, 1] * x2_grid + b[1] @ z

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.quiver(x1_grid, x2_grid, dx1, dx2, color="0.3")
    ax.plot(*steady_state_point, "o", color="black", markersize=8)
    ax.set_title("Phase Diagram")
    ax.set_xlabel(f"Variable {labels[0]}")
    ax.set_ylabel(f"Variable {labels[1]}")
    ax.grid(True, alpha=0.3)
    return fig
