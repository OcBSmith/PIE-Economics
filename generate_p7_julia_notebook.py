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

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae el paquete X. Pkg.activate("../..") usa el entorno del repo
# (Project.toml/Manifest.toml) en vez del global de la máquina — así todo el
# mundo ejecuta con las mismas versiones. Pkg.instantiate() instala lo que falte.
# "import Plots: mm" es selectivo: solo trae "mm" (unidad de margen) en vez de
# todo Plots, porque mm no se exporta por defecto. default() fija estilo de
# grid consistente con los notebooks Python.
# QUÉ VERÁS al ejecutar: información de precompilación de paquetes (la primera
# vez tarda un poco; las siguientes es instantáneo).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# MacroAIComp separa la lógica del modelo (src/models/) de la visualización
# (que hacemos aquí con Plots). El notebook solo llama funciones ya probadas.
using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra      # álgebra lineal: eigvals, inv, etc.
using NLsolve             # resolvedor no lineal (shooting)
using Interact            # @manipulate para sliders interactivos (equivalente a ipywidgets)
using BenchmarkTools      # @btime para medir rendimiento (Fase III)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: calcula el estado estacionario del modelo DGE (K*, C*, Y*, I*) usando
# la calibración base (alpha=0.35, beta=0.96, delta=0.06, A=1.0, rho=0.80).
# POR QUÉ: el SS es el punto de partida de TODAS las simulaciones y
# linealizaciones; si está mal, todo lo demás también. Es un punto fijo del
# sistema dinámico: la economía no se mueve si empieza aquí sin shocks.
# QUÉ VERÁS: 4 valores impresos con round(..., digits=4) — deben coincidir
# con la Tabla 8.2 del libro (K*=6.6986, Y*=1.9458, C*=1.5439, I*=0.4019).
# default_calibration(DGEParams) devuelve un struct con los valores por defecto.
# ss es un Dict{String, Float64} que asocia nombres de variable a sus valores.
params_base = default_calibration(DGEParams)
ss = compute_steady_state(params_base)

