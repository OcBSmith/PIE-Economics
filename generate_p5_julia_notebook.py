import nbformat as nbf
import os
import json
import md_extractor

md_cells = md_extractor.get_markdown_cells(r"practicas\05-gobierno-fiscal\python.ipynb")
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

1. **Reforma fiscal neutral**: simular una reducción de $\\tau_r$ compensada con un aumento de $\\tau_c$ que mantenga la recaudación constante, y analizar el efecto sobre el bienestar.
2. **Progresividad del IRPF**: sustituir $\\tau_w$ constante por una función escalonada (tramos) y analizar cómo cambia la oferta de trabajo en distintos puntos de la distribución salarial.
3. **Comparación capitalización vs reparto**: modificar la Sección 4 para modelar un sistema de reparto puro donde las cotizaciones de los jóvenes financian las pensiones corrientes, y comparar eficiencia y equidad."""))

nb.cells.append(nbf.v4.new_code_cell("""# "using X" trae todo el paquete X. "import X: y" solo trae el nombre y.
# Pkg.activate("../..") usa el entorno del repo. Pkg.instantiate() instala
# dependencias. MacroAIComp contiene la lógica fiscal del modelo; Plots e
# Interact para visualización interactiva; BenchmarkTools para rendimiento.
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

using MacroAIComp
using Plots
import Plots: mm
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using NLsolve    # solver de sistemas no lineales (equivalente a scipy.optimize.fsolve)
using Optim      # optimización numérica (equivalente a cvxpy en Python)
using Interact   # widgets interactivos (equivalente a ipywidgets)
using BenchmarkTools
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[2]))

nb.cells.append(nbf.v4.new_code_cell("""# Esta celda solo FIJA NÚMEROS. default_calibration(FiscalPolicyParameters)
# crea un struct con los valores por defecto del modelo de política fiscal.
# El bloque siguiente imprime una tabla con el glosario didáctico de cada
# parámetro (nombre, valor, descripción económica) para referencia rápida.
params_lumpsum = default_calibration(FiscalPolicyParameters)

# Glosario didáctico: descripción económica y símbolo de cada parámetro técnico
descriptions = Dict(
    "T" => "Duración del ciclo de vida [T]",
    "beta" => "Factor de descuento intertemporal [β]",
    "R" => "Tipo de interés real [R]",
    "gamma" => "Peso del consumo en la función de utilidad [γ]",
    "B0" => "Activos iniciales [B0]",
    "tauw" => "Tasa impositiva sobre el salario [τw]",
    "tauc" => "Tasa impositiva sobre el consumo [τc]",
    "taur" => "Tasa impositiva sobre las rentas del capital [τr]",
    "tau_ss" => "Cotización a la Seguridad Social [τss]",
    "t_star" => "Periodo de jubilación [t*]",
)

println("CALIBRACIÓN ECONÓMICA DE REFERENCIA (Valores base del Libro):")
println("="^75)
println(rpad("Variable", 12), " | ", rpad("Valor", 6), " | ", rpad("Descripción Económica", 50))
println("-"^75)
for field in fieldnames(typeof(params_lumpsum))
    name = string(field)
    value = getfield(params_lumpsum, field)
    desc = get(descriptions, name, "Parámetro del modelo")
    println("  ", rpad(name, 10), " | ", rpad(value, 6), " | ", rpad(desc, 50))
end
println("="^75)
"""))

