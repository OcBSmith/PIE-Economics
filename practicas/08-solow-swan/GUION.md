# GUION-P8: El modelo neoclásico de crecimiento exógeno (Solow-Swan)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P8-v1.0
- **Capítulo del libro:** Cap. 9 — *Neoclassical exogenous growth* (Bongers, Gómez y Torres, 2019). Modelo de crecimiento neoclásico de Solow-Swan.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/growth.py`).
- **Julia**: `Plots.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Growth.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice O MATLAB).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **Confundir niveles con per cápita**: todas las variables del modelo están en términos per cápita. Si las confundes con niveles agregados, la ecuación de acumulación incluirá incorrectamente el crecimiento poblacional.
- **El consumo NO sube inmediatamente tras el shock de ahorro**: es el error conceptual más común. Un aumento de $s$ significa que se CONSUME MENOS hoy para invertir más, lo que a largo plazo produce más output y más consumo. Pero en el impacto, $c$ BAJA. Si tu gráfica muestra $c$ subiendo desde $t=0$, revisa $c_t = (1-s)y_t$.
- **La Regla de Oro NO es $s=1-\alpha$**: $s^{gold} = \alpha$ es específica de la función Cobb-Douglas. Con CES, la regla de oro sería distinta. Si lees "Regla de Oro = 0.35", es porque $\alpha=0.35$, no es una constante universal.
- **$n=0.02$ vs $n=0.015$**: la calibración de Julia usaba $n=0.015$ antes de la homogeneización. Si el SS no coincide con el oráculo, comprueba que $n$ es exactamente $0.02$.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 9. Vernon Press.
- Solow, R.M. (1956), "A Contribution to the Theory of Economic Growth", *Quarterly Journal of Economics* 70(1), 65-94.
- Apéndice O (MATLAB, `referencia/`).
- `oraculo.md` (esta misma carpeta).
