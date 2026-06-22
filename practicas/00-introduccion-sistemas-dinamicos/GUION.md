# GUION-P0: Introducción a los sistemas dinámicos computacionales

> Acompaña a `python.ipynb` y `julia.ipynb` de esta misma carpeta. No repite
> su código: lo enmarca (objetivos, prerrequisitos, errores típicos,
> preguntas de bitácora). Primer piloto de la plantilla
> `practicas/_plantilla/GUION.md` (Hito 2 del plan maestro).

- **ID de práctica:** LAB-P0-v1.0
- **Capítulo del libro:** Cap. 1 — *An introduction to computational dynamic
  systems* (Bongers, Gómez y Torres, 2019). Modelo de carrera de armamentos
  de Richardson.

## Objetivos didácticos

1. **Calcular** el estado estacionario y los autovalores de un sistema
   dinámico lineal de dos ecuaciones.
2. **Clasificar** un sistema como globalmente estable o de punto de silla a
   partir del criterio de módulo de los autovalores ($|\lambda+1|<1$).
3. **Interpretar** económicamente cómo un shock sobre una variable exógena o
   un cambio de parámetro desplaza la trayectoria de transición y el nuevo
   estado estacionario.

## Conocimientos previos requeridos

- **Matemáticas**: matrices 2x2 y autovalores (álgebra lineal básica),
  ecuaciones en diferencias de primer orden.
- **Economía**: ninguno — P0 es la primera práctica del curso y no asume
  modelos macroeconómicos previos.
- **Programación**: ninguno previo. El propio notebook explica la sintaxis
  de Python/Julia que usa (imports, funciones, indexado...) a medida que
  aparece — no falta hacer ningún tutorial externo antes.

## Tiempo estimado y nivel

~60-90 minutos. Grado en Economía / Administración y Dirección de Empresas,
asignatura de Macroeconomía o Métodos Cuantitativos (primer tema, sistemas
dinámicos).

## "Reactivos" digitales

- **Python**: `numpy`, `matplotlib`, `ipywidgets` + paquete `macroaicomp`
  (`src/macroaicomp/models/arms_race.py`, `src/macroaicomp/plotting/phase_diagram.py`).
- **Julia**: `Plots.jl`, `LinearAlgebra`, `BenchmarkTools.jl` + paquete
  `MacroAIComp` (`src/models/ArmsRace.jl`).
- **Oráculo numérico**: `oraculo.md` de esta misma carpeta (valores del
  libro + `referencia/m1.m`, Apéndice B MATLAB, y `referencia/m1d.mod`,
  Apéndice C DYNARE).

## Procedimiento paso a paso

Mismo orden en `python.ipynb` y `julia.ipynb`:

1. **Teoría**: ecuaciones del sistema (1.7-1.11), fórmula del estado
   estacionario (1.14) y criterio de estabilidad (Apéndice A).
2. **Calibración Caso 1**: fijar los 6 parámetros y las exógenas $z_1, z_2$
   de la Tabla 1.1/1.2 (estabilidad global).
3. **Resolución**: calcular estado estacionario y autovalores con esa
   calibración.
4. **Verificación frente al oráculo**: comparar el resultado contra
   `oraculo.md`/MATLAB con una tolerancia numérica.
5. **Shock**: subir $z_1$ de 1 a 2 y simular la transición al nuevo SS.
6. **Diagrama de fases**: visualizar el campo vectorial y la convergencia
   hacia el SS.
7. **Sensibilidad**: subir $\alpha$ de 0.50 a 0.70 y repetir el cálculo del
   paso 3.
8. **Punto de silla (Caso 2)**: nueva calibración (Tabla 1.3) donde un
   autovalor es estable y otro inestable; simular el salto instantáneo de
   la variable forward-looking.
9. **Interactivo**: explorar varias magnitudes de shock sobre $z_1$ (slider
   en Python, 4 escenarios fijos en Julia).
10. **Buenas prácticas**: por qué la lógica del modelo vive en `src/` y no
    en el notebook.
11. **Conclusión**: síntesis de los dos comportamientos cualitativos
    (estabilidad global vs. punto de silla).

## Reacciones esperadas

Ver la tabla completa en `oraculo.md` (y repetida dentro de ambos
notebooks, en las secciones 4 y 8): Caso 1 con SS inicial $(4,4)$,
autovalores $(-0.25,-0.75)$, SS tras shock $(6.67,5.33)$, SS tras
sensibilidad $(2.61,3.30)$; Caso 2 con SS inicial $(4,4)$, autovalores
$(-0.75,0.25)$, salto de $x_1$ a $2.00$ y SS final $(3.33,2.67)$.

## Posibles accidentes de laboratorio

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

## Cuestionario de bitácora

1. ¿Por qué el criterio de estabilidad es $|\lambda+1|<1$ y no simplemente
   "autovalor negativo"? ¿Qué pasaría con un autovalor positivo pero de
   módulo $|\lambda+1|<1$?
2. En la Sección 7, subir $\alpha$ reduce el estado estacionario de AMBOS
   países, no solo del país 1. ¿Por qué, si $\alpha$ solo aparece en la
   ecuación de $\Delta x_1$?
3. En el Caso 2 (punto de silla), ¿por qué $x_1$ "salta" instantáneamente
   ante el shock mientras $x_2$ no? ¿Qué supuesto económico justifica tratar
   a $x_1$ como variable forward-looking?
4. Si el shock del paso 5 se aplicara sobre $z_2$ en vez de $z_1$, ¿qué
   esperarías que cambiara en los resultados? Compruébalo modificando la
   celda.
5. ¿Qué interpretación económica tiene la calibración $\beta=\gamma=0$
   (ambos países deja de reaccionar al armamento del otro)? ¿Sigue habiendo
   "carrera" armamentística en ese caso?

## Variantes / extensiones para ABP

1. **Generalizar a 3 países**: extender el sistema a una matriz $3\times3$ y
   adaptar el criterio de estabilidad (autovalores de una matriz $3\times3$).
2. **Velocidad de convergencia**: calcular y comparar la vida media de
   convergencia ($\ln(2)/|\ln(1+\lambda)|$) entre el Caso 1 base y el Caso 1
   con la sensibilidad de la Sección 7 — ¿cuál converge más rápido?
3. **Escenario de "tregua"**: simular una reducción simultánea de $z_1$ y
   $z_2$ (en vez de un aumento) y comparar la velocidad de ajuste con el
   shock expansivo de la Sección 5.

## Referencias

- Bongers, A., Gómez, T. y Torres, J.L. (2019), *An Introduction to
  Computational Macroeconomics*, Cap. 1. Vernon Press.
- Apéndice B (MATLAB, `referencia/m1.m`) y Apéndice C (DYNARE,
  `referencia/m1d.mod`).
- `oraculo.md` (esta misma carpeta).
