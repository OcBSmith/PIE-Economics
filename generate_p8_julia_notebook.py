import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\08-solow-swan\python.ipynb")
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

1. **Contabilidad del crecimiento (growth accounting)**: descomponer el crecimiento observado de una economía real (ej. España 1980-2020) en contribuciones del capital, trabajo y PTF usando la Cobb-Douglas calibrada.
2. **Convergencia $\\beta$ y $\\sigma$**: simular varias economías con distintos $k_0$ iniciales y verificar la convergencia condicional predicha por Solow-Swan.
3. **Extensión con capital humano**: añadir acumulación de capital humano $h_t$ al modelo (Mankiw-Romer-Weil) y analizar cómo cambia la velocidad de convergencia y la Regla de Oro."""))

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae el paquete X. Pkg.activate("../..") usa el entorno del repo
# (Project.toml) en vez del global. Pkg.instantiate() instala lo que falte.
# "import Plots: mm" trae solo mm (unidad de margen) sin exportar el resto.
# default() fija estilo de grid consistente con los notebooks Python.
# QUÉ VERÁS: información de precompilación de paquetes (lento la primera vez).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# MacroAIComp contiene el modelo de Solow-Swan en src/models/Growth.jl.
# El notebook solo llama funciones ya probadas, no reimplementa fórmulas.
using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using Interact            # @manipulate para sliders interactivos
using BenchmarkTools      # @btime para medir rendimiento (Fase III)
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: calcula el estado estacionario del modelo de Solow-Swan (k*, y*, c*,
# i*) usando la calibración base (alpha=0.35, s=0.20, A=1.0). POR QUÉ: el SS
# es el punto fijo de la dinámica de acumulación; si está mal, todas las
# simulaciones siguientes errarían. QUÉ VERÁS: 4 valores impresos que deben
# coincidir con la Tabla 9.3: k*=4.0946, y*=1.6378, c*=1.3103, i*=0.3276.
# default_calibration(SolowSwanParameters) devuelve struct con defaults.
# round.(x, digits=4) redondea para mostrar; el "." es broadcasting.
params_base = default_calibration(SolowSwanParameters)
ss = compute_solow_steady_state(params_base)

println("VALORES DE ESTADO ESTACIONARIO:")
println("  Capital por trabajador (k*)   : ", round(ss["k"], digits=4))
println("  Producción por trabajador (y*): ", round(ss["y"], digits=4))
println("  Consumo por trabajador (c*)   : ", round(ss["c"], digits=4))
println("  Inversión por trabajador (i*) : ", round(ss["i"], digits=4))
"""))

# SS assert against oracle
nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica que compute_solow_steady_state() devuelve los valores del
# oráculo (Tabla 9.3). POR QUÉ: si el SS base está mal, todas las simulaciones
# siguientes errarían. QUÉ VERÁS: "OK: ..." o AssertionError.
# isapprox(a, b; atol=...) compara con tolerancia. @assert es control
# silencioso. La calibración por defecto usa delta=0.08, n=0.0, que da
# delta+n=0.08, igual que el oráculo (delta=0.06, n=0.02).
# Los valores numéricos son idénticos en ambos casos.

