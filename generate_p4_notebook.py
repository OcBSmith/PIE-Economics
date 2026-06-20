import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(nbf.v4.new_markdown_cell(r"""# Práctica P4: La Elección Óptima de Consumo-Ocio y Ahorro
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P4-v1.0
*   **Capítulo de Referencia**: Capítulo 5, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Analizar la decisión óptima conjunta de consumo-ahorro (decisión intertemporal) y de consumo-ocio (decisión intratemporal que define la oferta de trabajo) a lo largo de un ciclo de vida finito. Estudiar cómo responden el empleo y la acumulación de riqueza a cambios en la productividad salarial y las preferencias de los agentes.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Modelar** conjuntamente decisiones dinámicas intertemporales (ahorro) y estáticas intratemporales (oferta de trabajo).
2.  **Derivar** y comprender la condición de tangencia intratemporal: la tasa marginal de sustitución (TMS) entre consumo y ocio igualada al salario real.
3.  **Visualizar e Interpretar** el efecto renta y el efecto sustitución ante shocks salariales sobre la oferta de trabajo.
4.  **Resolver** sistemas de ecuaciones no lineales acoplados de tamaño $2T \times 2T$ en Python empleando `fsolve` y optimización convexa con `cvxpy`.
5.  **Analizar** la sensibilidad del modelo ante cambios en las preferencias por el ocio (parámetro $\gamma$) y en los rendimientos financieros ($R$).
"""))

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# Esta celda se ejecuta silenciosamente. Si estás en Google Colab, instalará las librerías necesarias.
# En tu entorno local de desarrollo (venv), estas dependencias ya deberían estar instaladas.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets cvxpy
"""))

# 3. IMPORTACIONES
nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
import cvxpy as cp
from ipywidgets import interact, FloatSlider

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.consumption_leisure import (
    ConsumptionLeisureParameters,
    solve_foc_fsolve,
    solve_direct_cvxpy
)
"""))

# 4. MARCO TEÓRICO
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. El Marco Teórico: Consumo, Ahorro y Oferta de Trabajo Endógena

En este modelo, el hogar obtiene satisfacción de dos bienes: el consumo ($C_t$) y el ocio ($O_t$). El ocio representa el tiempo discrecional no dedicado a actividades laborales. Normalizando el tiempo total diario a $1$, la restricción de tiempo es:

$$L_t + O_t = 1$$

Donde $L_t \in [0, 1]$ es la fracción de tiempo dedicada al trabajo. El problema de optimización intertemporal del hogar consiste en maximizar:

$$\max_{\{C_t, L_t\}_{t=0}^{T-1}} \sum_{t=0}^{T-1} \beta^t \left[ \gamma \ln(C_t) + (1-\gamma) \ln(1 - L_t) \right]$$

Donde $\gamma \in (0,1)$ representa el peso del consumo en la utilidad (y $1-\gamma$ representa la preferencia relativa por el ocio). 

### 1.1 Restricción Presupuestaria
La acumulación de activos financieros ($B_t$) está determinada por la restricción presupuestaria secuencial:

$$C_t + B_t = W_t L_t + (1+R_{t-1})B_{t-1}$$

Con condiciones inicial y terminal: $B_{-1} = 0$, $B_{T-1} = 0$. Aquí, el ingreso salarial $W_t L_t$ depende endógenamente de las horas trabajadas $L_t$.

### 1.2 Condiciones de Primer Orden (FOC)
El lagrangiano de este problema produce dos condiciones fundamentales:
1.  **Condición Intratemporal (Oferta de Trabajo):**
    $$(1-\gamma) C_t = \gamma (1-L_t) W_t$$
    Esta condición iguala la relación marginal de sustitución entre consumo y ocio con el coste de oportunidad del ocio (el salario real $W_t$). Despejando, la oferta de trabajo óptima es:
    $$L_t = 1 - \left(\frac{1-\gamma}{\gamma}\right)\frac{C_t}{W_t}$$
2.  **Condición Intertemporal (Ecuación de Euler):**
    $$C_{t+1} = \beta (1 + R_t) C_t$$
"""))

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# CALIBRACIÓN DE REFERENCIA (Capítulo 5 - Libro original)
# ==============================================================================

params = ConsumptionLeisureParameters()

print("CALIBRACIÓN BASE DE REFERENCIA:")
print("-" * 60)
print(f"  Lifespan (T)                     : {params.T} periodos")
print(f"  Factor de descuento (beta)       : {params.beta} (theta ≈ {((1-params.beta)/params.beta)*100:.2f}%)")
print(f"  Peso del consumo en utilidad (γ) : {params.gamma:.2f}")
print(f"  Tasa de interés real (R)         : {params.R*100:.2f}%")
print("-" * 60)
"""))

# 6. COMPARATIVA DE SOLVERS
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Solución Numérica: fsolve vs cvxpy

