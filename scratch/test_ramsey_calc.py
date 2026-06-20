import numpy as np


def compute_ramsey_transition_matrix_proposed(
    alpha=0.35, beta=0.97, delta=0.06, n=0.02, A=1.0
):
    Omega = 1.0 - beta + beta * delta
    Gamma = Omega - alpha * beta * (delta + n)

    J11 = -(alpha - 1) * Omega * Gamma / (alpha * beta * (1.0 + n))
    J12 = (alpha - 1) * Omega / (beta * (1.0 + n))
    J21 = -Gamma / (alpha * beta * (1.0 + n))
    J22 = (1.0 - beta * (1.0 + n)) / (beta * (1.0 + n))

    # Notebook order: J has variables c_hat, k_hat
    J = np.array([[J11, J12], [J21, J22]])

    eigenvals = np.linalg.eigvals(J)
    eigenvals = np.real(eigenvals)

    # Sort eigenvalues
    sorted_idx = np.argsort(eigenvals)
    lambda_1 = eigenvals[sorted_idx[0]]  # stable (negative)
    lambda_2 = eigenvals[sorted_idx[1]]  # unstable (positive)

    # Log slope formula from notebook:
    theta = (
        alpha
        * (alpha - 1)
        * Omega
        / ((alpha - 1) * Omega * Gamma + alpha * beta * (1.0 + n) * lambda_1)
    )

    return J, lambda_1, lambda_2, theta


# Test for A=1.0 (pre-shock)
J_pre, l1_pre, l2_pre, theta_pre = compute_ramsey_transition_matrix_proposed(A=1.0)
print("PRE-SHOCK A=1.0:")
print(f"J:\n{J_pre}")
print(f"lambda_1 (stable): {l1_pre:.6f}")
print(f"lambda_2 (unstable): {l2_pre:.6f}")
print(f"theta (log slope): {theta_pre:.6f}")

# Test for A=1.05 (post-shock)
J_post, l1_post, l2_post, theta_post = compute_ramsey_transition_matrix_proposed(A=1.05)
print("\nPOST-SHOCK A=1.05:")
print(f"lambda_1 (stable): {l1_post:.6f}")
print(f"lambda_2 (unstable): {l2_post:.6f}")
print(f"theta (log slope): {theta_post:.6f}")
