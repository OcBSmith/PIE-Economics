import nbformat as nbf
import os
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\01-is-lm-dinamico\python.ipynb")
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

1. **Política monetaria con regla de Taylor**: sustituir la oferta monetaria fija por una regla $i = i^* + \\phi_\\pi (P - P^*) + \\phi_Y (Y - Y^*)$ y analizar cómo cambia la estabilidad del sistema según $\\phi_\\pi, \\phi_Y$.
2. **Comparación de métodos numéricos**: simular el mismo shock con RK45, Radau y BDF y comparar tiempos de ejecución y precisión (error respecto al SS analítico).
3. **Shock combinado**: aplicar un shock monetario expansivo y uno fiscal contractivo simultáneamente para mantener $Y$ constante. ¿Es posible? ¿Qué implicaciones tiene para el policy mix?"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        """# "using X" trae a este cuaderno todo el código público del paquete X, para
# no tener que reescribirlo (es el equivalente Julia de "import X" en
# Python, pero sin necesidad de poner un alias para usar sus funciones).
# Pkg.activate("../..") le dice a Julia "usa el entorno (versiones de
# librerías) definido en Project.toml/Manifest.toml de la raíz del repo, no
# el entorno global de la máquina" — así todo el mundo ejecuta con las
# mismas versiones. Pkg.instantiate() descarga/instala lo que falte de ese
# entorno (la primera vez puede tardar; las siguientes es instantáneo).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# La lógica del modelo (ecuaciones, simulación, estado estacionario) vive en
# src/models/ISLM.jl dentro del paquete MacroAIComp. El notebook solo llama
# funciones ya probadas, no reimplementa fórmulas.
using MacroAIComp
using Plots
# "import Plots: mm" es más selectivo que "using Plots": solo trae el nombre
# "mm" (una unidad de medida para márgenes) en vez de todo el paquete, que
# ya importamos en la línea anterior.
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using DifferentialEquations    # integración numérica de ODEs (equivalente a scipy.integrate)
using Interact                 # widgets interactivos (sliders) para Jupyter
using BenchmarkTools           # medición de rendimiento (Fase III)
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Esta celda solo FIJA NÚMEROS (Apéndice D del libro): todavía no calcula
# nada. default_calibration(ISLMParams) devuelve un ISLMParams, un struct
# (definido en src/models/ISLM.jl): una "ficha" con 8 campos con nombre
# (theta, psi, beta1, mi, ni, beta0, m0, ypot0), como el dataclass de
# Python. Usar default_calibration() evita escribir los números a mano y
# posibles errores de tecleo: los valores están centralizados en el código
# fuente y testeados. Al ejecutar veremos los 8 valores impresos con su
# descripción económica como comprobación visual.
params = default_calibration(ISLMParams)

# Glosario didáctico: descripción económica y símbolo de cada parámetro técnico
descriptions = Dict(
    "theta" => "Sensibilidad de la demanda de dinero al tipo de interés nominal [θ]",
    "psi" => "Sensibilidad de la demanda de dinero a la renta real (PIB) [ψ]",
    "beta1" => "Sensibilidad de la inversión y consumo al tipo de interés real [β1]",
    "mi" => "Ajuste de precios ante brecha de producción (Curva de Phillips) [μ]",
    "ni" => "Velocidad de ajuste de la producción física en mercado de bienes [ν]",
    "beta0" => "Demanda agregada autónoma base (Gasto público + Consumo base) [β0]",
    "m0" => "Oferta monetaria nominal fijada por el Banco Central [M0]",
    "ypot0" => "Producción potencial de pleno empleo a largo plazo [Y_barra]",
)

println("CALIBRACIÓN ECONÓMICA DE REFERENCIA (Valores base del Libro):")
println("="^75)
println(rpad("Variable", 12), " | ", rpad("Valor", 6), " | ", rpad("Descripción Económica", 50))
println("-"^75)
for field in fieldnames(typeof(params))
    name = string(field)
    value = getfield(params, field)
    desc = get(descriptions, name, "Parámetro del modelo")
    println("  ", rpad(name, 10), " | ", rpad(value, 6), " | ", rpad(desc, 50))
