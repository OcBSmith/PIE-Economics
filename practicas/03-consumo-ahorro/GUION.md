# GUION-P3: La decisión óptima de consumo-ahorro

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P3-v1.0
- **Capítulo del libro:** Cap. 4 — *Consumption-saving optimal decision* (Bongers, Gómez y Torres, 2019). Decisión intertemporal de consumo y ahorro del hogar representativo.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `cvxpy`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/consumption_savings.py`).
- **Julia**: `Plots.jl`, `NLsolve.jl`, `Optim.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/ConsumptionSavings.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + `referencia/`, Apéndice G MATLAB y Apéndice H Newton).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **`fsolve` no converge**: si cambias los parámetros a valores extremos ($\beta$ muy cercano a 1, $R$ muy alto), el sistema de $2T-1$ ecuaciones puede volverse numéricamente difícil. El resolvedor `cvxpy` es más robusto — si `fsolve` falla, compara con `cvxpy` para diagnosticar si es un problema numérico o de especificación.
- **Condición terminal $B_T \neq 0$**: el código MATLAB original del Apéndice G contiene una errata en la ecuación residual terminal que forzaba erróneamente $B_T = W_T$ en lugar de $B_T = 0$. Si modificas el código y obtienes activos terminales no nulos, revisa la ecuación del último periodo.
- **Confundir ahorro con activos**: los activos financieros $B_t$ pueden ser negativos (deuda), lo que NO significa que el consumidor no esté optimizando — simplemente está tomando prestado contra ingresos futuros. El ahorro flujo es $B_t - B_{t-1}$.
- **Indexado temporal**: el modelo usa $t=0,1,\dots,T-1$ (Python) o $t=1,\dots,T$ (Julia). El "último periodo" es $T-1$ en Python y $T$ en Julia. Si verificas $B_T=0$ en el índice equivocado, parecerá un error que no existe.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 4. Vernon Press.
- Apéndice G (MATLAB, `referencia/`) y Apéndice H (Newton, `referencia/`).
- `oraculo.md` (esta misma carpeta).
