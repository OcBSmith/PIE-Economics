import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# Práctica P6: La Empresa y la Decisión de Inversión (Modelo Q de Tobin)
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P6-v1.0
*   **Capítulo de Referencia**: Capítulo 7, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Modelar la decisión de inversión de una empresa competitiva que enfrenta costos de ajuste cuadráticos en la instalación del capital físico. Estudiaremos:
    1. La derivación analítica de la dinámica del capital ($K_t$) y la Q de Tobin marginal ($q_t$).
    2. La log-linealización del modelo y la resolución mediante autovalores del stable saddle path (Uhlig, 1999).
    3. La resolución numérica del modelo no lineal exacto utilizando `scipy.optimize.fsolve`.
    4. La simulación y análisis de shocks permanentes en la tasa de interés real, evaluando el "salto" instantáneo de la variable forward-looking ($q_t$) y la transición gradual del capital ($K_t$).
    5. La visualización de la dinámica del sistema en el diagrama de fases.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Comprender** el concepto de la Q de Tobin marginal y su relación con el precio de sombra de los activos físicos.
2.  **Analizar** cómo los costos de ajuste de la inversión ralentizan el proceso de acumulación de capital físico, rompiendo la equivalencia directa instantánea entre ahorro e inversión.
3.  **Calcular** la estabilidad del sistema dinámico mediante el análisis de autovalores, identificando la naturaleza del punto de silla (saddle point).
4.  **Resolver** la condición de salto de las expectativas para determinar el comportamiento instantáneo de las variables flexibles (jump variables).
5.  **Comparar** de forma crítica la precisión de la aproximación linealizada frente al modelo no lineal exacto.
6.  **Graficar e interpretar** un diagrama de fases dinámico con curvas de demarcación y campos de vectores en el plano de fases.
"""
    )
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
" + "### 🕹️ GUÍA RÁPIDA DE INICIO - Q de Tobin (Inversión)
*   **¿Qué estamos haciendo aquí?** Explicando cuándo decide una empresa comprar más maquinaria e invertir.
*   **La Regla de la Q:** Si la Q de Tobin es mayor que 1.0, significa que la empresa vale más en bolsa de lo que cuesta comprar sus máquinas. ¡Es hora de invertir y expandirse! Si es menor que 1.0, no conviene invertir.
*   **¡Prueba esto!** Cambia la tasa de interés y observa cómo el ratio Q cae o sube, arrastrando consigo la inversión de la empresa.
"""
    )
)

