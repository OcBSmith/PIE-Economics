# GUION-P5: Gobierno y política fiscal

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P5-v1.0
- **Capítulo del libro:** Cap. 6 — *Government and fiscal policy* (Bongers, Gómez y Torres, 2019). Tres escenarios: impuestos de suma fija, impuestos distorsionadores y Seguridad Social.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `cvxpy`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/fiscal_policy.py`).
- **Julia**: `Plots.jl`, `NLsolve.jl`, `Optim.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/FiscalPolicy.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice J MATLAB).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **El widget de $\tau_r$ no parece tener efecto**: antes de la homogeneización Julia↔Python (2026-06-22), el widget de impuestos distorsionadores de P5 Julia pasaba los argumentos posicionales de `FiscalPolicyParameters` en orden equivocado, filtrando `taur_val` a un campo que no era $\tau_r$. Si observas este bug regresado, comprueba el orden de los argumentos del struct.
- **La Equivalencia Ricardiana no se cumple exactamente**: si la diferencia de consumo no es 0.0, comprueba que las transferencias se están devolviendo correctamente (el gobierno recauda $\tau_w W_t$ y lo transfiere como lump-sum $G_t = \tau_w W_t$ a cada hogar en cada periodo).
- **Surrogate convex problem**: la Sección 2 usa un problema sustituto con pesos de utilidad y tasas de descuento modificados ($\beta^{eff}, \gamma^{eff}$). Si cambias las fórmulas de este problema sustituto, la equivalencia FOC vs cvxpy se romperá — el surrogate NO es un truco numérico, es una derivación analítica exacta.
- **Confundir SS de capitalización con SS de reparto**: en este modelo la SS es de capitalización (lo cotizado se invierte y se devuelve capitalizado), NO de reparto (los jóvenes pagan las pensiones de los jubilados). El resultado de "ahorro privado negativo" solo se da con capitalización.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 6. Vernon Press.
- Apéndice J (MATLAB, `referencia/`).
- Barro, R.J. (1974), "Are Government Bonds Net Wealth?", *Journal of Political Economy* 82(6), 1095-1117.
- `oraculo.md` (esta misma carpeta).
