module ISLM

using DifferentialEquations

export ISLMParams, default_calibration, steady_state, system_dynamics, simulate_shock

"""
    ISLMParams

Estructura de datos (Struct) que contiene los parámetros de calibración para el modelo IS-LM dinámico.
En Julia, usamos estructuras inmutables (`struct` en lugar de `mutable struct`) porque son mucho más rápidas y seguras.
"""
struct ISLMParams
    theta::Float64  # Sensibilidad de la demanda de dinero al tipo de interés [θ] (cuánto cae la demanda si sube el interés)
    psi::Float64    # Sensibilidad de la demanda de dinero a la renta [ψ] (cuánto sube la demanda por motivo transacción)
    beta1::Float64  # Sensibilidad de la demanda agregada (Inversión/Consumo) al tipo de interés real [β1]
    mi::Float64     # Parámetro de la Curva de Phillips [μ]: sensibilidad de la inflación a la brecha de producción (output gap)
    ni::Float64     # Velocidad de ajuste de la producción en el mercado de bienes [ν]
    beta0::Float64  # Demanda agregada autónoma [β0] (Gasto público, consumo autónomo)
    m0::Float64     # Oferta monetaria inicial dictada por el Banco Central [M0]
    ypot0::Float64  # Producción potencial o de pleno empleo [Y_barra]
end

"""
    default_calibration()

Devuelve una instancia de `ISLMParams` con los valores por defecto. 
Estos valores coinciden con el oráculo de MATLAB provisto en los apéndices.
"""
function default_calibration()
    return ISLMParams(
        0.5,     # theta
        0.01,    # psi
        50.0,    # beta1
        0.01,    # mi
        0.2,     # ni
        2100.0,  # beta0
        100.0,   # m0
        2000.0   # ypot0
    )
end

"""
    steady_state(params::ISLMParams)

Calcula el Estado Estacionario (Steady State) analítico del modelo IS-LM dinámico.
En estado estacionario, las variaciones (derivadas) de la producción (dY) y los precios (dP) son exactamente cero.

# Retorna
Un diccionario (`Dict`) con los valores de equilibrio de:
- `Y`: Producción (igual al potencial)
- `P`: Nivel de Precios
- `i`: Tipo de Interés
- `Yd`: Demanda Agregada
"""
function steady_state(params::ISLMParams)
    # 1. En el equilibrio de largo plazo, la producción es igual a la potencial por la Curva de Phillips.
    y_bar = params.ypot0
    
    # 2. Despejamos el nivel de precios P igualando la oferta y demanda de bienes y dinero.
    p_bar = (params.theta * params.beta0) / params.beta1 + params.m0 - (params.psi + params.theta / params.beta1) * y_bar
    
    # 3. Sustituyendo P en la ecuación de la LM, obtenemos el tipo de interés de equilibrio.
    i_bar = (p_bar - params.m0 + params.psi * y_bar) / params.theta
    
    # 4. La demanda agregada es la parte autónoma menos la parte sensible al interés.
    yd_bar = params.beta0 - params.beta1 * i_bar

    return Dict(
        "Y" => y_bar,
        "P" => p_bar,
        "i" => i_bar,
        "Yd" => yd_bar,
        "dP" => 0.0,
        "dY" => 0.0
    )
end

"""
    system_dynamics(u, params, t)

Define el campo vectorial del sistema de ecuaciones diferenciales continuas.
Esta función será integrada paso a paso por `DifferentialEquations.jl`.

# Argumentos
- `u`: Vector de estado actual `[Y, P]`.
- `params`: Parámetros del modelo (`ISLMParams`).
- `t`: Tiempo actual (necesario para el solver de ODEs aunque sea autónomo).
"""
function system_dynamics(u::AbstractVector, params::ISLMParams, t::Real)
    Y, P = u  # Desempaquetamos el vector de estado

    # 1. Equilibrio instantáneo en el mercado de dinero (Curva LM).
    # Suponemos ajuste instantáneo, por lo que despejamos el tipo de interés `i`.
    i = (P - params.m0 + params.psi * Y) / params.theta

    # 2. Demanda Agregada (Curva IS)
    Yd = params.beta0 - params.beta1 * i

    # 3. Leyes de Movimiento (Derivadas temporales)
    # Ajuste gradual de la producción según exceso de demanda (mercado de bienes)
    dY = params.ni * (Yd - Y)
    
    # Ajuste gradual de los precios (inflación) según la brecha de producción (Curva de Phillips)
    dP = params.mi * (Y - params.ypot0)

    # Retornamos el vector de derivadas [dY/dt, dP/dt]
    return [dY, dP]
end

"""
    simulate_shock(params, initial_state, t_span, t_eval)

Simula la dinámica del modelo IS-LM tras un shock partiendo de unas condiciones iniciales.

# Solucionador (Solver)
Utiliza el algoritmo `Tsit5()` que es un Runge-Kutta de orden 5 (ideal para problemas no rígidos), 
garantizando altísima precisión con tolerancias `reltol=1e-8` y `abstol=1e-10`.
"""
function simulate_shock(
    params::ISLMParams,
    initial_state::AbstractVector,
    t_span::Tuple{<:Real, <:Real},
    t_eval::AbstractVector
)
    # Definimos el problema matemático (Ecuación diferencial ordinaria)
    prob = ODEProblem(system_dynamics, initial_state, t_span, params)
    
    # Resolvemos el sistema guardando los puntos solicitados en `t_eval`
    sol = solve(prob, Tsit5(); saveat=t_eval, reltol=1e-8, abstol=1e-10)
    
    return sol
end

end # module ISLM
