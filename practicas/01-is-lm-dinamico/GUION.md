# GUION-P1: Respuesta dinámica del modelo IS-LM ante shocks monetarios y fiscales

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P1-v1.0
- **Capítulo del libro:** Cap. 2 — *The dynamic IS-LM model* (Bongers, Gómez y Torres, 2019). Modelo IS-LM dinámico con curva de Phillips.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/islm.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `DifferentialEquations.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/ISLM.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + `referencia/m2.m`, Apéndice D MATLAB, y `referencia/m2d.mod`, Apéndice E DYNARE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **`ValueError` en `solve_ivp`**: puede ocurrir si los parámetros generan un sistema stiff (muy rígido). Si el integrador lanza este error, probar con `method='Radau'` o `'BDF'` en lugar del RK45 por defecto.
- **Confundir shock monetario con fiscal en el widget**: el shock monetario ($M_0$) solo desplaza la LM y es neutro a largo plazo; el fiscal ($\beta_0$) desplaza la IS y SÍ cambia la producción de largo plazo. Si al mover un slider la producción a largo plazo no cambia, es que estás moviendo el monetario.
- **Interpretar mal el diagrama de fases**: la trayectoria en espiral NO significa ciclo económico perpetuo — es la convergencia amortiguada hacia el nuevo SS. Si las flechas del campo vectorial apuntan hacia el SS, el sistema es estable.
- **Indexado Julia vs Python**: en Julia los arrays empiezan en índice 1, en Python en 0. Al inspeccionar valores de la simulación, ajustar el índice (ej. `sol[1]` en Julia equivale a `sol[0]` en Python).

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 2. Vernon Press.
- Apéndice D (MATLAB, `referencia/m2.m`) y Apéndice E (DYNARE, `referencia/m2d.mod`).
- `oraculo.md` (esta misma carpeta).