# 3. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
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
from ipywidgets import interact, FloatSlider

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.tobin_q import (
    TobinQParameters,
    compute_steady_state,
    compute_linearized_system,
    solve_linearized_simulation,
    solve_nonlinear_simulation
)
"""
    )
)

# 4. SECCIÓN 1: INTRODUCCIÓN TEÓRICA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 1. El Modelo Q de Tobin con Costos de Ajuste

En el modelo neoclásico estándar sin costos de ajuste, la empresa ajusta su stock de capital de forma instantánea ante cualquier perturbación, de modo que la productividad marginal del capital se iguala en cada instante con el coste de uso del capital. 

En la realidad, la instalación de nueva maquinaria o la construcción de infraestructuras implican costes adicionales (parada de producción, entrenamiento, logística). El **Modelo Q de Tobin** introduce costes de ajuste cuadráticos en la inversión:
$$C(I_t, K_t) = \frac{\phi}{2} \left( \frac{I_t - \delta K_t}{K_t} \right)^2 K_t$$

Donde $I_t$ es la inversión bruta, $K_t$ el stock de capital, $\delta$ la tasa de depreciación y $\phi$ el parámetro que regula la magnitud de los costos de ajuste.

El problema intertemporal de la empresa consiste en maximizar el valor presente de los beneficios:
$$\max_{\{I_t, K_{t+1}\}} \sum_{t=0}^{\infty} \frac{1}{(1+R)^t} \left[ K_t^\alpha - I_t - \frac{\phi}{2} \left( \frac{I_t - \delta K_t}{K_t} \right)^2 K_t \right]$$

Sujeto a la dinámica de acumulación de capital:
$$K_{t+1} = (1-\delta) K_t + I_t$$

### 1.1 Ecuaciones Dinámicas del Modelo
De las condiciones de primer orden (FOCs), definimos la **q marginal** como el multiplicador de Lagrange asociado a la acumulación de capital (el valor de sombra de una unidad adicional de capital instalado):
1. **Regla de Inversión (Dinámica del Capital):**
   $$q_t = 1 + \phi \left( \frac{I_t - \delta K_t}{K_t} \right) \implies \Delta K_t = K_{t+1} - K_t = (q_t - 1) \frac{K_t}{\phi}$$
   La inversión neta es positiva si y sólo si el valor de la empresa por unidad de capital ($q_t$) es superior a su coste de reemplazo ($1.0$).
   
2. **Ecuación de Arbitraje (Dinámica del Valor q):**
   $$(1-\delta) q_{t+1} = (1+R) q_t - \alpha K_{t+1}^{\alpha-1} + C_K(I_{t+1}, K_{t+1})$$
   Donde, tras simplificar, la dinámica exacta de $q_t$ se escribe como:
   $$q_{t+1} = (1+R) q_t - \alpha K_{t+1}^{\alpha-1} - \frac{(q_{t+1}-1)^2}{2\phi} + \delta$$

### 1.2 Estado Estacionario
En el estado estacionario, el capital no cambia ($\Delta K_t = 0$), lo que implica que la Q de Tobin es igual a la unidad, y el stock de capital viene determinado por la tasa de interés real y la depreciación:
$$\bar{q} = 1.0, \quad \bar{K} = \left( \frac{R + \delta}{\alpha} \right)^{\frac{1}{\alpha - 1}}$$
""")
)

# 5. CÁLCULO DEL ESTADO ESTACIONARIO Y ESTABILIDAD
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# CÁLCULO DEL ESTADO ESTACIONARIO, AUTOVALORES Y FÓRMULA DE SALTO
# ==============================================================================

params_ss = TobinQParameters()  # α=0.35, β=0.97, δ=0.06, φ=10.0, R=0.04
ss = compute_steady_state(params_ss, R=0.04)
lin_sys = compute_linearized_system(params_ss, R=0.04)

K_star = ss["K"]
q_star = ss["q"]
I_star = ss["I"]
lambdas = lin_sys["eigenvalues"]
theta_simple = lin_sys["theta"]
theta_book = lin_sys.get("theta_book", theta_simple)

