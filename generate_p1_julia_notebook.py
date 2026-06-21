import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\01-is-lm-dinamico\python.ipynb")
nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[0]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[1]))

nb.cells.append(nbf.v4.new_code_cell("""# En Google Colab se activarían y descargarían los paquetes necesarios.
# using Pkg; Pkg.activate("."); Pkg.instantiate()
"""))

nb.cells.append(nbf.v4.new_code_cell("""using Pkg
Pkg.activate("../..")

using MacroAIComp
using Plots
import Plots: mm
using LinearAlgebra
using DifferentialEquations
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params = default_calibration(ISLMParams)
println(params)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""ss = steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Renta de pleno empleo (Y*) : ", ss["Y"])
println("  Nivel de precios (P*)      : ", ss["P"])
println("  Tipo de interés (i*)       : ", round(ss["i"], digits=2), "%")
println("  Demanda agregada (Yd*)     : ", ss["Yd"])
"""))

# Reemplazar la referencia a scipy en la celda 4
md_4 = md_cells[4].replace("`scipy.integrate.solve_ivp`", "`DifferentialEquations.jl`").replace("Python", "Julia")
nb.cells.append(nbf.v4.new_markdown_cell(md_4))

# Mostramos el system_dynamics en Julia como se hacía en Python con def
nb.cells.append(nbf.v4.new_code_cell("""# Así definimos el sistema dinámico en Julia (ver src/models/ISLM.jl)
function custom_system_dynamics!(du, u, p, t)
    Y = u[1]
    P = u[2]
    
    params = p
    # Curva LM
    i_rate = (P - params.m0 + params.psi * Y) / params.theta
    # Curva IS
    Y_d = params.beta0 - params.beta1 * (i_rate - 0.0) # pi=0
    
    # Phillips y Ajuste
    du[1] = params.ni * (Y_d - Y)
    du[2] = params.mi * (Y - params.ypot0)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con diagrama de fases
@manipulate for m0_val in 80.0:1.0:120.0, beta0_val in 1800.0:10.0:2400.0
    
    params_sim = default_calibration(ISLMParams)
    ss_init = steady_state(params_sim)
    initial_state = [ss_init["Y"], ss_init["P"]]
    
    params_sim = ISLMParams(params_sim.theta, params_sim.psi, params_sim.beta1, 
                            params_sim.mi, params_sim.ni, beta0_val, m0_val, params_sim.ypot0)
    
    t_span = (0.0, 30.0)
    t_eval = collect(range(0.0, 30.0, length=300))
    
    res = simulate_shock(params_sim, initial_state, t_span, t_eval)
    Y_path = res[1, :]
    P_path = res[2, :]
    ss_final = steady_state(params_sim)
    
    # Panel 1: Renta
    p1 = plot(t_eval, Y_path, color=:steelblue, lw=2.5, label="Producción (Y)")
    hline!([params_sim.ypot0], color=:red, ls=:dash, label="Renta Potencial")
    title!("Evolución de la Renta")
    xlabel!("Tiempo (t)")
    ylabel!("Y")
    
    # Panel 2: Precios
    p2 = plot(t_eval, P_path, color=:forestgreen, lw=2.5, label="Precios (P)")
    hline!([ss_init["P"]], color=:gray, ls=:dot, label="P inicial")
    hline!([ss_final["P"]], color=:black, ls=:dash, label="P final")
    title!("Evolución de Precios")
    xlabel!("Tiempo (t)")
    ylabel!("P")
    
    # Panel 3: Diagrama de Fases
    p3 = plot(Y_path, P_path, color=:purple, lw=3, label="Trayectoria dinámica")
    vline!([params_sim.ypot0], color=:orange, ls=:dash, lw=2, label="P_dot = 0")
    
    Y_vals = range(minimum(Y_path)-15, maximum(Y_path)+15, length=100)
    slope = params_sim.theta * params_sim.mi - params_sim.theta / params_sim.beta1 - params_sim.psi
    int_init = ss_init["P"] - slope * params_sim.ypot0
    int_final = ss_final["P"] - slope * params_sim.ypot0
    
    P_loc_init = int_init .+ slope .* Y_vals
    P_loc_final = int_final .+ slope .* Y_vals
    
    plot!(Y_vals, P_loc_init, color=:blue, ls=:dot, label="Y_dot = 0 (Inicial)")
    plot!(Y_vals, P_loc_final, color=:blue, ls=:dash, lw=2, label="Y_dot = 0 (Final)")
    
    # Quiver
    Y_grid = range(minimum(Y_path)-8, maximum(Y_path)+8, length=12)
    P_grid = range(minimum(P_path)-0.8, maximum(P_path)+0.8, length=12)
    
    y_pts = Float64[]
    p_pts = Float64[]
    dy_pts = Float64[]
    dp_pts = Float64[]
    
    for y in Y_grid, p in P_grid
        dy, dp = system_dynamics([y, p], params_sim, 0.0)
        norm = sqrt(dy^2 + dp^2)
        if norm > 0
            push!(y_pts, y)
            push!(p_pts, p)
            push!(dy_pts, (dy/norm)*2.0) # Escalar para visualización
            push!(dp_pts, (dp/norm)*0.2)
        end
    end
    quiver!(y_pts, p_pts, quiver=(dy_pts, dp_pts), color=:gray, alpha=0.5)
    
    scatter!([ss_init["Y"]], [ss_init["P"]], color=:gray, markersize=6, label="EE Inicial")
    scatter!([ss_final["Y"]], [ss_final["P"]], color=:black, markersize=8, marker=:star, label="EE Final")
    
    title!("Diagrama de Fases (Y, P)")
    xlabel!("Producción (Y)")
    ylabel!("Nivel de Precios (P)")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Respuesta del modelo IS-LM", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_code_cell("""@assert isapprox(ss["Y"], 2000.0; atol=1e-5)
@assert isapprox(ss["P"], 81.0; atol=1e-5)
@assert isapprox(ss["i"], 2.0; atol=1e-5)
println("OK: coincide con el oráculo.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[8]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime simulate_shock($params, [2000.0, 81.0], (0.0, 50.0), collect(range(0.0, 50.0, length=500)))
"""))

nb.metadata = {
    "kernelspec": {
        "display_name": "Julia 1.12.6",
        "language": "julia",
        "name": "julia-1.12",
    },
    "language_info": {
        "file_extension": ".jl",
        "mimetype": "application/julia",
        "name": "julia",
        "version": "1.12.6",
    },
}

dir_path = "practicas/01-is-lm-dinamico/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
