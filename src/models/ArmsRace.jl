module ArmsRace

using LinearAlgebra

export ArmsRaceParams,
    coefficient_matrices,
    steady_state,
    eigenvalues,
    is_saddle_path,
    simulate,
    simulate_saddle_path

"""
    ArmsRaceParams

Calibration of Richardson's arms race model (eq. 1.9-1.11).

# Fields
- `alpha::Float64`: Elasticity of dx1 with respect to x1.
- `beta::Float64`: Elasticity of dx1 with respect to x2.
- `gamma::Float64`: Elasticity of dx2 with respect to x1.
- `delta::Float64`: Elasticity of dx2 with respect to x2.
- `theta::Float64`: Elasticity of dx1 with respect to z1.
- `eta::Float64`: Elasticity of dx2 with respect to z2.
"""
struct ArmsRaceParams
    alpha::Float64
    beta::Float64
    gamma::Float64
    delta::Float64
    theta::Float64
    eta::Float64
end

"""
    coefficient_matrices(params::ArmsRaceParams)

Build the A and B matrices of the dynamic system (eq. 1.7-1.8).
"""
function coefficient_matrices(params::ArmsRaceParams)
    A = [-params.alpha params.beta; params.gamma -params.delta]
    B = [params.theta 0.0; 0.0 params.eta]
    return A, B
end

"""
    steady_state(params::ArmsRaceParams, z::AbstractVector)

Compute the steady state of the system (eq. 1.14).
"""
function steady_state(params::ArmsRaceParams, z::AbstractVector)
    A, B = coefficient_matrices(params)
    return -(A \ (B * z))
end

"""
    eigenvalues(params::ArmsRaceParams)

Compute the eigenvalues of matrix A (eq. 1.20-1.25).
"""
function eigenvalues(params::ArmsRaceParams)
    A, _ = coefficient_matrices(params)
    return eigvals(A)
end

"""
    is_saddle_path(params::ArmsRaceParams)

Classify the steady state as a saddle point or globally stable.
"""
function is_saddle_path(params::ArmsRaceParams)
    lambdas = eigenvalues(params)
    moduli = abs.(lambdas .+ 1.0)
    return count(x -> x < 1.0, moduli) == 1
end

"""
    simulate(params::ArmsRaceParams, z_initial::AbstractVector, z_final::AbstractVector, periods::Int=30, shock_period::Int=2)

Simulate the transition dynamics after a shock (Section 1.5).
"""
function simulate(
    params::ArmsRaceParams,
    z_initial::AbstractVector,
    z_final::AbstractVector,
    periods::Int=30,
    shock_period::Int=2,
)
    A, B = coefficient_matrices(params)
    x = zeros(periods, 2)
    x[1, :] = steady_state(params, z_initial)
    for t in 1:(periods - 1)
        z_t = (t + 1 >= shock_period) ? z_final : z_initial
        # x[t+1] = x[t] + A*x[t] + B*z_t
        x[t + 1, :] = x[t, :] + (A * x[t, :] + B * z_t)
    end
    return x[:, 1], x[:, 2]
end

"""
    simulate_saddle_path(params::ArmsRaceParams, z_initial::AbstractVector, z_final::AbstractVector, periods::Int=30, shock_period::Int=2, jump_variable::Int=1)

Simulate transition dynamics when the steady state is a saddle point.
"""
function simulate_saddle_path(
    params::ArmsRaceParams,
    z_initial::AbstractVector,
    z_final::AbstractVector,
    periods::Int=30,
    shock_period::Int=2,
    jump_variable::Int=1,
)
    if !is_saddle_path(params)
        throw(ArgumentError("Calibration does not produce a saddle-point steady state."))
    end

    A, B = coefficient_matrices(params)
    lambdas = eigenvalues(params)
    # Find the eigenvalue closest to stable boundary
    stable_lambda = lambdas[argmin(abs.(lambdas .+ 1.0))]

    other_variable = 3 - jump_variable
    x_bar_final = steady_state(params, z_final)

    x = zeros(periods, 2)
    x[1, :] = steady_state(params, z_initial)

    for t in 1:(periods - 1)
        if t + 1 == shock_period
            # other_variable evolves backward
            x[t + 1, other_variable] =
                x[t, other_variable] +
                A[other_variable, 1] * x[t, 1] +
                A[other_variable, 2] * x[t, 2] +
                B[other_variable, 1] * z_initial[1] +
                B[other_variable, 2] * z_initial[2]

            # jump_variable jumps to saddle path
            row = A[jump_variable, :]
            x[t + 1, jump_variable] =
                (
                    row[other_variable] * x[t + 1, other_variable] +
                    B[jump_variable, jump_variable] * z_final[jump_variable] +
                    stable_lambda * x_bar_final[jump_variable]
                ) / (stable_lambda - row[jump_variable])
        else
            z_t = (t + 1 > shock_period) ? z_final : z_initial
            x[t + 1, :] = x[t, :] + (A * x[t, :] + B * z_t)
        end
    end
    return x[:, 1], x[:, 2]
end

end # module ArmsRace
