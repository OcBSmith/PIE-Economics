import numpy as np
from scipy.optimize import fsolve

# Parameters
alpha = 0.35
beta = 0.97
delta = 0.06
n = 0.02
A_init = 1.0
A_final = 1.05
T = 100
t_shock = 5

# Pre-shock Steady State
R_ss_pre = 1.0 / beta - 1.0 + delta
k_ss_pre = (alpha * A_init / R_ss_pre) ** (1.0 / (1.0 - alpha))
y_ss_pre = A_init * k_ss_pre**alpha
c_ss_pre = y_ss_pre - (delta + n) * k_ss_pre

# Post-shock Steady State
R_ss_post = 1.0 / beta - 1.0 + delta
k_ss_post = (alpha * A_final / R_ss_post) ** (1.0 / (1.0 - alpha))
y_ss_post = A_final * k_ss_post**alpha
c_ss_post = y_ss_post - (delta + n) * k_ss_post

k0 = k_ss_pre

def simulate(c_shock):
    k_sim = np.zeros(T - t_shock)
    c_sim = np.zeros(T - t_shock)
    k_sim[0] = k0
    c_sim[0] = c_shock
    for t in range(T - t_shock - 1):
        y_t = A_final * k_sim[t] ** alpha
        # Notebook equation: (1+n)*k_{t+1} = (1-delta)*k_t + y_t - c_t
        k_sim[t + 1] = ((1.0 - delta) * k_sim[t] + y_t - c_sim[t]) / (1.0 + n)
        if k_sim[t + 1] <= 0:
            k_sim[t + 1] = 1e-8
        mpk_t1 = alpha * A_final * k_sim[t + 1] ** (alpha - 1.0)
        c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
    return k_sim, c_sim

def residuals(c_shock_arr):
    k_sim, _ = simulate(c_shock_arr[0])
    return [k_sim[-1] - k_ss_post]

c0_guess = [1.476379]
sol = fsolve(residuals, c0_guess)
print(f"Sol: {sol[0]:.12f}, Converged? {np.abs(simulate(sol[0])[0][-1] - k_ss_post) < 1e-5}")