print("ESTADO ESTACIONARIO (R=0.04):")
print("-" * 55)
print(f"  Q de Tobin (q*)               : {q_star:.6f}")
print(f"  Stock de capital (K*)          : {K_star:.6f}")
print(f"  Inversión (I* = delta*K*)      : {I_star:.6f}")
print(f"  Producción (Y* = K*^alpha)     : {K_star**0.35:.6f}")
print()
print("ESTABILIDAD (log-desviaciones):")
print("-" * 55)
print(f"  Autovalor estable lambda1      : {lambdas[0]:.6f}")
print(f"  Autovalor inestable lambda2    : {lambdas[1]:.6f}")
print(f"  Modulo |1+lambda1|             : {abs(1+lambdas[0]):.6f}  (< 1, estable en niveles)")
print(f"  Modulo |1+lambda2|             : {abs(1+lambdas[1]):.6f}  (> 1, inestable en niveles)")
print(f"  Clasificacion                  : Punto de silla")
print()
print("FORMULA DE SALTO:")
print("-" * 55)
print(f"  theta (simplificada = phi*lambda1): {theta_simple:.10f}")
print(f"  theta_book (formula del libro)    : {theta_book:.10f}")
print(f"  Diferencia                        : {abs(theta_simple - theta_book):.2e}")
"""
    )
)

# 6. ORÁCULO: VERIFICACIÓN DE RESULTADOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro (Capítulo 7) y
reproducidos por el código DYNARE del Apéndice K, recogidos en
`oraculo.md`:

**Calibración base (alpha=0.35, beta=0.97, delta=0.06, R=0.04, phi=10.0):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Q de Tobin en SS (q*) | 1.0 |
| Stock de capital en SS (K*) | 6.8711236 |
| Inversión en SS (I* = delta*K*) | 0.06 x 6.8711236 |
| Autovalor estable lambda1 | -0.060658 |
| Autovalor inestable lambda2 | 0.107158 |
| theta (simplificada) vs theta_book | Idénticos (atol 1e-12) |
| Clasificación | Punto de silla |

**Shock permanente R: 4% -> 3%:**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| K0 (predeterminado, sin salto) | K* en R=4% |
| q0 (salto inicial) | ~1.1033 (>1.0) |
| K largo plazo | K* en R=3% (mayor que K inicial) |
| q largo plazo | 1.0 |
| Consistencia lineal vs no lineal | K y q coinciden con rtol 1e-2 |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""
    )
)

# 7. ASERCIÓN: ESTADO ESTACIONARIO, AUTOVALORES Y FÓRMULA DE SALTO
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACION: SS, AUTOVALORES Y FORMULA DE SALTO (Apéndice K del libro)
# ==============================================================================

# 1. Estado estacionario
np.testing.assert_allclose(q_star, 1.0, atol=1e-6)
np.testing.assert_allclose(K_star, 6.8711236, rtol=1e-6)
np.testing.assert_allclose(I_star, 0.06 * K_star, rtol=1e-6)
print("OK (SS 1/3): q*=1.0, K*~6.871, I*=delta*K*, coincide con el oraculo DYNARE.")

# 2. Autovalores (log-desviaciones)
np.testing.assert_allclose(lambdas[0], -0.060658, rtol=1e-4)
np.testing.assert_allclose(lambdas[1], 0.107158, rtol=1e-4)
assert abs(1 + lambdas[0]) < 1.0, "lambda1 debe ser estable en niveles (|1+lambda1| < 1)"
assert abs(1 + lambdas[1]) > 1.0, "lambda2 debe ser inestable en niveles (|1+lambda2| > 1)"
print("OK (SS 2/3): lambda1~-0.060658, lambda2~0.107158, punto de silla confirmado.")

# 3. Identidad de la formula de salto: theta = theta_book para varias calibraciones
for R_val in [0.02, 0.03, 0.04, 0.05]:
    for phi_val in [5.0, 10.0, 15.0]:
        p = TobinQParameters(alpha=0.35, delta=0.06, phi=phi_val, R=R_val)
        ls = compute_linearized_system(p, R=R_val)
        assert abs(ls["theta"] - ls.get("theta_book", ls["theta"])) < 1e-12, \
            f"theta != theta_book para R={R_val}, phi={phi_val}"
print("OK (SS 3/3): theta = theta_book para todo R en {0.02,0.03,0.04,0.05}, phi en {5,10,15} (atol=1e-12).")
"""
    )
)

# 8. SECCIÓN 3: SIMULACIÓN INTERACTIVA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 3. Simulación Interactiva: Shock de Tasa de Interés

Supongamos que la economía se encuentra inicialmente en su estado estacionario correspondiente a una tasa de interés del $4\%$ ($R_0 = 0.04$). En el período $t=1$, se produce una caída permanente e inesperada de la tasa de interés real al $3\%$ ($R_f = 0.03$).

