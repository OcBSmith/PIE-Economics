module Ramsey

using LinearAlgebra
using NLsolve

export RamseyParams, default_calibration, compute_ramsey_steady_state, compute_ramsey_transition_matrix, solve_ramsey_linearized, solve_ramsey_nonlinear

"""
    RamseyParams

Calibration parameters for the Ramsey optimal growth model (Cap. 10).
"""
struct RamseyParams
    alpha::Float64  # Capital income share
    beta::Float64   # Household discount factor
    delta::Float64  # Capital depreciation rate
    n::Float64      # Population growth rate
    A::Float64      # TFP steady state
end

"""
    default_calibration()

Returns the default calibration.
"""
function default_calibration()
    return RamseyParams(0.35, 0.97, 0.06, 0.02, 1.0)
end

"""
    compute_ramsey_steady_state(params)

Computes the deterministic steady state of the Ramsey model.
"""
"""
    compute_ramsey_steady_state(params)

Computes the deterministic steady state of the Ramsey model.
"""
function compute_ramsey_steady_state(params::RamseyParams)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    n = params.n
    A = params.A

    # 1. En el estado estacionario de largo plazo:
    #    La tasa de interés real (R_ss) se iguala a la tasa de descuento intertemporal modificada por la depreciación:
    #    Por la regla de oro modificada, 1/beta = 1 + R_ss - delta
    R_ss = 1.0 / beta - 1.0 + delta
    
    # 2. El capital per cápita estacionario (k_ss) despejado de la productividad marginal del capital:
    #    f'(k) = alpha * A * k^(alpha - 1) = R_ss
    k_ss = (alpha * A / R_ss) ^ (1.0 / (1.0 - alpha))
    
    # 3. Producción per cápita estacionaria y de pleno empleo (y_ss):
    y_ss = A * k_ss^alpha
    
    # 4. Inversión bruta per cápita estacionaria para reponer depreciación y absorber crecimiento poblacional:
    i_ss = (delta + n) * k_ss
    
    # 5. Consumo per cápita de equilibrio estacionario (c_ss) a partir de la restricción agregada:
    c_ss = y_ss - i_ss

    return Dict("k" => k_ss, "y" => y_ss, "c" => c_ss, "i" => i_ss, "R" => R_ss)
end

"""
    compute_ramsey_transition_matrix(params)

Computes the transition matrix J and saddle-path slope for the linearized Ramsey model.
"""
function compute_ramsey_transition_matrix(params::RamseyParams)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta
    n = params.n

    # Parámetros agregados de linealización de primer orden alrededor del steady state:
    Omega = 1.0 - beta + beta * delta
    Gamma = Omega - alpha * beta * (delta + n)

    # Elementos de la matriz Jacobiana J para el sistema en diferencias logarítmicas [c_hat, k_hat]':
    J11 = - (alpha - 1.0) * Omega * Gamma / (alpha * beta * (1.0 + n))
    J12 = (alpha - 1.0) * Omega / (beta * (1.0 + n))
    J21 = - Gamma / (alpha * beta * (1.0 + n))
    J22 = (1.0 - beta * (1.0 + n)) / (beta * (1.0 + n))

    J = [J11 J12; J21 J22]

    # Obtenemos los dos autovalores del Jacobiano J
    eigenvals = real(eigvals(J))
    sorted_idx = sortperm(eigenvals)
    lambda_1 = eigenvals[sorted_idx[1]]  # Autovalor estable (negativo, menor que 0)
    lambda_2 = eigenvals[sorted_idx[2]]  # Autovalor inestable (positivo, mayor que 0)

    # Pendiente analítica (theta) de la senda estable o saddle path para el consumo (c_hat = theta * k_hat)
    theta = alpha * (alpha - 1.0) * Omega / ((alpha - 1.0) * Omega * Gamma + alpha * beta * (1.0 + n) * lambda_1)

    return J, lambda_1, lambda_2, theta
end

"""
    solve_ramsey_linearized(params, k0, A_final, n_final, beta_final, T, t_shock)

Solves the Ramsey model using log-linearized saddle-path policy functions.
"""
function solve_ramsey_linearized(
    params::RamseyParams,
    k0::Real,
    A_final::Real=1.0,
    n_final::Real=0.02,
    beta_final::Real=0.97,
    T::Int=100,
    t_shock::Int=0
)
    # 1. Definimos y calculamos el nuevo steady state post-shock
    params_post = RamseyParams(params.alpha, beta_final, params.delta, n_final, A_final)
    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_new = ss_post["k"]
    c_ss_new = ss_post["c"]

    # 2. Obtenemos el autovalor estable y la pendiente theta post-shock
    _, r_stable, _, theta = compute_ramsey_transition_matrix(params_post)
    mu_s = 1.0 + r_stable  # Multiplicador estable en diferencias finitas

    k = zeros(T)
    c = zeros(T)
    y = zeros(T)
    i = zeros(T)
    k_hat = zeros(T)
    c_hat = zeros(T)

    # 3. Estado estacionario inicial previo al shock
    ss_pre = compute_ramsey_steady_state(params)
    k_ss_pre = ss_pre["k"]
    c_ss_pre = ss_pre["c"]
    y_ss_pre = ss_pre["y"]
    i_ss_pre = ss_pre["i"]

    shock_idx = t_shock + 1

    # 4. Periodos previos al shock: la economía se mantiene estable en su equilibrio inicial
    for t in 1:(shock_idx - 1)
        k[t] = k_ss_pre
        c[t] = c_ss_pre
        y[t] = y_ss_pre
        i[t] = i_ss_pre
        k_hat[t] = 0.0
        c_hat[t] = 0.0
    end

    # 5. Periodo de impacto del shock (t_shock):
    #    El capital (k) es rígido y no puede cambiar en t=t_shock (predeterminado por el pasado).
    k[shock_idx] = k0
    k_hat[shock_idx] = log(k0 / k_ss_new)
    #    El consumo (c) es flexible y salta de inmediato a la senda estable del nuevo steady state:
    c_hat[shock_idx] = theta * k_hat[shock_idx]
    c[shock_idx] = c_ss_new * exp(c_hat[shock_idx])
    y[shock_idx] = A_final * k[shock_idx]^params.alpha
    i[shock_idx] = y[shock_idx] - c[shock_idx]

    # 6. Evolución temporal sobre la senda estable post-shock
    for t in (shock_idx + 1):T
        k_hat[t] = mu_s * k_hat[t - 1]
        c_hat[t] = theta * k_hat[t]
        k[t] = k_ss_new * exp(k_hat[t])
        c[t] = c_ss_new * exp(c_hat[t])
        y[t] = A_final * k[t]^params.alpha
        i[t] = y[t] - c[t]
    end

    return Dict("k" => k, "c" => c, "y" => y, "i" => i, "k_hat" => k_hat, "c_hat" => c_hat)
