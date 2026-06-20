import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P8: El Modelo Neoclásico de Crecimiento Exógeno (Solow-Swan) (Julia)
- **ID de práctica:** LAB-P8-v1.0-julia
- **Capítulo del libro:** Cap. 9 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Simular y analizar la dinámica de acumulación de capital en tiempo discreto, el proceso de transición hacia el estado estacionario, los efectos de perturbaciones estructurales (tasa de ahorro, demografía y TFP), y el principio de la Regla de Oro. Versión en Julia.
"""))

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""# En Google Colab se activarían y descargarían los paquetes necesarios.
# using Pkg; Pkg.activate("."); Pkg.instantiate()
"""))

# 3. IMPORTACIONES Y CONFIGURACIÓN
nb.cells.append(nbf.v4.new_code_cell(r"""using Pkg
Pkg.activate("../..")

using MacroAIComp
using Plots
using LinearAlgebra
"""))

# 4. TEORÍA Y ECUACIONES DEL MODELO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Crecimiento de Solow-Swan

El modelo de acumulación de capital per cápita se describe mediante:
$$k_{t+1} = \frac{(1 - \delta)k_t + s A_t k_t^\alpha}{1 + n}$$

Y las variables de bienestar en estado estacionario se derivan de:
$$\bar{k} = \left( \frac{\delta + n}{s A} \right)^{\frac{1}{\alpha - 1}}$$
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(SolowSwanParameters)
println(params)
"""))

# 6. ESTADO ESTACIONARIO Y EQUILIBRIO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Equilibrio de Largo Plazo (Estado Estacionario)
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""ss = compute_solow_steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Capital per cápita (k*)     : ", ss["k"])
println("  Producción per cápita (y*)  : ", ss["y"])
println("  Consumo per cápita (c*)     : ", ss["c"])
println("  Inversión per cápita (i*)   : ", ss["i"])
"""))

# 7. VERIFICACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y en `oraculo.md`: $k^* = 4.0946$, $c^* = 1.3103$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""@assert isapprox(ss["k"], 4.0946; atol=1e-4)
@assert isapprox(ss["c"], 1.3103; atol=1e-4)
println("OK: coincide con el oráculo.")
"""))

# 8. SHOCK DE TASA DE AHORRO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Análisis de Shock y Transición Dinámica

Simulamos un incremento en la tasa de ahorro del $20\%$ al $25\%$ en el período $t=5$ (índice 5 en Julia).
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""T = 150
s_path = fill(0.25, T)
n_path = fill(params.n, T)
A_path = fill(1.00, T)

res = simulate_solow_swan(params, ss["k"], s_path, n_path, A_path, T)

# Graficar
t = 0:(T-1)
p1 = plot(t, res["k"], label="Capital (k_t)", color=:green, lw=2.5)
title!("Acumulación de Capital")
xlabel!("Periodos")

p2 = plot(t, res["c"], label="Consumo (c_t)", color=:purple, lw=2.5)
title!("Consumo per cápita")
xlabel!("Periodos")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

# 9. REGLA DE ORO DE ACUMULACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Demostración Visual de la Regla de Oro

El consumo de estado estacionario se maximiza cuando la tasa de ahorro equivale a la participación del capital en el PIB ($s = \alpha$).
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""s_grid = range(0.01, 0.95, length=100)
c_ss_grid = [compute_solow_steady_state(params, s_val)["c"] for s_val in s_grid]

# Encontrar el óptimo (Regla de Oro)
alpha = params.alpha
ss_gold = compute_solow_steady_state(params, alpha)
c_gold = ss_gold["c"]

plot(s_grid, c_ss_grid, label="c estacionario", color=:purple, lw=2.5,
     title="Regla de Oro de Solow-Swan", xlabel="Tasa de Ahorro (s)", ylabel="Consumo (c)")
scatter!([alpha], [c_gold], label="Regla de Oro (s = alpha)", color=:green, markersize=8)
"""))

# 10. SIMULACIÓN MODULAR INTERACTIVA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 6. Simulación modular interactiva

Define una función para graficar la transición del capital ante shocks permanentes de ahorro o demografía.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function graficar_solow_shocks(s_fn::Float64, n_fn::Float64)
    T_sh = 100
    s_p = fill(params.s, T_sh)
    n_p = fill(params.n, T_sh)
    A_p = fill(params.A, T_sh)
    
    s_p[5:end] .= s_fn
    n_p[5:end] .= n_fn
    
    res_sh = simulate_solow_swan(params, ss["k"], s_p, n_p, A_p, T_sh)
    
    p1 = plot(0:99, res_sh["k"], label="k", color=:green, lw=2)
    title!("k (s -> $s_fn, n -> $n_fn)")
    
    p2 = plot(0:99, res_sh["c"], label="c", color=:purple, lw=2)
    title!("c (s -> $s_fn, n -> $n_fn)")
    
    plot(p1, p2, layout=(1,2), size=(800, 300))
end

# Ejemplo de ejecución
graficar_solow_shocks(0.30, 0.01)
"""))

# 11. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 7. Buenas Prácticas Aplicadas y Conclusión

Este laboratorio demuestra cómo la ineficiencia dinámica puede producir sobreacumulación de capital, reduciendo el consumo a largo plazo. La regla de oro nos muestra la tasa de ahorro óptima que maximiza el consumo intertemporal.
"""))

# METADATOS DEL CUADERNO (KERNEL DE JULIA)
nb.metadata = {
    "kernelspec": {
        "display_name": "Julia 1.12.6",
        "language": "julia",
        "name": "julia-1.12"
    },
    "language_info": {
        "file_extension": ".jl",
        "mimetype": "application/julia",
        "name": "julia",
        "version": "1.12.6"
    }
}

dir_path = 'practicas/08-solow-swan/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
