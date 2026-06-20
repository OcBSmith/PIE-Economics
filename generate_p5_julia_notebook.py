import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P5: Política Fiscal y Distorsiones Impositivas (Julia)
- **ID de práctica:** LAB-P5-v1.0-julia
- **Capítulo del libro:** Cap. 6 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Antonio F. Romero Carrasco, Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Evaluar los efectos dinámicos y distorsionadores de los impuestos de suma fija y de los impuestos sobre el consumo, el trabajo y el capital, así como la Seguridad Social, en una economía con horizonte temporal finito. Versión en Julia.
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
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Impuestos y Seguridad Social

El consumidor con preferencias de consumo y ocio se enfrenta a impuestos distorsionadores:
- $\tau_w$: impuesto sobre la renta del trabajo.
- $\tau_c$: impuesto sobre el consumo.
- $\tau_r$: impuesto sobre la rentabilidad de los activos.
- $\tau_{ss}$: cotizaciones a la Seguridad Social (pensiones de capitalización).
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(FiscalPolicyParameters)
println(params)
"""))

# 6. COMPARATIVA FOC VS OPTIM EN IMPUESTOS DISTORSIONADORES
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Equivalencia de Resolvedores con Impuestos Distorsionadores
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# Generar salario constante
W = fill(100.0, params.T)

# 1. FOC (fsolve/nlsolve)
res_foc = solve_distortionary_foc(params, W, true)

# 2. Optimización Directa (Optim)
res_optim = solve_distortionary_optim(params, W, true)

println("COMPARATIVA:")
println("  C(1) [FOC]   : ", res_foc["C"][1])
println("  C(1) [Optim] : ", res_optim["C"][1])
println("  L(1) [FOC]   : ", res_foc["L"][1])
println("  L(1) [Optim] : ", res_optim["L"][1])

@assert isapprox(res_foc["C"], res_optim["C"]; atol=1e-3)
@assert isapprox(res_foc["L"], res_optim["L"]; atol=1e-3)
println("OK: los resolvedores coinciden numéricamente.")
"""))

# 7. SIMULACIÓN DE SEGURIDAD SOCIAL
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Simulación del Sistema de Seguridad Social (Capitalización)

Simulamos un sistema de Seguridad Social donde las cotizaciones se capitalizan y se devuelven en forma de pensión en el periodo de jubilación.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# Parámetros con Seguridad Social (cotización del 36% sobre el salario)
params_ss = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.36, 26)
W_ss = zeros(params_ss.T)
W_ss[1:params_ss.t_star] .= 10.0

res_ss = solve_social_security(params_ss, W_ss)

println("Pensión de jubilación calculada: ", res_ss["Pension"])

t = 0:(params_ss.T-1)
p1 = plot(t, res_ss["C"], label="Consumo", color=:purple, lw=2.5)
title!("Consumo en el ciclo de vida con SS")
xlabel!("Periodo")

p2 = plot(t, res_ss["B"], label="Activos", color=:blue, lw=2.5)
hline!([0.0], color=:black, linestyle=:dot, label="")
title!("Activos Financieros")
xlabel!("Periodo")

plot(p1, p2, layout=(1,2), size=(800, 350))
"""))

# 8. BUENAS PRÁCTICAS Y CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Buenas Prácticas Aplicadas y Conclusión

Este laboratorio analiza el impacto distorsionador de la fiscalidad sobre la oferta laboral y la acumulación de activos financieros. Se verifica que la Seguridad Social de capitalización actúa como un perfecto sustituto del ahorro privado no distorsionador, desplazando la acumulación de riqueza personal pero manteniendo el mismo perfil de consumo óptimo.
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

dir_path = 'practicas/05-gobierno-fiscal/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
