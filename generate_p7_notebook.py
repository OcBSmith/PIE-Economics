import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# Práctica P7: El Modelo de Equilibrio General Dinámico Básico (DGE)
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P7-v1.0
*   **Capítulo de Referencia**: Capítulo 8, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Desarrollar e interactuar con el modelo canónico de Equilibrio General Dinámico (DGE) en tiempo discreto, resolviendo y comparando la aproximación linealizada de Blanchard-Khan frente a la solución numérica no lineal exacta.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Comprender** la microfundamentación intertemporal de las decisiones de consumo y ahorro y su interacción con el sector productivo en equilibrio general.
2.  **Aplicar** el método de Blanchard-Khan para resolver y simular sistemas dinámicos lineales con expectativas racionales y variables forward-looking.
3.  **Analizar** el mecanismo de propagación intertemporal y la persistencia de shocks tecnológicos (TFP) sobre las variables macroeconómicas clave (Producción, Consumo, Inversión, Capital y Tasa de Interés).
4.  **Evaluar** la precisión y los límites de la aproximación linealizada frente a la solución no lineal exacta ante perturbaciones de distinta magnitud.
5.  **Identificar** discrepancias de programación y timing en modelos macroeconómicos computacionales complejos.
"""
    )
)

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# Esta celda se ejecuta silenciosamente. Si estás en Google Colab, instalará las librerías necesarias.
# En tu entorno local de desarrollo (venv), estas dependencias ya deberían estar instaladas.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets
"""))

# 3. IMPORTACIONES Y CONFIGURACIÓN
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Checkbox

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.dge import (
    DGEParameters,
    compute_steady_state,
    solve_blanchard_khan,
    solve_nonlinear_simulation
)
"""
    )
)

# 4. SECCIÓN 1: INTRODUCCIÓN TEÓRICA
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 1. El Modelo Canónico de Equilibrio General Dinámico (DGE)

Los modelos de Equilibrio General Dinámico (DGE), en sus versiones deterministas o estocásticas (DSGE), constituyen el núcleo de la macroeconomía moderna. A diferencia de los modelos IS-LM, los modelos DGE se basan en la **microfundamentación**: las ecuaciones de comportamiento se derivan directamente de los problemas de optimización intertemporal de los consumidores y las empresas.

### 1.1 Estructura del Modelo
El modelo canónico desarrollado en el Capítulo 8 representa una economía cerrada y perfectamente competitiva sin elecciones de ocio ($L_t = 1$):

1. **Problema del Consumidor:**
   Maximizar la utilidad descontada intertemporal:
   $$\max_{\{C_t\}} \sum_{t=0}^{\infty} \beta^t \ln(C_t)$$
   Sujeto a la restricción presupuestaria intertemporal:
   $$C_t + K_{t+1} = W_t + (R_t + 1 - \delta) K_t$$

2. **Problema de la Empresa:**
   Maximizar beneficios periodo a periodo:
   $$\max_{\{K_t, L_t\}} Y_t - W_t L_t - R_t K_t$$
   Sujeta a la función de producción Cobb-Douglas:
   $$Y_t = A_t K_t^\alpha L_t^{1-\alpha}$$

3. **Condición de Equilibrio (Vaciado de Mercados):**
   $$Y_t = C_t + I_t \quad \text{y} \quad K_{t+1} = (1-\delta) K_t + I_t$$

### 1.2 Sistema de Ecuaciones Reducido
El equilibrio competitivo dinámico de esta economía se reduce a un sistema de dos ecuaciones diferenciales en diferencias (una para la variable rígida/predeterminada $K_t$ y otra para la variable de expectativas/flexible $C_t$), alimentado por el proceso autorregresivo de la productividad (TFP):
1. **Dinámica del Capital:**
   $$K_{t+1} = (1-\delta)K_t + A_t K_t^\alpha - C_t$$
2. **Ecuación de Euler (Keynes-Ramsey):**
   $$C_{t+1} = \beta [ \alpha A_{t+1} K_{t+1}^{\alpha-1} + 1 - \delta ] C_t$$
3. **Proceso de la TFP:**
   $$\ln(A_t) = \rho \ln(A_{t-1}) + \epsilon_t$$
   Donde $\epsilon_t$ es un shock tecnológico exógeno y $\rho$ es la persistencia.

### 1.3 Estado Estacionario
Estableciendo $A = 1$ y eliminando los subíndices de tiempo en el sistema, obtenemos los valores de largo plazo:
$$\bar{R} = \frac{1 - \beta + \beta\delta}{\beta}, \quad \bar{K} = \left( \frac{\bar{R}}{\alpha} \right)^{\frac{1}{\alpha - 1}}, \quad \bar{Y} = \bar{K}^\alpha, \quad \bar{I} = \delta \bar{K}, \quad \bar{C} = \bar{Y} - \bar{I}$$
"""
    )
)

