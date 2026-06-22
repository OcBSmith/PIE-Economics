import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# Práctica P8: El Modelo Neoclásico de Crecimiento Exógeno (Solow-Swan)
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P8-v1.0
*   **Capítulo de Referencia**: Capítulo 9, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Simular y analizar la dinámica de acumulación de capital en tiempo discreto, el proceso de transición hacia el estado estacionario, los efectos de perturbaciones estructurales (tasa de ahorro, demografía y TFP), y el principio de la Regla de Oro.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Comprender** el mecanismo dinámico de acumulación de capital físico per cápita propuesto por Solow (1956) y Swan (1956).
2.  **Identificar** los determinantes de largo plazo de la riqueza y productividad laboral en el estado estacionario (tasa de ahorro, depreciación, crecimiento poblacional y TFP).
3.  **Analizar** la transición dinámica de las variables per cápita (capital, producción, consumo e inversión) tras shocks estructurales.
4.  **Diferenciar** entre el efecto impacto (corto plazo) y el efecto de largo plazo sobre el bienestar tras un incremento del ahorro.
5.  **Explicar** analítica y visualmente el concepto de la **Regla de Oro** y las consecuencias de la ineficiencia dinámica (infra-acumulación vs. sobre-acumulación).
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
        r"""# "import X as np" trae la librería X con alias np. "from X import Y" es selectivo.
# "import sys; sys.path.append(...)" añade una carpeta al PATH para que Python
# encuentre el código del proyecto aunque el notebook esté en un subdirectorio.

# Librerías de terceros (instaladas en el entorno con pip)
import numpy as np                      # cálculo numérico: vectores, arrays, operaciones vectorizadas
import matplotlib.pyplot as plt         # gráficos científicos con estilo MATLAB
from ipywidgets import interact, FloatSlider   # widgets interactivos (sliders) para Jupyter

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Proyecto. El modelo de Solow-Swan vive en src/macroaicomp/models/growth.py.
# SolowSwanParameters: dataclass con parámetros (alpha, delta, s, n, A).
# compute_solow_steady_state: calcula k*, y*, c*, i* a partir de los parámetros.
# simulate_solow_swan: simula la dinámica de acumulación periodo a periodo.
from macroaicomp.models.growth import (
    SolowSwanParameters,
    compute_solow_steady_state,
    simulate_solow_swan
)
"""
    )
)

# 4. INTRODUCCIÓN TEÓRICA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 1. El Modelo Neoclásico de Crecimiento (Solow-Swan)

El modelo de Solow-Swan es el bloque fundamental de la teoría moderna del crecimiento económico. A diferencia de los modelos de equilibrio general dinámico con agentes optimizadores (como Ramsey o DGE básico), este modelo asume que **la tasa de ahorro es exógena y constante**. 

### 1.1 Estructura Matemática

El modelo se define en variables per cápita (por trabajador) para aislar el tamaño de la economía y capturar el bienestar individual:
*   **Población (Trabajo):** Crece a una tasa constante $n$:
    $$L_{t} = L_{t-1}(1 + n)$$
*   **Función de Producción Intensiva (Cobb-Douglas):**
    $$y_t = A_t k_t^\alpha$$
    donde $y_t \equiv Y_t/L_t$ es la producción per cápita, $k_t \equiv K_t/L_t$ es el stock de capital per cápita, $A_t$ es la TFP, y $\alpha$ es la elasticidad capital-trabajo.
*   **Ahorro e Inversión:** Una fracción constante $s$ de la producción se destina a la inversión bruta:
    $$i_t = s y_t$$
*   **Consumo per cápita:** Lo que no se ahorra se consume:
    $$c_t = (1 - s)y_t$$

### 1.2 Dinámica del Capital y Estado Estacionario
La acumulación de capital per cápita sigue la siguiente ecuación en diferencias de primer orden:
$$k_{t+1} = \frac{(1 - \delta)k_t + s A_t k_t^\alpha}{1 + n}$$

El estado estacionario ($\bar{k}$) ocurre cuando el capital por trabajador permanece constante ($\Delta k_t = 0$), lo que implica que la inversión por trabajador cubre exactamente la depreciación física y el crecimiento de la población (depreciación efectiva):
$$s A \bar{k}^\alpha = (\delta + n)\bar{k}$$

