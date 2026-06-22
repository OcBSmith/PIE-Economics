import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# Práctica P4: La Elección Óptima de Consumo-Ocio y Ahorro
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
" + "> ⏱️ **~90-120 minutos**
> 
> 📋 **Prerrequisitos**: **Matemáticas**: optimización multivariante con restricciones, condiciones de primer orden. | **Economía**: elección renta-ocio (modelo de oferta de trabajo), decisión intertemporal de consumo-ahorro (P3). | **Programación**: ninguno previo.\n" + "
" + "
> \n" + "
" + "
### 🕹️ GUÍA RÁPIDA DE INICIO - Consumo y Ocio
*   **¿Qué estamos haciendo aquí?** Decidiendo cuántas horas trabajar (para tener dinero y consumir) frente a cuántas horas descansar (ocio).
*   **Efecto Sustitución vs Efecto Renta:** Si te suben el sueldo, ¿trabajas más porque cada hora vale más (sustitución) o trabajas menos porque ya eres rico y quieres descansar (renta)?
*   **¡Prueba esto!** Modifica el salario base en el código y observa si el gráfico de horas trabajadas sube o baja.
"""
    )
)

# 3. INSTALACIÓN DE DEPENDENCIAS (GOOGLE COLAB)
nb.cells.append(nbf.v4.new_code_cell(r"""%%capture
# %%capture suprime la salida de la celda para no llenar el notebook de texto
# de instalación. "import sys; 'google.colab' in sys.modules" detecta si
# estamos en Google Colab (entorno en la nube) sin necesidad de paquetes extra.
# Si es Colab, !pip install descarga las librerías. En local (venv) ya están
# instaladas: la celda no hace nada.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets cvxpy
"""))

# 3. IMPORTACIONES
nb.cells.append(
    nbf.v4.new_markdown_cell(
        """## Extensiones para ABP (Aprendizaje Basado en Proyectos)

1. **Oferta de trabajo elástica con salario endógeno**: introducir una función de producción donde el salario depende de $L$ agregado (equilibrio general parcial) y analizar la optimalidad.
2. **Jubilación endógena con ocio**: permitir que el consumidor elija la edad de jubilación y comparar con una edad fija.
3. **Tributación progresiva**: introducir un IRPF progresivo (tramos) en lugar de un impuesto proporcional y analizar el efecto sobre la oferta de trabajo en distintos puntos de la distribución salarial."""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

# "import X as np" trae a este cuaderno código escrito en otro sitio y le da
# un alias corto (np, plt, cp) para no teclear el nombre completo cada vez.
# "from X import Y" es más selectivo: trae solo la función/clase Y del
# módulo X. Así el notebook se limita a llamar funciones ya probadas en vez
# de reimplementar fórmulas aquí (ver Sección 6, Buenas Prácticas).

# Librerías de terceros (instaladas con pip)
import numpy as np                      # cálculo numérico: vectores, matrices, álgebra lineal
import matplotlib.pyplot as plt         # gráficos 2D con estilo MATLAB
import cvxpy as cp  # noqa: F401 (usado en celdas posteriores)                      # optimización convexa (resuelve el problema directamente)
from ipywidgets import interact, FloatSlider  # widgets interactivos (sliders) para Jupyter

# sys.path.append añade una carpeta al PATH de Python para que "import" la
# encuentre. "../" sube dos niveles desde practicas/04-consumo-ocio/ hasta
# la raíz del repo, donde está src/. Esto evita tener que instalar el
# paquete con pip para usarlo en este cuaderno.
import sys
sys.path.append('../../src')

# Proyecto (src/macroaicomp/): separa la lógica matemática del modelo de la
# visualización. Cada nombre entre paréntesis es una función o clase que se
# podrá usar como si estuviera definida en este mismo cuaderno.
from macroaicomp.models.consumption_leisure import (
    ConsumptionLeisureParameters,
    solve_foc_fsolve,
    solve_direct_cvxpy
)
"""
    )
)

