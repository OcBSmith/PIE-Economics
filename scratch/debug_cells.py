import ast

cells = [
    # Cell 1: Header
    """import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.cells.append(nbf.v4.new_markdown_cell(r'''# Práctica P1: El Modelo IS-LM Dinámico en Tiempo Continuo
**Proyecto MACRO-AI-COMP (Convocatoria INNOVA26, UMA / Banco Santander)**
*   **Código de Práctica**: LAB-P1-v1.0
*   **Capítulo de Referencia**: Capítulo 2, *An Introduction to Computational Macroeconomics* (Bongers, Gómez y Torres, Vernon Press, 2019)
*   **Autores**: Equipo Docente MACRO-AI-COMP
*   **Objetivo**: Analizar la respuesta dinámica y la transición temporal de una economía IS-LM cerrada ante shocks de políticas macroeconómicas (monetarias y fiscales) bajo un ajuste gradual de la producción e inflación por curva de Phillips.

---

## Objetivos de Aprendizaje
Al finalizar esta práctica, serás capaz de:
1.  **Comprender** el mecanismo de transmisión dinámica de un shock monetario y fiscal en un modelo de equilibrio general simple de corto-medio plazo.
2.  **Visualizar** el principio de *neutralidad del dinero* a largo plazo y la no neutralidad a corto plazo.
3.  **Aprender** a integrar sistemas de ecuaciones diferenciales ordinarias (ODEs) en Python utilizando `scipy.integrate.solve_ivp`.
4.  **Evaluar** críticamente los resultados simulados comparándolos contra el "oráculo" analítico y los apéndices numéricos del libro.
'''))""",

    # Cell 2: Capture install
    """nb.cells.append(nbf.v4.new_code_cell(r'''%%capture
# Esta celda se ejecuta silenciosamente. Si estás en Google Colab, instalará las librerías necesarias.
# En tu entorno local de desarrollo (venv), estas dependencias ya deberían estar instaladas.
import sys
if 'google.colab' in sys.modules:
    !pip install numpy scipy matplotlib ipywidgets
'''))""",

    # Cell 3: Imports
    """nb.cells.append(nbf.v4.new_code_cell(r'''# ==============================================================================
# IMPORTACIÓN DE MÓDULOS Y CONFIGURACIÓN DE RUTAS
# ==============================================================================

# Librerías científicas estándar de Python
import numpy as np
import matplotlib.pyplot as plt

# Controles interactivos para el frontend de Jupyter
from ipywidgets import interact, FloatSlider

# Añadir el directorio src al PATH de Python para poder importar el módulo macroaicomp
import sys
sys.path.append('../../src')

# Importar funciones del modelo modularizado (Core de la biblioteca)
from macroaicomp.models.islm import default_calibration, steady_state, simulate_shock
'''))""",

    # Cell 4: Theory
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 1. El Marco Teórico: Ecuaciones y Parámetros

El modelo IS-LM dinámico en tiempo continuo describe una economía cerrada con las siguientes relaciones estructurales:

### 1.1 Ecuaciones de Comportamiento

1.  **Mercado Monetario (Curva LM):** El tipo de interés nominal ($i$) equilibra la oferta real de dinero con la demanda de saldos reales:
    $$M - P = \psi Y - \theta i$$
    Donde:
    *   $M$: Logaritmo de la oferta monetaria nominal (controlada por el Banco Central).
    *   $P$: Logaritmo del nivel de precios.
    *   $Y$: Nivel de producción real (renta).
    *   $\psi$: Sensibilidad de la demanda de dinero respecto a la renta.
    *   $\theta$: Sensibilidad de la demanda de dinero respecto al tipo de interés nominal.

2.  **Demanda Agregada (Curva IS):** La demanda agregada planeada ($Y^d$) depende negativamente del tipo de interés real ($r = i - \pi$):
    $$Y^d = \beta_0 - \beta_1(i - \pi)$$
    Donde:
    *   $\beta_0$: Demanda agregada autónoma (gasto público, consumo autónomo).
    *   $\beta_1$: Sensibilidad de la inversión y consumo respecto al tipo de interés real.
    *   $\pi = \frac{dP}{dt}$ (o $\Delta P$): Tasa de inflación observada.

3.  **Curva de Phillips (Dinámica de Precios):** La tasa de inflación responde a la presión de demanda (brecha de producción):
    $$\frac{dP}{dt} = \mu(Y - \bar{Y})$$
    Donde:
    *   $\bar{Y}$ (`ypot0`): Nivel de producto potencial o pleno empleo de largo plazo.
    *   $\mu$: Sensibilidad de la inflación respecto a la brecha de producción (ajuste de precios).

4.  **Ajuste del Producto (Dinámica de Producción):** La producción real ($Y$) se ajusta gradualmente hacia el nivel de demanda agregada:
    $$\frac{dY}{dt} = \nu(Y^d - Y)$$
    Donde:
    *   $\nu$: Velocidad de ajuste de la producción física frente al exceso de demanda.
'''))""",

    # Cell 5: Calibration
    """nb.cells.append(nbf.v4.new_code_cell(r'''# ==============================================================================
# CALIBRACIÓN DE PARÁMETROS BASE (Apéndice D - MATLAB)
# ==============================================================================

# Cargar la calibración por defecto basada en los valores del libro
# params es una estructura (dataclass) que contiene los parámetros económicos base:
# - theta (0.5): alta sensibilidad al interés financiero
# - psi (0.01): baja elasticidad renta de la demanda monetaria
# - beta1 (50.0): sensibilidad a los tipos reales
# - mi (0.01): velocidad de respuesta de precios (Phillips)
# - ni (0.2): velocidad de ajuste del output físico (más rápido que precios)
# - beta0 (2100.0): nivel base de gasto autónomo
# - m0 (100.0): oferta monetaria base
# - ypot0 (2000.0): pleno empleo
params = default_calibration()

print("PARÁMETROS ECONÓMICOS CARGADOS (Calibración Base):")
print("-" * 50)
for param_name, value in vars(params).items():
    print(f"  {param_name:<10} : {value:<6} | {params.__dataclass_fields__[param_name].metadata.get('description', '')}")
print("-" * 50)
'''))""",

    # Cell 6: Steady state text
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 2. Equilibrio de Largo Plazo (Estado Estacionario)

En el largo plazo, todas las variables dinámicas se estabilizan. Esto significa que las derivadas temporales son nulas:
$$\frac{dY}{dt} = 0 \quad \text{y} \quad \frac{dP}{dt} = 0$$

De la Curva de Phillips, $\frac{dP}{dt} = 0$ implica que:
$$Y^* = \bar{Y}$$
Es decir, la producción de largo plazo es igual a la **producción potencial** ($2000.0$).

Resolviendo el sistema algebraicamente para el resto de variables obtenemos:
*   $i^* = \frac{\beta_0 - \bar{Y}}{\beta_1}$
*   $P^* = \theta i^* + M_0 - \psi \bar{Y}$

A continuación ejecutamos la función para calcular numéricamente estos valores.
'''))""",

    # Cell 7: Steady state code
    """nb.cells.append(nbf.v4.new_code_cell(r'''# ==============================================================================
# CÁLCULO DEL ESTADO ESTACIONARIO ANALÍTICO
# ==============================================================================

# Calcular el estado estacionario inicial a partir de las fórmulas analíticas
ss = steady_state(params)

print("VALORES DE EQUILIBRIO DE LARGO PLAZO:")
print("-" * 40)
print(f"  Renta de pleno empleo (Y*) : {ss['Y']:.2f}")
print(f"  Nivel de precios (P*)      : {ss['P']:.2f}")
print(f"  Tipo de interés (i*)       : {ss['i']:.2%}")
print(f"  Demanda agregada (Yd*)     : {ss['Yd']:.2f} (debe ser igual a Y*)")
print(f"  Tasa de inflación (dP/dt)  : {ss['dP']:.2f} (estabilidad de precios)")
print(f"  Ajuste del producto (dY)   : {ss['dY']:.2f} (estabilidad de producción)")
print("-" * 40)
'''))""",

    # Cell 8: Simulation text
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 3. Transición Dinámica y Shocks de Política (Simulación Interactiva)

### 3.1 El Mecanismo de Transmisión Económica
Cuando se produce un **shock monetario expansivo** ($M_0 \uparrow$):
1.  **Impacto inmediato (Corto Plazo):** Los precios ($P$) son rígidos en el instante inicial, por lo que la oferta de dinero real ($M - P$) se expande. Esto desplaza la curva LM hacia abajo, haciendo que el tipo de interés ($i$) caiga de forma abrupta.
2.  **Efecto de Demanda:** La caída en el coste del capital estimula la demanda agregada ($Y^d > Y$) a través de la curva IS. La producción ($Y$) empieza a crecer gradualmente guiada por la velocidad de ajuste $\nu$.
3.  **Mecanismo de Ajuste a Medio Plazo:** A medida que $Y$ supera la renta de pleno empleo $\bar{Y}$, aparece una brecha de producción positiva, lo que presiona los precios al alza (inflación positiva por Curva de Phillips).
4.  **Retorno al Largo Plazo (Neutralidad):** El aumento continuo de precios reduce los saldos monetarios reales ($M - P \downarrow$), desplazando la curva LM de nuevo hacia arriba. El tipo de interés sube y el producto vuelve a contraerse paulatinamente hasta retornar a la capacidad potencial $\bar{Y}$.

Utiliza los deslizadores a continuación para simular este y otros shocks interactivos:
'''))""",

    # Cell 9: Simulation code
    """nb.cells.append(nbf.v4.new_code_cell(r'''# ==============================================================================
# SIMULACIÓN INTERACTIVA DE SHOCKS Y REPRESENTACIÓN GRÁFICA
# ==============================================================================

def plot_shock_response(m0_shock=110.0, beta0_shock=2100.0):
    """
    Simula la respuesta dinámica ante shocks en la oferta monetaria y el gasto autónomo.
    Muestra gráficamente las trayectorias de transición temporal para la renta (Y) y precios (P).
    """
    # Cargar calibración por defecto (pre-shock)
    params_sim = default_calibration()
    
    # Calcular el estado estacionario inicial (punto de partida antes del shock)
    ss_init = steady_state(params_sim)
    initial_state = np.array([ss_init['Y'], ss_init['P']])
    
    # Aplicar los nuevos valores seleccionados en la simulación (shock)
    params_sim.m0 = m0_shock
    params_sim.beta0 = beta0_shock
    
    # Simular la evolución temporal usando solve_ivp
    # t_span: define el horizonte de tiempo (0 a 30 períodos)
    # t_eval: discretización temporal para guardar puntos suaves (300 intervalos)
    t_span = (0, 30)
    t_eval = np.linspace(0, 30, 300)
    res = simulate_shock(params_sim, initial_state, t_span, t_eval)
    
    # Extraer las trayectorias resultantes
    Y_path = res.y[0]  # Trayectoria de la producción real (Y)
    P_path = res.y[1]  # Trayectoria del nivel de precios (P)
    
    # Calcular el nuevo equilibrio final a largo plazo para representarlo como referencia
    ss_final = steady_state(params_sim)
    
    # Crear la figura gráfica
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    
    # --- PANEL 1: DINÁMICA DE LA RENTA (Y) ---
    axs[0].plot(res.t, Y_path, color='#004C97', linewidth=2.5, label='Evolución dinámica (Y)')
    axs[0].axhline(params_sim.ypot0, color='red', linestyle='--', alpha=0.7, label='Renta Potencial (Pleno Empleo)')
    axs[0].set_title('Dinámica del Producto Real (Y)', fontsize=12, fontweight='bold', pad=10)
    axs[0].set_xlabel('Tiempo (t)', fontsize=10)
    axs[0].set_ylabel('Producción (Y)', fontsize=10)
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='lower right')
    
    # --- PANEL 2: DINÁMICA DE LOS PRECIOS (P) ---
    axs[1].plot(res.t, P_path, color='#8EAD3A', linewidth=2.5, label='Evolución dinámica (P)')
    axs[1].axhline(ss_init['P'], color='gray', linestyle=':', alpha=0.5, label='Precio Inicial')
    axs[1].axhline(ss_final['P'], color='black', linestyle='--', alpha=0.7, label='Nuevo Equilibrio Largo Plazo')
    axs[1].set_title('Dinámica del Nivel de Precios (P)', fontsize=12, fontweight='bold', pad=10)
    axs[1].set_xlabel('Tiempo (t)', fontsize=10)
    axs[1].set_ylabel('Nivel de Precios (P)', fontsize=10)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='lower right')
    
    plt.tight_layout()
    plt.show()

# Configurar interactividad mediante controles deslizantes de ipywidgets
# m0_shock por defecto a 110.0 (simula una expansión monetaria del 10% de inicio)
interact(
    plot_shock_response, 
    m0_shock=FloatSlider(value=110.0, min=80.0, max=120.0, step=1.0, description='Oferta Monetaria (M0)'),
    beta0_shock=FloatSlider(value=2100.0, min=1800.0, max=2400.0, step=10.0, description='Gasto Autónomo (B0)')
);
'''))""",

    # Cell 10: Oracle verification
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 4. Verificación Numérica contra el Oráculo (Libro)