Despejando el capital per cápita estacionario:
$$\bar{k} = \left( \frac{\delta + n}{s A} \right)^{\frac{1}{\alpha - 1}}$$

Una vez obtenido $\bar{k}$, las demás variables se calculan de manera directa:
$$\bar{y} = A \bar{k}^\alpha, \quad \bar{c} = (1 - s)\bar{y}, \quad \bar{i} = s\bar{y}$$
""")
)

# 5. SIMULACIÓN INTERACTIVA DE SHOCKS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Simulación Interactiva: Transición Dinámica y Shocks

Supongamos que la economía parte de su estado estacionario base con una tasa de ahorro del $20\%$ ($s_0 = 0.20$), depreciación del $6\%$ ($\delta = 0.06$) y crecimiento poblacional del $2\%$ ($n_0 = 0.02$). En el período $t = 5$, la economía sufre una perturbación permanente en su tasa de ahorro (por ejemplo, sube al $25\%$).

Con el siguiente panel interactivo, puedes mover la tasa de ahorro final ($s_1$), el crecimiento poblacional final ($n_1$), y la TFP final ($A_1$) para analizar cómo responde la economía período a período.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# "def nombre(args):" define FUNCIÓN — no se ejecuta hasta que interact() la llama.
# QUÉ: simula un shock estructural PERMANENTE en t=5 (ahorro s, demografía n
# o TFP A) en el modelo de Solow-Swan y grafica 4 paneles: k, y, c, gy.
# POR QUÉ (intuición económica): un aumento de s implica MÁS inversión hoy
# pero MENOS consumo hoy (cae en t=5). A largo plazo, la mayor acumulación
# de capital eleva la producción y el consumo por encima del nivel inicial.
# La tasa de crecimiento gy salta en el impacto pero vuelve a CERO en el
# largo plazo (sin progreso técnico, el crecimiento se agota al llegar al
# nuevo SS). QUÉ VERÁS: 4 gráficos con SS inicial (--), SS final (:), y
# línea vertical en t=5 (momento del shock). Al mover sliders, cambian las
# trayectorias y los niveles finales.
# np.full(T, valor) crea un array de T copias del mismo valor.
# s_path[t_shock:] = s_final cambia todos los elementos desde t_shock hasta
# el final en una sola línea (slicing vectorizado).
def plot_solow_simulation(s_final=0.25, n_final=0.02, A_final=1.00):
    params = SolowSwanParameters()

    # Estado estacionario inicial con la calibración base del libro.
    ss_init = compute_solow_steady_state(params)

    # Shock PERMANENTE en t=5: s, n y/o A cambian a su valor final.
    # np.full(T, valor) llena el array entero con el valor inicial, luego
    # sobrescribimos desde t_shock en adelante con el valor final.
    T = 100
    t_shock = 5

    s_path = np.full(T, params.s)
    n_path = np.full(T, params.n)
    A_path = np.full(T, params.A)

    s_path[t_shock:] = s_final
    n_path[t_shock:] = n_final
    A_path[t_shock:] = A_final

    # simulate_solow_swan() reproduce la ecuación de acumulación periodo a
    # periodo k[t+1] = ((1-delta)*k[t] + s[t]*A[t]*k[t]**alpha) / (1+n[t]).
    res = simulate_solow_swan(params, ss_init["k"], s_path, n_path, A_path, T=T)

    # Estado estacionario final con los nuevos parámetros — hacia él converge
    # la economía asintóticamente.
    ss_final = compute_solow_steady_state(params, s=s_final, n=n_final, A=A_final)

    # plt.subplots(2,2) crea cuadrícula 2x2. axhline = línea horizontal en
    # el nivel del SS. axvline = línea vertical en t_shock.
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    t_axis = np.arange(T)

    # Panel 1: Capital per cápita (k_t) — NO salta, acumula gradualmente
    axs[0, 0].plot(t_axis, res["k"], color='#8EAD3A', linewidth=2.5, label='Trayectoria ($k_t$)')
    axs[0, 0].axhline(ss_init["k"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[0, 0].axhline(ss_final["k"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[0, 0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0, 0].set_title('Stock de Capital per cápita', fontsize=11, fontweight='bold')
    axs[0, 0].set_xlabel('Períodos')
    axs[0, 0].set_ylabel('k')
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend()

    # Panel 2: Producción per cápita (y_t) — ligada a k, misma dinámica gradual
    axs[0, 1].plot(t_axis, res["y"], color='#004C97', linewidth=2.5, label='Trayectoria ($y_t$)')
    axs[0, 1].axhline(ss_init["y"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[0, 1].axhline(ss_final["y"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[0, 1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[0, 1].set_title('Producción per cápita (PIB p.c.)', fontsize=11, fontweight='bold')
    axs[0, 1].set_xlabel('Períodos')
    axs[0, 1].set_ylabel('y')
    axs[0, 1].grid(True, linestyle=':', alpha=0.6)
    axs[0, 1].legend()

    # Panel 3: Consumo per cápita (c_t) — CAE en t=5 (sacrificio: más ahorro
    # implica menos consumo hoy) pero a largo plazo SUPERA el nivel inicial
    # (la mayor producción compensa el sacrificio)
    axs[1, 0].plot(t_axis, res["c"], color='#7A3E9F', linewidth=2.5, label='Trayectoria ($c_t$)')
    axs[1, 0].axhline(ss_init["c"], color='black', linestyle='--', alpha=0.5, label='SS Inicial')
    axs[1, 0].axhline(ss_final["c"], color='red', linestyle=':', alpha=0.7, label='SS Final')
    axs[1, 0].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1, 0].set_title('Consumo per cápita', fontsize=11, fontweight='bold')
    axs[1, 0].set_xlabel('Períodos')
    axs[1, 0].set_ylabel('c')
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)
    axs[1, 0].legend()

    # Panel 4: Tasa de Crecimiento de y (gy_t) — salta en el impacto pero
    # vuelve a 0% en el largo plazo. Sin progreso técnico, el crecimiento
    # per cápita es CERO en estado estacionario.
    axs[1, 1].plot(t_axis, res["gy"], color='#D95319', linewidth=2.5, label='Tasa de Crecimiento ($g_{y,t}$)')
    axs[1, 1].axvline(t_shock, color='grey', linestyle=':', alpha=0.5)
    axs[1, 1].set_title('Tasa de Crecimiento de la Producción per cápita (%)', fontsize=11, fontweight='bold')
    axs[1, 1].set_xlabel('Períodos')
    axs[1, 1].set_ylabel('% de crecimiento')
    axs[1, 1].grid(True, linestyle=':', alpha=0.6)
    axs[1, 1].legend()

    plt.tight_layout()
    plt.show()

# interact() conecta la función a sliders: al moverlos, redibuja la figura.
# El ";" al final suprime la representación de texto del objeto devuelto.
interact(
    plot_solow_simulation,
    s_final=FloatSlider(value=0.25, min=0.05, max=0.60, step=0.05, description='Ahorro (s)'),
    n_final=FloatSlider(value=0.02, min=0.00, max=0.10, step=0.01, description='Pob. (n)'),
    A_final=FloatSlider(value=1.00, min=0.50, max=2.00, step=0.05, description='TFP (A)')
);
"""
    )
)