Para resolver este sistema, implementamos dos solvers:
1.  **`fsolve`**: Resuelve el sistema no lineal acoplado de tamaño $2T \times 2T$ (las $T-1$ ecuaciones de Euler, las $T$ condiciones de oferta de trabajo y la condición terminal de activos en cero).
    *   *Resolución de Errata:* Hemos corregido el error de indexación del código MATLAB del libro (`m5foc.m`), que skipeaba el índice residual $2T-1$ e indexaba un elemento fuera de rango en $2T+1$.
2.  **`cvxpy`**: Resuelve el problema mediante optimización convexa directa (Clarabel).
"""))

# 7. CÓDIGO DE EJECUCIÓN COMPARATIVA
nb.cells.append(nbf.v4.new_code_cell(r"""# Salario constante exógeno de W = 30
W_base = np.full(params.T, 30.0)

# Resolver mediante FOC (fsolve)
res_fsolve = solve_foc_fsolve(params, W_base)

# Resolver mediante Optimización Convexa (cvxpy)
res_cvxpy = solve_direct_cvxpy(params, W_base)

# Comparativa de resultados
print("COMPARACIÓN DE TRAYECTORIAS (fsolve vs cvxpy):")
print("-" * 75)
print(f"  Consumo Inicial C(0) [fsolve]   : {res_fsolve['C'][0]:.6f}")
print(f"  Consumo Inicial C(0) [cvxpy]    : {res_cvxpy['C'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [fsolve]   : {res_fsolve['L'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [cvxpy]    : {res_cvxpy['L'][0]:.6f}")
print(f"  Activos Finales B(T-1) [fsolve] : {res_fsolve['B'][-1]:.6e}")
print(f"  Activos Finales B(T-1) [cvxpy]  : {res_cvxpy['B'][-1]:.6e}")
print("-" * 75)

# Verificar máxima diferencia absoluta
diff_C = np.max(np.abs(res_fsolve["C"] - res_cvxpy["C"]))
diff_L = np.max(np.abs(res_fsolve["L"] - res_cvxpy["L"]))
print(f"Máxima diferencia absoluta en Consumo : {diff_C:.2e}")
print(f"Máxima diferencia absoluta en Trabajo : {diff_L:.2e}")
if diff_C < 1e-4 and diff_L < 1e-4:
    print("✅ ¡Los resolvedores numéricos son perfectamente equivalentes!")
else:
    print("❌ Discrepancia detectada entre solucionadores.")
"""))

# 8. SIMULACIÓN INTERACTIVA EN 3 PANELES
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Simulación Interactiva en 3 Paneles

Visualizaremos las trayectorias dinámicas resultantes de la simulación en **3 columnas**:
*   **Panel 1 (Consumo e Ingreso Salarial)**: Muestra el consumo óptimo $C_t$ contra el ingreso salarial endógeno $W_t L_t$.
*   **Panel 2 (Oferta de Trabajo y Ocio)**: Muestra la fracción de tiempo dedicada a trabajar $L_t$ y al ocio $O_t = 1 - L_t$.
*   **Panel 3 (Activos Financieros)**: Muestra el perfil de acumulación de riqueza y deuda ($B_t$). Las áreas coloreadas representan periodos de endeudamiento (naranja) o ahorro (azul).

Interactúa con los sliders para analizar los efectos renta y sustitución:
*   `beta`: Paciencia intertemporal.
*   `gamma`: Preferencia por el consumo vs. ocio (cuanto mayor es `gamma`, más valoran el consumo y más horas trabajan).
*   `R`: Tasa de interés de los ahorros.
*   `W`: Salario por unidad de tiempo.
"""))

