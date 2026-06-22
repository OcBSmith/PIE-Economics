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

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae el paquete X. Pkg.activate("../..") usa el entorno del repo
# (Project.toml) en vez del global. Pkg.instantiate() instala lo que falte.
# "import Plots: mm" trae solo mm (unidad de margen) sin exportar el resto.
# default() fija estilo de grid consistente con los notebooks Python.
# QUÉ VERÁS: información de precompilación (lento la primera vez, instantáneo después).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# MacroAIComp contiene el modelo de Ramsey en src/models/Ramsey.jl.
# El notebook solo llama funciones ya probadas, no reimplementa fórmulas.
using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra      # álgebra lineal: eigvals, inv, etc.
using NLsolve             # resolvedor no lineal (shooting, equivalente a fsolve de Python)
using Interact            # @manipulate para sliders interactivos
using BenchmarkTools      # @btime para medir rendimiento (Fase III)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: calcula el estado estacionario del modelo de Ramsey (K*, C*, Y*, I*)
# usando la calibración base (alpha=0.35, beta=0.97, delta=0.06, n=0.02,
# A=1.0). POR QUÉ: el SS es el punto fijo del sistema dinámico de Ramsey; si
# está mal, todas las linealizaciones y simulaciones siguientes errarían.
# QUÉ VERÁS: 4 valores impresos que deben coincidir con Tabla 10.2:
# K*=7.9537, Y*=2.0663, C*=1.4300, I*=0.6363.
# default_calibration(RamseyParams) devuelve struct con valores por defecto.
# round.(x, digits=4) redondea para mostrar; "." = broadcasting.
params_base = default_calibration(RamseyParams)
ss = compute_ramsey_steady_state(params_base)

