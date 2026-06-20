import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P4: Decisión Óptima de Consumo-Ocio y Oferta de Trabajo (Julia)
- **ID de práctica:** LAB-P4-v1.0-julia
- **Capítulo del libro:** Cap. 5 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Analizar la decisión óptima de consumo, ocio y oferta de trabajo en un modelo intertemporal de ciclo de vida con horizonte finito. Estudiar cómo responden el consumo y la oferta de trabajo a variaciones en el salario real y en las tasas de interés. Versión en Julia.
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
using NLsolve
using Optim
"""))

# 4. TEORÍA Y ECUACIONES DEL MODELO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Consumo, Ocio y Trabajo

El hogar maximiza la utilidad intertemporal descontada:
$$\max_{\{C_t, L_t\}_{t=0}^{T-1}} \sum_{t=0}^{T-1} \beta^t \left[ \gamma \ln(C_t) + (1 - \gamma) \ln(1 - L_t) \right]$$

Sujeto a:
$$C_t + B_t = (1 + R_{t-1})B_{t-1} + W_t L_t$$
Con $B_{-1} = 0$, $B_{T-1} = 0$, y $L_t \in [0, 1)$.
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(ConsumptionLeisureParameters)
println(params)
"""))

# 6. RESOLUCIÓN DE LOS DOS MÉTODOS Y COMPARATIVA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Métodos de Resolución Computacional: FOC vs Optimización Directa
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# Generar salario constante
W = fill(30.0, params.T)

# 1. FOC (fsolve/nlsolve)
res_fsolve = solve_foc_fsolve(params, W)

# 2. Optimización Directa (Optim)
res_optim = solve_direct_optim(params, W)

println("COMPARATIVA:")
println("  C(1) [FOC]   : ", res_fsolve["C"][1])
println("  C(1) [Optim] : ", res_optim["C"][1])
println("  L(1) [FOC]   : ", res_fsolve["L"][1])
println("  L(1) [Optim] : ", res_optim["L"][1])

@assert isapprox(res_fsolve["C"], res_optim["C"]; atol=1e-3)
@assert isapprox(res_fsolve["L"], res_optim["L"]; atol=1e-3)
println("OK: ambos solucionadores coinciden.")
"""))

# 7. SIMULACIÓN DE CASOS E INTERACTIVIDAD
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Simulación de la dinámica interactiva de ocio y consumo
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function graficar_consumo_ocio(beta_val::Float64, R_val::Float64, gamma_val::Float64)
    p_sh = ConsumptionLeisureParameters(params.T, beta_val, R_val, gamma_val, params.B0)
    W_path = fill(30.0, p_sh.T)
    res = solve_foc_fsolve(p_sh, W_path)
    
    t = 0:(p_sh.T-1)
    p1 = plot(t, res["C"], label="Consumo (C)", color=:purple, lw=2.5)
    title!("Consumo óptimo")
    xlabel!("Periodos")
    
    p2 = plot(t, res["L"], label="Trabajo (L)", color=:orange, lw=2.5)
    plot!(t, res["O"], label="Ocio (O)", color=:blue, lw=2.5)
    title!("Oferta de Trabajo y Ocio")
    xlabel!("Periodos")
    
    plot(p1, p2, layout=(1,2), size=(800, 350))
end

# Ejemplo de ejecución
graficar_consumo_ocio(0.97, 0.02, 0.5)
"""))

# 8. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Buenas Prácticas Aplicadas y Conclusión

Este modelo demuestra el tradeoff consumo-ocio. Incrementos en el salario real de largo plazo aumentan el consumo de equilibrio, mientras que el efecto sobre la oferta de trabajo depende del balance entre los efectos renta y sustitución intertemporales.
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

dir_path = 'practicas/04-consumo-ocio/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
