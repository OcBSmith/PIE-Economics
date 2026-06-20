import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""# Práctica P5: El Gobierno y la Política Fiscal
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P5-v1.0
*   **Capítulo de Referencia**: Capítulo 6, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Explorar el papel macroeconómico y distorsionador del sector público en una economía con agentes racionales de ciclo de vida finito. Estudiaremos:
    1. Impuestos no distorsionadores de suma fija (lump-sum) y la demostración computacional del **Principio de Equivalencia Ricardiana**.
    2. Impuestos distorsionadores directos e indirectos (sobre el consumo $\tau^c$, el trabajo $\tau^w$ y las rentas del capital $\tau^r$), y sus efectos sobre la asignación del tiempo y el ahorro.
    3. Un sistema de Seguridad Social de capitalización (ahorro forzoso) y su efecto de sustitución perfecta sobre el ahorro privado voluntario.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Analizar** la diferencia matemática y económica entre impuestos de suma fija (no distorsionadores) e impuestos distorsionadores.
2.  **Comprender** y verificar computacionalmente el Principio de Equivalencia Ricardiana en el comportamiento del consumo.
3.  **Simular** el impacto de las distorsiones impositivas sobre la oferta de trabajo y la trayectoria intertemporal de consumo y ahorro.
4.  **Modelar** un sistema de Seguridad Social de capitalización y comprender la sustitución perfecta entre ahorro forzoso y voluntario.
5.  **Resolver** de forma exacta equilibria descentralizados con impuestos empleando el resolvedor de FOCs (`fsolve`) y la optimización convexa equivalente (`cvxpy`).
""")
)

# 2. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# Esta celda se ejecuta silenciosamente. Si estás en Google Colab, instalará las librerías necesarias.
# En tu entorno local de desarrollo (venv), estas dependencias ya deberían estar instaladas.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets cvxpy
"""))

# 3. IMPORTACIONES
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
import cvxpy as cp
from ipywidgets import interact, FloatSlider, IntSlider, Checkbox

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.fiscal_policy import (
    FiscalPolicyParameters,
    solve_non_distortionary,
    solve_distortionary_foc,
    solve_distortionary_cvxpy,
    solve_social_security
)
"""
    )
)

# 4. SECCIÓN 1: IMPUESTOS NO DISTORSIONADORES
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 1. Impuestos de Suma Fija (Lump-Sum) y Equivalencia Ricardiana

Un impuesto es **no distorsionador** (lump-sum) si la carga impositiva es fija e independiente de las decisiones de los agentes. En este caso, el impuesto de ingresos exógenos es equivalente a un impuesto de suma fija porque el agente no puede alterar su base imponible (el salario es exógeno y no hay elección de ocio).

El problema del agente consiste en maximizar:
$$\max_{\{C_t\}_{t=0}^{T-1}} \sum_{t=0}^{T-1} \beta^t \ln(C_t)$$

Sujeto a la restricción presupuestaria secuencial:
$$C_t + B_t = (1-\tau^w_t) W_t + (1+R)B_{t-1} + G_t$$

Donde $\tau^w_t$ es la tasa impositiva y $G_t$ son las transferencias del gobierno.

### 1.1 El Principio de Equivalencia Ricardiana
Si el gobierno financia un gasto público devolviendo toda la recaudación de impuestos al consumidor mediante transferencias de suma fija ($G_t = \tau^w_t W_t$), la restricción presupuestaria en equilibrio se reduce a la de una economía libre de impuestos:
$$C_t + B_t = W_t + (1+R)B_{t-1}$$

En este caso, la trayectoria óptima de consumo y ahorro es **completamente insensible** a la tasa impositiva. Si las transferencias no se devuelven ($G_t = 0$), se produce un efecto renta puro: los agentes consumen y ahorran menos, pero la pendiente del consumo (la ecuación de Euler) permanece idéntica.
"""
    )
)

# 5. CÓDIGO INTERACTIVO SECCIÓN 1
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA: IMPUESTO DE SUMA FIJA Y EQUIVALENCIA RICARDIANA
# ==============================================================================