# 5a. ORACLE VERIFICATION TABLE AND STEADY-STATE ASSERT
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2.1 Verificación frente al oráculo

Comparamos contra los valores reportados en el libro (Tabla 9.3) y reproducidos por el
código MATLAB del Apéndice O, recogidos en `oraculo.md`:

**Estado estacionario (calibración base: α=0.35, s=0.20, δ=0.06, n=0.02, A=1.0):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Capital per cápita en SS (k*) | 4.0946 |
| Producción per cápita en SS (y*) | 1.6378 |
| Consumo per cápita en SS (c*) | 1.3103 |
| Inversión per cápita en SS (i*) | 0.3276 |

**Shock de ahorro s 0.20 → 0.25:**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| k₀ | Parte de k* inicial ≈ 4.0946 |
| Trayectoria de k | Creciente monótona hacia nuevo SS |
| c en impacto (cae por mayor ahorro) | c₀ = 0.75 × y₀ < c* inicial |
| Largo plazo: c_final | > c* inicial (el sacrificio compensa) |

**Regla de Oro:**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Tasa de ahorro que maximiza c* | s_gold = α = 0.35 |
| c* en s_gold | Máximo global de la curva c̄(s) |
| c* en s=0.20 (infra-acumulación) | < c*_gold |
| c* en s=0.50 (sobre-acumulación) | < c*_gold |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# QUÉ: verifica que compute_solow_steady_state() devuelve los valores de la
# Tabla 9.3 del libro (k*=4.0946, y*=1.6378, c*=1.3103, i*=0.3276). POR
# QUÉ: si el SS base está mal, TODAS las simulaciones de shock y la Regla
# de Oro partirían de un punto erróneo. QUÉ VERÁS: "OK: estado estacionario
# coincide con el oráculo" o un AssertionError.
# SolowSwanParameters(...) crea un dataclass con argumentos CON NOMBRE.
# La calibración exacta del oráculo usa delta=0.06, n=0.02 (defaults del
# código usan delta=0.08, n=0.0; ambos dan delta+n=0.08, la depreciación
# efectiva es la misma y por tanto los valores numéricos coinciden).
# np.testing.assert_allclose(a, b, atol=...) compara con tolerancia.

