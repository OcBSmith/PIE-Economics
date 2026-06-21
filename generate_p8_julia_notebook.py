import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\08-solow-swan\python.ipynb")
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

nb.cells.append(nbf.v4.new_code_cell("""params_base = default_calibration(SolowSwanParameters)
ss = compute_solow_steady_state(params_base)

println("VALORES DE ESTADO ESTACIONARIO:")
println("  Capital por trabajador (k*)   : ", round(ss["k"], digits=4))
println("  Producción por trabajador (y*): ", round(ss["y"], digits=4))
println("  Consumo por trabajador (c*)   : ", round(ss["c"], digits=4))
println("  Inversión por trabajador (i*) : ", round(ss["i"], digits=4))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Transición Dinámica de Solow
@manipulate for s_final in 0.10:0.01:0.50, n_final in 0.00:0.005:0.05, A_final in 0.5:0.1:2.0
    
    params_init = default_calibration(SolowSwanParameters)
    ss_init = compute_solow_steady_state(params_init)
    k0 = ss_init["k"]
    T_sim = 100
    
    # Send shocks at t=5
    s_path = fill(params_init.s, T_sim)
    s_path[6:end] .= s_final
    
    n_path = fill(params_init.n, T_sim)
    n_path[6:end] .= n_final
    
    A_path = fill(params_init.A, T_sim)
    A_path[6:end] .= A_final
    
    res = simulate_solow_swan(params_init, k0, s_path, n_path, A_path, T_sim)
    
    params_fin = SolowSwanParameters(params_init.alpha, params_init.delta, s_final, n_final, A_final)
    ss_fin = compute_solow_steady_state(params_fin)
    
    t_shock = 5
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res["k"], color=:blue, lw=2.5, label="Capital (k)")
    hline!([ss_init["k"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["k"]], color=:black, ls=:dash, label="k* Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Capital por trabajador")
    xlabel!("Tiempo")
    
    p2 = plot(t_axis, res["y"], color=:purple, lw=2.5, label="Renta (y)")
    hline!([ss_init["y"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["y"]], color=:black, ls=:dash, label="y* Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Renta per cápita")
    xlabel!("Tiempo")
    
    p3 = plot(t_axis, res["c"], color=:forestgreen, lw=2.5, label="Consumo (c)")
    hline!([ss_init["c"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["c"]], color=:black, ls=:dash, label="c* Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita")
    xlabel!("Tiempo")
    
    p4 = plot(t_axis, res["gy"], color=:orange, lw=2.5, label="Crecimiento (gy)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Tasa de Crecimiento del PIB p.c. (%)")
    xlabel!("Tiempo")
    ylabel!("% de crecimiento")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste hacia el Nuevo Estado Estacionario", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Demostración Visual de la Regla de Oro
@manipulate for s_current in 0.05:0.01:0.60
    
    params = default_calibration(SolowSwanParameters)
    alpha_val = params.alpha
    delta_val = params.delta
    n_val = params.n
    A_val = params.A
    
    # Calcular la tasa de ahorro de la regla de oro (s_gold = alpha en Solow simple)
    s_gold = alpha_val
    k_gold = (s_gold * A_val / (delta_val + n_val))^(1 / (1 - alpha_val))
    c_gold = A_val * k_gold^alpha_val - (delta_val + n_val) * k_gold
    
    # Estado estacionario actual
    k_curr = (s_current * A_val / (delta_val + n_val))^(1 / (1 - alpha_val))
    y_curr = A_val * k_curr^alpha_val
    i_curr = s_current * y_curr
    c_curr = y_curr - i_curr
    
    # Crear malla de capitales para graficar
    k_vals = range(0.1, 50.0, length=200)
    y_vals = A_val .* k_vals .^ alpha_val
    inv_vals = s_current .* y_vals
    req_inv = (delta_val + n_val) .* k_vals
    
    # Gráfica
    p1 = plot(k_vals, y_vals, color=:purple, lw=3, label="Producción f(k)")
    plot!(k_vals, inv_vals, color=:blue, lw=2.5, label="Ahorro/Inv. s_current")
    plot!(k_vals, req_inv, color=:red, lw=2.5, label="Inv. Requerida (n+δ)k")
    
    # Marcar el punto actual
    vline!([k_curr], color=:gray, ls=:dot, lw=2, label="k* Actual")
    scatter!([k_curr], [y_curr], color=:purple, markersize=6, label="")
    scatter!([k_curr], [req_inv[argmin(abs.(k_vals .- k_curr))]], color=:red, markersize=6, label="")
    
    # Llenar área de consumo actual
    plot!( [k_curr, k_curr], [i_curr, y_curr], color=:forestgreen, lw=5, label="Consumo actual: $(round(c_curr, digits=2))" )
    
    # Marcar Golden Rule
    vline!([k_gold], color=:orange, ls=:dash, lw=2, label="k* Golden Rule")
    scatter!([k_gold], [A_val * k_gold^alpha_val], color=:orange, markersize=8, marker=:star, label="Max Consumo")
    
    title!("Regla de Oro en Solow-Swan")
    xlabel!("Capital por trabajador (k)")
    ylabel!("Renta, Inversión")
    
    plot(p1, size=(700, 450), plot_title="Comparativa Consumo vs Golden Rule", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
T_bench = 100
s_path = fill(0.20, T_bench); n_path = fill(0.015, T_bench); A_path = fill(1.0, T_bench)
@btime simulate_solow_swan($params_base, $ss["k"], $s_path, $n_path, $A_path, $T_bench)
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

dir_path = "practicas/08-solow-swan/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
