import numpy as np
from macroaicomp.models.fiscal_policy import (
    FiscalPolicyParameters,
    solve_distortionary_foc,
    solve_distortionary_cvxpy,
)

params = FiscalPolicyParameters()
W = np.full(params.T, 100.0)

res_foc = solve_distortionary_foc(params, W, return_transfers=False)
res_cvxpy = solve_distortionary_cvxpy(params, W, return_transfers=False)

print("PERIOD | FOC C | CVXPY C | FOC L | CVXPY L | FOC B | CVXPY B")
for t in range(5):
    print(
        f"{t:6d} | {res_foc['C'][t]:7.3f} | {res_cvxpy['C'][t]:7.3f} | {res_foc['L'][t]:7.3f} | {res_cvxpy['L'][t]:7.3f} | {res_foc['B'][t]:7.3f} | {res_cvxpy['B'][t]:7.3f}"
    )

print("Last period B:")
print(f"FOC B[T-1]: {res_foc['B'][-1]:.6f}")
print(f"CVXPY B[T-1]: {res_cvxpy['B'][-1]:.6f}")