def plot_non_distortionary(tauw_val=0.40, return_transfers=True):
    # Calibración base: T = 30, beta = 0.97, R = 0.05
    params = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tauw=tauw_val)
    W = np.full(params.T, 10.0) # Salario constante exógeno de 10
    
    # 1. Resolver caso base sin impuestos
    params_no_tax = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tauw=0.0)
    res_base = solve_non_distortionary(params_no_tax, W)
    
    # 2. Resolver caso con impuestos impositivos
    res_tax = solve_non_distortionary(params, W, return_transfers=return_transfers)
    
    # Graficación
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    t_axis = np.arange(params.T)
    
    # Consumo
    axs[0].plot(t_axis, res_base["C"], color='black', linestyle='--', linewidth=2.0, label='Consumo sin impuestos')
    axs[0].plot(t_axis, res_tax["C"], color='#004C97', linewidth=2.5, label=f'Consumo con impuesto (tauw={tauw_val:.2f})')
    axs[0].set_title('Decisión de Consumo Óptimo', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Periodo (t)', fontsize=9)
    axs[0].set_ylabel('Consumo (C)', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # Ahorro
    axs[1].plot(t_axis, res_base["B"], color='black', linestyle='--', linewidth=2.0, label='Ahorro sin impuestos')
    axs[1].plot(t_axis, res_tax["B"], color='#D95319', linewidth=2.5, label=f'Ahorro con impuesto (tauw={tauw_val:.2f})')
    axs[1].axhline(0.0, color='black', linestyle=':', alpha=0.5)
    axs[1].set_title('Evolución de Activos Financieros', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Periodo (t)', fontsize=9)
    axs[1].set_ylabel('Activos (B)', fontsize=9)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Widget interactivo
interact(
    plot_non_distortionary,
    tauw_val=FloatSlider(value=0.40, min=0.0, max=0.80, step=0.05, description='Impuesto (τw)'),
    return_transfers=Checkbox(value=True, description='Devolver recaudación (G=T)')
);
"""
    )
)

# 6. SECCIÓN 2: IMPUESTOS DISTORSIONADORES
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Impuestos Distorsionadores (Consumo, Trabajo y Ahorro)

Cuando la oferta de trabajo es endógena (decisión intratemporal entre consumo y ocio) y el ahorro genera rentas financieras, las tasas impositivas sobre el consumo ($\tau^c$), el salario ($\tau^w$) y los rendimientos financieros ($\tau^r$) alteran los precios relativos.

El problema del agente consiste en maximizar:
$$\max_{\{C_t, L_t\}_{t=0}^{T-1}} \sum_{t=0}^{T-1} \beta^t \left[ \gamma \ln(C_t) + (1-\gamma) \ln(1 - L_t) \right]$$

Sujeto a la restricción presupuestaria distorsionada:
$$(1+\tau^c_t) C_t + B_t = (1-\tau^w_t) W_t L_t + [1 + (1-\tau^r_t) R] B_{t-1} + G_t$$

### 2.1 Canal de Distorsión
Las distorsiones de la política fiscal actúan directamente a través de las condiciones marginales:
1.  **Distorsión Intratemporal (Oferta de Trabajo):**
    $$(1-\tau^w_t) W_t (1-L_t) = \frac{1-\gamma}{\gamma} (1+\tau^c_t) C_t$$
    Un aumento de $\tau^w$ (impuesto al salario) o $\tau^c$ (impuesto al consumo) reduce la rentabilidad marginal de trabajar frente al ocio, desincentivando la oferta de trabajo ($L_t$ cae).
2.  **Distorsión Intertemporal (Ahorro):**
    $$(1+\tau^c_{t+1}) C_{t+1} = \beta [1 + (1-\tau^r_t)R] (1+\tau^c_t) C_t$$
    El impuesto sobre el capital ($\tau^r$) reduce el rendimiento neto del ahorro, lo que hace al consumidor más propenso a consumir hoy que mañana (la trayectoria de consumo se aplana y el ahorro cae).
"""
    )
)

# 7. COMPARATIVA DE SOLVERS P5
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# COMPARACIÓN NUMÉRICA: FOC (fsolve) vs OPTIMIZACIÓN DIRECTA (cvxpy)
# ==============================================================================

params_dist = FiscalPolicyParameters()
W_dist = np.full(params_dist.T, 100.0)

# 1. Resolver con FOC (fsolve)
res_foc = solve_distortionary_foc(params_dist, W_dist, return_transfers=False)

# 2. Resolver con CVXPY (Surrogate Convex Optimization)
res_cvxpy = solve_distortionary_cvxpy(params_dist, W_dist, return_transfers=False)

# Comparativa de resultados
print("VERIFICACIÓN DE CONSISTENCIA NUMÉRICA (fsolve vs cvxpy):")
print("-" * 75)
print(f"  Consumo Inicial C(0) [fsolve]   : {res_foc['C'][0]:.6f}")
print(f"  Consumo Inicial C(0) [cvxpy]    : {res_cvxpy['C'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [fsolve]   : {res_foc['L'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [cvxpy]    : {res_cvxpy['L'][0]:.6f}")
print(f"  Activos Finales B(T-1) [fsolve] : {res_foc['B'][-1]:.6e}")
print(f"  Activos Finales B(T-1) [cvxpy]  : {res_cvxpy['B'][-1]:.6e}")
print("-" * 75)

diff_C = np.max(np.abs(res_foc["C"] - res_cvxpy["C"]))
diff_L = np.max(np.abs(res_foc["L"] - res_cvxpy["L"]))
print(f"Máxima diferencia absoluta en Consumo : {diff_C:.2e}")
print(f"Máxima diferencia absoluta en Trabajo : {diff_L:.2e}")
if diff_C < 1e-4 and diff_L < 1e-4:
    print("✅ ¡Los resolvedores numéricos son perfectamente equivalentes!")
else:
    print("❌ Discrepancia detectada entre solucionadores.")
"""
    )
)

# 8. CÓDIGO GRAFICACIÓN INTERACTIVA SECCIÓN 2
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA EN 3 PANELES: IMPUESTOS DISTORSIONADORES
# ==============================================================================

def plot_distortionary(tauc_val=0.15, tauw_val=0.35, taur_val=0.25, return_transfers=False):
    params = FiscalPolicyParameters(
        T=30, beta=0.97, gamma=0.40, R=0.05,
        tauc=tauc_val, tauw=tauw_val, taur=taur_val
    )
    W = np.full(params.T, 100.0)
    
    # 1. Caso Base de Referencia (Sin impuestos)
    params_base = FiscalPolicyParameters(T=30, beta=0.97, gamma=0.40, R=0.05, tauc=0, tauw=0, taur=0)
    res_base = solve_distortionary_cvxpy(params_base, W, return_transfers=True)
    
    # 2. Caso impositivo distorsionador
    res_tax = solve_distortionary_cvxpy(params, W, return_transfers=return_transfers)
    
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    t_axis = np.arange(params.T)
    
    # Panel 1: Consumo
    axs[0].plot(t_axis, res_base["C"], color='black', linestyle='--', linewidth=2.0, label='Sin Impuestos')
    axs[0].plot(t_axis, res_tax["C"], color='#7A3E9F', linewidth=2.5, label='Con Impuestos')
    axs[0].set_title('Consumo de Bienes', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Periodo (t)', fontsize=9)
    axs[0].set_ylabel('Unidades de C', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # Panel 2: Oferta de Trabajo (L)
    axs[1].plot(t_axis, res_base["L"], color='black', linestyle='--', linewidth=2.0, label='Sin Impuestos')
    axs[1].plot(t_axis, res_tax["L"], color='#E05A47', linewidth=2.5, label='Con Impuestos')
    axs[1].set_title('Oferta de Trabajo (L)', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Periodo (t)', fontsize=9)
    axs[1].set_ylabel('Fracción de Tiempo Trabajado', fontsize=9)
    axs[1].set_ylim(-0.05, 1.05)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    # Panel 3: Activos Financieros (B)
    axs[2].plot(t_axis, res_base["B"], color='black', linestyle='--', linewidth=2.0, label='Sin Impuestos')
    axs[2].plot(t_axis, res_tax["B"], color='#004C97', linewidth=2.5, label='Con Impuestos')
    axs[2].fill_between(t_axis, res_tax["B"], 0, where=(res_tax["B"] >= 0), color='#004C97', alpha=0.15)
    axs[2].fill_between(t_axis, res_tax["B"], 0, where=(res_tax["B"] < 0), color='#D95319', alpha=0.15)
    axs[2].axhline(0.0, color='black', linestyle=':', alpha=0.5)
    axs[2].set_title('Acumulación de Activos', fontsize=11, fontweight='bold', pad=10)
    axs[2].set_xlabel('Periodo (t)', fontsize=9)
    axs[2].set_ylabel('Activos (B)', fontsize=9)
    axs[2].grid(True, linestyle=':', alpha=0.6)
    axs[2].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Controles interactivos
interact(
    plot_distortionary,
    tauc_val=FloatSlider(value=0.15, min=0.0, max=0.50, step=0.05, description='Consumo (τc)'),
    tauw_val=FloatSlider(value=0.35, min=0.0, max=0.80, step=0.05, description='Trabajo (τw)'),
    taur_val=FloatSlider(value=0.25, min=0.0, max=0.80, step=0.05, description='Capital (τr)'),
    return_transfers=Checkbox(value=False, description='Equilibrio G = Recaudación')
);
"""
    )
)