end
println("="^75)
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# steady_state() es una FUNCIÓN: le pasamos los parámetros (params) y nos
# devuelve un diccionario con los valores de equilibrio de largo plazo
# (Y, P, i, Yd, dP, dY). Por dentro resuelve las condiciones dY/dt = 0,
# dP/dt = 0 usando las fórmulas analíticas derivadas en la Sección 2 del
# notebook: Y* = ypot0 (producción potencial), i* = (beta0 - Y*)/beta1,
# P* = theta*i* + m0 - psi*Y*. No necesitamos saber CÓMO lo calcula para
# usarla: solo qué entra y qué sale.
# round(ss["i"], digits=2) redondea SOLO para imprimir más corto; el valor
# real guardado en la variable no cambia. println() imprime texto en la
# consola (como print() en Python).
ss = steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Renta de pleno empleo (Y*) : ", ss["Y"])
println("  Nivel de precios (P*)      : ", ss["P"])
println("  Tipo de interés (i*)       : ", round(ss["i"], digits=2), "%")
println("  Demanda agregada (Yd*)     : ", ss["Yd"])
"""
    )
)

# Reemplazar la referencia a scipy en la celda 4
md_4 = (
    md_cells[4]
    .replace("`scipy.integrate.solve_ivp`", "`DifferentialEquations.jl`")
    .replace("Python", "Julia")
)
nb.cells.append(nbf.v4.new_markdown_cell(md_4))

# Mostramos el system_dynamics en Julia como se hacía en Python con def
nb.cells.append(
    nbf.v4.new_code_cell(
        """# Esta celda DEFINE (no ejecuta) la función custom_system_dynamics!(), el
# "motor" del modelo IS-LM: dado un punto (Y, P) y unos parámetros, calcula
# [dY/dt, dP/dt] y los GUARDA en el vector du (la "!" en el nombre indica
# que MODIFICA su primer argumento en vez de devolver un resultado nuevo,
# por convención de Julia). El integrador de DifferentialEquations.jl
# llamará a esta función miles de veces durante la simulación.
# "function nombre(args) ... end" define una FUNCIÓN en Julia, igual que
# "def" en Python pero terminada con "end" en vez de por indentación.
# La definimos aquí desglosada para que veas las ecuaciones que hay dentro
# de simulate_shock() — en el paquete esta lógica está en system_dynamics().
function custom_system_dynamics!(du, u, p, t)
    Y = u[1]
    P = u[2]

    params = p
    # Curva LM: tipo de interés nominal que equilibra el mercado de dinero
    i_rate = (P - params.m0 + params.psi * Y) / params.theta
    # Curva IS: demanda agregada en función del tipo de interés real (aquí pi=0)
    Y_d = params.beta0 - params.beta1 * (i_rate - 0.0) # pi=0

    # Phillips: inflación proporcional a la brecha de producción
    # Ajuste: la producción se mueve hacia la demanda agregada
    du[1] = params.ni * (Y_d - Y)
    du[2] = params.mi * (Y - params.ypot0)
