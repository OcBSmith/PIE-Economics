import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\02-overshooting-dornbusch\python.ipynb")
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

nb.cells.append(nbf.v4.new_code_cell("""params_sim = default_calibration(DornbuschParams)

# Glosario didáctico: descripción económica y símbolo de cada parámetro técnico
descriptions = Dict(
    "psi" => "Sensibilidad de la demanda de dinero respecto al PIB [ψ]",
    "theta" => "Sensibilidad de la demanda de dinero respecto al interés nominal [θ]",
    "beta1" => "Sensibilidad de la demanda agregada respecto al tipo de cambio real [β1]",
    "beta2" => "Sensibilidad de la demanda agregada respecto al interés nominal [β2]",
    "mi" => "Velocidad de ajuste de precios ante excesos de demanda (Phillips) [μ]",
    "beta0" => "Demanda agregada autónoma base [β0]",
    "m0" => "Oferta monetaria nominal (logaritmo) [M0]",
    "ypot0" => "Producción potencial (pleno empleo) [ypot]",
    "pstar0" => "Logaritmo del nivel de precios extranjero [pstar]",
    "istar0" => "Tipo de interés nominal extranjero (porcentaje) [istar]",
)

println("CALIBRACIÓN ECONÓMICA DE REFERENCIA (Valores base del Libro):")
println("="^78)
println(rpad("Variable", 12), " | ", rpad("Valor", 6), " | ", rpad("Descripción Económica", 50))
println("-"^78)
for field in fieldnames(typeof(params_sim))
    name = string(field)
    value = getfield(params_sim, field)
    desc = get(descriptions, name, "Parámetro del modelo")
    println("  ", rpad(name, 10), " | ", rpad(value, 6), " | ", rpad(desc, 50))
end
println("="^78)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""ss_init = steady_state(params_sim)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Precios nacionales (p*)    : ", ss_init["p"])
println("  Tipo de cambio nominal (s*): ", ss_init["s"])
println("  Tipo de interés (i*)       : ", ss_init["i"], "%")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Función explicativa que simula paso a paso la dinámica de Dornbusch en
# diferencias, equivalente didáctico de `simulate_dornbusch_manual` en Python.
# z = [beta0, m, ypot, istar, pstar] (vector de variables exógenas)
function simulate_dornbusch_manual(params, z_init, z_final, periods=30, shock_period=1)
    # 1. Obtener autovalores de la matriz del sistema para identificar el autovalor estable
    lambdas_m = eigenvalues(params)
    stable_idx_m = argmin(abs.(lambdas_m .+ 1.0))
    stable_lambda_m = lambdas_m[stable_idx_m]  # lambda1 (aprox -0.74)

    # 2. Inicializar arrays de trayectorias
    p = zeros(periods)
    s = zeros(periods)

    # Calcular estados estacionarios
    p_ss_init = z_init[2] - params.psi * z_init[3] + params.theta * z_init[4]
    s_ss_final = (
        z_final[2]
        - z_final[1] / params.beta1
        + ((1.0 - params.psi * params.beta1) / params.beta1) * z_final[3]
        + ((params.theta * params.beta1 + params.beta2) / params.beta1) * z_final[4]
        - z_final[5]
    )

    # Periodo inicial: Estado estacionario inicial
    p[1] = p_ss_init
    s[1] = z_init[2] - z_init[1]/params.beta1 + ((1.0 - params.psi*params.beta1)/params.beta1)*z_init[3] + ((params.theta*params.beta1 + params.beta2)/params.beta1)*z_init[4] - z_init[5]

    # Evolución temporal paso a paso
    for t in 2:periods
        if t == shock_period + 1
            # Precios rígidos a corto plazo
            p[t] = p[t - 1]
            # Salto del tipo de cambio al stable path (Overshooting)
            m_1 = z_final[2]
            ypot_1 = z_final[3]
            istar_1 = z_final[4]
            s[t] = (
                -(m_1 - p[t] - params.psi * ypot_1) / (params.theta * stable_lambda_m)
                - istar_1 / stable_lambda_m
                + s_ss_final
            )
        else
            # Propagación estándar para periodos posteriores usando las ecuaciones del sistema
            z_curr = t >= shock_period + 1 ? z_final : z_init
            i_prev = -(z_curr[2] - p[t-1] - params.psi * z_curr[3]) / params.theta
            yd_prev = z_curr[1] + params.beta1 * (s[t-1] - p[t-1] + z_curr[5]) - params.beta2 * i_prev
            dp_prev = params.mi * (yd_prev - z_curr[3])
            ds_prev = i_prev - z_curr[4]

            p[t] = p[t-1] + dp_prev
            s[t] = s[t-1] + ds_prev
        end
    end

    return p, s
end

# Verificación: comparamos la simulación manual contra el resolvedor de la
# biblioteca para el mismo shock monetario que usa el diagrama de fases.
p_manual, s_manual = simulate_dornbusch_manual(params_sim, [500.0, 100.0, 2000.0, 3.0, 0.0], [500.0, 101.0, 2000.0, 3.0, 0.0], 30, 1)
res_lib = simulate_shock(params_sim, [500.0, 100.0, 2000.0, 3.0, 0.0], [500.0, 101.0, 2000.0, 3.0, 0.0], 30, 1)
max_err_p = maximum(abs.(p_manual .- res_lib["p"]))
max_err_s = maximum(abs.(s_manual .- res_lib["s"]))
println("Función de simulación manual registrada con éxito.")
println("Diferencia máxima vs simulate_shock(): p -> ", max_err_p, ", s -> ", max_err_s)
@assert max_err_p < 1e-8 && max_err_s < 1e-8
"""))

