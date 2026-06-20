import numpy as np

R = 0.05
tau_ss = 0.36
T = 30

print("Searching for parameters that give pension fund value ~246.3:")

# Let's search over possible retirement periods t_star (from 15 to 28)
# and wage paths (constant, or linear)
for t_star in range(15, 29):
    # Case A: wage = 10 + t
    W_inc = [10.0 + t for t in range(t_star)]
    D = 0.0
    for t in range(t_star):
        D = D * (1.0 + R) + tau_ss * W_inc[t]
    if abs(D - 246.3) < 5.0:
        print(f"t_star = {t_star}, wage = 10+t: D = {D:.4f}")

    # Case B: wage = 10 + 0.5*t
    W_inc2 = [10.0 + 0.5 * t for t in range(t_star)]
    D = 0.0
    for t in range(t_star):
        D = D * (1.0 + R) + tau_ss * W_inc2[t]
    if abs(D - 246.3) < 5.0:
        print(f"t_star = {t_star}, wage = 10+0.5*t: D = {D:.4f}")

    # Case C: wage = constant (what constant wage W would give 246.3?)
    # D = tau_ss * W * sum((1+R)^(t_star-1-t))
    annuity_factor = sum((1.0 + R) ** (t_star - 1 - t) for t in range(t_star))
    W_const = 246.3 / (tau_ss * annuity_factor)
    print(f"t_star = {t_star}, constant wage needed for 246.3: {W_const:.4f}")
