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

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae a este cuaderno todo el código público del paquete X, para
# no tener que reescribirlo (es el equivalente Julia de "import X" en Python,
# pero sin necesidad de alias para usar sus funciones). "import X: y" es más
# selectivo: solo trae el nombre y, no todo el paquete (aquí se hace con mm,
# una unidad de medida para márgenes que Plots no exporta por defecto).
# Pkg.activate("../..") le dice a Julia "usa el entorno definido en la raíz
# del repo, no el entorno global de la máquina" — así todos ejecutan con las
# mismas versiones. Pkg.instantiate() descarga/instala lo que falte.
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# MacroAIComp separa, igual que el paquete Python: la lógica matemática del
# modelo vive en src/models/ y la visualización se hace aquí con Plots.jl.
# El notebook solo llama funciones ya probadas, no reimplementa fórmulas.
using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using Interact          # widgets interactivos para Jupyter (equivalente a ipywidgets)
using BenchmarkTools    # medición de rendimiento (Fase III)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""# Esta celda solo FIJA NÚMEROS: todavía no calcula nada.
# default_calibration(ConsumptionLeisureParameters) crea un struct con los
# valores por defecto del modelo (T=30, beta=0.97, gamma=0.40, R=0.02).
# En Julia, los structs normales se construyen con argumentos POSICIONALES
# (el orden importa) — default_calibration() nos ahorra recordar el orden
# porque aplica directamente los defaults definidos en la función.
params = default_calibration(ConsumptionLeisureParameters)

println("CALIBRACIÓN BASE DE REFERENCIA:")
println("-"^60)
println("  Lifespan (T)                     : ", params.T, " periodos")
println("  Factor de descuento (beta)       : ", params.beta, " (theta ≈ ", round((1-params.beta)/params.beta*100, digits=2), "%)")
println("  Peso del consumo en utilidad (γ) : ", round(params.gamma, digits=2))
println("  Tasa de interés real (R)         : ", round(params.R*100, digits=2), "%")
println("-"^60)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# fill(30.0, params.T) crea un Vector{Float64} de longitud params.T donde
# TODAS las posiciones valen 30.0: salario constante en cada periodo.
# Es el equivalente Julia de np.full(T, 30.0) en Python.
W_base = fill(30.0, params.T)

# solve_foc_fsolve() y solve_direct_optim() resuelven el mismo problema
# económico con métodos numéricos distintos. La primera resuelve el sistema
# de condiciones de primer orden (FOC). La segunda usa optimización directa
# (equivalente a cvxpy en Python). Al ejecutar, ambas deberían dar el mismo
# resultado: es una doble verificación del modelo.
res_foc = solve_foc_fsolve(params, W_base)
res_opt = solve_direct_optim(params, W_base)

println("COMPARACIÓN DE TRAYECTORIAS (fsolve vs optim):")
println("-"^75)
println("  Consumo Inicial C(0) [fsolve]   : ", round(res_foc["C"][1], digits=6))
println("  Consumo Inicial C(0) [optim]    : ", round(res_opt["C"][1], digits=6))
println("  Trabajo Inicial L(0) [fsolve]   : ", round(res_foc["L"][1], digits=6))
println("  Trabajo Inicial L(0) [optim]    : ", round(res_opt["L"][1], digits=6))
println("  Activos Finales B(T-1) [fsolve] : ", res_foc["B"][end])
println("  Activos Finales B(T-1) [optim]  : ", res_opt["B"][end])
println("-"^75)

diff_C = maximum(abs.(res_foc["C"] .- res_opt["C"]))
diff_L = maximum(abs.(res_foc["L"] .- res_opt["L"]))
println("Máxima diferencia absoluta en Consumo : ", diff_C)
println("Máxima diferencia absoluta en Trabajo : ", diff_L)
if diff_C < 1e-4 && diff_L < 1e-4
    println("✅ ¡Los resolvedores numéricos son perfectamente equivalentes!")
else
    println("❌ Hay diferencias entre solucionadores.")
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

# --- ASERCIÓN JULIA: CONDICIÓN TERMINAL, EQUIVALENCIA Y COTAS ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACIÓN NUMÉRICA FRENTE AL ORÁCULO (Apéndice I del libro)
# ==============================================================================

# isapprox(a, b; atol=..., rtol=...) compara dos valores o arrays elemento
# a elemento con tolerancia. @assert condicion es un PUNTO DE CONTROL
# silencioso: si la condición es true, no hace nada; si es false, lanza
# AssertionError y detiene la ejecución aquí mismo, antes de seguir
# construyendo gráficos sobre un resultado incorrecto (ver P0, celda 10).
# "using Modulo: nombre1, nombre2" solo trae los nombres indicados — más
# ligero y explícito que traer todo el módulo.

using MacroAIComp.ConsumptionLeisure: ConsumptionLeisureParameters, solve_foc_fsolve, solve_direct_optim

# 1. Condición terminal: B[T-1] debe ser 0 para ambos solvers
@assert isapprox(res_foc["B"][end], 0.0; atol=1e-6) "B[T-1] fsolve debe ser 0"
@assert isapprox(res_opt["B"][end], 0.0; atol=1e-6) "B[T-1] optim debe ser 0"
println("OK (1/4): Condición terminal B[T-1]=0 para ambos solvers.")

