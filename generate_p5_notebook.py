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

# 2. BIENVENIDA Y GUÍA RÁPIDA
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""> **👋 BIENVENIDA A LA PRÁCTICA - LEER ANTES DE EMPEZAR**
>
> *   **¿Nunca has usado Jupyter?** No te preocupes. Este cuaderno es interactivo. Haz clic en cualquier celda de código y pulsa **`Shift + Enter`** para ejecutarla. Ve de arriba a abajo en orden.
> *   **¿Se ha congelado o sale un asterisco `[*]` eterno?** Ve al menú superior y dale a `Kernel` ➔ `Restart`.
> *   **El objetivo** de esta práctica es que juegues con la economía. Cambia los números del código que representan impuestos, dinero o tecnología, vuelve a ejecutar y mira los gráficos. ¡No puedes romper nada!
>

> *   **📋 Antes de empezar**, consulta ' (en esta misma carpeta): objetivos, tiempo estimado y conocimientos previos de esta práctica." + "
" + "
" + "### 🕹️ GUÍA RÁPIDA DE INICIO - Gobierno y Política Fiscal
*   **¿Qué estamos haciendo aquí?** Estudiando cómo afectan los impuestos del gobierno a las decisiones de las personas.
*   **Impuestos Distorsionadores:** Cuando el gobierno cobra impuestos sobre el trabajo, la gente decide trabajar menos porque se queda con menos dinero neto.
*   **¡Prueba esto!** Incrementa la tasa impositiva (los impuestos) en el modelo y observa la caída en el consumo y en las horas de trabajo.
"""
    )
)

# 3. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# %%capture suprime la salida de la celda. "import sys; 'google.colab' in
# sys.modules" detecta si estamos en Google Colab. Si es Colab, !pip install
# descarga las librerías. En local (venv) ya están instaladas: no hace nada.
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

# "import X as np" trae la librería X con un alias corto (np, plt, cp) para
# no teclear el nombre completo cada vez. "from X import Y" es más selectivo:
# trae solo la función/clase Y del módulo X. Así el notebook se limita a
# llamar funciones ya probadas (ver Sección 6, Buenas Prácticas).

# Librerías de terceros (instaladas con pip)
import numpy as np                      # cálculo numérico: vectores, matrices, álgebra lineal
import matplotlib.pyplot as plt         # gráficos 2D con estilo MATLAB
import cvxpy as cp                      # optimización convexa
from ipywidgets import interact, FloatSlider, IntSlider, Checkbox  # widgets interactivos

# sys.path.append añade una carpeta al PATH para que "import" la encuentre.
# "../" sube dos niveles desde practicas/05-gobierno-fiscal/ hasta la raíz
# del repo, donde está src/.
import sys
sys.path.append('../../src')

# Proyecto (src/macroaicomp/): la lógica fiscal del modelo está en
# fiscal_policy.py, separada de la visualización. Los nombres entre
# paréntesis se podrán usar como si estuvieran definidos en este cuaderno.
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

# "def nombre(argumentos):" define una FUNCIÓN reutilizable que no se
# ejecuta al escribirla, solo cuando interact() la llame al mover un slider.
# return_transfers=True significa que el gobierno DEVUELVE toda la
# recaudación como transferencia (G=T): si el agente recibe de vuelta lo
# mismo que pagó, el impuesto no debería alterar sus decisiones — eso es la
# Equivalencia Ricardiana que verificamos en esta celda.
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

# 6. ORÁCULO: VERIFICACIÓN DE RESULTADOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro (Capítulo 6) y
reproducidos por el código MATLAB del Apéndice J, recogidos en
`oraculo.md`:

**Calibración base común (β=0.97, R=0.05, γ=0.40, T=30):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| **Sección 1 — Equivalencia Ricardiana** | |
| τw=0.40 con devolución vs sin impuestos | C y B idénticos (rtol 1e−6) |
| τw=0.40 SIN devolución | C menor que sin impuestos |
| **Sección 2 — Impuestos distorsionadores** | |
| FOC vs cvxpy (return_transfers=True y False) | C, L, B idénticos (rtol 1e−4) |
| τw↑ (0.10→0.40) o τc↑ (0.0→0.30) | L media disminuye |
| **Sección 3 — Impuesto al capital** | |
| τr↑ (0.0→0.50) | Activos medios menores, pendiente C más plana |
| **Sección 4 — Seguridad Social** | |
| SS (τss=0.36, t*=26) vs modelo sin SS | Consumo idéntico (rtol 1e−6) |
| Ahorro privado B durante vida laboral | Negativo al inicio |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""
    )
)

# 7. ASERCIÓN: EQUIVALENCIA RICARDIANA (Sección 1)
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN SECCIÓN 1: EQUIVALENCIA RICARDIANA (Apéndice J del libro)
# ==============================================================================

# np.testing.assert_allclose(a, b, rtol=...) compara con tolerancia y SOLO
# lanza error si la diferencia supera el margen. Si pasa, es silencioso
# (PUNTO DE CONTROL). La Equivalencia Ricardiana predice que si el gobierno
# devuelve TODO lo recaudado como transferencia, el agente descuenta el
# impuesto futuro y NO cambia su consumo ni su ahorro: C y B deben ser
# IDÉNTICOS al caso sin impuestos (rtol=1e-6). Esta celda lo comprueba.

W10 = np.full(30, 10.0)

# 1. Caso base sin impuestos
params_no_tax = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tauw=0.0)
res_no_tax = solve_non_distortionary(params_no_tax, W10)

# 2. Equivalencia Ricardiana: tauw=0.40 CON devolución => C y B idénticos al caso sin impuestos
params_tax_ret = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tauw=0.40)
res_tax_ret = solve_non_distortionary(params_tax_ret, W10, return_transfers=True)
np.testing.assert_allclose(res_no_tax["C"], res_tax_ret["C"], rtol=1e-6)
np.testing.assert_allclose(res_no_tax["B"], res_tax_ret["B"], rtol=1e-6)
print("OK (Ricardiano 1/2): Con devolución, C y B son idénticos al caso sin impuestos (rtol=1e-6).")

# 3. Sin devolución: C debe ser menor que en el caso sin impuestos
res_tax_noret = solve_non_distortionary(params_tax_ret, W10, return_transfers=False)
assert np.all(res_tax_noret["C"] < res_no_tax["C"]), "Sin devolución, C debe ser menor"
print("OK (Ricardiano 2/2): Sin devolución, C es menor que en el caso sin impuestos.")
"""
    )
)

