# GUION-P8: El modelo neoclásico de crecimiento exógeno (Solow-Swan)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P8-v1.0
- **Capítulo del libro:** Cap. 9 — *Neoclassical exogenous growth* (Bongers, Gómez y Torres, 2019). Modelo de crecimiento neoclásico de Solow-Swan.

## Objetivos didácticos

1. **Calcular** la dinámica de transición hacia el estado estacionario tras un shock en la tasa de ahorro, la tasa de crecimiento poblacional o la productividad.
2. **Identificar** la Regla de Oro de la acumulación de capital ($s^{gold} = \alpha$) que maximiza el consumo per cápita de largo plazo.
3. **Comparar** la convergencia condicional del modelo de Solow-Swan con la optimalidad del modelo de Ramsey (P9), entendiendo por qué la tasa de ahorro exógena puede llevar a ineficiencia dinámica.

## Conocimientos previos requeridos

- **Matemáticas**: ecuaciones en diferencias no lineales de primer orden, diagrama de Solow, análisis de estabilidad gráfico y analítico.
- **Economía**: función de producción neoclásica (Cobb-Douglas), acumulación de capital, estado estacionario, tasa de crecimiento de largo plazo, Regla de Oro de Phelps.
- **Programación**: ninguno previo.
- **Práctica previa recomendada**: P0 (sistemas dinámicos) y opcionalmente P9 (Ramsey — es el contrapunto óptimo de Solow-Swan).

## Tiempo estimado y nivel

~90-120 minutos. Grado en Economía, asignatura de Macroeconomía (crecimiento económico) o Teoría del Crecimiento.

## "Reactivos" digitales

- **Python**: `numpy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/growth.py`).
- **Julia**: `Plots.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Growth.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice O MATLAB).

## Procedimiento paso a paso

1. **Teoría**: ecuación de acumulación de capital per cápita $k_{t+1} = \frac{1}{1+n}\left[(1-\delta)k_t + sA k_t^\alpha\right]$, estado estacionario $k^*$, diagrama de Solow.
2. **Calibración base**: $\alpha=0.35, s=0.20, \delta=0.06, n=0.02, A=1.0$ — Tabla 9.3 del libro.
3. **Estado estacionario**: $k^*=4.0946, y^*=1.6378, c^*=1.3103, i^*=0.3276$ — verificar contra el oráculo.
4. **Simulación dinámica**: loop de acumulación de capital periodo a periodo hasta alcanzar el nuevo SS.
5. **Shock de ahorro**: $s$ sube de 20% a 25% permanentemente — analizar la caída inmediata del consumo (sacrificio de ahorro) y la posterior convergencia a un SS con mayor $k, y, c$.
6. **Shock de productividad o población**: modificar $A$ o $n$ y observar la transición.
7. **Regla de Oro**: derivar $s^{gold} = \alpha = 0.35$, graficar la curva $c^*(s)$ y mostrar que el consumo estacionario es máximo en $s=\alpha$ y decrece para $s>\alpha$ (ineficiencia dinámica).
8. **Widgets interactivos**: sliders para $s, n, A$ y panel de Regla de Oro con rastreador de consumo respecto al ahorro actual.
9. **Conclusión**: la tasa de ahorro determina el nivel de producción de largo plazo pero no la tasa de crecimiento (que es exógena, cero en términos per cápita sin progreso técnico). Una tasa de ahorro demasiado alta puede ser dinámicamente ineficiente.

## Reacciones esperadas

Ver `oraculo.md`. SS con calibración base: $k=4.09, y=1.64, c=1.31$. Shock $s: 20\% \to 25\%$: $k$ crece monótonamente, $y$ crece monótonamente, $c$ cae en impacto (de $1.31$ a $1.23$) pero converge a un valor mayor ($>1.31$). $g_y$ positiva tras el shock y decreciente hacia 0. Regla de Oro: $c^*$ alcanza su máximo en $s=0.35$, es menor tanto en $s=0.20$ (infra-acumulación) como en $s=0.50$ (sobre-acumulación).

## Posibles accidentes de laboratorio

- **Confundir niveles con per cápita**: todas las variables del modelo están en términos per cápita. Si las confundes con niveles agregados, la ecuación de acumulación incluirá incorrectamente el crecimiento poblacional.
- **El consumo NO sube inmediatamente tras el shock de ahorro**: es el error conceptual más común. Un aumento de $s$ significa que se CONSUME MENOS hoy para invertir más, lo que a largo plazo produce más output y más consumo. Pero en el impacto, $c$ BAJA. Si tu gráfica muestra $c$ subiendo desde $t=0$, revisa $c_t = (1-s)y_t$.
- **La Regla de Oro NO es $s=1-\alpha$**: $s^{gold} = \alpha$ es específica de la función Cobb-Douglas. Con CES, la regla de oro sería distinta. Si lees "Regla de Oro = 0.35", es porque $\alpha=0.35$, no es una constante universal.
- **$n=0.02$ vs $n=0.015$**: la calibración de Julia usaba $n=0.015$ antes de la homogeneización. Si el SS no coincide con el oráculo, comprueba que $n$ es exactamente $0.02$.

## Cuestionario de bitácora

1. ¿Por qué el consumo cae en el impacto tras un aumento de la tasa de ahorro? ¿Bajo qué condición el consumidor estaría dispuesto a aceptar ese sacrificio?
2. ¿Qué significa que una economía esté en la zona de "ineficiencia dinámica" ($s > \alpha$)? ¿Por qué es ineficiente si el PIB per cápita es mayor?
3. Si la tasa de crecimiento poblacional $n$ aumenta, ¿qué ocurre con $k^*, y^*, c^*$? Explica la intuición económica del "capital diluido".
4. Compara el estado estacionario de Solow-Swan ($s=0.20$) con el de Ramsey (P9) — ¿cuál tiene mayor $k^*$ y $c^*$? ¿Por qué?
5. ¿Qué le ocurre a la tasa de crecimiento $g_y$ durante la transición? ¿Por qué no puede ser permanentemente positiva sin progreso técnico?
6. Si se introduce progreso técnico aumentador de trabajo ($A_t$ crece a tasa $g$), ¿cómo cambia la dinámica de $k$ e $y$ en términos per cápita? ¿Y en términos de eficiencia?

## Variantes / extensiones para ABP

1. **Contabilidad del crecimiento (growth accounting)**: descomponer el crecimiento observado de una economía real (ej. España 1980-2020) en contribuciones del capital, trabajo y PTF usando la Cobb-Douglas calibrada.
2. **Convergencia $\beta$ y $\sigma$**: simular varias economías con distintos $k_0$ iniciales y verificar la convergencia condicional predicha por Solow-Swan.
3. **Extensión con capital humano**: añadir acumulación de capital humano $h_t$ al modelo (Mankiw-Romer-Weil) y analizar cómo cambia la velocidad de convergencia y la Regla de Oro.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 9. Vernon Press.
- Solow, R.M. (1956), "A Contribution to the Theory of Economic Growth", *Quarterly Journal of Economics* 70(1), 65-94.
- Apéndice O (MATLAB, `referencia/`).
- `oraculo.md` (esta misma carpeta).