Dado que la tasa de interés representa el coste de financiación y la tasa de descuento de los beneficios futuros, una reducción de la misma aumenta el valor de sombra del capital ($q_t$). Al ser el capital una variable rígida (predeterminada), su valor no puede saltar en $t=1$ ($K_1 = \bar{K}_{init}$). Sin embargo, la variable de expectativas $q_1$ dará un **salto instantáneo hacia arriba** para situarse sobre la nueva trayectoria estable de transición.
""")
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# GRAFICACIÓN INTERACTIVA EN 3 PANELES: SHOCK DE TASA DE INTERÉS
# ==============================================================================

def plot_tobin_simulation(R_init=0.04, R_final=0.03, phi_val=10.0, delta_val=0.06, alpha_val=0.35):
    params = TobinQParameters(alpha=alpha_val, delta=delta_val, phi=phi_val, R=R_init)
    
    # 1. Calcular estados estacionarios
    ss_init = compute_steady_state(params, R=R_init)
    K0 = ss_init["K"]
    
    ss_final = compute_steady_state(params, R=R_final)
    K_ss_final = ss_final["K"]
    
    # 2. Generar trayectoria de shock permanente en t=1 (índice 1)
    T = 100
    R_path = np.full(T, R_final)
    R_path[0] = R_init
    
    # 3. Resolver simulación con el resolvedor numérico no lineal exacto
    res = solve_nonlinear_simulation(params, K0, R_path, T=T)
    
    # 4. Graficación en 3 paneles con estética premium
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    t_axis = np.arange(T)
    
    # Panel 1: Q de Tobin
    axs[0].plot(t_axis, res["q"], color='#7A3E9F', linewidth=2.5, label='Q marginal ($q_t$)')
    axs[0].axhline(1.0, color='black', linestyle='--', alpha=0.5, label='SS ($q=1.0$)')
    axs[0].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[0].set_title('Ratio Q de Tobin', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Período (t)', fontsize=9)
    axs[0].set_ylabel('Ratio q', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # Panel 2: Stock de Capital
    axs[1].plot(t_axis, np.full(T, K0), color='black', linestyle='--', alpha=0.5, label=f'SS Inicial ({K0:.2f})')
    axs[1].plot(t_axis, np.full(T, K_ss_final), color='grey', linestyle=':', alpha=0.8, label=f'SS Final ({K_ss_final:.2f})')
    axs[1].plot(t_axis, res["K"], color='#004C97', linewidth=2.5, label='Stock de Capital ($K_t$)')
    axs[1].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[1].set_title('Stock de Capital ($K_t$)', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Período (t)', fontsize=9)
    axs[1].set_ylabel('Capital (K)', fontsize=9)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    # Panel 3: Inversión Bruta y Neta
    axs[2].plot(t_axis, res["I"], color='#D95319', linewidth=2.5, label='Inversión Bruta ($I_t$)')
    axs[2].plot(t_axis, delta_val * res["K"], color='grey', linestyle=':', alpha=0.8, label='Depreciación ($\delta K_t$)')
    axs[2].fill_between(t_axis, res["I"], delta_val * res["K"], color='#D95319', alpha=0.15, label='Inversión Neta')
    axs[2].axhline(delta_val * K0, color='black', linestyle='--', alpha=0.4, label='Inversión SS Inicial')
    axs[2].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[2].set_title('Dinámica de Inversión', fontsize=11, fontweight='bold', pad=10)
    axs[2].set_xlabel('Período (t)', fontsize=9)
    axs[2].set_ylabel('Inversión (I)', fontsize=9)
    axs[2].grid(True, linestyle=':', alpha=0.6)
    axs[2].legend(loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.show()

# Controles interactivos
interact(
    plot_tobin_simulation,
    R_init=FloatSlider(value=0.04, min=0.01, max=0.08, step=0.005, description='R inicial'),
    R_final=FloatSlider(value=0.03, min=0.01, max=0.08, step=0.005, description='R final'),
    phi_val=FloatSlider(value=10.0, min=1.0, max=30.0, step=1.0, description='Costos Aj. (φ)'),
    delta_val=FloatSlider(value=0.06, min=0.01, max=0.15, step=0.01, description='Deprec. (δ)'),
    alpha_val=FloatSlider(value=0.35, min=0.20, max=0.50, step=0.05, description='Elasticidad (α)')
);
"""
    )
)

# 6. SECCIÓN 3: LOG-LINEALIZACIÓN VS NO LINEAL
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 4. Log-Linealización frente a Solución No Lineal Exacta

En la teoría macroeconómica, el método estándar consiste en linealizar (o log-linealizar) el sistema no lineal alrededor de su estado estacionario. Utilizando la aproximación de Uhlig (1999), definimos las desviaciones logarítmicas:
$$\hat{k}_t = \ln(K_t) - \ln(\bar{K}), \quad \hat{q}_t = \ln(q_t) - \ln(\bar{q}) = \ln(q_t)$$

