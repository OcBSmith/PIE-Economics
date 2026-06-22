import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\07-equilibrio-general-dinamico\python.ipynb")
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
using Interact
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""params_base = default_calibration(DGEParams)
ss = compute_steady_state(params_base)

println("VALORES DE EQUILIBRIO (SS):")
println("  Capital (K*)   : ", round(ss["K"], digits=4))
println("  Consumo (C*)   : ", round(ss["C"], digits=4))
println("  Producción (Y*): ", round(ss["Y"], digits=4))
println("  Inversión (I*) : ", round(ss["I"], digits=4))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock Tecnológico Transitorio
@manipulate for epsilon in slider(-0.05:0.005:0.05; value=0.01), rho_val in slider(0.0:0.05:0.99; value=0.80), alpha_val in 0.2:0.05:0.5, beta_val in 0.90:0.01:0.99
    
    params = DGEParams(alpha_val, beta_val, 0.05, rho_val, 1.0)
    ss_sim = compute_steady_state(params)
    K0 = ss_sim["K"]
    T_sim = 50
    
    # Path del TFP: shock ocurre en t=1 (índice 2 en Julia), igual que en Python
    A_path = ones(T_sim)
    a_shock = zeros(T_sim)
    a_shock[2] = epsilon
    for t in 3:T_sim
        a_shock[t] = rho_val * a_shock[t-1]
    end
    A_path .= exp.(a_shock)

    res = solve_nonlinear_simulation(params, K0, A_path, T_sim)

    t_axis = 0:(T_sim - 1)
    t_shock = 1

    p1 = plot(t_axis, res["Y"], color="#004C97", lw=2.5, label="Producción (Y)")
    hline!([ss_sim["Y"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Evolución de la Producción (PIB)")
    xlabel!("Período (t)")
    ylabel!("Y")

    p2 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    hline!([ss_sim["C"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Evolución del Consumo Privado")
    xlabel!("Período (t)")
    ylabel!("C")

    p3 = plot(t_axis, res["I"], color="#D95319", lw=2.5, label="Inversión (I)")
    hline!([ss_sim["I"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Dinámica de Inversión")
    xlabel!("Período (t)")
    ylabel!("I")

    p4 = plot(t_axis, res["K"], color="#8EAD3A", lw=2.5, label="Capital (K)")
    hline!([ss_sim["K"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Trayectoria de Acumulación de Capital")
    xlabel!("Período (t)")
    ylabel!("K")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste Dinámico frente a Shock TFP (No Lineal)", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal (Blanchard-Kahn) vs No Lineal
@manipulate for epsilon_shock in 0.01:0.01:0.10
    
    params = default_calibration(DGEParams)
    ss_comp = compute_steady_state(params)
    K0 = ss_comp["K"]
    T_sim = 40
    
    A_path = ones(T_sim)
    a_s = zeros(T_sim)
    a_s[2] = epsilon_shock  # shock ocurre en t=1 (índice 2 en Julia), igual que en Python
    for t in 3:T_sim
        a_s[t] = params.rho * a_s[t-1]
    end
    A_path .= exp.(a_s)

    # Resolver
    res_lin = solve_blanchard_khan(params, K0, A_path, T_sim)
    res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T_sim)

    t_axis = 0:(T_sim - 1)
    t_shock = 1

    # Error relativo máximo en Consumo y Capital
    diff_C = maximum(abs.(res_lin["C"] .- res_nonlin["C"])) / ss_comp["C"] * 100
    diff_K = maximum(abs.(res_lin["K"] .- res_nonlin["K"])) / ss_comp["K"] * 100
    println("Error relativo máximo en Consumo : ", round(diff_C, digits=4), "%")
    println("Error relativo máximo en Capital  : ", round(diff_K, digits=4), "%")

    p1 = plot(t_axis, res_lin["C"], color="#7A3E9F", ls=:dash, lw=2, label="Blanchard-Khan (Linealizado)")
    plot!(t_axis, res_nonlin["C"], color="#7A3E9F", lw=2, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Consumo (C): Comparación de resolvedores")
    xlabel!("Periodo (t)")
    ylabel!("C")

    p2 = plot(t_axis, res_lin["K"], color="#8EAD3A", ls=:dash, lw=2, label="Blanchard-Khan (Linealizado)")
    plot!(t_axis, res_nonlin["K"], color="#8EAD3A", lw=2, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Capital (K): Comparación de resolvedores")
    xlabel!("Periodo (t)")
    ylabel!("K")

    plot(p1, p2, layout=(1,2), size=(900, 400), top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation para No Lineal y Blanchard-Kahn
A_bench = ones(50)
A_bench[1] = exp(0.01)
a_bench = zeros(50); a_bench[1] = 0.01

println("Benchmark NLsolve (No Lineal):")
@btime solve_nonlinear_simulation($params_base, $ss["K"], $A_bench, 50)

println("Benchmark Blanchard-Kahn (Lineal):")
@btime solve_blanchard_khan($params_base, $ss["K"], $A_bench, 50)
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

dir_path = "practicas/07-equilibrio-general-dinamico/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
