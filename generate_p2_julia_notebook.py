import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P2: El Modelo de Overshooting de Dornbusch en Tiempo Discreto (Julia)
- **ID de práctica:** LAB-P2-v1.0-julia
- **Capítulo del libro:** Cap. 3 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Antonio F. Romero Carrasco, Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Analizar el comportamiento dinámico de una pequeña economía abierta con movilidad perfecta de capitales. Estudiar cómo responde el tipo de cambio nominal a shocks monetarios y por qué experimenta una sobrerreacción o *overshooting* inicial debido a la rigidez temporal de los precios nacionales. Versión en Julia.
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
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Ecuaciones y Estabilidad de Punto de Silla

El modelo de Dornbusch describe una economía pequeña y abierta con perfecta movilidad de capitales bajo las siguientes ecuaciones:

1. **Mercado Monetario (LM):** $i_t = \frac{p_t - m_t + \psi y^n_t}{\theta}$
2. **Demanda Agregada (IS):** $y^d_t = \beta_0 + \beta_1(s_t - p_t + p^*_t) - \beta_2 i_t$
3. **Ajuste de Precios (Phillips):** $\Delta p_t = \mu(y^d_t - y^n_t)$
4. **Paridad de Intereses (UIP):** $\Delta s_t = i_t - i^*_t$
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(DornbuschParams)
println(params)
"""))

# 6. ESTADO ESTACIONARIO Y EQUILIBRIO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Equilibrio de Largo Plazo (Estado Estacionario)
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""ss = steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Precios nacionales (p*)    : ", ss["p"])
println("  Tipo de cambio nominal (s*): ", ss["s"])
println("  Tipo de interés (i*)       : ", ss["i"], "%")
"""))

# 7. VERIFICACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y en `oraculo.md`: $p^* = 1.5$, $s^* = 76.5150$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""@assert isapprox(ss["p"], 1.5; atol=1e-5)
@assert isapprox(ss["s"], 76.5150; atol=1e-3)
println("OK: coincide con el oráculo.")
"""))

# 8. SHOCK SIMSIMULATION
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Análisis de Shock Monetario

Simulamos un incremento en la oferta monetaria de $100$ a $101$ y observamos el salto cambiario.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# Vectores exógenos z = [beta0, m, ypot, istar, pstar]
z_initial = [500.0, 100.0, 2000.0, 3.0, 0.0]
z_final = [500.0, 101.0, 2000.0, 3.0, 0.0]
periods = 30

res = simulate_shock(params, z_initial, z_final, periods, 1)

# Graficar
t = 0:(periods-1)
p1 = plot(t, res["s"], label="Tipo de cambio (s)", color=:purple, lw=2.5)
title!("Evolución de Tipo de Cambio")
xlabel!("Periodos")
ylabel!("s")

p2 = plot(t, res["p"], label="Precios (p)", color=:green, lw=2.5)
title!("Evolución de Precios")
xlabel!("Periodos")
ylabel!("p")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

# 9. SIMULACIÓN DE DIAGRAMA DE FASES
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Simulación interactiva / modular

Define una función para graficar la respuesta dinámica ante variaciones en la oferta de dinero ($M$) y gasto autónomo ($B_0$).
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function graficar_shock_dornbusch(m0_val::Float64, beta0_val::Float64)
    z_fn = [beta0_val, m0_val, 2000.0, 3.0, 0.0]
    res_sh = simulate_shock(params, z_initial, z_fn, periods, 1)
    
    p1 = plot(0:29, res_sh["s"], label="s", color=:purple, lw=2)
    title!("s (M0 -> $m0_val, B0 -> $beta0_val)")
    
    p2 = plot(0:29, res_sh["p"], label="p", color=:green, lw=2)
    title!("p (M0 -> $m0_val, B0 -> $beta0_val)")
    
    plot(p1, p2, layout=(1,2), size=(800, 300))
end

# Ejemplo de ejecución
graficar_shock_dornbusch(101.0, 500.0)
"""))

# 10. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas y Conclusión

El modelo de Dornbusch demuestra el concepto de sobrerreacción cambiaria (overshooting) a corto plazo ante shocks monetarios permanentes. Esto surge debido a la lentitud en el ajuste de los precios de bienes en comparación con la flexibilidad del mercado de activos financieros.
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

dir_path = 'practicas/02-overshooting-dornbusch/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