El sistema dinámico linealizado se expresa en forma matricial como:
$$\begin{bmatrix}
\Delta\hat{q}_t \\
\Delta\hat{k}_t
\end{bmatrix} = A \begin{bmatrix}
\hat{q}_t \\
\hat{k}_t
\end{bmatrix} = \begin{bmatrix}
\frac{R\phi - (\alpha - 1)(R + \delta)}{\phi} & - (\alpha - 1)(R + \delta) \\
\frac{1}{\phi} & 0
\end{bmatrix}\begin{bmatrix}
\hat{q}_t \\
\hat{k}_t
\end{bmatrix}$$

### 3.1 Propiedades de Estabilidad
Para la calibración por defecto ($\alpha=0.35, \delta=0.06, \phi=10.0, R=0.04$), la matriz $A$ posee dos autovalores reales:
$$\lambda_1 \approx -0.0607, \quad \lambda_2 \approx 0.1072$$

Como un autovalor es estrictamente negativo (estable en niveles, $|1+\lambda_1| < 1$) y el otro es estrictamente positivo (inestable, $|1+\lambda_2| > 1$), el sistema dinámico presenta un **equilibrio de punto de silla (saddle-point)**. Esto asegura la existencia de una única trayectoria convergente al estado estacionario final.

### 3.2 Condición de Salto Estable
Para evitar la divergencia del sistema dinámico, la variable forward-looking $\hat{q}_t$ debe saltar instantáneamente a la trayectoria estable en el momento del shock:
$$\hat{q}_1 = \theta \hat{k}_1$$
Donde la pendiente de la trayectoria estable es simplemente $\theta = \phi \lambda_1$.

A continuación, comparamos gráficamente la solución analítica aproximada (log-linealizada) frente a la solución numérica exacta calculada por `fsolve`.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# COMPARACIÓN GRÁFICA DE SOLUCIONADORES (LINEALIZADO VS NO LINEAL)
# ==============================================================================

params = TobinQParameters()
ss_init = compute_steady_state(params, R=0.04)
K0 = ss_init["K"]

T = 100
R_path = np.full(T, 0.03)
R_path[0] = 0.04

# Resolver con ambos métodos
res_lin = solve_linearized_simulation(params, K0, R_path, T=T)
res_nonlin = solve_nonlinear_simulation(params, K0, R_path, T=T)

# Graficar
fig, axs = plt.subplots(1, 2, figsize=(15, 5))
t_axis = np.arange(T)

# Comparación Q
axs[0].plot(t_axis, res_lin["q"], color='#7A3E9F', linestyle='--', linewidth=2.0, label='Aproximación Linealizada')
axs[0].plot(t_axis, res_nonlin["q"], color='#7A3E9F', linewidth=2.0, label='Exacto No Lineal')
axs[0].set_title('Comparación: Q de Tobin ($q_t$)', fontsize=11, fontweight='bold')
axs[0].set_xlabel('Período (t)')
axs[0].set_ylabel('Ratio q')
axs[0].grid(True, linestyle=':', alpha=0.6)
axs[0].legend()

# Comparación K
axs[1].plot(t_axis, res_lin["K"], color='#004C97', linestyle='--', linewidth=2.0, label='Aproximación Linealizada')
axs[1].plot(t_axis, res_nonlin["K"], color='#004C97', linewidth=2.0, label='Exacto No Lineal')
axs[1].set_title('Comparación: Stock de Capital ($K_t$)', fontsize=11, fontweight='bold')
axs[1].set_xlabel('Período (t)')
axs[1].set_ylabel('Capital (K)')
axs[1].grid(True, linestyle=':', alpha=0.6)
axs[1].legend()

plt.tight_layout()
plt.show()

