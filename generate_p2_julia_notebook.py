import nbformat as nbf
import os
import json
import sys

# Load md extractor
sys.path.append('scratch')
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\02-overshooting-dornbusch\python.ipynb")
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
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params_sim = default_calibration(DornbuschParams)
println(params_sim)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""ss_init = steady_state(params_sim)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Precios nacionales (p*)    : ", ss_init["p"])
println("  Tipo de cambio nominal (s*): ", ss_init["s"])
println("  Tipo de interés (i*)       : ", ss_init["i"], "%")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Autovalores
lambdas = eigenvalues(params_sim)
println("Autovalores: ", lambdas)
stable_idx = argmin(abs.(lambdas .+ 1.0))
stable_lambda = lambdas[stable_idx]
println("Autovalor estable: ", stable_lambda)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con diagrama de fases
@manipulate for m0_val in 98.0:0.5:104.0, beta0_val in 450.0:10.0:550.0
    
    z_initial = [500.0, 100.0, 2000.0, 3.0, 0.0]
    z_final = [beta0_val, m0_val, 2000.0, 3.0, 0.0]
    periods = 30
    
    # Calcular nuevos parámetros con z_final
    params_final = DornbuschParams(params_sim.theta, params_sim.psi, params_sim.beta1, 
                                 params_sim.beta2, params_sim.mi, 
                                 beta0_val, m0_val, 2000.0, 3.0, 0.0)
    ss_final = steady_state(params_final)
    
    res = simulate_shock(params_sim, z_initial, z_final, periods, 1)
    
    # Panel 1: Dinámica Temporal p y s
    t_axis = 0:(periods-1)
    p1 = plot(t_axis, res["s"], color=:purple, lw=2.5, label="Tipo cambio (s)")
    plot!(t_axis, res["p"], color=:forestgreen, lw=2.5, label="Precios (p)")
    hline!([ss_init["s"]], color=:purple, ls=:dot, label="s Inicial")
    hline!([ss_final["s"]], color=:purple, ls=:dash, label="s Final")
    hline!([ss_init["p"]], color=:forestgreen, ls=:dot, label="p Inicial")
    hline!([ss_final["p"]], color=:forestgreen, ls=:dash, label="p Final")
    vline!([1], color=:red, ls=:dash, label="Shock (t=1)")
    title!("Trayectorias (s y p)")
    xlabel!("Tiempo (t)")
    ylabel!("Escala Log")
    
    # Panel 2: Interés y Demanda Agregada
    p2 = plot(t_axis, res["i"], color=:steelblue, lw=2.0, label="Interés (i)")
    plot!(t_axis, res["yd"], color=:orange, lw=2.0, label="Demanda (yd)")
    hline!([z_final[4]], color=:steelblue, ls=:dash, label="i*")
    hline!([z_final[3]], color=:orange, ls=:dash, label="ypot")
    vline!([1], color=:red, ls=:dash, label="")
    title!("Tipos y Demanda")
    xlabel!("Tiempo (t)")
    
    # Panel 3: Diagrama de Fases
    p3 = plot(res["p"], res["s"], color=:purple, lw=3, label="Trayectoria dinámica")
    vline!([ss_final["p"]], color=:steelblue, ls=:dash, lw=2, label="ds = 0 (Final)")
    vline!([ss_init["p"]], color=:steelblue, ls=:dot, label="ds = 0 (Inicial)")
    
    p_vals = range(minimum(res["p"]) - 0.5, maximum(res["p"]) + 0.5, length=100)
    slope_dp = 1.0 + params_sim.beta2 / (params_sim.theta * params_sim.beta1)
    c_locus_init = ss_init["s"] - slope_dp * ss_init["p"]
    c_locus_final = ss_final["s"] - slope_dp * ss_final["p"]
    
    s_locus_init = c_locus_init .+ slope_dp .* p_vals
    s_locus_final = c_locus_final .+ slope_dp .* p_vals
    
    plot!(p_vals, s_locus_init, color=:forestgreen, ls=:dot, label="dp = 0 (Inicial)")
    plot!(p_vals, s_locus_final, color=:forestgreen, ls=:dash, lw=2, label="dp = 0 (Final)")
    
    a_mat, _ = coefficient_matrices(params_sim)
    k_slope = (stable_lambda - a_mat[1,1]) / a_mat[1,2]
    saddle_final = ss_final["s"] .+ k_slope .* (p_vals .- ss_final["p"])
    plot!(p_vals, saddle_final, color=:black, ls=:dashdot, label="Saddle Path")
    
    p_grid = range(minimum(res["p"]) - 0.3, maximum(res["p"]) + 0.3, length=10)
    s_grid = range(minimum(res["s"]) - 0.5, maximum(res["s"]) + 0.5, length=10)
    
    p_pts, s_pts, dp_pts, ds_pts = Float64[], Float64[], Float64[], Float64[]
    for pp in p_grid, ss in s_grid
        i_pt = -(z_final[2] - pp - params_sim.psi * z_final[3]) / params_sim.theta
        yd_pt = z_final[1] + params_sim.beta1 * (ss - pp + z_final[5]) - params_sim.beta2 * i_pt
        dp = params_sim.mi * (yd_pt - z_final[3])
        ds = i_pt - z_final[4]
        
        norm = sqrt(dp^2 + ds^2)
        if norm > 0
            push!(p_pts, pp); push!(s_pts, ss)
            push!(dp_pts, (dp/norm)*0.03); push!(ds_pts, (ds/norm)*0.05)
        end
    end
    quiver!(p_pts, s_pts, quiver=(dp_pts, ds_pts), color=:gray, alpha=0.5)
    
    scatter!([ss_init["p"]], [ss_init["s"]], color=:gray, markersize=6, label="EE Inic")
    scatter!([ss_final["p"]], [ss_final["s"]], color=:black, marker=:star, markersize=8, label="EE Fin")
    
    title!("Plano de Fases (p, s)")
    xlabel!("Precios (p)")
    ylabel!("Tipo cambio (s)")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Respuesta del modelo Dornbusch", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_code_cell("""@assert isapprox(ss_init["p"], 1.5; atol=1e-5)
@assert isapprox(ss_init["s"], 76.5150; atol=1e-3)
println("OK: coincide con el oráculo.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[8]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime simulate_shock($params_sim, [500.0, 100.0, 2000.0, 3.0, 0.0], [500.0, 101.0, 2000.0, 3.0, 0.0], 30, 1)
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

dir_path = "practicas/02-overshooting-dornbusch/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