# 5. SECCIÓN 2: SIMULACIÓN INTERACTIVA DE SHOCK TECNOLÓGICO
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Simulación Interactiva: Shock Tecnológico Transitorio (TFP)

Imaginemos que la economía parte de su estado estacionario. En el periodo $t=1$, se produce un shock tecnológico transitorio positivo del $1\%$ ($\epsilon_1 = 0.01$) en la TFP, que decae de acuerdo con la persistencia $\rho = 0.8$.

Dado que la productividad aumenta, la economía experimenta un incremento inmediato en la capacidad de producción. Los consumidores, al tener expectativas de que la productividad y la tasa de interés serán más altas, aumentan su consumo inmediatamente ($C_1$ salta). Sin embargo, al ser el capital un factor rígido, no puede saltar en el periodo del shock ($K_1 = \bar{K}$). El aumento de producción se destina tanto a consumo como a inversión, lo que genera una acumulación gradual de capital físico. Este capital alcanzará su pico varios periodos después (efecto *hump-shape* o respuesta jorobada) antes de converger lentamente hacia el equilibrio inicial.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA EN 4 PANELES: SHOCK DE TFP
# ==============================================================================

def plot_dge_simulation(epsilon=0.01, rho_val=0.80, alpha_val=0.35, beta_val=0.96, delta_val=0.06):
    params = DGEParameters(alpha=alpha_val, beta=beta_val, delta=delta_val, rho=rho_val)
    
    # 1. Calcular el estado estacionario base
    ss = compute_steady_state(params)
    K0 = ss["K"]
    
    # 2. Generar la trayectoria del shock temporal de TFP
    T = 60
    a_hat = np.zeros(T)
    a_hat[0] = 0.0
    a_hat[1] = epsilon  # Shock ocurre en t=1 (índice 1)
    for t in range(2, T):
        a_hat[t] = rho_val * a_hat[t - 1]
    A_path = np.exp(a_hat)
    
    # 3. Resolver simulación con el resolvedor numérico no lineal exacto
    res = solve_nonlinear_simulation(params, K0, A_path, T=T)
    
    # 4. Graficar respuestas impulsivas en 4 paneles con estética premium
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    t_axis = np.arange(T)
    
    # Panel 1: Producción (Y)
    axs[0, 0].plot(t_axis, np.full(T, ss["Y"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[0, 0].plot(t_axis, res["Y"], color='#004C97', linewidth=2.5, label='Producción ($Y_t$)')
    axs[0, 0].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[0, 0].set_title('Evolución de la Producción (PIB)', fontsize=11, fontweight='bold', pad=10)
    axs[0, 0].set_xlabel('Período (t)', fontsize=9)
    axs[0, 0].set_ylabel('Y', fontsize=9)
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend(loc='best', fontsize=8)
    
    # Panel 2: Consumo (C)
    axs[0, 1].plot(t_axis, np.full(T, ss["C"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[0, 1].plot(t_axis, res["C"], color='#7A3E9F', linewidth=2.5, label='Consumo ($C_t$)')
    axs[0, 1].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[0, 1].set_title('Evolución del Consumo Privado', fontsize=11, fontweight='bold', pad=10)
    axs[0, 1].set_xlabel('Período (t)', fontsize=9)
    axs[0, 1].set_ylabel('C', fontsize=9)
    axs[0, 1].grid(True, linestyle=':', alpha=0.6)
    axs[0, 1].legend(loc='best', fontsize=8)
    
    # Panel 3: Inversión (I)
    axs[1, 0].plot(t_axis, np.full(T, ss["I"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[1, 0].plot(t_axis, res["I"], color='#D95319', linewidth=2.5, label='Inversión ($I_t$)')
    axs[1, 0].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[1, 0].set_title('Dinámica de Inversión', fontsize=11, fontweight='bold', pad=10)
    axs[1, 0].set_xlabel('Período (t)', fontsize=9)
    axs[1, 0].set_ylabel('I', fontsize=9)
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)
    axs[1, 0].legend(loc='best', fontsize=8)
    
    # Panel 4: Stock de Capital (K)
    axs[1, 1].plot(t_axis, np.full(T, K0), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[1, 1].plot(t_axis, res["K"], color='#8EAD3A', linewidth=2.5, label='Stock de Capital ($K_t$)')
    axs[1, 1].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[1, 1].set_title('Trayectoria de Acumulación de Capital', fontsize=11, fontweight='bold', pad=10)
    axs[1, 1].set_xlabel('Período (t)', fontsize=9)
    axs[1, 1].set_ylabel('K', fontsize=9)
    axs[1, 1].grid(True, linestyle=':', alpha=0.6)
    axs[1, 1].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Controles interactivos
interact(
    plot_dge_simulation,
    epsilon=FloatSlider(value=0.01, min=-0.05, max=0.05, step=0.005, description='Shock (ε1)'),
    rho_val=FloatSlider(value=0.80, min=0.0, max=0.99, step=0.05, description='Persist. (ρ)'),
    alpha_val=FloatSlider(value=0.35, min=0.20, max=0.50, step=0.05, description='Elasticidad (α)'),
    beta_val=FloatSlider(value=0.96, min=0.90, max=0.99, step=0.01, description='Descuento (β)'),
    delta_val=FloatSlider(value=0.06, min=0.01, max=0.15, step=0.01, description='Deprec. (δ)')
);
"""
    )
)

# 6. SECCIÓN 3: BK VS SOLUCIÓN EXACTA NO LINEAL
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 3. Límites de la Aproximación Lineal: Blanchard-Khan frente a Modelo No Lineal

El método de Blanchard-Khan (o cualquier método de linealización de primer orden) asume que la economía realiza fluctuaciones pequeñas en torno a su estado estacionario, de modo que la curvatura de las funciones de utilidad y producción puede aproximarse mediante tangencias de primer orden.

Sin embargo, si la economía sufre perturbaciones de gran magnitud (por ejemplo, una caída catastrófica de TFP o un shock tecnológico masivo), la aproximación lineal comete un **error de truncamiento** sistemático.

A continuación, puedes simular shocks de diferente envergadura y evaluar visualmente cómo difieren las soluciones calculadas mediante:
1. **Blanchard-Khan (Log-Linealizado)**: Resuelve el sistema linealizado mediante la descomposición de autovalores de la matriz $J$.
2. **SciPy fsolve (No Lineal)**: Resuelve el sistema completo de ecuaciones no lineales en niveles mediante métodos iterativos de Newton.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# COMPARACIÓN DINÁMICA: BLANCHARD-KHAN VS NO LINEAL
# ==============================================================================

def plot_solver_comparison(epsilon_shock=0.01, use_matlab_timing=False):
    params = DGEParameters()
    ss = compute_steady_state(params)
    K0 = ss["K"]
    
    T = 60
    a_hat = np.zeros(T)
    a_hat[0] = 0.0
    a_hat[1] = epsilon_shock
    for t in range(2, T):
        a_hat[t] = params.rho * a_hat[t - 1]
    A_path = np.exp(a_hat)
    
    # 1. Solución Blanchard-Khan
    res_bk = solve_blanchard_khan(params, K0, A_path, T=T)

    # 2. Solución No Lineal Exacta
    res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T=T)
    
    # Graficar comparación de Consumo y Capital
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    t_axis = np.arange(T)
    
    # Consumo
    axs[0].plot(t_axis, res_bk["C"], color='#7A3E9F', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Linealizado)')
    axs[0].plot(t_axis, res_nonlin["C"], color='#7A3E9F', linewidth=2.0, label='Exacto No Lineal')
    axs[0].set_title('Consumo ($C_t$): Comparación de resolvedores', fontsize=11, fontweight='bold')
    axs[0].set_xlabel('Período (t)')
    axs[0].set_ylabel('C')
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend()
    
    # Capital
    axs[1].plot(t_axis, res_bk["K"], color='#8EAD3A', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Linealizado)')
    axs[1].plot(t_axis, res_nonlin["K"], color='#8EAD3A', linewidth=2.0, label='Exacto No Lineal')
    axs[1].set_title('Capital ($K_t$): Comparación de resolvedores', fontsize=11, fontweight='bold')
    axs[1].set_xlabel('Período (t)')
    axs[1].set_ylabel('K')
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend()
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir discrepancia relativa
    diff_C = np.max(np.abs(res_bk["C"] - res_nonlin["C"])) / ss["C"] * 100
    diff_K = np.max(np.abs(res_bk["K"] - res_nonlin["K"])) / ss["K"] * 100
    print(f"Error relativo máximo en Consumo : {diff_C:.4f}%")
    print(f"Error relativo máximo en Capital  : {diff_K:.4f}%")

# Slider de comparación
interact(
    plot_solver_comparison,
    epsilon_shock=FloatSlider(value=0.01, min=-0.30, max=0.30, step=0.02, description='Shock TFP'),
    use_matlab_timing=Checkbox(value=False, description='Timing del libro')
);
"""
    )
)

# 7. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 4. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con el modelo de equilibrio general dinámico:

1.  **Mecanismo de Propagación del Shock**:
    *   Establece un shock tecnológico $\epsilon_1 = 0.01$ y una persistencia $\rho = 0.8$. Describe el patrón dinámico de las 4 variables graficadas en la simulación 1. ¿Por qué el consumo y la inversión saltan instantáneamente en $t=1$, mientras que el stock de capital responde con retraso?
    *   Reduce la persistencia a $\rho = 0.2$. ¿Cómo cambia la trayectoria de consumo y capital? Explica la relación entre la persistencia del shock tecnológico y la velocidad de acumulación de capital.
2.  **Límites de la Log-Linealización**:
    *   En la simulación 2, establece un shock de TFP de $\epsilon = 0.01$ (un shock estándar de $1\%$). Observa el error relativo máximo entre Blanchard-Khan y el resolvedor no lineal exacto. ¿Qué magnitud tiene?
    *   Incrementa el shock tecnológico a $\epsilon = 0.25$ (un shock masivo de productividad del $25\%$). ¿Qué ocurre con el error relativo en consumo y capital? Explica por qué la aproximación de primer orden de Blanchard-Khan pierde validez cuando las desviaciones respecto al estado estacionario son grandes.
3.  **Higiene IA y Validación cruzada**:
    *   Verifica que los valores de estado estacionario calculados por Python coincidan con la Tabla 8.2 del libro impreso ($\bar{K}=6.699$, $\bar{Y}=1.946$, $\bar{C}=1.544$, $\bar{R}=0.102$). Reporta el resultado en tu bitácora.
""")
)

# 8. BUENAS PRÁCTICAS APRENDER AQUÍ
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 5. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento Paramétrico**: El código de las rutinas matriciales y resolvedores de Blanchard-Khan y Newton no lineal están desacoplados en el módulo [dge.py](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/dge.py), importados de manera modular.
2.  **Corrección de Timing y Parámetros**: Hemos solucionado la discrepancia de indexación de TFP del código MATLAB impreso, ofreciendo una opción `use_matlab_timing` para que los estudiantes comprueben la equivalencia con la hoja del libro y con el modelo de Dynare correcto.
3.  **Higiene del Repositorio**: El cuaderno se somete automáticamente a `nbstripout` mediante hooks de `pre-commit` para evitar subir gráficos cargados y metadatos volátiles de Jupyter al control de versiones.
""")
)

# 9. ESCRIBIR EL ARCHIVO
os.makedirs(
    "c:/Users/AntonioRC/Desktop/PIE/practicas/07-equilibrio-general-dinamico/",
    exist_ok=True,
)
nbf.write(
    nb,
    "c:/Users/AntonioRC/Desktop/PIE/practicas/07-equilibrio-general-dinamico/python.ipynb",
)
print(
    "Notebook generado con éxito en practicas/07-equilibrio-general-dinamico/python.ipynb."
)
