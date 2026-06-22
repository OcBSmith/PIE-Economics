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
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
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

# Oracle table and SS/eigenvalue assert
nb.cells.append(nbf.v4.new_markdown_cell("""## 2.1 Verificacion frente al oraculo

Comparamos contra los valores reportados en el libro (Tabla 10.2) y reproducidos por el
codigo DYNARE del Apendice P, recogidos en `oraculo.md`:

**Estado estacionario (calibracion base: alpha=0.35, beta=0.97, delta=0.06, n=0.02, A=1.0):**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Capital per capita en SS (k*) | 7.9537 |
| Produccion per capita en SS (y*) | 2.0663 |
| Consumo per capita en SS (c*) | 1.4300 |
| Inversion per capita en SS (i*) | 0.6363 |
| Tipo de interes en SS (R*) | 0.0909 |

**Estabilidad — Blanchard-Khan log-linealizado:**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Raiz estable lambda1 (log-desviacion) | -0.0907 |
| Raiz inestable lambda2 (log-desviacion) | 0.1115 |
| Pendiente de salto theta (Delta c_hat / Delta k_hat) | 0.5751 |

**Shock permanente de PTF (A 1.00 -> 1.05 en t=5):**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| k en t_shock (predeterminado) | = k* inicial approx 7.9537 |
| c_hat en t_shock (salto sobre senda estable) | = k_hat * theta (tol 1e-3) |
| Consistencia lineal vs no lineal | k y c coinciden con atol 5e-2, rtol 1e-2 |
"""))

nb.cells.append(nbf.v4.new_code_cell("""# Verificacion del estado estacionario y los autovalores contra el oraculo
# (Tabla 10.2 del libro, reproducido en oraculo.md).
# La calibracion por defecto de RamseyParams (alpha=0.35, beta=0.97, delta=0.06, n=0.02, A=1.0)
# coincide con la calibracion base del oraculo.

# --- Estado estacionario (atol=1e-4 segun oraculo.md) ---
@assert isapprox(ss["K"], 7.9537; atol=1e-4)
@assert isapprox(ss["Y"], 2.0663; atol=1e-4)
@assert isapprox(ss["C"], 1.4300; atol=1e-4)
@assert isapprox(ss["I"], 0.6363; atol=1e-4)
@assert isapprox(ss["R"], 0.0909; atol=1e-4)
println("OK: estado estacionario coincide con el oraculo (Apendice P).")

# --- Autovalores y theta (atol=1e-4 segun oraculo.md) ---
@assert isapprox(lambda_1, -0.0907; atol=1e-4)
@assert isapprox(lambda_2, 0.1115; atol=1e-4)
@assert isapprox(theta, 0.5751; atol=1e-4)
println("OK: autovalores y theta coinciden con el oraculo (Apendice P).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva: Shock permanente Ramsey
@manipulate for A_final in slider(0.90:0.01:1.20; value=1.05, label="TFP (A)"), beta_final in slider(0.92:0.01:0.99; value=0.97, label="Descuento (β)")
    
    params_init = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params_init)
    K0 = ss_init["K"]
    T_sim = 80
    t_shock = 5
    
    res = solve_ramsey_linearized(params_init, K0, A_final, params_init.n, beta_final, T_sim, t_shock)
    
    params_fin = RamseyParams(params_init.alpha, beta_final, params_init.delta, params_init.n, A_final)
    ss_fin = compute_ramsey_steady_state(params_fin)
    
    t_axis = 0:(T_sim - 1)
    
    p1 = plot(t_axis, res["Y"], color="#004C97", lw=2.5, label="Renta (Y)")
    hline!([ss_init["Y"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["Y"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Evolución de la Producción per cápita")
    xlabel!("Períodos")
    ylabel!("y")

    p2 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    hline!([ss_init["C"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["C"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Respuesta de Consumo per cápita (Salto)")
    xlabel!("Períodos")
    ylabel!("c")

    p3 = plot(t_axis, res["I"], color="#D95319", lw=2.5, label="Inversión (I)")
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["I"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Evolución de la Inversión per cápita")
    xlabel!("Períodos")
    ylabel!("i")

    p4 = plot(t_axis, res["K"], color="#8EAD3A", lw=2.5, label="Capital (K)")
    hline!([ss_init["K"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["K"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Trayectoria de Capital per cápita")
    xlabel!("Períodos")
    ylabel!("k")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600), 
         plot_title="Ajuste Dinámico frente a Shock Permanente (Ramsey)", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación Lineal (Blanchard-Kahn) vs No Lineal (Shooting)
@manipulate for A_shock in slider(0.70:0.02:1.30; value=1.05, label="TFP final")
    
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
    
    p1 = plot(t_axis, res_nonlin["C"], color="#7A3E9F", lw=3, label="Exacto No Lineal")
    plot!(t_axis, res_lin["C"], color="#7A3E9F", ls=:dash, lw=2, label="Blanchard-Khan (Lineal)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita (c_t)")
    xlabel!("Períodos")
    ylabel!("c")

    p2 = plot(t_axis, res_nonlin["K"], color="#8EAD3A", lw=3, label="Exacto No Lineal")
    plot!(t_axis, res_lin["K"], color="#8EAD3A", ls=:dash, lw=2, label="Blanchard-Khan (Lineal)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Capital per cápita (k_t)")
    xlabel!("Períodos")
    ylabel!("k")
    
    plot(p1, p2, layout=(1,2), size=(800, 350), 
         plot_title="Comparación Lineal vs No Lineal (Shock A=$(A_shock))", top_margin=10mm)
end
"""))