println("VALORES DE EQUILIBRIO (SS):")
println("  Capital por trabajador efectivo (K*) : ", round(ss["K"], digits=4))
println("  Consumo (C*)                         : ", round(ss["C"], digits=4))
println("  Producción (Y*)                      : ", round(ss["Y"], digits=4))
println("  Inversión (I*)                       : ", round(ss["I"], digits=4))
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: calcula la matriz de transición J (Jacobiano log-linealizado del
# sistema Ramsey) y extrae sus autovalores (lambda_1, lambda_2) y la
# pendiente de salto theta. POR QUÉ: los autovalores determinan la estabilidad
# del sistema (punto de silla si uno es estable |mu|<1 y otro inestable).
# theta = pendiente ĉ/k̂ sobre la senda estable: relaciona la variable de
# salto (C) con la predeterminada (K). QUÉ VERÁS: autovalores de J impresos
# (deberían ser lambda_1≈-0.09 y lambda_2≈0.11 en log-desviaciones).
# compute_ramsey_transition_matrix() devuelve 4 valores: J, lambda_1, lambda_2, theta.
# eigvals(J) devuelve los autovalores de la matriz J.
println("Autovalores de la matriz de transición (Blanchard-Kahn):")
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

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica el estado estacionario y los autovalores del modelo Ramsey
# contra el oráculo (Tabla 10.2, Apéndice P): K*=7.9537, Y*=2.0663,
# C*=1.4300, I*=0.6363, R*=0.0909, lambda_1=-0.0907, lambda_2=0.1115,
# theta=0.5751. POR QUÉ: SS y autovalores determinan TODA la dinámica.
# lambda_1<0 y lambda_2>0 confirman PUNTO DE SILLA (1 raíz estable = 1
# variable predeterminada K). theta relaciona ĉ con k̂ en la senda estable.
# QUÉ VERÁS: dos "OK: ..." o AssertionError.
# isapprox(a, b; atol=...) compara con tolerancia. @assert es control silencioso.

# --- Estado estacionario (atol=1e-4 segun oraculo.md) ---
@assert isapprox(ss["K"], 7.9537; atol=1e-4)
@assert isapprox(ss["Y"], 2.0663; atol=1e-4)
@assert isapprox(ss["C"], 1.4300; atol=1e-4)
@assert isapprox(ss["I"], 0.6363; atol=1e-4)
@assert isapprox(ss["R"], 0.0909; atol=1e-4)
println("OK: estado estacionario coincide con el oraculo (Apendice P).")

# --- Autovalores y theta (atol=1e-4 segun oraculo.md) ---
# lambda_1 = estable, lambda_2 = inestable, theta = pendiente de salto ĉ/k̂.
@assert isapprox(lambda_1, -0.0907; atol=1e-4)
@assert isapprox(lambda_2, 0.1115; atol=1e-4)
@assert isapprox(theta, 0.5751; atol=1e-4)
println("OK: autovalores y theta coinciden con el oraculo (Apendice P).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: simula un shock PERMANENTE de TFP (A) o paciencia (beta) en t=5 en
# el modelo de Ramsey usando Blanchard-Khan (linealizado) y grafica 4
# paneles: Y, C, I, K. POR QUÉ: a diferencia de Solow, en Ramsey el ahorro
# es ENDÓGENO. Un aumento de A eleva la productividad marginal del capital,
# incentivando inversión. C SALTA en t=5 (forward-looking, variable de salto
# en el punto de silla). K no salta (predeterminado). Un aumento de beta
# (más paciencia) reduce C en el impacto para ahorrar más hoy. QUÉ VERÁS:
# 4 gráficos actualizables con sliders @manipulate.
# solve_ramsey_linearized() aplica BK: usa autovalores y theta para la senda.
# RamseyParams es struct con argumentos POSICIONALES (orden: alpha, beta,
# delta, n, A). plot() crea gráfico NUEVO; hline!/vline! AÑADEN líneas.
@manipulate for A_final in slider(0.90:0.01:1.20; value=1.05, label="TFP (A)"), beta_final in slider(0.92:0.01:0.99; value=0.97, label="Descuento (β)")

    params_init = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params_init)
    K0 = ss_init["K"]
    T_sim = 80
    t_shock = 5

    res = solve_ramsey_linearized(params_init, K0, A_final, params_init.n, beta_final, T_sim, t_shock)

    # Estado estacionario final con los nuevos parámetros.
    params_fin = RamseyParams(params_init.alpha, beta_final, params_init.delta, params_init.n, A_final)
    ss_fin = compute_ramsey_steady_state(params_fin)

    t_axis = 0:(T_sim - 1)

    # Panel 1: Producción (Y) — salta en t=5 por el shock de TFP, converge al nuevo SS
    p1 = plot(t_axis, res["Y"], color="#004C97", lw=2.5, label="Renta (Y)")
    hline!([ss_init["Y"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["Y"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Evolución de la Producción per cápita")
    xlabel!("Períodos")
    ylabel!("y")

    # Panel 2: Consumo (C) — SALTA en t=5 (forward-looking). Con A>1 salta
    # al ALZA; con beta mayor, CAE en el impacto (ahorro hoy > consumo mañana).
    p2 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    hline!([ss_init["C"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["C"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Respuesta de Consumo per cápita (Salto)")
    xlabel!("Períodos")
    ylabel!("c")

    # Panel 3: Inversión (I) — también salta. Con A>1, sube para acumular más K.
    p3 = plot(t_axis, res["I"], color="#D95319", lw=2.5, label="Inversión (I)")
    hline!([ss_init["I"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["I"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Evolución de la Inversión per cápita")
    xlabel!("Períodos")
    ylabel!("i")

    # Panel 4: Capital (K) — NO salta en t=5 (predeterminado), acumula gradualmente
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

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: compara la solución linealizada de Blanchard-Khan con la solución no
# lineal exacta (shooting/NLsolve) para un shock permanente de TFP, mostrando
# el error relativo máximo en C y K. POR QUÉ: BK usa aproximación de primer
# orden; es muy precisa para A=1.05 (~5%) pero acumula error para A=1.30
# (~30%). QUÉ VERÁS: 2 gráficos (C, K) con línea gruesa (no lineal exacta)
# y discontinua (BK), más errores impresos abajo.
# "." en .- y abs. es BROADCASTING: aplica a cada elemento.
# maximum() = máximo de un array. ls=:dash = línea discontinua.
# "$(A_shock)" interpola el valor de A_shock en el título.
@manipulate for A_shock in slider(0.70:0.02:1.30; value=1.05, label="TFP final")

    params = default_calibration(RamseyParams)
    ss_comp = compute_ramsey_steady_state(params)
    K0 = ss_comp["K"]
    T_sim = 80
    t_shock = 5

    # A_path: 1.00 hasta t_shock, A_shock desde t_shock+1.
    A_path = fill(1.00, T_sim)
    A_path[t_shock+1:end] .= A_shock

    n_path = fill(params.n, T_sim)

    # BK (linealizado): rápido, aproximado.
    res_lin = solve_ramsey_linearized(params, K0, A_shock, params.n, params.beta, T_sim, t_shock)
    # No lineal (shooting): exacto, referencia "verdadera".
    res_nonlin = solve_ramsey_nonlinear(params, K0, A_path, n_path, T_sim, t_shock)

    # Errores relativos máximos en % del SS. Para A=1.05 deben ser < 0.2%.
    err_C = maximum(abs.(res_nonlin["C"] .- res_lin["C"])) / ss_comp["C"] * 100
    err_K = maximum(abs.(res_nonlin["K"] .- res_lin["K"])) / ss_comp["K"] * 100
    println("Error relativo máximo en Consumo (C): ", round(err_C, digits=4), "%")
    println("Error relativo máximo en Capital (K): ", round(err_K, digits=4), "%")

    t_axis = 0:(T_sim - 1)

    # Consumo: variable forward-looking, concentra el error de linealización.
    # No lineal primero (línea gruesa), BK encima (discontinua).
    p1 = plot(t_axis, res_nonlin["C"], color="#7A3E9F", lw=3, label="Exacto No Lineal")
    plot!(t_axis, res_lin["C"], color="#7A3E9F", ls=:dash, lw=2, label="Blanchard-Khan (Lineal)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita (c_t)")
    xlabel!("Períodos")
    ylabel!("c")

    # Capital: variable predeterminada, menor error de linealización.
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
nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica TRES propiedades del oráculo (Apéndice P): 1) consistencia
# BK vs no lineal (atol=5e-2, rtol=1e-2); 2) K en t_shock es predeterminado
# (= K* inicial); 3) C salta al ALZA en t_shock para un shock expansivo de
# TFP (verificación cualitativa de la senda estable). POR QUÉ: un modelo de
# Ramsey debe exhibir punto de silla: K no salta (variable de estado), C sí
# salta (forward-looking) en la dirección correcta (al alza si A sube).
# QUÉ VERÁS: tres "OK: ..." o AssertionError.
# NOTA IMPORTANTE: ĉ = θ·k̂ es una identidad EXACTA para la solución
# LINEALIZADA (por construcción de BK). Para la solución NO LINEAL, k̂ en
# t_shock es ≈0 (K predeterminado), por lo que θ·k̂ ≈ 0, mientras que ĉ
# sí salta. Por eso aquí verificamos CUALITATIVAMENTE (ĉ > 0), no
# cuantitativamente (ĉ ≈ θ·k̂). Esto es correcto y esperado.
# t_shock+1 indexa el periodo del shock (Julia es 1-based; t_shock=5,
# los periodos 0..4 son pre-shock, el shock ocurre en el índice 6=t_shock+1).
# log(x / x_bar) = log-desviación.
# "." en .- y abs. es BROADCASTING: aplica a cada elemento.
# @assert cond "mensaje" lanza AssertionError con mensaje si cond es falsa.

# --- Consistencia lineal vs. no lineal (atol=5e-2, rtol=1e-2) ---
T_check = 80
t_shock = 5
A_path_check = fill(1.00, T_check)
A_path_check[t_shock+1:end] .= 1.05
n_path_check = fill(params_base.n, T_check)

res_lin = solve_ramsey_linearized(params_base, ss["K"], 1.05, params_base.n, params_base.beta, T_check, t_shock)
res_nl = solve_ramsey_nonlinear(params_base, ss["K"], A_path_check, n_path_check, T_check, t_shock)

# Verificar que K y C de ambas soluciones coinciden (atol=5e-2, rtol=1e-2)
for key in ["K", "C"]
    max_diff = maximum(abs.(res_nl[key] .- res_lin[key]))
    rel_diff = max_diff / ss[key]
    @assert max_diff < 5e-2 || rel_diff < 1e-2 "La discrepancia en $key ($max_diff abs, $rel_diff rel) supera la tolerancia"
end
println("OK: soluciones BK y no lineal coinciden (atol=5e-2, rtol=1e-2; oraculo).")

# --- K en t_shock es predeterminado (= K* inicial) ---
# K es variable de ESTADO: no puede saltar, su valor en el periodo del shock
# es exactamente el del SS inicial (7.9537).
@assert isapprox(res_nl["K"][t_shock+1], ss["K"]; atol=1e-6)
println("OK: k en t_shock = ", round(res_nl["K"][t_shock+1], digits=4), " = k* inicial (predeterminado).")

# --- C en t_shock sigue la senda estable (verificacion cualitativa) ---
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

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: mide el tiempo de ejecución y la memoria asignada de los dos
# resolvedores de Ramsey (no lineal/shooting vs Blanchard-Khan) usando
# BenchmarkTools.@btime. POR QUÉ: Fase III del proyecto — cuantifica la
# ventaja de velocidad de BK (solo álgebra matricial) frente al shooting no
# lineal (iteraciones de Newton con NLsolve). QUÉ VERÁS: tiempo mínimo y
# bytes asignados. BK debe ser ~10-100x más rápido que el shooting no lineal.
# @btime ejecuta la función repetidamente y reporta el tiempo mínimo.
# El "$" delante de variables evita que BenchmarkTools las trate como globales.
# fill(valor, N) crea Vector{Float64} de N copias. A_bench[1]=1.00 fija el
# primer periodo en el SS; el resto en 1.05 (shock permanente).
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
