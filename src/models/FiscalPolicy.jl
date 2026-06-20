module FiscalPolicy

using NLsolve
using Optim

export FiscalPolicyParameters, default_calibration, solve_non_distortionary, solve_distortionary_foc, solve_distortionary_optim, solve_social_security

function log_barrier(u, epsilon=1e-9)
    if u > epsilon
        return log(u)
    else
        return log(epsilon) - (epsilon - u) / epsilon - 0.5 * ((epsilon - u) / epsilon)^2
    end
end

"""
    FiscalPolicyParameters

Calibration parameters for the fiscal policy model (Cap. 6).
"""
struct FiscalPolicyParameters
    T::Int            # Number of periods
    beta::Float64     # Discount factor
    R::Float64        # Real interest rate
    gamma::Float64    # Consumption weight in utility
    B0::Float64       # Initial assets
    tauw::Float64     # Wage income tax rate
    tauc::Float64     # Consumption tax rate
    taur::Float64     # Capital income tax rate
    tau_ss::Float64   # Social security contribution rate
    t_star::Int       # Retirement period (1-based index is t_star + 1)
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
end

"""
    solve_non_distortionary(params, W, return_transfers=false)

Solves the consumption-savings problem with lump-sum taxes.
"""
function solve_non_distortionary(
    params::FiscalPolicyParameters,
    W::AbstractVector,
    return_transfers::Bool=false
)
    T = params.T
    beta = params.beta
    R = params.R
    tauw = params.tauw
    B0 = params.B0
    growth = beta * (1.0 + R)

    # Effective income
    Y_eff = return_transfers ? copy(W) : W .* (1.0 - tauw)

    function build_path(C0)
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        B = zeros(T)
        B[1] = (1.0 + R) * B0 + Y_eff[1] - C[1]
        for t in 2:T
            B[t] = (1.0 + R) * B[t - 1] + Y_eff[t] - C[t]
        end
        return C, B
    end

    function residuals!(F, x)
        C0 = x[1]
        _, B = build_path(C0)
        F[1] = B[T]
    end

    C0_guess = [sum(Y_eff) / T]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C, B = build_path(sol.zero[1])
    return Dict("C" => C, "B" => B)
end

"""
    solve_distortionary_foc(params, W, return_transfers=false)

Solves the optimal consumption-leisure problem with distortionary taxes using FOCs.
"""
function solve_distortionary_foc(
    params::FiscalPolicyParameters,
    W::AbstractVector,
    return_transfers::Bool=false
)
    T = params.T
    beta = params.beta
    R_net = params.R * (1.0 - params.taur)
    R_gross = 1.0 + R_net
    tauw = params.tauw
    tauc = params.tauc
    gamma = params.gamma
    B0 = params.B0
    growth = beta * R_gross

    function build_path(C0)
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        net_wage = W .* (1.0 - tauw) ./ (1.0 + tauc)
        net_wage = [w < 1e-12 ? 1e-12 : w for w in net_wage]
        L = clamp.(1.0 .- (1.0 - gamma) .* C ./ (gamma .* net_wage), 0.0, 1.0 - 1e-9)

        # Tax revenue transfer (if returned)
        transfer = zeros(T)
        if return_transfers
            transfer[1] = tauw * W[1] * L[1] + tauc * C[1] + params.taur * params.R * max(0.0, B0)
            for t in 2:T
                transfer[t] = tauw * W[t] * L[t] + tauc * C[t]
            end
        end

        B = zeros(T)
        B[1] = (1.0 + params.R) * B0 + W[1] * L[1] * (1.0 - tauw) - C[1] * (1.0 + tauc) + transfer[1]
        for t in 2:T
            B[t] = (1.0 + R_net) * B[t - 1] + W[t] * L[t] * (1.0 - tauw) - C[t] * (1.0 + tauc) + transfer[t]
        end
        return C, L, B
    end

    function residuals!(F, x)
        C0 = x[1]
        _, _, B = build_path(C0)
        F[1] = B[T]
    end

    C0_guess = [sum(W) / T * gamma * 0.5]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C, L, B = build_path(sol.zero[1])
    return Dict("C" => C, "L" => L, "B" => B)
end

