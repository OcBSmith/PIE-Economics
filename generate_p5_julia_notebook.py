import nbformat as nbf
import os
import json
import sys

sys.path.append('scratch')
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\05-gobierno-fiscal\python.ipynb")
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
using Optim
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params_lumpsum = default_calibration(FiscalPolicyParameters)
println("Parámetros Base: ", params_lumpsum)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Generar salario constante
W = fill(30.0, params_lumpsum.T)

# 1. Resolver con FOC
res_foc = solve_lump_sum_foc(params_lumpsum, W)

# 2. Optimización Directa
res_opt = solve_lump_sum_optim(params_lumpsum, W)

println("Diferencia media en Consumo: ", sum(abs.(res_foc["C"] .- res_opt["C"])) / params_lumpsum.T)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl (Impuestos Distorsionadores)
@manipulate for tauc_val in 0.0:0.05:0.50, tauw_val in 0.0:0.05:0.50, taur_val in 0.0:0.05:0.50, ret_opt in ["lump_sum", "government_spending"]
    
    is_lump_sum_return = (ret_opt == "lump_sum")
    params = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, tauc_val, tauw_val, taur_val, 0.0, 0.0, 0)
    W_sim = fill(30.0, params.T)
    res = solve_distortionary_foc(params, W_sim, is_lump_sum_return)
    
    t_axis = 0:(params.T - 1)
    
    # Panel 1: Consumo e Ingresos
    p1 = plot(t_axis, res["C"], color=:purple, lw=2.5, label="Consumo (C)")
    plot!(t_axis, res["W_L"], color=:forestgreen, lw=2.5, ls=:dash, label="Ingreso Neto")
    title!("Consumo e Ingreso Salarial")
    xlabel!("Periodo (t)")
    ylabel!("Bienes")
    
    # Panel 2: Oferta de Trabajo y Ocio
    p2 = plot(t_axis, res["L"], color=:red, lw=2.5, label="Trabajo (L)")
    plot!(t_axis, res["O"], color=:teal, lw=2.5, ls=:dot, label="Ocio (O=1-L)")
    ylims!(-0.05, 1.05)
    title!("Asignación del Tiempo")
    xlabel!("Periodo (t)")
    ylabel!("Fracción")
    
    # Panel 3: Activos
    p3 = plot(t_axis, res["B"], color=:steelblue, lw=2.5, label="Activos (B)")
    hline!([0.0], color=:black, ls=:dot, label="")
    plot!(t_axis, max.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color=:steelblue, lw=0, label="Ahorro")
    plot!(t_axis, min.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color=:orange, lw=0, label="Deuda")
    title!("Evolución de Activos")
    xlabel!("Periodo (t)")
    ylabel!("Riqueza Neta")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Efecto de Impuestos Distorsionadores", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl (Seguridad Social)
@manipulate for tau_ss_val in 0.0:0.04:0.50, t_star_val in 15:1:29
    
    params_ss = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, tau_ss_val, t_star_val)
    W_ss = zeros(params_ss.T)
    W_ss[1:params_ss.t_star] .= 10.0
    
    res = solve_social_security(params_ss, W_ss)
    
    t_axis = 0:(params_ss.T - 1)
    
    # Panel 1: Consumo e Ingresos Laborales
    p1 = plot(t_axis, res["C"], color=:purple, lw=2.5, label="Consumo Óptimo")
    plot!(t_axis, W_ss, color=:gray, lw=2.0, ls=:dash, label="Salario Bruto (W)")
    plot!(t_axis, res["W_net"], color=:forestgreen, lw=2.5, label="Ingreso Disponible")
    title!("Consumo e Ingresos")
    xlabel!("Periodo (t)")
    ylabel!("Bienes")
    
    # Panel 2: Activos
    p2 = plot(t_axis, res["B"], color=:steelblue, lw=2.5, label="Ahorro Privado (B)")
    plot!(t_axis, res["B_ss"], color=:orange, lw=2.5, label="Fondo SS (B_ss)")
    plot!(t_axis, res["B_total"], color=:black, lw=3.0, ls=:dashdot, label="Riqueza Total")
    hline!([0.0], color=:black, ls=:dot, label="")
    title!("Evolución de Riqueza")
    xlabel!("Periodo (t)")
    
    plot(p1, p2, layout=(1,2), size=(800, 350), 
         plot_title="Impacto del Sistema de Seguridad Social", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime solve_distortionary_foc($params_lumpsum, fill(30.0, $params_lumpsum.T), true)
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

dir_path = "practicas/05-gobierno-fiscal/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
