module TobinQ

using LinearAlgebra
using NLsolve

export TobinQParams, default_calibration, compute_steady_state, compute_linearized_system, solve_linearized_simulation, solve_nonlinear_simulation

"""
    TobinQParams

Calibration parameters for Tobin's Q investment model (Cap. 7).
"""
struct TobinQParams
    alpha::Float64  # Capital elasticity of production
    delta::Float64  # Capital depreciation rate
    phi::Float64    # Investment adjustment cost parameter
    R::Float64      # Real interest rate
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return TobinQParams(0.35, 0.06, 10.0, 0.04)
end

"""
    compute_steady_state(params, R=nothing)

Computes the steady state of the Tobin's Q model.
"""
function compute_steady_state(params::TobinQParams, R::Union{Real, Nothing}=nothing)
    R_val = isnothing(R) ? params.R : R
    delta = params.delta
    alpha = params.alpha

    # En el estado estacionario de largo plazo:
    # 1. El ratio Q de Tobin (q_ss) es exactamente 1.0 (el coste de capital equivale a su valor de mercado).
    q_ss = 1.0
    # 2. El stock de capital estacionario K_ss se deriva igualando el PMK neto al tipo de interés real (R_val + delta):
    K_ss = ((R_val + delta) / alpha) ^ (1.0 / (alpha - 1.0))
    # 3. La inversión bruta (I_ss) cubre exactamente la depreciación del capital (delta * K_ss):
    I_ss = delta * K_ss
    # 4. El producto de estado estacionario Y_ss se calcula con la función de producción Cobb-Douglas:
    Y_ss = K_ss ^ alpha

    return Dict("q" => q_ss, "K" => K_ss, "I" => I_ss, "Y" => Y_ss)
end

"""
    compute_linearized_system(params)

Computes transition matrix A and saddle path slope for the linearized Tobin's Q.
"""
function compute_linearized_system(params::TobinQParams)
    alpha = params.alpha
    delta = params.delta
    phi = params.phi
    R = params.R

    # Coeficientes lineales de la matriz de transición A para el sistema dinámico [k_hat, q_hat]':
    A11 = (R * phi - (alpha - 1.0) * (R + delta)) / phi
    A12 = - (alpha - 1.0) * (R + delta)
    A21 = 1.0 / phi
    A22 = 0.0

    A = [A11 A12; A21 A22]

    # Obtenemos los autovalores para analizar la estabilidad de punto de silla
    eigenvals = real(eigvals(A))
    sorted_idx = sortperm(eigenvals)
    lambda_1 = eigenvals[sorted_idx[1]]  # Autovalor estable (negativo/menor que 1 en valor absoluto)
    lambda_2 = eigenvals[sorted_idx[2]]  # Autovalor inestable (positivo)

    # Multiplicadores de estabilidad en tiempo discreto:
    mu_1 = 1.0 + lambda_1
    mu_2 = 1.0 + lambda_2

    # Pendiente de la senda de silla estable (saddle path): determina cómo salta q_hat
    # ante desviaciones del stock de capital respecto al estado estacionario:
    theta = phi * lambda_1
    theta_book = theta

    return Dict(
        "lambda_1" => lambda_1,
        "lambda_2" => lambda_2,
        "mu_1" => mu_1,
        "mu_2" => mu_2,
        "theta" => theta,
        "theta_book" => theta_book,
        "A" => A
    )
end