"""
    solve_distortionary_optim(params, W, return_transfers=false)

Solves the optimal consumption-leisure problem with distortionary taxes using direct Optim.jl optimization.
"""
function solve_distortionary_optim(
    params::FiscalPolicyParameters,
    W::AbstractVector,
    return_transfers::Bool=false
)
    T = params.T
    beta = params.beta
    R = params.R
    tauw = params.tauw
    tauc = params.tauc
    taur = params.taur
    gamma = params.gamma
    B0 = params.B0
    R_asset = R * (1.0 - taur)

    if return_transfers
        tauw_capped = min(tauw, 1.0 - 1e-9)
        ratio = ((1.0 - gamma) / gamma) * (1.0 + tauc) / (1.0 - tauw_capped)
        gamma_eff = 1.0 / (1.0 + ratio)
    else
        gamma_eff = gamma
    end

    # Decision variables: B[1] ... B[T-1]
    function objective(x)
        B = [x..., 0.0]
        C = zeros(T)
        L = zeros(T)

        if return_transfers
            C[1] = gamma_eff * ((1.0 + R_asset) * B0 + W[1] - B[1])
            L[1] = W[1] < 1e-12 ? 0.0 : 1.0 - ((1.0 - gamma_eff) / gamma_eff) * C[1] / W[1]
            for t in 2:T
                C[t] = gamma_eff * ((1.0 + R_asset) * B[t - 1] + W[t] - B[t])
                L[t] = W[t] < 1e-12 ? 0.0 : 1.0 - ((1.0 - gamma_eff) / gamma_eff) * C[t] / W[t]
            end
        else
            C[1] = (gamma / (1.0 + tauc)) * ((1.0 + R_asset) * B0 + W[1] * (1.0 - tauw) - B[1])
            L[1] = (W[1] < 1e-12 || abs(1.0 - tauw) < 1e-12) ? 0.0 : 1.0 - ((1.0 - gamma) / gamma) * ((1.0 + tauc) / (1.0 - tauw)) * C[1] / W[1]
            for t in 2:T
                C[t] = (gamma / (1.0 + tauc)) * ((1.0 + R_asset) * B[t - 1] + W[t] * (1.0 - tauw) - B[t])
                L[t] = (W[t] < 1e-12 || abs(1.0 - tauw) < 1e-12) ? 0.0 : 1.0 - ((1.0 - gamma) / gamma) * ((1.0 + tauc) / (1.0 - tauw)) * C[t] / W[t]
            end
        end

        val = 0.0
        for t in 1:T
            val += beta^(t - 1) * (gamma_eff * log_barrier(C[t], 1e-9) + (1.0 - gamma_eff) * log_barrier(1.0 - L[t], 1e-9))
        end
        return -val
    end

    # Initial guess assuming constant consumption
    L_const = 0.5
    C_const = (sum(W) / T) * L_const * gamma
    B_guess = zeros(T - 1)
    if return_transfers
        B_guess[1] = (1.0 + R_asset) * B0 + W[1] * L_const - C_const
        for t in 2:(T - 1)
            B_guess[t] = (1.0 + R_asset) * B_guess[t - 1] + W[t] * L_const - C_const
        end
    else
        B_guess[1] = (1.0 + R_asset) * B0 + W[1] * (1.0 - tauw) * L_const - (1.0 + tauc) * C_const
        for t in 2:(T - 1)
            B_guess[t] = (1.0 + R_asset) * B_guess[t - 1] + W[t] * (1.0 - tauw) * L_const - (1.0 + tauc) * C_const
        end
    end

    res = optimize(objective, B_guess, BFGS(), Optim.Options(g_tol=1e-12, iterations=2000))
    best_B = res.minimizer

    B = [best_B..., 0.0]
    C = zeros(T)
    L = zeros(T)
    if return_transfers
        C[1] = gamma_eff * ((1.0 + R_asset) * B0 + W[1] - B[1])
        L[1] = W[1] < 1e-12 ? 0.0 : 1.0 - ((1.0 - gamma_eff) / gamma_eff) * C[1] / W[1]
        for t in 2:T
            C[t] = gamma_eff * ((1.0 + R_asset) * B[t - 1] + W[t] - B[t])
            L[t] = W[t] < 1e-12 ? 0.0 : 1.0 - ((1.0 - gamma_eff) / gamma_eff) * C[t] / W[t]
        end
    else
        C[1] = (gamma / (1.0 + tauc)) * ((1.0 + R_asset) * B0 + W[1] * (1.0 - tauw) - B[1])
        L[1] = (W[1] < 1e-12 || abs(1.0 - tauw) < 1e-12) ? 0.0 : 1.0 - ((1.0 - gamma) / gamma) * ((1.0 + tauc) / (1.0 - tauw)) * C[1] / W[1]
        for t in 2:T
            C[t] = (gamma / (1.0 + tauc)) * ((1.0 + R_asset) * B[t - 1] + W[t] * (1.0 - tauw) - B[t])
            L[t] = (W[t] < 1e-12 || abs(1.0 - tauw) < 1e-12) ? 0.0 : 1.0 - ((1.0 - gamma) / gamma) * ((1.0 + tauc) / (1.0 - tauw)) * C[t] / W[t]
        end
    end
    L = clamp.(L, 0.0, 1.0 - 1e-9)

    return Dict("C" => C, "L" => L, "B" => B)
end

"""
    solve_social_security(params, W)

Solves the social security capitalization pension system.
"""
function solve_social_security(params::FiscalPolicyParameters, W::AbstractVector)
    T = params.T
    beta = params.beta
    R = params.R
    tau_ss = params.tau_ss
    t_star = params.t_star
    B0 = params.B0
    growth = beta * (1.0 + R)

    # Compute pension accumulated value at t_star (1-based is t_star)
    pension = 0.0
    for t in 1:t_star
        pension += tau_ss * W[t] * (1.0 + R)^(t_star - t)
    end

    # Build effective income path
    Y_eff = zeros(T)
    for t in 1:t_star
        Y_eff[t] = W[t] * (1.0 - tau_ss)
    end
    if t_star + 1 <= T
        Y_eff[t_star + 1] += pension
    end

    function build_path(C0)
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        B = zeros(T)
        B[1] = (1.0 + R) * B0 + Y_eff[1] - C[1]
        for t in 2:T
            B[t] = (1.0 + R) * B[t - 1] + Y_eff[t] - C[t]
        end
        return C, B
    end

    function residuals!(F, x)
        C0 = x[1]
        _, B = build_path(C0)
        F[1] = B[T]
    end

    valid_W = W[W .> 0]
    C0_guess = [!isempty(valid_W) ? (sum(valid_W) / length(valid_W)) * (1.0 - tau_ss) : 1.0]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C, B = build_path(sol.zero[1])

    return Dict("C" => C, "B" => B, "Pension" => pension)
end

end # module FiscalPolicy
