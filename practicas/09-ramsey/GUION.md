# GUION-P9: El modelo de crecimiento óptimo de Ramsey

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P9-v1.0
- **Capítulo del libro:** Cap. 10 — *Ramsey's optimal growth* (Bongers, Gómez y Torres, 2019). Modelo de crecimiento óptimo de Ramsey-Cass-Koopmans.

## Objetivos didácticos

1. **Calcular** la dinámica de transición óptima del capital y el consumo ante un shock de productividad, comparando la trayectoria de punto de silla con la acumulación exógena de Solow-Swan (P8).
2. **Derivar** la condición de optimalidad intertemporal del planificador central (Ecuación de Euler en tiempo discreto) y la condición de transversalidad.
3. **Comparar** la solución linealizada de Blanchard-Khan con la solución no lineal exacta, evaluando la precisión de la aproximación para shocks de productividad tecnológica e impaciencia ($\beta$).

## Conocimientos previos requeridos

- **Matemáticas**: log-linealización, descomposición de autovalores para punto de silla, sistemas de ecuaciones no lineales acoplados, shooting algorithm.
- **Economía**: problema del planificador central, optimalidad de Pareto, Regla de Oro modificada, inconsistencia temporal, comparación Solow-Swan vs Ramsey.
- **Programación**: ninguno previo.
- **Práctica previa recomendada**: P7 (DGE — misma técnica BK), P8 (Solow-Swan — contrapunto de ahorro exógeno), P3 (consumo-ahorro — Ecuación de Euler en horizonte finito).

## Tiempo estimado y nivel

~120-150 minutos. Grado en Economía (último curso) o Posgrado, asignatura de Teoría del Crecimiento o Macroeconomía Avanzada.