params_orac = SolowSwanParameters(alpha=0.35, delta=0.06, s=0.20, n=0.02, A=1.0)
ss_orac = compute_solow_steady_state(params_orac)

np.testing.assert_allclose(ss_orac["k"], 4.0946, atol=1e-4)
np.testing.assert_allclose(ss_orac["y"], 1.6378, atol=1e-4)
np.testing.assert_allclose(ss_orac["c"], 1.3103, atol=1e-4)
np.testing.assert_allclose(ss_orac["i"], 0.3276, atol=1e-4)
print("OK: estado estacionario coincide con el oráculo (Apéndice O).")
"""
    )
)

# 6. LA REGLA DE ORO DE ACUMULACIÓN DE CAPITAL
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 3. La Regla de Oro (Golden Rule) de Acumulación de Capital

Dado que un mayor ahorro implica mayor capital y producción de largo plazo, ¿debe una economía ahorrar tanto como sea posible? La respuesta es **no**. 

El objetivo último de la actividad económica es el **consumo** y el bienestar de los hogares, no la acumulación de capital por sí misma. Si ahorramos una fracción muy alta (cercana al $100\%$), la producción será inmensa, pero casi toda se reinvertirá para compensar la depreciación del gigantesco stock de capital, dejando un consumo cercano a cero. Si ahorramos una fracción muy baja, el capital se agotará y la producción será insignificante, resultando también en un consumo residual.

### 3.1 Derivación Analítica
La tasa de ahorro de la **Regla de Oro** ($s^{gold}$) es aquella que maximiza el consumo de estado estacionario:
$$\max_{s} \bar{c}(s) = \bar{y} - (\delta + n)\bar{k}$$
Sustituyendo $\bar{y} = A \bar{k}^\alpha$:
$$\max_{k} \bar{c} = A \bar{k}^\alpha - (\delta + n)\bar{k}$$
La condición de primer orden con respecto a $\bar{k}$ es:
$$\frac{d\bar{c}}{d\bar{k}} = \alpha A \bar{k}^{\alpha-1} - (\delta + n) = 0 \implies \alpha \frac{\bar{y}}{\bar{k}} = \delta + n$$

Multiplicando ambos lados por $\bar{k}/\bar{y}$ y sabiendo que en estado estacionario $s \frac{\bar{y}}{\bar{k}} = \delta + n$, llegamos a:
$$s^{gold} = \alpha$$

*   **Ineficiencia Dinámica:** Si $s > \alpha$, la economía está sobre-acumulando capital. Podría aumentar el consumo tanto hoy como a largo plazo simplemente reduciendo su tasa de ahorro.
*   **Bajo-acumulación:** Si $s < \alpha$, la economía está consumiendo demasiado a corto plazo, de modo que un incremento del ahorro aumentaría el consumo en el futuro.
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# "def nombre(args):" define FUNCIÓN — no se ejecuta hasta que interact() la llama.
# QUÉ: dibuja la curva de consumo de estado estacionario c_bar(s) en función
# de la tasa de ahorro s, marca el punto actual y el máximo (Regla de Oro).
# POR QUÉ (intuición económica): existe una tasa de ahorro óptima s_gold=α
# que maximiza el consumo de largo plazo. Si s < α (infra-acumulación),
# aumentar s eleva c futuro. Si s > α (sobre-acumulación), la economía es
# DINÁMICAMENTE INEFICIENTE: podría consumir MÁS hoy y en el futuro
# reduciendo s. QUÉ VERÁS: curva en forma de U invertida con punto rojo
# (ahorro actual), estrella verde (Regla de Oro), y regiones sombreadas
# (azul=infra-acumulación, rosa=sobre-acumulación).
# np.linspace(inicio, fin, N) crea N puntos equiespaciados — aquí 100 tasas
# de ahorro entre 0.01 y 0.95 para dibujar la curva suave.
# np.zeros_like(s_grid) crea un array del mismo tamaño lleno de ceros.
def plot_golden_rule(s_current=0.20):
    params = SolowSwanParameters()
    alpha = params.alpha

    # Para cada s en el grid, calculamos el consumo de SS y lo guardamos.
    s_grid = np.linspace(0.01, 0.95, 100)
    c_ss_grid = np.zeros_like(s_grid)
    k_ss_grid = np.zeros_like(s_grid)

    for idx, s_val in enumerate(s_grid):
        ss = compute_solow_steady_state(params, s=s_val)
        c_ss_grid[idx] = ss["c"]
        k_ss_grid[idx] = ss["k"]

    # Consumo actual con el s que elijas en el slider.
    ss_current = compute_solow_steady_state(params, s=s_current)
    c_current = ss_current["c"]

    # Consumo de Regla de Oro: s = alpha = 0.35 en esta calibración.
    ss_gold = compute_solow_steady_state(params, s=alpha)
    c_gold = ss_gold["c"]

    plt.figure(figsize=(10, 6))
    plt.plot(s_grid, c_ss_grid, color='#7A3E9F', linewidth=3, label='Consumo de Estado Estacionario ($\\overline{c}$)')

    # plt.scatter dibuja un PUNTO. s=100 controla el tamaño del marcador.
    # zorder controla qué se dibuja encima (mayor = más arriba).
    plt.scatter(s_current, c_current, color='red', s=100, zorder=5, label=f'Ahorro actual (s = {s_current:.2f}, c = {c_current:.3f})')
    plt.axvline(s_current, color='red', linestyle=':', alpha=0.5)
    plt.axhline(c_current, color='red', linestyle=':', alpha=0.5)

    # marker='*' dibuja una estrella en el máximo.
    plt.scatter(alpha, c_gold, color='#8EAD3A', s=120, marker='*', zorder=6, label=f'Regla de Oro ($s^{{gold}} = \\alpha = {alpha:.2f}$, $c^{{gold}} = {c_gold:.3f}$)')
    plt.axvline(alpha, color='#8EAD3A', linestyle='--', alpha=0.7)
    plt.axhline(c_gold, color='#8EAD3A', linestyle='--', alpha=0.7)

    # axvspan sombrea una región vertical entre dos valores de x.
    plt.axvspan(0.01, alpha, color='#E6F2FF', alpha=0.5, label='Bajo-acumulación (Eficiente)')
    plt.axvspan(alpha, 0.95, color='#FFE6E6', alpha=0.5, label='Sobre-acumulación (Ineficiente)')

    plt.title('La Regla de Oro: Consumo Estacionario vs. Tasa de Ahorro', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Tasa de Ahorro ($s$)', fontsize=10)
    plt.ylabel('Consumo Estacionario ($\\overline{c}$)', fontsize=10)
    plt.xlim(0.01, 0.95)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower center', fontsize=9)
    plt.show()

# Slider para mover el punto de "ahorro actual" sobre la curva.
interact(
    plot_golden_rule,
    s_current=FloatSlider(value=0.20, min=0.02, max=0.90, step=0.02, description='Tasa Ahorro')
);
"""
    )
)