# 9. SECCIÓN 3: SEGURIDAD SOCIAL
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 3. El Sistema de Seguridad Social de Capitalización

En un sistema de Seguridad Social de capitalización, los trabajadores contribuyen obligatoriamente con una fracción $\tau^{ss}$ de su salario durante su periodo activo ($t < t^*$). Estas contribuciones se acumulan en un fondo de pensiones $D_t$ que obtiene rentabilidad a la tasa de interés de mercado $R$.

Al jubilarse ($t = t^*$), el individuo recibe el fondo acumulado como un pago único ($Pension$).

### 3.1 Sustitución Perfecta de Ahorro
En este modelo, el agente tiene previsión perfecta y libre acceso al mercado financiero (sin restricciones de liquidez). Por lo tanto, el ahorro forzoso de la Seguridad Social es un **sustituto perfecto** del ahorro privado voluntario.
Si el gobierno aumenta la tasa impositiva $\tau^{ss}$, el consumo óptimo del agente **no varía**. En su lugar, el agente reduce proporcionalmente su ahorro privado voluntario (llegando a ser negativo si es necesario tomar prestado contra el fondo de jubilación bloqueado) para mantener la misma trayectoria de consumo.
""")
)

# 10. CÓDIGO GRAFICACIÓN INTERACTIVA SECCIÓN 3
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA: SEGURIDAD SOCIAL Y ACTIVOS
# ==============================================================================

def plot_social_security(tau_ss_val=0.36, t_star_val=26):
    params = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tau_ss=tau_ss_val, t_star=t_star_val)
    
    # Wage profile: 10 en period 0, incrementando en 1 cada periodo hasta t_star-1. Cero después.
    W = np.zeros(params.T)
    for t in range(params.t_star):
        W[t] = 10.0 + t
        
    # 1. Caso sin Seguridad Social (tau_ss = 0)
    params_no_ss = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tau_ss=0.0, t_star=t_star_val)
    res_no_ss = solve_social_security(params_no_ss, W)
    
    # 2. Caso con Seguridad Social
    res_ss = solve_social_security(params, W)
    
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    t_axis = np.arange(params.T)
    
    # Panel 1: Consumo
    axs[0].plot(t_axis, res_no_ss["C"], color='black', linestyle='--', linewidth=2.0, label='Sin Seguridad Social')
    axs[0].plot(t_axis, res_ss["C"], color='#7A3E9F', linewidth=2.5, label='Con Seguridad Social')
    axs[0].axvline(t_star_val, color='grey', linestyle=':', alpha=0.8, label='Jubilación')
    axs[0].set_title('Decisión de Consumo Óptimo', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Periodo (t)', fontsize=9)
    axs[0].set_ylabel('Consumo (C)', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # Panel 2: Ahorro Privado (Voluntario)
    axs[1].plot(t_axis, res_no_ss["B"], color='black', linestyle='--', linewidth=2.0, label='Sin Seguridad Social')
    axs[1].plot(t_axis, res_ss["B"], color='#D95319', linewidth=2.5, label='Ahorro Privado (B)')
    axs[1].fill_between(t_axis, res_ss["B"], 0, where=(res_ss["B"] < 0), color='#D95319', alpha=0.15, label='Deuda Privada')
    axs[1].axhline(0.0, color='black', linestyle=':', alpha=0.5)
    axs[1].axvline(t_star_val, color='grey', linestyle=':', alpha=0.8)
    axs[1].set_title('Activos Privados (Ahorro Voluntario)', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Periodo (t)', fontsize=9)
    axs[1].set_ylabel('Activos (B)', fontsize=9)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    # Panel 3: Fondo de Pensiones de la Seguridad Social (Forzoso)
    axs[2].plot(t_axis, res_ss["D"], color='#8EAD3A', linewidth=2.5, label='Fondo de Pensiones (D)')
    axs[2].fill_between(t_axis, res_ss["D"], 0, color='#8EAD3A', alpha=0.15)
    axs[2].axvline(t_star_val, color='grey', linestyle=':', alpha=0.8)
    axs[2].set_title('Acumulación en Fondo de Pensiones', fontsize=11, fontweight='bold', pad=10)
    axs[2].set_xlabel('Periodo (t)', fontsize=9)
    axs[2].set_ylabel('Fondo de SS (D)', fontsize=9)
    axs[2].grid(True, linestyle=':', alpha=0.6)
    axs[2].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Controles interactivos
interact(
    plot_social_security,
    tau_ss_val=FloatSlider(value=0.36, min=0.0, max=0.60, step=0.05, description='Cotización (τss)'),
    t_star_val=IntSlider(value=26, min=15, max=28, step=1, description='Jubilación (t*)')
);
"""
    )
)

