import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
# Inyectamos una celda Markdown inicial con información del curso.
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P1: El Modelo IS-LM Dinámico en Tiempo Continuo (Julia)
- **ID de práctica:** LAB-P1-v1.0-julia
- **Capítulo del libro:** Cap. 2 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Antonio F. Romero Carrasco, Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Analizar la respuesta dinámica y la transición temporal de una economía IS-LM cerrada ante shocks de políticas macroeconómicas (monetarias y fiscales) bajo un ajuste gradual de la producción e inflación por curva de Phillips. Versión en Julia.
"""))

# 1.B. INSTRUCCIONES BÁSICAS (PEDAGÓGICAS) PARA ALUMNOS
# Celda anti-frustración para usuarios que no conocen Jupyter.
nb.cells.append(nbf.v4.new_markdown_cell(r"""> **👋 ¡Bienvenido/a a tu primer Cuaderno Interactivo!**
> Si nunca has usado Jupyter, aquí tienes las reglas básicas:
> 1. Este documento está compuesto por **celdas** de texto (como esta) y de código.
> 2. Para **ejecutar** una celda de código, haz clic en ella y pulsa `Shift + Enter` (o el botón ▶️ Play arriba).
> 3. Las variables se guardan en memoria. Ejecuta las celdas **en orden** (de arriba a abajo).
> 4. Si algo falla o se queda colgado, ve al menú superior: `Kernel` -> `Restart Kernel and Clear All Outputs` y empieza de nuevo. ¡No tengas miedo de romper nada!
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
using DifferentialEquations
"""))

# 4. TEORÍA Y ECUACIONES DEL MODELO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Ecuaciones y Parámetros

El modelo IS-LM dinámico en tiempo continuo describe una economía cerrada con las siguientes relaciones estructurales:

1. **Mercado Monetario (Curva LM):**
   $$i(Y, P) = \frac{P - M + \psi Y}{\theta}$$
2. **Demanda Agregada (Curva IS):**
   $$Y^d = \beta_0 - \beta_1(i - \pi)$$
3. **Curva de Phillips (Dinámica de Precios):**
   $$\frac{dP}{dt} = \mu(Y - \bar{Y})$$
4. **Ajuste del Producto (Dinámica de Producción):**
   $$\frac{dY}{dt} = \nu(Y^d - Y)$$
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(ISLMParams)
println(params)
"""))

# 6. ESTADO ESTACIONARIO Y EQUILIBRIO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Equilibrio de Largo Plazo (Estado Estacionario)
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""ss = steady_state(params)

println("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Renta de pleno empleo (Y*) : ", ss["Y"])
println("  Nivel de precios (P*)      : ", ss["P"])
println("  Tipo de interés (i*)       : ", round(ss["i"], digits=2), "%")
println("  Demanda agregada (Yd*)     : ", ss["Yd"])
"""))

# 7. VERIFICACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y en `oraculo.md`: $Y^* = 2000.0$, $P^* = 81.0$, $i^* = 2.0\%$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""@assert isapprox(ss["Y"], 2000.0; atol=1e-5)
@assert isapprox(ss["P"], 81.0; atol=1e-5)
@assert isapprox(ss["i"], 2.0; atol=1e-5)
println("OK: coincide con el oráculo.")
"""))

# 8. SHOCK SIMSIMULATION
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Análisis de Shock Monetario

Simulamos un incremento en la oferta monetaria de $100$ a $101$ y observamos la transición dinámica.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# Nueva calibración con shock monetario
params_shock = ISLMParams(
    params.theta, params.psi, params.beta1, params.mi, params.ni, params.beta0,
    101.0, # m0: shock monetario
    params.ypot0
)

initial_state = [ss["Y"], ss["P"]]
t_span = (0.0, 50.0)
t_eval = collect(range(0.0, 50.0, length=500))

res = simulate_shock(params_shock, initial_state, t_span, t_eval)

# Graficar
t = t_eval
p1 = plot(t, res[1, :], label="Renta (Y)", color=:blue, lw=2.5)
title!("Evolución de la Renta")
xlabel!("Periodos")
ylabel!("Y")

p2 = plot(t, res[2, :], label="Precios (P)", color=:green, lw=2.5)
title!("Evolución de Precios")
xlabel!("Periodos")
ylabel!("P")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

# 9. SIMULACIÓN ALTERNATIVA SHOCK MONETARIO INTERACTIVO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Simulación modular interactiva

Define una función para graficar la respuesta dinámica ante cualquier magnitud del shock sobre la oferta monetaria $m_0$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function graficar_shock_monetario(m0_val::Float64)
    p_shock = ISLMParams(
        params.theta, params.psi, params.beta1, params.mi, params.ni, params.beta0,
        m0_val,
        params.ypot0
    )
    res_sh = simulate_shock(p_shock, initial_state, t_span, t_eval)
    
    p1 = plot(t_eval, res_sh[1, :], label="Y", color=:blue, lw=2)
    title!("Y (M0 -> $m0_val)")
    
    p2 = plot(t_eval, res_sh[2, :], label="P", color=:green, lw=2)
    title!("P (M0 -> $m0_val)")
    
    plot(p1, p2, layout=(1,2), size=(800, 300))
end

# Ejemplo de ejecución
graficar_shock_monetario(103.0)
"""))

# 10. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas y Conclusión

El mismo modelo IS-LM dinámico muestra cómo la oferta monetaria tiene efectos reales a corto plazo (la producción responde y oscila), pero a largo plazo el dinero es neutral (la producción retorna a su nivel potencial $Y^*$ y solo cambian los precios nominales).
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

dir_path = 'practicas/01-is-lm-dinamico/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
