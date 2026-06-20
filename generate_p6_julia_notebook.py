import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# LAB-P6: La Empresa y la Decisión de Inversión (Modelo Q de Tobin) (Julia)
- **ID de práctica:** LAB-P6-v1.0-julia
- **Capítulo del libro:** Cap. 7 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Modelar la decisión de inversión de una empresa competitiva que enfrenta costos de ajuste cuadráticos en la instalación del capital físico. Compararemos el solucionador log-linealizado frente al exacto no lineal. Versión en Julia.
"""
    )
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
"""))

# 4. TEORÍA Y ECUACIONES DEL MODELO
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Tobin's Q y Costos de Ajuste

El problema de inversión intertemporal de la empresa con costos de ajuste cuadráticos es:
$$\max_{\{I_t, K_{t+1}\}} \sum_{t=0}^{\infty} \frac{1}{(1+R)^t} \left[ K_t^\alpha - I_t - \frac{\phi}{2} \left( \frac{I_t - \delta K_t}{K_t} \right)^2 K_t \right]$$

Sujeto a:
$$K_{t+1} = (1-\delta) K_t + I_t$$
""")
)

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(TobinQParams)
println(params)
"""))

# 6. ESTADO ESTACIONARIO Y EQUILIBRIO
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 2. Equilibrio de Largo Plazo (Estado Estacionario)
""")
)

nb.cells.append(nbf.v4.new_code_cell(r"""ss = compute_steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Ratio q de Tobin marginal (q*) : ", ss["q"])
println("  Stock de capital (K*)          : ", ss["K"])
println("  Producción (Y*)                : ", ss["Y"])
println("  Inversión bruta (I*)           : ", ss["I"])
"""))

# 7. VERIFICACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y en `oraculo.md`: $q^* = 1.0$, $K^* = 6.8711$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""@assert isapprox(ss["q"], 1.0; atol=1e-5)
@assert isapprox(ss["K"], 6.8711236; atol=1e-5)
println("OK: coincide con el oráculo.")
"""))

# 8. SHOCK E COMPARACIÓN DE SOLUCIONADORES
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 4. Análisis de Shock y Comparación de Solucionadores (Lineal vs No Lineal)

Simulamos una caída permanente de la tasa de interés real del $4\%$ al $3\%$ en el período $t=2$ (segundo elemento del vector).
"""
    )
)

nb.cells.append(nbf.v4.new_code_cell(r"""# Initial steady state capital at R = 4%
ss_init = compute_steady_state(params, 0.04)
K0 = ss_init["K"]
T = 100

# Shock permanente a partir del periodo t=2 (index 2)
R_path = zeros(T)
R_path[1] = 0.04
R_path[2:end] .= 0.03

# Resolver lineal y no lineal
res_lin = solve_linearized_simulation(params, K0, R_path, T)
res_nonlin = solve_nonlinear_simulation(params, K0, R_path, T)

println("Q inicial (shock) [Lineal]    : ", res_lin["q"][1])
println("Q inicial (shock) [No Lineal] : ", res_nonlin["q"][1])

# Graficar
t = 0:(T-1)
p1 = plot(t, res_lin["q"], label="Lineal", color=:purple, linestyle=:dash, lw=2)
plot!(t, res_nonlin["q"], label="No Lineal", color=:purple, lw=2)
title!("Q de Tobin (q_t)")
xlabel!("Periodos")

p2 = plot(t, res_lin["K"], label="Lineal", color=:blue, linestyle=:dash, lw=2)
plot!(t, res_nonlin["K"], label="No Lineal", color=:blue, lw=2)
title!("Stock de Capital (K_t)")
xlabel!("Periodos")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

# 9. SIMULACIÓN MODULAR INTERACTIVA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Simulación interactiva / modular

Define una función para graficar la respuesta de la inversión ante cualquier tasa de interés de shock final.
"""))

nb.cells.append(
    nbf.v4.new_code_cell(r"""function graficar_shock_interes(R_final_val::Float64)
    R_sh = zeros(T)
    R_sh[1] = 0.04
    R_sh[2:end] .= R_final_val
    res_sh = solve_nonlinear_simulation(params, K0, R_sh, T)
    
    p1 = plot(0:99, res_sh["q"], label="q", color=:purple, lw=2)
    title!("q (R_final -> $R_final_val)")
    
    p2 = plot(0:99, res_sh["K"], label="K", color=:blue, lw=2)
    title!("K (R_final -> $R_final_val)")
    
    plot(p1, p2, layout=(1,2), size=(800, 300))
end

# Ejemplo de ejecución
graficar_shock_interes(0.02)
""")
)

# 10. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas y Conclusión

Este modelo ejemplifica cómo los costes de instalación retrasan la acumulación de capital. La variable flexible (Q de Tobin) salta instantáneamente para situarse sobre el camino de silla estable, guiando la acumulación lenta y gradual del capital hacia el nuevo estado estacionario.
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

dir_path = "practicas/06-tobin-q/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
