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
nb.cells.append(nbf.v4.new_markdown_cell("""## Extensiones para ABP (Aprendizaje Basado en Proyectos)

1. **Shock fiscal permanente**: introducir un aumento del gasto público financiado con impuestos lump-sum y analizar el crowding-out de la inversión.
2. **DGE estocástico**: simular 1000 trayectorias con shocks aleatorios de PTF y calcular momentos (desviaciones estándar, correlaciones) para comparar con los hechos estilizados del ciclo económico.
3. **Extensión con ocio endógeno**: añadir oferta de trabajo elástica al DGE (fusionar P4 y P7) y analizar cómo cambia la respuesta a un shock tecnológico."""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# "import X as np" trae la librería X con alias np. "from X import Y" es selectivo.
# "import sys; sys.path.append(...)" añade una carpeta al PATH para que Python
# encuentre el código del proyecto aunque el notebook esté en un subdirectorio.

# Librerías de terceros (instaladas en el entorno con pip)
import numpy as np                      # cálculo numérico: vectores, matrices, álgebra lineal
import matplotlib.pyplot as plt         # gráficos científicos con estilo MATLAB
from ipywidgets import interact, FloatSlider, Checkbox   # widgets interactivos (sliders) para Jupyter

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Proyecto (requiere `pip install -e .` desde la raíz del repo).
# Cada nombre entre paréntesis es una función o clase que se podrá usar más
# abajo como si estuviera definida en este mismo cuaderno. El modelo DGE
# vive en src/macroaicomp/models/dge.py, no en el notebook — así la lógica
# está separada de la visualización (ver Sección 5, Buenas Prácticas).
from macroaicomp.models.dge import (
    DGEParameters,              # dataclass con los 5 parámetros del modelo (alpha, beta, delta, rho, A)
    compute_steady_state,        # calcula K*, Y*, C*, I*, R* a partir de los parámetros
    solve_blanchard_khan,        # resuelve el sistema linealizado (Blanchard-Khan, descomposición espectral)
    solve_nonlinear_simulation   # resuelve el sistema no lineal exacto (fsolve periodo a periodo)
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
        r"""# "def nombre(args):" define FUNCIÓN — no se ejecuta hasta que se llama.
# QUÉ: simula un shock temporal de TFP (epsilon en t=1, decae con rho)
# y grafica 4 paneles (Y, C, I, K) + líneas de SS inicial y momento del shock.
# POR QUÉ (intuición económica): un shock de productividad positivo (epsilon>0)
# aumenta la producción. Los consumidores, anticipando mayor renta futura,
# elevan su consumo YA en t=1 (C es forward-looking, salta). La inversión
# también sube para acumular capital, que alcanza su pico con retardo
# (respuesta "jorobada" o hump-shape). Si rho es bajo, el shock se disipa
# rápido y las variables vuelven antes al SS inicial.
# QUÉ VERÁS: 4 gráficos de evolución temporal. Al mover los sliders verás
# cómo cambian la magnitud del salto, la persistencia y la velocidad de
# convergencia. El capital NUNCA salta en t=1 (es predeterminado).
def plot_dge_simulation(epsilon=0.01, rho_val=0.80, alpha_val=0.35, beta_val=0.96, delta_val=0.06):
    # DGEParameters(...) es un dataclass: "ficha" con parámetros del modelo.
    # Argumentos CON NOMBRE evitan errores de orden.
    params = DGEParameters(alpha=alpha_val, beta=beta_val, delta=delta_val, rho=rho_val)

    # compute_steady_state() es FUNCIÓN: recibe params, devuelve dict con K*, Y*, C*, I*, R*.
    ss = compute_steady_state(params)
    K0 = ss["K"]

    # np.zeros(T) crea un VECTOR de T ceros. a_hat[t] guarda la log-desviación
    # de la TFP en cada periodo: shock en t=1, decaimiento AR(1) desde t=2.
    # np.exp(a_hat) convierte log-desviaciones en niveles (A = 1 en SS).
    T = 60
    a_hat = np.zeros(T)
    a_hat[0] = 0.0
    a_hat[1] = epsilon  # Shock ocurre en t=1 (índice 1)
    for t in range(2, T):
        a_hat[t] = rho_val * a_hat[t - 1]
    A_path = np.exp(a_hat)

    # solve_nonlinear_simulation() resuelve el sistema NO LINEAL exacto periodo
    # a periodo con fsolve. No linealiza: es la solución "verdadera" contra
    # la que compararemos Blanchard-Khan en la Sección 3.
    res = solve_nonlinear_simulation(params, K0, A_path, T=T)

    # plt.subplots(2,2) crea una cuadrícula de 2x2 gráficos (axes) en una
    # sola figura. axs[fila, columna] accede a cada panel por su posición.
    # np.full(T, valor) crea un array de T copias del mismo valor — útil para
    # dibujar una línea horizontal recta en el nivel del estado estacionario.
    # axvline dibuja una línea VERTICAL en x=1 para marcar el momento del shock.
    # El ";" al final de interact() suprime el texto del objeto devuelto.
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    t_axis = np.arange(T)

    # Panel 1: Producción (Y) — salta al alza en t=1 por el shock productivo
    axs[0, 0].plot(t_axis, np.full(T, ss["Y"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[0, 0].plot(t_axis, res["Y"], color='#004C97', linewidth=2.5, label='Producción ($Y_t$)')
    axs[0, 0].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[0, 0].set_title('Evolución de la Producción (PIB)', fontsize=11, fontweight='bold', pad=10)
    axs[0, 0].set_xlabel('Período (t)', fontsize=9)
    axs[0, 0].set_ylabel('Y', fontsize=9)
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend(loc='best', fontsize=8)

    # Panel 2: Consumo (C) — salta en t=1 (forward-looking), converge al SS
    axs[0, 1].plot(t_axis, np.full(T, ss["C"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[0, 1].plot(t_axis, res["C"], color='#7A3E9F', linewidth=2.5, label='Consumo ($C_t$)')
    axs[0, 1].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[0, 1].set_title('Evolución del Consumo Privado', fontsize=11, fontweight='bold', pad=10)
    axs[0, 1].set_xlabel('Período (t)', fontsize=9)
    axs[0, 1].set_ylabel('C', fontsize=9)
    axs[0, 1].grid(True, linestyle=':', alpha=0.6)
    axs[0, 1].legend(loc='best', fontsize=8)

    # Panel 3: Inversión (I) — sube en t=1 (forward-looking), cae por debajo del
    # SS durante la convergencia (efecto "acelerador")
    axs[1, 0].plot(t_axis, np.full(T, ss["I"]), color='black', linestyle='--', alpha=0.5, label='SS')
    axs[1, 0].plot(t_axis, res["I"], color='#D95319', linewidth=2.5, label='Inversión ($I_t$)')
    axs[1, 0].axvline(1.0, color='grey', linestyle=':', alpha=0.7)
    axs[1, 0].set_title('Dinámica de Inversión', fontsize=11, fontweight='bold', pad=10)
    axs[1, 0].set_xlabel('Período (t)', fontsize=9)
    axs[1, 0].set_ylabel('I', fontsize=9)
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)
    axs[1, 0].legend(loc='best', fontsize=8)

    # Panel 4: Stock de Capital (K) — NO salta en t=1 (predeterminado), acumula
    # con retardo (hump), alcanza el pico hacia t~5-10 y luego converge al SS
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

# interact() conecta la función a sliders: cada vez que mueves uno, llama a
# plot_dge_simulation() con los nuevos valores y redibuja — sin ejecutar la
# celda de nuevo. FloatSlider define rango y paso de cada control.
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

# 5a. ORACLE VERIFICATION TABLE AND STEADY-STATE ASSERT
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2.1 Verificación frente al oráculo

Comparamos contra los valores reportados en el libro (Tabla 8.2) y reproducidos por el
código MATLAB/DYNARE del Apéndice N, recogidos en `oraculo.md`:

**Estado estacionario (calibración base: α=0.35, β=0.96, δ=0.06, A=1.0):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Capital en SS (K*) | 6.698596 |
| Producción en SS (Y*) | 1.945783 |
| Consumo en SS (C*) | 1.543867 |
| Inversión en SS (I*) | 0.401916 |
| Tipo de interés en SS (R*) | 0.10166666666666667 |

**Blanchard-Khan — Estabilidad:**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Autovalor estable μ₁ (|μ| < 1) | ≈0.90399 |
| Autovalor inestable μ₂ (|μ| > 1) | ≈1.15229 |
| Clasificación | Punto de silla (exactamente 1 raíz estable) |

**Shock temporal de PTF (+1% con ρ=0.8):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| K₁ (predeterminado, no salta) | = K* ≈ 6.6986 |
| C₁ (salta al alza en impacto) | > C* |
| Y₁ (salta al alza en impacto) | > Y* |
| I₁ (salta al alza en impacto) | > I* |
| Pico de K (hump, ocurre con retardo) | Entre periodos 2 y 12 |
| Convergencia de largo plazo (C, K) | Vuelven al SS inicial (tol 1e-3) |
| Consistencia Blanchard-Khan vs simulación no lineal | K y C coinciden con rtol 1e-2 |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# QUÉ: verifica que compute_steady_state() devuelve los valores exactos de
# la Tabla 8.2 del libro (K*=6.698596, Y*=1.945783, C*=1.543867, I*=0.401916,
# R*=0.101667). POR QUÉ: si el estado estacionario base está mal, TODAS las
# simulaciones siguientes (shock, BK, no lineal) partirían de un punto
# erróneo. QUÉ VERÁS: "OK: estado estacionario coincide con el oráculo" o un
# AssertionError que detiene la ejecución antes de seguir.
# np.testing.assert_allclose(a, b, atol=...) compara con tolerancia.
# No usar "==" con decimales. Si pasa, no imprime nada (control silencioso).
# DGEParameters() sin argumentos usa los defaults: alpha=0.35, beta=0.96,
# delta=0.06, A=1.0 — que coinciden con la calibración del oráculo.

params_orac = DGEParameters()
ss_orac = compute_steady_state(params_orac)

np.testing.assert_allclose(ss_orac["K"], 6.698596, atol=1e-6)
np.testing.assert_allclose(ss_orac["Y"], 1.945783, atol=1e-6)
np.testing.assert_allclose(ss_orac["C"], 1.543867, atol=1e-6)
np.testing.assert_allclose(ss_orac["I"], 0.401916, atol=1e-6)
np.testing.assert_allclose(ss_orac["R"], 0.10166666666666667, atol=1e-6)
print("OK: estado estacionario coincide con el oráculo (Apéndice N).")
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
        r"""# QUÉ: compara la solución linealizada de Blanchard-Khan (BK) con la solución
# no lineal exacta (fsolve) para un mismo shock de TFP. POR QUÉ: BK
# aproxima el modelo con una tangente de primer orden alrededor del SS; esa
# aproximación es muy buena para shocks pequeños (epsilon=0.01) pero acumula
# error de truncamiento ante shocks grandes (epsilon=0.25). Esta celda
# permite ver la discrepancia crecer con el slider.
# QUÉ VERÁS: 2 gráficos (C y K) con dos líneas superpuestas (BK vs no
# lineal), más el error relativo máximo impreso debajo. Para epsilon=0.01
# las líneas son casi indistinguibles; para epsilon=0.25 se separan
# visiblemente, sobre todo en Consumo (la variable de salto).
# "def nombre(args):" define FUNCIÓN — no se ejecuta hasta que interact() la llama.
# np.arange(T) crea array [0, 1, 2, ..., T-1] para el eje x de los gráficos.
# np.max(np.abs(a - b)) / ss["C"] * 100 calcula el error relativo máximo en %.
# f"texto {var:.4f}%" (f-string) interpola la variable con 4 decimales y añade "%".
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

    # solve_blanchard_khan() resuelve el sistema LINEALIZADO usando
    # descomposición de autovalores de la matriz J (Apéndice N).
    res_bk = solve_blanchard_khan(params, K0, A_path, T=T)

    # solve_nonlinear_simulation() resuelve el sistema NO LINEAL exacto
    # resolviendo las ecuaciones de Euler y acumulación simultáneamente.
    res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T=T)

    # plt.subplots(1,2) crea 2 paneles uno al lado del otro.
    # linestyle='--' (discontinua) para BK, continua para no lineal — así se
    # distingue cuál es cuál aunque los colores sean iguales.
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    t_axis = np.arange(T)

    # Consumo — variable forward-looking, el error de linealización se concentra aquí
    axs[0].plot(t_axis, res_bk["C"], color='#7A3E9F', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Linealizado)')
    axs[0].plot(t_axis, res_nonlin["C"], color='#7A3E9F', linewidth=2.0, label='Exacto No Lineal')
    axs[0].set_title('Consumo ($C_t$): Comparación de resolvedores', fontsize=11, fontweight='bold')
    axs[0].set_xlabel('Período (t)')
    axs[0].set_ylabel('C')
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend()

    # Capital — variable predeterminada, menor error de linealización
    axs[1].plot(t_axis, res_bk["K"], color='#8EAD3A', linestyle='--', linewidth=2.0, label='Blanchard-Khan (Linealizado)')
    axs[1].plot(t_axis, res_nonlin["K"], color='#8EAD3A', linewidth=2.0, label='Exacto No Lineal')
    axs[1].set_title('Capital ($K_t$): Comparación de resolvedores', fontsize=11, fontweight='bold')
    axs[1].set_xlabel('Período (t)')
    axs[1].set_ylabel('K')
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend()

    plt.tight_layout()
    plt.show()

    # diff_C = error relativo máximo en Consumo como % del SS.
    # Para shocks pequeños (~1%) debe ser < 0.1%; para shocks grandes
    # (~25%) puede superar el 1%, indicando que BK pierde precisión.
    diff_C = np.max(np.abs(res_bk["C"] - res_nonlin["C"])) / ss["C"] * 100
    diff_K = np.max(np.abs(res_bk["K"] - res_nonlin["K"])) / ss["K"] * 100
    print(f"Error relativo máximo en Consumo : {diff_C:.4f}%")
    print(f"Error relativo máximo en Capital  : {diff_K:.4f}%")

# Slider de comparación. Checkbox "use_matlab_timing" permite al alumno
# verificar la equivalencia con el código del libro.
interact(
    plot_solver_comparison,
    epsilon_shock=FloatSlider(value=0.01, min=-0.30, max=0.30, step=0.02, description='Shock TFP'),
    use_matlab_timing=Checkbox(value=False, description='Timing del libro')
);
"""
    )
)

# 6a. BK EIGENVALUES AND LINEAR VS NONLINEAR CONSISTENCY ASSERT
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# QUÉ: verifica TRES propiedades del oráculo (Apéndice N) en orden:
# 1) autovalores de la matriz J del sistema linealizado (estable mu_s≈0.904,
#    inestable mu_u≈1.152) — confirman que el sistema es un PUNTO DE SILLA;
# 2) consistencia BK vs no lineal para shock pequeño (rtol=1e-2);
# 3) convergencia de largo plazo al SS inicial (shock transitorio se disipa).
# POR QUÉ: un sistema DGE DEBE ser punto de silla (tantas raíces
# inestables como variables forward-looking) para tener solución única y
# determinada; si no lo fuera, la economía no tendría una senda de equilibrio
# bien definida. QUÉ VERÁS: tres líneas "OK: ..." o AssertionError si el
# port de Python tuviera un bug numérico.
# np.linalg.inv() calcula la matriz INVERSA (A^{-1}).
# np.linalg.eigvals() devuelve los autovalores de una matriz.
# np.real() toma solo la parte real (los autovalores de J en este modelo son reales).
# np.sort(np.abs(mu)) ordena por valor absoluto: el primero es el estable.
# x[-1] = último elemento (indexado negativo). res_nl["K"][-1] es K en t=T-1.

# --- Autovalores BK ---
alpha_v = params_orac.alpha
beta_v = params_orac.beta
delta_v = params_orac.delta

Omega = 1.0 - beta_v + beta_v * delta_v
Phi = 1.0 - beta_v + (1.0 - alpha_v) * beta_v * delta_v

A_mat = np.array([[1.0, 0.0], [Omega, -alpha_v * beta_v * delta_v]])
B_mat = np.array([[0.0, alpha_v], [Phi, 0.0]])
D_mat = np.array([[1.0, Omega], [0.0, 1.0]])
F_mat = np.array([[-Omega, 0.0], [0.0, 0.0]])
G_mat = np.array([[1.0, 0.0], [0.0, 1.0 - delta_v]])
H_mat = np.array([[0.0, 0.0], [0.0, delta_v]])

invA = np.linalg.inv(A_mat)
inv_term = np.linalg.inv(D_mat + F_mat @ invA @ B_mat)
J = inv_term @ (G_mat + H_mat @ invA @ B_mat)

mu = np.real(np.linalg.eigvals(J))
mu_sorted = np.sort(np.abs(mu))
mu_s = mu_sorted[0]  # estable (|mu| < 1)
mu_u = mu_sorted[1]  # inestable (|mu| > 1)

np.testing.assert_allclose(mu_s, 0.90399, atol=1e-5)
np.testing.assert_allclose(mu_u, 1.15229, atol=1e-5)
print("OK: autovalores BK coinciden con el oráculo (Apéndice N).")

# --- Consistencia lineal vs. no lineal (shock +1% con rho=0.8) ---
# Si BK y el modelo no lineal difieren mucho para un shock pequeño,
# hay un error en la implementación de uno de los dos resolvedores.
T_check = 60
a_hat_check = np.zeros(T_check)
a_hat_check[1] = 0.01
for t in range(2, T_check):
    a_hat_check[t] = params_orac.rho * a_hat_check[t - 1]
A_path_check = np.exp(a_hat_check)

res_bk = solve_blanchard_khan(params_orac, ss_orac["K"], A_path_check, T=T_check)
res_nl = solve_nonlinear_simulation(params_orac, ss_orac["K"], A_path_check, T=T_check)

np.testing.assert_allclose(res_bk["K"], res_nl["K"], rtol=1e-2)
np.testing.assert_allclose(res_bk["C"], res_nl["C"], rtol=1e-2)
print("OK: soluciones BK y no lineal coinciden con rtol=1e-2 (oráculo).")

# --- Convergencia de largo plazo al SS inicial ---
# Un shock transitorio (epsilon que decae con rho<1) debe devolver la
# economía al MISMO SS inicial, no a uno nuevo. K[-1] y C[-1] son
# los valores en el último periodo simulado (t=59).
np.testing.assert_allclose(res_nl["K"][-1], ss_orac["K"], atol=1e-3)
np.testing.assert_allclose(res_nl["C"][-1], ss_orac["C"], atol=1e-3)
print("OK: convergencia de largo plazo al SS inicial (tol 1e-3, oráculo).")
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
