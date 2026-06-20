import numpy as np

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


def simulate(q0):
    K = np.zeros(T)
    q = np.zeros(T)
    K[0] = K_ss_init
    q[0] = q0
    for t in range(T - 1):
        R_t = R_path[min(t, len(R_path) - 1)]
        I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
        K[t + 1] = (1.0 - delta) * K[t] + I_t
        if K[t + 1] <= 1e-8:
            K[t + 1] = 1e-8
        mpk = alpha * K[t] ** (alpha - 1.0)
        q[t + 1] = (1.0 + R_t) * q[t] - mpk + delta + (q[t] - 1.0) ** 2 / (2.0 * phi)
    return K, q


low = 1.05
high = 1.15
for i in range(50):
    mid = (low + high) / 2.0
    K, q = simulate(mid)
    final_q = q[-1]

    # If final_q is too large (explodes to inf), q0 is too high
    # If final_q is too small (goes to -inf), q0 is too low
    # Since we have nan or inf, let's look at where it ends up
    if np.isnan(final_q) or np.isinf(final_q) or final_q > 1.0:
        # Wait, let's see which way it explodes.
        # Let's check the last non-nan/non-inf value or trace it
        # Actually, let's just inspect the path.
        # If q goes above 1.0 and grows, it is too high.
        # Let's check if q is increasing at the end of valid values
        # Or simply, if q[-1] > 1.0 or q has overflowed to positive inf:
        # (Since (q-1)^2/2phi is positive, it tends to blow up to +inf if too high)
        # Let's check:
        has_inf_or_nan = np.isnan(final_q) or np.isinf(final_q)
        if has_inf_or_nan:
            # Check where it overflowed. If it overflowed to +inf, it's too high.
            # If it became negative, it's too low.
            # Let's check the sign of the first overflow or large value:
            huge_idx = np.where(np.abs(q) > 1e4)[0]
            if len(huge_idx) > 0 and q[huge_idx[0]] > 0:
                high = mid
            else:
                low = mid
        else:
            if final_q > 1.0:
                high = mid
            else:
                low = mid

    if i % 5 == 0:
        print(f"Iter {i}: mid = {mid:.12f}, final_q = {final_q:.6f}")

print(f"Final q0: {mid:.12f}")
K, q = simulate(mid)
print(f"Final K (last 5): {K[-5:]}")
print(f"Final q (last 5): {q[-5:]}")