# 9. CÓDIGO DE GRAFICACIÓN E INTERACTIVIDAD
nb.cells.append(nbf.v4.new_code_cell(r"""# ==============================================================================
# FUNCIÓN DE GRAFICACIÓN INTERACTIVA EN 3 PANELES
# ==============================================================================

def plot_consumption_leisure(beta_val=0.97, gamma_val=0.40, R_val=0.02, W_val=30.0):
    # Cargar parámetros configurados
    params_int = ConsumptionLeisureParameters(T=30, beta=beta_val, gamma=gamma_val, R=R_val)
    W = np.full(params_int.T, W_val)
    
    # Resolver
    res = solve_foc_fsolve(params_int, W)
    
    # Crear la figura de 3 paneles
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    t_axis = np.arange(params_int.T)
    
    # --- PANEL 1: CONSUMO E INGRESO SALARIAL ---
    axs[0].plot(t_axis, res["C"], color='#7A3E9F', linewidth=2.5, label='Consumo Óptimo (C)')
    axs[0].plot(t_axis, res["W_L"], color='#8EAD3A', linewidth=2.5, linestyle='--', label='Ingreso Salarial (W·L)')
    axs[0].set_title('Consumo e Ingreso Salarial', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Periodo (t)', fontsize=9)
    axs[0].set_ylabel('Unidades de Bienes', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # --- PANEL 2: OFERTA DE TRABAJO Y OCIO ---
    axs[1].plot(t_axis, res["L"], color='#E05A47', linewidth=2.5, label='Oferta de Trabajo (L)')
    axs[1].plot(t_axis, res["O"], color='#3BB193', linewidth=2.5, linestyle=':', label='Ocio (O = 1-L)')
    axs[1].set_title('Asignación del Tiempo (Trabajo vs Ocio)', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Periodo (t)', fontsize=9)
    axs[1].set_ylabel('Fracción de Tiempo', fontsize=9)
    axs[1].set_ylim(-0.05, 1.05)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    # --- PANEL 3: ACTIVOS FINANCIEROS (AHORRO Y DEUDA) ---
    axs[2].plot(t_axis, res["B"], color='#004C97', linewidth=2.5, label='Activos Financieros (B)')
    axs[2].fill_between(t_axis, res["B"], 0, where=(res["B"] >= 0), color='#004C97', alpha=0.15, label='Posición Acreedora')
    axs[2].fill_between(t_axis, res["B"], 0, where=(res["B"] < 0), color='#D95319', alpha=0.15, label='Posición Deudora')
    axs[2].axhline(0.0, color='black', linestyle=':', alpha=0.5)
    axs[2].set_title('Evolución de Activos Financieros', fontsize=11, fontweight='bold', pad=10)
    axs[2].set_xlabel('Periodo (t)', fontsize=9)
    axs[2].set_ylabel('Riqueza Neta', fontsize=9)
    axs[2].grid(True, linestyle=':', alpha=0.6)
    axs[2].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Configurar controles interactivos
interact(
    plot_consumption_leisure,
    beta_val=FloatSlider(value=0.97, min=0.90, max=0.999, step=0.01, description='Paciencia (β)'),
    gamma_val=FloatSlider(value=0.40, min=0.10, max=0.90, step=0.05, description='Consumo (γ)'),
    R_val=FloatSlider(value=0.02, min=-0.05, max=0.15, step=0.01, description='Interés (R)'),
    W_val=FloatSlider(value=30.0, min=10.0, max=100.0, step=5.0, description='Salario (W)')
);
"""))

# 10. CUADERNO DE BITÁCORA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones analíticas en tu Cuaderno de Bitácora tras interactuar con la simulación:

1.  **El Efecto Renta y Sustitución sobre el Trabajo**:
    *   Incrementa el salario exógeno $W$ de 30 a 60. ¿Cómo reacciona la oferta de trabajo inicial $L_0$?
    *   En la teoría microeconómica, un aumento de salario tiene dos efectos contrapuestos sobre el ocio: el **efecto sustitución** (el ocio es más caro, por lo que trabajo más) y el **efecto renta** (soy más rico, por lo que consumo más ocio). Dado que con utilidad logarítmica estos efectos se cancelan exactamente en el periodo inicial si la riqueza es constante, describe cómo cambia el perfil del trabajo a lo largo del ciclo vital y por qué.
2.  **El Peso de las Preferencias ($\gamma$)**:
    *   Establece $\gamma = 0.20$ (alta preferencia por el ocio) y luego $\gamma = 0.80$ (alta preferencia por consumir bienes). 
    *   Compara los niveles de empleo resultantes en el Panel 2. ¿Cómo se ajustan las curvas de consumo e ingresos salariales en el Panel 1 en respuesta a esta variación en la psicología del consumidor?
3.  **La Dinámica del Ahorro y la Tasa de Interés**:
    *   Fija $R = 10\%$ y describe la trayectoria de acumulación de activos financieros. ¿El individuo es deudor o acreedor la mayor parte de su vida?
    *   ¿Por qué el individuo reduce drásticamente su ocio (trabaja más) al principio de su ciclo de vida cuando la tasa de interés es muy elevada? Explica la ganancia intertemporal de ahorrar capital temprano.
"""))

# 11. BUENAS PRÁCTICAS
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento Paramétrico**: Las rutinas matemáticas y de simulación están completamente desacopladas de la interfaz visual, residiendo en `src/macroaicomp/models/consumption_leisure.py`.
2.  **Control de Calidad Automático**: Se ha verificado que la simulación es robusta mediante tests unitarios automatizados (`pytest`).
3.  **Control de Versiones Limpio**: Este cuaderno ha sido limpiado de metadatos volátiles mediante `nbstripout` antes de guardarse en el repositorio.
"""))

os.makedirs('c:/Users/AntonioRC/Desktop/PIE/practicas/04-consumo-ocio/', exist_ok=True)
nbf.write(nb, 'c:/Users/AntonioRC/Desktop/PIE/practicas/04-consumo-ocio/python.ipynb')
print("Notebook generado con éxito.")
