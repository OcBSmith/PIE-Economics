# GUION-P2: Overshooting del tipo de cambio (Dornbusch)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P2-v1.0
- **Capítulo del libro:** Cap. 3 — *Exchange rate overshooting* (Bongers, Gómez y Torres, 2019). Modelo de overshooting del tipo de cambio de Dornbusch.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/dornbusch.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Dornbusch.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + `referencia/m2d.mod`, Apéndice F DYNARE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **Confundir $\beta_1$ con $\beta_2$ en la ecuación de $s^*$**: el libro original contiene una errata tipográfica en esa ecuación (usa $\beta_2$ donde debería usar $\beta_1$). El código del proyecto ya está corregido, pero si comparas con el texto impreso verás una discrepancia — confía en el código y en el oráculo.
- **Interpretar el salto de $s$ como una ineficiencia**: el overshooting no es un "fallo de mercado", es la respuesta óptima del mercado de divisas ante la rigidez de precios. Si los precios fueran flexibles, $s$ saltaría directamente al nuevo SS sin overshooting.
- **Signo del autovalor inestable**: en diferencias, un autovalor > 0 en el módulo $\lambda+1$ indica inestabilidad. $\lambda_2 = 0.5395 \Rightarrow |1+0.5395| = 1.5395 > 1$ — la raíz es inestable. Si calculas $|\lambda|$ en vez de $|\lambda+1|$, obtendrás una conclusión equivocada.
- **Shock con timing incorrecto en Julia**: el salto ocurre en el periodo del shock (`shock_period=1`). En Julia (indexado 1-based), esto es índice 2 del array devuelto (el índice 1 es t=0, pre-shock). Si inspeccionas `s[1]` esperando el salto, verás el valor pre-shock.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 3. Vernon Press.
- Dornbusch, R. (1976), "Expectations and Exchange Rate Dynamics", *Journal of Political Economy* 84(6), 1161-1176.
- Apéndice F (DYNARE, `referencia/m2d.mod`).
- `oraculo.md` (esta misma carpeta).
