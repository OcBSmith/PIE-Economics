import nbformat as nbf
import os
import json
import sys

sys.path.append('scratch')
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\06-tobin-q\python.ipynb")
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
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock Tasa Interés
@manipulate for R_init in 0.02:0.005:0.06, R_final in 0.02:0.005:0.06, phi_val in 1.0:1.0:20.0, delta_val in 0.02:0.01:0.10, alpha_val in 0.2:0.05:0.4
    
    params_base = TobinQParams(alpha_val, delta_val, phi_val, R_init)
    ss_init = compute_steady_state(params_base)
    K0 = ss_init["K"]
    T_sim = 50
    
    R_path = fill(R_final, T_sim)
    R_path[1] = R_init
    
    res = solve_nonlinear_simulation(params_base, K0, R_path, T_sim)
    
    params_final = TobinQParams(alpha_val, delta_val, phi_val, R_final)
    ss_final = compute_steady_state(params_final)
    
    t_axis = 0:(T_sim - 1)
    
    # Panel 1: Q de Tobin
    p1 = plot(t_axis, res["q"], color=:purple, lw=2.5, label="Q (Valor de Mercado)")
    hline!([ss_init["q"]], color=:gray, ls=:dot, label="q Inicial")
    hline!([ss_final["q"]], color=:black, ls=:dash, label="q Final")
    title!("Q de Tobin (q_t)")
    xlabel!("Periodos")
    
    # Panel 2: Capital
    p2 = plot(t_axis, res["K"], color=:blue, lw=2.5, label="Capital (K)")
    hline!([ss_init["K"]], color=:gray, ls=:dot, label="K Inicial")
    hline!([ss_final["K"]], color=:black, ls=:dash, label="K Final")
    title!("Stock de Capital (K_t)")
    xlabel!("Periodos")
    
    # Panel 3: Inversión
    p3 = plot(t_axis, res["I"], color=:orange, lw=2.5, label="Inversión Bruta (I)")
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="I Inicial")
    hline!([ss_final["I"]], color=:black, ls=:dash, label="I Final")
    title!("Inversión (I_t)")
    xlabel!("Periodos")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Ajuste de Inversión y Capital ante Shock", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal vs No Lineal
params = TobinQParams(0.33, 0.06, 10.0, 0.04)
ss_init = compute_steady_state(params, 0.04)
K0 = ss_init["K"]
T_sim = 50

R_path = fill(0.03, T_sim)
R_path[1] = 0.04

res_lin = solve_linearized_simulation(params, K0, R_path, T_sim)
res_nonlin = solve_nonlinear_simulation(params, K0, R_path, T_sim)

t_axis = 0:(T_sim - 1)

p1 = plot(t_axis, res_nonlin["q"], label="No Lineal", color=:purple, lw=3)
plot!(t_axis, res_lin["q"], label="Linealizado", color=:purple, ls=:dash, lw=2)
title!("q de Tobin (Lineal vs No Lineal)")
xlabel!("Tiempo")

p2 = plot(t_axis, res_nonlin["K"], label="No Lineal", color=:blue, lw=3)
plot!(t_axis, res_lin["K"], label="Linealizado", color=:blue, ls=:dash, lw=2)
title!("Capital (Lineal vs No Lineal)")
xlabel!("Tiempo")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Diagrama de Fases
@manipulate for R_init in 0.02:0.005:0.06, R_final in 0.02:0.005:0.06, phi_val in 1.0:1.0:20.0, delta_val in 0.02:0.01:0.10, alpha_val in 0.2:0.05:0.4
    params_base = TobinQParams(alpha_val, delta_val, phi_val, R_init)
    ss_init = compute_steady_state(params_base)
    K0 = ss_init["K"]
    T_sim = 40
    
    R_path = fill(R_final, T_sim)
    R_path[1] = R_init
    res = solve_nonlinear_simulation(params_base, K0, R_path, T_sim)
    
    params_final = TobinQParams(alpha_val, delta_val, phi_val, R_final)
    ss_final = compute_steady_state(params_final)
    
    p1 = plot(res["K"], res["q"], color=:purple, lw=3, label="Trayectoria de silla")
    scatter!([ss_init["K"]], [ss_init["q"]], color=:gray, markersize=6, label="EE Inicial")
    scatter!([ss_final["K"]], [ss_final["q"]], color=:black, marker=:star, markersize=8, label="EE Final")
    
    hline!([1.0], color=:blue, ls=:dash, label="dq = 0")
    vline!([ss_final["K"]], color=:red, ls=:dash, label="dK = 0")
    
    title!("Diagrama de Fases (K, q)")
    xlabel!("Capital (K)")
    ylabel!("Q de Tobin (q)")
    
    plot(p1, size=(600, 400), plot_title="Ajuste Dinámico", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime solve_nonlinear_simulation($params, $K0, $R_path, $T_sim)
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

dir_path = "practicas/06-tobin-q/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