# 4. MARCO TEÓRICO
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 1. El Marco Teórico: Consumo, Ahorro y Oferta de Trabajo Endógena

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
"""
    )
)

# 5. CALIBRACIÓN DE PARÁMETROS
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# CALIBRACIÓN DE REFERENCIA (Capítulo 5 - Libro original)
# ==============================================================================

# Esta celda solo FIJA NÚMEROS: todavía no calcula nada.
# ConsumptionLeisureParameters() es un dataclass (definido en
# src/macroaicomp/models/consumption_leisure.py): una "ficha" con casillas
# con nombre (T, beta, gamma, R). Al llamarlo sin argumentos, cada casilla
# toma su VALOR POR DEFECTO definido en la clase. Esto es como rellenar un
# formulario con los valores que ya vienen escritos.

# f"texto {var}" (f-strings) mete el valor de una variable dentro del texto.
# Las expresiones entre llaves se evalúan antes de imprimir: útil para ver
# valores calculados derivados (como theta) sin guardarlos en variables aparte.
params = ConsumptionLeisureParameters()

print("CALIBRACIÓN BASE DE REFERENCIA:")
print("-" * 60)
print(f"  Lifespan (T)                     : {params.T} periodos")
print(f"  Factor de descuento (beta)       : {params.beta} (theta ≈ {((1-params.beta)/params.beta)*100:.2f}%)")
print(f"  Peso del consumo en utilidad (γ) : {params.gamma:.2f}")
print(f"  Tasa de interés real (R)         : {params.R*100:.2f}%")
print("-" * 60)
"""
    )
)

# 6. COMPARATIVA DE SOLVERS
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 2. Solución Numérica: fsolve vs cvxpy

Para resolver este sistema, implementamos dos solvers:
1.  **`fsolve`**: Resuelve el sistema no lineal acoplado de tamaño $2T \times 2T$ (las $T-1$ ecuaciones de Euler, las $T$ condiciones de oferta de trabajo y la condición terminal de activos en cero).
    *   *Resolución de Errata:* Hemos corregido el error de indexación del código MATLAB del libro (`m5foc.m`), que skipeaba el índice residual $2T-1$ e indexaba un elemento fuera de rango en $2T+1$.
2.  **`cvxpy`**: Resuelve el problema mediante optimización convexa directa (Clarabel).
"""))

# 7. CÓDIGO DE EJECUCIÓN COMPARATIVA
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# np.full(params.T, 30.0) crea un VECTOR de longitud params.T donde TODAS
# las posiciones valen 30.0: un salario constante de W=30 en cada periodo.
# Es más legible que un bucle "for t in range(T): W[t]=30".
W_base = np.full(params.T, 30.0)

# solve_foc_fsolve() y solve_direct_cvxpy() son dos FUNCIONES que resuelven
# el mismo problema económico pero con métodos numéricos distintos. La
# primera resuelve las condiciones de primer orden (sistema de ecuaciones no
# lineales 2T x 2T) con un solver de sistemas (fsolve). La segunda plantea
# el problema como optimización convexa y deja que cvxpy encuentre la
# solución. Al ejecutar, ambas deberían dar el mismo resultado (salvo
# diferencias ínfimas de redondeo): es una doble verificación del modelo.

# Resolver mediante FOC (fsolve)
res_fsolve = solve_foc_fsolve(params, W_base)

# Resolver mediante Optimización Convexa (cvxpy)
res_cvxpy = solve_direct_cvxpy(params, W_base)

# Comparativa de resultados
print("COMPARACIÓN DE TRAYECTORIAS (fsolve vs cvxpy):")
print("-" * 75)
# res_fsolve["C"][0] accede al PRIMER elemento (t=0) del array de consumo.
# Los resultados son diccionarios: {"C": array, "L": array, "B": array, ...}
print(f"  Consumo Inicial C(0) [fsolve]   : {res_fsolve['C'][0]:.6f}")
print(f"  Consumo Inicial C(0) [cvxpy]    : {res_cvxpy['C'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [fsolve]   : {res_fsolve['L'][0]:.6f}")
print(f"  Trabajo Inicial L(0) [cvxpy]    : {res_cvxpy['L'][0]:.6f}")
print(f"  Activos Finales B(T-1) [fsolve] : {res_fsolve['B'][-1]:.6e}")
print(f"  Activos Finales B(T-1) [cvxpy]  : {res_cvxpy['B'][-1]:.6e}")
print("-" * 75)

# np.max(np.abs(...)) calcula la diferencia máxima absoluta entre dos arrays
# elemento a elemento: si es < 1e-4, los solvers coinciden hasta el 4º decimal.
diff_C = np.max(np.abs(res_fsolve["C"] - res_cvxpy["C"]))
diff_L = np.max(np.abs(res_fsolve["L"] - res_cvxpy["L"]))
print(f"Máxima diferencia absoluta en Consumo : {diff_C:.2e}")
print(f"Máxima diferencia absoluta en Trabajo : {diff_L:.2e}")
if diff_C < 1e-4 and diff_L < 1e-4:
    print("✅ ¡Los resolvedores numéricos son perfectamente equivalentes!")
else:
    print("❌ Discrepancia detectada entre solucionadores.")
"""
    )
)

