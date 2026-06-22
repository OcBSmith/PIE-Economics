# GUION-P3: La decisión óptima de consumo-ahorro

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P3-v1.0
- **Capítulo del libro:** Cap. 4 — *Consumption-saving optimal decision* (Bongers, Gómez y Torres, 2019). Decisión intertemporal de consumo y ahorro del hogar representativo.

## Objetivos didácticos

1. **Resolver** el problema de optimización intertemporal del consumidor mediante dos enfoques equivalentes (condiciones de primer orden con `fsolve` y optimización convexa directa con `cvxpy`).
2. **Interpretar** la Ecuación de Euler y cómo la relación $\beta(1+R)$ determina la pendiente del perfil de consumo a lo largo del ciclo vital.
3. **Evaluar** cómo distintos perfiles de ingresos (constante, creciente, jubilación) y cambios en la impaciencia ($\beta$) o la tasa de interés ($R$) alteran el patrón óptimo de ahorro y endeudamiento.

## Conocimientos previos requeridos

- **Matemáticas**: optimización con restricciones, condiciones de primer orden, sistemas de ecuaciones no lineales.
- **Economía**: teoría del consumidor intertemporal (Fisher), tasa marginal de sustitución intertemporal, restricción presupuestaria intertemporal, concepto de utilidad marginal decreciente.
- **Programación**: ninguno previo. El notebook explica tanto `fsolve` como `cvxpy`.
- **Práctica previa recomendada**: ninguna obligatoria (P3 es autocontenida en la parte de microfundamentos del consumidor).

## Tiempo estimado y nivel

~90-120 minutos. Grado en Economía, asignatura de Macroeconomía (fundamentos micro del consumo) o Microeconomía Avanzada.

## "Reactivos" digitales

- **Python**: `numpy`, `scipy`, `matplotlib`, `cvxpy`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/consumption_savings.py`).
- **Julia**: `Plots.jl`, `NLsolve.jl`, `Optim.jl`, `Interact.jl` + paquete `MacroAIComp` (`src/models/ConsumptionSavings.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + `referencia/`, Apéndice G MATLAB y Apéndice H Newton).

## Procedimiento paso a paso

1. **Teoría**: problema de maximización de utilidad intertemporal con utilidad logarítmica, restricciones presupuestarias secuenciales y condición terminal $B_T = 0$.
2. **Calibración base**: $\beta=0.97, R=0.02, T=30$, perfil de ingresos constante $W_t=10$.
3. **Resolución vía FOC con fsolve**: plantear el sistema de $2T-1$ ecuaciones (Euler + restricciones presupuestarias) y resolver con `scipy.optimize.fsolve`.
4. **Resolución vía optimización directa con cvxpy**: plantear el problema como programa convexo (maximizar utilidad sujeta a restricciones lineales) y resolver con `cvxpy` + `Clarabel`.
5. **Verificación frente al oráculo**: comparar que ambos solvers coinciden numéricamente y que $B_T = 0$.
6. **Perfil de ingresos creciente**: observar endeudamiento juvenil (activos negativos al inicio) y convergencia a $B_T=0$.
7. **Perfil de jubilación**: observar acumulación de activos durante la vida laboral (pico en $t=19$) y desacumulación durante la jubilación.
8. **Sensibilidad a la impaciencia**: subir $\beta$ a $0.99$ para que $\beta(1+R)>1$ y observar cómo la pendiente del consumo se vuelve positiva.
9. **Widgets interactivos**: modificar $\beta$ y $R$ en vivo y observar cambios en los perfiles de consumo, ahorro y utilidad.
10. **Conclusión**: la Ecuación de Euler como determinante de la pendiente del consumo, el papel del ahorro como "suavizador" del consumo frente a ingresos irregulares, y la equivalencia entre optimización y sistema de FOCs.

## Reacciones esperadas

Ver `oraculo.md`. Consumo constante con ingresos constantes y $\beta(1+R)<1$ (pendiente negativa suave). Endeudamiento inicial con ingresos crecientes ($B_0 < 0$). Pico de activos en $t=19$ con perfil de jubilación. Con $\beta=0.99$, la pendiente de consumo se invierte (creciente). Ambos solvers (fsolve y cvxpy) deben coincidir con tolerancia $<10^{-4}$.

## Posibles accidentes de laboratorio

- **`fsolve` no converge**: si cambias los parámetros a valores extremos ($\beta$ muy cercano a 1, $R$ muy alto), el sistema de $2T-1$ ecuaciones puede volverse numéricamente difícil. El resolvedor `cvxpy` es más robusto — si `fsolve` falla, compara con `cvxpy` para diagnosticar si es un problema numérico o de especificación.
- **Condición terminal $B_T \neq 0$**: el código MATLAB original del Apéndice G contiene una errata en la ecuación residual terminal que forzaba erróneamente $B_T = W_T$ en lugar de $B_T = 0$. Si modificas el código y obtienes activos terminales no nulos, revisa la ecuación del último periodo.
- **Confundir ahorro con activos**: los activos financieros $B_t$ pueden ser negativos (deuda), lo que NO significa que el consumidor no esté optimizando — simplemente está tomando prestado contra ingresos futuros. El ahorro flujo es $B_t - B_{t-1}$.
- **Indexado temporal**: el modelo usa $t=0,1,\dots,T-1$ (Python) o $t=1,\dots,T$ (Julia). El "último periodo" es $T-1$ en Python y $T$ en Julia. Si verificas $B_T=0$ en el índice equivocado, parecerá un error que no existe.

## Cuestionario de bitácora

1. ¿Por qué el consumidor se endeuda al inicio de su vida cuando los ingresos son crecientes? ¿Es óptimo ese comportamiento? ¿Qué restricción de mercado impediría ese endeudamiento?
2. ¿Qué signo tiene la pendiente del consumo cuando $\beta(1+R)=1$ exactamente? ¿Qué implicación tiene para la política monetaria (cambios en $R$)?
3. En el perfil de jubilación, ¿por qué los activos NO caen a cero justo en $t=19$ (último periodo trabajado) sino que quedan para $t \ge 20$?
4. Compara los perfiles de consumo con $\beta=0.97$ y $\beta=0.99$. ¿Cuál da mayor utilidad total? ¿Por qué entonces no todo el mundo tiene $\beta=0.99$?
5. ¿Qué ocurriría con el perfil de consumo si $R$ dependiera del nivel de activos (ej. tipos más altos para deudores)? ¿Seguiría siendo el problema convexo?
6. Si añadieras herencia (utilidad del legado $B_T$), ¿cómo cambiaría la condición terminal?

## Variantes / extensiones para ABP

1. **Elección de jubilación endógena**: permitir que el consumidor elija $t^*$ (edad de jubilación) además del perfil de consumo. Plantear como problema de optimización con variable discreta.
2. **Shock de renta transitorio vs permanente**: comparar la respuesta del consumo ante un shock que afecta a UN solo periodo vs uno que afecta a TODOS los periodos, verificando la teoría de la renta permanente.
3. **Restricción de liquidez**: añadir la restricción $B_t \ge 0$ (no se permite endeudamiento) y comparar el perfil de consumo resultante con el caso irrestricto.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 4. Vernon Press.
- Apéndice G (MATLAB, `referencia/`) y Apéndice H (Newton, `referencia/`).
- `oraculo.md` (esta misma carpeta).