# 6a. GOLDEN RULE ASSERT
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# QUÉ: verifica analíticamente la Regla de Oro contra el oráculo
# (Apéndice O): s_gold = α = 0.35, y c* en s_gold es MAYOR que en s=0.20
# (infra-acumulación) y que en s=0.50 (sobre-acumulación). POR QUÉ: la
# Regla de Oro es un resultado analítico exacto (derivado igualando la
# productividad marginal del capital a delta+n); si no se cumpliera, habría
# un bug en compute_solow_steady_state(). QUÉ VERÁS: dos "OK: ..." o un
# AssertionError.
# assert condicion, mensaje: si la condición es False, lanza AssertionError
# con el mensaje (a diferencia de np.testing, aquí usamos "assert" puro de
# Python para comparaciones de desigualdad >, que assert_allclose no soporta).

alpha_gold = params_orac.alpha
ss_gold = compute_solow_steady_state(params_orac, s=alpha_gold)
ss_low = compute_solow_steady_state(params_orac, s=0.20)
ss_high = compute_solow_steady_state(params_orac, s=0.50)

# s_gold debe ser exactamente alpha (propiedad analítica de la Cobb-Douglas)
np.testing.assert_allclose(alpha_gold, 0.35, atol=1e-6)
print(f"OK: s_gold = alpha = {alpha_gold:.2f}")

