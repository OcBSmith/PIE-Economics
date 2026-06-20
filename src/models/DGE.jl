module DGE

using LinearAlgebra
using NLsolve

export DGEParams, default_calibration, compute_steady_state, solve_blanchard_khan, solve_nonlinear_simulation

"""
    DGEParams

Calibration parameters for the basic dynamic general equilibrium model (Cap. 8).
"""
struct DGEParams
    alpha::Float64  # Capital income share
    beta::Float64   # Discount factor
    delta::Float64  # Capital depreciation rate
    rho::Float64    # TFP AR(1) persistence
    A::Float64      # Steady state TFP
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return DGEParams(0.35, 0.96, 0.06, 0.80, 1.0)
end

"""
    compute_steady_state(params)

Computes the steady state of the DGE model.
"""
function compute_steady_state(params::DGEParams)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    A = params.A

    R_ss = 1.0 / beta - 1.0 + delta
    K_ss = (alpha * A / R_ss) ^ (1.0 / (1.0 - alpha))
    Y_ss = A * K_ss^alpha
    I_ss = delta * K_ss
    C_ss = Y_ss - I_ss

    return Dict("K" => K_ss, "Y" => Y_ss, "C" => C_ss, "I" => I_ss, "R" => R_ss)
end

"""
    solve_blanchard_khan(params, K0, A_path, T=100)

Solves the DGE model using the linearized Blanchard-Khan policy functions.
"""
function solve_blanchard_khan(
    params::DGEParams,
    K0::Real,
    A_path::AbstractVector,
    T::Int=100
)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    rho = params.rho

    ss = compute_steady_state(params)
    K_ss = ss["K"]
    C_ss = ss["C"]
    Y_ss = ss["Y"]

    Omega = 1.0 - beta + beta * delta
    Phi = 1.0 - beta + (1.0 - alpha) * beta * delta

    A_mat = [1.0 0.0; Omega -alpha * beta * delta]
    B_mat = [0.0 alpha; Phi 0.0]
    C_mat = [1.0; 0.0]
    D_mat = [1.0 Omega; 0.0 1.0]
    F_mat = [-Omega 0.0; 0.0 0.0]
    G_mat = [1.0 0.0; 0.0 1.0 - delta]
    H_mat = [0.0 0.0; 0.0 delta]

    invA = inv(A_mat)
    inv_term = inv(D_mat + F_mat * invA * B_mat)
    J = inv_term * (G_mat + H_mat * invA * B_mat)
    M = inv_term * (H_mat * invA * C_mat - F_mat * invA * C_mat * rho)

    decomp = eigen(J)
    eigenvals = real(decomp.values)
    P = decomp.vectors

    sorted_idx = sortperm(abs.(eigenvals))
    mu_s = eigenvals[sorted_idx[1]]  # stable
    mu_u = eigenvals[sorted_idx[2]]  # unstable

    P_sorted = zeros(2, 2)
    P_sorted[:, 1] = P[:, sorted_idx[1]]
    P_sorted[:, 2] = P[:, sorted_idx[2]]
    Q = inv(P_sorted)

    QM = Q * M
    N2 = - QM[2, 1] / (mu_u - rho)

    eta_ck = - Q[2, 2] / Q[2, 1]
    eta_ca = N2 / Q[2, 1]
    eta_kk = J[2, 1] * eta_ck + J[2, 2]
    eta_ka = J[2, 1] * eta_ca + M[2, 1]

    k_hat = zeros(T)
    c_hat = zeros(T)
    a_hat = log.(A_path)

    k_hat[1] = (K0 - K_ss) / K_ss

    for t in 1:(T - 1)
        c_hat[t] = eta_ck * k_hat[t] + eta_ca * a_hat[t]
        k_hat[t + 1] = eta_kk * k_hat[t] + eta_ka * a_hat[t]
    end
    c_hat[T] = eta_ck * k_hat[T] + eta_ca * a_hat[T]

    K = K_ss .* (1.0 .+ k_hat)
    C = C_ss .* (1.0 .+ c_hat)
    Y = zeros(T)
    I = zeros(T)

    for t in 1:T
        Y[t] = A_path[t] * K[t]^alpha
        I[t] = Y[t] - C[t]
    end

    return Dict("K" => K, "C" => C, "Y" => Y, "I" => I)
end

"""
    solve_nonlinear_simulation(params, K0, A_path, T=100)

Solves the DGE model non-linearly using a simultaneous path solver.
"""
function solve_nonlinear_simulation(
    params::DGEParams,
    K0::Real,
    A_path::AbstractVector,
    T::Int=100
)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta

    ss = compute_steady_state(params)
    K_ss = ss["K"]

    res_bk = solve_blanchard_khan(params, K0, A_path, T)
    K_guess = res_bk["K"]
    C_guess = res_bk["C"]

    function system_equations!(F, vars_flat)
        K = zeros(T)
        C = zeros(T)
        K[1] = K0
        K[2:T] = vars_flat[1:(T - 1)]
        C[1:T] = vars_flat[T:(2 * T - 1)]

        eqs = Float64[]

        # Capital accumulation: K[t+1] = (1-delta)*K[t] + Y_t - C[t]
        for t in 1:(T - 1)
            A_t = A_path[min(t, length(A_path))]
            Y_t = A_t * K[t]^alpha
            push!(eqs, K[t + 1] - ((1.0 - delta) * K[t] + Y_t - C[t]))
        end

        # Consumption Euler: C[t+1] = beta * (1 + R_{t+1} - delta) * C[t]
        for t in 1:(T - 1)
            A_t1 = A_path[min(t + 1, length(A_path))]
            K_next_bounded = max(K[t + 1], 1e-8)
            R_t1 = alpha * A_t1 * K_next_bounded^(alpha - 1.0)
            push!(eqs, C[t + 1] - (beta * (1.0 + R_t1 - delta) * C[t]))
        end

        # Terminal condition: K[end] = K_ss
        push!(eqs, K[T] - K_ss)

        F .= eqs
    end

    guess_flat = [K_guess[2:T]..., C_guess...]
    sol = nlsolve(system_equations!, guess_flat, xtol=1e-12, ftol=1e-12)

    K = zeros(T)
    C = zeros(T)
    K[1] = K0
    K[2:T] = sol.zero[1:(T - 1)]
    C[1:T] = sol.zero[T:(2 * T - 1)]

    Y = zeros(T)
    I = zeros(T)
    for t in 1:T
        Y[t] = A_path[min(t, length(A_path))] * K[t]^alpha
        I[t] = Y[t] - C[t]
    end

    return Dict("K" => K, "C" => C, "Y" => Y, "I" => I)
end

end # module DGE
