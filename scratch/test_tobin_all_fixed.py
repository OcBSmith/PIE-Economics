import numpy as np
from scipy.optimize import fsolve


# Parameters class
class TobinQParameters:
    alpha: float = 0.35
    delta: float = 0.06
    phi: float = 10.0
    R: float = 0.04


def compute_steady_state(params, R=None):
    R_val = R if R is not None else params.R
    delta = params.delta
    alpha = params.alpha
    q_ss = 1.0
    K_ss = ((R_val + delta) / alpha) ** (1.0 / (alpha - 1.0))
    I_ss = delta * K_ss
    Y_ss = K_ss**alpha
    return {"q": q_ss, "K": K_ss, "I": I_ss, "Y": Y_ss}


def compute_linearized_system(params):
    alpha = params.alpha
    delta = params.delta
    phi = params.phi
    R = params.R

    A11 = (R * phi - (alpha - 1.0) * (R + delta)) / phi
    A12 = -(alpha - 1.0) * (R + delta)
    A21 = 1.0 / phi
    A22 = 0.0

    A = np.array([[A11, A12], [A21, A22]])

    eigenvals = np.linalg.eigvals(A)
    eigenvals = np.real(eigenvals)

    sorted_idx = np.argsort(eigenvals)
    lambda_1 = eigenvals[sorted_idx[0]]  # stable
    lambda_2 = eigenvals[sorted_idx[1]]  # unstable

    mu_1 = 1.0 + lambda_1
    mu_2 = 1.0 + lambda_2

    theta = phi * lambda_1
    theta_book = theta

    return {
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "mu_1": mu_1,
        "mu_2": mu_2,
        "theta": theta,
        "theta_book": theta_book,
        "A": A,
    }


def solve_linearized_simulation(params, K0, R_path, T=100):
    params_post = TobinQParameters()
    params_post.alpha = params.alpha
    params_post.delta = params.delta
    params_post.phi = params.phi
    params_post.R = R_path[-1]

    ss_final = compute_steady_state(params_post)
    K_ss = ss_final["K"]

    lin = compute_linearized_system(params_post)
    lambda_1 = lin["lambda_1"]
    theta = lin["theta"]

    K = np.zeros(T)
    q = np.zeros(T)
    k_hat = np.zeros(T)
    q_hat = np.zeros(T)

    k_hat[0] = np.log(K0 / K_ss)
    q_hat[0] = theta * k_hat[0]

    K[0] = K0
    q[0] = np.exp(q_hat[0])

    for t in range(1, T):
        k_hat[t] = (1.0 + lambda_1) * k_hat[t - 1]
        q_hat[t] = theta * k_hat[t]

        K[t] = K_ss * np.exp(k_hat[t])
        q[t] = np.exp(q_hat[t])

    I = params.delta * K + K * (q - 1.0) / params.phi
    Y = K**params.alpha

    return {"K": K, "q": q, "I": I, "Y": Y}


def solve_nonlinear_simulation(params, K0, R_path, T=100):
    alpha = params.alpha
    delta = params.delta
    phi = params.phi

    res_lin = solve_linearized_simulation(params, K0, R_path, T=T)
    K_guess = res_lin["K"]
    q_guess = res_lin["q"]

    def system_equations(vars_flat):
        K = np.zeros(T)
        q = np.zeros(T)
        K[0] = K0
        K[1:] = vars_flat[: T - 1]
        q[:] = vars_flat[T - 1 :]

        eqs = []
        for t in range(T - 1):
            I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
            eqs.append(K[t + 1] - ((1.0 - delta) * K[t] + I_t))

        for t in range(T - 1):
            R_t = R_path[min(t, len(R_path) - 1)]
            mpk = alpha * K[t] ** (alpha - 1.0)
            eqs.append(
                q[t + 1]
                - ((1.0 + R_t) * q[t] - mpk + delta - (q[t] - 1.0) ** 2 / (2.0 * phi))
            )

        eqs.append(q[-1] - 1.0)
        return eqs

    guess_flat = np.concatenate([K_guess[1:], q_guess])
    sol = fsolve(system_equations, guess_flat)

    K = np.zeros(T)
    q = np.zeros(T)
    K[0] = K0
    K[1:] = sol[: T - 1]
    q[:] = sol[T - 1 :]

    I = delta * K + K * (q - 1.0) / phi
    Y = K**alpha

    return {"K": K, "q": q, "I": I, "Y": Y}


# Validate with tests:
params = TobinQParameters()
lin_sys = compute_linearized_system(params)
print(f"lambda_1: {lin_sys['lambda_1']:.6f} (expected -0.060658)")
print(f"lambda_2: {lin_sys['lambda_2']:.6f} (expected 0.107158)")

# Run shock simulation
K0 = compute_steady_state(params, R=0.04)["K"]
R_path = np.full(100, 0.03)
R_path[0] = 0.04

res_lin = solve_linearized_simulation(params, K0, R_path)
res_nonlin = solve_nonlinear_simulation(params, K0, R_path)

print(f"res_lin K[-1]: {res_lin['K'][-1]:.6f} (expected: 8.080233)")
print(f"res_nonlin K[-1]: {res_nonlin['K'][-1]:.6f} (expected: 8.080233)")
print(f"res_lin q[0]: {res_lin['q'][0]:.6f} (expected: 1.1033)")
print(f"res_nonlin q[0]: {res_nonlin['q'][0]:.6f}")

print(f"q[-1] lin: {res_lin['q'][-1]:.6f}, nonlin: {res_nonlin['q'][-1]:.6f}")
print(
    f"Max rel diff K: {np.max(np.abs(res_lin['K'] - res_nonlin['K']) / res_lin['K']):.6f}"
)
print(
    f"Max rel diff q: {np.max(np.abs(res_lin['q'] - res_nonlin['q']) / res_lin['q']):.6f}"
)
print(f"Allclose K? {np.allclose(res_lin['K'], res_nonlin['K'], rtol=1e-2)}")
print(f"Allclose q? {np.allclose(res_lin['q'], res_nonlin['q'], rtol=1e-2)}")
