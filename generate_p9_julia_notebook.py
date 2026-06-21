import nbformat as nbf
import os
import json
import sys

sys.path.append('scratch')
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\09-ramsey\python.ipynb")
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
using NLsolve
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params_base = default_calibration(RamseyParams)
ss = compute_ramsey_steady_state(params_base)

println("VALORES DE EQUILIBRIO (SS):")
println("  Capital por trabajador efectivo (K*) : ", round(ss["K"], digits=4))
println("  Consumo (C*)                         : ", round(ss["C"], digits=4))
println("  Producción (Y*)                      : ", round(ss["Y"], digits=4))
println("  Inversión (I*)                       : ", round(ss["I"], digits=4))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""println("Autovalores de la matriz de transición (Blanchard-Kahn):")
mat = compute_ramsey_transition_matrix(params_base)
println(eigvals(mat))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock permanente Ramsey
@manipulate for A_final in 0.50:0.05:1.50, beta_final in 0.90:0.01:0.99
    
    params_init = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params_init)
    K0 = ss_init["K"]
    T_sim = 50
    
    A_path = fill(A_final, T_sim)
    A_path[1] = params_init.A
    
    beta_path = fill(beta_final, T_sim)
    beta_path[1] = params_init.beta
    
    res = solve_ramsey_nonlinear(params_init, K0, A_path, beta_path, T_sim)
    
    params_fin = RamseyParams(params_init.alpha, beta_final, params_init.delta, params_init.n, params_init.g, A_final)
    ss_fin = compute_ramsey_steady_state(params_fin)
    
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res["Y"], color=:blue, lw=2.5, label="Renta (Y)")
    hline!([ss_init["Y"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["Y"]], color=:black, ls=:dash, label="Y* Final")
    title!("Producción (Y)")
    
    p2 = plot(t_axis, res["C"], color=:purple, lw=2.5, label="Consumo (C)")
    hline!([ss_init["C"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["C"]], color=:black, ls=:dash, label="C* Final")
    title!("Consumo (C)")
    
    p3 = plot(t_axis, res["I"], color=:orange, lw=2.5, label="Inversión (I)")
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["I"]], color=:black, ls=:dash, label="I* Final")
    title!("Inversión (I)")
    
    p4 = plot(t_axis, res["K"], color=:forestgreen, lw=2.5, label="Capital (K)")
    hline!([ss_init["K"]], color=:gray, ls=:dot, label="")
    hline!([ss_fin["K"]], color=:black, ls=:dash, label="K* Final")
    title!("Capital (K)")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste hacia el Nuevo Estado Estacionario (Ramsey)", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal (Blanchard-Kahn) vs No Lineal (Shooting)
@manipulate for A_shock in 1.01:0.01:1.10
    
    params = default_calibration(RamseyParams)
    ss_comp = compute_ramsey_steady_state(params)
    K0 = ss_comp["K"]
    T_sim = 40
    
    A_path = fill(A_shock, T_sim)
    A_path[1] = params.A
    
    beta_path = fill(params.beta, T_sim)
    
    # Resolver
    res_lin = solve_ramsey_linearized(params, K0, A_path, beta_path, T_sim)
    res_nonlin = solve_ramsey_nonlinear(params, K0, A_path, beta_path, T_sim)
    
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res_nonlin["K"], color=:purple, lw=3, label="Shooting (NL)")
    plot!(t_axis, res_lin["K"], color=:blue, ls=:dash, lw=2, label="Lineal (BK)")
    title!("Capital (K)")
    xlabel!("Tiempo")
    
    p2 = plot(t_axis, res_nonlin["C"], color=:orange, lw=3, label="Shooting (NL)")
    plot!(t_axis, res_lin["C"], color=:blue, ls=:dash, lw=2, label="Lineal (BK)")
    title!("Consumo (C)")
    xlabel!("Tiempo")
    
    plot(p1, p2, layout=(1,2), size=(800, 350), 
         plot_title="Aproximación Lineal vs Exacta (Shock $(A_shock))", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation para No Lineal y Blanchard-Kahn
A_bench = fill(1.05, 50)
A_bench[1] = 1.00
beta_bench = fill(0.96, 50)

println("Benchmark NLsolve (Shooting No Lineal):")
@btime solve_ramsey_nonlinear($params_base, $ss["K"], $A_bench, $beta_bench, 50)

println("Benchmark Blanchard-Kahn (Lineal):")
@btime solve_ramsey_linearized($params_base, $ss["K"], $A_bench, $beta_bench, 50)
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

dir_path = "practicas/09-ramsey/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