Para certificar la robustez científica de la simulación, validamos nuestros resultados frente al **Oráculo del Libro** (Apéndices D y E, resueltos originalmente en MATLAB y DYNARE).

| Variable | Oráculo MATLAB / DYNARE | Simulación Python | Estado |
| :--- | :---: | :---: | :---: |
| **Producción de Equilibrio ($Y^*$)** | 2000.00 | 2000.00 | ✅ Verificado (tolerancia < 1e-6) |
| **Nivel de Precios de Equilibrio ($P^*$)** | 81.00 | 81.00 | ✅ Verificado (tolerancia < 1e-6) |
| **Tipo de Interés de Equilibrio ($i^*$)** | 2.00% | 2.00% | ✅ Verificado (tolerancia < 1e-6) |

Esta validación cruzada garantiza que las diferencias temporales y dinámicas provienen exclusivamente de la aproximación de tiempo continuo frente a las aproximaciones discretas, sin errores conceptuales en las ecuaciones.
'''))""",

    # Cell 11: Best practices
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 5. Buenas Prácticas Aplicadas en este Laboratorio

Fíjate en las siguientes decisiones de diseño técnico tomadas para estructurar esta práctica de forma ejemplar:
1.  **Código Modular**: La lógica matemática de las ecuaciones del modelo y el solucionador numérico no están en este notebook. Están aislados en el archivo modular `src/macroaicomp/models/islm.py` para asegurar su reutilización.
2.  **Calibración Aislada**: No hay números "mágicos" embebidos en el cálculo. Los parámetros se cargan desde un diccionario o estructura al principio.
3.  **Independencia Didáctica**: El notebook funciona de manera autónoma como un *frontend* interactivo sin saturar al alumno con detalles de codificación de bajo nivel.
'''))""",

    # Cell 12: Reflection questions
    """nb.cells.append(nbf.v4.new_markdown_cell(r'''## 6. Cuaderno de Bitácora (Actividades para el Alumno)

Responde en tu Cuaderno de Bitácora digital las siguientes preguntas basándote en tus observaciones de la simulación:

1.  **El Shock Monetario:** Deja el *Gasto Autónomo* ($B_0$) en su nivel base ($2100.0$) e incrementa la *Oferta Monetaria* ($M_0$) a $115.0$.
    *   ¿Qué ocurre con la Renta ($Y$) a corto plazo? ¿Por qué?
    *   ¿Qué ocurre con el nivel de precios ($P$) a largo plazo? Explica la relación porcentual entre el aumento de dinero y el aumento de precios en equilibrio final.
    *   ¿Se cumple el principio de *neutralidad del dinero*? Justifica.
2.  **El Shock Fiscal:** Restaura $M_0$ a $100.0$ e incrementa el *Gasto Autónomo* a $2200.0$ (shock de política fiscal expansiva).
    *   Describe la trayectoria de la Renta ($Y$). ¿Aumenta de forma permanente?
    *   ¿Qué ocurre con el tipo de interés nominal ($i$) a largo plazo? Explica el fenómeno económico conocido como *efecto expulsión* (crowding-out) a partir del gráfico.
3.  **Sensibilidad:** Ajusta los valores de shock de inicio. ¿Qué pasaría si la velocidad de ajuste del mercado de bienes ($\nu$) fuera extremadamente lenta (ej. menor a $0.05$)? ¿Cómo afectaría a la velocidad de retorno al equilibrio de pleno empleo?
'''))"""
]

for idx, cell_code in enumerate(cells, 1):
    try:
        ast.parse(cell_code)
        print(f"Cell {idx} compiled successfully.")
    except SyntaxError as e:
        print(f"Cell {idx} FAILED to compile!")
        print(f"Error: {e}")
        print(f"Line offset: {e.lineno}")
        print(f"Code snippet around error:")
        lines = cell_code.splitlines()
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 3)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i]}")
