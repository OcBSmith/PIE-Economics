import numpy as np

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

# Definitions from Appendix N
Omega = 1.0 - beta + beta * delta
Phi = 1.0 - beta + (1.0 - alpha) * beta * delta

A = np.array([[1.0, 0.0], [Omega, -alpha * beta * delta]])
B = np.array([[0.0, alpha], [Phi, 0.0]])
C = np.array([[1.0], [0.0]])
D = np.array([[1.0, Omega], [0.0, 1.0]])
F = np.array([[-Omega, 0.0], [0.0, 0.0]])
G = np.array([[1.0, 0.0], [0.0, 1.0 - delta]])
H = np.array([[0.0, 0.0], [0.0, delta]])

# compute J and M matrices
invA = np.linalg.inv(A)
inv_term = np.linalg.inv(D + F @ invA @ B)
J = inv_term @ (G + H @ invA @ B)
M = inv_term @ (H @ invA @ C - F @ invA @ C * rho)

# Eigenvalue decomposition of J
# E_t [c_hat_{t+1}, k_hat_{t+1}]^T = J [c_hat_t, k_hat_t]^T + M a_hat_t
# Note: variables in vector are [c_hat, k_hat]
eigenvals, P = np.linalg.eig(J)
eigenvals = np.real(eigenvals)
P = np.real(P)

sorted_idx = np.argsort(np.abs(eigenvals))
mu_s = eigenvals[sorted_idx[0]]  # stable
mu_u = eigenvals[sorted_idx[1]]  # unstable

# Sort eigenvectors accordingly
P_sorted = np.zeros_like(P)
P_sorted[:, 0] = P[:, sorted_idx[0]]
P_sorted[:, 1] = P[:, sorted_idx[1]]
Q = np.linalg.inv(P_sorted)

# Q * [c_hat, k_hat]^T
# unstable component is row 1 (index 1) of Q:
# Q21 * c_hat + Q22 * k_hat = y2
# E_t y2_{t+1} = mu_u * y2_t + (Q @ M)_2 * a_hat_t
# y2_t = N2 * a_hat_t  where N2 = - (Q @ M)_2 / (mu_u - rho)
QM = Q @ M
N2 = -QM[1, 0] / (mu_u - rho)

# Policy function coefficients:
# Q21 * c_hat + Q22 * k_hat = N2 * a_hat
# => c_hat = eta_ck * k_hat + eta_ca * a_hat
eta_ck = -Q[1, 1] / Q[1, 0]
eta_ca = N2 / Q[1, 0]

# Transition function coefficients:
# k_hat_{t+1} = J21 * c_hat_t + J22 * k_hat_t + M2 * a_hat_t
# => k_hat_{t+1} = (J21 * eta_ck + J22) * k_hat_t + (J21 * eta_ca + M2) * a_hat_t
# = eta_kk * k_hat_t + eta_ka * a_hat_t
eta_kk = J[1, 0] * eta_ck + J[1, 1]
eta_ka = J[1, 0] * eta_ca + M[1, 0]

print("MATRICES:")
print(f"J:\n{J}")
print(f"M:\n{M}")
print(f"Eigenvalues: {eigenvals}")
print(f"Stable eigenvalue mu_s: {mu_s:.6f}")
print(f"Unstable eigenvalue mu_u: {mu_u:.6f}")
print("\nCOEFFICIENTS:")
print(f"eta_ck: {eta_ck:.6f}")
print(f"eta_ca: {eta_ca:.6f}")
print(f"eta_kk: {eta_kk:.6f} (should equal mu_s: {mu_s:.6f})")
print(f"eta_ka: {eta_ka:.6f}")

# Simulation check
T = 100
a_hat = np.zeros(T)
a_hat[0] = 0.0
a_hat[1] = 0.01
for t in range(2, T):
    a_hat[t] = rho * a_hat[t - 1]

k_hat = np.zeros(T)
c_hat = np.zeros(T)

for t in range(T - 1):
    c_hat[t] = eta_ck * k_hat[t] + eta_ca * a_hat[t]
    k_hat[t + 1] = eta_kk * k_hat[t] + eta_ka * a_hat[t]

c_hat[-1] = eta_ck * k_hat[-1] + eta_ca * a_hat[-1]

# Convert to levels
K = K_ss * (1.0 + k_hat)
C = C_ss * (1.0 + c_hat)
Y = np.zeros(T)
I = np.zeros(T)
A_path = np.exp(a_hat)

for t in range(T):
    Y[t] = A_path[t] * K[t] ** alpha
    I[t] = Y[t] - C[t]

print(f"\nSIMULATION (t=1):")
print(f"C[1]: {C[1]:.6f} (ss C: {C_ss:.6f})")
print(f"Y[1]: {Y[1]:.6f} (ss Y: {Y_ss:.6f})")
print(f"I[1]: {I[1]:.6f} (ss I: {I_ss:.6f})")
print(f"K[2]: {K[2]:.6f} (ss K: {K_ss:.6f})")

peak_idx = np.argmax(K)
print(f"Capital peak index: {peak_idx} (should be between 2 and 12)")
print(f"Capital value at peak: {K[peak_idx]:.6f}")
print(f"Capital value at end: {K[-1]:.6f} (should be close to {K_ss:.6f})")
