import numpy as np

# Parameters
alpha = 0.35
delta = 0.06
phi = 10.0
R_init = 0.04
R_final = 0.03
T = 100

# Steady states
def compute_ss(R_val):
    K_ss = ((R_val + delta) / alpha) ** (1.0 / (alpha - 1.0))
    q_ss = 1.0
    return K_ss, q_ss

K_ss_init, q_ss_init = compute_ss(R_init)
K_ss_final, q_ss_final = compute_ss(R_final)

# Linearized system for final R
A11 = (R_final * phi - (alpha - 1.0) * (R_final + delta)) / phi
A12 = - (alpha - 1.0) * (R_final + delta)
A21 = 1.0 / phi
A22 = 0.0
A = np.array([[A11, A12], [A21, A22]])

eigenvals = np.linalg.eigvals(A)
eigenvals = np.real(eigenvals)
sorted_idx = np.argsort(eigenvals)
lambda_1 = eigenvals[sorted_idx[0]]  # stable
lambda_2 = eigenvals[sorted_idx[1]]  # unstable

theta = phi * lambda_1

# Simulation
K0 = K_ss_init
k_hat = np.zeros(T)
q_hat = np.zeros(T)

# Initial shock (log deviation from the new steady state)
k_hat[0] = np.log(K0 / K_ss_final)
q_hat[0] = theta * k_hat[0]

K = np.zeros(T)
q = np.zeros(T)
K[0] = K0
q[0] = q_ss_final * np.exp(q_hat[0])

# Time evolution
for t in range(1, T):
    # k_hat_t = (1 + lambda_1) * k_hat_{t-1}
    k_hat[t] = (1.0 + lambda_1) * k_hat[t - 1]
    q_hat[t] = theta * k_hat[t]
    
    K[t] = K_ss_final * np.exp(k_hat[t])
    q[t] = q_ss_final * np.exp(q_hat[t])

print(f"K_ss_init: {K_ss_init:.6f}")
print(f"K_ss_final: {K_ss_final:.6f}")
print(f"k_hat[0]: {k_hat[0]:.6f}")
print(f"q_hat[0]: {q_hat[0]:.6f}")
print(f"q[0] (levels): {q[0]:.6f}")
print(f"K[-1]: {K[-1]:.6f} (expected SS final: {K_ss_final:.6f})")
print(f"q[-1]: {q[-1]:.6f} (expected: 1.0)")