# 11. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 4. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con las simulaciones de política fiscal:

1.  **Análisis de Equivalencia Ricardiana**:
    *   Activa la casilla `Devolver recaudación` en la simulación 1. Cambia el impuesto $\tau^w$ de 0 a 0.60. ¿Qué le ocurre al consumo en el panel de la izquierda? Explica detalladamente en base a la teoría microeconómica por qué no cambia.
    *   Desactiva la casilla `Devolver recaudación`. ¿Cómo responde el consumo y el ahorro? ¿Por qué la pendiente temporal del consumo sigue siendo positiva y con el mismo crecimiento relativo?
2.  **Efectos del Menú Fiscal Distorsionador**:
    *   En la simulación 2, establece `Equilibrio G = Recaudación` en `False`. Incrementa el impuesto sobre el trabajo $\tau^w$ de 0.0 a 0.50. ¿Cómo reacciona la oferta de trabajo $L_t$? ¿Por qué?
    *   Establece ahora un impuesto al consumo $\tau^c$ de 0.30 manteniendo $\tau^w = 0.0$. ¿Qué diferencia observas en el impacto sobre la oferta de trabajo respecto a $\tau^w$? ¿A qué se debe esto?
    *   Incrementa el impuesto al capital $\tau^r$ a 0.60. Observa el gráfico de Consumo. ¿Por qué la trayectoria se vuelve más plana (horizontal)? Explica el efecto intertemporal de la pérdida de interés real.