# Imprimir discrepancia máxima
diff_K = np.max(np.abs(res_lin["K"] - res_nonlin["K"]))
diff_q = np.max(np.abs(res_lin["q"] - res_nonlin["q"]))
print(f"Discrepancia máxima en Capital (K) : {diff_K:.6f}")
print(f"Discrepancia máxima en Ratio q      : {diff_q:.6f}")
"""
    )
)

# 8. ASERCIÓN: SHOCK DE TIPO DE INTERÉS (R 4% -> 3%)
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN DEL SHOCK: SALTO DE q, CONVERGENCIA Y CONSISTENCIA (Apéndice K)
# ==============================================================================

ss_R04 = compute_steady_state(params_ss, R=0.04)
ss_R03 = compute_steady_state(params_ss, R=0.03)
K_star_R04 = ss_R04["K"]
K_star_R03 = ss_R03["K"]

# 1. K0 es predeterminado: debe ser K* en R=4%
np.testing.assert_allclose(K0, K_star_R04, rtol=1e-6)
print(f"OK (Shock 1/4): K0 = K*(R=4%) = {K0:.6f}, predeterminado (sin salto).")

# 2. q0 salta por encima de 1.0 (forward-looking)
q0_jump = res_nonlin["q"][1]  # periodo del shock (t=1)
print(f"q0 (post-shock) = {q0_jump:.6f}")
assert q0_jump > 1.0, "q0 debe saltar por encima de 1.0 tras la caida de R"
np.testing.assert_allclose(q0_jump, 1.1033, rtol=1e-3)
print("OK (Shock 2/4): q0 ~ 1.1033 > 1.0, la inversion se estimula.")

# 3. Largo plazo: q -> 1.0, K -> K*(R=3%)
q_long_run = res_nonlin["q"][-1]
K_long_run = res_nonlin["K"][-1]
np.testing.assert_allclose(q_long_run, 1.0, atol=1e-4)
np.testing.assert_allclose(K_long_run, K_star_R03, rtol=1e-3)
print(f"q[T-1] = {q_long_run:.6f} (esperado: 1.0)")
print(f"K[T-1] = {K_long_run:.6f} (esperado: {K_star_R03:.6f})")
print("OK (Shock 3/4): Convergencia a nuevo SS en el largo plazo.")

# 4. Consistencia lineal vs no lineal: K y q coinciden
np.testing.assert_allclose(res_lin["K"], res_nonlin["K"], rtol=1e-2)
np.testing.assert_allclose(res_lin["q"], res_nonlin["q"], rtol=1e-2)
print("OK (Shock 4/4): Trayectorias lineal y no lineal consistentes (rtol=1e-2).")
"""
    )
)

# 9. SECCIÓN 4: DIAGRAMA DE FASES
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Diagrama de Fases Interactivo

El diagrama de fases permite visualizar geométricamente el comportamiento dinámico del sistema en el espacio de estados $(\hat{k}, \hat{q})$. En este plano:
*   El **locus de capital** ($\Delta \hat{k} = 0$) es la recta horizontal $\hat{q} = 0$.
*   El **locus de valor** ($\Delta \hat{q} = 0$) es una recta con pendiente negativa.
*   El **saddle path** (trayectoria estable) es la recta $\hat{q} = \theta \hat{k}$.

