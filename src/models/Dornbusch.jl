module Dornbusch

using LinearAlgebra

export DornbuschParams, default_calibration, steady_state, coefficient_matrices, eigenvalues, is_saddle_path, simulate_shock

"""
    DornbuschParams

Calibration parameters for the exchange rate overshooting model (Cap. 3).
"""
struct DornbuschParams
    psi::Float64     # Income sensitivity of money demand
    theta::Float64   # Interest rate sensitivity of money demand
    beta1::Float64   # Real exchange rate sensitivity of aggregate demand
    beta2::Float64   # Nominal interest rate sensitivity of aggregate demand
    mi::Float64      # Speed of price adjustment
    beta0::Float64   # Autonomous aggregate demand
    m0::Float64      # Log of money supply
    ypot0::Float64   # Potential output
    pstar0::Float64  # Log of foreign price level
    istar0::Float64  # Foreign nominal interest rate
end

"""
    default_calibration()

Returns the default calibration based on Chapter 3.
"""
function default_calibration()
    return DornbuschParams(
        0.05,    # psi
        0.5,     # theta
        20.0,    # beta1
        0.1,     # beta2
        0.01,    # mi
        500.0,   # beta0
        100.0,   # m0
        2000.0,  # ypot0
        0.0,     # pstar0
        3.0      # istar0
    )
end

"""
    steady_state(params::DornbuschParams)

Computes the analytical steady state of the Dornbusch overshooting model.
"""
function steady_state(params::DornbuschParams)
    # En el estado estacionario de largo plazo:
    # 1. Los precios nacionales (p_ss) se derivan del equilibrio del mercado monetario (LM).
    #    Cuando la producción está en su nivel potencial (ypot0) y el interés nacional iguala al extranjero (istar0):
    #    p = m - psi * ypot + theta * istar
    p_ss = params.m0 - params.psi * params.ypot0 + params.theta * params.istar0
    
    # 2. El tipo de cambio nominal de largo plazo (s_ss) equilibra la demanda agregada (IS).
    #    Despejando s de la ecuación IS cuando yd = ypot:
    s_ss = p_ss + (params.ypot0 - params.beta0 + params.beta2 * params.istar0) / params.beta1 - params.pstar0

    return Dict(
        "p" => p_ss,
        "s" => s_ss,
        "i" => params.istar0,   # Por la condición de paridad de intereses (UIP), i = istar
        "yd" => params.ypot0,   # En el largo plazo la demanda agregada coincide con el producto potencial
        "dp" => 0.0,            # En el estado estacionario, los precios no varían (dp = 0)
        "ds" => 0.0             # Tampoco varía el tipo de cambio nominal (ds = 0)
    )
end

"""
    coefficient_matrices(params::DornbuschParams)

Builds the system transition matrices A and B.
"""
function coefficient_matrices(params::DornbuschParams)
    mi = params.mi
    beta1 = params.beta1
    beta2 = params.beta2
    theta = params.theta
    psi = params.psi

    # Matriz A (2x2): Matriz de coeficientes del sistema dinámico lineal para las variables
    # endógenas de estado y expectativa: [p_t, s_t]'.
    # Modela el efecto cruzado de los precios nacionales y el tipo de cambio.
    A = [-mi * (beta1 + beta2 / theta)  mi * beta1;
         1.0 / theta                     0.0]

    # Matriz B (2x5): Matriz de impacto de los shocks exógenos.
    # El vector de variables exógenas z_t se compone de: [beta0, m_t, ypot0, istar0, pstar0]'
    B = [mi   mi * beta2 / theta   -mi * (1.0 + psi * beta2 / theta)   0.0       mi * beta1;
         0.0  -1.0 / theta          psi / theta                         -1.0      0.0]

    return A, B
end

"""
    eigenvalues(params::DornbuschParams)

Computes the eigenvalues of system matrix A.
"""
function eigenvalues(params::DornbuschParams)
    # Obtenemos la matriz de coeficientes A del sistema linealizado
    A, _ = coefficient_matrices(params)
    # Calculamos sus autovalores (eigenvalues). En un modelo de tipo de cambio 
    # de Dornbusch, para tener estabilidad de punto de silla, debemos tener 
    # un autovalor estable (negativo/menor que 1 en valor absoluto) y uno inestable.
    return real(eigvals(A))
end