3.  **Seguridad Social e Implicaciones de Ahorro**:
    *   En la simulación 3, aumenta la cotización obligatoria $\tau^{ss}$ de 0.0 a 0.45. ¿Cambia el consumo óptimo del agente?
    *   Describe qué le ocurre a los activos privados (Panel 2) durante el periodo de vida laboral activa (antes de $t^* = 26$). ¿Por qué los activos privados caen a niveles fuertemente negativos (deuda)? Explica la lógica de "sustitución de ahorro" bajo previsión perfecta.
""")
)

# 12. BUENAS PRÁCTICAS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 5. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento Paramétrico**: Las rutinas matemáticas y de simulación están completamente desacopladas de la interfaz visual, residiendo en `src/macroaicomp/models/fiscal_policy.py`.
2.  **Modelización Equivalente de Equilibria**: La resolución de CVXPY para el caso de transferencias devueltas ha sido implementada mediante un modelo equivalente surrogate en un solo paso, optimizando estabilidad numérica y eficiencia de cálculo.
3.  **Control de Versiones Limpio**: Este cuaderno ha sido limpiado de metadatos volátiles mediante `nbstripout` antes de guardarse en el repositorio.
""")
)

os.makedirs(
    "c:/Users/AntonioRC/Desktop/PIE/practicas/05-gobierno-fiscal/", exist_ok=True
)
nbf.write(
    nb, "c:/Users/AntonioRC/Desktop/PIE/practicas/05-gobierno-fiscal/python.ipynb"
)
print("Notebook generado con éxito en practicas/05-gobierno-fiscal/python.ipynb.")