# 8. SECCIÓN 2: IMPUESTOS DISTORSIONADORES
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 3. Impuestos Distorsionadores (Consumo, Trabajo y Ahorro)

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

# solve_distortionary_foc() resuelve las condiciones de primer orden con un
# solver de sistemas no lineales. solve_distortionary_cvxpy() formula el
# problema como optimización convexa y deja que el solver encuentre la
# solución. Son DOS caminos hacia el mismo resultado: si coinciden (diff <
# 1e-4), el modelo está bien implementado en ambos métodos.

params_dist = FiscalPolicyParameters()  # valores por defecto
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

# 9. ASERCIÓN SECCIÓN 2: EQUIVALENCIA FOC-CVXPY Y DISTORSIONES
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN SECCIÓN 2: EQUIVALENCIA FOC-CVXPY Y DISTORSIONES (Apéndice J)
# ==============================================================================

# --- Equivalencia FOC vs cvxpy CON return_transfers=True ---
res_foc_ret = solve_distortionary_foc(params_dist, W_dist, return_transfers=True)
res_cvxpy_ret = solve_distortionary_cvxpy(params_dist, W_dist, return_transfers=True)
np.testing.assert_allclose(res_foc_ret["C"], res_cvxpy_ret["C"], rtol=1e-4)
np.testing.assert_allclose(res_foc_ret["L"], res_cvxpy_ret["L"], rtol=1e-4)
np.testing.assert_allclose(res_foc_ret["B"], res_cvxpy_ret["B"], rtol=1e-4, atol=1e-6)
print("OK (Dist 1/3): FOC y cvxpy equivalentes con return_transfers=True (rtol=1e-4).")