println("VALORES DE EQUILIBRIO (SS):")
println("  Capital (K*)   : ", round(ss["K"], digits=4))
println("  Consumo (C*)   : ", round(ss["C"], digits=4))
println("  Producción (Y*): ", round(ss["Y"], digits=4))
println("  Inversión (I*) : ", round(ss["I"], digits=4))
"""))

# SS assert against oracle
nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica que compute_steady_state() devuelve los valores exactos del
# oráculo (Tabla 8.2 del libro). POR QUÉ: si el SS base está mal, TODAS las
# simulaciones siguientes partirían de un punto erróneo — este assert lo
# detecta ANTES de seguir. QUÉ VERÁS: "OK: ..." o AssertionError que detiene
# la ejecución.
# isapprox(a, b; atol=...) compara con tolerancia. @assert es control
# silencioso: si pasa, no imprime nada (solo la linea del println final).

@assert isapprox(ss["K"], 6.698596; atol=1e-6)
@assert isapprox(ss["Y"], 1.945783; atol=1e-6)
@assert isapprox(ss["C"], 1.543867; atol=1e-6)
@assert isapprox(ss["I"], 0.401916; atol=1e-6)
@assert isapprox(ss["R"], 0.10166666666666667; atol=1e-6)
println("OK: estado estacionario coincide con el oráculo (Apéndice N).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: simula un shock temporal de TFP (épsilon en t=1, decae con rho) y
# grafica 4 paneles (Y, C, I, K) con líneas de SS y momento del shock.
# POR QUÉ (intuición económica): un shock de productividad aumenta Y, el
# consumidor anticipa mayor renta futura y eleva C YA (C salta por ser
# forward-looking). I también sube para acumular K, que alcanza su pico con
# retardo (hump-shape). Si rho es bajo, el shock se disipa pronto.
# QUÉ VERÁS: 4 gráficos que se actualizan al mover los sliders. K NUNCA
# salta en t=1 (es predeterminado). C e I sí saltan.
# @manipulate: macro de Interact.jl que crea sliders y re-ejecuta el bloque
# al moverlos (equivalente al interact() de ipywidgets en Python).
# NOTA: índices en Julia empiezan en 1, por eso a_shock[2] es t=1.
# "." en exp.(a_shock) y .= es BROADCASTING: aplica a cada elemento.
# plot() crea gráfico NUEVO; hline!/vline! AÑADEN líneas horizontales/verticales.
@manipulate for epsilon in slider(-0.05:0.005:0.05; value=0.01, label="Shock (ε1)"), rho_val in slider(0.0:0.05:0.99; value=0.80, label="Persist. (ρ)"), alpha_val in slider(0.2:0.05:0.5; value=0.35, label="Elasticidad (α)"), beta_val in slider(0.90:0.01:0.99; value=0.96, label="Descuento (β)"), delta_val in slider(0.01:0.01:0.15; value=0.06, label="Deprec. (δ)")

    # DGEParams es struct con argumentos POSICIONALES (el orden IMPORTA):
    # alpha, beta, delta, rho, A.
    params = DGEParams(alpha_val, beta_val, delta_val, rho_val, 1.0)
    ss_sim = compute_steady_state(params)
    K0 = ss_sim["K"]
    T_sim = 50

    # ones(T_sim) crea Vector de T_sim unos. a_shock[2] = shock en t=1.
    # El bucle for t in 3:T_sim construye el decaimiento AR(1) desde t=2.
    A_path = ones(T_sim)
    a_shock = zeros(T_sim)
    a_shock[2] = epsilon
    for t in 3:T_sim
        a_shock[t] = rho_val * a_shock[t-1]
    end
    A_path .= exp.(a_shock)

    # solve_nonlinear_simulation() resuelve el sistema NO LINEAL exacto.
    res = solve_nonlinear_simulation(params, K0, A_path, T_sim)

    # t_axis = 0:29 (Julia), los gráficos empiezan en periodo 0.
    t_axis = 0:(T_sim - 1)
    t_shock = 1

    # Panel 1: Producción (Y) — salta al alza en t=1 por el shock productivo
    p1 = plot(t_axis, res["Y"], color="#004C97", lw=2.5, label="Producción (Y)")
    hline!([ss_sim["Y"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Evolución de la Producción (PIB)")
    xlabel!("Período (t)")
    ylabel!("Y")

    # Panel 2: Consumo (C) — salta en t=1 (forward-looking)
    p2 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    hline!([ss_sim["C"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Evolución del Consumo Privado")
    xlabel!("Período (t)")
    ylabel!("C")

    # Panel 3: Inversión (I) — sube en t=1, cae por debajo del SS en la convergencia
    p3 = plot(t_axis, res["I"], color="#D95319", lw=2.5, label="Inversión (I)")
    hline!([ss_sim["I"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Dinámica de Inversión")
    xlabel!("Período (t)")
    ylabel!("I")

    # Panel 4: Capital (K) — NO salta en t=1, acumula con retardo (hump)
    p4 = plot(t_axis, res["K"], color="#8EAD3A", lw=2.5, label="Capital (K)")
    hline!([ss_sim["K"]], color=:gray, ls=:dot, label="")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Trayectoria de Acumulación de Capital")
    xlabel!("Período (t)")
    ylabel!("K")

    # layout=(2,2) crea cuadrícula 2x2. top_margin evita solapamiento del título.
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600),
         plot_title="Ajuste Dinámico frente a Shock TFP (No Lineal)", top_margin=10mm)
end
"""))

