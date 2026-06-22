import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\05-gobierno-fiscal\python.ipynb")
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
using NLsolve
using Optim
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params_lumpsum = default_calibration(FiscalPolicyParameters)

# Glosario didáctico: descripción económica y símbolo de cada parámetro técnico
descriptions = Dict(
    "T" => "Duración del ciclo de vida [T]",
    "beta" => "Factor de descuento intertemporal [β]",
    "R" => "Tipo de interés real [R]",
    "gamma" => "Peso del consumo en la función de utilidad [γ]",
    "B0" => "Activos iniciales [B0]",
    "tauw" => "Tasa impositiva sobre el salario [τw]",
    "tauc" => "Tasa impositiva sobre el consumo [τc]",
    "taur" => "Tasa impositiva sobre las rentas del capital [τr]",
    "tau_ss" => "Cotización a la Seguridad Social [τss]",
    "t_star" => "Periodo de jubilación [t*]",
)

println("CALIBRACIÓN ECONÓMICA DE REFERENCIA (Valores base del Libro):")
println("="^75)
println(rpad("Variable", 12), " | ", rpad("Valor", 6), " | ", rpad("Descripción Económica", 50))
println("-"^75)
for field in fieldnames(typeof(params_lumpsum))
    name = string(field)
    value = getfield(params_lumpsum, field)
    desc = get(descriptions, name, "Parámetro del modelo")
    println("  ", rpad(name, 10), " | ", rpad(value, 6), " | ", rpad(desc, 50))
end
println("="^75)
"""))

nb.cells.append(nbf.v4.new_code_cell("""# Generar salario constante (calibración base: T=30, beta=0.97, R=0.05)
W = fill(10.0, params_lumpsum.T)

# Caso con impuesto de suma fija (tauw=0.40) y devolución de la recaudación (G=T)
params_tax = FiscalPolicyParameters(30, 0.97, 0.05, params_lumpsum.gamma, 0.0, 0.40, 0.0, 0.0, 0.0, 26)

# 1. Resolver caso base sin impuestos
params_no_tax = FiscalPolicyParameters(30, 0.97, 0.05, params_lumpsum.gamma, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
res_base = solve_non_distortionary(params_no_tax, W)

# 2. Resolver con impuestos de suma fija y devolución (Equivalencia Ricardiana)
res_tax = solve_non_distortionary(params_tax, W, true)

println("Diferencia media en Consumo (Equivalencia Ricardiana): ", sum(abs.(res_base["C"] .- res_tax["C"])) / params_lumpsum.T)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl (Impuestos Distorsionadores)
@manipulate for tauc_val in 0.0:0.05:0.50, tauw_val in 0.0:0.05:0.50, taur_val in 0.0:0.05:0.80, ret_opt in ["lump_sum", "government_spending"]

    is_lump_sum_return = (ret_opt == "lump_sum")
    params = FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, tauw_val, tauc_val, taur_val, 0.0, 0)
    W_sim = fill(100.0, params.T)
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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl (Seguridad Social)
@manipulate for tau_ss_val in 0.0:0.05:0.60, t_star_val in 15:1:29

    params_ss = FiscalPolicyParameters(30, 0.97, 0.05, 0.5, 0.0, 0.0, 0.0, 0.0, tau_ss_val, t_star_val)
    # Perfil salarial creciente: W_t = 10 + t durante la vida activa, 0 después
    W_ss = zeros(params_ss.T)
    W_ss[1:params_ss.t_star] .= 10.0 .+ (0:(params_ss.t_star - 1))

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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

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