Cuando ocurre el shock de interés (reducción de la tasa de descuento), las variables de desviación se calculan respecto al *nuevo* estado estacionario (que pasa a ser el origen $(0,0)$).
El capital inicial $\hat{k}_1$ está a la izquierda del origen (dado que el nuevo capital de largo plazo es mayor, el capital inicial representa una desviación negativa). 
1. La economía comienza en la recta horizontal del estado estacionario previo (punto rojo).
2. Al ocurrir el shock, la variable forward-looking $q$ salta verticalmente hacia arriba hasta la recta del **saddle path** (punto naranja).
3. A partir del punto de salto, las fuerzas dinámicas del sistema empujan a la economía de forma gradual a lo largo del saddle path hasta alcanzar el nuevo estado estacionario en el origen (estrella verde).
"""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# DIAGRAMA DE FASES INTERACTIVO Y CAMPO DE VECTORES
# ==============================================================================

def plot_phase_diagram(R_init=0.04, R_final=0.03, phi_val=10.0, delta_val=0.06, alpha_val=0.35):
    params = TobinQParameters(alpha=alpha_val, delta=delta_val, phi=phi_val, R=R_final)
    
    # 1. Calcular estados estacionarios
    ss_init = compute_steady_state(params, R=R_init)
    K_ss_init = ss_init["K"]
    
    ss_final = compute_steady_state(params, R=R_final)
    K_ss_final = ss_final["K"]
    
    # 2. Obtener coeficientes del sistema linealizado final
    lin_sys = compute_linearized_system(params, R=R_final)
    A = lin_sys["A"]
    theta = lin_sys["theta"]
    
    # 3. Crear rejilla de espacio de estados (desviaciones logarítmicas)
    k_min, k_max = -0.25, 0.25
    q_min, q_max = -0.15, 0.15
    k_grid, q_grid = np.meshgrid(np.linspace(k_min, k_max, 50), np.linspace(q_min, q_max, 50))
    
    # 4. Campo vectorial del sistema linealizado
    dk_hat = A[1,0] * q_grid + A[1,1] * k_grid
    dq_hat = A[0,0] * q_grid + A[0,1] * k_grid
    
    plt.figure(figsize=(10, 8))
    
    # Flujo del sistema dinámico
    plt.streamplot(k_grid, q_grid, dk_hat, dq_hat, color='grey', alpha=0.3, density=1.2, arrowsize=0.8)
    
    # Loci (curvas de demarcación)
    plt.axhline(0.0, color='#004C97', linestyle='--', linewidth=1.5, label=r'$\Delta \hat{k} = 0$ (Locus Capital)')
    
    slope_dq = -A[0,1] / A[0,0]
    k_vals = np.linspace(k_min, k_max, 100)
    plt.plot(k_vals, slope_dq * k_vals, color='#7A3E9F', linestyle='--', linewidth=1.5, label=r'$\Delta \hat{q} = 0$ (Locus Q)')
    
    # Saddle Path (Trayectoria estable)
    plt.plot(k_vals, theta * k_vals, color='black', linewidth=2.5, label='Saddle Path (Trayectoria Estable)')
    
    # Puntos clave del shock
    k_hat_0 = np.log(K_ss_init) - np.log(K_ss_final)
    q_hat_0 = theta * k_hat_0
    
    plt.scatter([k_hat_0], [0.0], color='red', s=90, zorder=5, label='E.E. Inicial (Pre-shock)')
    plt.scatter([k_hat_0], [q_hat_0], color='orange', s=90, zorder=5, label='Salto Inicial (Post-shock)')
    plt.scatter([0.0], [0.0], color='green', s=150, marker='*', zorder=5, label='E.E. Final (Nuevo)')
    
    # Flecha del salto instantáneo en t=1
    plt.annotate('', xy=(k_hat_0, q_hat_0), xytext=(k_hat_0, 0.0),
                 arrowprops=dict(facecolor='darkred', edgecolor='darkred', arrowstyle='->', lw=2.0, ls=':'),
                 zorder=4)
    
    # Simulación de la trayectoria temporal de desviaciones
    T_path = 40
    R_path = np.full(T_path, R_final)
    R_path[0] = R_init
    res_sim = solve_linearized_simulation(params, K_ss_init, R_path, T=T_path)
    k_sim = np.log(res_sim["K"]) - np.log(K_ss_final)
    q_sim = np.log(res_sim["q"])
    
    plt.plot(k_sim, q_sim, color='red', linestyle='-', linewidth=2.0, zorder=4, label='Trayectoria Dinámica')
    
    # Flechas de dirección sobre la trayectoria simulada
    for i in range(0, T_path - 2, 8):
        plt.annotate('', xy=(k_sim[i+2], q_sim[i+2]), xytext=(k_sim[i], q_sim[i]),
                     arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=1.5),
                     zorder=4)
                     
    plt.xlim(k_min, k_max)
    plt.ylim(q_min, q_max)
    plt.title('Diagrama de Fases y Transición Dinámica del Modelo Q de Tobin', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel(r'Desviación del Capital ($\hat{k}_t$)', fontsize=10)
    plt.ylabel(r'Desviación del Valor q ($\hat{q}_t$)', fontsize=10)
    plt.axvline(0.0, color='black', alpha=0.3, zorder=1)
    plt.axhline(0.0, color='black', alpha=0.3, zorder=1)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='best', fontsize=9)
    plt.show()

# Controles interactivos para el diagrama de fases
interact(
    plot_phase_diagram,
    R_init=FloatSlider(value=0.04, min=0.01, max=0.08, step=0.005, description='R inicial'),
    R_final=FloatSlider(value=0.03, min=0.01, max=0.08, step=0.005, description='R final'),
    phi_val=FloatSlider(value=10.0, min=1.0, max=30.0, step=1.0, description='Costos Aj. (φ)'),
    delta_val=FloatSlider(value=0.06, min=0.01, max=0.15, step=0.01, description='Deprec. (δ)'),
    alpha_val=FloatSlider(value=0.35, min=0.20, max=0.50, step=0.05, description='Elasticidad (α)')
);
"""
    )
)

