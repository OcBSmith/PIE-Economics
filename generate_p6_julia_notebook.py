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

nb.cells.append(nbf.v4.new_markdown_cell("""## Extensiones para ABP (Aprendizaje Basado en Proyectos)

1. **Shock de productividad**: introducir un shock de PTF ($A_t$) y comparar la dinámica de $q$ y $I$ con el shock de tipo de interés.
2. **Costes de ajuste asimétricos**: modificar la función de costes para que desinvertir sea más costoso que invertir y analizar el efecto sobre la velocidad de ajuste.
3. **Modelo con restricción de irreversibilidad**: añadir la restricción $I_t \\ge 0$ (no se puede desinvertir) y comparar con el modelo base."""))

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae todo el paquete X. "import X: y" solo trae el nombre y.
# Pkg.activate("../..") usa el entorno del repo; Pkg.instantiate() instala
# dependencias. MacroAIComp contiene la lógica del modelo Q de Tobin; Plots
# e Interact para visualización interactiva; BenchmarkTools para rendimiento.
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using NLsolve         # solver de sistemas no lineales
using Interact        # widgets interactivos (equivalente a ipywidgets)
using BenchmarkTools  # medición de rendimiento (Fase III)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

# --- CÁLCULO DEL ESTADO ESTACIONARIO Y ESTABILIDAD ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# CALCULO DEL ESTADO ESTACIONARIO, AUTOVALORES Y FORMULA DE SALTO
# ==============================================================================

# TobinQParams es un struct (definido en src/models/TobinQ.jl) con
# argumentos POSICIONALES: alpha, delta, phi, R (en ese orden, el orden
# importa). compute_steady_state() calcula el punto fijo; compute_
# linearized_system() obtiene la matriz A, autovalores y theta (pendiente
# del saddle path). En Julia los índices empiezan en 1: lambdas[1] es el
# primer autovalor. Al ejecutar veremos SS, estabilidad y theta comparado
# con theta_book — la diferencia debe ser < 1e-12 (son algebraicamente
# idénticas, igual que en Python).
params_ss = TobinQParams(0.35, 0.06, 10.0, 0.04)  # alpha, delta, phi, R
ss = compute_steady_state(params_ss)
lin_sys = compute_linearized_system(params_ss)

K_star = ss["K"]
q_star = ss["q"]
I_star = ss["I"]
lambdas = lin_sys["eigenvalues"]
theta_simple = lin_sys["theta"]
theta_book = get(lin_sys, "theta_book", theta_simple)

println("ESTADO ESTACIONARIO (R=0.04):")
println("-"^55)
println("  Q de Tobin (q*)               : ", round(q_star, digits=6))
println("  Stock de capital (K*)          : ", round(K_star, digits=6))
println("  Inversion (I* = delta*K*)      : ", round(I_star, digits=6))
println("  Produccion (Y* = K*^alpha)     : ", round(K_star^0.35, digits=6))
println()
println("ESTABILIDAD (log-desviaciones):")
println("-"^55)
println("  Autovalor estable lambda1      : ", round(lambdas[1], digits=6))
println("  Autovalor inestable lambda2    : ", round(lambdas[2], digits=6))
println("  Modulo |1+lambda1|             : ", round(abs(1+lambdas[1]), digits=6), "  (< 1, estable en niveles)")
println("  Modulo |1+lambda2|             : ", round(abs(1+lambdas[2]), digits=6), "  (> 1, inestable en niveles)")
println("  Clasificacion                  : Punto de silla")
println()
println("FORMULA DE SALTO:")
println("-"^55)
println("  theta (simplificada = phi*lambda1): ", theta_simple)
println("  theta_book (formula del libro)    : ", theta_book)
println("  Diferencia                        : ", abs(theta_simple - theta_book))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

# --- ASERCIÓN JULIA: SS, AUTOVALORES Y FORMULA DE SALTO ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACION: SS, AUTOVALORES Y FORMULA DE SALTO (Apendice K del libro)
# ==============================================================================

# isapprox(a, b; rtol=...) compara con tolerancia. @assert es PUNTO DE
# CONTROL silencioso. Verificamos: 1) q*=1, K*~6.87, I*=delta*K*.
# 2) lambda1~-0.0607 (estable, |1+lambda1|<1), lambda2~0.1072 (inestable)
# => punto de silla. 3) theta = theta_book para varias calibraciones.

# 1. Estado estacionario
@assert isapprox(q_star, 1.0; atol=1e-6)
@assert isapprox(K_star, 6.8711236; rtol=1e-6)
@assert isapprox(I_star, 0.06 * K_star; rtol=1e-6)
println("OK (SS 1/3): q*=1.0, K*~6.871, I*=delta*K*, coincide con el oraculo DYNARE.")

# 2. Autovalores (log-desviaciones)
@assert isapprox(lambdas[1], -0.060658; rtol=1e-4)
@assert isapprox(lambdas[2], 0.107158; rtol=1e-4)
@assert abs(1 + lambdas[1]) < 1.0 "lambda1 debe ser estable en niveles"
@assert abs(1 + lambdas[2]) > 1.0 "lambda2 debe ser inestable en niveles"
println("OK (SS 2/3): lambda1~-0.060658, lambda2~0.107158, punto de silla confirmado.")

