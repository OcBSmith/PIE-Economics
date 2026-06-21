module ConsumptionLeisure

using NLsolve
using Optim

export ConsumptionLeisureParameters, default_calibration, solve_foc_fsolve, solve_direct_optim

function log_barrier(u, epsilon=1e-9)
    if u > epsilon
        return log(u)
    else
        return log(epsilon) - (epsilon - u) / epsilon - 0.5 * ((epsilon - u) / epsilon)^2
    end
end

"""
    ConsumptionLeisureParameters

Calibration parameters for the consumption-leisure model (Cap. 5).
"""
struct ConsumptionLeisureParameters
    T::Int          # Number of periods
    beta::Float64   # Discount factor
    R::Float64      # Real interest rate
    gamma::Float64  # Consumption weight in utility function
    B0::Float64     # Initial assets
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return ConsumptionLeisureParameters(30, 0.97, 0.02, 0.5, 0.0)
end

"""
    solve_foc_fsolve(params, W)

Solves the optimal consumption-leisure problem using first-order conditions and NLsolve.
"""
function solve_foc_fsolve(params::ConsumptionLeisureParameters, W::AbstractVector)
    T = params.T
    beta = params.beta
    R = params.R
    gamma = params.gamma
    B0 = params.B0
    growth = beta * (1.0 + R)

    function build_path(C0)
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        # L_t = 1 - (1-gamma)*C_t / (gamma*W_t), clipped to [0.0, 1.0 - 1e-9]
        L = clamp.(1.0 .- (1.0 - gamma) .* C ./ (gamma .* W), 0.0, 1.0 - 1e-9)
        B = zeros(T)
        B[1] = (1.0 + R) * B0 + W[1] * L[1] - C[1]
        for t in 2:T
            B[t] = (1.0 + R) * B[t - 1] + W[t] * L[t] - C[t]
        end
        return C, L, B
    end

    function residuals!(F, x)
        C0 = x[1]
        _, _, B = build_path(C0)
        F[1] = B[T]
    end

    C0_guess = [(sum(W) / T) * gamma]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C0 = sol.zero[1]

    C, L, B = build_path(C0)
    O = 1.0 .- L
    W_L = W .* L

    return Dict("C" => C, "L" => L, "O" => O, "B" => B, "W_L" => W_L)
end

"""
    solve_direct_optim(params, W)

Solves the optimal consumption-leisure problem using direct optimization with Optim.jl.
"""
function solve_direct_optim(params::ConsumptionLeisureParameters, W::AbstractVector)
    T = params.T
    beta = params.beta
    R = params.R
    gamma = params.gamma
    B0 = params.B0

    # Decision variables: B[1] ... B[T-1]
    function objective(x)
        B = [x..., 0.0]
        C = zeros(T)
        L = zeros(T)

        C[1] = gamma * ((1.0 + R) * B0 + W[1] - B[1])
        L[1] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B0 + W[1] - B[1]) / W[1]
        for t in 2:T
            C[t] = gamma * ((1.0 + R) * B[t - 1] + W[t] - B[t])
            L[t] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B[t - 1] + W[t] - B[t]) / W[t]
        end

        val = 0.0
        for t in 1:T
            val += beta^(t - 1) * (gamma * log_barrier(C[t], 1e-9) + (1.0 - gamma) * log_barrier(1.0 - L[t], 1e-9))
        end
        return -val
    end

    # Initial guess assuming constant consumption
    L_const = 0.5
    C_const = (sum(W) / T) * L_const * gamma
    B_guess = zeros(T - 1)
    B_guess[1] = (1.0 + R) * B0 + W[1] * L_const - C_const
    for t in 2:(T - 1)
        B_guess[t] = (1.0 + R) * B_guess[t - 1] + W[t] * L_const - C_const
    end

    res = optimize(objective, B_guess, BFGS(), Optim.Options(g_tol=1e-12, iterations=2000))
    best_B = res.minimizer

    B = [best_B..., 0.0]
    C = zeros(T)
    L = zeros(T)
    C[1] = gamma * ((1.0 + R) * B0 + W[1] - B[1])
    L[1] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B0 + W[1] - B[1]) / W[1]
    for t in 2:T
        C[t] = gamma * ((1.0 + R) * B[t - 1] + W[t] - B[t])
        L[t] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B[t - 1] + W[t] - B[t]) / W[t]
    end
    L = clamp.(L, 0.0, 1.0 - 1e-9)
    O = 1.0 .- L
    W_L = W .* L

    return Dict("C" => C, "L" => L, "O" => O, "B" => B, "W_L" => W_L)
end

end # module ConsumptionLeisure
