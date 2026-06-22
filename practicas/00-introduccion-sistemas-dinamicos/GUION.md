# GUION-P0: Introducción a los sistemas dinámicos computacionales

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora). Primer piloto de la plantilla
> `practicas/_plantilla/GUION.md` (Hito 2 del plan maestro).

- **ID de práctica:** LAB-P0-v1.0
- **Capítulo del libro:** Cap. 1 — *An introduction to computational dynamic
  systems* (Bongers, Gómez y Torres, 2019). Modelo de carrera de armamentos
  de Richardson.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp`
  (`src/macroaicomp/models/arms_race.py`, `src/macroaicomp/plotting/phase_diagram.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `BenchmarkTools.jl` + paquete
  `MacroAIComp` (`src/models/ArmsRace.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del
  libro + `referencia/m1.m`, Apéndice B MATLAB, y `referencia/m1d.mod`,
  Apéndice C DYNARE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **`NameError` al ejecutar una celda**: casi siempre significa que se
  ejecutó una celda sin haber ejecutado antes la celda de imports (celda 3)
  en esa misma sesión de kernel. Solución: `Kernel` → `Restart & Run All`.
- **`ValueError` al llamar a `simulate_saddle_path`**: esa función exige que
  la calibración sea realmente un punto de silla (un autovalor estable y
  otro inestable); si se cambian los parámetros del Caso 2 y deja de
  cumplirse esa condición, la función lo detecta y avisa en vez de devolver
  un resultado sin sentido.
- **Confundir el índice del periodo del shock**: Python indexa los arrays
  desde 0 y Julia desde 1, así que el mismo "periodo 1" se lee como
  `x1_path[1]` en Python pero `x1_path[2]` en Julia. Si al cambiar
  `shock_period` el resultado no coincide con lo esperado, revisar primero
  si el índice usado corresponde al lenguaje correcto.
- **En Julia, intercambiar el orden de los argumentos de `ArmsRaceParams`**:
  a diferencia de Python (que usa argumentos con nombre), en Julia el
  struct se construye con argumentos posicionales. Cambiar el orden no
  lanza ningún error — simplemente da un resultado numérico distinto al
  esperado, porque cada número se asigna a la casilla equivocada.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to
  Computational Macroeconomics*, Cap. 1. Vernon Press.
- Apéndice B (MATLAB, `referencia/m1.m`) y Apéndice C (DYNARE,
  `referencia/m1d.mod`).
- `oraculo.md` (esta misma carpeta).
