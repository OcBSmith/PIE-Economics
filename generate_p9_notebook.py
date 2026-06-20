import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# Práctica P9: El Modelo de Crecimiento Óptimo de Ramsey
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P9-v1.0
*   **Capítulo de Referencia**: Capítulo 10, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Resolver e interactuar con el modelo canónico de crecimiento óptimo de Ramsey-Cass-Koopmans en tiempo discreto, calculando las condiciones de estabilidad de punto de silla, los autovalores jacobianos, la condición de salto de la variable forward-looking (Consumo) y contrastando la solución linealizada frente a la solución no lineal exacta.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Comprender** la microfundamentación intertemporal del crecimiento óptimo bajo vida infinita (enfoque de dinastías familiares).
2.  **Derivar** y entender la Regla de Keynes-Ramsey en tiempo discreto y cómo gobierna las decisiones de consumo-ahorro.
3.  **Analizar** la estabilidad del sistema dinámico mediante la descomposición en autovalores, comprobando que se cumple la condición de punto de silla.
4.  **Calcular** analíticamente el coeficiente de salto ($\theta$) de la variable flexible (consumo) ante perturbaciones estructurales.
5.  **Simular** y comparar el impacto dinámico de shocks tecnológicos (TFP) y de preferencias (paciencia/tasa de descuento $\beta$).
6.  **Evaluar** la precisión del resolvedor linealizado de Blanchard-Khan frente a la solución numérica no lineal exacta (`fsolve`) ante shocks de distinta envergadura.
"""))

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# Esta celda se ejecuta silenciosamente. Si estás en Google Colab, instalará las librerías necesarias.
# En tu entorno local de desarrollo (venv), estas dependencias ya deberían estar instaladas.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets
"""))

# 3. IMPORTACIONES Y CONFIGURACIÓN
nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.ramsey import (
    RamseyParameters,
    compute_ramsey_steady_state,
    compute_ramsey_transition_matrix,
    solve_ramsey_linearized,
    solve_ramsey_nonlinear
)
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

# 6. SIMULACIÓN INTERACTIVA DE SHOCKS EN RAMSEY
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Simulación Interactiva: Transición ante Shocks de Productividad y Preferencias

A continuación, simularemos la economía partiendo del estado estacionario calibrado en el libro ($\alpha=0.35, \beta=0.97, \delta=0.06, n=0.02$). En el período $t = 5$, ocurre un shock estructural permanente. 

Puedes mover el control interactivo para simular un shock de productividad ($A_1$) o de paciencia ($\beta_1$), y observar el ajuste en tiempo real.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA DEL SHOCK EN RAMSEY
# ==============================================================================

