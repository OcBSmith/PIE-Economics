import numpy as np
from scipy.optimize import fsolve


# Define parameters and steady state
class RamseyParameters:
    alpha: float = 0.35
    beta: float = 0.97
    delta: float = 0.06
    n: float = 0.02
    A: float = 1.0


def compute_ramsey_steady_state(params):
    R_ss = 1.0 / params.beta - 1.0 + params.delta
    k_ss = (params.alpha * params.A / R_ss) ** (1.0 / (1.0 - params.alpha))
    y_ss = params.A * k_ss**params.alpha
    i_ss = (params.delta + params.n) * k_ss
    c_ss = y_ss - i_ss
    return {"k": k_ss, "y": y_ss, "c": c_ss, "i": i_ss, "R": R_ss}


def compute_ramsey_transition_matrix(params):
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    n = params.n

    Omega = 1.0 - beta + beta * delta
    Gamma = Omega - alpha * beta * (delta + n)

    J11 = -(alpha - 1) * Omega * Gamma / (alpha * beta * (1.0 + n))
    J12 = (alpha - 1) * Omega / (beta * (1.0 + n))
    J21 = -Gamma / (alpha * beta * (1.0 + n))
    J22 = (1.0 - beta * (1.0 + n)) / (beta * (1.0 + n))

    J = np.array([[J11, J12], [J21, J22]])

    eigenvals = np.linalg.eigvals(J)
    eigenvals = np.real(eigenvals)

    sorted_idx = np.argsort(eigenvals)
    lambda_1 = eigenvals[sorted_idx[0]]  # stable
    lambda_2 = eigenvals[sorted_idx[1]]  # unstable

    theta = (
        alpha
        * (alpha - 1)
        * Omega
        / ((alpha - 1) * Omega * Gamma + alpha * beta * (1.0 + n) * lambda_1)
    )

    return J, lambda_1, lambda_2, theta


def solve_ramsey_linearized(
    params, k0, A_final=1.0, n_final=0.02, beta_final=0.97, T=100, t_shock=0
):
    params_post = RamseyParameters()
    params_post.alpha = params.alpha
    params_post.beta = beta_final
    params_post.delta = params.delta
    params_post.n = n_final
    params_post.A = A_final

    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_new = ss_post["k"]
    c_ss_new = ss_post["c"]

    _, r_stable, _, theta = compute_ramsey_transition_matrix(params_post)
    mu_s = 1.0 + r_stable

    k = np.zeros(T)
    c = np.zeros(T)
    y = np.zeros(T)
    i = np.zeros(T)
    k_hat = np.zeros(T)
    c_hat = np.zeros(T)

    ss_pre = compute_ramsey_steady_state(params)
    k_ss_pre = ss_pre["k"]
    c_ss_pre = ss_pre["c"]
    y_ss_pre = ss_pre["y"]
    i_ss_pre = ss_pre["i"]

    for t in range(t_shock):
        k[t] = k_ss_pre
        c[t] = c_ss_pre
        y[t] = y_ss_pre
        i[t] = i_ss_pre
        k_hat[t] = 0.0
        c_hat[t] = 0.0

    # At shock
    k[t_shock] = k0
    k_hat[t_shock] = np.log(k0 / k_ss_new)
    c_hat[t_shock] = theta * k_hat[t_shock]
    c[t_shock] = c_ss_new * np.exp(c_hat[t_shock])
    y[t_shock] = A_final * k[t_shock] ** params.alpha
    i[t_shock] = y[t_shock] - c[t_shock]

    for t in range(t_shock + 1, T):
        k_hat[t] = mu_s * k_hat[t - 1]
        c_hat[t] = theta * k_hat[t]
        k[t] = k_ss_new * np.exp(k_hat[t])
        c[t] = c_ss_new * np.exp(c_hat[t])
        y[t] = A_final * k[t] ** params.alpha
        i[t] = y[t] - c[t]

    return {"k": k, "c": c, "y": y, "i": i, "k_hat": k_hat, "c_hat": c_hat}


def solve_ramsey_nonlinear(params, k0, A_path, n_path, T=100, t_shock=0):
    alpha = params.alpha
    beta = params.beta
    delta = params.delta

    params_post = RamseyParameters()
    params_post.alpha = alpha
    params_post.beta = beta
    params_post.delta = delta
    params_post.n = n_path[-1]
    params_post.A = A_path[-1]

    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_final = ss_post["k"]

    ss_pre = compute_ramsey_steady_state(params)
    k_pre = ss_pre["k"]
    c_pre = ss_pre["c"]

    def _simulate_from_shock(c_shock):
        k_sim = np.zeros(T - t_shock)
        c_sim = np.zeros(T - t_shock)
        k_sim[0] = k0
        c_sim[0] = c_shock
        for t in range(T - t_shock - 1):
            idx = t + t_shock
            A_t = A_path[min(idx, len(A_path) - 1)]
            n_t = n_path[min(idx, len(n_path) - 1)]
            A_t1 = A_path[min(idx + 1, len(A_path) - 1)]
            n_t1 = n_path[min(idx + 1, len(n_path) - 1)]

            y_t = A_t * k_sim[t] ** alpha
            k_sim[t + 1] = (1.0 - delta - n_t) * k_sim[t] + y_t - c_sim[t]
            if k_sim[t + 1] <= 0:
                k_sim[t + 1] = 1e-8
            mpk_t1 = alpha * A_t1 * k_sim[t + 1] ** (alpha - 1.0)
            c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
        return k_sim, c_sim

    def _residuals(c_shock_arr):
        k_sim, _ = _simulate_from_shock(c_shock_arr[0])
        return [k_sim[-1] - k_ss_final]

    c0_guess = [ss_post["c"]]
    sol = fsolve(_residuals, c0_guess)
    c_shock = sol[0]

    k_full = np.zeros(T)
    c_full = np.zeros(T)

    for t in range(t_shock):
        k_full[t] = k_pre
        c_full[t] = c_pre

    k_sim, c_sim = _simulate_from_shock(c_shock)
    n_post = T - t_shock
    k_full[t_shock:] = k_sim[:n_post]
    c_full[t_shock:] = c_sim[:n_post]

    return {"k": k_full, "c": c_full}


# Run simulation and comparison
params = RamseyParameters()
ss_init = compute_ramsey_steady_state(params)
T = 100
t_shock = 5

res_lin = solve_ramsey_linearized(
    params, ss_init["k"], A_final=1.05, T=T, t_shock=t_shock
)

A_path = np.full(T, 1.0)
A_path[t_shock:] = 1.05
n_path = np.full(T, 0.02)
res_nonlin = solve_ramsey_nonlinear(
    params, ss_init["k"], A_path, n_path, T=T, t_shock=t_shock
)

print(
    f"res_lin k_hat ratio: {res_lin['c_hat'][t_shock] / res_lin['k_hat'][t_shock]:.6f} (expected: 0.575075)"
)
print(f"k allclose: {np.allclose(res_lin['k'], res_nonlin['k'], atol=5e-2, rtol=1e-2)}")
print(f"c allclose: {np.allclose(res_lin['c'], res_nonlin['c'], atol=5e-2, rtol=1e-2)}")
