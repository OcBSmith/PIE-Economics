# GUION-P6: La empresa y la decisión de inversión (Q de Tobin)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P6-v1.0
- **Capítulo del libro:** Cap. 7 — *Firm/investment, Tobin's Q* (Bongers, Gómez y Torres, 2019). Modelo de inversión con costes de ajuste y Q de Tobin.

## Objetivos didácticos

1. **Calcular** el estado estacionario y la dinámica de transición de la inversión, el capital y la Q de Tobin ante un shock de tipo de interés.
2. **Interpretar** la Q de Tobin como el valor marginal del capital instalado: por qué $q>1$ desencadena inversión positiva y $q<1$ desinversión.
3. **Comparar** la aproximación linealizada (Blanchard-Khan) con la solución no lineal exacta, evaluando el error de aproximación para shocks de distinta magnitud.

## Conocimientos previos requeridos

- **Matemáticas**: log-linealización alrededor del estado estacionario, descomposición de autovalores para punto de silla, sistemas de ecuaciones no lineales.
- **Economía**: teoría neoclásica de la inversión, costes de ajuste convexos, Q de Tobin, decisión de inversión forward-looking.
- **Programación**: ninguno previo.
- **Práctica previa recomendada**: P0 (sistemas dinámicos y punto de silla), P1 (IS-LM), P7 (DGE básico — P6 es más simple que P7 pero comparte la técnica de Blanchard-Khan).

## Tiempo estimado y nivel

~90-120 minutos. Grado en Economía, asignatura de Macroeconomía Intermedia o Avanzada.

## "Reactivos" digitales

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/tobin_q.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `NLsolve.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/TobinQ.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + Apéndice K DYNARE).

## Procedimiento paso a paso

1. **Teoría**: función de producción Cobb-Douglas, costes de ajuste cuadráticos de la inversión, derivación de la Q de Tobin, sistema dinámico en $(K, q)$.
2. **Calibración base**: $\alpha=0.35, \beta=0.97, \delta=0.06, R=0.04, \phi=10$.
3. **Estado estacionario**: $q^*=1.0$, $K^* \approx 6.87$ (interpretar: el capital de largo plazo iguala el coste de uso).
4. **Verificación frente al oráculo**: comparar SS y autovalores con el Apéndice K (DYNARE).
5. **Linealización**: derivar el sistema log-linealizado alrededor del SS, calcular autovalores $(-0.0607, 0.1072)$, confirmar punto de silla.
6. **Fórmula de salto**: demostrar la identidad entre la fórmula simplificada $\hat{q}_1 = \theta \lambda_1 \hat{k}_1$ y la fórmula del libro.
7. **Shock de tipo de interés**: $R$ baja del 4% al 3% permanentemente en $t=1$, observar salto de $q$ por encima de 1 (inversión positiva) y acumulación gradual de $K$.
8. **Diagrama de fases**: campo vectorial con `streamplot`, loci $\Delta \hat{k}=0$ y $\Delta \hat{q}=0$, senda estable, salto instantáneo de $q$ y ajuste posterior.
9. **Comparación lineal vs no lineal**: resolver con ambos métodos y mostrar que coinciden para el shock pequeño (1 pp), pero divergen para shocks mayores.
10. **Widgets interactivos**: modificar $R$, $\phi$, $\delta$, $\alpha$ y explorar la sensibilidad de la dinámica de inversión.

## Reacciones esperadas

Ver `oraculo.md`. $q^*=1.0$, $K^* \approx 6.87$, $\lambda_1 = -0.0607$, $\lambda_2 = 0.1072$. Shock $R: 4\% \to 3\%$: $q$ salta a ~1.103 (inversión neta positiva), $K$ converge de ~6.87 a un nuevo SS mayor, $I$ muestra un pico inicial y luego decrece hacia el nuevo nivel de depreciación. $q$ converge de vuelta a 1.0 (el largo plazo ancla $q$ a 1).

## Posibles accidentes de laboratorio

- **`compute_linearized_system` con 2 argumentos**: la función en `TobinQ.jl` solo acepta 1 argumento (`params`). Si la celda la llama con 2 argumentos (`params, R_final`), lanzará `MethodError`. Usa `compute_linearized_system(params)` y modifica `params.R` antes de llamar.
- **Signo de los costes de ajuste en la Euler no lineal**: el resolvedor no lineal usa la condición de optimalidad con costes de ajuste. Si el signo del término cuadrático está mal, la trayectoria de $q$ divergirá en lugar de converger.
- **Confundir log-desviaciones con niveles**: los autovalores $(-0.0607, 0.1072)$ SON log-desviaciones, no niveles. Para pasarlos a niveles discretos: $1+\lambda$. Solo entonces se aplica el criterio $|1+\lambda| \lessgtr 1$ para estabilidad.
- **El diagrama de fases no muestra el saddle path correcto**: el locus $\Delta \hat{q}=0$ debe tener pendiente (no ser vertical). Si es vertical, la matriz de transición log-linealizada no se ha calculado correctamente.

## Cuestionario de bitácora

1. ¿Por qué $q$ tiene que ser exactamente 1 en el estado estacionario, independientemente de los valores de $\alpha, \beta, \delta, \phi$? ¿Qué condición de optimalidad lo impone?
2. Si $\phi$ (costes de ajuste) fuera muy bajo, ¿cómo cambiaría cualitativamente el salto de $q$ y la velocidad de ajuste de $K$? Compruébalo con el widget.
3. ¿Por qué la inversión bruta $I_t$ puede ser negativa en el modelo? ¿Qué significaría $I_t < 0$ económicamente y por qué eso no es realista?
4. Compara el salto de $q$ en este modelo con el salto de $x_1$ en el Caso 2 de P0. ¿Son conceptualmente equivalentes? ¿Qué variable es la forward-looking en cada caso?
5. ¿Por qué el error entre la solución lineal y la no lineal crece con la magnitud del shock? ¿Qué términos desprecia la log-linealización?
6. ¿Qué le ocurriría a la inversión si $R$ subiera en lugar de bajar? ¿Puede $q$ ser menor que 1? ¿Qué significa $q<1$ para la inversión?

## Variantes / extensiones para ABP

1. **Shock de productividad**: introducir un shock de PTF ($A_t$) y comparar la dinámica de $q$ y $I$ con el shock de tipo de interés.
2. **Costes de ajuste asimétricos**: modificar la función de costes para que desinvertir sea más costoso que invertir y analizar el efecto sobre la velocidad de ajuste.
3. **Modelo con restricción de irreversibilidad**: añadir la restricción $I_t \ge 0$ (no se puede desinvertir) y comparar con el modelo base.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 7. Vernon Press.
- Tobin, J. (1969), "A General Equilibrium Approach to Monetary Theory", *Journal of Money, Credit and Banking* 1(1), 15-29.
- Apéndice K (DYNARE, `referencia/`).
- `oraculo.md` (esta misma carpeta).
