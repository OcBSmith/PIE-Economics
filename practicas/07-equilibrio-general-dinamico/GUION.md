# GUION-P7: El modelo de Equilibrio General Dinámico (DGE) básico

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P7-v1.0
- **Capítulo del libro:** Cap. 8 — *Basic Dynamic General Equilibrium* (Bongers, Gómez y Torres, 2019). Modelo de equilibrio general dinámico con hogar, empresa y gobierno.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/dge.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `NLsolve.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/DGE.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice L MATLAB, Apéndice M DYNARE, Apéndice N DSGE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **Divergencia en el resolvedor no lineal**: si el fsolve simultáneo diverge, comprueba que $K$ tenga cota inferior estricta ($10^{-8}$) para evitar potencias negativas en la productividad marginal del capital. También verifica que el punto de partida (`c0_guess`) se inicializa cerca del valor de salto linealizado.
- **Indexado temporal de la PTF**: el libro original (MATLAB) usa un timing ligeramente distinto al DYNARE para la productividad en la ecuación de acumulación de capital. El código del proyecto usa el timing de DYNARE por defecto con un toggle opcional `use_matlab_timing` (inactivo por defecto). Si comparas con el MATLAB del libro y ves discrepancias en $K$, comprueba el timing.
- **Error de multiplicación de matrices en BK**: las funciones de política $\eta$ multiplican el vector de estado. Si los vectores no están correctamente dimensionados (ej. `M.flatten()` necesario en Python), la simulación linealizada lanzará `ValueError`.
- **Interpretar erróneamente el hump de $K$**: el capital alcanza su pico CON RETARDO respecto al shock de PTF. Esto NO es inercia ni rigidez — es la consecuencia natural de la acumulación: la inversión alta de hoy se traduce en más capital mañana.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 8. Vernon Press.
- Blanchard, O.J. y Kahn, C.M. (1980), "The Solution of Linear Difference Models under Rational Expectations", *Econometrica* 48(5), 1305-1311.
- Apéndice L (MATLAB, `referencia/`), Apéndice M (DYNARE, `referencia/`) y Apéndice N (DSGE, `referencia/`).
- `oraculo.md` (esta misma carpeta).
