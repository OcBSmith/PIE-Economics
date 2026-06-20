import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.append("src")

from macroaicomp.models.islm import default_calibration, steady_state, simulate_shock


def generate_shock_image():
    params = default_calibration()
    # Variables iniciales pre-shock (Estado estacionario inicial)
    ss_init = steady_state(params)
    y0, p0 = ss_init["Y"], ss_init["P"]

    # Aplicar el shock monetario (de 100 a 105 para que sea más visible)
    params.m0 = 105.0

    # Simular trayectoria
    t_span = (0, 30)
    t_eval = np.linspace(0, 30, 300)
    res = simulate_shock(params, np.array([y0, p0]), t_span, t_eval)

    # Calcular resto de variables en la trayectoria
    Y_path = res.y[0]
    P_path = res.y[1]

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))

    axs[0].plot(res.t, Y_path, color="#004C97", linewidth=2)
    axs[0].axhline(params.ypot0, color="gray", linestyle="--")
    axs[0].set_title("Renta (Y)")
    axs[0].set_xlabel("Tiempo")
    axs[0].grid(True, alpha=0.3)

    axs[1].plot(res.t, P_path, color="#8EAD3A", linewidth=2)
    axs[1].set_title("Precios (P)")
    axs[1].set_xlabel("Tiempo")
    axs[1].grid(True, alpha=0.3)

    fig.suptitle("Respuesta ante Shock Monetario (M0 = 105)", fontsize=14, y=1.05)
    plt.tight_layout()

    plt.savefig(
        "C:/Users/AntonioRC/.gemini/antigravity-ide/brain/8d293854-94b0-4b78-ab6c-d9e2ed1c5d26/is_lm_shock.png",
        dpi=300,
        bbox_inches="tight",
    )


if __name__ == "__main__":
    generate_shock_image()