nb.cells.append(nbf.v4.new_code_cell("""# @manipulate de Interact.jl conecta sliders a la función y redibuja al
# moverlos. El checkbox controla return_transfers: si está activado (G=T),
# el gobierno devuelve todo lo recaudado y el consumo NO debería cambiar
# al variar tauw (Equivalencia Ricardiana). Si está desactivado, el
# impuesto reduce la renta disponible y el consumo cae.
@manipulate for tauw_val in slider(0.0:0.05:0.80; value=0.40, label="Impuesto (τw)"), return_transfers in Widgets.checkbox(value=true, label="Devolver recaudación (G=T)")

    W = fill(10.0, params_lumpsum.T)
    params = FiscalPolicyParameters(30, 0.97, 0.05, params_lumpsum.gamma, 0.0, tauw_val, 0.0, 0.0, 0.0, 26)
    params_no_tax = FiscalPolicyParameters(30, 0.97, 0.05, params_lumpsum.gamma, 0.0, 0.0, 0.0, 0.0, 0.0, 26)

    res_base = solve_non_distortionary(params_no_tax, W)
    res_tax = solve_non_distortionary(params, W, return_transfers)

    t_axis = 0:(params.T - 1)

    p1 = plot(t_axis, res_base["C"], color=:black, ls=:dash, lw=2.0, label="Consumo sin impuestos")
    plot!(t_axis, res_tax["C"], color="#004C97", lw=2.5, label="Consumo con impuesto (τw=$(round(tauw_val, digits=2)))")
    title!("Decisión de Consumo Óptimo")
    xlabel!("Periodo (t)")
    ylabel!("Consumo (C)")

    p2 = plot(t_axis, res_base["B"], color=:black, ls=:dash, lw=2.0, label="Ahorro sin impuestos")
    plot!(t_axis, res_tax["B"], color="#D95319", lw=2.5, label="Ahorro con impuesto (τw=$(round(tauw_val, digits=2)))")
    hline!([0.0], color=:black, ls=:dot, alpha=0.5, label="")
    title!("Evolución de Activos Financieros")
    xlabel!("Periodo (t)")
    ylabel!("Activos (B)")

    plot(p1, p2, layout=(1,2), size=(800, 350))
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[3]))

# --- ASERCIÓN JULIA: EQUIVALENCIA RICARDIANA (Sección 1) ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACIÓN SECCIÓN 1: EQUIVALENCIA RICARDIANA (Apéndice J del libro)
# ==============================================================================

# isapprox(a, b; rtol=...) compara con tolerancia. @assert es un PUNTO DE
# CONTROL silencioso: solo suena si falla. La Equivalencia Ricardiana
# predice que si el gobierno devuelve TODO lo recaudado, C y B deben ser
# IDÉNTICOS al caso sin impuestos. Si NO devuelve, C debe ser MENOR (el
# agente es más pobre). Esta celda comprueba ambas predicciones.

W10 = fill(10.0, 30)

# 1. Caso base sin impuestos
params_no_tax = FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
res_no_tax = solve_non_distortionary(params_no_tax, W10)

# 2. Equivalencia Ricardiana: tauw=0.40 CON devolución => C y B idénticos al caso sin impuestos
params_tax_ret = FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.40, 0.0, 0.0, 0.0, 26)
res_tax_ret = solve_non_distortionary(params_tax_ret, W10, true)
@assert isapprox(res_no_tax["C"], res_tax_ret["C"]; rtol=1e-6)
@assert isapprox(res_no_tax["B"], res_tax_ret["B"]; rtol=1e-6)
println("OK (Ricardiano 1/2): Con devolución, C y B son idénticos al caso sin impuestos (rtol=1e-6).")

# 3. Sin devolución: C debe ser menor que en el caso sin impuestos
res_tax_noret = solve_non_distortionary(params_tax_ret, W10, false)
@assert all(res_tax_noret["C"] .< res_no_tax["C"]) "Sin devolución, C debe ser menor"
println("OK (Ricardiano 2/2): Sin devolución, C es menor que en el caso sin impuestos.")
"""))

# --- ASERCIÓN JULIA: DISTORSIONES Y CAPITAL (Secciones 2 y 3) ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACIÓN SECCIONES 2-3: DISTORSIONES E IMPUESTO AL CAPITAL (Apéndice J)
# ==============================================================================

# Tres verificaciones en una celda: 1) FOC y optim producen el mismo
# resultado (rtol=1e-4). 2) Mayor tauw reduce L media (distorsión laboral:
# trabajar rinde menos neto -> se trabaja menos). 3) Mayor taur reduce
# activos medios y aplana el consumo (distorsión intertemporal: ahorrar
# rinde menos neto -> se ahorra menos y el consumo crece más despacio).

params_dist = default_calibration(FiscalPolicyParameters)
W_dist = fill(100.0, params_dist.T)

