# GUION-P6: La empresa y la decisión de inversión (Q de Tobin)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P6-v1.0
- **Capítulo del libro:** Cap. 7 — *Firm/investment, Tobin's Q* (Bongers, Gómez y Torres, 2019). Modelo de inversión con costes de ajuste y Q de Tobin.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/tobin_q.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `NLsolve.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/TobinQ.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice K DYNARE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **`compute_linearized_system` con 2 argumentos**: la función en `TobinQ.jl` solo acepta 1 argumento (`params`). Si la celda la llama con 2 argumentos (`params, R_final`), lanzará `MethodError`. Usa `compute_linearized_system(params)` y modifica `params.R` antes de llamar.
- **Signo de los costes de ajuste en la Euler no lineal**: el resolvedor no lineal usa la condición de optimalidad con costes de ajuste. Si el signo del término cuadrático está mal, la trayectoria de $q$ divergirá en lugar de converger.
- **Confundir log-desviaciones con niveles**: los autovalores $(-0.0607, 0.1072)$ SON log-desviaciones, no niveles. Para pasarlos a niveles discretos: $1+\lambda$. Solo entonces se aplica el criterio $|1+\lambda| \lessgtr 1$ para estabilidad.
- **El diagrama de fases no muestra el saddle path correcto**: el locus $\Delta \hat{q}=0$ debe tener pendiente (no ser vertical). Si es vertical, la matriz de transición log-linealizada no se ha calculado correctamente.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 7. Vernon Press.
- Tobin, J. (1969), "A General Equilibrium Approach to Monetary Theory", *Journal of Money, Credit and Banking* 1(1), 15-29.
- Apéndice K (DYNARE, `referencia/`).
- `oraculo.md` (esta misma carpeta).