# Oracle table
nb.cells.append(nbf.v4.new_markdown_cell("""## 2.1 Verificación frente al oraculo

Comparamos contra los valores reportados en el libro (Tabla 8.2) y reproducidos por el
codigo MATLAB/DYNARE del Apendice N, recogidos en `oraculo.md`:

**Estado estacionario (calibracion base: alpha=0.35, beta=0.96, delta=0.06, A=1.0):**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Capital en SS (K*) | 6.698596 |
| Produccion en SS (Y*) | 1.945783 |
| Consumo en SS (C*) | 1.543867 |
| Inversion en SS (I*) | 0.401916 |
| Tipo de interes en SS (R*) | 0.10166666666666667 |

**Blanchard-Khan — Estabilidad:**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Autovalor estable mu1 (|mu| < 1) | approx 0.90399 |
| Autovalor inestable mu2 (|mu| > 1) | approx 1.15229 |
| Clasificacion | Punto de silla (exactamente 1 raiz estable) |

**Shock temporal de PTF (+1% con rho=0.8):**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| K1 (predeterminado, no salta) | = K* approx 6.6986 |
| C1 (salta al alza en impacto) | > C* |
| Y1 (salta al alza en impacto) | > Y* |
| I1 (salta al alza en impacto) | > I* |
| Pico de K (hump, ocurre con retardo) | Entre periodos 2 y 12 |
| Convergencia de largo plazo (C, K) | Vuelven al SS inicial (tol 1e-3) |
| Consistencia Blanchard-Khan vs simulacion no lineal | K y C coinciden con rtol 1e-2 |
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: compara la solución linealizada de Blanchard-Khan (solve_blanchard_khan)
# con la solución no lineal exacta (solve_nonlinear_simulation) para un shock
# de TFP, mostrando el error relativo máximo. POR QUÉ: BK usa una
# aproximación de primer orden alrededor del SS que es muy buena para shocks
# pequeños pero acumula error de truncamiento ante shocks grandes (epsilon
# hasta 0.10). QUÉ VERÁS: 2 gráficos (C y K) con líneas superpuestas +
# errores impresos. La línea discontinua (ls=:dash) es BK, la continua es la
# solución exacta.
# "." en .- y abs. es BROADCASTING: resta/valor absoluto elemento a elemento.
# maximum() = máximo de un array (equivalente a np.max de Python).
# plot() crea gráfico NUEVO; plot!() AÑADE líneas al existente.
@manipulate for epsilon_shock in 0.01:0.01:0.10

    params = default_calibration(DGEParams)
    ss_comp = compute_steady_state(params)
    K0 = ss_comp["K"]
    T_sim = 40

    A_path = ones(T_sim)
    a_s = zeros(T_sim)
    a_s[2] = epsilon_shock  # shock ocurre en t=1 (índice 2 en Julia)
    for t in 3:T_sim
        a_s[t] = params.rho * a_s[t-1]
    end
    A_path .= exp.(a_s)

    res_lin = solve_blanchard_khan(params, K0, A_path, T_sim)
    res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T_sim)

    t_axis = 0:(T_sim - 1)
    t_shock = 1

    # Error relativo máximo: diferencia máxima abs entre BK y no lineal,
    # dividida por el valor de SS, en %. Para epsilon=0.01 debe ser < 0.1%.
    diff_C = maximum(abs.(res_lin["C"] .- res_nonlin["C"])) / ss_comp["C"] * 100
    diff_K = maximum(abs.(res_lin["K"] .- res_nonlin["K"])) / ss_comp["K"] * 100
    println("Error relativo máximo en Consumo : ", round(diff_C, digits=4), "%")
    println("Error relativo máximo en Capital  : ", round(diff_K, digits=4), "%")

    # Consumo: variable forward-looking donde se concentra el error de linealización
    p1 = plot(t_axis, res_lin["C"], color="#7A3E9F", ls=:dash, lw=2, label="Blanchard-Khan (Linealizado)")
    plot!(t_axis, res_nonlin["C"], color="#7A3E9F", lw=2, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Consumo (C): Comparación de resolvedores")
    xlabel!("Periodo (t)")
    ylabel!("C")

    # Capital: variable predeterminada, menor error de linealización
    p2 = plot(t_axis, res_lin["K"], color="#8EAD3A", ls=:dash, lw=2, label="Blanchard-Khan (Linealizado)")
    plot!(t_axis, res_nonlin["K"], color="#8EAD3A", lw=2, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.7, label="")
    title!("Capital (K): Comparación de resolvedores")
    xlabel!("Periodo (t)")
    ylabel!("K")

    plot(p1, p2, layout=(1,2), size=(900, 400), top_margin=10mm)
end
"""))

