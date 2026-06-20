# Guía de Referencia Pedagógica — MACRO-AI-COMP

Esta guía está diseñada para profesores, alumnos e investigadores de la Universidad de Málaga (UMA). Su objetivo es facilitar el aprendizaje y la experimentación con los modelos macroeconómicos del proyecto, tanto si se cuenta con experiencia previa en entornos interactivos (Jupyter) como si se prefiere trabajar mediante scripts de consola.

---

## 1. Introducción Rápida a Jupyter Notebooks (El "Frontend")

Si nunca has usado un cuaderno de Jupyter (*Jupyter Notebook*), piensa en él como un **documento dinámico interactivo** que combina tres elementos en una sola página web:
1. **Texto enriquecido y ecuaciones (Markdown/LaTeX)**: Explicaciones del modelo macroeconómico, sus ecuaciones matemáticas y sus implicaciones.
2. **Celdas de código (Python o Julia)**: Bloques ejecutables donde se definen los parámetros, se resuelven las ecuaciones y se simulan los shocks.
3. **Resultados y Gráficos interactivos**: Al ejecutar el código, las gráficas resultantes y los estados estacionarios se muestran en pantalla inmediatamente debajo del código.

### ¿Cómo interactuar con un Notebook?
* **Las Celdas**: El cuaderno está dividido en bloques o "celdas". Las celdas de código tienen un indicador a la izquierda como `In [1]:`.
* **Ejecutar una Celda**: Selecciona una celda de código y pulsa **`Shift + Enter`** (o haz clic en el botón *Run* de la barra superior). El código se ejecutará y el foco pasará a la celda siguiente.
* **El Kernel**: Detrás del notebook hay un motor computacional activo (el *kernel* de Python o Julia). Si algo se queda atascado o quieres reiniciar todos los cálculos desde cero, ve al menú superior y selecciona **`Kernel` -> `Restart & Run All`**.

---

## 2. Cómo Ejecutar los Modelos sin Jupyter (Mediante Consola)

Si prefieres no usar el navegador web, puedes ejecutar cualquier modelo directamente mediante scripts estándar de consola utilizando los archivos de origen de Python y Julia.

### 2.1. Vía Python (Terminal de comandos)
Asegúrate de estar en el directorio raíz del proyecto (`c:\Users\AntonioRC\Desktop\PIE`) y de tener el entorno virtual activado.

#### Ejemplo: Ejecutar un script de simulación de IS-LM (P1) en Python
Puedes crear un script temporal en la carpeta `scratch/prueba_islm.py` con el siguiente contenido:

```python
import numpy as np
from macroaicomp.models.islm import default_calibration, steady_state, simulate_shock

# 1. Cargar parámetros por defecto
params = default_calibration()
print("Parámetros:", params)

# 2. Calcular estado estacionario
ss = steady_state(params)
print(f"Estado Estacionario: Y* = {ss['Y']}, P* = {ss['P']}, i* = {ss['i']}%")

# 3. Simular un shock monetario
params.m0 = 101.0  # Incrementamos la oferta monetaria
ss_new = steady_state(params)
print(f"Nuevo Estado Estacionario: Y* = {ss_new['Y']}, P* = {ss_new['P']}, i* = {ss_new['i']}%")
```

Para ejecutarlo, escribe en tu terminal:
```bash
.venv\Scripts\python.exe scratch/prueba_islm.py
```

---

### 2.2. Vía Julia (Consola REPL)
Puedes abrir la consola interactiva de Julia (REPL) y cargar directamente nuestra biblioteca `MacroAIComp`.

#### Ejemplo: Ejecutar el modelo IS-LM (P1) en el REPL de Julia
Abre tu consola de Julia apuntando al entorno del proyecto:
```bash
C:\Users\AntonioRC\AppData\Local\Programs\Julia-1.12.6\bin\julia.exe --project=.
```

Una vez dentro de la consola REPL de Julia, ejecuta los siguientes comandos:
```julia
# 1. Cargar el paquete del proyecto
using MacroAIComp

# 2. Inicializar parámetros
params = default_calibration(ISLMParams)

# 3. Calcular estado estacionario
ss = steady_state(params)
println("Renta de equilibrio Y* = ", ss["Y"])
println("Tipo de interés i* = ", ss["i"], "%")
```

---

## 3. Comparativa de Código: Python vs. Julia

Para comprender cómo traduce cada lenguaje la teoría económica, comparemos la estructura matemática de ambos.

### 3.1. Representación de Parámetros
En economía, es vital agrupar los parámetros del modelo (tasas de descuento, elasticidades) en una estructura limpia.

| Característica | Implementación en Python (`src/macroaicomp/models/`) | Implementación en Julia (`src/models/`) |
| :--- | :--- | :--- |
| **Definición** | Usa `dataclasses` para mutabilidad y legibilidad de valores por defecto. | Usa `struct` (inmutables por defecto) para optimizar el rendimiento. |
| **Código** | ```python<br>@dataclass<br>class ISLMParameters:<br>    theta: float = 0.5<br>    psi: float = 0.01<br>    beta1: float = 50.0<br>``` | ```julia<br>struct ISLMParams<br>    theta::Float64<br>    psi::Float64<br>    beta1::Float64<br>end<br>``` |

---

### 3.2. Solución de Ecuaciones Dinámicas (Continuas y Discretas)
Los modelos continuos (como IS-LM) requieren integradores numéricos de ecuaciones diferenciales.

#### En Python (SciPy):
Usa `solve_ivp` de la librería `scipy.integrate`. La función de derivadas toma el estado de la economía y devuelve los cambios en el tiempo:
```python
def system_dynamics(t: float, state: np.ndarray, params: ISLMParameters) -> np.ndarray:
    Y, P = state
    i = (P - params.m0 + params.psi * Y) / params.theta
    Yd = params.beta0 - params.beta1 * i
    dY = params.ni * (Yd - Y)
    dP = params.mi * (Y - params.ypot0)
    return np.array([dY, dP])
```

#### En Julia (DifferentialEquations.jl):
Usa `ODEProblem` y `solve`. Las funciones se definen de forma similar, aprovechando el compilador JIT de Julia para una ejecución mucho más rápida:
```julia
function system_dynamics(u::AbstractVector, params::ISLMParams, t::Real)
    Y, P = u
    i = (P - params.m0 + params.psi * Y) / params.theta
    Yd = params.beta0 - params.beta1 * i
    dY = params.ni * (Yd - Y)
    dP = params.mi * (Y - params.ypot0)
    return [dY, dP]
end
```

---

## 4. Despacho Múltiple (Multiple Dispatch) en Julia

Una de las mayores ventajas pedagógicas de Julia es el **despacho múltiple**. Nos permite definir una función con el mismo nombre (ej. `default_calibration` o `solve_direct_optim`) y que Julia decida qué algoritmo ejecutar según el tipo de parámetros que le pasemos.

### Ejemplo didáctico:
En la biblioteca del proyecto, para obtener la calibración base de cualquier modelo, el estudiante solo tiene que recordar una única función:
```julia
# Calibrar Solow-Swan (P8)
params_solow = default_calibration(SolowSwanParameters)

# Calibrar Ramsey (P9)
params_ramsey = default_calibration(RamseyParams)
```
Julia detecta automáticamente el tipo de dato del argumento (`SolowSwanParameters` vs `RamseyParams`) y redirige internamente a la rutina matemática correspondiente. En Python, esto requeriría importar funciones con nombres distintos para cada práctica (como `default_calibration_solow()` y `default_calibration_ramsey()`).
