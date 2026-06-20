import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.append("src")

from macroaicomp.models.islm import (
    default_calibration,
    steady_state,
    simulate_shock,
    system_dynamics,
)


def test_plot():
    params_sim = default_calibration()
    ss_init = steady_state(params_sim)
    initial_state = np.array([ss_init["Y"], ss_init["P"]])

    # Shock monetario
    params_sim.m0 = 110.0
    params_sim.beta0 = 2100.0

    t_span = (0, 30)
    t_eval = np.linspace(0, 30, 300)
    res = simulate_shock(params_sim, initial_state, t_span, t_eval)

    Y_path = res.y[0]
    P_path = res.y[1]
    ss_final = steady_state(params_sim)

    # Crear la figura gráfica de 3 paneles
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    # --- PANEL 1: DINÁMICA DE LA RENTA (Y) ---
    axs[0].plot(res.t, Y_path, color="#004C97", linewidth=2.5, label="Producción (Y)")
    axs[0].axhline(
        params_sim.ypot0,
        color="red",
        linestyle="--",
        alpha=0.7,
        label="Renta Potencial",
    )
    axs[0].set_title(
        "Evolución Temporal del Producto Real (Y)",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    axs[0].set_xlabel("Tiempo (t)", fontsize=10)
    axs[0].set_ylabel("Producción (Y)", fontsize=10)
    axs[0].grid(True, linestyle=":", alpha=0.6)
    axs[0].legend(loc="lower right")

    # --- PANEL 2: DINÁMICA DE LOS PRECIOS (P) ---
    axs[1].plot(
        res.t, P_path, color="#8EAD3A", linewidth=2.5, label="Nivel de Precios (P)"
    )
    axs[1].axhline(
        ss_init["P"], color="gray", linestyle=":", alpha=0.5, label="Precio Inicial"
    )
    axs[1].axhline(
        ss_final["P"],
        color="black",
        linestyle="--",
        alpha=0.7,
        label="Nuevo E.E. Largo Plazo",
    )
    axs[1].set_title(
        "Evolución Temporal del Nivel de Precios (P)",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    axs[1].set_xlabel("Tiempo (t)", fontsize=10)
    axs[1].set_ylabel("Nivel de Precios (P)", fontsize=10)
    axs[1].grid(True, linestyle=":", alpha=0.6)
    axs[1].legend(loc="lower right")

    # --- PANEL 3: DIAGRAMA DE FASES EN EL PLANO (Y, P) ---
    # 1. Dibujar la trayectoria dinámica
    axs[2].plot(
        Y_path, P_path, color="#7A3E9F", linewidth=3, label="Trayectoria dinámica"
    )

    # 2. Dibujar locus dP/dt = 0 (Pleno empleo: Y = Y_pot0)
    axs[2].axvline(
        params_sim.ypot0,
        color="#D95319",
        linestyle="--",
        linewidth=2,
        label=r"$\dot{P} = 0$ (Pleno Empleo)",
    )

    # 3. Dibujar locus dY/dt = 0 (Curva IS en equilibrio)
    Y_vals = np.linspace(min(Y_path) - 15, max(Y_path) + 15, 100)
    slope = (
        params_sim.theta * params_sim.mi
        - params_sim.theta / params_sim.beta1
        - params_sim.psi
    )
    intercept_init = ss_init["P"] - slope * params_sim.ypot0
    intercept_final = ss_final["P"] - slope * params_sim.ypot0

    P_locus_init = intercept_init + slope * Y_vals
    P_locus_final = intercept_final + slope * Y_vals

    axs[2].plot(
        Y_vals,
        P_locus_init,
        color="#0072BD",
        linestyle=":",
        alpha=0.5,
        label=r"$\dot{Y} = 0$ (Inicial)",
    )
    axs[2].plot(
        Y_vals,
        P_locus_final,
        color="#0072BD",
        linestyle="--",
        linewidth=2,
        label=r"$\dot{Y} = 0$ (Final)",
    )

    # 4. Dibujar el campo de vectores en el fondo (quiver)
    Y_grid, P_grid = np.meshgrid(
        np.linspace(min(Y_path) - 8, max(Y_path) + 8, 12),
        np.linspace(min(P_path) - 0.8, max(P_path) + 0.8, 12),
    )
    dY_grid = np.zeros_like(Y_grid)
    dP_grid = np.zeros_like(P_grid)
    for r in range(Y_grid.shape[0]):
        for c in range(Y_grid.shape[1]):
            derivs = system_dynamics(
                0.0, np.array([Y_grid[r, c], P_grid[r, c]]), params_sim
            )
            dY_grid[r, c] = derivs[0]
            dP_grid[r, c] = derivs[1]

    norm = np.hypot(dY_grid, dP_grid)
    norm[norm == 0] = 1.0
    dY_grid /= norm
    dP_grid /= norm

    axs[2].quiver(
        Y_grid,
        P_grid,
        dY_grid,
        dP_grid,
        color="lightgray",
        alpha=0.6,
        scale=25,
        width=0.003,
    )

    # 5. Dibujar puntos singulares
    axs[2].scatter(
        ss_init["Y"], ss_init["P"], color="gray", s=100, zorder=5, label="E.E. Inicial"
    )
    axs[2].scatter(
        ss_final["Y"],
        ss_final["P"],
        color="black",
        marker="*",
        s=200,
        zorder=5,
        label="E.E. Final",
    )

    # Flecha de dirección
    half_idx = len(Y_path) // 2
    axs[2].annotate(
        "",
        xy=(Y_path[half_idx], P_path[half_idx]),
        xytext=(Y_path[half_idx - 1], P_path[half_idx - 1]),
        arrowprops=dict(arrowstyle="->", color="#7A3E9F", lw=3, mutation_scale=15),
    )

    axs[2].set_title(
        "Diagrama de Fases en el Plano (Y, P)", fontsize=12, fontweight="bold", pad=10
    )
    axs[2].set_xlabel("Producción (Y)", fontsize=10)
    axs[2].set_ylabel("Nivel de Precios (P)", fontsize=10)
    axs[2].set_xlim(min(Y_path) - 10, max(Y_path) + 10)
    axs[2].set_ylim(min(P_path) - 1, max(P_path) + 1)
    axs[2].grid(True, linestyle=":", alpha=0.6)
    axs[2].legend(loc="best")

    plt.tight_layout()
    os.makedirs(
        "C:/Users/AntonioRC/.gemini/antigravity-ide/brain/0fdfe251-07a4-4597-9b29-043dac53e81a",
        exist_ok=True,
    )
    plt.savefig(
        "C:/Users/AntonioRC/.gemini/antigravity-ide/brain/0fdfe251-07a4-4597-9b29-043dac53e81a/test_phase_diagram.png",
        dpi=150,
        bbox_inches="tight",
    )
    print("Gráfica generada con éxito.")


if __name__ == "__main__":
    test_plot()