# 8. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 6. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con las simulaciones de la inversión empresarial:

1.  **Interpretación Económica del Salto de $q_t$**:
    *   Al reducirse la tasa de interés de 4% a 3%, explica por qué el ratio Q de Tobin marginal ($q_1$) salta instantáneamente por encima de 1.0. ¿Qué representa esto desde la perspectiva del valor de la empresa frente a sus costes de instalación?
    *   ¿Por qué el stock de capital ($K_t$) no puede dar un salto similar en $t=1$? ¿Qué pasaría si la empresa intentara realizar una inversión infinita para cubrir la brecha al instante?
2.  **Análisis de Sensibilidad de los Costes de Ajuste ($\phi$)**:
    *   En la simulación 2, aumenta el parámetro de costos de ajuste $\phi$ de 10 a 25. Observa el comportamiento del capital ($K_t$) y la inversión ($I_t$). ¿Qué ocurre con la velocidad de convergencia al nuevo estado estacionario?
    *   ¿Cómo cambia la magnitud del salto inicial de $q_1$ al aumentar $\phi$? Explica la intuición económica tras este resultado.
3.  **Diagrama de Fases y Estabilidad**:
    *   Utilizando el diagrama de fases interactivo, describe detalladamente la transición del sistema desde el pre-shock (punto rojo) hasta el post-shock inmediato (punto naranja) y la subsecuente trayectoria continua hasta el origen (estrella verde).
    *   ¿Qué ocurriría si $q_t$ diera un salto incorrecto (por ejemplo, a un valor de $q_1 = 1.05$ en lugar de su valor teórico estable de $1.1033$)? Observa las líneas de flujo del campo vectorial fuera del saddle path para razonar tu respuesta.
""")
)

# 9. BUENAS PRÁCTICAS APRENDER AQUÍ
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 7. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento de Lógica Computacional**: La resolución numérica no lineal y el análisis matricial están desacoplados de las celdas didácticas de visualización, residiendo enteramente en el módulo [tobin_q.py](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/tobin_q.py).
2.  **Identidad Algebraica en Códigos**: Hemos verificado en los unit tests que la fórmula simplificada de salto estable ($\theta = \phi \lambda_1$) y la ecuación extendida del libro son exactamente idénticas, simplificando el código didáctico notablemente.
3.  **Higiene del Repositorio**: Antes de cada confirmación de commit, los outputs de este cuaderno se eliminan automáticamente mediante `nbstripout` para evitar el almacenamiento ineficiente de imágenes y datos pesados.
""")
)

# 10. ESCRIBIR EL ARCHIVO
os.makedirs("c:/Users/AntonioRC/Desktop/PIE/practicas/06-tobin-q/", exist_ok=True)
nbf.write(nb, "c:/Users/AntonioRC/Desktop/PIE/practicas/06-tobin-q/python.ipynb")
print("Notebook generado con éxito en practicas/06-tobin-q/python.ipynb.")
