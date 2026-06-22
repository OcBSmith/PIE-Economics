import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\08-solow-swan\python.ipynb")
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
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
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
@manipulate for s_final in slider(0.10:0.01:0.50; value=0.25, label="Ahorro (s)"), n_final in slider(0.00:0.005:0.05; value=0.02, label="Pob. (n)"), A_final in slider(0.5:0.1:2.0; value=1.00, label="TFP (A)")
    
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
    
    p1 = plot(t_axis, res["k"], color="#8EAD3A", lw=2.5, label="Capital (k)")
    hline!([ss_init["k"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["k"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Stock de Capital per cápita")
    xlabel!("Períodos")
    ylabel!("k")

    p2 = plot(t_axis, res["y"], color="#004C97", lw=2.5, label="Renta (y)")
    hline!([ss_init["y"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["y"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Producción per cápita (PIB p.c.)")
    xlabel!("Períodos")
    ylabel!("y")

    p3 = plot(t_axis, res["c"], color="#7A3E9F", lw=2.5, label="Consumo (c)")
    hline!([ss_init["c"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["c"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita")
    xlabel!("Períodos")
    ylabel!("c")

    p4 = plot(t_axis, res["gy"], color="#D95319", lw=2.5, label="Crecimiento (gy)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Tasa de Crecimiento de la Producción per cápita (%)")
    xlabel!("Períodos")
    ylabel!("% de crecimiento")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste hacia el Nuevo Estado Estacionario", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Demostración Visual de la Regla de Oro: Consumo de Estado Estacionario vs Tasa de Ahorro
@manipulate for s_current in slider(0.05:0.01:0.60; value=0.20, label="Tasa Ahorro")

    params = default_calibration(SolowSwanParameters)
    alpha_val = params.alpha

    # 1. Generar una malla de tasas de ahorro entre 0.01 y 0.95
    s_grid = range(0.01, 0.95, length=100)
    c_ss_grid = [compute_solow_steady_state(params, s_val)["c"] for s_val in s_grid]

    # Consumo actual y de la Regla de Oro (s_gold = alpha)
    c_current = compute_solow_steady_state(params, s_current)["c"]
    c_gold = compute_solow_steady_state(params, alpha_val)["c"]

    # 2. Gráfica
    p1 = plot(s_grid, c_ss_grid, color="#7A3E9F", lw=3, label="Consumo de Estado Estacionario (c̄)")

    # Regiones de (in)eficiencia dinámica
    plot!([0.01, alpha_val], [0.0, 0.0], fillrange=maximum(c_ss_grid) * 1.1, fillalpha=0.5,
          color="#E6F2FF", lw=0, label="Bajo-acumulación (Eficiente)")
    plot!([alpha_val, 0.95], [0.0, 0.0], fillrange=maximum(c_ss_grid) * 1.1, fillalpha=0.5,
          color="#FFE6E6", lw=0, label="Sobre-acumulación (Ineficiente)")

    # Punto actual
    scatter!([s_current], [c_current], color=:red, markersize=6,
             label="Ahorro actual (s=$(round(s_current, digits=2)), c=$(round(c_current, digits=3)))")
    vline!([s_current], color=:red, ls=:dot, alpha=0.5, label="")
    hline!([c_current], color=:red, ls=:dot, alpha=0.5, label="")

    # Regla de Oro
    scatter!([alpha_val], [c_gold], color="#8EAD3A", markersize=10, marker=:star,
             label="Regla de Oro (s_gold=α=$(round(alpha_val, digits=2)), c_gold=$(round(c_gold, digits=3)))")
    vline!([alpha_val], color="#8EAD3A", ls=:dash, alpha=0.7, label="")
    hline!([c_gold], color="#8EAD3A", ls=:dash, alpha=0.7, label="")

    title!("La Regla de Oro: Consumo Estacionario vs. Tasa de Ahorro")
    xlabel!("Tasa de Ahorro (s)")
    ylabel!("Consumo Estacionario (c̄)")
    xlims!(0.01, 0.95)

    plot(p1, size=(750, 500), legend=:bottom, legendfontsize=7)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
T_bench = 100
s_path = fill(0.20, T_bench); n_path = fill(0.02, T_bench); A_path = fill(1.0, T_bench)
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