end

"""
    solve_ramsey_nonlinear(params, k0, A_path, n_path, T, t_shock)

Solves the Ramsey model non-linearly using a shooting algorithm and NLsolve.
"""
function solve_ramsey_nonlinear(
    params::RamseyParams,
    k0::Real,
    A_path::AbstractVector,
    n_path::AbstractVector,
    T::Int=100,
    t_shock::Int=0
)
    alpha = params.alpha
    beta = params.beta
    delta = params.delta

    # Nuevo steady state de largo plazo para la condición terminal de convergencia
    params_post = RamseyParams(alpha, beta, delta, n_path[end], A_path[end])
    ss_post = compute_ramsey_steady_state(params_post)
    k_ss_final = ss_post["k"]
    c_ss_final = ss_post["c"]

    ss_pre = compute_ramsey_steady_state(params)
    k_pre = ss_pre["k"]
    c_pre = ss_pre["c"]

    shock_idx = t_shock + 1
    n_post = T - t_shock

    # Simulación temporal no lineal paso a paso dado un valor de consumo inicial (c_shock) en t_shock
    function simulate_from_shock(c_shock)
        k_sim = zeros(n_post)
        c_sim = zeros(n_post)
        k_sim[1] = k0
        c_sim[1] = c_shock
        for t in 1:(n_post - 1)
            idx = t + t_shock
            A_t = A_path[min(idx, length(A_path))]
            n_t = n_path[min(idx, length(n_path))]
            A_t1 = A_path[min(idx + 1, length(A_path))]

            y_t = A_t * k_sim[t]^alpha
            # Ley de acumulación de capital exacta per cápita:
            k_sim[t + 1] = ((1.0 - delta) * k_sim[t] + y_t - c_sim[t]) / (1.0 + n_t)
            if k_sim[t + 1] <= 0
                k_sim[t + 1] = 1e-8
            end
            # Regla de Keynes-Ramsey exacta para el consumo en el siguiente periodo:
            mpk_t1 = alpha * A_t1 * k_sim[t + 1]^(alpha - 1.0)
            c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
        end
        return k_sim, c_sim
    end

    # Función residual: mide la distancia entre el capital acumulado al final y el steady state final
    function residual(c_shock)
        k_sim, _ = simulate_from_shock(c_shock)
        return k_sim[end] - k_ss_final
    end

    # Método de Disparo (Shooting) mediante Búsqueda de Bisección No Lineal:
    # 1. Obtenemos una estimación inicial usando la aproximación lineal
    _, _, _, theta = compute_ramsey_transition_matrix(params_post)
    c_shock_guess = c_ss_final * exp(theta * log(k0 / k_ss_final))

    a = c_shock_guess * 0.5
    b = c_shock_guess * 1.5

    # 2. Acotamos el intervalo inferior (a) y superior (b) para la bisección
    while residual(a) < 0.0
        a *= 0.5
    end
    while residual(b) > 0.0
        b *= 1.5
    end

    # 3. Bucle de bisección para hallar la condición inicial c_shock exacta que elimina la divergencia
    for iter in 1:100
        mid = (a + b) / 2.0
        res = residual(mid)
        if abs(b - a) < 1e-15 || abs(res) < 1e-15
            break
        end
        if res > 0.0
            a = mid
        else
            b = mid
        end
    end
    c_shock = (a + b) / 2.0

    k_full = zeros(T)
    c_full = zeros(T)

    # 4. Reconstruimos los vectores de la simulación pre-shock
    for t in 1:(shock_idx - 1)
        k_full[t] = k_pre
        c_full[t] = c_pre
    end

    # 5. Acoplamos los resultados post-shock simulados con el consumo inicial corregido
    k_sim, c_sim = simulate_from_shock(c_shock)
    k_full[shock_idx:T] = k_sim
    c_full[shock_idx:T] = c_sim

    return Dict("k" => k_full, "c" => c_full)
end

end # module Ramsey
