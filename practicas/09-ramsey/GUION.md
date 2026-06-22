# GUION-P9: El modelo de crecimiento óptimo de Ramsey

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P9-v1.0
- **Capítulo del libro:** Cap. 10 — *Ramsey's optimal growth* (Bongers, Gómez y Torres, 2019). Modelo de crecimiento óptimo de Ramsey-Cass-Koopmans.

> ⚠️ **Este documento es material de referencia para el profesor.**
> El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
> cuestionario de bitácora y extensiones ABP) dentro del propio notebook
> (python.ipynb / julia.ipynb). Este GUION queda como chuleta del
> instructor con los detalles técnicos que el alumno no necesita ver:
> librerías, versiones, accidentes típicos y referencias.

## "Reactivos" digitales (librerías y versiones)

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/ramsey.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `NLsolve.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Ramsey.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice P DYNARE).

## Posibles accidentes de laboratorio (chuleta del profesor)

- **Bisección de shooting infinita**: el resolvedor no lineal de Julia usa un bucle de bisección para encontrar el $c_0$ óptimo. Si el shock es muy intenso, el bucle puede no converger. El código tiene un límite máximo de 50 iteraciones — si se supera, relaja la magnitud del shock o usa la aproximación lineal como punto de partida.
- **Errata en la ecuación de capital linealizada (10.72)**: el libro impreso omite el factor $(1+n)$ en el denominador de la desviación de consumo en la ecuación de capital linealizada. El código del proyecto ya está corregido usando la hoja de cálculo original y DYNARE.
- **Confundir $R^*$ de Ramsey con $R$ de P3-P5**: en Ramsey, $R^*$ es endógeno (determinado por la productividad marginal del capital en SS). En P3-P5, $R$ es exógeno. $R^*_{Ramsey} = \alpha / (\alpha / (1/\beta - 1 + \delta))$ — es un resultado, no un parámetro.
- **$\theta$ vs $\eta$**: la pendiente de salto $\theta$ de Ramsey es el análogo a las funciones de política $\eta_{ck}$ del DGE (P7). Ambas indican cómo salta la variable forward-looking ($c$) ante una desviación de la predeterminada ($k$). No confundir con otras $\theta$ del proyecto (P0 la usa para otro parámetro).

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 10. Vernon Press.
- Ramsey, F.P. (1928), "A Mathematical Theory of Saving", *The Economic Journal* 38(152), 543-559.
- Cass, D. (1965), "Optimum Growth in an Aggregative Model of Capital Accumulation", *Review of Economic Studies* 32(3), 233-240.
- Apéndice P (DYNARE, `referencia/`).
- `oraculo.md` (esta misma carpeta).