## "Reactivos" digitales

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/ramsey.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `NLsolve.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Ramsey.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice P DYNARE).

## Procedimiento paso a paso

1. **Teoría**: problema del planificador central, Hamiltoniano/valor presente, Ecuación de Euler $\beta(1+R_{t+1})U_c(C_{t+1}) = U_c(C_t)$, condición de transversalidad.
2. **Calibración base**: $\alpha=0.35, \beta=0.97, \delta=0.06, n=0.02, A=1.0$ — Tabla 10.2 del libro.
3. **Estado estacionario**: $k^*=7.95, y^*=2.07, c^*=1.43, i^*=0.64, R^*=0.091$ — comparar con Solow-Swan ($k^*=4.09$ con $s=0.20$).
4. **Verificación frente al oráculo**: comparar SS y autovalores con Apéndice P (DYNARE).
5. **Linealización Blanchard-Khan**: derivar sistema log-linealizado en $(\hat{k}, \hat{c})$, calcular autovalores $(-0.0907, 0.1115)$, pendiente de salto $\theta=0.5751$.
6. **Shock de productividad**: $A$ sube de 1.00 a 1.05 permanentemente en $t=5$, calcular salto de $c$ sobre la senda estable ($\hat{c}_5 = \theta \hat{k}_5$), simular transición.
7. **Shock de impaciencia**: $\beta$ sube de 0.97 a 0.99 — el consumo salta hacia ABAJO en impacto (mayor paciencia → más ahorro → menos consumo hoy).
8. **Comparación BK vs no lineal**: resolver el sistema no lineal con fsolve simultáneo y comparar error relativo para shocks de distinta magnitud (1%, 5%, 20%).
9. **Widgets interactivos**: sliders para shock de productividad ($A$) y descuento ($\beta$).
10. **Conclusión**: Ramsey cierra el curso — es el modelo de crecimiento óptimo que microfundamenta la tasa de ahorro, frente al $s$ exógeno de Solow-Swan. La senda de saddle path es la generalización dinámica de la Regla de Oro.

## Reacciones esperadas

Ver `oraculo.md`. SS: $k^*=7.95, c^*=1.43$. Shock $A: 1.00 \to 1.05$: $c$ salta al alza en $t=5$ (mayor productividad → más consumo hoy y más ahorro para el futuro), $k$ converge monótonamente de 7.95 al nuevo SS mayor. Shock $\beta: 0.97 \to 0.99$: $c$ salta a la baja en impacto (mayor paciencia → se pospone consumo para ahorrar más). Autovalores: $(-0.0907, 0.1115)$ con $\theta=0.5751$. Error relativo BK vs no lineal < 1% para shocks pequeños.

## Posibles accidentes de laboratorio

- **Bisección de shooting infinita**: el resolvedor no lineal de Julia usa un bucle de bisección para encontrar el $c_0$ óptimo. Si el shock es muy intenso, el bucle puede no converger. El código tiene un límite máximo de 50 iteraciones — si se supera, relaja la magnitud del shock o usa la aproximación lineal como punto de partida.
- **Errata en la ecuación de capital linealizada (10.72)**: el libro impreso omite el factor $(1+n)$ en el denominador de la desviación de consumo en la ecuación de capital linealizada. El código del proyecto ya está corregido usando la hoja de cálculo original y DYNARE.
- **Confundir $R^*$ de Ramsey con $R$ de P3-P5**: en Ramsey, $R^*$ es endógeno (determinado por la productividad marginal del capital en SS). En P3-P5, $R$ es exógeno. $R^*_{Ramsey} = \alpha / (\alpha / (1/\beta - 1 + \delta))$ — es un resultado, no un parámetro.
- **$\theta$ vs $\eta$**: la pendiente de salto $\theta$ de Ramsey es el análogo a las funciones de política $\eta_{ck}$ del DGE (P7). Ambas indican cómo salta la variable forward-looking ($c$) ante una desviación de la predeterminada ($k$). No confundir con otras $\theta$ del proyecto (P0 la usa para otro parámetro).

## Cuestionario de bitácora

1. ¿Por qué $k^*$ en Ramsey (7.95) es mayor que $k^*$ en Solow-Swan con $s=0.20$ (4.09)? ¿Qué tasa de ahorro implícita tiene el consumidor de Ramsey en SS?
2. ¿Qué ocurre con el consumo en impacto tras un aumento de $\beta$? ¿Por qué el consumidor reduce consumo hoy si es MÁS paciente (valora más el futuro)?
3. Compara el saddle path de Ramsey con el de Dornbusch (P2): ¿en qué se parecen estructuralmente? ¿Cuál es la variable forward-looking en cada caso?
4. ¿Por qué el error entre BK y la solución no lineal es mayor para el shock de $A=1.20$ (+20%) que para $A=1.01$ (+1%)? ¿Qué términos del modelo causan la no linealidad?
5. ¿Cumple el estado estacionario de Ramsey la Regla de Oro de Phelps ($s=\alpha$)? Si no la cumple, ¿por qué es óptimo no estar en la Regla de Oro?
6. Si se elimina el crecimiento poblacional ($n=0$), ¿cómo cambian $k^*, c^*$ y la dinámica de transición? ¿Se altera la clasificación de punto de silla?

## Variantes / extensiones para ABP

1. **Comparación Solow-Swan vs Ramsey**: simular ambos modelos con la misma calibración ($s$ de Solow ajustado para igualar el $k^*$ de Ramsey) y comparar las dinámicas de transición ante el mismo shock de PTF.
2. **Ramsey estocástico**: introducir shocks aleatorios de PTF y resolver trayectorias óptimas con certainty equivalence, comparando con el caso determinista.
3. **Extensión con gobierno**: añadir gasto público financiado con impuestos distorsionadores en el modelo de Ramsey y analizar la pérdida de bienestar (Harberger triangle dinámico).

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 10. Vernon Press.
- Ramsey, F.P. (1928), "A Mathematical Theory of Saving", *The Economic Journal* 38(152), 543-559.
- Cass, D. (1965), "Optimum Growth in an Aggregative Model of Capital Accumulation", *Review of Economic Studies* 32(3), 233-240.
- Apéndice P (DYNARE, `referencia/`).
- `oraculo.md` (esta misma carpeta).
