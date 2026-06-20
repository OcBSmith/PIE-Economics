import numpy as np
import cvxpy as cp
from macroaicomp.models.fiscal_policy import (
    FiscalPolicyParameters,
    solve_distortionary_foc,
)

params = FiscalPolicyParameters()
W = np.full(params.T, 100.0)

T = params.T
beta = params.beta
gamma = params.gamma
R = params.R
tauw = params.tauw
taur = params.taur
tauc = params.tauc

# Surrogate parameters
ratio = ((1.0 - gamma) / gamma) * ((1.0 + tauc) / (1.0 - tauw))
gamma_eff = 1.0 / (1.0 + ratio)
beta_eff = beta * (1.0 + (1.0 - taur) * R) / (1.0 + R)

# Solve surrogate problem in CVXPY
C = cp.Variable(T)
L = cp.Variable(T)
B = cp.Variable(T)

objective = cp.Maximize(
    cp.sum(
        [
            (beta_eff**t)
            * (gamma_eff * cp.log(C[t]) + (1.0 - gamma_eff) * cp.log(1.0 - L[t]))
            for t in range(T)
        ]
    )
)

constraints = [C >= 1e-6, L >= 0.0, L <= 1.0 - 1e-6, B[0] == W[0] * L[0] - C[0]]
for t in range(1, T):
    constraints.append(B[t] == (1.0 + R) * B[t - 1] + W[t] * L[t] - C[t])
constraints.append(B[T - 1] == 0.0)

prob = cp.Problem(objective, constraints)
prob.solve(solver=cp.CLARABEL, tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11)

C_opt = C.value
L_opt = L.value
B_opt = B.value

res_foc = solve_distortionary_foc(params, W, return_transfers=True)

print("Comparing FOC vs CVXPY (Surrogate):")
print(f"Max diff C: {np.max(np.abs(res_foc['C'] - C_opt)):.2e}")
print(f"Max diff L: {np.max(np.abs(res_foc['L'] - L_opt)):.2e}")
print(f"Max diff B: {np.max(np.abs(res_foc['B'] - B_opt)):.2e}")
