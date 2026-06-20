import numpy as np
import matplotlib.pyplot as plt
from macroaicomp.models.ramsey import RamseyParameters, compute_ramsey_steady_state, solve_ramsey_linearized, solve_ramsey_nonlinear

import sys
sys.path.append('src')

def test_plot():
    params = RamseyParameters()
    ss_init = compute_ramsey_steady_state(params)
    
    T = 80
    t_shock = 5
    
    # 1. Solución linealizada de BK
    res_lin = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_final=1.05,
        n_final=params.n,
        beta_final=params.beta,
        T=T,
        t_shock=t_shock
    )
    
    A_path = np.full(T, 1.00)
    A_path[t_shock:] = 1.05
    n_path = np.full(T, 0.02)
    
    # 2. Solución exacta no lineal de fsolve
    res_nonlin = solve_ramsey_nonlinear(
        params,
        ss_init["k"],
        A_path,
        n_path,
        T=T,
        t_shock=t_shock
    )
    
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    t_axis = np.arange(T)
    
    # Consumo
    axs[0].plot(t_axis, res_lin["c"], color='#7A3E9F', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Lineal)')
    axs[0].plot(t_axis, res_nonlin["c"], color='#7A3E9F', linewidth=2.0, label='Exacto No Lineal')
    axs[0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0].set_title('Consumo per cápita ($c_t$)', fontsize=11, fontweight='bold')
    axs[0].set_xlabel('Períodos')
    axs[0].set_ylabel('c')
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend()
    
    # Capital
    axs[1].plot(t_axis, res_lin["k"], color='#8EAD3A', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Lineal)')
    axs[1].plot(t_axis, res_nonlin["k"], color='#8EAD3A', linewidth=2.0, label='Exacto No Lineal')
    axs[1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1].set_title('Capital per cápita ($k_t$)', fontsize=11, fontweight='bold')
    axs[1].set_xlabel('Períodos')
    axs[1].set_ylabel('k')
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend()
    
    plt.tight_layout()
    plt.savefig('scratch/test_fig2.png')
    print("Success with comparison plot!")

if __name__ == '__main__':
    test_plot()