nb.cells.append(nbf.v4.new_code_cell("""# Autovalores
lambdas = eigenvalues(params_sim)
println("Autovalores: ", lambdas)
stable_idx = argmin(abs.(lambdas .+ 1.0))
stable_lambda = lambdas[stable_idx]
println("Autovalor estable: ", stable_lambda)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con diagrama de fases
@manipulate for m0_val in slider(98.0:0.5:104.0; value=101.0, label="Dinero (M)"), beta0_val in slider(450.0:10.0:550.0; value=500.0, label="Gasto (B0)")
    
    z_initial = [500.0, 100.0, 2000.0, 3.0, 0.0]
    z_final = [beta0_val, m0_val, 2000.0, 3.0, 0.0]
    periods = 30
    
    # Calcular nuevos parámetros con z_final
    params_final = DornbuschParams(params_sim.theta, params_sim.psi, params_sim.beta1, 
                                 params_sim.beta2, params_sim.mi, 
                                 beta0_val, m0_val, 2000.0, 3.0, 0.0)
    ss_final = steady_state(params_final)
    
    res = simulate_shock(params_sim, z_initial, z_final, periods, 1)
    
    # Panel 1: Dinámica Temporal p y s
    t_axis = 0:(periods-1)
    p1 = plot(t_axis, res["s"], color="#7A3E9F", lw=2.5, label="Tipo cambio (s)")
    plot!(t_axis, res["p"], color="#8EAD3A", lw=2.5, label="Precios (p)")
    hline!([ss_init["s"]], color="#7A3E9F", ls=:dot, label="s Inicial")
    hline!([ss_final["s"]], color="#7A3E9F", ls=:dash, label="s Final")
    hline!([ss_init["p"]], color="#8EAD3A", ls=:dot, label="p Inicial")
    hline!([ss_final["p"]], color="#8EAD3A", ls=:dash, label="p Final")
    vline!([1], color=:red, ls=:dash, label="Shock (t=1)")
    title!("Trayectorias Temporales (s y p)")
    xlabel!("Tiempo (t)")
    ylabel!("Escala Logarítmica")
    
    # Panel 2: Interés y Demanda Agregada
    p2 = plot(t_axis, res["i"], color="#004C97", lw=2.0, label="Interés (i)")
    plot!(t_axis, res["yd"], color="#D95319", lw=2.0, label="Demanda (yd)")
    hline!([z_final[4]], color="#004C97", ls=:dash, label="i*")
    hline!([z_final[3]], color="#D95319", ls=:dash, label="ypot")
    vline!([1], color=:red, ls=:dash, label="")
    title!("Tipos de Interés y Demanda Agregada")
    xlabel!("Tiempo (t)")
    
    # Panel 3: Diagrama de Fases
    p3 = plot(res["p"], res["s"], color="#7A3E9F", lw=3, label="Trayectoria dinámica")
    vline!([ss_final["p"]], color="#004C97", ls=:dash, lw=2, label="ds = 0 (Final)")
    vline!([ss_init["p"]], color="#004C97", ls=:dot, label="ds = 0 (Inicial)")
    
    p_vals = range(minimum(res["p"]) - 0.5, maximum(res["p"]) + 0.5, length=100)
    slope_dp = 1.0 + params_sim.beta2 / (params_sim.theta * params_sim.beta1)
    c_locus_init = ss_init["s"] - slope_dp * ss_init["p"]
    c_locus_final = ss_final["s"] - slope_dp * ss_final["p"]
    
    s_locus_init = c_locus_init .+ slope_dp .* p_vals
    s_locus_final = c_locus_final .+ slope_dp .* p_vals
    
    plot!(p_vals, s_locus_init, color="#8EAD3A", ls=:dot, label="dp = 0 (Inicial)")
    plot!(p_vals, s_locus_final, color="#8EAD3A", ls=:dash, lw=2, label="dp = 0 (Final)")
    
    a_mat, _ = coefficient_matrices(params_sim)
    k_slope = (stable_lambda - a_mat[1,1]) / a_mat[1,2]
    saddle_final = ss_final["s"] .+ k_slope .* (p_vals .- ss_final["p"])
    plot!(p_vals, saddle_final, color=:black, ls=:dashdot, label="Saddle Path")
    
    p_grid = range(minimum(res["p"]) - 0.3, maximum(res["p"]) + 0.3, length=10)
    s_grid = range(minimum(res["s"]) - 0.5, maximum(res["s"]) + 0.5, length=10)
    
    # Normalización uniforme: la longitud de cada flecha es la misma fracción
    # (5%) del rango de su propio eje, evitando una escala arbitraria distinta
    # entre p y s.
    arrow_frac = 0.05
    p_range = maximum(p_grid) - minimum(p_grid)
    s_range = maximum(s_grid) - minimum(s_grid)

    p_pts, s_pts, dp_pts, ds_pts = Float64[], Float64[], Float64[], Float64[]
    for pp in p_grid, ss in s_grid
        i_pt = -(z_final[2] - pp - params_sim.psi * z_final[3]) / params_sim.theta
        yd_pt = z_final[1] + params_sim.beta1 * (ss - pp + z_final[5]) - params_sim.beta2 * i_pt
        dp = params_sim.mi * (yd_pt - z_final[3])
        ds = i_pt - z_final[4]

        norm = sqrt(dp^2 + ds^2)
        if norm > 0
            push!(p_pts, pp); push!(s_pts, ss)
            push!(dp_pts, (dp/norm)*arrow_frac*p_range); push!(ds_pts, (ds/norm)*arrow_frac*s_range)
        end
    end
    quiver!(p_pts, s_pts, quiver=(dp_pts, ds_pts), color=:gray, alpha=0.5)
    
    scatter!([ss_init["p"]], [ss_init["s"]], color=:gray, markersize=6, label="EE Inic")
    scatter!([ss_final["p"]], [ss_final["s"]], color=:black, marker=:star, markersize=8, label="EE Fin")

    # Salto instantáneo del tipo de cambio en el periodo del shock (t=0 -> t=1)
    plot!([res["p"][1], res["p"][2]], [res["s"][1], res["s"][2]], color="#7A3E9F", lw=2, arrow=:closed, label="")
    annotate!(res["p"][1] - 0.15, (res["s"][1] + res["s"][2]) / 2, text("Jump", "#7A3E9F", :bold, 9))

    title!("Plano de Fases (p, s)")
    xlabel!("Precios (p)")
    ylabel!("Tipo de cambio (s)")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Respuesta del modelo Dornbusch", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_code_cell("""@assert isapprox(ss_init["p"], 1.5; atol=1e-6)
@assert isapprox(ss_init["s"], 76.5150; atol=1e-6)
println("OK: coincide con el oráculo.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[8]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# Benchmark simulation
@btime simulate_shock($params_sim, [500.0, 100.0, 2000.0, 3.0, 0.0], [500.0, 101.0, 2000.0, 3.0, 0.0], 30, 1)
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

dir_path = "practicas/02-overshooting-dornbusch/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
