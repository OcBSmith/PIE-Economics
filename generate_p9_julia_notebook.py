import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# LAB-P9: El Modelo de Crecimiento Óptimo de Ramsey (Julia)
- **ID de práctica:** LAB-P9-v1.0-julia
- **Capítulo del libro:** Cap. 10 — *An introduction to computational macroeconomics* (Bongers, Gómez y Torres, 2019)
- **Autores:** Antonio F. Romero Carrasco, Anelí Bongers
- **Fecha:** 2026-06-20
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Objetivo: Resolver e interactuar con el modelo canónico de crecimiento óptimo de Ramsey-Cass-Koopmans en tiempo discreto, calculando las condiciones de estabilidad de punto de silla, los autovalores jacobianos, la condición de salto de la variable forward-looking (Consumo) y contrastando la solución linealizada frente a la solución no lineal exacta. Versión en Julia.
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

# 4. INTRODUCCIÓN TEÓRICA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Modelo de Crecimiento Óptimo de Ramsey

El modelo de Ramsey-Cass-Koopmans microfunda las decisiones de ahorro. A diferencia del modelo de Solow-Swan, donde el ahorro es una fracción fija exógena, aquí el ahorro se determina endógenamente a partir del problema de optimización intertemporal de los hogares, que maximizan su utilidad a lo largo de un horizonte infinito (representando a la dinastía familiar).

### 1.1 El Problema de Optimización del Hogar
El hogar representativo maximiza su utilidad descontada sujeta a la dinámica demográfica (la población crece a tasa constante $n$):
$$\max_{\{c_t\}} \sum_{t=0}^{\infty} \left( \frac{1+n}{1+\theta} \right)^t \ln(c_t)$$
Sujeto a la restricción presupuestaria per cápita:
$$c_t + (1+n)k_{t+1} = w_t + (R_t + 1 - \delta)k_t$$
donde $\theta$ es la tasa de preferencia intertemporal ($1+\theta = 1/\beta$). La condición de primer orden para este problema da lugar a la **Regla de Keynes-Ramsey**:
$$c_{t+1} = \beta (R_{t+1} + 1 - \delta) c_t$$

### 1.2 El Problema de la Empresa y Equilibrio
La empresa maximiza beneficios periodos a periodo bajo una función de producción Cobb-Douglas $y_t = A_t k_t^\alpha$, lo que determina las demandas de factores competitivas:
$$R_t = \alpha A_t k_t^{\alpha-1}, \quad w_t = (1-\alpha)y_t$$

Sustituyendo estas demandas en las ecuaciones del hogar, el equilibrio competitivo dinámico se reduce a un sistema bidimensional de dos ecuaciones en diferencias no lineales:
1.  **Dinámica de Consumo (Regla de Euler):**
    $$c_{t+1} = \beta \left( \alpha A_{t+1} k_{t+1}^{\alpha-1} + 1 - \delta \right) c_t$$
2.  **Dinámica de Acumulación de Capital:**
    $$(1+n)k_{t+1} = (1-\delta)k_t + A_t k_t^\alpha - c_t$$

### 1.3 Estado Estacionario
Eliminando los subíndices de tiempo en el sistema, obtenemos los valores de largo plazo:
$$\bar{k} = \left( \frac{1 - \beta + \beta\delta}{\alpha A\beta} \right)^{\frac{1}{\alpha - 1}}$$
$$\bar{y} = A \bar{k}^\alpha, \quad \bar{c} = \bar{y} - (n + \delta)\bar{k}, \quad \bar{i} = (n + \delta)\bar{k}, \quad \bar{R} = \frac{1}{\beta} - 1 + \delta$$
"""))

# 5. LINEALIZACIÓN Y ESTABILIDAD
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Linealización de Blanchard-Khan y la Condición de Salto

El sistema dinámico no lineal anterior se aproxima linealmente alrededor de su estado estacionario en log-desviaciones ($\hat{c}_t = \ln(c_t/\bar{c})$ y $\hat{k}_t = \ln(k_t/\bar{k})$). El sistema resultante de ecuaciones en diferencias es:
$$\begin{bmatrix} \Delta \hat{c}_t \\ \Delta \hat{k}_t \end{bmatrix} = \begin{bmatrix} J_{11} & J_{12} \\ J_{21} & J_{22} \end{bmatrix} \begin{bmatrix} \hat{c}_t \\ \hat{k}_t \end{bmatrix}$$

donde:
$$J_{11} = - \frac{(\alpha - 1)\Omega\Gamma}{\alpha\beta(1+n)}, \quad J_{12} = \frac{(\alpha - 1)\Omega}{\beta(1+n)}$$
$$J_{21} = - \frac{\Gamma}{\alpha\beta(1+n)}, \quad J_{22} = \frac{1 - \beta(1+n)}{\beta(1+n)}$$
siendo $\Omega \equiv 1-\beta+\beta\delta$ y $\Gamma \equiv 1-\beta+\beta\delta - \alpha\beta(\delta+n)$.

Este sistema tiene una estructura de **punto de silla** (un autovalor estable y otro inestable). Al producirse un shock, la variable rígida (Capital, $\hat{k}_t$) no puede saltar instantáneamente. Es la variable flexible (Consumo, $\hat{c}_t$) la que realiza un **salto discreto instantáneo** en el periodo de impacto para colocarse sobre la trayectoria estable:
$$\hat{c}_0 = \theta \hat{k}_0 \quad \text{donde } \theta = \frac{\alpha(\alpha - 1)\Omega}{(\alpha - 1)\Omega\Gamma + \alpha\beta(1 + n)\lambda_1}$$
donde $\lambda_1$ es el autovalor estable del Jacobiano $J$.
"""))