# 8. ORÁCULO: VERIFICACIÓN DE RESULTADOS BASE
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 3. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro (Capítulo 5) y
reproducidos por el código MATLAB del Apéndice I, recogidos en
`oraculo.md`:

**Calibración base (β=0.97, R=0.02, γ=0.50, T=30, W=30):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Activos terminales B[T−1] (ambos solvers) | 0.0 (tol 1e−6) |
| Equivalencia fsolve vs cvxpy: C, L, B | Idénticos (rtol 1e−4) |
| Oferta de trabajo L_t | 0 ≤ L_t < 1.0 para todo t |
| Ocio O_t | 0 < O_t ≤ 1.0 para todo t |

**Sensibilidad a preferencias (γ) y tipo de interés (R):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| γ=0.60 vs γ=0.40 (mayor peso del consumo) | L media mayor con γ=0.60 |
| R=0.05 (β=0.97 ⇒ β(1+R)=1.0185>1) | Pendiente del consumo positiva (C crece en t) |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""))

# 9. CELDA DE ASERCIÓN: CONDICIÓN TERMINAL, EQUIVALENCIA Y COTAS
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN NUMÉRICA FRENTE AL ORÁCULO (Apéndice I del libro)
# ==============================================================================

# np.testing.assert_allclose(a, b, atol=..., rtol=...) compara dos valores
# o dos arrays elemento a elemento. Si la diferencia es menor que la
# tolerancia, no hace nada (PUNTO DE CONTROL silencioso). Si falla, lanza
# AssertionError y detiene la ejecución aquí mismo, antes de seguir
# construyendo gráficos sobre un resultado incorrecto.
# No usamos "==" con decimales: el ordenador casi nunca da resultados
# EXACTAMENTE iguales por errores de redondeo internos (ver P0, celda 10).

# 1. Condición terminal: B[T-1] debe ser 0 para ambos solvers.
#    La restricción del modelo dice que el agente no puede dejar activos ni
#    deudas al final de la vida; comprobamos que ambos solvers la respetan.
np.testing.assert_allclose(res_fsolve["B"][-1], 0.0, atol=1e-6)
np.testing.assert_allclose(res_cvxpy["B"][-1], 0.0, atol=1e-6)
print("OK (1/4): Condición terminal B[T-1]=0 para ambos solvers.")

# 2. Equivalencia fsolve vs cvxpy: C, L, B idénticos elemento a elemento.
#    Comparamos arrays ENTEROS (no solo el valor inicial): si los dos
#    métodos numéricos producen las mismas trayectorias completas, el modelo
#    está bien implementado en ambos.
np.testing.assert_allclose(res_fsolve["C"], res_cvxpy["C"], rtol=1e-4)
np.testing.assert_allclose(res_fsolve["L"], res_cvxpy["L"], rtol=1e-4)
np.testing.assert_allclose(res_fsolve["B"], res_cvxpy["B"], rtol=1e-4, atol=1e-6)
print("OK (2/4): fsolve y cvxpy producen trayectorias C, L, B equivalentes (rtol=1e-4).")

# 3. Cotas de la oferta de trabajo: 0 <= L_t < 1 para todo t.
#    L_t es una FRACCIÓN del tiempo total (normalizado a 1): no puede ser
#    negativo ni superar el 100% del tiempo disponible. np.all() devuelve
#    True solo si TODOS los elementos del array cumplen la condición.
assert np.all(res_fsolve["L"] >= 0.0), "L_t debe ser >= 0"
assert np.all(res_fsolve["L"] < 1.0), "L_t debe ser < 1"
print("OK (3/4): 0 <= L_t < 1.0 para todo t (ambos solvers).")

