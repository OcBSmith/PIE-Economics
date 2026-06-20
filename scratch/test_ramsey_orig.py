import sys
sys.path.append('c:/Users/AntonioRC/Desktop/PIE/src')
from macroaicomp.models.ramsey import RamseyParameters, compute_ramsey_transition_matrix, compute_ramsey_steady_state

params = RamseyParameters()
J, r_stable, r_unstable, theta = compute_ramsey_transition_matrix(params)
ss = compute_ramsey_steady_state(params)

print("ORIGINAL CODE:")
print(f"J:\n{J}")
print(f"r_stable: {r_stable:.6f}")
print(f"r_unstable: {r_unstable:.6f}")
print(f"theta (returned from original function): {theta:.6f}")
print(f"k_ss: {ss['k']:.6f}, c_ss: {ss['c']:.6f}")
print(f"theta * (c_ss / k_ss): {theta * (ss['c'] / ss['k']):.6f}")