# Verificar que también con return_transfers=False (datos ya calculados en celda anterior)
np.testing.assert_allclose(res_foc["C"], res_cvxpy["C"], rtol=1e-4)
np.testing.assert_allclose(res_foc["L"], res_cvxpy["L"], rtol=1e-4)
np.testing.assert_allclose(res_foc["B"], res_cvxpy["B"], rtol=1e-4, atol=1e-6)
print("OK (Dist 2/3): FOC y cvxpy equivalentes con return_transfers=False (rtol=1e-4).")

# --- Distorsión laboral: mayor tauw => menor L media ---
# La intuición: un impuesto al salario reduce el pago neto por hora
# trabajada, así que el agente sustituye trabajo por ocio (efecto
# sustitución). Comprobamos que L media baja al subir tauw de 0.10 a 0.40.
res_tauw_low = solve_distortionary_foc(
    FiscalPolicyParameters(T=30, beta=0.97, gamma=0.40, R=0.05, tauw=0.10),
    W_dist, return_transfers=True
)
res_tauw_high = solve_distortionary_foc(
    FiscalPolicyParameters(T=30, beta=0.97, gamma=0.40, R=0.05, tauw=0.40),
    W_dist, return_transfers=True
)
mean_L_low = np.mean(res_tauw_low["L"])
mean_L_high = np.mean(res_tauw_high["L"])
print(f"L media con tauw=0.10: {mean_L_low:.6f}")
print(f"L media con tauw=0.40: {mean_L_high:.6f}")
assert mean_L_high < mean_L_low, "Mayor tauw debe reducir la oferta de trabajo media"
print("OK (Dist 3/3): L media disminuye al subir tauw de 0.10 a 0.40, coincide con el oraculo.")
"""
    )
)

# 10. ASERCIÓN SECCIÓN 3: IMPUESTO AL CAPITAL
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN SECCIÓN 3: IMPUESTO AL CAPITAL (Apéndice J)
# ==============================================================================

# El impuesto al capital (taur) reduce el rendimiento neto del ahorro:
# beta*(1+(1-taur)*R) baja, así que el consumo futuro es menos atractivo.
# Predicciones: 1) Activos medios menores (se ahorra menos). 2) Pendiente
# del consumo más plana (crece menos en el tiempo). Esta celda verifica
# ambas direcciones comparando taur=0.0 contra taur=0.50.

# tau_r=0.0 vs tau_r=0.50 SIN devolución
res_taur0 = solve_distortionary_foc(
    FiscalPolicyParameters(T=30, beta=0.97, gamma=0.40, R=0.05, taur=0.0),
    W_dist, return_transfers=False
)
res_taur50 = solve_distortionary_foc(
    FiscalPolicyParameters(T=30, beta=0.97, gamma=0.40, R=0.05, taur=0.50),
    W_dist, return_transfers=False
)
mean_B_taur0 = np.mean(res_taur0["B"])
mean_B_taur50 = np.mean(res_taur50["B"])
print(f"Activos medios con taur=0.00: {mean_B_taur0:.6f}")
print(f"Activos medios con taur=0.50: {mean_B_taur50:.6f}")
assert mean_B_taur50 < mean_B_taur0, "Mayor taur debe reducir los activos medios (ahorro desincentivado)"
print("OK (Capital 1/2): Activos medios menores con taur=0.50.")

# Pendiente del consumo: con mayor taur, C es mas plano (menor crecimiento)
slope_taur0 = res_taur0["C"][-1] - res_taur0["C"][0]
slope_taur50 = res_taur50["C"][-1] - res_taur50["C"][0]
print(f"Pendiente C con taur=0.00: {slope_taur0:.6f}")
print(f"Pendiente C con taur=0.50: {slope_taur50:.6f}")
assert slope_taur50 < slope_taur0, "Mayor taur debe aplanar la trayectoria de consumo"
print("OK (Capital 2/2): Pendiente del consumo mas plana con taur=0.50, coincide con el oraculo.")
"""
    )
)

