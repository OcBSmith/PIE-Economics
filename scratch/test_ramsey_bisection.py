import numpy as np

# Parameters
alpha = 0.35
beta = 0.97
delta = 0.06
n = 0.02
A_init = 1.0
A_final = 1.05
T = 100
t_shock = 5

# Pre-shock Steady State
R_ss_pre = 1.0 / beta - 1.0 + delta
k_ss_pre = (alpha * A_init / R_ss_pre) ** (1.0 / (1.0 - alpha))
y_ss_pre = A_init * k_ss_pre**alpha
c_ss_pre = y_ss_pre - (delta + n) * k_ss_pre

# Post-shock Steady State
R_ss_post = 1.0 / beta - 1.0 + delta
k_ss_post = (alpha * A_final / R_ss_post) ** (1.0 / (1.0 - alpha))
y_ss_post = A_final * k_ss_post**alpha
c_ss_post = y_ss_post - (delta + n) * k_ss_post

k0 = k_ss_pre


def simulate(c_shock):
    k_sim = np.zeros(T - t_shock)
    c_sim = np.zeros(T - t_shock)
    k_sim[0] = k0
    c_sim[0] = c_shock
    for t in range(T - t_shock - 1):
        y_t = A_final * k_sim[t] ** alpha
        # Note: Capital accumulation equation from the book / notebook:
        # (1+n)*k_{t+1} = (1-delta)*k_t + y_t - c_t
        k_sim[t + 1] = ((1.0 - delta) * k_sim[t] + y_t - c_sim[t]) / (1.0 + n)
        if k_sim[t + 1] <= 0:
            k_sim[t + 1] = 1e-8
        mpk_t1 = alpha * A_final * k_sim[t + 1] ** (alpha - 1.0)
        c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
    return k_sim, c_sim


# Let's search c_shock between 1.45 and 1.50
low = 1.45
high = 1.50
for i in range(50):
    mid = (low + high) / 2.0
    k_sim, c_sim = simulate(mid)
    final_k = k_sim[-1]

    # If final_k is too small, it means we consumed too much (c_shock is too high)
    # If final_k is too large, it means we consumed too little (c_shock is too low)
    if final_k < k_ss_post:
        high = mid
    else:
        low = mid

    if i % 5 == 0:
        print(
            f"Iter {i}: mid = {mid:.12f}, final_k = {final_k:.6f}, target = {k_ss_post:.6f}"
        )

print(f"Final c_shock: {mid:.12f}")
k_sim, c_sim = simulate(mid)
print(f"Final capital path (last 5): {k_sim[-5:]}")
