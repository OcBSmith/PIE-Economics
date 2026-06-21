import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\09-ramsey\python.ipynb")
nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[0]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[1]))

nb.cells.append(nbf.v4.new_code_cell("""# Este cuaderno depende del paquete `MacroAIComp` (Project.toml/Manifest.toml
# en la raíz del repositorio). En MyBinder (ver docs/DESPLIEGUE_BINDER.md) y en
# tu entorno local, el kernel ya arranca dentro del repositorio clonado, así
# que la celda siguiente activa e instancia el proyecto automáticamente.
# Nota: Google Colab no soporta Julia de forma nativa desde un notebook .ipynb;
# para la versión Julia de esta práctica usa MyBinder.
"""))

nb.cells.append(nbf.v4.new_code_cell("""using Pkg
Pkg.activate("../..")
Pkg.instantiate()

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
J, lambda_1, lambda_2, theta = compute_ramsey_transition_matrix(params_base)
println(eigvals(J))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock permanente Ramsey
@manipulate for A_final in 0.90:0.01:1.20, beta_final in 0.92:0.01:0.99
    
    params_init = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params_init)
    K0 = ss_init["K"]
    T_sim = 80
    t_shock = 5
    
    res = solve_ramsey_linearized(params_init, K0, A_final, params_init.n, beta_final, T_sim, t_shock)
    
    params_fin = RamseyParams(params_init.alpha, beta_final, params_init.delta, params_init.n, A_final)
    ss_fin = compute_ramsey_steady_state(params_fin)
    
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res["Y"], color=:blue, lw=2.5, label="Renta (Y)")
    hline!([ss_init["Y"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["Y"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Producción per cápita")
    xlabel!("Periodos")
    ylabel!("Y")
    
    p2 = plot(t_axis, res["C"], color=:purple, lw=2.5, label="Consumo (C)")
    hline!([ss_init["C"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["C"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita")
    xlabel!("Periodos")
    ylabel!("C")
    
    p3 = plot(t_axis, res["I"], color=:orange, lw=2.5, label="Inversión (I)")
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["I"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Inversión per cápita")
    xlabel!("Periodos")
    ylabel!("I")
    
    p4 = plot(t_axis, res["K"], color=:forestgreen, lw=2.5, label="Capital (K)")
    hline!([ss_init["K"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["K"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Capital per cápita")
    xlabel!("Periodos")
    ylabel!("K")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste Dinámico frente a Shock Permanente (Ramsey)", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal (Blanchard-Kahn) vs No Lineal (Shooting)
@manipulate for A_shock in 0.70:0.02:1.30
    
    params = default_calibration(RamseyParams)
    ss_comp = compute_ramsey_steady_state(params)
    K0 = ss_comp["K"]
    T_sim = 80
    t_shock = 5
    
    A_path = fill(1.00, T_sim)
    A_path[t_shock+1:end] .= A_shock
    
    n_path = fill(params.n, T_sim)
    
    # Resolver
    res_lin = solve_ramsey_linearized(params, K0, A_shock, params.n, params.beta, T_sim, t_shock)
    res_nonlin = solve_ramsey_nonlinear(params, K0, A_path, n_path, T_sim, t_shock)
    
    # Calcular errores relativos máximos
    err_C = maximum(abs.(res_nonlin["C"] .- res_lin["C"])) / ss_comp["C"] * 100
    err_K = maximum(abs.(res_nonlin["K"] .- res_lin["K"])) / ss_comp["K"] * 100
    println("Error relativo máximo en Consumo (C): ", round(err_C, digits=4), "%")
    println("Error relativo máximo en Capital (K): ", round(err_K, digits=4), "%")
    
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res_nonlin["C"], color=:purple, lw=3, label="Exacto No Lineal")
    plot!(t_axis, res_lin["C"], color=:purple, ls=:dash, lw=2, label="Blanchard-Khan (Lineal)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo (C_t)")
    xlabel!("Periodos")
    ylabel!("C")
    
    p2 = plot(t_axis, res_nonlin["K"], color=:forestgreen, lw=3, label="Exacto No Lineal")
    plot!(t_axis, res_lin["K"], color=:forestgreen, ls=:dash, lw=2, label="Blanchard-Khan (Lineal)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Capital (K_t)")
    xlabel!("Periodos")
    ylabel!("K")
    
    plot(p1, p2, layout=(1,2), size=(800, 350), 
         plot_title="Comparación Lineal vs No Lineal (Shock A=$(A_shock))", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation para No Lineal y Blanchard-Kahn
A_bench = fill(1.05, 50)
A_bench[1] = 1.00
n_bench = fill(params_base.n, 50)

println("Benchmark NLsolve (Shooting No Lineal):")
@btime solve_ramsey_nonlinear($params_base, $ss["K"], $A_bench, $n_bench, 50, 1)

println("Benchmark Blanchard-Kahn (Lineal):")
@btime solve_ramsey_linearized($params_base, $ss["K"], 1.05, $params_base.n, $params_base.beta, 50, 1)
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
