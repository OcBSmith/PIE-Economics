import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""# LAB-P3: La Decisión Óptima de Consumo-Ahorro (Julia)
- **ID de práctica:** LAB-P3-v1.0-julia
- **Capítulo del libro:** Cap. 4 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Analizar la decisión óptima intertemporal de un hogar en un ciclo de vida finito. Comprender cómo la tasa de interés real, la impaciencia subjetiva y la estructura temporal de ingresos determinan el perfil óptimo de consumo y la trayectoria de acumulación de activos financieros (ahorro/deuda). Versión en Julia.
""")
)

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# En Google Colab se activarían y descargarían los paquetes necesarios.
# using Pkg; Pkg.activate("."); Pkg.instantiate()
"""
    )
)

# 3. IMPORTACIONES Y CONFIGURACIÓN
nb.cells.append(nbf.v4.new_code_cell(r"""using Pkg
Pkg.activate("../..")

using MacroAIComp
using Plots
using LinearAlgebra
using NLsolve
using Optim
"""))

# 4. TEORÍA Y ECUACIONES DEL MODELO
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 1. El Marco Teórico: Optimización Intertemporal del Consumidor

El consumidor decide su nivel de consumo a lo largo de un ciclo de vida finito de $T$ periodos. Su objetivo es maximizar:
$$\max_{\{C_t\}_{t=0}^{T-1}} \sum_{t=0}^{T-1} \beta^t \ln(C_t)$$

Sujeto a:
$$C_t + B_t = (1 + R_{t-1})B_{t-1} + W_t$$
Con $B_{-1} = 0$ y la condición terminal $B_{T-1} = 0$.
"""
    )
)

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(
    nbf.v4.new_code_cell(r"""params = default_calibration(ConsumptionSavingParameters)
println(params)
""")
)

# 6. RESOLUCIÓN DE LOS DOS MÉTODOS Y COMPARATIVA
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Métodos de Resolución Computacional: FOC vs Optimización Directa

Resolvemos la trayectoria de consumo óptima empleando la ecuación de Euler (FOC) y mediante optimización numérica directa (Optim.jl).
"""
    )
)

nb.cells.append(nbf.v4.new_code_cell(r"""# Generar perfil de ingresos constante
W_const = generate_income_profile("constant", params.T)

# 1. FOC (fsolve/nlsolve)
res_fsolve = solve_foc_fsolve(params, W_const)

# 2. Optimización Directa (Optim)
res_optim = solve_direct_optim(params, W_const)

println("COMPARATIVA:")
println("  C(1) [FOC]     : ", res_fsolve["C"][1])
println("  C(1) [Optim]   : ", res_optim["C"][1])
println("  B(end) [FOC]   : ", res_fsolve["B"][end])
println("  B(end) [Optim] : ", res_optim["B"][end])

@assert isapprox(res_fsolve["C"], res_optim["C"]; atol=1e-3)
println("OK: ambos métodos coinciden numéricamente.")
"""))

# 7. SIMULACIÓN DE CASOS (INCREASING Y RETIREMENT)
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 3. Simulación interactiva de perfiles salariales y parámetros

Analizamos las respuestas del consumo y los activos ante salarios crecientes y jubilación.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""function graficar_consumo_ahorro(beta_val::Float64, R_val::Float64, profile::String)
    p_sh = ConsumptionSavingParameters(params.T, beta_val, R_val, params.B0)
    W = generate_income_profile(profile, p_sh.T)
    res = solve_foc_fsolve(p_sh, W)
    
    t = 0:(p_sh.T-1)
    p1 = plot(t, res["C"], label="Consumo (C)", color=:purple, lw=2.5)
    plot!(t, W, label="Ingresos (W)", color=:green, lw=2, linestyle=:dash)
    title!("Consumo e Ingresos ($profile)")
    xlabel!("Periodos")
    
    p2 = plot(t, res["B"], label="Activos (B)", color=:blue, lw=2.5)
    hline!([0.0], color=:black, linestyle=:dot, label="")
    title!("Evolución de Activos Financieros")
    xlabel!("Periodos")
    
    plot(p1, p2, layout=(1,2), size=(800, 350))
end

# Ejemplo de ejecución
graficar_consumo_ahorro(0.97, 0.02, "retirement")
"""
    )
)

# 8. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 4. Buenas Prácticas Aplicadas y Conclusión

El ahorro permite suavizar el perfil de consumo frente a las fluctuaciones en los ingresos (como en la jubilación). En este laboratorio, ambos resolvedores numéricos se validan mutuamente al dar exactamente la misma trayectoria óptima.
""")
)

# METADATOS DEL CUADERNO (KERNEL DE JULIA)
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
