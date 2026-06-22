# GUION-P2: Overshooting del tipo de cambio (Dornbusch)

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora).

- **ID de práctica:** LAB-P2-v1.0
- **Capítulo del libro:** Cap. 3 — *Exchange rate overshooting* (Bongers, Gómez y Torres, 2019). Modelo de overshooting del tipo de cambio de Dornbusch.

## Objetivos didácticos

1. **Simular** el fenómeno del overshooting cambiario: por qué el tipo de cambio reacciona más que proporcionalmente a un shock monetario cuando los precios de los bienes son rígidos a corto plazo.
2. **Identificar** la estructura de punto de silla en el espacio de estados $(p, s)$ y el papel de la variable forward-looking ($s$, tipo de cambio) frente a la predeterminada ($p$, nivel de precios).
3. **Comparar** la dinámica de ajuste del mercado de bienes (lento, vía precios) y del mercado de activos (instantáneo, vía tipo de cambio) ante un shock monetario permanente.

## Conocimientos previos requeridos

- **Matemáticas**: sistemas de ecuaciones en diferencias, autovalores y punto de silla, diagramas de fases en tiempo discreto.
- **Economía**: paridad descubierta de intereses (UIP), modelo IS-LM estático, neutralidad monetaria a largo plazo, relación entre tipo de interés y tipo de cambio.
- **Programación**: ninguno previo.
- **Práctica previa recomendada**: P0 (punto de silla en sistemas dinámicos) y P1 (IS-LM dinámico).

## Tiempo estimado y nivel

~90-120 minutos. Grado en Economía, asignatura de Macroeconomía Internacional o Macroeconomía Intermedia.

## "Reactivos" digitales

- **Python**: `numpy`, `scipy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp` (`src/macroaicomp/models/dornbusch.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `Interact.jl` + paquete `MacroAIComp` (`src/models/Dornbusch.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del libro + `referencia/m2d.mod`, Apéndice F DYNARE).

## Procedimiento paso a paso

1. **Teoría**: ecuaciones del modelo (IS, LM, UIP, Phillips), reducción a sistema de 2 ecuaciones en diferencias en $(p, s)$, condición de punto de silla.
2. **Calibración base**: fijar los parámetros del libro ($\beta_0, \beta_1, \theta, \psi, \mu, \nu, m_0, ypot_0, i^*, y^*$).
3. **Estado estacionario**: $p^*=1.5$, $s^*=76.515$, $i^*=3.0$ — interpretar el tipo de cambio real de largo plazo.
4. **Verificación frente al oráculo**: comparar contra los valores del Apéndice F (DYNARE).
5. **Estabilidad**: calcular autovalores $(-0.7415, 0.5395)$, clasificar como punto de silla, identificar cuál raíz es la forward-looking.
6. **Simulación manual**: implementar la recursión periodo a periodo con el salto del tipo de cambio en $t=1$ usando la senda estable.
7. **Shock monetario**: $m_0$ de 100 a 101 en $t=1$, observar el overshooting ($s$ de 76.5 a 80.2, luego converge a 77.5) con precios pegajosos ($p$ no se mueve en $t=1$, converge a 2.5).
8. **Diagrama de fases**: visualizar el punto de silla en $(p, s)$ con los loci $\Delta p=0$ y $\Delta s=0$, la senda estable, y el salto del tipo de cambio.
9. **Widget interactivo**: modificar la magnitud del shock monetario y fiscal para explorar distintas intensidades de overshooting.
10. **Conclusión**: por qué la rigidez de precios genera overshooting, qué pasaría si los precios fueran perfectamente flexibles, y cómo la UIP ancla la senda de convergencia.

## Reacciones esperadas

Ver `oraculo.md`. Shock monetario: $s$ salta de 76.515 a ~80.215 en $t=1$ (overshooting), luego converge a 77.515; $p$ se mantiene en 1.5 en $t=1$ y converge a 2.5; $i$ cae de 3.0% a 1.0% en impacto y vuelve al 3.0% en el largo plazo. La trayectoria de $s$ debe mostrar un pico pronunciado seguido de convergencia gradual (forma de "joroba invertida").

## Posibles accidentes de laboratorio

- **Confundir $\beta_1$ con $\beta_2$ en la ecuación de $s^*$**: el libro original contiene una errata tipográfica en esa ecuación (usa $\beta_2$ donde debería usar $\beta_1$). El código del proyecto ya está corregido, pero si comparas con el texto impreso verás una discrepancia — confía en el código y en el oráculo.
- **Interpretar el salto de $s$ como una ineficiencia**: el overshooting no es un "fallo de mercado", es la respuesta óptima del mercado de divisas ante la rigidez de precios. Si los precios fueran flexibles, $s$ saltaría directamente al nuevo SS sin overshooting.
- **Signo del autovalor inestable**: en diferencias, un autovalor > 0 en el módulo $\lambda+1$ indica inestabilidad. $\lambda_2 = 0.5395 \Rightarrow |1+0.5395| = 1.5395 > 1$ — la raíz es inestable. Si calculas $|\lambda|$ en vez de $|\lambda+1|$, obtendrás una conclusión equivocada.
- **Shock con timing incorrecto en Julia**: el salto ocurre en el periodo del shock (`shock_period=1`). En Julia (indexado 1-based), esto es índice 2 del array devuelto (el índice 1 es t=0, pre-shock). Si inspeccionas `s[1]` esperando el salto, verás el valor pre-shock.

## Cuestionario de bitácora

1. ¿Por qué $s$ "salta" instantáneamente en $t=1$ mientras $p$ no puede hacerlo? ¿Qué supuesto microeconómico justifica esta asimetría?
2. Si la velocidad de ajuste de precios $\mu$ fuera mayor (precios más flexibles), ¿el overshooting sería mayor o menor? Compruébalo modificando el parámetro.
3. ¿Qué ocurre con el overshooting si la elasticidad de la demanda de dinero al tipo de interés $\theta$ es muy pequeña (trampa de liquidez)? ¿Desaparece o se amplifica?
4. Compara el overshooting de $s$ con el salto de $x_1$ en el Caso 2 de P0 — ¿en qué se parecen y en qué se diferencian?
5. ¿Qué le ocurriría a $s$ en el largo plazo si el shock monetario fuera acompañado de un aumento permanente del tipo de interés internacional $i^*$?
6. Explica intuitivamente por qué $i$ cae por debajo de $i^*$ en el impacto — ¿no viola eso la UIP?

## Variantes / extensiones para ABP

1. **Shock fiscal**: simular un aumento del gasto público ($\beta_0$) y analizar si produce overshooting o undershooting, y por qué.
2. **Ajuste gradual de expectativas**: modificar la UIP para que las expectativas cambiarias sean adaptativas en vez de racionales (ej. $\Delta s^e = \lambda(s^* - s)$) y comparar la dinámica.
3. **Calibración con datos reales**: calibrar $\mu$ y $\nu$ con datos trimestrales de inflación y brecha de producción de una economía real (ej. España 1999-2019) y simular un shock de política monetaria.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to Computational Macroeconomics*, Cap. 3. Vernon Press.
- Dornbusch, R. (1976), "Expectations and Exchange Rate Dynamics", *Journal of Political Economy* 84(6), 1161-1176.
- Apéndice F (DYNARE, `referencia/m2d.mod`).
- `oraculo.md` (esta misma carpeta).