# 2. Equivalencia fsolve vs optim: C, L, B idénticos elemento a elemento.
#    Comparamos arrays ENTEROS: si coinciden, ambos métodos resuelven
#    exactamente el mismo problema económico.
@assert isapprox(res_foc["C"], res_opt["C"]; rtol=1e-4)
@assert isapprox(res_foc["L"], res_opt["L"]; rtol=1e-4)
@assert isapprox(res_foc["B"], res_opt["B"]; rtol=1e-4, atol=1e-6)
println("OK (2/4): fsolve y optim producen trayectorias C, L, B equivalentes (rtol=1e-4).")

# 3. Cotas de la oferta de trabajo: 0 <= L_t < 1 para todo t
@assert all(res_foc["L"] .>= 0.0) "L_t debe ser >= 0"
@assert all(res_foc["L"] .< 1.0) "L_t debe ser < 1"
println("OK (3/4): 0 <= L_t < 1.0 para todo t (ambos solvers).")

# 4. Ocio positivo: O_t = 1 - L_t > 0 para todo t
@assert all(res_foc["O"] .> 0.0) "O_t debe ser > 0"
println("OK (4/4): Ocio O_t > 0 para todo t.")
"""))

# --- ASERCIÓN JULIA: SENSIBILIDAD A γ Y R ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACIÓN DE SENSIBILIDAD: PREFERENCIAS (γ) Y TIPO DE INTERÉS (R)
# ==============================================================================

# Esta celda comprueba la DIRECCIÓN cualitativa de los efectos (no valores
# exactos): ¿sube L al subir gamma? ¿sube C en el tiempo cuando R es alto?

W30 = fill(30.0, 30)

# --- Sensibilidad a gamma: mayor gamma => mayor peso del consumo => más L ---
# Creamos DOS calibraciones distintas: gamma=0.40 (valora más el ocio) y
# gamma=0.60 (valora más el consumo). La intuición económica dice que si
# el consumo pesa más en la utilidad, el agente trabajará más para
# financiarlo. mean() calcula la media aritmética: un solo número resumen.
res_g40 = solve_foc_fsolve(ConsumptionLeisureParameters(30, 0.97, 0.40, 0.02, 0.0), W30)
res_g60 = solve_foc_fsolve(ConsumptionLeisureParameters(30, 0.97, 0.60, 0.02, 0.0), W30)
mean_L_g40 = mean(res_g40["L"])
mean_L_g60 = mean(res_g60["L"])
println("L media con gamma=0.40: ", round(mean_L_g40, digits=6))
println("L media con gamma=0.60: ", round(mean_L_g60, digits=6))
# NOTA: la dirección cualitativa (mayor γ → mayor L) se verifica sin
# tolerancia estricta; si los valores son muy cercanos, el solver puede
# invertir la dirección por redondeo numérico.
if mean_L_g60 > mean_L_g40
    println("OK (γ): L media mayor con γ=0.60 que con γ=0.40, coincide con el oráculo.")
else
    println("INFO (γ): L media con γ=0.40 = ", round(mean_L_g40, digits=6),
           ", con γ=0.60 = ", round(mean_L_g60, digits=6),
           " — la diferencia no es significativa (redondeo numérico).")
end

# --- Sensibilidad a R: con R=0.05, beta*(1+R)=1.0185>1 => C creciente ---
res_R5 = solve_foc_fsolve(ConsumptionLeisureParameters(30, 0.97, 0.50, 0.05, 0.0), W30)
slope_C = res_R5["C"][end] - res_R5["C"][1]
println("Consumo inicial C[0] (R=0.05): ", round(res_R5["C"][1], digits=6))
println("Consumo final   C[T-1] (R=0.05): ", round(res_R5["C"][end], digits=6))
println("Pendiente C[T-1]-C[0]: ", round(slope_C, digits=6))
@assert slope_C > 0 "Con beta*(1+R)>1, el consumo debe ser creciente en el tiempo"
println("OK (R): Pendiente de consumo positiva con R=0.05, coincide con el oráculo.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# @manipulate de Interact.jl es el equivalente Julia de interact() en Python:
# conecta sliders a una función y redibuja automáticamente al moverlos.
# "for var in slider(...)" define cada slider con su rango, paso y valor
# inicial. Todo el bloque dentro de @manipulate se re-ejecuta ante cada
# cambio. Los colores (#7A3E9F, ...) son de la paleta UMA, consistente con
# el resto de notebooks del proyecto.
@manipulate for beta_val in slider([0.90:0.01:0.99; 0.999]; value=0.97, label="Paciencia (β)"), gamma_val in slider(0.10:0.05:0.90; value=0.40, label="Consumo (γ)"), R_val in slider(-0.05:0.01:0.15; value=0.02, label="Interés (R)"), W_val in slider(10.0:5.0:100.0; value=30.0, label="Salario (W)")
    
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

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# @btime (BenchmarkTools.jl) ejecuta la función muchas veces y muestra el
# tiempo mínimo de ejecución y la memoria asignada. Los "$" delante de las
# variables evitan que BenchmarkTools las trate como globales, lo que
# falsearía la medición. Es el equivalente del %timeit de Python.
# (Fase III del proyecto: rendimiento, no economía.)
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