# Tanto infra-acumulación (s=0.20 < alpha) como sobre-acumulación (s=0.50 > alpha)
# dan un consumo de SS MENOR que el de la Regla de Oro.
assert ss_gold["c"] > ss_low["c"], (
    f"c_gold={ss_gold['c']:.4f} debería ser > c_s020={ss_low['c']:.4f}"
)
assert ss_gold["c"] > ss_high["c"], (
    f"c_gold={ss_gold['c']:.4f} debería ser > c_s050={ss_high['c']:.4f}"
)
print(f"OK: c_gold={ss_gold['c']:.4f} > c_s020={ss_low['c']:.4f} y "
      f"c_gold > c_s050={ss_high['c']:.4f} (oráculo, Apéndice O).")
"""
    )
)

# 7. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 4. Cuaderno de Bitácora (Actividades para el Alumno)

Responde a las siguientes cuestiones tras interactuar con las simulaciones del modelo de crecimiento de Solow-Swan:

1.  **Mecanismo de Transición y Sacrificio de Consumo**:
    *   Establece una tasa de ahorro final de $s_1 = 0.25$ (partiendo de $s_0 = 0.20$). Observa la gráfica de consumo per cápita. ¿Qué ocurre exactamente en el período $t=5$ (momento del shock)? ¿Por qué cae el consumo instantáneamente si la producción se mantiene igual?
    *   Explica cómo evoluciona el consumo a partir de $t=6$. ¿Por qué se recupera y acaba superando al nivel inicial? Relaciona esto con el concepto de "acumulación de capital".
2.  **La Regla de Oro y la Ineficiencia Dinámica**:
    *   Utiliza el panel de la Regla de Oro. Establece la tasa de ahorro actual en $s = 0.50$. ¿Qué le ocurre al consumo estacionario comparado con el de la Regla de Oro ($s=0.35$)? ¿Por qué se dice que una economía con $s = 0.50$ es dinámicamente ineficiente? ¿Cómo podría esa economía mejorar el bienestar tanto hoy como en el futuro?
3.  **Transición Demográfica y TFP**:
    *   En la simulación de shocks (Sección 2), devuelve el ahorro al $20\%$ y reduce la tasa de crecimiento demográfico de $n_0 = 0.02$ a $n_1 = 0.00$. Describe la dinámica del capital per cápita y de la producción per cápita. ¿Por qué una población constante ($n=0$) eleva la riqueza por trabajador a largo plazo?
    *   Ahora, aplica un incremento permanente de la TFP del $5\%$ ($A = 1.05$). ¿Qué ocurre con la tasa de crecimiento del PIB per cápita en el año del shock y a largo plazo? Explica por qué, en ausencia de crecimiento continuo de la TFP ($g_A = 0$), el crecimiento de la renta per cápita a largo plazo acaba siendo cero en este modelo.
""")
)

# 8. BUENAS PRÁCTICAS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 5. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Modularización del Modelo**: Las ecuaciones y simulaciones del modelo de Solow-Swan no están dispersas, sino importadas del módulo de biblioteca [`growth.py`](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/growth.py), aislando la visualización del backend computacional.
2.  **Diseño Paramétrico Limpio**: La calibración y los shocks se definen mediante objetos `SolowSwanParameters` y vectores ordenados de tiempo, facilitando la escalabilidad del simulador.
3.  **Higiene del Repositorio**: El cuaderno está integrado en el flujo de trabajo de Git con `nbstripout` y controles linter en el hook de `pre-commit`, previniendo que los gráficos pesados contaminen el repositorio y asegurando un arranque limpio.
""")
)

# 9. ESCRIBIR EL ARCHIVO
os.makedirs("c:/Users/AntonioRC/Desktop/PIE/practicas/08-solow-swan/", exist_ok=True)
nbf.write(nb, "c:/Users/AntonioRC/Desktop/PIE/practicas/08-solow-swan/python.ipynb")
print("Notebook generado con éxito en practicas/08-solow-swan/python.ipynb.")