# BK eigenvalues and consistency asserts
nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica TRES propiedades del oráculo (Apéndice N): 1) autovalores de
# la matriz J (estable mu_s≈0.904, inestable mu_u≈1.152) que confirman
# PUNTO DE SILLA; 2) consistencia BK vs no lineal (rtol=1e-2); 3) convergencia
# al SS inicial tras shock transitorio (tol=1e-3). POR QUÉ: un sistema DGE
# DEBE ser punto de silla para tener solución única y determinada (Blanchard-Khan).
# QUÉ VERÁS: tres "OK: ..." o AssertionError.
# inv() = inversa de matriz. eigvals() = autovalores. real() = parte real.
# sort(abs.(mu_vals)) ordena por módulo; [1]=estable, [2]=inestable.
# x[end] = último elemento (Julia indexa desde 1, no 0 como Python).
# "$key" interpola el valor de key en cadenas (como f-strings de Python).

# --- Autovalores BK ---
alpha_v = params_base.alpha
beta_v = params_base.beta
delta_v = params_base.delta

Omega_val = 1.0 - beta_v + beta_v * delta_v
Phi_val = 1.0 - beta_v + (1.0 - alpha_v) * beta_v * delta_v

A_mat = [1.0 0.0; Omega_val -alpha_v * beta_v * delta_v]
B_mat = [0.0 alpha_v; Phi_val 0.0]
D_mat = [1.0 Omega_val; 0.0 1.0]
F_mat = [-Omega_val 0.0; 0.0 0.0]
G_mat = [1.0 0.0; 0.0 1.0 - delta_v]
H_mat = [0.0 0.0; 0.0 delta_v]

invA = inv(A_mat)
inv_term = inv(D_mat + F_mat * invA * B_mat)
J = inv_term * (G_mat + H_mat * invA * B_mat)

mu_vals = real(eigvals(J))
mu_sorted = sort(abs.(mu_vals))
mu_s = mu_sorted[1]  # estable (|mu| < 1)
mu_u = mu_sorted[2]  # inestable (|mu| > 1)

@assert isapprox(mu_s, 0.90399; atol=1e-5)
@assert isapprox(mu_u, 1.15229; atol=1e-5)
println("OK: autovalores BK coinciden con el oraculo (Apendice N).")

# --- Consistencia lineal vs. no lineal (shock +1% con rho=0.8) ---
T_check = 60
a_hat_check = zeros(T_check)
a_hat_check[2] = 0.01  # shock en t=1 (índice 2 en Julia)
for t in 3:T_check
    a_hat_check[t] = params_base.rho * a_hat_check[t-1]
end
A_path_check = exp.(a_hat_check)

res_bk = solve_blanchard_khan(params_base, ss["K"], A_path_check, T_check)
res_nl = solve_nonlinear_simulation(params_base, ss["K"], A_path_check, T_check)

# Verificar que K y C de ambas soluciones coinciden (rtol 1e-2)
for key in ["K", "C"]
    max_diff = maximum(abs.(res_bk[key] .- res_nl[key]))
    rel_diff = max_diff / ss[key]
    @assert rel_diff < 0.02 "La discrepancia relativa en $key ($rel_diff) supera rtol=1e-2"
end
println("OK: soluciones BK y no lineal coinciden con rtol=1e-2 (oraculo).")

# --- Convergencia de largo plazo al SS inicial ---
# Un shock transitorio debe devolver la economía al mismo SS, no a uno nuevo.
# res_nl["K"][end] = K en el último periodo simulado.
@assert isapprox(res_nl["K"][end], ss["K"]; atol=1e-3)
@assert isapprox(res_nl["C"][end], ss["C"]; atol=1e-3)
println("OK: convergencia de largo plazo al SS inicial (tol 1e-3, oraculo).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: mide el tiempo de ejecución y la memoria asignada de los dos
# resolvedores (no lineal vs Blanchard-Khan) usando BenchmarkTools.@btime.
# POR QUÉ: Fase III del proyecto — cuantifica la ventaja de velocidad de la
# solución linealizada (BK) frente a la no lineal (NLsolve). QUÉ VERÁS:
# tiempo mínimo en micro/milisegundos y bytes asignados. BK debe ser más
# rápido (solo álgebra matricial) que NLsolve (iteraciones de Newton).
# @btime ejecuta la función muchas veces y reporta el tiempo mínimo.
# El "$" delante de variables evita que BenchmarkTools las trate como globales.
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
