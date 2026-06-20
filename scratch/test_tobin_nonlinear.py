import numpy as np
from scipy.optimize import fsolve

# Parameters
alpha = 0.35
delta = 0.06
phi = 10.0
R_init = 0.04
R_final = 0.03
T = 100

def compute_ss(R_val):
    K_ss = ((R_val + delta) / alpha) ** (1.0 / (alpha - 1.0))
    q_ss = 1.0
    return K_ss, q_ss

K_ss_init, q_ss_init = compute_ss(R_init)
K_ss_final, q_ss_final = compute_ss(R_final)

R_path = np.full(T, R_final)
R_path[0] = R_init

# Linearized slope
A11 = (R_final * phi - (alpha - 1.0) * (R_final + delta)) / phi
A12 = - (alpha - 1.0) * (R_final + delta)
A21 = 1.0 / phi
A22 = 0.0
A = np.array([[A11, A12], [A21, A22]])
eigenvals = np.real(np.linalg.eigvals(A))
lambda_1 = np.sort(eigenvals)[0]
theta = phi * lambda_1

def simulate_nonlinear(q0):
    K = np.zeros(T)
    q = np.zeros(T)
    K[0] = K_ss_init
    q[0] = q0
    for t in range(T - 1):
        R_t = R_path[min(t, len(R_path) - 1)]
        # Corrected gross investment
        I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
        K[t + 1] = (1.0 - delta) * K[t] + I_t
        if K[t + 1] <= 1e-8:
            K[t + 1] = 1e-8
            
        mpk = alpha * K[t] ** (alpha - 1.0)
        # q Euler:
        q[t + 1] = (1.0 + R_t) * q[t] - mpk + delta + (q[t] - 1.0) ** 2 / (2.0 * phi)
        if t < 10:
            print(f"t={t}: K={K[t]:.6f}, q={q[t]:.6f}, I={I_t:.6f}, mpk={mpk:.6f}")
    return K, q

def residuals(q0_arr):
    _, q = simulate_nonlinear(q0_arr[0])
    return [q[-1] - 1.0]

q0_guess = [1.0 + theta * (np.log(K_ss_init / K_ss_final))]
# Wait! In level deviations, the guess would be 1.0 + (theta_level) * (K0 - K_ss)
# Since the system is log-linearized, the log-deviation is np.log(K0 / K_ss_final)
# Let's see: q0 = exp(theta * log(K0/K_ss)) = exp(q_hat_0)
q0_guess_level = np.exp(theta * np.log(K_ss_init / K_ss_final))

sol = fsolve(residuals, [q0_guess_level])
q0 = sol[0]
print(f"Sol: {q0:.6f}")

K_nonlin, q_nonlin = simulate_nonlinear(q0)
print(f"Non-linear K[-1]: {K_nonlin[-1]:.6f} (expected: {K_ss_final:.6f})")
print(f"Non-linear q[-1]: {q_nonlin[-1]:.6f} (expected: 1.0)")
