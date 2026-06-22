import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\04-consumo-ocio\python.ipynb")
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

nb.cells.append(nbf.v4.new_code_cell("""params = default_calibration(ConsumptionLeisureParameters)

println("CALIBRACIÓN BASE DE REFERENCIA:")
println("-"^60)
println("  Lifespan (T)                     : ", params.T, " periodos")
println("  Factor de descuento (beta)       : ", params.beta, " (theta ≈ ", round((1-params.beta)/params.beta*100, digits=2), "%)")
println("  Peso del consumo en utilidad (γ) : ", round(params.gamma, digits=2))
println("  Tasa de interés real (R)         : ", round(params.R*100, digits=2), "%")
println("-"^60)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Salario constante exógeno de W = 30
W_base = fill(30.0, params.T)

# Resolución
res_foc = solve_foc_fsolve(params, W_base)
res_opt = solve_direct_optim(params, W_base)

println("Diferencia media en Consumo (FOC vs Optim): ", sum(abs.(res_foc["C"] .- res_opt["C"])) / params.T)
println("Diferencia media en Trabajo (FOC vs Optim): ", sum(abs.(res_foc["L"] .- res_opt["L"])) / params.T)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl
@manipulate for beta_val in slider([0.90:0.01:0.99; 0.999]; value=0.97), gamma_val in 0.10:0.05:0.90, R_val in -0.05:0.01:0.15, W_val in 10.0:5.0:100.0
    
    params_int = ConsumptionLeisureParameters(30, beta_val, gamma_val, R_val, 0.0)
    W = fill(W_val, params_int.T)
    res = solve_foc_fsolve(params_int, W)
    
    t_axis = 0:(params_int.T - 1)
    
    # Panel 1: Consumo e Ingresos
    p1 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    plot!(t_axis, res["W_L"], color="#8EAD3A", lw=2.5, ls=:dash, label="Ingreso (W·L)")
    title!("Consumo e Ingreso Salarial")
    xlabel!("Periodo (t)")
    ylabel!("Unidades de Bienes")
    
    # Panel 2: Oferta de Trabajo y Ocio
    p2 = plot(t_axis, res["L"], color="#E05A47", lw=2.5, label="Trabajo (L)")
    plot!(t_axis, res["O"], color="#3BB193", lw=2.5, ls=:dot, label="Ocio (O=1-L)")
    ylims!(-0.05, 1.05)
    title!("Asignación del Tiempo (Trabajo vs Ocio)")
    xlabel!("Periodo (t)")
    ylabel!("Fracción de Tiempo")
    
    # Panel 3: Activos
    p3 = plot(t_axis, res["B"], color="#004C97", lw=2.5, label="Activos (B)")
    hline!([0.0], color=:black, ls=:dot, label="")
    plot!(t_axis, max.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#004C97", lw=0, label="Acreedor")
    plot!(t_axis, min.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#D95319", lw=0, label="Deudor")
    title!("Evolución de Activos Financieros")
    xlabel!("Periodo (t)")
    ylabel!("Riqueza Neta")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Decisión de Consumo-Ocio Intertemporal", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime solve_foc_fsolve($params, $W_base)
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

dir_path = "practicas/04-consumo-ocio/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