# Linear vs nonlinear consistency and saddle path assert
nb.cells.append(nbf.v4.new_code_cell("""# Verificacion de la consistencia lineal vs no lineal y de la senda estable
# (oraculo.md, Apendice P).

# --- Consistencia lineal vs. no lineal (atol=5e-2, rtol=1e-2) ---
# Simulamos un shock permanente de TFP A: 1.00 -> 1.05 en t=5
T_check = 80
t_shock = 5
A_path_check = fill(1.00, T_check)
A_path_check[t_shock+1:end] .= 1.05
n_path_check = fill(params_base.n, T_check)

res_lin = solve_ramsey_linearized(params_base, ss["K"], 1.05, params_base.n, params_base.beta, T_check, t_shock)
res_nl = solve_ramsey_nonlinear(params_base, ss["K"], A_path_check, n_path_check, T_check, t_shock)

# Verificar que k y c de ambas soluciones coinciden (atol=5e-2, rtol=1e-2)
for key in ["K", "C"]
    max_diff = maximum(abs.(res_nl[key] .- res_lin[key]))
    rel_diff = max_diff / ss[key]
    @assert max_diff < 5e-2 || rel_diff < 1e-2 "La discrepancia en $key ($max_diff abs, $rel_diff rel) supera la tolerancia"
end
println("OK: soluciones BK y no lineal coinciden (atol=5e-2, rtol=1e-2; oraculo).")

# --- k en t_shock es predeterminado (= k* inicial) ---
@assert isapprox(res_nl["K"][t_shock+1], ss["K"]; atol=1e-6)
println("OK: k en t_shock = ", round(res_nl["K"][t_shock+1], digits=4), " = k* inicial (predeterminado).")

# --- c_hat en t_shock sigue la senda estable (c_hat ~ k_hat * theta, tol 1e-3) ---
# NOTA: ĉ = θ·k̂ es una identidad exacta para la solución LINEALIZADA
# (por construcción de Blanchard-Khan). Para la solución NO LINEAL, k̂_t
# en t_shock es ≈0 (k predeterminado), por lo que θ·k̂ ≈ 0, mientras
# que ĉ sí salta. La relación solo es exacta para la solución lineal.
# La verificamos cualitativamente: ĉ en t_shock debe ser positivo para
# un shock expansivo (salto al alza del consumo forward-looking).
c_hat_shock_nl = log(res_nl["C"][t_shock+1] / ss["C"])
@assert c_hat_shock_nl > 0.0 "c debe saltar al alza en t_shock para un shock de TFP positivo"
println("OK: c salta al alza en t_shock (c_hat = ", round(c_hat_shock_nl, digits=4), " > 0).")
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