def plot_ramsey_simulation(A_final=1.05, beta_final=0.97):
    params = RamseyParameters()
    ss_init = compute_ramsey_steady_state(params)
    
    T = 80
    t_shock = 5
    
    # Resolver la trayectoria linealizada
    res = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_final=A_final,
        n_final=params.n,
        beta_final=beta_final,
        T=T,
        t_shock=t_shock
    )
    
    # Calcular el nuevo steady state esperado
    params_new = RamseyParameters(alpha=params.alpha, beta=beta_final, delta=params.delta, n=params.n, A=A_final)
    ss_final = compute_ramsey_steady_state(params_new)
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    t_axis = np.arange(T)
    
    # Panel 1: Producción per cápita (y_t)
    axs[0, 0].plot(t_axis, res["y"], color='#004C97', linewidth=2.5, label='Trayectoria (y_t)')
    axs[0, 0].axhline(ss_init["y"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[0, 0].axhline(ss_final["y"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[0, 0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0, 0].set_title('Evolución de la Producción per cápita', fontsize=11, fontweight='bold')
    axs[0, 0].set_xlabel('Períodos')
    axs[0, 0].set_ylabel('y')
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend()
    
    # Panel 2: Stock de Capital per cápita (k_t)
    axs[0, 1].plot(t_axis, res["k"], color='#8EAD3A', linewidth=2.5, label='Trayectoria (k_t)')
    axs[0, 1].axhline(ss_init["k"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[0, 1].axhline(ss_final["k"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[0, 1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0, 1].set_title('Trayectoria de Capital per cápita', fontsize=11, fontweight='bold')
    axs[0, 1].set_xlabel('Períodos')
    axs[0, 1].set_ylabel('k')
    axs[0, 1].grid(True, linestyle=':', alpha=0.6)
    axs[0, 1].legend()
    
    # Panel 3: Consumo per cápita (c_t)
    axs[1, 0].plot(t_axis, res["c"], color='#7A3E9F', linewidth=2.5, label='Trayectoria (c_t)')
    axs[1, 0].axhline(ss_init["c"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[1, 0].axhline(ss_final["c"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[1, 0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1, 0].set_title('Respuesta de Consumo per cápita (Salto)', fontsize=11, fontweight='bold')
    axs[1, 0].set_xlabel('Períodos')
    axs[1, 0].set_ylabel('c')
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)
    axs[1, 0].legend()
    
    # Panel 4: Inversión per cápita (i_t)
    axs[1, 1].plot(t_axis, res["i"], color='#D95319', linewidth=2.5, label='Trayectoria (i_t)')
    axs[1, 1].axhline(ss_init["i"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[1, 1].axhline(ss_final["i"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[1, 1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1, 1].set_title('Evolución de la Inversión per cápita', fontsize=11, fontweight='bold')
    axs[1, 1].set_xlabel('Períodos')
    axs[1, 1].set_ylabel('i')
    axs[1, 1].grid(True, linestyle=':', alpha=0.6)
    axs[1, 1].legend()
    
    plt.tight_layout()
    plt.show()

# Controles interactivos
interact(
    plot_ramsey_simulation,
    A_final=FloatSlider(value=1.05, min=0.90, max=1.20, step=0.01, description='TFP (A)'),
    beta_final=FloatSlider(value=0.97, min=0.92, max=0.99, step=0.01, description='Descuento (β)')
);
"""))

# 7. COMPARACIÓN DE SOLVER BK VS FSOLVE NO LINEAL
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Precisión de Resolvedores: Blanchard-Khan frente a Solución No Lineal

El resolvedor de Blanchard-Khan asume una linealización de primer orden alrededor del estado estacionario y es altamente preciso para shocks de baja envergadura. Para shocks de gran tamaño, sin embargo, el error acumulado por la curvatura puede ser relevante.

A continuación, compara las trayectorias calculadas mediante **Blanchard-Khan (BK)** y por el resolvedor **No Lineal Exacto (SciPy fsolve)** ante perturbaciones de distinta envergadura.
"""))

nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# COMPARACIÓN DINÁMICA: BLANCHARD-KHAN VS NO LINEAL
# ==============================================================================

def plot_ramsey_comparison(A_shock=1.05):
    params = RamseyParameters()
    ss_init = compute_ramsey_steady_state(params)
    
    T = 80
    t_shock = 5
    
    A_path = np.full(T, 1.00)
    A_path[t_shock:] = A_shock
    n_path = np.full(T, 0.02)
    
    # 1. Solución linealizada de BK
    res_lin = solve_ramsey_linearized(
        params,
        ss_init["k"],
        A_final=A_shock,
        n_final=params.n,
        beta_final=params.beta,
        T=T,
        t_shock=t_shock
    )
    
    # 2. Solución exacta no lineal de fsolve
    res_nonlin = solve_ramsey_nonlinear(
        params,
        ss_init["k"],
        A_path,
        n_path,
        T=T,
        t_shock=t_shock
    )
    
    # Graficar
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    t_axis = np.arange(T)
    
    # Consumo
    axs[0].plot(t_axis, res_lin["c"], color='#7A3E9F', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Lineal)')
    axs[0].plot(t_axis, res_nonlin["c"], color='#7A3E9F', linewidth=2.0, label='Exacto No Lineal')
    axs[0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0].set_title('Consumo per cápita (c_t)', fontsize=11, fontweight='bold')
    axs[0].set_xlabel('Períodos')
    axs[0].set_ylabel('c')
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend()
    
    # Capital
    axs[1].plot(t_axis, res_lin["k"], color='#8EAD3A', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Lineal)')
    axs[1].plot(t_axis, res_nonlin["k"], color='#8EAD3A', linewidth=2.0, label='Exacto No Lineal')
    axs[1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1].set_title('Capital per cápita (k_t)', fontsize=11, fontweight='bold')
    axs[1].set_xlabel('Períodos')
    axs[1].set_ylabel('k')
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend()
    
    plt.tight_layout()
    plt.show()
    
    # Error relativo máximo
    err_c = np.max(np.abs(res_lin["c"] - res_nonlin["c"])) / ss_init["c"] * 100
    err_k = np.max(np.abs(res_lin["k"] - res_nonlin["k"])) / ss_init["k"] * 100
    print(f"Error relativo máximo en Consumo : {err_c:.4f}%")
    print(f"Error relativo máximo en Capital  : {err_k:.4f}%")

# Slider
interact(
    plot_ramsey_comparison,
    A_shock=FloatSlider(value=1.05, min=0.70, max=1.30, step=0.02, description='TFP final')
);
"""))

# 8. CUADERNO DE BITÁCORA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con el simulador del modelo de crecimiento óptimo de Ramsey:

1.  **Dinámica de Consumo y Ahorro en Ramsey (Comparación con Solow-Swan)**:
    *   Simula un incremento permanente de la TFP del $5\%$ ($A = 1.05$, Sección 3). Describe cómo responden el consumo y la inversión en el momento del impacto ($t=5$). ¿Por qué el consumo salta instantáneamente en Ramsey, en lugar de mantenerse constante como ocurriría bajo una tasa de ahorro fija?
    *   Explica qué motiva a los hogares representativos a aumentar su inversión y sacrificar consumo relativo a largo plazo para acumular más capital.
2.  **Shock de Paciencia (Preferencia Intertemporal $\beta$)**:
    *   Simula un incremento del factor de descuento $\beta$ de $0.97$ a $0.98$ (Sección 3). Describe el comportamiento del consumo y la inversión en el período del shock $t=5$. ¿Por qué se produce una caída instantánea del consumo? ¿Cómo compensa este "sacrificio" de corto plazo al bienestar dinámico de los consumidores en el largo plazo?
3.  **Límites de la linealización**:
    *   En la Sección 4, establece un shock de TFP estándar del $5\%$ ($A = 1.05$) y anota el error relativo máximo entre el resolvedor de Blanchard-Khan y el no lineal exacto.
    *   Aplica un shock masivo del $30\%$ ($A = 1.30$). ¿Cómo afecta esto al error relativo en consumo y capital? Explica la relación entre la magnitud de la perturbación respecto al estado estacionario base y la validez de las aproximaciones de primer orden.
"""))

# 9. BUENAS PRÁCTICAS APRENDER AQUÍ
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento del Backend Computacional**: Las rutinas paramétricas, el cálculo de estado estacionario y los resolvedores dinámicos están aislados en el módulo [`ramsey.py`](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/ramsey.py), manteniendo el notebook limpio y enfocado exclusivamente en la didáctica y visualización.
2.  **Inicialización Inteligente (Smart Guessing)**: El resolvedor no lineal exacto (`fsolve`) utiliza la trayectoria de Blanchard-Khan linealizada como punto de partida, garantizando una convergencia instantánea y robusta.
3.  **Higiene del Repositorio**: El cuaderno se acoge a las directivas de control de versiones del repo limpiando salidas volátiles mediante `nbstripout` en `pre-commit`.
"""))

# 10. ESCRIBIR EL ARCHIVO
os.makedirs('c:/Users/AntonioRC/Desktop/PIE/practicas/09-ramsey/', exist_ok=True)
nbf.write(nb, 'c:/Users/AntonioRC/Desktop/PIE/practicas/09-ramsey/python.ipynb')
print("Notebook generado con éxito en practicas/09-ramsey/python.ipynb.")
