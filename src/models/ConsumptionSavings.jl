module ConsumptionSavings

using NLsolve
using Optim

export ConsumptionSavingParameters, default_calibration, generate_income_profile, solve_foc_fsolve, solve_direct_optim

"""
    ConsumptionSavingParameters

Calibration parameters for the consumption-savings model (Cap. 4).
"""
struct ConsumptionSavingParameters
    T::Int         # Number of periods (horizon)
    beta::Float64  # Discount factor
    R::Float64     # Real interest rate
    B0::Float64    # Initial assets
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return ConsumptionSavingParameters(30, 0.97, 0.02, 0.0)
end

"""
    generate_income_profile(profile, T)

Generates an income profile of length T.
"""
function generate_income_profile(profile::String, T::Int)
    W = zeros(T)
    if profile == "constant"
        W .= 10.0
    elseif profile == "increasing"
        W = collect(range(10.0, 20.0, length=T))
    elseif profile == "retirement"
        working = min(20, T)
        W[1:working] .= 10.0
        W[(working + 1):T] .= 0.0
    else
        throw(ArgumentError("Unknown income profile: \$profile"))
    end
    return W
end

"""
    solve_foc_fsolve(params, W)

Solves the optimal consumption-savings problem using Euler equations and NLsolve.
"""
function solve_foc_fsolve(params::ConsumptionSavingParameters, W::AbstractVector)
    T = params.T
    beta = params.beta
    R = params.R
    B0 = params.B0
    growth = beta * (1.0 + R)

    function residuals!(F, x)
        C0 = x[1]
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        B = zeros(T)
        B[1] = (1.0 + R) * B0 + W[1] - C[1]
        for t in 2:T
            B[t] = (1.0 + R) * B[t - 1] + W[t] - C[t]
        end
        F[1] = B[T]
    end

    C0_guess = [sum(W) / T]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C0 = sol.zero[1]

    C = [C0 * (growth^t) for t in 0:(T - 1)]
    B = zeros(T)
    B[1] = (1.0 + R) * B0 + W[1] - C[1]
    for t in 2:T
        B[t] = (1.0 + R) * B[t - 1] + W[t] - C[t]
    end

    return Dict("C" => C, "B" => B)
end

"""
    solve_direct_optim(params, W)

Solves the optimal consumption-savings problem using direct optimization with Optim.jl.
"""
function solve_direct_optim(params::ConsumptionSavingParameters, W::AbstractVector)
    T = params.T
    beta = params.beta
    R = params.R
    B0 = params.B0

    # Decision variables: B[1] ... B[T-1]
    # We reconstruct the full path including B[T] = 0.0.
    function objective(x)
        B = [x..., 0.0]
        C = zeros(T)
        C[1] = (1.0 + R) * B0 + W[1] - B[1]
        for t in 2:T
            C[t] = (1.0 + R) * B[t - 1] + W[t] - B[t]
        end
        
        # Smooth barrier penalty to prevent non-positive consumption
        if any(c -> c <= 1e-10, C)
            return 1e10 + sum(c <= 0.0 ? (1e-10 - c)^2 : 0.0 for c in C)
        end
        
        return -sum(beta^(t - 1) * log(C[t]) for t in 1:T)
    end

    # Initial guess assuming constant consumption
    C_const = sum(W) / T
    B_guess = zeros(T - 1)
    B_guess[1] = (1.0 + R) * B0 + W[1] - C_const
    for t in 2:(T - 1)
        B_guess[t] = (1.0 + R) * B_guess[t - 1] + W[t] - C_const
    end

    res = optimize(objective, B_guess, BFGS(), Optim.Options(g_tol=1e-12, iterations=1000))
    
    best_B = res.minimizer
    B = [best_B..., 0.0]
    C = zeros(T)
    C[1] = (1.0 + R) * B0 + W[1] - B[1]
    for t in 2:T
        C[t] = (1.0 + R) * B[t - 1] + W[t] - B[t]
    end

    return Dict("C" => C, "B" => B)
end

end # module ConsumptionSavings
