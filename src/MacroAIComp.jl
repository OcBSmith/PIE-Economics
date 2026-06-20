module MacroAIComp

# Incluimos los modelos
include("models/ArmsRace.jl")
include("models/ISLM.jl")
include("models/Dornbusch.jl")
include("models/ConsumptionSavings.jl")
include("models/ConsumptionLeisure.jl")
include("models/FiscalPolicy.jl")
include("models/TobinQ.jl")
include("models/DGE.jl")
include("models/Growth.jl")
include("models/Ramsey.jl")

using .ArmsRace
using .ISLM
using .Dornbusch
using .ConsumptionSavings: ConsumptionSavingParameters, generate_income_profile
using .ConsumptionLeisure: ConsumptionLeisureParameters
using .FiscalPolicy
using .TobinQ: TobinQParams, compute_linearized_system, solve_linearized_simulation
using .DGE: DGEParams, solve_blanchard_khan
using .Growth
using .Ramsey

# ==============================================================================
# RESOLUCIÓN DE DESPACHO MÚLTIPLE PARA FUNCIONES COMUNES
# ==============================================================================

export default_calibration,
    steady_state,
    compute_steady_state,
    coefficient_matrices,
    eigenvalues,
    is_saddle_path,
    simulate,
    simulate_shock

# steady_state
function steady_state(params::ArmsRaceParams, z::AbstractVector)
    return ArmsRace.steady_state(params, z)
end

function steady_state(params::ISLMParams)
    return ISLM.steady_state(params)
end

function steady_state(params::DornbuschParams)
    return Dornbusch.steady_state(params)
end

# compute_steady_state
function compute_steady_state(params::TobinQParams, R::Union{Real, Nothing}=nothing)
    return TobinQ.compute_steady_state(params, R)
end

function compute_steady_state(params::DGEParams)
    return DGE.compute_steady_state(params)
end

# default_calibration
function default_calibration(::Type{ISLMParams})
    return ISLM.default_calibration()
end

function default_calibration(::Type{DornbuschParams})
    return Dornbusch.default_calibration()
end

function default_calibration(::Type{ConsumptionSavingParameters})
    return ConsumptionSavings.default_calibration()
end

function default_calibration(::Type{ConsumptionLeisureParameters})
    return ConsumptionLeisure.default_calibration()
end

function default_calibration(::Type{FiscalPolicyParameters})
    return FiscalPolicy.default_calibration()
end

function default_calibration(::Type{TobinQParams})
    return TobinQ.default_calibration()
end

function default_calibration(::Type{DGEParams})
    return DGE.default_calibration()
end

function default_calibration(::Type{SolowSwanParameters})
    return Growth.default_calibration()
end

function default_calibration(::Type{RamseyParams})
    return Ramsey.default_calibration()
end

# coefficient_matrices
function coefficient_matrices(params::ArmsRaceParams)
    return ArmsRace.coefficient_matrices(params)
end

function coefficient_matrices(params::DornbuschParams)
    return Dornbusch.coefficient_matrices(params)
end

# eigenvalues
function eigenvalues(params::ArmsRaceParams)
    return ArmsRace.eigenvalues(params)
end

function eigenvalues(params::DornbuschParams)
    return Dornbusch.eigenvalues(params)
end

# is_saddle_path
function is_saddle_path(params::ArmsRaceParams)
    return ArmsRace.is_saddle_path(params)
end

function is_saddle_path(params::DornbuschParams)
    return Dornbusch.is_saddle_path(params)
end

# simulate (Richardson)
function simulate(
    params::ArmsRaceParams,
    z_initial::AbstractVector,
    z_final::AbstractVector,
    periods::Int=30,
    shock_period::Int=2
)
    return ArmsRace.simulate(params, z_initial, z_final, periods, shock_period)
end

# simulate_shock
function simulate_shock(
    params::ISLMParams,
    initial_state::AbstractVector,
    t_span::Tuple{<:Real, <:Real},
    t_eval::AbstractVector
)
    return ISLM.simulate_shock(params, initial_state, t_span, t_eval)
end

function simulate_shock(
    params::DornbuschParams,
    z_initial::AbstractVector,
    z_final::AbstractVector,
    periods::Int=30,
    shock_period::Int=1
)
    return Dornbusch.simulate_shock(params, z_initial, z_final, periods, shock_period)
end

# solve_foc_fsolve
function solve_foc_fsolve(params::ConsumptionSavingParameters, W::AbstractVector)
    return ConsumptionSavings.solve_foc_fsolve(params, W)
end

function solve_foc_fsolve(params::ConsumptionLeisureParameters, W::AbstractVector)
    return ConsumptionLeisure.solve_foc_fsolve(params, W)
end

# solve_direct_optim
function solve_direct_optim(params::ConsumptionSavingParameters, W::AbstractVector)
    return ConsumptionSavings.solve_direct_optim(params, W)
end

function solve_direct_optim(params::ConsumptionLeisureParameters, W::AbstractVector)
    return ConsumptionLeisure.solve_direct_optim(params, W)
end

# solve_nonlinear_simulation
function solve_nonlinear_simulation(
    params::TobinQParams,
    K0::Real,
    R_path::AbstractVector,
    T::Int=100
)
    return TobinQ.solve_nonlinear_simulation(params, K0, R_path, T)
end

function solve_nonlinear_simulation(
    params::DGEParams,
    K0::Real,
    A_path::AbstractVector,
    T::Int=100
)
    return DGE.solve_nonlinear_simulation(params, K0, A_path, T)
end

# ==============================================================================
# EXPORTS ESPECÍFICOS DE CADA MODELO
# ==============================================================================

# ArmsRace
export ArmsRaceParams,
    simulate_saddle_path

# ISLM
export ISLMParams,
    system_dynamics

# Dornbusch
export DornbuschParams

# ConsumptionSavings
export ConsumptionSavingParameters,
    generate_income_profile,
    solve_foc_fsolve,
    solve_direct_optim

# ConsumptionLeisure
export ConsumptionLeisureParameters

# FiscalPolicy
export FiscalPolicyParameters,
    solve_non_distortionary,
    solve_distortionary_foc,
    solve_distortionary_optim,
    solve_social_security

# TobinQ
export TobinQParams,
    compute_linearized_system,
    solve_linearized_simulation,
    solve_nonlinear_simulation

# DGE
export DGEParams,
    solve_blanchard_khan,
    solve_nonlinear_simulation

# Growth
export SolowSwanParameters,
    compute_solow_steady_state,
    simulate_solow_swan

# Ramsey
export RamseyParams,
    compute_ramsey_steady_state,
    compute_ramsey_transition_matrix,
    solve_ramsey_linearized,
    solve_ramsey_nonlinear

end # module MacroAIComp