@assert isapprox(ss["k"], 4.0946; atol=1e-4)
@assert isapprox(ss["y"], 1.6378; atol=1e-4)
@assert isapprox(ss["c"], 1.3103; atol=1e-4)
@assert isapprox(ss["i"], 0.3276; atol=1e-4)
println("OK: estado estacionario coincide con el oraculo (Apendice O).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: simula un shock estructural PERMANENTE en t=5 (ahorro s, demografía n
# o TFP A) en Solow-Swan y grafica 4 paneles: k, y, c, gy. POR QUÉ: el modelo
# de Solow predice que un aumento de s sacrifica consumo hoy (cae en t=5)
# pero eleva k, y y c a largo plazo. La tasa de crecimiento gy salta en el
# impacto pero vuelve a CERO (sin progreso técnico, no hay crecimiento
# per cápita en estado estacionario). QUÉ VERÁS: 4 gráficos que se actualizan
# al mover los sliders de @manipulate.
# NOTA: índices en Julia empiezan en 1, por eso s_path[6:end] aplica el
# shock desde t=5 (sexto elemento = periodo 5 con t_axis empezando en 0).
# fill(valor, N) crea un Vector de N copias del mismo valor.
# "." en .= es broadcasting de asignación: cambia cada elemento del rango.
# plot() crea gráfico NUEVO; hline!/vline! AÑADEN líneas.
@manipulate for s_final in slider(0.10:0.01:0.50; value=0.25, label="Ahorro (s)"), n_final in slider(0.00:0.005:0.05; value=0.02, label="Pob. (n)"), A_final in slider(0.5:0.1:2.0; value=1.00, label="TFP (A)")

    params_init = default_calibration(SolowSwanParameters)
    ss_init = compute_solow_steady_state(params_init)
    k0 = ss_init["k"]
    T_sim = 100

    # Shock PERMANENTE desde t=5 (índice 6 en Julia 1-based). fill() llena
    # con el valor inicial; .= sobrescribe desde t_shock+1 hasta el final.
    s_path = fill(params_init.s, T_sim)
    s_path[6:end] .= s_final

    n_path = fill(params_init.n, T_sim)
    n_path[6:end] .= n_final

    A_path = fill(params_init.A, T_sim)
    A_path[6:end] .= A_final

    # simulate_solow_swan() reproduce la ecuación de acumulación k[t+1] = f(k[t]).
    res = simulate_solow_swan(params_init, k0, s_path, n_path, A_path, T_sim)

    # Estado estacionario final hacia el que converge la economía.
    params_fin = SolowSwanParameters(params_init.alpha, params_init.delta, s_final, n_final, A_final)
    ss_fin = compute_solow_steady_state(params_fin)

    t_shock = 5
    t_axis = 0:(T_sim - 1)

    # Panel 1: Capital (k) — NO salta, acumula gradualmente hacia nuevo SS
    p1 = plot(t_axis, res["k"], color="#8EAD3A", lw=2.5, label="Capital (k)")
    hline!([ss_init["k"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["k"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Stock de Capital per cápita")
    xlabel!("Períodos")
    ylabel!("k")

    # Panel 2: Producción (y) — misma dinámica gradual que k
    p2 = plot(t_axis, res["y"], color="#004C97", lw=2.5, label="Renta (y)")
    hline!([ss_init["y"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["y"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Producción per cápita (PIB p.c.)")
    xlabel!("Períodos")
    ylabel!("y")

    # Panel 3: Consumo (c) — CAE en t=5 (sacrificio), supera SS inicial a largo plazo
    p3 = plot(t_axis, res["c"], color="#7A3E9F", lw=2.5, label="Consumo (c)")
    hline!([ss_init["c"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_fin["c"]], color=:red, ls=:dash, label="SS Final")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Consumo per cápita")
    xlabel!("Períodos")
    ylabel!("c")

    # Panel 4: Crecimiento (gy) — salta en impacto, vuelve a 0% en SS
    p4 = plot(t_axis, res["gy"], color="#D95319", lw=2.5, label="Crecimiento (gy)")
    vline!([t_shock], color=:grey, ls=:dot, alpha=0.5, label="")
    title!("Tasa de Crecimiento de la Producción per cápita (%)")
    xlabel!("Períodos")
    ylabel!("% de crecimiento")

    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600),
         plot_title="Ajuste hacia el Nuevo Estado Estacionario", top_margin=10mm)
end
"""))

# Oracle table
nb.cells.append(nbf.v4.new_markdown_cell("""## 2.1 Verificacion frente al oraculo

Comparamos contra los valores reportados en el libro (Tabla 9.3) y reproducidos por el
codigo MATLAB del Apendice O, recogidos en `oraculo.md`:

**Estado estacionario (calibracion base: alpha=0.35, s=0.20, delta=0.06, n=0.02, A=1.0):**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Capital per capita en SS (k*) | 4.0946 |
| Produccion per capita en SS (y*) | 1.6378 |
| Consumo per capita en SS (c*) | 1.3103 |
| Inversion per capita en SS (i*) | 0.3276 |

**Shock de ahorro s 0.20 -> 0.25:**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| k0 | Parte de k* inicial approx 4.0946 |
| Trayectoria de k | Creciente monotona hacia nuevo SS |
| c en impacto (cae por mayor ahorro) | c0 = 0.75 * y0 < c* inicial |
| Largo plazo: c_final | > c* inicial (el sacrificio compensa) |

**Regla de Oro:**

| Magnitud | Valor esperado (oraculo) |
|---|---|
| Tasa de ahorro que maximiza c* | s_gold = alpha = 0.35 |
| c* en s_gold | Maximo global de la curva c_bar(s) |
| c* en s=0.20 (infra-acumulacion) | < c*_gold |
| c* en s=0.50 (sobre-acumulacion) | < c*_gold |
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: dibuja la curva c_bar(s) — consumo de estado estacionario en función
# de la tasa de ahorro — marca el punto actual y el máximo (Regla de Oro
# en s_gold = alpha = 0.35). POR QUÉ: muestra que existe una tasa de ahorro
# óptima que maximiza el consumo de largo plazo. A la izquierda (s < alpha,
# infra-acumulación), ahorrar más eleva c futuro. A la derecha (s > alpha,
# sobre-acumulación), la economía es dinámicamente INEFICIENTE: podría
# consumir más hoy Y en el futuro reduciendo s. QUÉ VERÁS: curva en U
# invertida, punto rojo (ahorro actual), estrella verde (Regla de Oro),
# regiones sombreadas azul/rosa.
# range(inicio, fin, length=N) crea N puntos equiespaciados.
# [f(s_val) for s_val in s_grid] es una COMPREHENSIÓN DE ARRAY: evalúa f
# para cada elemento y devuelve un Vector con los resultados.
# plot!() AÑADE al gráfico existente. scatter!() añade puntos.
# "$(expr)" interpola el resultado de expr en cadenas.
@manipulate for s_current in slider(0.05:0.01:0.60; value=0.20, label="Tasa Ahorro")

    params = default_calibration(SolowSwanParameters)
    alpha_val = params.alpha

    # Malla de 100 tasas de ahorro para dibujar la curva suave.
    s_grid = range(0.01, 0.95, length=100)
    c_ss_grid = [compute_solow_steady_state(params, s_val)["c"] for s_val in s_grid]

    # Consumo en el ahorro actual y en la Regla de Oro (s = alpha).
    c_current = compute_solow_steady_state(params, s_current)["c"]
    c_gold = compute_solow_steady_state(params, alpha_val)["c"]

    p1 = plot(s_grid, c_ss_grid, color="#7A3E9F", lw=3, label="Consumo de Estado Estacionario (c̄)")

    # fillrange sombrea desde la línea hasta el valor dado; aquí crea las
    # regiones de infra y sobre-acumulación.
    plot!([0.01, alpha_val], [0.0, 0.0], fillrange=maximum(c_ss_grid) * 1.1, fillalpha=0.5,
          color="#E6F2FF", lw=0, label="Bajo-acumulación (Eficiente)")
    plot!([alpha_val, 0.95], [0.0, 0.0], fillrange=maximum(c_ss_grid) * 1.1, fillalpha=0.5,
          color="#FFE6E6", lw=0, label="Sobre-acumulación (Ineficiente)")

    # Punto rojo: dónde está la economía ahora con la s elegida.
    scatter!([s_current], [c_current], color=:red, markersize=6,
             label="Ahorro actual (s=$(round(s_current, digits=2)), c=$(round(c_current, digits=3)))")
    vline!([s_current], color=:red, ls=:dot, alpha=0.5, label="")
    hline!([c_current], color=:red, ls=:dot, alpha=0.5, label="")

    # Estrella verde: máximo de la curva = Regla de Oro (s = alpha).
    scatter!([alpha_val], [c_gold], color="#8EAD3A", markersize=10, marker=:star,
             label="Regla de Oro (s_gold=α=$(round(alpha_val, digits=2)), c_gold=$(round(c_gold, digits=3)))")
    vline!([alpha_val], color="#8EAD3A", ls=:dash, alpha=0.7, label="")
    hline!([c_gold], color="#8EAD3A", ls=:dash, alpha=0.7, label="")

    title!("La Regla de Oro: Consumo Estacionario vs. Tasa de Ahorro")
    xlabel!("Tasa de Ahorro (s)")
    ylabel!("Consumo Estacionario (c̄)")
    xlims!(0.01, 0.95)

    plot(p1, size=(750, 500), legend=:bottom, legendfontsize=7)
end
"""))

# Golden Rule assert
nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: verifica analíticamente la Regla de Oro: s_gold = alpha = 0.35, y c*
# en s_gold > c* en s=0.20 (infra-acumulación) y > c* en s=0.50 (sobre-
# acumulación). POR QUÉ: la Regla de Oro es un resultado analítico exacto
# (PMgK = delta + n); si no se cumpliera, habría un bug en el modelo.
# QUÉ VERÁS: dos "OK: ..." o AssertionError con mensaje explicativo.
# @assert condicion "mensaje": si la condición es false, lanza AssertionError
# con el mensaje. "$(expr)" interpola el resultado de expr en el mensaje.

alpha_gold = params_base.alpha
ss_gold = compute_solow_steady_state(params_base, alpha_gold)
ss_low = compute_solow_steady_state(params_base, 0.20)
ss_high = compute_solow_steady_state(params_base, 0.50)

@assert isapprox(alpha_gold, 0.35; atol=1e-6)
println("OK: s_gold = alpha = ", round(alpha_gold, digits=2))

@assert ss_gold["c"] > ss_low["c"] "c_gold=$(ss_gold["c"]) deberia ser > c_s020=$(ss_low["c"])"
@assert ss_gold["c"] > ss_high["c"] "c_gold=$(ss_gold["c"]) deberia ser > c_s050=$(ss_high["c"])"
println("OK: c_gold=", round(ss_gold["c"], digits=4), " > c_s020=", round(ss_low["c"], digits=4),
        " y c_gold > c_s050=", round(ss_high["c"], digits=4), " (oraculo, Apendice O).")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# QUÉ: mide el tiempo de ejecución y la memoria asignada de simulate_solow_swan
# usando BenchmarkTools.@btime. POR QUÉ: Fase III del proyecto — cuantifica
# la velocidad de Julia en la simulación de Solow-Swan. QUÉ VERÁS: tiempo
# mínimo en micro/milisegundos y bytes asignados para 100 periodos.
# @btime ejecuta la función repetidamente y reporta el tiempo mínimo.
# El "$" delante de variables evita que BenchmarkTools las trate como globales.
# fill(valor, N) crea Vector{Float64} de N copias de valor.
T_bench = 100
s_path = fill(0.20, T_bench); n_path = fill(0.02, T_bench); A_path = fill(1.0, T_bench)
@btime simulate_solow_swan($params_base, $ss["k"], $s_path, $n_path, $A_path, $T_bench)
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

dir_path = "practicas/08-solow-swan/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