# 3. Identidad de la formula de salto: theta = theta_book para varias calibraciones
for R_val in [0.02, 0.03, 0.04, 0.05]
    for phi_val in [5.0, 10.0, 15.0]
        p = TobinQParams(0.35, 0.06, phi_val, R_val)
        ls = compute_linearized_system(p)
        @assert abs(ls["theta"] - get(ls, "theta_book", ls["theta"])) < 1e-12 "theta != theta_book para R=$R_val, phi=$phi_val"
    end
end
println("OK (SS 3/3): theta = theta_book para todo R, phi (atol=1e-12).")
"""))

# --- ASERCIÓN JULIA: SHOCK DE TIPO DE INTERES ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACION DEL SHOCK: SALTO DE q, CONVERGENCIA Y CONSISTENCIA (Apendice K)
# ==============================================================================

# Cuatro verificaciones: 1) K0 es predeterminado (K* en R=4%). 2) q0 SALTA a
# ~1.1033 (>1.0) en t=1 (variable forward-looking). En Julia los índices
# empiezan en 1: res["q"][2] es el periodo del shock (t=1). 3) Convergencia
# a largo plazo: q -> 1.0, K -> K*(R=3%). 4) Lineal y no lineal consistentes
# (rtol=1e-2).

ss_R04 = compute_steady_state(params_ss, 0.04)
ss_R03 = compute_steady_state(params_ss, 0.03)
K_star_R04 = ss_R04["K"]
K_star_R03 = ss_R03["K"]

T_sim = 100
R_path = fill(0.03, T_sim)
R_path[1] = 0.04

K0_shock = ss_R04["K"]
res_nonlin = solve_nonlinear_simulation(params_ss, K0_shock, R_path, T_sim)
res_lin = solve_linearized_simulation(params_ss, K0_shock, R_path, T_sim)

# 1. K0 es predeterminado
@assert isapprox(K0_shock, K_star_R04; rtol=1e-6)
println("OK (Shock 1/4): K0 = K*(R=4%) = ", round(K0_shock, digits=6), ", predeterminado (sin salto).")

# 2. q0 salta por encima de 1.0
q0_jump = res_nonlin["q"][2]  # periodo del shock (t=1, indice 2 en Julia)
println("q0 (post-shock) = ", round(q0_jump, digits=6))
@assert q0_jump > 1.0 "q0 debe saltar por encima de 1.0 tras la caida de R"
@assert isapprox(q0_jump, 1.1033; rtol=1e-3)
println("OK (Shock 2/4): q0 ~ 1.1033 > 1.0, la inversion se estimula.")

# 3. Largo plazo: q -> 1.0, K -> K*(R=3%)
q_long_run = res_nonlin["q"][end]
K_long_run = res_nonlin["K"][end]
@assert isapprox(q_long_run, 1.0; atol=1e-4)
@assert isapprox(K_long_run, K_star_R03; rtol=1e-3)
println("q[T-1] = ", round(q_long_run, digits=6), " (esperado: 1.0)")
println("K[T-1] = ", round(K_long_run, digits=6), " (esperado: ", round(K_star_R03, digits=6), ")")
println("OK (Shock 3/4): Convergencia a nuevo SS en el largo plazo.")

# 4. Consistencia lineal vs no lineal
@assert isapprox(res_lin["K"], res_nonlin["K"]; rtol=1e-2)
@assert isapprox(res_lin["q"], res_nonlin["q"]; rtol=1e-2)
println("OK (Shock 4/4): Trayectorias lineal y no lineal consistentes (rtol=1e-2).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# @manipulate crea sliders y redibuja al moverlos. Al bajar R_final por
# debajo de R_init, veremos: Panel 1) q salta > 1.0 en t=1 y converge a
# 1.0. Panel 2) K crece gradualmente (no salta, es predeterminado). Panel
# 3) Inversión neta positiva mientras q>1, sombreado por encima de la
# depreciación. Cuanto mayor phi (costes de ajuste), más lenta la
# convergencia de K y menor el salto inicial de q.
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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal vs No Lineal. solve_linearized_simulation() usa la
# aproximación de Uhlig (1999) con theta; solve_nonlinear_simulation()
# resuelve el sistema exacto con fsolve. Al ejecutar, ambas trayectorias
# deberían superponerse casi perfectamente: la aproximación lineal es muy
# precisa para shocks moderados. plot!() (con "!") añade al gráfico
# existente: primero se dibuja la curva no lineal (lw=3, sólida) y luego
# la linealizada (ls=:dash, discontinua) encima.
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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_code_cell("""# Diagrama de Fases en el espacio de desviaciones logarítmicas (k_hat, q_hat).
# quiver!() dibuja el campo vectorial (normalizado para que todas las
# flechas tengan la misma longitud). scatter!() añade los puntos clave:
# rojo = SS inicial, naranja = salto de q, verde (star) = SS final. La
# trayectoria simulada (roja) recorre el saddle path desde el salto hasta el
# origen. Cualquier punto fuera del saddle path divergería: solo el salto
# EXACTO a q_hat_0 = theta * k_hat_0 garantiza la convergencia.
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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[8]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# @btime mide el tiempo mínimo de ejecución y la memoria asignada. Los "$"
# evitan que las variables se traten como globales (falsearía la medición).
# (Fase III del proyecto: rendimiento computacional, no economía.)
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
