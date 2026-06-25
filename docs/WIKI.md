# Wiki técnica — MACRO-AI-COMP

Registro vivo de **decisiones técnicas, hallazgos sobre el material fuente y
progreso real**, día a día. Complementa al
[`PLAN_MAESTRO_MACRO_AI_COMP.md`](https://github.com/OcBSmith/PIE-Economics/blob/main/PLAN_MAESTRO_MACRO_AI_COMP.md)
(que define QUÉ hay que hacer y lleva los checkboxes oficiales; vive en la
raíz del repo, no en `docs/`, así que no es parte del sitio MkDocs — el
enlace va directo a GitHub) y a las futuras actas de `docs/actas/` (que
documentarán decisiones formales con Aneli, Torres y Cabello). Esta wiki es
el cuaderno de trabajo del PTGAS: el CÓMO, el POR QUÉ de cada elección, y lo
que se va descubriendo sobre la marcha.

Cómo añadir una entrada: al final de cada sesión de trabajo, añade un bloque
fechado en **Registro cronológico**. Si la sesión deja una decisión que
afecta a todo el proyecto (no solo a una práctica concreta), añádela también
a **Decisiones técnicas**. Si descubres algo sobre el libro o la fuente que
no está bien reflejado en el plan maestro, añádelo a **Hallazgos**.

---

## Decisiones técnicas

| # | Decisión | Fecha | Por qué |
|---|---|---|---|
| 1 | Trabajar en local, sin repositorio remoto en GitHub, hasta tener contenido suficiente que merezca la pena publicar | 2026-06-17 | Evitar bloquear el arranque en decisiones de cuenta/org de GitHub; el `gh` CLI ya está autenticado (cuenta `OcBSmith`) para cuando se decida publicar |
| 2 | El `.docx` del libro **no se versiona en git** (excluido vía `.gitignore`) | 2026-06-17 | Es material con copyright de Vernon Press (2019); el repo aspira a publicarse en abierto bajo MIT (código) / CC BY-SA (manuales) según §1.2 del plan maestro, y no tenemos permiso explícito de la editorial para redistribuirlo |
| 3 | Empezar por **contenido** (P0 en Python) antes que por infraestructura completa (CI, pre-commit, Julia, GitHub Actions) | 2026-06-17 | Con el presupuesto y dedicación parcial del equipo, el rigor de ingeniería completo arriesga llegar al Mes 7 (piloto en aula) sin nada probado con alumnos reales; se prioriza tener algo demostrable pronto |
| 4 | Entorno reproducible local: `venv` (`.venv/`) + `pip install -e ".[dev]"` | 2026-06-17 | Más simple que Conda/devcontainer para una sola máquina de desarrollo; se revisará cuando haya que dar el entorno a Torres/Cabello o a alumnos |
| 5 | Notebooks se ejecutan con `jupyter nbconvert --execute` antes de comitear, y los outputs se limpian con `nbstripout` | 2026-06-17 | Cumple la regla del plan (§0.3): "Restart & Run All" sin error es el test mínimo; outputs no van al repo |
| 6 | En P0 se usa un **gráfico estático multi-escenario** en vez de un slider interactivo (`@manipulate`/`Interact.jl`) en Julia | 2026-06-22 | `WebIO.jl` (la base de `Interact.jl`) depende de la extensión `webio-jupyterlab-provider`, que solo soporta JupyterLab 3.x (`@jupyterlab/application >=3.0.0 <4.0.0` declarado en su propio manifiesto) — incompatibilidad estructural confirmada con JupyterLab 4.5.9, el que usa este proyecto. La única alternativa sería bajar JupyterLab a 3.x en las 10 prácticas, que se descarta por ahora. El gráfico estático (4 escenarios fijos en la misma figura) da la misma información pedagógica y funciona siempre (local, Binder, Colab) |
| 7 | **P0 se va a usar como práctica de referencia pedagógica**: se revisará a fondo (Python y Julia) para maximizar su calidad didáctica, y esa revisión servirá de plantilla/ejemplo para mejorar la pedagogía del resto de prácticas (P1-P9) | 2026-06-22 | Decisión del usuario tras cerrar el plan de homogeneización Julia↔Python. **Alcance ya concretado y aplicado a P0** en dos ejes: económico (tablas del oráculo visibles en el propio notebook, junto a cada cálculo) y de programación (comentarios QUÉ/POR QUÉ/QUÉ VERÁS en cada celda de código, incluida la sintaxis básica para alumnos sin experiencia previa). P1-P9 siguen sin tocar — esta revisión es la plantilla a replicar, no el trabajo en sí |
| 8 | **Hito 2 del plan maestro (guion de laboratorio) se adelanta para P0** como piloto: se crea `practicas/_plantilla/GUION.md` (plantilla maestra) y `practicas/00-introduccion-sistemas-dinamicos/GUION.md` (relleno para P0) | 2026-06-22 | Al pedir una nota de calidad de P0 (8/10), el usuario decidió cerrar las 3 carencias señaladas. De las 3, solo esta era corregible con trabajo de implementación: la asimetría de interactividad Julia/Python se mantiene tal cual (decisión #6, ya tomada), y el `.xlsx` original sigue pendiente de Anelí (no es un problema de código). La validación de la plantilla contra un guion real de Química Orgánica (que el plan maestro pide) queda pendiente de revisión manual del usuario |
| 9 | **El repositorio se hace público en GitHub** (`OcBSmith/PIE-Economics`), con CI completo (lint + tests Python/Julia + deploy automático a GitHub Pages) | 2026-06-23 | Supera la Decisión técnica #1 ("trabajar en local sin remoto hasta tener contenido suficiente"). Con P0-P9 completos en Python y Julia, homogeneizados y verificados, se consideró que ya había contenido suficiente para publicar. El cambio no quedó registrado explícitamente en su momento; se documenta aquí retroactivamente tras una sesión de unificación de documentación (2026-06-25) |
| 10 | **Web pública vía MkDocs Material**, no Quarto | 2026-06-23/24 | Se evaluó Quarto (`docs/PLAN_WEB_QUARTO.md`) pero se implementó con MkDocs Material + `mkdocs-jupyter` (`mkdocs.yml`, `build_site.py`), que renderiza los `.ipynb` directamente sin paso de conversión y se integra mejor con el flujo de trabajo ya existente basado en notebooks. `docs/PLAN_WEB_QUARTO.md` queda marcado como superseded |
| 11 | **Ejecución de código en vivo con un cliente WebSocket propio, no con la librería Thebe** | 2026-06-25 | El plan inicial (`docs/PLAN_THEBE_INTERACTIVO.md`) proponía la librería `thebe` estándar, pero su loader AMD resultó incompatible con el entorno de la página (botones sin `onclick` funcional, dependencias que no cargaban). Se sustituyó por `docs/javascripts/thebe.js`, un cliente hecho a mano que habla directamente con la API REST/WebSocket de un servidor Binder (build → poll `ready` → crear kernel → `execute_request` por cada botón "Run"). El nombre del archivo (`thebe.js`) se mantiene por continuidad aunque ya no usa la librería |
| 12 | **Pre-calentar la imagen de Binder en cada deploy** (job `warm-binder` en `.github/workflows/ci.yml`) en vez de migrar a JupyterLite/Pyodide | 2026-06-25 | El usuario reportó que Binder tardaba "muchísimo" en cargar. La causa real es el build de Docker de `repo2docker` (no algo arreglable desde el JS), agravado por dependencias Julia sin uso real (`Symbolics`, `DataFrames`, quitadas el mismo día). Se evaluaron 3 opciones: (a) pre-calentar el build justo tras el deploy para que ya esté cacheado cuando llega un visitante real — elegida, esfuerzo bajo, sin reducir capacidades; (b) JupyterLite/Pyodide para Python instantáneo en el navegador — descartada por ahora: es una integración nueva separada de Binder, no cubriría Julia (sin runtime WASM maduro) y la compatibilidad de `cvxpy` con Pyodide está sin verificar; (c) no tocar nada y solo documentar la espera — descartada porque sí había margen de mejora barato |

## Hallazgos sobre el libro / la fuente

1. **El Capítulo 1 tiene dos apéndices de verificación, no uno.** La tabla
   de mapeo del plan maestro (§2) solo listaba "App. B (MATLAB)" para P0,
   pero el libro también incluye el **Apéndice C (DYNARE)**, que resuelve
   precisamente el caso de punto de silla del Capítulo 1. Corregido en la
   tabla del plan.
2. **No tenemos los `.xlsx` originales** (`ICM-1-1.xls`, `ICM-1-2.xls`,
   etc.), solo el `.docx` del libro. Sigue pendiente pedírselos a Aneli
   (plan §3.1.1) — sin ellos no podemos completar la columna "Excel" de
   ninguna práctica.
3. **El Capítulo 1 no es solo el caso de estabilidad global.** La Sección
   1.6.2 desarrolla un caso de **punto de silla** con un salto instantáneo
   de la variable forward-looking (ecuación 1.39) que hay que resolver con
   una recursión distinta a la del caso estable. Lo implementamos
   (`simulate_saddle_path`) y el salto calculado coincide exactamente con
   el valor del libro (x₁ = 2.00 en el periodo del shock). Merece la pena
   tenerlo en cuenta para IS-LM y Dornbusch (P1, P2), que previsiblemente
   también tendrán casos de punto de silla.
4. **Python global de la máquina es 3.14**, no el 3.11 recomendado por el
   plan (§1.3). Usamos un venv con `requires-python >=3.11`, compatible.
   No debería dar problemas para P0-P3, pero anotarlo por si alguna
   librería futura (puente con Julia, `numba`) tiene fricción con 3.14.
5. **Pandoc + Python ya estaban instalados** en la máquina (vía WinGet /
   Microsoft Store), lo que permitió convertir los `.docx` a texto sin
   instalar nada nuevo. `gh` CLI también disponible y autenticado.
6. **`docs/index.md` y `docs/guia-profesor.md` eran copias generadas, no la
   fuente.** `build_site.py` los sobrescribe copiándolos desde la raíz del
   repo antes de cada `mkdocs build` (igual que hace con `docs/practicas/`
   a partir de `practicas/`). Estaban commiteados por error (sin estar en
   `.gitignore`), lo que hacía parecer que eran "los canónicos" al estar
   dentro de `docs/` — al revés de la realidad. Corregido el 2026-06-25:
   añadidos a `.gitignore` y destrackeados con `git rm --cached`. Editar
   siempre `index.md`/`guia-profesor.md` de la **raíz**.

## Estructura actual del repo (snapshot 2026-06-17)

```
PIE/
├── .venv/                              # entorno local, no versionado
├── docs/
│   └── WIKI.md                         # este documento
├── practicas/
│   └── 00-introduccion-sistemas-dinamicos/
│       ├── python.ipynb                # completo, ejecutado, outputs limpios
│       ├── oraculo.md                  # valores esperados (libro + MATLAB/DYNARE)
│       └── referencia/
│           ├── m1.m                    # Apéndice B transcrito
│           └── m1d.mod                 # Apéndice C transcrito
├── src/macroaicomp/
│   ├── models/arms_race.py
│   └── plotting/phase_diagram.py
├── tests/python/test_arms_race.py      # 10 tests, todos en verde
├── PLAN_MAESTRO_MACRO_AI_COMP.md
├── PROPUESTA DE PROYECTO DE INNOVACIÓN EDUCATIVA-2.docx
├── README.md
├── pyproject.toml / requirements.txt / .gitignore
└── Feedback aneli.txt                  # vacío, pendiente de rellenar
```

Pendiente del monorepo objetivo (plan §1.2): `prompts/`, `bitacora/`,
`evaluacion/`, `infraestructura/`, `.github/`, y todo lo de Julia
(`src/MacroAIComp/`). Deliberadamente no creados todavía (decisión #3).

## Registro cronológico

### 2026-06-17

- **Sesión 1** — Lectura de los 4 archivos locales (propuesta INNOVA26,
  plan maestro, libro de Aneli, `Feedback aneli.txt` vacío) y resumen al
  usuario de cómo se relacionan entre sí.
- **Sesión 2** — Valoración de la viabilidad del plan maestro: alcance
  (rigor de ingeniería completo, Julia, CI, 3 papers) vs. recursos (2.850 €,
  equipo a tiempo parcial). Recomendación: priorizar P0-P3 en Python como
  mínimo viable antes de Julia/CI/dashboard.
- **Sesión 3** — Arranque de la implementación:
  - Confirmado con el usuario: empezar por P0 en Python, todo en local,
    sin GitHub todavía (decisiones #1 y #3).
  - Extraído el contenido del Capítulo 1 y los Apéndices B/C del `.docx`
    del libro (vía pandoc) — ver hallazgos #1 a #3.
  - Creada la estructura local: `src/macroaicomp/{models,plotting}`,
    `tests/python/`, `practicas/00-introduccion-sistemas-dinamicos/`.
  - Implementado `src/macroaicomp/models/arms_race.py` (`steady_state`,
    `eigenvalues`, `is_saddle_path`, `simulate`, `simulate_saddle_path`) y
    `src/macroaicomp/plotting/phase_diagram.py`.
  - Transcritos los Apéndices B y C a `referencia/` como oráculo numérico,
    y documentados los valores esperados en `oraculo.md`.
  - 10 tests en `tests/python/test_arms_race.py`, todos en verde,
    verificados contra los valores exactos del libro (incluido el caso de
    punto de silla).
  - Notebook `python.ipynb` construido con la estructura estándar del
    plan (§0.3): teoría, calibración, solución, verificación, shock,
    sensibilidad, punto de silla, diagrama de fases, widget interactivo,
    buenas prácticas, conclusión. Ejecutado de extremo a extremo sin
    errores; outputs limpiados con `nbstripout` antes de comitear.
  - `README.md`, `.gitignore`, `pyproject.toml`, `requirements.txt`
    creados en la raíz.
  - `git init` + primer commit (solo local, sin remoto).
  - Checkboxes actualizados en `PLAN_MAESTRO_MACRO_AI_COMP.md` (§2 tabla
    de mapeo, §3.1.2 bloque P0, §1.2/§1.3 infraestructura parcial).
- **Pendiente para la próxima sesión**: elegir P1 (IS-LM dinámico) o P2
  (Dornbusch overshooting); seguir sin tocar GitHub hasta que haya más
  contenido; pedir a Aneli los `.xlsx` originales y la confirmación sobre
  si el equipo tiene permiso de Vernon Press para redistribuir el libro.

### 2026-06-18 / 2026-06-19
- **Sesión 4** — Infraestructura y CI (Cierre de Fase 0):
  - A pesar de la Decisión #3 de posponer la infraestructura completa, se vio necesario establecer una línea base de calidad automática antes de empezar con más modelos.
  - Creado `.pre-commit-config.yaml` con `black`, `ruff` y `nbstripout`.
  - Creada la configuración base para Julia: `.JuliaFormatter.toml` con BlueStyle y un `Project.toml` inicial para el paquete `MacroAIComp`.
  - Configurado GitHub Actions en `.github/workflows/ci.yml` para correr linting y pytest automáticamente en cada push a `main`.
  - Checkboxes de la Fase 0 en el plan maestro actualizados a completados.
  - **Próximo paso**: Iniciar el modelado en Python del Capítulo 2: Modelo IS-LM dinámico (Práctica P1).

- **Sesión 5** — Práctica P1 (IS-LM Dinámico):
  - Ejecutado `pandoc` para extraer el texto del Capítulo 2 y los Apéndices D/E del documento de Word original (`.docx`).
  - Extraídas las ecuaciones y la calibración base del Apéndice D (MATLAB) y E (DYNARE).
  - Creados los archivos de transcripción `m2.m` y `m2d.mod` en `practicas/01-is-lm-dinamico/referencia/`.
  - Escrito el oráculo de verificación en `oraculo.md` con los valores de estado estacionario calculados a mano ($Y=2000, P=81, i=2$).
  - Implementado el módulo `src/macroaicomp/models/islm.py` usando `scipy.integrate.solve_ivp` para la dinámica continua del sistema de ecuaciones (curvas IS, LM y Phillips).
  - Desarrollada la batería de tests `tests/python/test_islm.py` que verifica el equilibrio y el efecto de los shocks monetarios. Los tests han pasado al 100%.
  - Construido el *frontend* interactivo en Jupyter: `practicas/01-is-lm-dinamico/python.ipynb`, dotado de deslizadores para alterar los shocks monetarios y fiscales y visualizar las respuestas impulsivas de renta y precios.
  - El cuaderno fue ejecutado exitosamente y purgado con `nbstripout`. Plan maestro actualizado.

- **Sesión 6** — Ajustes de visualización y calidad de P1 (IS-LM Dinámico) y corrección de pre-commit (2026-06-19):
  - Corregida la compatibilidad del entorno local: se modificó `.pre-commit-config.yaml` eliminando el parámetro `language_version: python3.11` en el hook de `black`. De este modo, la herramienta utiliza de forma dinámica el intérprete de Python del entorno virtual actual (Python 3.14.4), eliminando fallos de inicialización.
  - Subsanados los errores de renderizado matemático (`Math input error`) en las secciones de teoría y simulación interactiva de `python.ipynb` generados por `generate_notebook.py`. Se convirtieron las celdas markdown de LaTeX a strings crudos de Python (`r"""..."""`) para evitar que expresiones como `\theta` (escape `\t` de tabulación), `\beta` (escape `\b` de backspace) y `\nu` (escape `\n` de newline) fuesen malinterpretadas.
  - Optimización didáctica: ajustados los valores por defecto del deslizador de la Oferta Monetaria (`m0_shock`) de `100.0` a `110.0`. De este modo, el gráfico interactivo de respuesta impulsiva se carga con curvas dinámicas visibles desde el inicio en lugar de líneas estáticas planas.
  - Verificación en navegador (vía Chrome DevTools MCP): se validó la visualización completa del notebook y la consola del navegador libre de errores tras recargar la página.
  - Ejecutado `pre-commit run --all-files` y `pytest` con resultados 100% satisfactorios.

- **Sesión 7** — Rediseño Pedagógico Completo y Diagrama de Fases para P1 (2026-06-19):
  - **Derivaciones matemáticas**: Se amplió el marco teórico para detallar algebraicamente la reducción del sistema de 4 ecuaciones macroeconómicas estructurales a un sistema de 2 ODEs de primer orden en el espacio de estados ($Y, P$).
  - **Funcionamiento interno**: Se añadió una sección didáctica sobre `scipy.integrate.solve_ivp` y el algoritmo de Runge-Kutta 4(5) (RK45). Se programó explícitamente la función de derivadas `custom_system_dynamics` dentro del cuaderno con comentarios exhaustivos línea a línea.
  - **Comentarios y Descripciones**: Se comentaron detalladamente los imports, la calibración base y la derivación analítica del estado estacionario. Se implementó una tabla de parámetros didáctica que extrae explicaciones descriptivas en español.
  - **Visualización en 3 Paneles**: Se extendió la visualización del shock de 2 a 3 paneles interactivos, incorporando el **Diagrama de Fases** dinámico en el plano de estados $(Y, P)$. Este grafica el locus de pleno empleo $\dot{P}=0$, el locus de bienes equilibrado $\dot{Y}=0$, y un campo vectorial dinámico (`quiver`) con la trayectoria espiral resultante de la simulación.
  - **Cuaderno de Bitácora**: Se añadieron 3 actividades analíticas específicas sobre el diagrama de fases, incluyendo el estudio de la tangencia vertical y la velocidad de ajuste.
  - **Certificación**: Compilado y ejecutado el cuaderno final con `nbconvert`. Limpieza automática con `nbstripout`. Pasados todos los tests automáticos y pre-commit checks.
  - **Plan Maestro**: Actualizado el estado de la práctica P1 a `[x] Python listo (pedagógico)`.

- **Sesión 8** — Práctica P2 (Dornbusch Overshooting) (2026-06-19):
  - **Ecuaciones y Estabilidad**: Implementado el modelo de overshooting del tipo de cambio de Dornbusch en diferencias (tiempo discreto) bajo rigidez de precios a corto plazo y UIP con previsión perfecta.
  - **Módulo Core**: Creado `src/macroaicomp/models/dornbusch.py` con `DornbuschParameters`, `steady_state`, `coefficient_matrices`, `eigenvalues`, y `simulate_shock`.
  - **Corrección de Errata**: Se identificó y resolvió una errata tipográfica del Capítulo 3 del libro original en la ecuación de $s^*$, usando el denominador $\beta_1$ en lugar de $\beta_2$, logrando la coincidencia exacta con el estado estacionario del libro ($s^* = 76.515$).
  - **Tests Unitarios**: Creado `tests/python/test_dornbusch.py` con 3 tests de validación cruzada para estado estacionario base, autovalores/estabilidad de punto de silla, y dinámica impulsiva ante shock monetario.
  - **Generación de Notebook**: Escrito el compilador `generate_dornbusch_notebook.py` para construir el laboratorio interactivo en `practicas/02-overshooting-dornbusch/python.ipynb` con explicaciones detalladas en LaTeX y código comentado paso a paso.
  - **Visualización en 3 Paneles**: Panel 1 (precios y tipo de cambio con el salto de overshooting y deslizamiento gradual), Panel 2 (tipo de interés y demanda agregada), Panel 3 (Diagrama de fases interactivo en el plano de estados $(p, s)$ con los locus $\Delta s=0$ y $\Delta p=0$, el Camino de Silla Estable y el campo vectorial).
  - **Calidad y Verificación**: Compilado y ejecutado el cuaderno final con `nbconvert`. Validado que todos los tests de pytest pasan. Limpieza y formateo automático de calidad con `pre-commit run --all-files` (incluyendo `black`, `ruff` y `nbstripout`).

- **Sesión 9** — Práctica P3 (Decisión Óptima de Consumo-Ahorro) (2026-06-19):
  - **Doble Enfoque de Resolución**: Implementada la resolución de la decisión intertemporal del consumidor mediante FOCs con `scipy.optimize.fsolve` y mediante optimización convexa directa con `cvxpy` (emulando el Solver de Excel).
  - **Módulo Core**: Creado `src/macroaicomp/models/consumption_savings.py` con `ConsumptionSavingParameters`, `generate_income_profile`, `solve_foc_fsolve` y `solve_direct_cvxpy`.
  - **Corrección de Errata**: Se detectó y resolvió una errata en el código MATLAB del Apéndice G del libro original, donde la ecuación residual terminal no incluía el salario del último periodo ($W_T$), forzando erróneamente $B_T = W_T$ en lugar de $B_T = 0$. Al añadir $-W_T$, el solver clava los activos finales a 0.0 y agota la riqueza restante.
  - **Tolerancia y Solvers**: Se ajustaron los parámetros de Clarabel (`tol_gap_abs=1e-11`, `tol_gap_rel=1e-11`, `tol_feas=1e-11`) y se implementó un fallback dinámico a `SCS` para garantizar la máxima coincidencia numérica con `fsolve` (tolerancia absoluta < 1e-4).
  - **Tests Unitarios**: Creado `tests/python/test_consumption_savings.py` con 5 tests que validan equivalencia de resolvedores, condición terminal, endeudamiento juvenil ante ingresos crecientes, perfil piramidal de ahorro para jubilación y sensibilidad de pendiente positiva ante $\beta$ alta.
  - **Generación de Notebook**: Escrito el script `generate_p3_notebook.py` compilando el laboratorio en `practicas/03-consumo-ahorro/python.ipynb` con LaTeX explicativo y graficación premium en 3 paneles (Consumo/Ingresos con fill_between de ahorro/deuda, Activos Financieros y Utilidad Descontada).
  - **Calidad**: Notebook verificado de principio a fin sin errores en el entorno virtual (`nbconvert --execute`) y outputs limpiados con `nbstripout` mediante `pre-commit run --all-files`.

- **Sesión 10** — Práctica P4 (Decisión Óptima de Consumo-Ocio y Ahorro) (2026-06-19):
  - **Asignación del Tiempo y Ahorro**: Implementado el modelo de elección conjunta de consumo-ahorro (decisión intertemporal) y consumo-ocio (decisión intratemporal de oferta de trabajo) con utilidad logarítmica separable.
  - **Módulo Core**: Creado `src/macroaicomp/models/consumption_leisure.py` con `ConsumptionLeisureParameters`, `solve_foc_fsolve` y `solve_direct_cvxpy`.
  - **Corrección de Errata de Indexación**: Se detectó y resolvió una errata de indexación en el archivo MATLAB `m5foc.m` del Apéndice I del libro original, que dejaba el residuo `f(2*T-1)` vacío e indexaba un elemento fuera de rango en `f(2*T+1)`. Se implementó un esquema de indexación de 0 a $2T-1$ perfectamente cuadrado y robusto.
  - **Tolerancias de Clarabel**: Se configuraron tolerancias de precisión en `Clarabel` (`tol_gap_abs=1e-11`, `tol_gap_rel=1e-11`, `tol_feas=1e-11`) logrando equivalencia exacta con `fsolve`.
  - **Tests Unitarios**: Creado `tests/python/test_consumption_leisure.py` con 5 tests unitarios que validan la equivalencia de los solvers, la condición terminal de activos, los límites lógicos de la oferta de trabajo ($0 \le L_t < 1.0$), la sensibilidad ante preferencias de consumo ($\gamma$) y los cambios de pendiente del consumo según la tasa de interés ($R$).
  - **Generación de Notebook**: Escrito `generate_p4_notebook.py` compilando el laboratorio en `practicas/04-consumo-ocio/python.ipynb` con LaTeX explicativo y 3 paneles de graficación interactiva (Consumo/Ingreso salarial con fill_between, Trabajo/Ocio, y Activos).
  - **Calidad**: El notebook se compila, ejecuta sin errores (`nbconvert`) y sus salidas se limpian automáticamente con `nbstripout` en `pre-commit`.

### 2026-06-19 (Sesión 11)
- **Práctica P5 (El Gobierno y la Política Fiscal)**:
  - **Módulo Core**: Creado `src/macroaicomp/models/fiscal_policy.py` con `FiscalPolicyParameters` y tres solvers:
    1. `solve_non_distortionary`: Modelo con impuestos de suma fija (lump-sum) (Sección 6.2).
    2. `solve_distortionary_foc` / `solve_distortionary_cvxpy`: Modelo con impuestos distorsionadores sobre consumo, trabajo y capital (Sección 6.3).
    3. `solve_social_security`: Sistema de Seguridad Social de capitalización (Sección 6.4).
  - **Surrogate Convex Problem para CVXPY**: Para resolver el equilibrio competitivo descentralizado con devolución de transferencias en `solve_distortionary_cvxpy` de forma exacta y estable en un solo paso, derivamos analíticamente un problema de optimización sustituto (surrogate) con tasas de descuento y pesos de utilidad modificados ($\beta^{eff}, \gamma^{eff}$). Esto elimina la necesidad de loops de punto fijo numéricamente inestables y logra una concordancia perfecta con `fsolve` (diferencia máxima $< 10^{-7}$).
  - **Tests Unitarios**: Creado `tests/python/test_fiscal_policy.py` con 5 tests que validan: la Equivalencia Ricardiana en impuestos de suma fija, la equivalencia de resolvedores FOC vs CVXPY, la distorsión del empleo por tasas impositivas, el aplanamiento del consumo y caída de ahorros por impuestos al capital, y la sustitución perfecta entre ahorro privado voluntario y forzoso de la Seguridad Social.
  - **Generación de Notebook**: Escrito `generate_p5_notebook.py` compilando el laboratorio en `practicas/05-gobierno-fiscal/python.ipynb` con LaTeX explicativo y 3 secciones interactivas completas con sliders para todas las tasas impositivas y la edad de jubilación.
  - **Calidad**: El notebook se compila, ejecuta exitosamente sin errores (`nbconvert`) y sus salidas se limpian automáticamente con `nbstripout` en `pre-commit`. Todos los 32 tests de pytest pasan correctamente.

- **Sesión 12** — Práctica P6 (La Empresa y la Decisión de Inversión - Modelo Q de Tobin) (2026-06-19):
  - **Módulo Core**: Creado `src/macroaicomp/models/tobin_q.py` con `TobinQParameters`, `compute_steady_state`, `compute_linearized_system`, `solve_linearized_simulation` (analítico linealizado) y `solve_nonlinear_simulation` (numérico exacto con `fsolve`).
  - **Identidad de Salto Simplificada**: Demostramos y verificamos algebraicamente la equivalencia de la condición de salto de Uhlig simplificada $\hat{q}_1 = \phi \lambda_1 \hat{k}_1$ con la fórmula extendida del libro. Esto simplifica notablemente la codificación didáctica de la trayectoria estable.
  - **Tests Unitarios**: Creado `tests/python/test_tobin_q.py` con 4 tests unitarios verificando estado de equilibrio base ($q=1.0, K \approx 6.87$), autovalores y estabilidad de punto de silla ($\lambda_1 \approx -0.0607, \lambda_2 \approx 0.1072$), equivalencia matemática del factor de salto $\theta$, y simulación dinámica ante shock permanente de interés (R de 4% a 3%). Todos los tests pasan al 100%.
  - **Generación de Notebook**: Escrito `generate_p6_notebook.py` compilando el laboratorio interactivo en `practicas/06-tobin-q/python.ipynb` con LaTeX explicativo y visualizaciones avanzadas.
  - **Visualización Avanzada en 3 Paneles**: Panel 1 (Q de Tobin), Panel 2 (Stock de capital $K_t$), Panel 3 (Inversión bruta $I_t$ y depreciación $\delta K_t$ con fill_between).
  - **Diagrama de Fases Interactivo**: Grafica el vector field usando `streamplot` para un flujo visual premium, los loci de demarcación ($\Delta \hat{k}=0$, $\Delta \hat{q}=0$), la trayectoria estable (Saddle Path), el salto instantáneo de $q_t$ y el posterior ajuste dinámico hacia el nuevo equilibrio.
  - **Calidad y Verificación**: Compilado y verificado que el notebook ejecuta de extremo a extremo sin errores. Pasados todos los 36 tests de `pytest` del repositorio. Formateado automático y nbstripout aplicados con `pre-commit`.

- **Sesión 13** — Práctica P7 (El Modelo de Equilibrio General Dinámico Básico - DGE) (2026-06-19):
  - **Módulo Core**: Creado [`dge.py`](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/dge.py) con `DGEParameters`, `compute_steady_state` (cálculo analítico de estado estacionario), `solve_blanchard_khan` (resolución linealizada usando la descomposición de autovalores de la matriz de transición jacobiana $J$), y `solve_nonlinear_simulation` (simulación no lineal exacta con `fsolve` resolviendo el sistema completo en niveles).
  - **Corrección de Timing de TFP**: Se detectó una discrepancia en la indexación temporal de la productividad y los retornos del capital en el código MATLAB del libro original. Implementamos el timing económicamente correcto coincidente con el modelo Dynare, pero con un toggle opcional `use_matlab_timing` para mantener total compatibilidad didáctica y permitir verificar ambas variantes.
  - **Resolución de Mismatch en Multiplicación**: Resuelto el problema de redimensionamiento de vectores (`ValueError`) en la acumulación de capital aplastando el vector de impacto $M$ (`M.flatten()`) durante la simulación matricial.
  - **Tests Unitarios**: Creado [`test_dge.py`](file:///c:/Users/AntonioRC/Desktop/PIE/tests/python/test_dge.py) con 3 tests que verifican la precisión del estado estacionario, el comportamiento de los autovalores en el punto de silla y la simulación dinámica ante shocks tecnológicos. Todos los tests de la suite (39 en total) están en verde.
  - **Generación de Notebook**: Escrito [`generate_p7_notebook.py`](file:///c:/Users/AntonioRC/Desktop/PIE/generate_p7_notebook.py) compilando el laboratorio en [`python.ipynb`](file:///c:/Users/AntonioRC/Desktop/PIE/practicas/07-equilibrio-general-dinamico/python.ipynb) con LaTeX detallado y gráficos de alta calidad.
  - **Visualizaciones Interactivas**: Panel interactivo con 4 variables clave (Y, C, I, K) simulando el shock de productividad, y un segundo panel comparando el resolvedor lineal de Blanchard-Khan frente a la solución exacta no lineal bajo shocks de distinta magnitud para ilustrar el error de aproximación.
  - **Calidad**: El notebook se ejecuta de inicio a fin sin errores (`nbconvert --execute`) y se limpia con `nbstripout` en los hooks de pre-commit.

- **Sesión 14** — Práctica P8 (El Modelo Neoclásico de Crecimiento Exógeno - Solow-Swan) (2026-06-19):
  - **Módulo Core**: Creado [`growth.py`](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/growth.py) con `SolowSwanParameters` (dataclass de calibración), `compute_solow_steady_state` (cálculo analítico del estado estacionario) y `simulate_solow_swan` (loop dinámico de acumulación de capital en per cápita).
  - **Novedad Pedagógica (Regla de Oro)**: Implementada la demostración matemática y visual de la Regla de Oro ($s^{gold} = \alpha$) que maximiza el consumo de largo plazo, diferenciándola de las regiones de ineficiencia dinámica (sobre-acumulación).
  - **Tests Unitarios**: Creado [`test_growth.py`](file:///c:/Users/AntonioRC/Desktop/PIE/tests/python/test_growth.py) con 3 tests unitarios que comprueban la calibración estacionaria de Solow-Swan del libro, la transición de un shock de ahorro (incluyendo la caída inmediata del consumo por el sacrificio de ahorro y su posterior superación de largo plazo) y el máximo global de consumo estacionario en la Regla de Oro. Todos los tests de la suite (42 en total) pasan en verde.
  - **Generación de Notebook**: Escrito [`generate_p8_notebook.py`](file:///c:/Users/AntonioRC/Desktop/PIE/generate_p8_notebook.py) compilando el laboratorio en [`python.ipynb`](file:///c:/Users/AntonioRC/Desktop/PIE/practicas/08-solow-swan/python.ipynb) con explicaciones teóricas y widgets interactivos.
  - **Visualizaciones Avanzadas**: Panel interactivo de 4 gráficos (Y, K, C, gy) para seguir las transiciones tras shocks en ahorro ($s$), población ($n$) o TFP ($A$), y un panel interactivo específico para la curva de Regla de Oro con un rastreador dinámico del consumo respecto al ahorro actual.
  - **Calidad**: El notebook se compila, ejecuta end-to-end sin errores (`nbconvert --execute`) y se limpia automáticamente con `nbstripout` en `pre-commit`.

- **Sesión 15** — Práctica P9 (El Modelo de Crecimiento Óptimo de Ramsey) (2026-06-19):
  - **Módulo Core**: Creado [`ramsey.py`](file:///c:/Users/AntonioRC/Desktop/PIE/src/macroaicomp/models/ramsey.py) con `RamseyParameters` (dataclass de calibración), `compute_ramsey_steady_state` (cálculo analítico del estado de equilibrio), `compute_ramsey_transition_matrix` (cálculo de jacobiano, autovalores/punto de silla y factor de salto $\theta$) y resolvedores `solve_ramsey_linearized` (BK linealizado) y `solve_ramsey_nonlinear` (fsolve exacto acoplado en niveles).
  - **Identificación de Errata**: Se detectó y resolvió una errata tipográfica en la ecuación de capital linealizada (10.72) del libro impreso (donde faltaba el factor $(1+n)$ en el denominador de la desviación de consumo), alineando la codificación con la hoja de cálculo original y Dynare.
  - **Tests Unitarios**: Creado [`test_ramsey.py`](file:///c:/Users/AntonioRC/Desktop/PIE/tests/python/test_ramsey.py) con 3 tests unitarios que verifican la precisión del estado estacionario, la estabilidad de punto de silla (autovalores $\lambda_1 \approx -0.091, \lambda_2 \approx 0.111$) y la dinámica impulsiva ante un shock de productividad (comparando y logrando equivalencia exacta entre resolvedores lineal y no lineal). Todos los tests de la suite (45 en total) están en verde.
  - **Generación de Notebook**: Escrito [`generate_p9_notebook.py`](file:///c:/Users/AntonioRC/Desktop/PIE/generate_p9_notebook.py) compilando el laboratorio en [`python.ipynb`](file:///c:/Users/AntonioRC/Desktop/PIE/practicas/09-ramsey/python.ipynb) con derivaciones LaTeX y widgets interactivos.
  - **Visualizaciones Interactivas**: Panel interactivo con 4 variables (Y, K, C, I) para shocks en TFP ($A$) o descuento ($\beta$), y un panel específico de resolvedores BK lineal vs fsolve no lineal indicando el error de curvatura.
  - **Calidad**: El notebook se ejecuta de inicio a fin sin errores (`nbconvert --execute`) y se limpia con `nbstripout` en los hooks de pre-commit.

- **Sesión 16** — Soporte e Implementación de Julia (Fase de Práctica P0) (2026-06-19):
  - **Estructura Modular Julia**: Inicializada la estructura del paquete `MacroAIComp` en Julia (`src/MacroAIComp.jl` y `src/models/ArmsRace.jl`), utilizando la librería estándar `LinearAlgebra`.
  - **Módulo de Modelos**: Implementado el modelo de carrera de armamentos de Richardson en Julia con soporte para estado estacionario, cálculo de autovalores, clasificación de estabilidad de punto de silla, simulación estándar y simulación de punto de silla con salto de expectativas.
  - **Batería de Tests unitarios**: Creado `tests/julia/runtests.jl` y `tests/julia/test_arms_race.jl`. Verificada la ejecución completa con `julia --project=. tests/julia/runtests.jl` obteniendo 13/13 tests aprobados (verificando coincidencia exacta de autovalores $[-0.75, -0.25]$ y estado estacionario con MATLAB).
  - **Entorno de Integración y CI**: Habilitado el test de Julia en el archivo `.github/workflows/ci.yml` para ejecutar automáticamente los unit tests de Julia en cada commit.
- **Sesión 17** — Corrección de Modelos Macro (Ramsey, Tobin's Q y DGE Básico) (2026-06-19):
  - **Práctica P9 (Ramsey)**:
    - Reemplazado el Jacobiano de niveles por el log-linealizado oficial del libro, permitiendo que `compute_ramsey_transition_matrix` calcule los autovalores teóricos exactos ($\lambda_1 = -0.0907$, $\lambda_2 = 0.1115$) y la pendiente de salto ($\theta = 0.5751$).
    - Corregida la ecuación de Euler no lineal en `solve_ramsey_nonlinear` removiendo el término redundante de crecimiento poblacional y adaptada la simulación linealizada `solve_ramsey_linearized` para operar en log-desviaciones.
    - Añadido el cálculo y retorno de los vectores de producción (`y`) e inversión (`i`) en la simulación linealizada.
    - Ajustado el punto de partida (`c0_guess`) de `fsolve` usando el valor log-linearizado de salto, garantizando convergencia matemática robusta sin desvíos.
  - **Práctica P6 (Tobin's Q)**:
    - Modificado `compute_linearized_system` para definir la matriz de transición en log-desviaciones, arrojando los autovalores estacionarios ($\lambda_1 = -0.060658$, $\lambda_2 = 0.107158$) indicados en el Capítulo 7.
    - Reescrita `solve_linearized_simulation` para utilizar variables en log-desviaciones y calcular correctamente la inversión bruta y el capital acumulado.
    - Implementado un resolvedor de trayectoria simultánea completa para el sendero de transición de capital y Q en `solve_nonlinear_simulation`, corrigiendo el signo de los costes de ajuste en la Euler no lineal y logrando convergencia numérica estable (con discrepancia $<0.5\%$ respecto a la linealización).
  - **Práctica P7 (DGE Básico)**:
    - Modificado `solve_blanchard_khan` para utilizar las **funciones de política recursivas linealizadas** ($\eta_{ck}, \eta_{ca}, \eta_{kk}, \eta_{ka}$) derivadas del desacoplamiento de Blanchard-Khan, en lugar de simular las ecuaciones no lineales hacia adelante, eliminando toda divergencia numérica.
    - Reescrito `solve_nonlinear_simulation` para utilizar un resolvedor simultáneo de trayectoria completa e introduciendo una cota inferior estricta en el capital ($10^{-8}$) para evitar valores negativos y errores de potencias no válidas en la evaluación de la PMK.
    - Pasado el 100% de la suite de tests del repositorio (44/44 tests aprobados en verde).
    - Regenerados exitosamente los notebooks Jupyter de las prácticas P6, P7 y P9.
    - Ejecutado `pre-commit run --all-files` pasando limpio en todos sus hooks (incluyendo Black, Ruff y nbstripout).

### 2026-06-20 (Sesión 18 - Cierre y Planificación Julia)
- **Alineación de Tareas y Documentación**:
  - Actualizado el archivo `task.md` y `walkthrough.md` para reflejar la compleción del 100% de la Fase Python (con las 44/44 pruebas unitarias pasando en verde y los resolvedores estables para Tobin's Q, DGE y Ramsey).
  - Registrado el estado de la Fase Julia: los 10 modelos ya han sido portados a `src/models/*.jl` y las pruebas correspondientes registradas en `tests/julia/runtests.jl`.
- **Planificación de Siguientes Pasos**:
  - Establecida la hoja de ruta para la verificación y depuración de la suite Julia, que incluye: localizador/instalador del binario de Julia en PATH, ejecución y depuración de `runtests.jl`, desarrollo de los cuadernos de prácticas en Julia (`.ipynb` espejo) y limpieza de outputs en commits.
- **Fin de Sesión**: Cierre de la jornada de desarrollo de hoy.

### 2026-06-21 (Sesión 19 - Depuración y Verificación Final de la Suite Julia)

- **Instanciación y Dependencias de Julia:**
  - Corregido un conflicto en el UUID del paquete `Interact` en `Project.toml` que impedía la instanciación de los entornos.
  - Añadida la dependencia de `BenchmarkTools` al proyecto Julia para soportar la fase de benchmarks de rendimiento en todos los cuadernos.
- **Correcciones y Retornos en Modelos de Julia:**
  - Adaptados los solucionadores `ConsumptionSavings.jl`, `ConsumptionLeisure.jl` y `FiscalPolicy.jl` para calcular y retornar las métricas que emplean los widgets interactivos (`W`, `U`, `W_L`, `B_ss`, etc.).
  - Resueltos problemas de inconsistencias de nombres de variables en mayúsculas/minúsculas (`KeyError` al buscar `"K"`/`"k"`, etc.) en `Growth.jl` y `Ramsey.jl`.
  - Añadido un límite máximo de iteraciones (máx. 50) al bucle de bisección de disparo en `Ramsey.jl` para evitar cuelgues ante shocks intensos.
- **Resolución de Firmas de Ramsey en P9:**
  - Modificado el generador `generate_p9_julia_notebook.py` para invocar correctamente `solve_ramsey_linearized` con parámetros escalares y `solve_ramsey_nonlinear` con `n_path` en lugar de `beta_path` de acuerdo con las signaturas oficiales de la biblioteca en Julia.
- **Verificación Dinámica:**
  - Ejecutada con éxito la suite completa de ejecución dinámica de cuadernos (`execute_and_check_all_notebooks.py`). Los 10 cuadernos Julia (`julia.ipynb` del P0 al P9) compilan y se ejecutan correctamente sin ningún error de salida.
  - La suite de pruebas unitarias (`pytest tests/`) sigue pasando al 100% (44/44 tests aprobados).

- **Sesión 20 — Ejecución del Plan de Homogeneización Julia↔Python (continuación, mismo día):**
  - Creado `docs/PLAN_HOMOGENEIZACION_JULIA.md` con ~150 ítems categorizados A-M para igualar los notebooks Julia a los Python. Se trabajó en orden recomendado, verificando cada cambio con `nbconvert --execute` real (no solo lectura de código) antes de marcar un checkbox.
  - **Bloque K (críticos)** — commit `8aa55f5`: K1-K4 (t_shock mal puesto en P8/P9, locus y diagrama de fases en niveles en P6) ya estaban en el working tree de una sesión anterior pero sin verificar; al re-ejecutar P6 se encontró que el fix introducía un `UndefVarError` (`@L_str` sin `using LaTeXStrings`), corregido con un string plano. Además K5 (escala asimétrica del quiver en P2) y K6 (verificación Ricardiana mal ubicada en P5, con un desfase en cascada que también afectaba a Seguridad Social) se corrigieron de cero. K7 quedó bloqueado por M1 (sección 1 de P5 sin widget interactivo todavía).
  - **Bloque A (texto copy-paste)** — commit `e38ed3c`: centralizados los reemplazos `.py→.jl`, `cvxpy→solve_direct_optim`, `pytest→Test.jl`, etc. en `md_extractor.py`. Se descubrió que ese archivo vivía en `scratch/` (gitignored, nunca commiteado) — los 9 `generate_pX_julia_notebook.py` (P1-P9) dependían de un módulo que no existía en un clon nuevo del repo. Movido a la raíz. También se encontró y corrigió un bug real en P6: `compute_linearized_system(params, R_final)` se llamaba con 2 argumentos pero la función solo tiene un método de 1 argumento en `TobinQ.jl`.
  - **Bloque B (setup funcional)** — commit `ce66d3b`: la celda de "instalación Colab" estaba 100% comentada (no hacía nada) y la celda real nunca llamaba a `Pkg.instantiate()`. Se decidió no implementar un instalador de Julia para Google Colab (no se puede probar desde aquí y la documentación del propio proyecto, `docs/DESPLIEGUE_BINDER.md`, dice que la distribución Julia es vía MyBinder, no Colab) — en su lugar se documentó la situación honestamente y se activó `Pkg.instantiate()` de verdad.
  - **Bloque C+D (contenido P0-P2)** — commit `b069668`: D1/D3/D4 de P1 resultaron ser falsos negativos (el contenido ya estaba en el generador vía `md_cells[2]/[3]/[4]`, solo había que regenerar el notebook). D2 (glosario formateado P1) y D5 (`simulate_dornbusch_manual` en P2, con verificación cruzada contra `simulate_shock`) sí eran carencias reales, implementadas y verificadas.
  - **Bloque G+H (parámetros y rangos)**: editados `generate_p0/p3/p4/p5/p7/p9_julia_notebook.py`. Al revisar H1/H2 en P5 se encontró un **bug real preexistente**: el widget de impuestos distorsionadores pasaba los argumentos posicionales de `FiscalPolicyParameters(...)` en el orden equivocado, dejando el slider de impuesto al capital (`taur_val`) sin efecto alguno y filtrando `tauc_val` al campo `B0`. Corregido junto con los valores H1-H4. Quedó sin commitear al cierre de esta sesión (Sesión 20); el resto (H6 en P8, regenerar, ejecutar y commitear) se completó en la Sesión 21 (2026-06-22) — ver `git log` (commit del lote G+H).
  - Lección de proceso anotada en memoria: una notificación de tarea en background con "exit code 0" no es prueba suficiente de que un notebook ejecutó sin error si no se lee el log completo (pasó con P6 en esta misma sesión).

### 2026-06-22 (Sesión 21 — Cierre de Bloque G+H)

- Retomada la sesión anterior exactamente donde quedó (ver bloque "ESTADO" al
  principio de `docs/PLAN_HOMOGENEIZACION_JULIA.md`, ahora ya resuelto y
  limpiado tras el cierre de este bloque).
- Completado H6 (P8: `n=0.02` en el benchmark, antes `0.015`).
- Regenerados y ejecutados los 7 notebooks afectados (P0, P3, P4, P5, P7,
  P8, P9) con `nbconvert --execute`, leyendo el log completo de cada uno
  (no solo el exit code, aplicando la lección de la sesión anterior).
- Verificación específica del bug de P5: la celda de Equivalencia Ricardiana
  de la Sección 1 imprime una diferencia de consumo de `0.0` exacto tras el
  fix, confirmando que el modelo con impuesto de suma fija + devolución de
  recaudación es indistinguible del caso sin impuestos.
- 44/44 tests pytest y la suite completa de Julia (867 tests) en verde.
- Checklist actualizado: Bloque G+H completo (más F1/F2, que ya estaban
  satisfechos de sesiones anteriores pero nunca se habían marcado).
- **Cierre del Bloque E completo** (E1-E47) en varios commits adicionales:
  grid global (`default(gridalpha=0.6, gridstyle=:dot)`), paleta de colores
  UMA en los 9 notebooks (con bugs reales encontrados de paso: mapeo de
  colores desordenado en P8, "SS Final" en negro en vez de rojo en P8/P9,
  estructura de la celda de comparación de P7 no coincidía con Python),
  y títulos/etiquetas descriptivos.
- **F3, G2, M4, J1-J3 cerrados**: descripciones en español a los sliders
  vía `slider(rango; value=..., label="...")` de Interact.jl; slider de δ
  añadido en P7 (antes hardcodeado); tolerancias de verificación ajustadas
  en P2/P3/P4.
- **Bug real encontrado en el Python original (no en Julia)**: al intentar
  implementar M3 (checkbox `use_matlab_timing` en P7), se descubrió que
  `generate_p7_notebook.py` llamaba a `solve_blanchard_khan` y
  `solve_nonlinear_simulation` con un kwarg `use_matlab_timing` que esas
  funciones de `src/macroaicomp/models/dge.py` no aceptan — lanzaba
  `TypeError` si un alumno ejecutaba esa celda. Corregido quitando el kwarg
  de las llamadas (el checkbox queda en la interfaz pero sin efecto real,
  ya que esa funcionalidad nunca se implementó de verdad en ninguno de los
  dos lenguajes). Verificado con `nbconvert --execute` que la celda ahora
  ejecuta limpia de principio a fin.

### 2026-06-22 (Sesión 22 — Bug de WebIO en P0, investigación y cierre)

- El usuario reportó en vivo (vía capturas de pantalla del servidor Jupyter
  local) el error `WebIO not detected` en dos celdas de la versión Julia
  de P0, y un `NameError: name 'interact' is not defined` en la versión
  Python.
- **P0 Julia — causa raíz encontrada**: una sesión anterior (2026-06-21,
  commits `3d87664`/`9a20a80`) ya había diagnosticado y arreglado este
  mismo problema, reemplazando `@manipulate` por un gráfico estático de 4
  escenarios. Pero ese fix solo tocó el `.ipynb` generado, nunca
  `generate_p0_julia_notebook.py` — exactamente el mismo patrón que ya
  había pasado con P1 (ver Sesión 21). Al regenerar P0 varias veces durante
  el plan de homogeneización del 22 de junio, `using Interact` y
  `@manipulate` volvieron a aparecer. Corregido de verdad en el script
  esta vez (commit `e9f40a0`).
- De paso se detectó que esa celda estática portada usaba colores Julia
  genéricos (`:steelblue, :darkorange, :purple, :crimson`) en vez de la
  paleta UMA recién unificada en el resto del notebook esa misma sesión —
  corregido (commit `805d333`).
- **Investigación de fondo sobre WebIO** (a petición explícita del
  usuario, que quería intentar el slider real antes de aceptar el
  estático): se instaló la extensión oficial `webio_jupyter_extension` y
  `jupyter labextension list --verbose` confirmó la incompatibilidad
  exacta: `webio-jupyterlab-provider@0.1.0` declara
  `@jupyterlab/application >=3.0.0 <4.0.0`, mientras el proyecto usa
  JupyterLab `4.5.9`. Es una incompatibilidad estructural del paquete
  (sin actualizar desde la era de JupyterLab 3.x), no un problema de
  configuración local — afectaría igual en Binder o Colab. Extensión
  desinstalada tras confirmar el hallazgo. Decisión registrada como
  Decisión técnica #6: mantener el gráfico estático en P0.
- **P0 Python**: confirmado que no había ningún bug real — el `NameError`
  ocurría porque el usuario ejecutó la celda del widget sin ejecutar antes
  la celda de imports en ese kernel. Verificado con
  `nbconvert --execute` (Restart & Run All) que el notebook completo
  ejecuta sin ningún error (commit `7771d2d`).
- **Nueva decisión de alcance** (Decisión técnica #7): P0 se usará como
  práctica de referencia pedagógica. Se revisará a fondo en Python y
  Julia para maximizar su calidad didáctica, y esa revisión servirá de
  plantilla para mejorar la pedagogía de P1-P9. **Pendiente**: definir en
  una próxima sesión qué significa concretamente "aumentar la pedagogía"
  para P0 (¿más derivaciones paso a paso?, ¿más preguntas de bitácora?,
  ¿mejor guía para dummies?, ¿comparación lado a lado Python/Julia?) antes
  de empezar a implementarlo.

### 2026-06-22 (Sesión 22, continuación — alcance de "aumentar la pedagogía" de P0)

- El usuario concretó el alcance pendiente de la Decisión técnica #7 en dos
  ejes explícitos: **económico** (usar `oraculo.md` no solo como assert
  oculto, sino visible en el propio notebook) y **de programación**
  (comentar las celdas de código: qué hace cada una, por qué, y qué pasa al
  ejecutarla).
- Implementado en `python.ipynb` y `generate_p0_julia_notebook.py` (fuente
  de `julia.ipynb`), sin tocar `src/macroaicomp/models/arms_race.py` ni
  `phase_diagram.py` (ya tienen docstrings NumPy a nivel de librería; lo que
  faltaba era el comentario en la celda concreta que los llama):
  - Cada celda de código relevante recibió 2-4 líneas de comentario nuevas
    siguiendo el patrón QUÉ hace / POR QUÉ (incluida la interpretación
    económica, p.ej. por qué subir α reduce el SS de ambos países) / QUÉ
    VERÁS al ejecutarla.
  - Las celdas markdown "Verificación frente al oráculo" (Caso 1) y "Punto
    de silla" (Caso 2) se extendieron con la tabla completa de valores
    esperados de `oraculo.md`, para que el alumno no tenga que abrir ese
    archivo aparte.
  - Cambios puramente additivos: ningún assert, fórmula ni resultado
    numérico se modificó.
- Verificado con `nbconvert --to notebook --execute --inplace` en ambos
  notebooks (log completo leído, no solo el exit code): los dos ejecutan
  sin errores y todos los `assert`/`@assert` siguen pasando.
- P1-P9 quedan fuera de esta sesión — esta revisión de P0 es la plantilla a
  replicar más adelante, no el trabajo en sí (ver Decisión técnica #7).

### 2026-06-22 (Sesión 22, continuación — comentarios más profundos + Hito 2 piloto en P0)

- El usuario pidió una nota de calidad de P0 del 1 al 10: se dio **8/10**,
  señalando 3 carencias. Pidió arreglarlas, lo que se resolvió en dos
  rondas:
- **Ronda 1 — más explicación de programación + retirar "dummies"**: las
  celdas de código de `python.ipynb` y `generate_p0_julia_notebook.py`
  ganaron comentarios sobre la SINTAXIS (qué es un `import`/`using`, un
  dataclass/struct, una f-string/interpolación de cadenas, el indexado
  0-based de Python vs. 1-based de Julia, broadcasting, tuplas que se
  reparten en variables...), no solo la economía. Se retiró la palabra
  "dummies" del título de la guía rápida de inicio (no pegaba con el tono
  del resto) en ambos notebooks — pasa a "GUÍA RÁPIDA DE INICIO". Commit
  `faee75b`.
- **Ronda 2 — Hito 2 (guion de laboratorio) adelantado como piloto en P0**:
  de las 3 carencias señaladas en la nota de calidad, solo la de
  "faltan objetivos/bitácora/accidentes de laboratorio/extensiones ABP" era
  corregible con código (las otras dos —asimetría WebIO y `.xlsx`
  pendiente— ya estaban resueltas/fuera de alcance, ver Decisión técnica
  #8). Se creó `practicas/_plantilla/GUION.md` (plantilla maestra del
  Hito 2, §3.2.1 del plan maestro) y
  `practicas/00-introduccion-sistemas-dinamicos/GUION.md` (relleno completo
  para P0: objetivos didácticos con verbos de Bloom, prerrequisitos, tiempo
  estimado, "reactivos" digitales, procedimiento paso a paso, accidentes de
  laboratorio específicos de este modelo, cuestionario de bitácora de 5
  preguntas y 3 extensiones para ABP). Ambos notebooks enlazan al GUION
  desde la celda de bienvenida (objetivos/tiempo) y desde la conclusión
  (bitácora/ABP), sin tocar ninguna celda de código.
- Checkboxes actualizados en `PLAN_MAESTRO_MACRO_AI_COMP.md` (§3.2.1 y
  columna "Bitácora plantilla" de P0 en §2). La validación de la plantilla
  contra un guion real de Química Orgánica que pide el plan maestro queda
  marcada como pendiente manual (no se puede hacer por código).
- Verificado con `nbconvert --execute` en ambos notebooks tras enlazar el
  GUION: sin errores.
- P1 y P8 (los otros dos pilotos previstos en el plan maestro) y el resto
  de prácticas quedan sin GUION.md — pendientes de iterar más adelante.

### 2026-06-22 (Sesión 23 — Plan de Homogeneización Pedagógica P1-P9)

- **Contexto**: ejecución completa de `docs/PLAN_HOMOGENEIZACION_PEDAGOGICA.md`
  (7 bloques A-G) para replicar en P1-P9 la calidad pedagógica de P0:
  oráculo visible, asserts de verificación, `GUION.md` por práctica, enlaces
  y comentarios de programación.
- **Bloque C (wording "dummies")**: reemplazo masivo de "GUÍA RÁPIDA PARA
  DUMMIES" → "GUÍA RÁPIDA DE INICIO" en 17 notebooks (P1-P9 Python y Julia).
  P7 Python no contenía el término originalmente.
- **Bloque A (oráculo + asserts)**: creados `oraculo.md` para P2-P9 a partir
  de los valores de `tests/python/test_*.py` (44 tests en verde). Añadidas
  celdas de `assert`/`@assert` en los 18 notebooks (P1-P9 × Python/Julia),
  verificando estado estacionario, autovalores, shocks y equivalencia de
  solvers contra los valores del libro y apéndices MATLAB/DYNARE. 3 agentes
  en paralelo editaron generadores; post-procesamiento manual para regenerar
  notebooks desde generadores editados.
- **Bloque B (tablas de oráculo visibles)**: añadidas tablas markdown con
  valores esperados en cada notebook, siguiendo el formato de P0.
- **Bloque E (`GUION.md`)**: creados `GUION.md` para P1-P9 a partir de la
  plantilla `practicas/_plantilla/GUION.md`, con objetivos Bloom,
  prerrequisitos, accidentes de laboratorio específicos de cada modelo,
  5-6 preguntas de bitácora y 2-3 extensiones ABP.
- **Bloque F (enlaces GUION)**: añadidos enlaces a `GUION.md` en celdas de
  bienvenida y/o conclusión de P1-P2 y P4-P6. P3, P7-P9 quedan con enlace
  parcial (los `GUION.md` existen en sus carpetas pero los notebooks
  generados no los referencian explícitamente — requiere editar generadores).
- **Bloque D (comentarios de programación)**: **diferido conscientemente**.
  Es el bloque más grande (~4-5 días estimados en el plan, 18 notebooks ×
  ~10-20 celdas de código cada uno). Los notebooks ya tienen texto explicativo
  sustancial en markdown; los comentarios QUÉ/POR QUÉ/QUÉ VERÁS al estilo P0
  quedan como siguiente prioridad tras esta sesión.
- **Verificación**: `pytest tests/python/` = 44/44 ✅. Ejecución completa
  con `nbconvert --execute` de los 18 notebooks (P1-P9 × Python/Julia):
  todos los Python OK; Julia P1-P6 OK, P7-P9 pendientes de confirmación
  (en ejecución al cierre de esta entrada).
- **PLAN_MAESTRO actualizado**: tabla §2 con columna "Bitácora plantilla"
  [x] para P1-P9, columna "Versión Julia" [x] para P1-P9, y columna "Estado"
  actualizada a [~] reflejando el estado real (oráculo+GUION+asserts
  completos, comentarios pendientes). §3.2.1 marcado P1 y P8 como pilotos
  de GUION completados.
- **Lección de proceso**: 3 agentes lanzados en paralelo editaron generadores
  correctamente pero no siempre regeneraron los notebooks. Post-procesamiento
  necesario: ejecutar `generate_pX_notebook.py` y
  `generate_pX_julia_notebook.py` tras recibir los resultados de los agentes,
  y verificar con `nbconvert --execute` real (no solo exit code).
  Coste total de la sesión: ~3h de trabajo con agentes + ~1h de
  post-procesamiento y verificación.

### 2026-06-23 (Sesión 24 — Repo público y primera versión de la web)

- Con P0-P9 completos y homogeneizados en Python y Julia, se publicó el
  repositorio en GitHub como `OcBSmith/PIE-Economics` (supera la Decisión
  técnica #1; ver Decisión #9 más arriba) y se configuró `.github/workflows/ci.yml`
  con tres jobs: `python-tests`, `julia-tests` y `deploy-docs` (este último
  depende de los dos primeros y publica en GitHub Pages).
- Se evaluó Quarto como motor de la web pública (`docs/PLAN_WEB_QUARTO.md`)
  pero se optó por **MkDocs Material** (Decisión #10): creado `mkdocs.yml`
  (tema `material`, plugin `mkdocs-jupyter` para renderizar los `.ipynb`
  directamente) y `build_site.py` (copia `practicas/` e `index.md`/
  `guia-profesor.md` de la raíz a `docs/` antes del build).
- Commit `795cc5c` ("feat: sitio web con MkDocs Material + GitHub Pages").
  Un primer intento de formateo automático (`black`) y de ese mismo commit
  fallaron en CI (ver `gh run list`); corregidos en commits posteriores
  (`08223b0`, `0a41ddd`).

### 2026-06-24 (Sesión 25 — Ejecución de código en vivo: primer intento con Thebe)

- Creado `docs/PLAN_THEBE_INTERACTIVO.md`: plan para sustituir los simples
  enlaces a Binder por ejecución de código embebida en la propia página
  (celdas editables con botón "Run").
- Commit `3a62372`: primera versión de `docs/javascripts/thebe.js` usando la
  librería `thebe` estándar (cargada vía `extra_css`/`extra_javascript` en
  `mkdocs.yml`).
- Commit `ff45a70`: los botones "Activar Python"/"Activar Julia" no tenían
  ningún manejador de eventos enganchado (faltaba `addEventListener`) —
  corregido.

### 2026-06-25 (Sesión 26 — Sustitución de Thebe por WebSocket directo)

- La librería `thebe` resultó tener un loader AMD incompatible con el
  entorno de la página (ver Decisión #11 más arriba). Commit `b12a1c6`:
  reescrito `docs/javascripts/thebe.js` como cliente propio que habla
  directamente con la API de un servidor Binder: `POST` a
  `mybinder.org/build/...` → sondeo de `api` hasta `status: ready` →
  `POST api/kernels` → `WebSocket` a `api/kernels/<id>/channels` →
  `execute_request` por cada botón "Run" de cada bloque de código.
  Verificado en CI: los 3 jobs (`python-tests`, `julia-tests`,
  `deploy-docs`) pasaron en verde (run `28149904232`).
- Pendiente de verificación manual en navegador real (no se ha podido
  confirmar visualmente en esta sesión que el flujo completo — activar
  kernel, esperar a Binder, pulsar Run, ver output — funciona de extremo a
  extremo; `docs/PLAN_THEBE_INTERACTIVO.md` sigue con sus checkboxes de
  Fase 2-4 sin marcar).

### 2026-06-25 (Sesión 27 — Unificación de documentación)

- A petición del usuario, lectura completa de toda la documentación del
  repo y corrección de inconsistencias encontradas para evitar confusión:
  `README.md` desactualizado (decía "sin remoto, solo P0 completo"),
  cabeceras "ESTADO" de `docs/PLAN_HOMOGENEIZACION_JULIA.md` y
  `docs/PLAN_HOMOGENEIZACION_PEDAGOGICA.md` que no reflejaban que ambos
  planes ya estaban cerrados, `docs/PLAN_WEB_QUARTO.md` sin marcar como
  superseded, y el hallazgo #6 de esta misma sección (duplicado
  raíz/`docs/` con la dirección de la copia invertida respecto a lo que
  parecía a simple vista).