end
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# @manipulate es el equivalente en Julia de interact() de Python: crea
# sliders y redibuja automáticamente cada vez que los mueves. La sintaxis
# "for var in slider(...)" define una variable controlada por un slider.
# El código dentro del bloque @manipulate se ejecuta completo cada vez que
# cambias cualquier slider — produce 3 paneles: (1) evolución temporal de Y,
# (2) evolución temporal de P, (3) diagrama de fases en el plano (Y, P).
# simulate_shock() llama a DifferentialEquations.jl para integrar las ODEs.
# Al mover los sliders verás en vivo cómo cambian las trayectorias.
@manipulate for m0_val in slider(80.0:1.0:120.0; value=110.0, label="Oferta Monetaria (M0)"), beta0_val in slider(1800.0:10.0:2400.0; value=2100.0, label="Gasto Autónomo (B0)")
    
    params_sim = default_calibration(ISLMParams)
    ss_init = steady_state(params_sim)
    initial_state = [ss_init["Y"], ss_init["P"]]
    
    params_sim = ISLMParams(params_sim.theta, params_sim.psi, params_sim.beta1, 
                            params_sim.mi, params_sim.ni, beta0_val, m0_val, params_sim.ypot0)
    
    t_span = (0.0, 30.0)
    t_eval = collect(range(0.0, 30.0, length=300))
    
    res = simulate_shock(params_sim, initial_state, t_span, t_eval)
    Y_path = res[1, :]
    P_path = res[2, :]
    ss_final = steady_state(params_sim)
    
    # Panel 1: Renta
    p1 = plot(t_eval, Y_path, color="#004C97", lw=2.5, label="Producción (Y)")
    hline!([params_sim.ypot0], color=:red, ls=:dash, label="Renta Potencial")
    title!("Evolución Temporal de la Renta (Y)")
    xlabel!("Tiempo (t)")
    ylabel!("Producción (Y)")

    # Panel 2: Precios
    p2 = plot(t_eval, P_path, color="#8EAD3A", lw=2.5, label="Precios (P)")
    hline!([ss_init["P"]], color=:gray, ls=:dot, label="SS Inicial")
    hline!([ss_final["P"]], color=:black, ls=:dash, label="SS Final")
    title!("Evolución Temporal de Precios (P)")
    xlabel!("Tiempo (t)")
    ylabel!("Nivel de Precios (P)")
    
    # Panel 3: Diagrama de Fases
    p3 = plot(Y_path, P_path, color="#7A3E9F", lw=3, label="Trayectoria dinámica")
    vline!([params_sim.ypot0], color="#D95319", ls=:dash, lw=2, label="P_dot = 0")

    Y_vals = range(minimum(Y_path)-15, maximum(Y_path)+15, length=100)
    slope = params_sim.theta * params_sim.mi - params_sim.theta / params_sim.beta1 - params_sim.psi
    int_init = ss_init["P"] - slope * params_sim.ypot0
    int_final = ss_final["P"] - slope * params_sim.ypot0

    P_loc_init = int_init .+ slope .* Y_vals
    P_loc_final = int_final .+ slope .* Y_vals

    plot!(Y_vals, P_loc_init, color="#0072BD", ls=:dot, label="Y_dot = 0 (Inicial)")
    plot!(Y_vals, P_loc_final, color="#0072BD", ls=:dash, lw=2, label="Y_dot = 0 (Final)")
    
    # Quiver
    Y_grid = range(minimum(Y_path)-8, maximum(Y_path)+8, length=12)
    P_grid = range(minimum(P_path)-0.8, maximum(P_path)+0.8, length=12)
    
    y_pts = Float64[]
    p_pts = Float64[]
    dy_pts = Float64[]
    dp_pts = Float64[]
    
    for y in Y_grid, p in P_grid
        dy, dp = system_dynamics([y, p], params_sim, 0.0)
        norm = sqrt(dy^2 + dp^2)
        if norm > 0
            push!(y_pts, y)
            push!(p_pts, p)
            push!(dy_pts, (dy/norm)*2.0) # Escalar para visualización
            push!(dp_pts, (dp/norm)*0.2)
        end
    end
    quiver!(y_pts, p_pts, quiver=(dy_pts, dp_pts), color=:gray, alpha=0.5)
    
    scatter!([ss_init["Y"]], [ss_init["P"]], color=:gray, markersize=6, label="EE Inicial")
    scatter!([ss_final["Y"]], [ss_final["P"]], color=:black, markersize=8, marker=:star, label="EE Final")
    
    title!("Diagrama de Fases en el Plano (Y, P)")
    xlabel!("Producción (Y)")
    ylabel!("Nivel de Precios (P)")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350), 
         plot_title="Respuesta del modelo IS-LM", top_margin=10mm)
end
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Verificamos que el estado estacionario calculado numéricamente coincide con
# el oráculo del Apéndice D (MATLAB) recogido en oraculo.md.
# @assert isapprox compara dos valores y SOLO lanza un error si la
# diferencia supera la tolerancia atol. No usamos "==" porque la aritmética
# con decimales casi nunca da resultados exactamente iguales (errores de
# redondeo internos). Si el port a Julia tuviera un error, esta celda
# lanzaría AssertionError y detendría la ejecución antes de seguir
# construyendo gráficos sobre un resultado incorrecto.
@assert isapprox(ss["Y"], 2000.0; atol=1e-6)
@assert isapprox(ss["P"], 81.0; atol=1e-6)
@assert isapprox(ss["i"], 2.0; atol=1e-6)
@assert isapprox(ss["Yd"], 2000.0; atol=1e-6)
@assert isapprox(ss["dP"], 0.0; atol=1e-6)
@assert isapprox(ss["dY"], 0.0; atol=1e-6)
println("OK: coincide con el oráculo MATLAB (Apéndice D).")
"""
    )
)

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))
nb.cells.append(nbf.v4.new_markdown_cell(md_cells[8]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(
    nbf.v4.new_code_cell(
        """# @btime (BenchmarkTools.jl) ejecuta la función muchas veces y muestra el
# tiempo mínimo/medio de ejecución y la memoria asignada. El $ delante de
# las variables evita que BenchmarkTools las trate como globales, lo que
# falsearía la medición de rendimiento (Fase III del proyecto). Al ejecutar
# veremos cuántos microsegundos tarda Julia en simular 50 periodos del
# modelo IS-LM.
@btime simulate_shock($params, [2000.0, 81.0], (0.0, 50.0), collect(range(0.0, 50.0, length=500)))
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

dir_path = "practicas/01-is-lm-dinamico/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
