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

K_ss_init, _ = compute_ss(R_init)
K_ss_final, _ = compute_ss(R_final)

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

def system_equations(vars_flat):
    # vars_flat contains K[1:T] (length T-1) and q[0:T] (length T)
    K = np.zeros(T)
    q = np.zeros(T)
    K[0] = K_ss_init
    K[1:] = vars_flat[:T-1]
    q[:] = vars_flat[T-1:]
    
    eqs = []
    
    # 1. Capital accumulation: K[t+1] = (1-delta)*K[t] + delta*K[t] + K[t]*(q[t]-1)/phi = K[t] * (1 + (q[t]-1)/phi)
    for t in range(T - 1):
        I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
        eqs.append(K[t+1] - ((1.0 - delta) * K[t] + I_t))
        
    # 2. Euler equation: q[t+1] = (1+R_t)*q[t] - alpha*K[t]^(alpha-1) + delta + (q[t]-1)^2/(2*phi)
    for t in range(T - 1):
        R_t = R_path[min(t, len(R_path) - 1)]
        # Note: MPK is evaluated at K[t+1] or K[t]? Let's check book/notebook.
        # Notebook has K[t+1] in FOC, let's use K[t+1] or K[t] depending on MPK index.
        # Let's test with K[t] first
        mpk = alpha * K[t] ** (alpha - 1.0)
        eqs.append(q[t+1] - ((1.0 + R_t) * q[t] - mpk + delta + (q[t] - 1.0) ** 2 / (2.0 * phi)))
        
    # 3. Terminal condition: q[-1] = 1.0
    eqs.append(q[-1] - 1.0)
    
    return eqs

# Initial guess from linearized simulation
# We can use the linearized path!
k_hat = np.zeros(T)
q_hat = np.zeros(T)
k_hat[0] = np.log(K_ss_init / K_ss_final)
q_hat[0] = theta * k_hat[0]
for t in range(1, T):
    k_hat[t] = (1.0 + lambda_1) * k_hat[t - 1]
    q_hat[t] = theta * k_hat[t]
    
K_guess = K_ss_final * np.exp(k_hat)
q_guess = 1.0 * np.exp(q_hat)

guess_flat = np.concatenate([K_guess[1:], q_guess])

sol = fsolve(system_equations, guess_flat)

K_sol = np.zeros(T)
q_sol = np.zeros(T)
K_sol[0] = K_ss_init
K_sol[1:] = sol[:T-1]
q_sol[:] = sol[T-1:]

print("PATH SOLVER RESULTS:")
print(f"K_sol[0]: {K_sol[0]:.6f}, q_sol[0]: {q_sol[0]:.6f}")
print(f"K_sol[-1]: {K_sol[-1]:.6f} (expected SS final: {K_ss_final:.6f})")
print(f"q_sol[-1]: {q_sol[-1]:.6f} (expected: 1.0)")