"""
    solve_linearized_simulation(params, K0, R_path, T=100)

Simulates Tobin's Q using log-linearization saddle-path solver.
"""
function solve_linearized_simulation(
    params::TobinQParams,
    K0::Real,
    R_path::AbstractVector,
    T::Int=100
)
    # 1. Definimos la calibración final tras el shock de tipos de interés
    params_post = TobinQParams(params.alpha, params.delta, params.phi, R_path[end])
    ss_final = compute_steady_state(params_post)
    K_ss = ss_final["K"]

    # 2. Obtenemos el sistema linealizado post-shock
    lin = compute_linearized_system(params_post)
    lambda_1 = lin["lambda_1"]
    theta = lin["theta"]

    K = zeros(T)
    q = zeros(T)
    k_hat = zeros(T)
    q_hat = zeros(T)

    # 3. Inicialización usando desviaciones logarítmicas (hat) respecto al nuevo steady state:
    k_hat[1] = log(K0 / K_ss)
    q_hat[1] = theta * k_hat[1]  # El ratio Q salta inmediatamente a la senda de silla estable

    K[1] = K0
    q[1] = exp(q_hat[1])

    # 4. Transición temporal a lo largo de la senda estable
    for t in 2:T
        k_hat[t] = (1.0 + lambda_1) * k_hat[t - 1]
        q_hat[t] = theta * k_hat[t]
        
        K[t] = K_ss * exp(k_hat[t])
        q[t] = exp(q_hat[t])
    end

    # 5. Reconstrucción de variables reales de inversión y output
    # Ley de inversión con costes de ajuste cuadráticos: I_t = delta * K_t + K_t * (q_t - 1) / phi
    I = params.delta .* K .+ K .* (q .- 1.0) ./ params.phi
    Y = K .^ params.alpha

    return Dict("K" => K, "q" => q, "I" => I, "Y" => Y)
end

"""
    solve_nonlinear_simulation(params, K0, R_path, T=100)

Simulates Tobin's Q using non-linear simultaneous equations path solver.
"""
function solve_nonlinear_simulation(
    params::TobinQParams,
    K0::Real,
    R_path::AbstractVector,
    T::Int=100
)
    alpha = params.alpha
    delta = params.delta
    phi = params.phi

    # Usamos la solución linealizada como estimación inicial (guess) para el solucionador no lineal
    res_lin = solve_linearized_simulation(params, K0, R_path, T)
    K_guess = res_lin["K"]
    q_guess = res_lin["q"]

    # Definición del sistema de ecuaciones simultáneas no lineales
    function system_equations!(F, vars_flat)
        K = zeros(T)
        q = zeros(T)
        K[1] = K0
        # Mapeamos el vector plano a las variables de estado y expectativa
        K[2:T] = vars_flat[1:(T - 1)]
        q[1:T] = vars_flat[T:(2 * T - 1)]

        eqs = Float64[]

        # 1. Ecuaciones de acumulación de capital exactas:
        #    K[t+1] = (1-delta)*K[t] + I_t, donde I_t incluye el efecto del ratio Q de Tobin
        for t in 1:(T - 1)
            I_t = delta * K[t] + K[t] * (q[t] - 1.0) / phi
            push!(eqs, K[t + 1] - ((1.0 - delta) * K[t] + I_t))
        end

        # 2. Ecuación de Euler para la dinámica temporal de la Q de Tobin (valor de mercado de la empresa):
        #    q[t+1] = (1 + R_t)*q[t] - PMK_t + delta - (q[t]-1)^2 / (2*phi)
        for t in 1:(T - 1)
            R_t = R_path[min(t, length(R_path))]
            mpk = alpha * K[t] ^ (alpha - 1.0) # Producto Marginal del Capital
            push!(eqs, q[t + 1] - ((1.0 + R_t) * q[t] - mpk + delta - (q[t] - 1.0) ^ 2 / (2.0 * phi)))
        end

        # 3. Condición terminal (Condición de Transversalidad aproximada):
        #    En el largo plazo (periodo T), el valor de la empresa q debe converger al estado estacionario q*=1.0
        push!(eqs, q[T] - 1.0)

        F .= eqs
    end

    guess_flat = [K_guess[2:T]..., q_guess...]
    # Resolvemos el sistema usando el algoritmo Trust Region (NLsolve) con alta precisión
    sol = nlsolve(system_equations!, guess_flat, xtol=1e-12, ftol=1e-12)

    K = zeros(T)
    q = zeros(T)
    K[1] = K0
    K[2:T] = sol.zero[1:(T - 1)]
    q[1:T] = sol.zero[T:(2 * T - 1)]

    I = delta .* K .+ K .* (q .- 1.0) ./ phi
    Y = K .^ alpha

    return Dict("K" => K, "q" => q, "I" => I, "Y" => Y)
end

end # module TobinQ
