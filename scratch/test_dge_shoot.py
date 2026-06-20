import numpy as np
from scipy.optimize import fsolve

alpha = 0.35
beta = 0.96
delta = 0.06
rho = 0.80

# Steady State
R_ss = 1.0 / beta - 1.0 + delta
K_ss = (alpha * 1.0 / R_ss) ** (1.0 / (1.0 - alpha))
Y_ss = K_ss**alpha
I_ss = delta * K_ss
C_ss = Y_ss - I_ss

# Blanchard-Khan Policy Functions
Omega = 1.0 - beta + beta * delta
Phi = 1.0 - beta + (1.0 - alpha) * beta * delta

A = np.array([[1.0, 0.0], [Omega, -alpha * beta * delta]])
B = np.array([[0.0, alpha], [Phi, 0.0]])
C = np.array([[1.0], [0.0]])
D = np.array([[1.0, Omega], [0.0, 1.0]])
F = np.array([[-Omega, 0.0], [0.0, 0.0]])
G = np.array([[1.0, 0.0], [0.0, 1.0 - delta]])
H = np.array([[0.0, 0.0], [0.0, delta]])

invA = np.linalg.inv(A)
inv_term = np.linalg.inv(D + F @ invA @ B)
J = inv_term @ (G + H @ invA @ B)
M = inv_term @ (H @ invA @ C - F @ invA @ C * rho)

eigenvals, P = np.linalg.eig(J)
eigenvals = np.real(eigenvals)
sorted_idx = np.argsort(np.abs(eigenvals))
mu_s = eigenvals[sorted_idx[0]]
mu_u = eigenvals[sorted_idx[1]]

P_sorted = np.zeros_like(P)
P_sorted[:, 0] = P[:, sorted_idx[0]]
P_sorted[:, 1] = P[:, sorted_idx[1]]
Q = np.linalg.inv(P_sorted)

QM = Q @ M
N2 = - QM[1, 0] / (mu_u - rho)

eta_ck = - Q[1, 1] / Q[1, 0]
eta_ca = N2 / Q[1, 0]
eta_kk = J[1, 0] * eta_ck + J[1, 1]
eta_ka = J[1, 0] * eta_ca + M[1, 0]

def solve_blanchard_khan(K0, A_path, T=100):
    k_hat = np.zeros(T)
    c_hat = np.zeros(T)
    a_hat = np.log(A_path)

    k_hat[0] = (K0 - K_ss) / K_ss

    for t in range(T - 1):
        c_hat[t] = eta_ck * k_hat[t] + eta_ca * a_hat[t]
        k_hat[t + 1] = eta_kk * k_hat[t] + eta_ka * a_hat[t]
        
    c_hat[-1] = eta_ck * k_hat[-1] + eta_ca * a_hat[-1]

    K = K_ss * (1.0 + k_hat)
    C = C_ss * (1.0 + c_hat)
    Y = np.zeros(T)
    I = np.zeros(T)

    for t in range(T):
        Y[t] = A_path[t] * K[t]**alpha
        I[t] = Y[t] - C[t]

    return {"K": K, "C": C, "Y": Y, "I": I}

def solve_nonlinear_simulation(K0, A_path, T=100):
    res_bk = solve_blanchard_khan(K0, A_path, T=T)
    C0_guess = [res_bk["C"][0]]
    
    def _simulate(C0):
        K = np.zeros(T)
        C = np.zeros(T)
        K[0] = K0
        C[0] = C0
        for t in range(T - 1):
            A_t = A_path[min(t, len(A_path) - 1)]
            Y_t = A_t * K[t] ** alpha
            K[t + 1] = (1.0 - delta) * K[t] + Y_t - C[t]
            if K[t + 1] <= 1e-8:
                K[t + 1] = 1e-8
            A_t1 = A_path[min(t + 1, len(A_path) - 1)]
            R_t1 = alpha * A_t1 * K[t + 1] ** (alpha - 1.0)
            C[t + 1] = beta * (1.0 + R_t1 - delta) * C[t]
        return K, C

    def _residuals(C0_arr):
        K, _ = _simulate(C0_arr[0])
        return [K[-1] - K_ss]

    sol, infodict, ier, mesg = fsolve(_residuals, C0_guess, full_output=True)
    print(f"Nonlinear solver status: ier={ier}, msg={mesg}")
    C0 = sol[0]

    K, C = _simulate(C0)
    Y = np.array([A_path[min(t, len(A_path) - 1)] * K[t] ** alpha for t in range(T)])
    I = Y - C

    return {"K": K, "C": C, "Y": Y, "I": I}

# Test shock simulation
T = 100
a_hat = np.zeros(T)
a_hat[0] = 0.0
a_hat[1] = 0.01
for t in range(2, T):
    a_hat[t] = rho * a_hat[t-1]
A_path = np.exp(a_hat)

res_nonlin = solve_nonlinear_simulation(K_ss, A_path, T=T)
print(f"Non-linear K[-1]: {res_nonlin['K'][-1]:.6f} (expected SS: {K_ss:.6f})")
print(f"Non-linear C[-1]: {res_nonlin['C'][-1]:.6f} (expected SS: {C_ss:.6f})")