# 6. CALIBRACIÓN Y ESTADO ESTACIONARIO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Calibración y Estado Estacionario"""))

nb.cells.append(nbf.v4.new_code_cell(r"""params = default_calibration(RamseyParams)
println(params)

ss = compute_ramsey_steady_state(params)
println("\nVALORES DE EQUILIBRIO DE LARGO PLAZO:")
println("  Capital per cápita (k*)     : ", ss["k"])
println("  Producción per cápita (y*)  : ", ss["y"])
println("  Consumo per cápita (c*)     : ", ss["c"])
println("  Inversión per cápita (i*)   : ", ss["i"])
println("  Tipo de interés real (R*)   : ", round(ss["R"] * 100, digits=2), "%")
"""))

# 7. VERIFICACIÓN CONTRA EL ORÁCULO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y en `oraculo.md`: $k^* = 7.9537$, $c^* = 1.4300$.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""@assert isapprox(ss["k"], 7.9537; atol=1e-4)
@assert isapprox(ss["c"], 1.4300; atol=1e-4)
println("OK: coincide con el oráculo.")
"""))

# 8. SIMULACIÓN DINÁMICA DE SHOCKS
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Simulación de Transición ante Shocks de Productividad y Preferencias

Definimos una función interactiva/modular para simular el impacto en el período $t = 5$ de un shock permanente sobre la TFP ($A$) o sobre el factor de descuento ($\beta$).
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function plot_ramsey_simulation(A_final::Float64, beta_final::Float64)
    params = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params)
    
    T = 80
    t_shock = 5
    
    # Resolver la trayectoria linealizada
    res = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_final,
        params.n,
        beta_final,
        T,
        t_shock
    )
    
    # Calcular el nuevo steady state esperado
    params_new = RamseyParams(params.alpha, beta_final, params.delta, params.n, A_final)
    ss_final = compute_ramsey_steady_state(params_new)
    
    t_axis = 0:(T-1)
    
    # Panel 1: Producción per cápita (y_t)
    p1 = plot(t_axis, res["y"], color=:blue, lw=2.5, label="Trayectoria (y_t)")
    hline!([ss_init["y"]], color=:black, linestyle=:dash, alpha=0.5, label="SS Inicial")
    hline!([ss_final["y"]], color=:red, linestyle=:dot, alpha=0.7, label="SS Final")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Producción per cápita")
    xlabel!("Períodos")
    ylabel!("y")
    
    # Panel 2: Stock de Capital per cápita (k_t)
    p2 = plot(t_axis, res["k"], color=:green, lw=2.5, label="Trayectoria (k_t)")
    hline!([ss_init["k"]], color=:black, linestyle=:dash, alpha=0.5, label="SS Inicial")
    hline!([ss_final["k"]], color=:red, linestyle=:dot, alpha=0.7, label="SS Final")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Capital per cápita")
    xlabel!("Períodos")
    ylabel!("k")
    
    # Panel 3: Consumo per cápita (c_t)
    p3 = plot(t_axis, res["c"], color=:purple, lw=2.5, label="Trayectoria (c_t)")
    hline!([ss_init["c"]], color=:black, linestyle=:dash, alpha=0.5, label="SS Inicial")
    hline!([ss_final["c"]], color=:red, linestyle=:dot, alpha=0.7, label="SS Final")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Consumo per cápita (Salto)")
    xlabel!("Períodos")
    ylabel!("c")
    
    # Panel 4: Inversión per cápita (i_t)
    p4 = plot(t_axis, res["i"], color=:orange, lw=2.5, label="Trayectoria (i_t)")
    hline!([ss_init["i"]], color=:black, linestyle=:dash, alpha=0.5, label="SS Inicial")
    hline!([ss_final["i"]], color=:red, linestyle=:dot, alpha=0.7, label="SS Final")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Inversión per cápita")
    xlabel!("Períodos")
    ylabel!("i")
    
    plot(p1, p2, p3, p4, layout=(2,2), size=(900, 600))
end

# Ejemplo de ejecución: shock permanente de TFP (+5%)
plot_ramsey_simulation(1.05, 0.97)
"""))

# 9. COMPARACIÓN DE SOLVER BK VS NO LINEAL
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 6. Precisión de Resolvedores: Blanchard-Khan frente a Solución No Lineal

