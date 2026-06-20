import numpy as np

alpha = 0.35
delta = 0.06
phi = 10.0
R = 0.04

A11 = (R * phi - (alpha - 1.0) * (R + delta)) / phi
A12 = - (alpha - 1.0) * (R + delta)
A21 = 1.0 / phi
A22 = 0.0

A = np.array([[A11, A12], [A21, A22]])

eigenvals = np.linalg.eigvals(A)
eigenvals = np.real(eigenvals)
sorted_idx = np.argsort(eigenvals)
lambda_1 = eigenvals[sorted_idx[0]]
lambda_2 = eigenvals[sorted_idx[1]]

print(f"Matrix A:\n{A}")
print(f"lambda_1 (stable): {lambda_1:.6f}")
print(f"lambda_2 (unstable): {lambda_2:.6f}")
print(f"mu_1 = 1 + lambda_1: {1.0 + lambda_1:.6f}")
print(f"mu_2 = 1 + lambda_2: {1.0 + lambda_2:.6f}")
print(f"Saddle path slope theta = lambda_1 * phi: {lambda_1 * phi:.6f}")
