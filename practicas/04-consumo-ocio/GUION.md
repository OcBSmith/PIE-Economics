# GUION-P4: La decisión óptima de consumo-ocio y ahorro

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P4-v1.0
- **Capítulo del libro:** Cap. 5 — *Consumption-saving + leisure* (Bongers, Gómez y Torres, 2019). Elección conjunta de consumo, ahorro y oferta de trabajo.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `cvxpy`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/consumption_leisure.py`).
- **Julia**: `Plots.jl`, `NLsolve.jl`, `Optim.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/ConsumptionLeisure.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice I MATLAB).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **Indexado out-of-bounds en el sistema FOC**: el Apéndice I (MATLAB) original contiene una errata de indexación que deja $f(2T-1)$ vacío y referencia $f(2T+1)$ (fuera de rango). El código del proyecto ya está corregido con indexado 0 a $2T-1$ cuadrado y robusto. Si modificas el bucle de residuos y ves `IndexError`, revisa los índices contra el tamaño del vector de variables.
- **$L_t \ge 1$**: si la solución da $L_t \ge 1$, significa que el consumidor "trabajaría más horas de las que tiene". Esto puede ocurrir con salarios extremadamente altos o $\gamma$ muy cercano a 1. El modelo no impone explícitamente $L_t < 1$ en la FOC; se verifica a posteriori.
- **Confundir efecto renta y sustitución en el widget de salario**: un aumento de salario tiene efecto renta positivo (consumo de ocio aumenta) y efecto sustitución (ocio se encarece, se consume menos). Cuál domina depende de la calibración — no asumir que el trabajo siempre aumenta con el salario.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 5. Vernon Press.
- Apéndice I (MATLAB, `referencia/`).
- `oraculo.md` (esta misma carpeta).
