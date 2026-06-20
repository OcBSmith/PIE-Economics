module Growth

export SolowSwanParameters, default_calibration, compute_solow_steady_state, simulate_solow_swan

"""
    SolowSwanParameters

Parámetros de calibración para el modelo de crecimiento de Solow-Swan (Cap. 9).
Se utiliza una estructura inmutable (`struct`) para garantizar el mejor rendimiento en Julia.
"""
struct SolowSwanParameters
    alpha::Float64  # Participación del capital en la renta [α] (elasticidad de la producción respecto al capital)
    delta::Float64  # Tasa de depreciación del capital [δ]
    s::Float64      # Tasa de ahorro exógena [s]
    n::Float64      # Tasa de crecimiento de la población [n]
    A::Float64      # Productividad Total de los Factores (PTF o TFP) [A]
end

"""
    default_calibration()

Devuelve la calibración por defecto para Solow-Swan.
"""
function default_calibration()
    return SolowSwanParameters(0.35, 0.08, 0.20, 0.0, 1.0)
end

"""
    compute_solow_steady_state(params, s=nothing, n=nothing, A=nothing)

Calcula el estado estacionario (steady state) del modelo Solow-Swan.
Permite sobrescribir algunos parámetros temporalmente (como s, n, A) para ver su efecto sin alterar la estructura original.
"""
function compute_solow_steady_state(
    params::SolowSwanParameters,
    s::Union{Real, Nothing}=nothing,
    n::Union{Real, Nothing}=nothing,
    A::Union{Real, Nothing}=nothing
)
    # Asignación condicional: usamos el parámetro provisto, o el de por defecto si es 'nothing'.
    s_val = isnothing(s) ? params.s : s
    n_val = isnothing(n) ? params.n : n
    A_val = isnothing(A) ? params.A : A
    alpha = params.alpha
    delta = params.delta

    # El capital per cápita estacionario se halla igualando la inversión de reposición al ahorro.
    # Inversión de reposición = (δ + n) * k
    # Ahorro = s * y = s * A * k^α
    # Igualando y despejando 'k': k_ss = (s * A / (δ + n)) ^ (1 / (1 - α))
    k_ss = (s_val * A_val / (delta + n_val)) ^ (1.0 / (1.0 - alpha))
    
    # Producción y variables estacionarias derivadas
    y_ss = A_val * k_ss^alpha
    i_ss = s_val * y_ss
    c_ss = (1.0 - s_val) * y_ss

    return Dict("k" => k_ss, "y" => y_ss, "c" => c_ss, "i" => i_ss)
end

"""
    simulate_solow_swan(params, k0, s_path, n_path, A_path, T=100)

Simula la transición del modelo Solow-Swan dado un stock de capital inicial (k0) y trayectorias exógenas en el tiempo.

# Argumentos
- `params`: Parámetros del modelo base.
- `k0`: Nivel de capital inicial per cápita.
- `s_path`, `n_path`, `A_path`: Vectores que definen los valores de s, n y A en cada momento temporal t.
- `T`: Horizonte de tiempo total para la simulación.
"""
function simulate_solow_swan(
    params::SolowSwanParameters,
    k0::Real,
    s_path::AbstractVector,
    n_path::AbstractVector,
    A_path::AbstractVector,
    T::Int=100
)
    alpha = params.alpha
    delta = params.delta

    # Preasignamos memoria para los vectores para hacer el bucle ultra-eficiente en Julia
    k = zeros(T)
    y = zeros(T)
    c = zeros(T)
    inv = zeros(T)
    gy = zeros(T)  # Tasa de crecimiento económico (growth rate of y)

    # Condiciones iniciales (t=1)
    k[1] = k0
    y[1] = A_path[1] * k[1]^alpha
    c[1] = (1.0 - s_path[1]) * y[1]
    inv[1] = s_path[1] * y[1]
    gy[1] = 0.0

    # Bucle principal de transición temporal (en diferencias discretas aproximadas)
    for t in 2:T
        # Ley de acumulación de capital per cápita. 
        # Es una versión discreta: el capital futuro es el no depreciado más la inversión ajustado por la población.
        k[t] = (1.0 - delta - n_path[t - 1]) * k[t - 1] + s_path[t - 1] * A_path[t - 1] * k[t - 1]^alpha
        
        # Variables endógenas del nuevo periodo
        y[t] = A_path[t] * k[t]^alpha
        c[t] = (1.0 - s_path[t]) * y[t]
        inv[t] = s_path[t] * y[t]
        
        # Cálculo de la tasa de crecimiento respecto al periodo anterior
        gy[t] = y[t - 1] > 0.0 ? (y[t] - y[t - 1]) / y[t - 1] : 0.0
    end

    return Dict("k" => k, "y" => y, "c" => c, "i" => inv, "gy" => gy)
end

end # module Growth