El resolvedor de Blanchard-Khan asume una linealización de primer orden alrededor del estado estacionario y es altamente preciso para shocks de baja envergadura. Para shocks de gran tamaño, sin embargo, el error acumulado por la curvatura puede ser relevante.

A continuación, compara las trayectorias calculadas mediante **Blanchard-Khan (BK)** y por el resolvedor **No Lineal Exacto** ante perturbaciones de distinta envergadura.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""function plot_ramsey_comparison(A_shock::Float64)
    params = default_calibration(RamseyParams)
    ss_init = compute_ramsey_steady_state(params)
    
    T = 80
    t_shock = 5
    
    A_path = fill(1.00, T)
    A_path[(t_shock + 1):end] .= A_shock
    n_path = fill(0.02, T)
    
    # 1. Solución linealizada de BK
    res_lin = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_shock,
        params.n,
        params.beta,
        T,
        t_shock
    )
    
    # 2. Solución exacta no lineal
    res_nonlin = solve_ramsey_nonlinear(
        params,
        ss_init["k"],
        A_path,
        n_path,
        T,
        t_shock
    )
    
    t_axis = 0:(T-1)
    
    # Consumo
    p1 = plot(t_axis, res_lin["c"], color=:purple, linestyle=:dash, lw=2.0, label="Blanchard-Khan (Lineal)")
    plot!(t_axis, res_nonlin["c"], color=:purple, lw=2.0, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Consumo per cápita (c_t)")
    xlabel!("Períodos")
    ylabel!("c")
    
    # Capital
    p2 = plot(t_axis, res_lin["k"], color=:green, linestyle=:dash, lw=2.0, label="Blanchard-Khan (Lineal)")
    plot!(t_axis, res_nonlin["k"], color=:green, lw=2.0, label="Exacto No Lineal")
    vline!([t_shock], color=:grey, linestyle=:dot, alpha=0.5, label="")
    title!("Capital per cápita (k_t)")
    xlabel!("Períodos")
    ylabel!("k")
    
    # Combinar gráficos
    p = plot(p1, p2, layout=(1,2), size=(800, 350))
    display(p)
    
    # Error relativo máximo
    err_c = maximum(abs.(res_lin["c"] .- res_nonlin["c"])) / ss_init["c"] * 100
    err_k = maximum(abs.(res_lin["k"] .- res_nonlin["k"])) / ss_init["k"] * 100
    println("Error relativo máximo en Consumo : ", round(err_c, digits=4), "%")
    println("Error relativo máximo en Capital  : ", round(err_k, digits=4), "%")
end

# Ejemplo de ejecución: shock del 5%
plot_ramsey_comparison(1.05)
"""))

# 10. CUADERNO DE BITÁCORA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 7. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con el simulador del modelo de crecimiento óptimo de Ramsey:

1.  **Dinámica de Consumo y Ahorro en Ramsey (Comparación con Solow-Swan)**:
    *   Simula un incremento permanente de la TFP del $5\%$ ($A = 1.05$). Describe cómo responden el consumo y la inversión en el momento del impacto ($t=5$). ¿Por qué el consumo salta instantáneamente en Ramsey, en lugar de mantenerse constante como ocurriría bajo una tasa de ahorro fija?
    *   Explica qué motiva a los hogares representativos a aumentar su inversión y sacrificar consumo relativo a largo plazo para acumular más capital.
2.  **Shock de Paciencia (Preferencia Intertemporal $\beta$)**:
    *   Simula un incremento del factor de descuento $\beta$ de $0.97$ a $0.98$. Describe el comportamiento del consumo y la inversión en el período del shock $t=5$. ¿Por qué se produce una caída instantánea del consumo? ¿Cómo compensa este "sacrificio" de corto plazo al bienestar dinámico de los consumidores en el largo plazo?
3.  **Límites de la linealización**:
    *   Establece un shock de TFP estándar del $5\%$ ($A = 1.05$) y anota el error relativo máximo entre el resolvedor de Blanchard-Khan y el no lineal exacto.
    *   Aplica un shock masivo del $30\%$ ($A = 1.30$). ¿Cómo afecta esto al error relativo en consumo y capital? Explica la relación entre la magnitud de la perturbación respecto al estado estacionario base y la validez de las aproximaciones de primer orden.
"""))

# 11. BUENAS PRÁCTICAS
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 8. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento del Backend Computacional**: Las rutinas paramétricas, el cálculo de estado estacionario y los resolvedores dinámicos están aislados en el módulo `MacroAIComp.jl`, manteniendo el notebook limpio y enfocado exclusivamente en la didáctica y visualización.
2.  **Inicialización Inteligente (Smart Guessing)**: El resolvedor no lineal exacto utiliza la trayectoria de Blanchard-Khan linealizada como punto de partida, garantizando una convergencia instantánea y robusta.
3.  **Higiene del Repositorio**: El cuaderno se acoge a las directivas de control de versiones del repo limpiando salidas volátiles mediante `nbstripout` en `pre-commit`.
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

dir_path = 'practicas/09-ramsey/'
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, 'julia.ipynb')
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