"""
    is_saddle_path(params::DornbuschParams)

Checks if the system has saddle-point stability.
"""
function is_saddle_path(params::DornbuschParams)
    lambdas = eigenvalues(params)
    # Contamos cuántos autovalores son estables en tiempo discreto.
    # Un autovalor es estable si |1 + lambda| < 1 (es decir, cae dentro del círculo unitario).
    stable_count = count(lam -> abs(1.0 + lam) < 1.0, lambdas)
    # La estabilidad de punto de silla requiere exactamente 1 autovalor estable (para 1 variable predeterminada y 1 no predeterminada).
    return stable_count == 1
end

"""
    simulate_shock(params, z_initial, z_final, periods=30, shock_period=1)

Simulates a permanent policy shock using saddle-path expectations.
"""
function simulate_shock(
    params::DornbuschParams,
    z_initial::AbstractVector,
    z_final::AbstractVector,
    periods::Int=30,
    shock_period::Int=1
)
    # 1. Definimos y calculamos el estado estacionario inicial (antes del shock)
    params_pre = DornbuschParams(
        params.psi, params.theta, params.beta1, params.beta2, params.mi,
        z_initial[1], z_initial[2], z_initial[3], z_initial[5], z_initial[4]
    )
    ss_pre = steady_state(params_pre)

    # 2. Definimos y calculamos el estado estacionario final (después del shock monetario u otro shock)
    params_post = DornbuschParams(
        params.psi, params.theta, params.beta1, params.beta2, params.mi,
        z_final[1], z_final[2], z_final[3], z_final[5], z_final[4]
    )
    ss_post = steady_state(params_post)

    # 3. Descomposición espectral de la matriz A para obtener los autovectores
    A, _ = coefficient_matrices(params_post)
    decomp = eigen(A)
    eigs = decomp.values
    V = decomp.vectors

    # Identificamos el autovector asociado al autovalor estable (saddle path)
    stable_idx = argmin(abs.(eigs .+ 1.0))
    v_s = real(V[:, stable_idx])

    t = 0:(periods - 1)
    p_path = zeros(periods)
    s_path = zeros(periods)
    i_path = zeros(periods)
    yd_path = zeros(periods)

    # 4. Fase Pre-Shock: La economía se encuentra tranquila en su equilibrio inicial
    for tt in 1:shock_period
        p_path[tt] = ss_pre["p"]
        s_path[tt] = ss_pre["s"]
        i_path[tt] = ss_pre["i"]
        yd_path[tt] = ss_pre["yd"]
    end

    # 5. Periodo del Shock (Impacto inmediato):
    # Los precios nacionales (p) son rígidos en el corto plazo (sticky prices), por lo que no cambian en t_shock.
    p_path[shock_period + 1] = ss_pre["p"]
    # El tipo de cambio (s) es flexible y da un salto inmediato (sobrerreacción)
    # ajustándose a la senda estable determinada por el autovector estable:
    s_path[shock_period + 1] = ss_post["s"] + (v_s[2] / v_s[1]) * (p_path[shock_period + 1] - ss_post["p"])

    # 6. Simulación temporal paso a paso tras el shock
    for tt in (shock_period + 2):periods
        # Calculamos la variación marginal de precios (dp) y del tipo de cambio (ds) usando el sistema A
        dp = A[1, 1] * (p_path[tt - 1] - ss_post["p"]) + A[1, 2] * (s_path[tt - 1] - ss_post["s"])
        ds = A[2, 1] * (p_path[tt - 1] - ss_post["p"]) + A[2, 2] * (s_path[tt - 1] - ss_post["s"])
        # Transición en diferencias finitas
        p_path[tt] = p_path[tt - 1] + dp
        s_path[tt] = s_path[tt - 1] + ds
    end

    # 7. Cálculo de las variables secundarias (tipo de interés e IS) post-shock
    for tt in (shock_period + 1):periods
        # Despejamos el tipo de interés a partir del equilibrio del mercado monetario (LM)
        i_path[tt] = (p_path[tt] - params_post.m0 + params_post.psi * params_post.ypot0) / params_post.theta
        # Calculamos la demanda agregada usando la ecuación IS
        yd_path[tt] = params_post.beta0 + params_post.beta1 * (s_path[tt] - p_path[tt] + params_post.pstar0) - params_post.beta2 * i_path[tt]
    end

    return Dict(
        "t" => collect(t),
        "p" => p_path,
        "s" => s_path,
        "i" => i_path,
        "yd" => yd_path
    )
end

end # module Dornbusch