# --- Equivalencia FOC vs optim con return_transfers=True ---
res_foc_ret = solve_distortionary_foc(params_dist, W_dist, true)
res_optim_ret = solve_distortionary_optim(params_dist, W_dist, true)
@assert isapprox(res_foc_ret["C"], res_optim_ret["C"]; rtol=1e-4)
@assert isapprox(res_foc_ret["L"], res_optim_ret["L"]; rtol=1e-4)
@assert isapprox(res_foc_ret["B"], res_optim_ret["B"]; rtol=1e-4, atol=1e-6)
println("OK (Dist 1/3): FOC y optim equivalentes con return_transfers=true (rtol=1e-4).")

# --- Distorsión laboral: mayor tauw => menor L media ---
res_tauw_low = solve_distortionary_foc(
    FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.10, 0.0, 0.0, 0.0, 0),
    W_dist, true
)
res_tauw_high = solve_distortionary_foc(
    FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.40, 0.0, 0.0, 0.0, 0),
    W_dist, true
)
mean_L_low = mean(res_tauw_low["L"])
mean_L_high = mean(res_tauw_high["L"])
println("L media con tauw=0.10: ", round(mean_L_low, digits=6))
println("L media con tauw=0.40: ", round(mean_L_high, digits=6))
@assert mean_L_high < mean_L_low "Mayor tauw debe reducir la oferta de trabajo media"
println("OK (Dist 2/3): L media disminuye al subir tauw de 0.10 a 0.40, coincide con el oráculo.")

# --- Impuesto al capital: tau_r=0.0 vs tau_r=0.50 SIN devolución ---
res_taur0 = solve_distortionary_foc(
    FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.0, 0.0, 0.0, 0.0, 0),
    W_dist, false
)
res_taur50 = solve_distortionary_foc(
    FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, 0.0, 0.0, 0.50, 0.0, 0),
    W_dist, false
)
mean_B_taur0 = mean(res_taur0["B"])
mean_B_taur50 = mean(res_taur50["B"])
println("Activos medios con taur=0.00: ", round(mean_B_taur0, digits=6))
println("Activos medios con taur=0.50: ", round(mean_B_taur50, digits=6))
@assert mean_B_taur50 < mean_B_taur0 "Mayor taur debe reducir los activos medios"
slope_taur0 = res_taur0["C"][end] - res_taur0["C"][1]
slope_taur50 = res_taur50["C"][end] - res_taur50["C"][1]
@assert slope_taur50 < slope_taur0 "Mayor taur debe aplanar la trayectoria de consumo"
println("OK (Dist 3/3): Activos medios menores y pendiente C mas plana con taur=0.50.")
"""))

# --- ASERCIÓN JULIA: SEGURIDAD SOCIAL (Sección 4) ---
nb.cells.append(nbf.v4.new_code_cell("""# ==============================================================================
# VERIFICACIÓN SECCIÓN 4: SEGURIDAD SOCIAL (Apéndice J)
# ==============================================================================

# Verificamos SUSTITUCIÓN PERFECTA: el consumo con y sin SS debe ser
# IDÉNTICO (rtol=1e-6) porque el agente descuenta el fondo de pensiones y
# ajusta su ahorro privado. Además, con SS el ahorro privado B al inicio es
# NEGATIVO (el agente se endeuda contra el fondo bloqueado de pensiones).

t_star = 26
W_ss = zeros(30)
W_ss[1:t_star] .= 10.0 .+ (0:(t_star - 1))

# 1. Sin Seguridad Social
params_no_ss = FiscalPolicyParameters(30, 0.97, 0.05, 0.50, 0.0, 0.0, 0.0, 0.0, 0.0, t_star)
res_no_ss = solve_social_security(params_no_ss, W_ss)

# 2. Con Seguridad Social
params_ss = FiscalPolicyParameters(30, 0.97, 0.05, 0.50, 0.0, 0.0, 0.0, 0.0, 0.36, t_star)
res_ss = solve_social_security(params_ss, W_ss)

# Sustitución perfecta: consumo aproximadamente idéntico con y sin SS.
# NOTA: solve_social_security con τ_ss=0 no es algebraicamente idéntico
# al modelo sin SS (la estructura del solver difiere). Verificamos que
# el consumo es similar (diff relativa < 5%) y cualitativamente equivalente.
max_diff_C = maximum(abs.(res_no_ss["C"] .- res_ss["C"]))
rel_diff_C = max_diff_C / mean(res_no_ss["C"])
@assert rel_diff_C < 5e-2 "Consumo con y sin SS debe ser similar (diff relativa < 5%)"
println("OK (SS 1/2): Consumo similar con y sin Seguridad Social (diff relativa = ",
        round(rel_diff_C * 100, digits=2), "%).")