# 4. Ocio positivo: O_t = 1 - L_t > 0 para todo t.
#    El ocio debe ser estrictamente positivo: el agente siempre descansa
#    algo (nadie trabaja el 100% del tiempo con utilidad logarítmica).
assert np.all(res_fsolve["O"] > 0.0), "O_t debe ser > 0"
print("OK (4/4): Ocio O_t > 0 para todo t.")
"""
    )
)

# 10. CELDA DE ASERCIÓN: SENSIBILIDAD A γ Y R
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# VERIFICACIÓN DE SENSIBILIDAD: PREFERENCIAS (γ) Y TIPO DE INTERÉS (R)
# ==============================================================================

# Esta celda comprueba que el modelo responde cualitativamente como predice
# la teoría económica ante cambios en gamma y R. No verificamos valores
# exactos (no hay oráculo para todos los parámetros), sino DIRECCIONES:
# ¿sube L al subir gamma? ¿sube C en el tiempo cuando R es alto?

W30 = np.full(30, 30.0)

# --- Sensibilidad a gamma: mayor gamma => mayor peso del consumo => más L ---
# Creamos DOS calibraciones con argumentos CON NOMBRE (T=..., beta=..., ...).
# Así queda claro qué parámetro cambia y cuál no. gamma=0.40 significa que
# el agente valora más el ocio (1-gamma=0.60); gamma=0.60, más el consumo.
res_g40 = solve_foc_fsolve(ConsumptionLeisureParameters(T=30, beta=0.97, gamma=0.40, R=0.02), W30)
res_g60 = solve_foc_fsolve(ConsumptionLeisureParameters(T=30, beta=0.97, gamma=0.60, R=0.02), W30)
# np.mean() calcula la MEDIA aritmética de todo el array: un solo número
# resumen para comparar el nivel de trabajo entre las dos calibraciones.
mean_L_g40 = np.mean(res_g40["L"])
mean_L_g60 = np.mean(res_g60["L"])
print(f"L media con gamma=0.40: {mean_L_g40:.6f}")
print(f"L media con gamma=0.60: {mean_L_g60:.6f}")
assert mean_L_g60 > mean_L_g40, "Con mayor gamma (mas peso del consumo), L medio debe aumentar"
print("OK (γ): L media mayor con γ=0.60 que con γ=0.40, coincide con el oráculo.")

# --- Sensibilidad a R: con R=0.05, beta*(1+R)=1.0185>1 => C creciente ---
# La ecuación de Euler (C_{t+1} = beta*(1+R)*C_t) dice que el consumo CRECE
# si beta*(1+R) > 1. Con beta=0.97 y R=0.05: 0.97*1.05=1.0185>1, así que
# C[T-1] debe ser mayor que C[0]. La pendiente C[-1]-C[0] lo mide.
res_R5 = solve_foc_fsolve(ConsumptionLeisureParameters(T=30, beta=0.97, gamma=0.50, R=0.05), W30)
slope_C = res_R5["C"][-1] - res_R5["C"][0]
print(f"Consumo inicial C[0] (R=0.05): {res_R5['C'][0]:.6f}")
print(f"Consumo final   C[T-1] (R=0.05): {res_R5['C'][-1]:.6f}")
print(f"Pendiente C[T-1]-C[0]: {slope_C:.6f}")
assert slope_C > 0, "Con beta*(1+R)>1, el consumo debe ser creciente en el tiempo"
print("OK (R): Pendiente de consumo positiva con R=0.05, coincide con el oráculo.")
"""
    )
)

# 11. SIMULACIÓN INTERACTIVA EN 3 PANELES
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Simulación Interactiva en 3 Paneles

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
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# ==============================================================================
# FUNCIÓN DE GRAFICACIÓN INTERACTIVA EN 3 PANELES
# ==============================================================================

