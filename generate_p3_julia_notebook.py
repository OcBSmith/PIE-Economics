import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\03-consumo-ahorro\python.ipynb")
nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[0]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[1]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Este cuaderno depende del paquete `MacroAIComp` (Project.toml/Manifest.toml
# en la raíz del repositorio). En MyBinder (ver docs/DESPLIEGUE_BINDER.md) y en
# tu entorno local, el kernel ya arranca dentro del repositorio clonado, así
# que la celda siguiente activa e instancia el proyecto automáticamente.
# Nota: Google Colab no soporta Julia de forma nativa desde un notebook .ipynb;
# para la versión Julia de esta práctica usa MyBinder.
"""
    )
)

nb.cells.append(
    nbf.v4.new_markdown_cell(
        """## Extensiones para ABP (Aprendizaje Basado en Proyectos)

1. **Elección de jubilación endógena**: permitir que el consumidor elija $t^*$ (edad de jubilación) además del perfil de consumo. Plantear como problema de optimización con variable discreta.
2. **Shock de renta transitorio vs permanente**: comparar la respuesta del consumo ante un shock que afecta a UN solo periodo vs uno que afecta a TODOS los periodos, verificando la teoría de la renta permanente.
3. **Restricción de liquidez**: añadir la restricción $B_t \\ge 0$ (no se permite endeudamiento) y comparar el perfil de consumo resultante con el caso irrestricto."""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        """# "using X" trae a este cuaderno todo el código público del paquete X, para
# no tener que reescribirlo. Pkg.activate("../..") usa el entorno del repo.
# Pkg.instantiate() instala lo que falte (la primera vez puede tardar).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# La lógica del modelo consumo-ahorro vive en src/models/ConsumptionSaving.jl
# dentro del paquete MacroAIComp. El notebook solo llama funciones ya
# probadas, no reimplementa ecuaciones de Euler ni el solver.
using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using Interact                 # widgets interactivos (sliders) para Jupyter
using BenchmarkTools           # medición de rendimiento (Fase III)
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Esta celda solo FIJA NÚMEROS (Capítulo 4 del libro): todavía no calcula
# nada. default_calibration(ConsumptionSavingParameters) devuelve un struct
# (definido en src/models/ConsumptionSaving.jl) con valores por defecto:
# T=30, beta=0.97, R=0.02. Al ejecutar veremos estos valores impresos como
# comprobación visual. La tasa de impaciencia theta se calcula como
# (1-beta)/beta: a menor beta (menos paciente), mayor theta.
params = default_calibration(ConsumptionSavingParameters)

println("CALIBRACIÓN ECONÓMICA BASE:")
println("-"^50)
println("  Duración del ciclo de vida (T)  : ", params.T, " periodos")
println("  Factor de descuento (beta)      : ", params.beta, " (equivale a theta ≈ ", round((1-params.beta)/params.beta*100, digits=2), "%)")
println("  Tasa de interés real (R)        : ", round(params.R*100, digits=2), "%")
println("-"^50)
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Esta celda RESUELVE el problema del consumidor por DOS métodos distintos
# y compara los resultados. generate_income_profile("constant", T) crea un
# array de T=30 periodos con salario W=10 en cada uno. solve_foc_fsolve()
# plantea el sistema de ecuaciones de Euler y lo resuelve con NLsolve.
# solve_direct_optim() maximiza directamente la suma de utilidades
# descontadas usando optimización convexa. Al ejecutar veremos que ambos
# métodos dan resultados numéricamente idénticos (diferencia < 1e-5).
# W_const[1:5] muestra SOLO los 5 primeros elementos del array para no
# llenar la pantalla con 30 números.

# Generar salario constante
W_const = generate_income_profile("constant", params.T)
println("W constante: ", W_const[1:5], "...")

res_foc = solve_foc_fsolve(params, W_const)
res_opt = solve_direct_optim(params, W_const)

println("-"^75)
println("  Consumo Inicial C(0) [fsolve]   : ", round(res_foc["C"][1], digits=6))
println("  Consumo Inicial C(0) [optim]    : ", round(res_opt["C"][1], digits=6))
println("  Consumo Final C(T-1) [fsolve]   : ", round(res_foc["C"][end], digits=6))
println("  Consumo Final C(T-1) [optim]    : ", round(res_opt["C"][end], digits=6))
println("  Activos Finales B(T-1) [fsolve] : ", res_foc["B"][end])
println("  Activos Finales B(T-1) [optim]  : ", res_opt["B"][end])
println("-"^75)

diferencia_max = maximum(abs.(res_foc["C"] .- res_opt["C"]))
println("Máxima diferencia absoluta en el consumo: ", diferencia_max)
if diferencia_max < 1e-5
    println("✅ ¡Los solucionadores son equivalentes numéricamente!")
else
    println("❌ Hay diferencias entre solucionadores.")
end
"""
    )
)

# ORACLE TABLE + ASSERT CELLS (Bloque A y B)
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2.1 Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y reproducidos por el
código MATLAB del Apéndice G (`referencia/consumption.m`), recogidos en
`oraculo.md`:

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Activos terminales $B_{T-1}$ (cualquier perfil) | 0.0 (tol. 1e-6) |
| Equivalencia fsolve vs optimización directa | $C$ y $B$ idénticos (rtol 1e-4) |
| Perfil creciente — $B_0$ | Negativo (endeudamiento juvenil) |
| Perfil creciente — pendiente de $C$ | Negativa ($\beta(1+R)<1$) |
| Perfil jubilación — pico de activos | $t=19$ (fin de vida laboral) |
| Perfil jubilación — activos en vida laboral | Positivos (acumulación) |
| $\beta=0.99$ — pendiente de $C$ | Positiva ($\beta(1+R)>1$) |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale."""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# Verificamos la condición terminal (B_{T-1}=0) y la equivalencia entre
# solvers contra el oráculo del Apéndice G (MATLAB) recogido en oraculo.md.
# @assert isapprox compara dos valores y SOLO lanza un error si la
# diferencia supera la tolerancia. No usamos "==" porque la aritmética con
# decimales casi nunca da resultados exactamente iguales (errores de redondeo
# internos). Si el port a Julia tuviera un error, esta celda lanzaría
# AssertionError y detendría la ejecución antes de seguir construyendo
# gráficos sobre un resultado incorrecto.

# Condición terminal: el consumidor no deja deudas ni herencias
@assert isapprox(res_foc["B"][end], 0.0; atol=1e-6)
@assert isapprox(res_opt["B"][end], 0.0; atol=1e-6)

# Equivalencia fsolve vs optimización directa: C y B deben ser idénticos
# (Julia usa isapprox con rtol para equivalencia relativa)
@assert isapprox(res_foc["C"], res_opt["C"]; rtol=1e-4, atol=1e-4)
@assert isapprox(res_foc["B"], res_opt["B"]; rtol=1e-4, atol=1e-4)
println("OK: coincide con el oráculo MATLAB (Apéndice G).")
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# @manipulate es el equivalente en Julia de interact() de Python: crea
# sliders y un dropdown y redibuja automáticamente cada vez que los mueves.
# El código dentro del bloque resuelve el modelo de consumo-ahorro con los
# valores de beta, R y perfil salarial que elijas y dibuja 3 paneles:
# (1) consumo C_t e ingreso W_t, (2) activos financieros B_t con áreas de
# ahorro (azul) y deuda (naranja), (3) utilidad descontada por periodo.
# Al mover los sliders verás en vivo cómo cambia el perfil de consumo.
@manipulate for beta_val in slider([0.90:0.01:0.99; 0.999]; value=0.97, label="Paciencia (β)"), R_val in slider(-0.05:0.01:0.15; value=0.02, label="Interés (R)"), profile in Widgets.dropdown(["constant", "increasing", "retirement"]; value="constant", label="Perfil Salarial")
    
    params_interactive = ConsumptionSavingParameters(30, beta_val, R_val, 0.0)
    W = generate_income_profile(profile, params_interactive.T)
    res = solve_foc_fsolve(params_interactive, W)
    
    t_axis = 0:(params_interactive.T - 1)
    
    # Panel 1: Consumo e Ingresos
    p1 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    plot!(t_axis, res["W"], color="#8EAD3A", lw=2.5, ls=:dash, label="Ingreso (W)")
    title!("Consumo e Ingresos a lo largo del Ciclo de Vida")
    xlabel!("Periodo (t)")
    ylabel!("Unidades de Bienes")
    
    # Panel 2: Activos
    p2 = plot(t_axis, res["B"], color="#004C97", lw=2.5, label="Activos (B)")
    hline!([0.0], color=:black, ls=:dot, label="")
    # Fill between (trick in Plots: fillrange=0)
    plot!(t_axis, max.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#004C97", lw=0, label="Ahorro")
    plot!(t_axis, min.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#D95319", lw=0, label="Deuda")
    title!("Evolución de Activos Financieros")
    xlabel!("Periodo (t)")
    ylabel!("Riqueza Neta")
    
    # Panel 3: Utilidad
    p3 = plot(t_axis, res["U"], color="#D95319", lw=2.0, label="Utilidad")
    title!("Utilidad Descontada por Periodo")
    xlabel!("Periodo (t)")
    ylabel!("Utilidad")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Decisión Óptima Intertemporal", top_margin=10mm)
end
"""
    )
)

# VERIFICACIÓN DE PERFILES DE INGRESO Y SENSIBILIDAD
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 4.1 Verificación de perfiles de ingreso y sensibilidad

Comprobamos contra el oráculo los resultados cualitativos y cuantitativos
para cada perfil de ingreso y el caso de sensibilidad $\beta=0.99$ (Apéndice G,
`oraculo.md`)."""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# Verificamos los casos adicionales del oráculo (Apéndice G):

# --- Perfil creciente: endeudamiento juvenil y pendiente negativa del consumo ---
W_inc = generate_income_profile("increasing", params.T)
res_inc = solve_foc_fsolve(params, W_inc)
@assert res_inc["B"][1] < 0 "B[1] debería ser negativo (endeudamiento juvenil) con perfil creciente, pero es $(res_inc["B"][1])"
# Pendiente de C negativa: C[1] > C[end] porque beta*(1+R) = 0.9894 < 1
@assert res_inc["C"][1] > res_inc["C"][end] "La pendiente del consumo debería ser negativa con beta=0.97, R=0.02"
@assert isapprox(res_inc["B"][end], 0.0; atol=1e-6)
println("  Perfil creciente: B[1]=", round(res_inc["B"][1], digits=4),
        " (negativo), C[1]=", round(res_inc["C"][1], digits=4),
        " > C[end]=", round(res_inc["C"][end], digits=4), " OK")

# --- Perfil jubilación: pico de activos en t=19 (índice 20 en Julia) ---
W_ret = generate_income_profile("retirement", params.T)
res_ret = solve_foc_fsolve(params, W_ret)
peak_idx = argmax(res_ret["B"])
@assert peak_idx == 20 "El pico de activos debería estar en t=19 (índice 20 en Julia), no en $(peak_idx)"
# Activos positivos durante la vida laboral (t < 20, índices 1:20 en Julia)
@assert all(res_ret["B"][1:20] .> 0) "Los activos deberían ser positivos durante la vida laboral"
@assert isapprox(res_ret["B"][end], 0.0; atol=1e-6)
println("  Perfil jubilación: pico de activos en t=", peak_idx - 1,
        ", activos positivos en vida laboral OK")

# --- Sensibilidad beta=0.99: pendiente del consumo positiva ---
params_beta99 = ConsumptionSavingParameters(30, 0.99, 0.02, 0.0)
W_c2 = generate_income_profile("constant", params_beta99.T)
res_beta99 = solve_foc_fsolve(params_beta99, W_c2)
@assert res_beta99["C"][1] < res_beta99["C"][end] "La pendiente del consumo debería ser positiva con beta=0.99 (beta*(1+R)=1.0098>1)"
@assert isapprox(res_beta99["B"][end], 0.0; atol=1e-6)
println("  beta=0.99: C[1]=", round(res_beta99["C"][1], digits=4),
        " < C[end]=", round(res_beta99["C"][end], digits=4),
        " (pendiente positiva) OK")

println("OK: todos los perfiles coinciden con el oráculo MATLAB (Apéndice G).")
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# @btime (BenchmarkTools.jl) ejecuta la función muchas veces y muestra el
# tiempo mínimo/medio de ejecución y la memoria asignada. El $ delante de
# params y W_const evita que BenchmarkTools las trate como globales, lo que
# falsearía la medición (Fase III). Al ejecutar veremos cuánto tarda Julia
# en resolver el sistema de 30 ecuaciones de Euler con NLsolve.
@btime solve_foc_fsolve($params, $W_const)
"""
    )
)

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

dir_path = "practicas/03-consumo-ahorro/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