# 11. CÓDIGO GRAFICACIÓN INTERACTIVA SECCIÓN 2
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# SIMULACIÓN INTERACTIVA EN 3 PANELES: IMPUESTOS DISTORSIONADORES
# ==============================================================================

# Esta función grafica el impacto de tres impuestos a la vez (consumo,
# trabajo, capital) comparando contra un caso base SIN impuestos (línea
# negra discontinua). Al ejecutar veremos 3 paneles: Consumo, Oferta de
# Trabajo y Activos. Moviendo los sliders se aprecia cómo cada impuesto
# distorsiona una decisión distinta del agente.
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
    nbf.v4.new_markdown_cell(r"""## 4. El Sistema de Seguridad Social de Capitalización

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

# Esta celda explora la SUSTITUCIÓN PERFECTA entre ahorro forzoso (Seguridad
# Social) y ahorro voluntario. Con previsión perfecta, el agente descuenta
# el fondo de pensiones futuro y ajusta su ahorro privado para mantener el
# mismo consumo. Al ejecutar, el Panel 1 (Consumo) debería ser IDÉNTICO con
# y sin SS; el Panel 2 (Ahorro privado B) caerá al introducir la SS porque
# el agente sustituye ahorro voluntario por forzoso.
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

# 12. ASERCIÓN SECCIÓN 4: SEGURIDAD SOCIAL
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN SECCIÓN 4: SEGURIDAD SOCIAL (Apéndice J)
# ==============================================================================

# Verificamos la SUSTITUCIÓN PERFECTA de ahorro: con SS, el consumo debe
# ser IDÉNTICO al caso sin SS (rtol=1e-6) porque el agente descuenta el
# fondo de pensiones futuro y ajusta su ahorro privado. Pero el ahorro
# privado B al inicio de la vida laboral se vuelve NEGATIVO (deuda): el
# agente se endeuda contra el fondo de SS bloqueado para mantener su
# senda óptima de consumo.

# Calibración SS: tau_ss=0.36, t_star=26, salario creciente W=10+t
t_star = 26
W_ss = np.zeros(30)
for t in range(t_star):
    W_ss[t] = 10.0 + t

# 1. Sin Seguridad Social
params_no_ss = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tau_ss=0.0, t_star=t_star)
res_no_ss = solve_social_security(params_no_ss, W_ss)

# 2. Con Seguridad Social
params_ss = FiscalPolicyParameters(T=30, beta=0.97, R=0.05, tau_ss=0.36, t_star=t_star)
res_ss = solve_social_security(params_ss, W_ss)

# Sustitución perfecta: consumo idéntico con y sin SS
np.testing.assert_allclose(res_no_ss["C"], res_ss["C"], rtol=1e-6)
print("OK (SS 1/2): Consumo idéntico con y sin Seguridad Social (rtol=1e-6).")

# Ahorro privado negativo al inicio de la vida laboral con SS
assert np.any(res_ss["B"][:5] < 0.0), "Con SS, el ahorro privado debe ser negativo al inicio"
print(f"B[0] con SS: {res_ss['B'][0]:.6f}")
print("OK (SS 2/2): Ahorro privado negativo al inicio de la vida laboral con SS.")
"""
    )
)

# 13. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 5. Cuaderno de Bitácora (Actividades para el Alumno)

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
    nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas en este Laboratorio
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