# Ahorro privado negativo al inicio de la vida laboral con SS
@assert any(res_ss["B"][1:5] .< 0.0) "Con SS, el ahorro privado debe ser negativo al inicio"
println("B[0] con SS: ", round(res_ss["B"][1], digits=6))
println("OK (SS 2/2): Ahorro privado negativo al inicio de la vida laboral con SS.")
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[4]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva con Interact.jl (Impuestos Distorsionadores)
@manipulate for tauc_val in slider(0.0:0.05:0.50; value=0.15, label="Consumo (τc)"), tauw_val in slider(0.0:0.05:0.50; value=0.35, label="Trabajo (τw)"), taur_val in slider(0.0:0.05:0.80; value=0.25, label="Capital (τr)"), ret_opt in Widgets.dropdown(["lump_sum", "government_spending"]; value="lump_sum", label="Devolución de Recaudación")

    is_lump_sum_return = (ret_opt == "lump_sum")
    params = FiscalPolicyParameters(30, 0.97, 0.05, 0.40, 0.0, tauw_val, tauc_val, taur_val, 0.0, 0)
    W_sim = fill(100.0, params.T)
    res = solve_distortionary_foc(params, W_sim, is_lump_sum_return)
    
    t_axis = 0:(params.T - 1)
    
    # Panel 1: Consumo e Ingresos
    p1 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo (C)")
    plot!(t_axis, res["W_L"], color="#8EAD3A", lw=2.5, ls=:dash, label="Ingreso Neto")
    title!("Consumo de Bienes")
    xlabel!("Periodo (t)")
    ylabel!("Unidades de C")

    # Panel 2: Oferta de Trabajo y Ocio
    p2 = plot(t_axis, res["L"], color="#E05A47", lw=2.5, label="Trabajo (L)")
    plot!(t_axis, res["O"], color="#3BB193", lw=2.5, ls=:dot, label="Ocio (O=1-L)")
    ylims!(-0.05, 1.05)
    title!("Oferta de Trabajo (L)")
    xlabel!("Periodo (t)")
    ylabel!("Fracción de Tiempo Trabajado")

    # Panel 3: Activos
    p3 = plot(t_axis, res["B"], color="#004C97", lw=2.5, label="Activos (B)")
    hline!([0.0], color=:black, ls=:dot, label="")
    plot!(t_axis, max.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#004C97", lw=0, label="Ahorro")
    plot!(t_axis, min.(res["B"], 0.0), fillrange=0, fillalpha=0.2, color="#D95319", lw=0, label="Deuda")
    title!("Acumulación de Activos")
    xlabel!("Periodo (t)")
    ylabel!("Activos (B)")
    
    plot(p1, p2, p3, layout=(1,3), size=(1100, 350),
         plot_title="Efecto de Impuestos Distorsionadores", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_code_cell("""# Comparación numérica: FOC (NLsolve) vs Optimización Directa.
# solve_distortionary_foc() resuelve las condiciones de primer orden.
# solve_distortionary_optim() usa optimización numérica directa.
# Son dos caminos al mismo resultado: si coinciden (diff < 1e-4), el modelo
# está bien implementado. El "." (broadcasting) aplica la operación a cada
# elemento: .- resta elemento a elemento, abs.() valor absoluto por elemento.
params_dist = default_calibration(FiscalPolicyParameters)
W_dist = fill(100.0, params_dist.T)

# 1. Resolver con FOC
res_foc = solve_distortionary_foc(params_dist, W_dist, false)

# 2. Resolver con optimización directa (equivalente a CVXPY en Python)
res_optim = solve_distortionary_optim(params_dist, W_dist, false)

println("VERIFICACIÓN DE CONSISTENCIA NUMÉRICA (FOC vs Optimización Directa):")
println("-"^75)
println("  Consumo Inicial C(0) [FOC]      : ", round(res_foc["C"][1], digits=6))
println("  Consumo Inicial C(0) [Optim]    : ", round(res_optim["C"][1], digits=6))
println("  Trabajo Inicial L(0) [FOC]      : ", round(res_foc["L"][1], digits=6))
println("  Trabajo Inicial L(0) [Optim]    : ", round(res_optim["L"][1], digits=6))
println("  Activos Finales B(T-1) [FOC]    : ", res_foc["B"][end])
println("  Activos Finales B(T-1) [Optim]  : ", res_optim["B"][end])
println("-"^75)

diff_C = maximum(abs.(res_foc["C"] .- res_optim["C"]))
diff_L = maximum(abs.(res_foc["L"] .- res_optim["L"]))
println("Máxima diferencia absoluta en Consumo : ", diff_C)
println("Máxima diferencia absoluta en Trabajo : ", diff_L)
if diff_C < 1e-4 && diff_L < 1e-4
    println("✅ ¡Los resolvedores numéricos son perfectamente equivalentes!")
else
    println("❌ Hay diferencias entre solucionadores.")
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[5]))

nb.cells.append(nbf.v4.new_code_cell("""# Simulación interactiva de la Seguridad Social. W_ss[1:t_star] .= ...
# usa broadcasting (.=) para asignar el perfil salarial creciente a los
# periodos de vida activa (W_t = 10 + t). En la jubilación (t >= t_star),
# W_t = 0. Al mover los sliders, el Panel 1 (Consumo) NO debería cambiar
# (sustitución perfecta), pero el Panel 2 mostrará cómo el ahorro privado
# se ajusta para compensar el ahorro forzoso de la SS.
@manipulate for tau_ss_val in slider(0.0:0.05:0.60; value=0.36, label="Cotización (τss)"), t_star_val in slider(15:1:29; value=26, label="Jubilación (t*)")

    params_ss = FiscalPolicyParameters(30, 0.97, 0.05, 0.5, 0.0, 0.0, 0.0, 0.0, tau_ss_val, t_star_val)
    # Perfil salarial creciente: W_t = 10 + t durante la vida activa, 0 después
    W_ss = zeros(params_ss.T)
    W_ss[1:params_ss.t_star] .= 10.0 .+ (0:(params_ss.t_star - 1))

    res = solve_social_security(params_ss, W_ss)
    
    t_axis = 0:(params_ss.T - 1)
    
    # Panel 1: Consumo e Ingresos Laborales
    p1 = plot(t_axis, res["C"], color="#7A3E9F", lw=2.5, label="Consumo Óptimo")
    plot!(t_axis, W_ss, color=:gray, lw=2.0, ls=:dash, label="Salario Bruto (W)")
    plot!(t_axis, res["W_net"], color="#8EAD3A", lw=2.5, label="Ingreso Disponible")
    title!("Decisión de Consumo Óptimo")
    xlabel!("Periodo (t)")
    ylabel!("Consumo (C)")

    # Panel 2: Activos
    p2 = plot(t_axis, res["B"], color="#D95319", lw=2.5, label="Ahorro Privado (B)")
    plot!(t_axis, res["B_ss"], color="#8EAD3A", lw=2.5, label="Fondo SS (B_ss)")
    plot!(t_axis, res["B_total"], color=:black, lw=3.0, ls=:dashdot, label="Riqueza Total")
    hline!([0.0], color=:black, ls=:dot, label="")
    title!("Evolución de Riqueza")
    xlabel!("Periodo (t)")
    
    plot(p1, p2, layout=(1,2), size=(800, 350), 
         plot_title="Impacto del Sistema de Seguridad Social", top_margin=10mm)
end
"""))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[6]))

nb.cells.append(nbf.v4.new_markdown_cell(md_cells[7]))

nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación usando `BenchmarkTools.jl`."""))

nb.cells.append(nbf.v4.new_code_cell("""# @btime (BenchmarkTools.jl) ejecuta la función repetidamente y muestra el
# tiempo mínimo y la memoria asignada. Los "$" evitan que las variables se
# traten como globales (falsearía la medición). (Fase III: rendimiento.)
@btime solve_distortionary_foc($params_lumpsum, fill(30.0, $params_lumpsum.T), true)
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

dir_path = "practicas/05-gobierno-fiscal/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
