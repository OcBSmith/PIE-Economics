import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\06-tobin-q\python.ipynb")
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
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock Tasa Interés
@manipulate for R_init in slider(0.01:0.005:0.08; value=0.04, label="R inicial"), R_final in slider(0.01:0.005:0.08; value=0.03, label="R final"), phi_val in slider(1.0:1.0:30.0; value=10.0, label="Costos Aj. (φ)"), delta_val in slider(0.01:0.01:0.15; value=0.06, label="Deprec. (δ)"), alpha_val in slider(0.20:0.05:0.50; value=0.35, label="Elasticidad (α)")
    
    params_base = TobinQParams(alpha_val, delta_val, phi_val, R_init)
    ss_init = compute_steady_state(params_base)
    K0 = ss_init["K"]
    T_sim = 100
    t_shock = 1
    
    R_path = fill(R_final, T_sim)
    R_path[1] = R_init
    
    res = solve_nonlinear_simulation(params_base, K0, R_path, T_sim)
    
    params_final = TobinQParams(alpha_val, delta_val, phi_val, R_final)
    ss_final = compute_steady_state(params_final)
    
    t_axis = 0:(T_sim - 1)
    
    # Panel 1: Q de Tobin
    p1 = plot(t_axis, res["q"], color="#7A3E9F", lw=2.5, label="Q (Valor de Mercado)")
    hline!([ss_init["q"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_final["q"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Ratio Q de Tobin")
    xlabel!("Período (t)")
    ylabel!("Ratio q")

    # Panel 2: Capital
    p2 = plot(t_axis, res["K"], color="#004C97", lw=2.5, label="Capital (K)")
    hline!([ss_init["K"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_final["K"]], color=:black, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Stock de Capital (K_t)")
    xlabel!("Período (t)")
    ylabel!("Capital (K)")

    # Panel 3: Inversión con depreciación y sombreado
    I_dep = delta_val .* res["K"]
    I_net = res["I"] .- I_dep
    p3 = plot(t_axis, res["I"], color="#D95319", lw=2.5, label="Inversión Bruta (I)")
    plot!(t_axis, I_dep, color=:red, ls=:dash, lw=1.5, label="Depreciación (δK)")
    plot!(t_axis, max.(I_net, 0.0), fillrange=0, color="#D95319", fillalpha=0.15, label="Inv. Neta (+)", lw=0)
    plot!(t_axis, min.(I_net, 0.0), fillrange=0, color=:red, fillalpha=0.15, label="Desinv. Neta (-)", lw=0)
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="I Inicial")
    hline!([ss_final["I"]], color=:black, ls=:dash, label="I Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Dinámica de Inversión")
    xlabel!("Período (t)")
    ylabel!("Inversión (I)")
    
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

p1 = plot(t_axis, res_nonlin["q"], label="No Lineal", color="#7A3E9F", lw=3)
plot!(t_axis, res_lin["q"], label="Linealizado", color="#7A3E9F", ls=:dash, lw=2)
title!("Comparación: Q de Tobin (q_t)")
xlabel!("Período (t)")
ylabel!("Ratio q")

p2 = plot(t_axis, res_nonlin["K"], label="No Lineal", color="#004C97", lw=3)
plot!(t_axis, res_lin["K"], label="Linealizado", color="#004C97", ls=:dash, lw=2)
title!("Comparación: Stock de Capital (K_t)")
xlabel!("Período (t)")
ylabel!("Capital (K)")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Diagrama de Fases en espacio de desviaciones logarítmicas
@manipulate for R_init in slider(0.01:0.005:0.08; value=0.04, label="R inicial"), R_final in slider(0.01:0.005:0.08; value=0.03, label="R final"), phi_val in slider(1.0:1.0:30.0; value=10.0, label="Costos Aj. (φ)"), delta_val in slider(0.01:0.01:0.15; value=0.06, label="Deprec. (δ)"), alpha_val in slider(0.20:0.05:0.50; value=0.35, label="Elasticidad (α)")
    params = TobinQParams(alpha_val, delta_val, phi_val, R_final)
    
    ss_init = compute_steady_state(params, R_init)
    K_ss_init = ss_init["K"]
    
    ss_final = compute_steady_state(params, R_final)
    K_ss_final = ss_final["K"]
    
    # Obtener coeficientes del sistema linealizado
    lin_sys = compute_linearized_system(params)
    A = lin_sys["A"]
    theta = lin_sys["theta"]
    
    # Crear rejilla en espacio de desviaciones logarítmicas
    k_min, k_max = -0.25, 0.25
    q_min, q_max = -0.15, 0.15
    k_vals_grid = range(k_min, k_max, length=50)
    q_vals_grid = range(q_min, q_max, length=50)
    
    # Campo vectorial
    k_grid = [k_i for k_i in k_vals_grid, _ in q_vals_grid]
    q_grid = [q_j for _ in k_vals_grid, q_j in q_vals_grid]
    dk_hat = A[2,1] .* q_grid .+ A[2,2] .* k_grid
    dq_hat = A[1,1] .* q_grid .+ A[1,2] .* k_grid
    
    # Normalizar flechas
    norm = sqrt.(dk_hat.^2 .+ dq_hat.^2)
    norm[norm .== 0.0] .= 1.0
    dk_hat_norm = dk_hat ./ norm .* 0.03
    dq_hat_norm = dq_hat ./ norm .* 0.03
    
    p1 = plot()
    quiver!(k_grid', q_grid', quiver=(dk_hat_norm', dq_hat_norm'), color=:lightgray, alpha=0.4, label="")
    
    # Loci (curvas de demarcación)
    hline!([0.0], color="#004C97", ls=:dash, lw=1.5, label="Delta k_hat = 0")
    
    slope_dq = -A[1,2] / A[1,1]
    k_line = collect(range(k_min, k_max, length=100))
    plot!(k_line, slope_dq .* k_line, color="#7A3E9F", ls=:dash, lw=1.5, label="Delta q_hat = 0")
    
    # Saddle Path
    plot!(k_line, theta .* k_line, color=:black, lw=2.5, label="Saddle Path")
    
    # Puntos clave del shock
    k_hat_0 = log(K_ss_init) - log(K_ss_final)
    q_hat_0 = theta * k_hat_0
    
    scatter!([k_hat_0], [0.0], color=:red, markersize=8, label="E.E. Inicial (Pre-shock)")
    scatter!([k_hat_0], [q_hat_0], color=:orange, markersize=8, label="Salto Inicial (Post-shock)")
    scatter!([0.0], [0.0], color=:green, markersize=10, marker=:star, label="E.E. Final (Nuevo)")
    
    # Flecha del salto instantáneo
    plot!([k_hat_0, k_hat_0], [0.0, q_hat_0], color=:darkred, ls=:dot, lw=2, arrow=:arrow, label="Salto (t=1)")
    
    # Simular trayectoria de desviaciones
    T_path = 40
    R_path = fill(R_final, T_path)
    R_path[1] = R_init
    res_sim = solve_linearized_simulation(params, K_ss_init, R_path, T_path)
    k_sim = log.(res_sim["K"]) .- log(K_ss_final)
    q_sim = log.(res_sim["q"])
    
    plot!(k_sim, q_sim, color=:red, lw=2, label="Trayectoria Dinámica")
    
    # Flechas direccionales sobre la trayectoria
    for i in 1:8:(T_path-2)
        plot!([k_sim[i], k_sim[i+2]], [q_sim[i], q_sim[i+2]], color=:red, lw=1.5, arrow=:arrow, label="")
    end
    
    xlims!(k_min, k_max)
    ylims!(q_min, q_max)
    vline!([0.0], color=:black, alpha=0.3, label="")
    hline!([0.0], color=:black, alpha=0.3, label="")
    
    title!("Diagrama de Fases y Transición Dinámica")
    xlabel!("Desviación del Capital (k̂ₜ)")
    ylabel!("Desviación del Valor q (q̂ₜ)")
    
    plot(p1, size=(700, 550), plot_title="Modelo Q de Tobin", top_margin=10mm)
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