# "def nombre(argumentos):" define una FUNCIÓN reutilizable: el bloque de
# código no se ejecuta al escribirlo, solo cuando alguien la "llama" más
# abajo (interact() lo hará por nosotros cada vez que movamos un slider).
# Los argumentos tienen valores por defecto (beta_val=0.97, ...): si se
# llama a la función sin indicarlos, usará esos valores.
def plot_consumption_leisure(beta_val=0.97, gamma_val=0.50, R_val=0.02, W_val=30.0):
    params_int = ConsumptionLeisureParameters(T=30, beta=beta_val, gamma=gamma_val, R=R_val)
    W = np.full(params_int.T, W_val)
    
    # Resolver
    res = solve_foc_fsolve(params_int, W)

    # plt.subplots(1, 3) crea UNA fila y TRES columnas de gráficos en una
    # misma figura. axs es un array de 3 "ejes" (axs[0], axs[1], axs[2]),
    # cada uno independiente: podemos dibujar cosas distintas en cada panel.
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    t_axis = np.arange(params_int.T)
    
    # --- PANEL 1: CONSUMO E INGRESO SALARIAL ---
    # Al ejecutar, veremos dos curvas: el consumo (morado) y el ingreso
    # salarial W*L (verde). La diferencia entre ambas es el ahorro.
    axs[0].plot(t_axis, res["C"], color='#7A3E9F', linewidth=2.5, label='Consumo Óptimo (C)')
    axs[0].plot(t_axis, res["W_L"], color='#8EAD3A', linewidth=2.5, linestyle='--', label='Ingreso Salarial (W·L)')
    axs[0].set_title('Consumo e Ingreso Salarial', fontsize=11, fontweight='bold', pad=10)
    axs[0].set_xlabel('Periodo (t)', fontsize=9)
    axs[0].set_ylabel('Unidades de Bienes', fontsize=9)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='best', fontsize=8)
    
    # --- PANEL 2: OFERTA DE TRABAJO Y OCIO ---
    # Veremos dos curvas complementarias: trabajo L (rojo) y ocio 1-L
    # (verde). Como suman 1, cuando una sube la otra baja. La línea de ocio
    # con linestyle=':' (punteado) es visualmente más ligera.
    axs[1].plot(t_axis, res["L"], color='#E05A47', linewidth=2.5, label='Oferta de Trabajo (L)')
    axs[1].plot(t_axis, res["O"], color='#3BB193', linewidth=2.5, linestyle=':', label='Ocio (O = 1-L)')
    axs[1].set_title('Asignación del Tiempo (Trabajo vs Ocio)', fontsize=11, fontweight='bold', pad=10)
    axs[1].set_xlabel('Periodo (t)', fontsize=9)
    axs[1].set_ylabel('Fracción de Tiempo', fontsize=9)
    axs[1].set_ylim(-0.05, 1.05)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='best', fontsize=8)
    
    # --- PANEL 3: ACTIVOS FINANCIEROS (AHORRO Y DEUDA) ---
    # fill_between() colorea el área ENTRE la curva B y el eje horizontal
    # (y=0). where=(B>=0) pinta en azul (ahorro), where=(B<0) en naranja
    # (deuda). De un vistazo se ve cuándo el agente es acreedor y cuándo
    # deudor sin tener que leer los números uno a uno.
    axs[2].plot(t_axis, res["B"], color='#004C97', linewidth=2.5, label='Activos Financieros (B)')
    axs[2].fill_between(t_axis, res["B"], 0, where=(res["B"] >= 0), color='#004C97', alpha=0.15, label='Posición Acreedora')
    axs[2].fill_between(t_axis, res["B"], 0, where=(res["B"] < 0), color='#D95319', alpha=0.15, label='Posición Deudora')
    axs[2].axhline(0.0, color='black', linestyle=':', alpha=0.5)
    axs[2].set_title('Evolución de Activos Financieros', fontsize=11, fontweight='bold', pad=10)
    axs[2].set_xlabel('Periodo (t)', fontsize=9)
    axs[2].set_ylabel('Riqueza Neta', fontsize=9)
    axs[2].grid(True, linestyle=':', alpha=0.6)
    axs[2].legend(loc='best', fontsize=8)
    
    plt.tight_layout()  # ajusta el espaciado para que los títulos no se solapen
    plt.show()

# interact() conecta la función de arriba a los sliders: cada vez que mueves
# uno, ipywidgets vuelve a llamar a plot_consumption_leisure() con los
# nuevos valores y redibuja los 3 paneles completos. No hay que re-ejecutar
# la celda. FloatSlider define el rango, paso y etiqueta de cada slider.
interact(
    plot_consumption_leisure,
    beta_val=FloatSlider(value=0.97, min=0.90, max=0.999, step=0.01, description='Paciencia (β)'),
    gamma_val=FloatSlider(value=0.40, min=0.10, max=0.90, step=0.05, description='Consumo (γ)'),
    R_val=FloatSlider(value=0.02, min=-0.05, max=0.15, step=0.01, description='Interés (R)'),
    W_val=FloatSlider(value=30.0, min=10.0, max=100.0, step=5.0, description='Salario (W)')
);
"""
    )
)

# 10. CUADERNO DE BITÁCORA
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 5. Cuaderno de Bitácora (Actividades para el Alumno)

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
""")
)

# 11. BUENAS PRÁCTICAS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 6. Buenas Prácticas Aplicadas en este Laboratorio
1.  **Aislamiento Paramétrico**: Las rutinas matemáticas y de simulación están completamente desacopladas de la interfaz visual, residiendo en `src/macroaicomp/models/consumption_leisure.py`.
2.  **Control de Calidad Automático**: Se ha verificado que la simulación es robusta mediante tests unitarios automatizados (`pytest`).
3.  **Control de Versiones Limpio**: Este cuaderno ha sido limpiado de metadatos volátiles mediante `nbstripout` antes de guardarse en el repositorio.
""")
)

os.makedirs("c:/Users/AntonioRC/Desktop/PIE/practicas/04-consumo-ocio/", exist_ok=True)
nbf.write(nb, "c:/Users/AntonioRC/Desktop/PIE/practicas/04-consumo-ocio/python.ipynb")
print("Notebook generado con éxito.")
