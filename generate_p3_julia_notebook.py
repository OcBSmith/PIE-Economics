import nbformat as nbf
import os
import json
import sys

# Load md extractor
sys.path.append('scratch')
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\03-consumo-ahorro\python.ipynb")
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

nb.cells.append(nbf.v4.new_code_cell("""params = default_calibration()
println("Parámetros: ", params)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Generar salario constante
W_const = generate_income_profile("constant", params.T)
println("W constante: ", W_const[1:5], "...")

res_foc = solve_foc_fsolve(params, W_const)
res_opt = solve_direct_optim(params, W_const)

println("Diferencia media entre FOC y Optim: ", sum(abs.(res_foc["C"] .- res_opt["C"])) / params.T)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl
@manipulate for beta_val in 0.90:0.01:0.99, R_val in -0.05:0.01:0.15, profile in ["constant", "increasing", "retirement"]
    
    params_interactive = ConsumptionSavingParameters(30, beta_val, R_val, 0.0)
    W = generate_income_profile(profile, params_interactive.T)
    res = solve_foc_fsolve(params_interactive, W)
    
    t_axis = 0:(params_interactive.T - 1)
    
    # Panel 1: Consumo e Ingresos
    p1 = plot(t_axis, res["C"], color=:purple, lw=2.5, label="Consumo (C)")
    plot!(t_axis, res["W"], color=:forestgreen, lw=2.5, ls=:dash, label="Ingreso (W)")
    title!("Consumo e Ingresos")
    xlabel!("Periodo (t)")
    ylabel!("Bienes")
    
    # Panel 2: Activos
    p2 = plot(t_axis, res["B"], color=:steelblue, lw=2.5, label="Activos (B)")
    hline!([0.0], color=:black, ls=:dot, label="")
    # Fill between (trick in Plots: fillrange=0)
    plot!(t_axis, max.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color=:steelblue, lw=0, label="Ahorro")
    plot!(t_axis, min.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color=:orange, lw=0, label="Deuda")
    title!("Evolución de Activos")
    xlabel!("Periodo (t)")
    ylabel!("Riqueza Neta")
    
    # Panel 3: Utilidad
    p3 = plot(t_axis, res["U"], color=:orange, lw=2.0, label="Utilidad")
    title!("Utilidad Descontada")
    xlabel!("Periodo (t)")
    ylabel!("Utilidad")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Decisión Óptima Intertemporal", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime solve_foc_fsolve($params, $W_const)
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

dir_path = "practicas/03-consumo-ahorro/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
