# PLAN MAESTRO DE EJECUCIÓN — PROYECTO MACRO-AI-COMP

> **Convocatoria:** INNOVA26 (UMA / Banco Santander)
> **Duración:** 24 meses (Noviembre 2026 – Noviembre 2028)
> **IP / Coordinadora:** Dra. Anelí Bongers
> **Responsable técnico (PTGAS):** D. Antonio Francisco Romero Carrasco
> **Versión del plan:** v1.0 — última actualización: 2026-06-17

---

## 0. NORTE ESTRATÉGICO Y FILOSOFÍA DE TRABAJO

### 0.1. La línea de Aneli (no perder de vista NUNCA)

> Aneli ha sido explícita: tenemos su libro *An Introduction to Computational Macroeconomics* (Bongers, Gómez, Torres — Vernon Press, 2019) en Word, y la idea fundamental es **"ir jugando con él para que vaya haciendo programas en Python y en Julia"**. En el libro los modelos están resueltos en **hoja de cálculo**; nuestra tarea es **portarlos a Python y Julia** y meter, además, los modelos matemáticos extra que aporte Cabello (Che).

**Traducción operativa de ese feedback en este plan:**

- El **libro de Aneli es el corpus mínimo obligatorio** del proyecto. Cada capítulo se trata como una "práctica de laboratorio".
- Cada práctica tiene **3 versiones equivalentes**: Excel (original del libro, Nivel 1) → Python/Colab (Nivel 2) → Julia (Nivel 3).
- Los **apéndices del libro en MATLAB y DYNARE** son nuestro "oráculo de verificación numérica": si nuestro código en Python/Julia da los mismos números, está bien.
- Los modelos extra de Cabello se integran como **prácticas complementarias** del bloque Métodos Matemáticos / Matemáticas Financieras / Optimización.
- La IA Generativa (Claude / ChatGPT) actúa como **copiloto del alumno**, nunca como sustituto. Cada práctica lleva su propio paquete de prompts curados.

### 0.2. Principio rector PTGAS

> "Si no se puede reproducir desde cero en menos de 10 minutos por un alumno con un portátil normal, no está terminado."

Aplicamos al laboratorio virtual los mismos estándares que en el laboratorio de química: protocolo escrito, materiales identificados, control de variables, bitácora obligatoria, trazabilidad de errores.

### 0.3. Estándares de programación (no negociables en todo el proyecto)

> El código que generamos es **material docente público con DOI**. Va a ser leído por alumnos que aprenden, por profesores que replican y por revisores de artículos. Tiene que ser ejemplar. Un código oscuro, sin documentar o con funciones de 200 líneas no enseña nada bueno.

**Principio**: aplicamos en todo momento las mismas buenas prácticas que le pediríamos a un alumno de último año o a un junior en cualquier equipo de data science. El código del proyecto es en sí mismo un objeto de aprendizaje.

#### Estándares Python

- **Estilo**: [PEP 8](https://peps.python.org/pep-0008/) obligatorio. Formateado automático con `black` (sin configuración manual, cero debates de estilo).
- **Linting**: `ruff` como linter rápido que sustituye a `flake8` + `isort` + `pydocstyle`.
- **Type hints**: obligatorios en todas las funciones de los módulos de librería (`src/`). Opcionales pero recomendados en los notebooks.
- **Docstrings**: formato [NumPy docstring](https://numpydoc.readthedocs.io/en/latest/format.html) en todas las funciones públicas. Incluir `Parameters`, `Returns`, `Examples` y referencia al capítulo del libro cuando aplique.
- **Modularización**:
  - Los notebooks son el *frontend* (exposición didáctica), **no el lugar donde vive la lógica**. Las funciones reutilizables van en `src/macroaicomp/`.
  - Regla: si una función aparece en más de un notebook, **ya está en `src/`**.
  - Tamaño máximo orientativo: funciones de ≤ 40 líneas; un módulo `.py` de ≤ 300 líneas.
- **Nombres**: descriptivos en inglés (para internacionalización del repo). Variables del modelo en la notación del libro (`k_ss`, `c_star`, `beta`). Sin abreviaturas crípticas.
- **Constantes de calibración**: definidas siempre en un dict o dataclass al inicio del notebook/función, nunca enterradas en una línea de cálculo.

#### Estándares Julia

- **Estilo**: [BlueStyle](https://github.com/JuliaDiff/BlueStyle) (variante de estilo más usada en economía computacional). Formateado con `JuliaFormatter.jl`.
- **Naming**: funciones en `snake_case`, tipos y módulos en `PascalCase`, consistente con Base Julia.
- **Modularización**: cada modelo va en su propio módulo Julia (`.jl` en `src/`). Los notebooks/scripts de práctica hacen `include()` o `using MacroAIComp`.
- **Type annotations**: en las funciones de `src/` para aprovechar el despacho múltiple de Julia.
- **Docstrings**: formato docstring estándar de Julia con `"""..."""` antes de cada función pública.
- **Performance**: no premature optimization, pero sí evitar asignaciones innecesarias en bucles (`@inbounds`, `@views` cuando sea pedagógicamente apropiado explicarlo). Usar `BenchmarkTools.@btime` para comparar con Python en el manual.

#### Estándares de notebooks (Jupyter / .ipynb)

- **Estructura obligatoria de cada notebook**:
  1. Celda de encabezado: título, ID de práctica, autores, fecha, versión, licencia
  2. Celda de instalación (Colab): `pip install` / `Pkg.add` dentro de `%%capture` para no contaminar el output
  3. Celda de imports: todos los imports juntos, agrupados (stdlib → third-party → proyecto)
  4. Secciones con headers Markdown numerados
  5. Celda de parámetros de calibración: bloque aislado, etiquetado, con comentario económico
  6. Celdas de solución: una operación conceptual por celda, con texto explicativo encima
  7. Celda de verificación: comparación numérica contra el oráculo (MATLAB/DYNARE del libro)
  8. Celda de visualización: siempre con título de gráfico, etiquetas de ejes con unidades y leyenda
  9. Celda de conclusión: 3-5 líneas de interpretación económica
- **Outputs limpios al commitear**: `nbstripout` borra los outputs antes de cada commit (el CI falla si hay outputs). Los alumnos ejecutan y ven los outputs en vivo, no en el repo.
- **Reproductibilidad**: ejecutar "Restart & Run All" no debe producir ningún error. Es el test mínimo antes de cualquier PR.
- **Seeds**: cualquier número aleatorio usa `np.random.seed(42)` / `Random.seed!(42)` al inicio.

#### Estructura del código fuente (`src/`)

```
src/
└── macroaicomp/             # Paquete Python instalable (pip install -e .)
    ├── __init__.py
    ├── models/
    │   ├── islm.py          # Funciones del modelo IS-LM
    │   ├── dornbusch.py
    │   ├── household.py     # Consumo-ahorro, consumo-ocio
    │   ├── dge.py           # DGE básico
    │   ├── growth.py        # Solow, Ramsey
    │   └── ...
    ├── solvers/
    │   ├── shooting.py      # Algoritmo de shooting para saddlepath
    │   ├── linearization.py # Linearización en estado estacionario
    │   └── ...
    ├── plotting/
    │   ├── phase_diagram.py # Diagrama de fases estándar del proyecto
    │   ├── irf.py           # Impulse response functions
    │   └── styles.py        # Estilo visual único del proyecto (colores UMA)
    └── utils/
        ├── calibration.py   # Helpers de calibración y validación
        └── io.py            # Lectura/escritura de parámetros desde YAML
```

```
src/
└── MacroAIComp/             # Paquete Julia registrable
    ├── MacroAIComp.jl       # Entry point, exports
    ├── models/
    │   ├── ISLM.jl
    │   ├── Household.jl
    │   ├── DGE.jl
    │   └── Growth.jl
    ├── solvers/
    │   ├── Shooting.jl
    │   └── Linearization.jl
    └── plotting/
        └── IRF.jl
```

#### Tests

- [ ] Directorio `tests/` con pruebas unitarias usando `pytest` (Python) y `Test.jl` (Julia)
- [ ] Tests mínimos obligatorios por práctica:
  - Que el estado estacionario calculado coincide con el del oráculo (tolerancia ≤ 1e-6)
  - Que los gráficos se generan sin error (smoke test)
  - Que la función principal funciona con los parámetros del libro y con parámetros alternativos
- [ ] Coverage objetivo: ≥ 80% en `src/` (no en notebooks)
- [ ] El CI de GitHub Actions falla si los tests fallan o si el coverage baja

#### Code review

- [ ] Toda incorporación de código al `main` va por Pull Request, sin excepciones
- [ ] PR template en `.github/PULL_REQUEST_TEMPLATE.md` con checklist: estilo ✓, tests ✓, notebook ejecutado ✓, oráculo verificado ✓, docstring ✓
- [ ] Al menos 1 reviewer (AR revisa siempre; AB o JLT según el modelo)
- [ ] Ningún PR se mergea con comentarios sin resolver

#### Cómo enseñamos estas prácticas al alumno

El código de las prácticas **no es solo una herramienta, es un modelo a imitar**. Cada notebook incluye una celda de "Buenas prácticas aplicadas aquí" que señala explícitamente: *"Observa que la función `compute_steady_state()` está documentada, tiene type hints y está separada de la celda de visualización. Cuando hagas tu ABP, haz lo mismo."*

Los megaprompts de la Capa B (§7) tienen instrucción explícita: *"Si el alumno te pide código, escríbelo siguiendo PEP 8 / BlueStyle, con docstring y separando la lógica del modelo de la visualización."*

**DOCUMENTACIÓN PARALELA:**
- [ ] `docs/guia-estilo-codigo.md`: guía de estilo de 2 páginas pensada para alumnos. Lenguaje claro, ejemplos buenos vs malos. Se distribuye en la Sesión 0.

---

### 0.4. Convenciones de este documento

- `[ ]` = pendiente · `[x]` = completado · `[~]` = en curso · `[!]` = bloqueado
- Cada checkbox lleva (cuando aplica) **responsable** entre paréntesis: `(AR)` Antonio, `(AB)` Aneli, `(JLT)` Torres, `(JMC)` Cabello.
- Cada hito tiene un bloque **DOCUMENTACIÓN PARALELA** — completarlo a la vez que se ejecuta, no después.
- Los enlaces a archivos del repo se ponen como ``[`ruta/al/archivo`](url)`` para que cliquen desde GitHub.
- Las referencias internas al plan usan el número de sección (ej. §3.1, §8.3).

---

## 1. FASE 0 — PRELANZAMIENTO E INFRAESTRUCTURA (Mes 0, antes de empezar oficialmente)

> Esta fase NO está en el cronograma oficial de la propuesta. Es trabajo previo del PTGAS para llegar al Mes 1 con todo listo. **Sin esto, el Mes 1 se pierde montando entornos.**

### 1.1. Identidad del proyecto

- [ ] Reservar nombre de la organización en GitHub: `macro-ai-comp-uma` (AR)
- [ ] Crear cuentas/roles para AB, JLT, JMC dentro de la organización (AR)
- [ ] Reservar dominio corto (opcional): `macroaicomp.uma.es` o subdominio en GitHub Pages
- [ ] Diseñar logo simple y paleta (azul UMA + verde laboratorio)
- [ ] Redactar `README.md` raíz con misión, equipo y badges (build, license MIT, DOI)

### 1.2. Arquitectura del monorepo

Estructura propuesta (todo bajo licencia MIT salvo manuales bajo CC BY-SA 4.0):

```
macro-ai-comp/
├── README.md
├── LICENSE                          # MIT (código)
├── LICENSE-DOCS                     # CC BY-SA 4.0 (manuales)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CITATION.cff                     # Para citas académicas
├── docs/                            # Web/GitHub Pages
│   ├── manual-prompting/
│   ├── guias-laboratorio/
│   └── memoria-tecnica/
├── practicas/                       # Núcleo del proyecto
│   ├── 00-introduccion-sistemas-dinamicos/
│   ├── 01-is-lm-dinamico/
│   ├── 02-overshooting-dornbusch/
│   ├── 03-consumo-ahorro/
│   ├── 04-consumo-ocio/
│   ├── 05-gobierno-fiscal/
│   ├── 06-tobin-q/
│   ├── 07-equilibrio-general-dinamico/
│   ├── 08-solow-swan/
│   ├── 09-ramsey/
│   └── X-modelos-cabello/           # Extras del Che
├── prompts/                         # Framework de prompting
│   ├── system-prompts/
│   ├── megaprompts/
│   └── catalogo-tutor/
├── bitacora/                        # Plantillas de cuaderno
│   ├── plantilla-bitacora.ipynb
│   └── plantilla-bitacora.jl
├── evaluacion/                      # Rúbricas, encuestas, KPIs
│   ├── rubricas/
│   ├── encuestas/
│   └── dashboard-kpi/
├── infraestructura/                 # Configs reproducibles
│   ├── requirements.txt             # Python pinneado
│   ├── Project.toml                 # Julia pinneado
│   ├── environment.yml              # Conda
│   ├── .devcontainer/               # Codespaces / VS Code
│   └── colab-setup.sh
├── src/                             # ⬅ Código fuente modularizado (ver §0.3)
│   ├── macroaicomp/                 # Paquete Python instalable
│   │   ├── models/                  # Un módulo por modelo del libro
│   │   ├── solvers/                 # Algoritmos numéricos (shooting, linealización)
│   │   ├── plotting/                # Estilo visual único del proyecto
│   │   └── utils/                   # Calibración, IO, helpers
│   └── MacroAIComp/                 # Paquete Julia equivalente
│       ├── models/
│       ├── solvers/
│       └── plotting/
├── tests/                           # Tests unitarios Python (pytest) + Julia (Test.jl)
│   ├── python/
│   └── julia/
└── .github/
    ├── workflows/                   # CI: tests + render notebooks
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

- [~] Crear estructura de carpetas con commits trazables (AR) — creados `src/`, `tests/`, `practicas/00.../` con el primer commit (2026-06-17); faltan `docs/actas/`, `prompts/`, `bitacora/`, `evaluacion/`, `infraestructura/`, `.github/`
- [~] Añadir `.gitignore` correcto para Python + Julia + Jupyter + LaTeX (AR) — Python/Jupyter cubierto; falta Julia y LaTeX
- [ ] Configurar `pre-commit` con los hooks de calidad de código (ver §0.3):
  - [ ] `black` — formateo automático Python
  - [ ] `ruff` — linting Python (sustituye flake8 + isort + pydocstyle)
  - [~] `nbstripout` — instalado y ejecutado manualmente antes de cada commit; falta integrarlo como hook de pre-commit automático
  - [ ] `JuliaFormatter` — formateo automático Julia (via pre-commit hook)
  - [ ] `nbval` (opcional) — valida que los notebooks se ejecutan como smoke test local
- [x] Crear `pyproject.toml` con configuración de `black` y `ruff` (line-length 88, target Python 3.11)
- [ ] Crear `.JuliaFormatter.toml` con estilo BlueStyle
- [x] Crear `setup.py` / `pyproject.toml` para que `macroaicomp` sea instalable con `pip install -e .`
- [ ] Crear `Project.toml` del paquete Julia `MacroAIComp`
- [ ] Configurar GitHub Actions para CI:
  - [ ] Test que cada notebook se ejecuta sin errores (`nbconvert --execute`)
  - [ ] Test que los scripts Julia se compilan (`julia --project -e "using MacroAIComp"`)
  - [ ] Ejecutar `pytest tests/python/` con coverage ≥ 80%
  - [ ] Ejecutar `julia --project tests/julia/runtests.jl`
  - [ ] Render automático de notebooks a HTML para GitHub Pages
  - [ ] Badge de estado del CI en el README
- [ ] Habilitar GitHub Pages servido desde `/docs`
- [ ] Configurar Zenodo para DOI automático en releases (citabilidad académica)

### 1.3. Entornos reproducibles

- [~] **Python**: fijar versión (recomendado 3.11), `requirements.txt` con:
  - `numpy`, `scipy`, `sympy`, `matplotlib`, `pandas`, `statsmodels`, `linearmodels`, `numba`, `jupyter`, `ipywidgets`
  - Hecho hasta ahora: `numpy`, `scipy`, `matplotlib`, `ipywidgets`, `jupyter`, `nbconvert`, `nbstripout`, `pytest` (suficiente para P0). Pendientes: `sympy`, `pandas`, `statsmodels`, `linearmodels`, `numba` (se añadirán cuando las prácticas que los necesiten lo requieran). Venv local con Python 3.14 (la máquina no tiene 3.11, pero `requires-python >=3.11` es compatible).
- [ ] **Julia**: fijar versión (recomendado 1.10 LTS), `Project.toml` con:
  - `DifferentialEquations`, `NLsolve`, `Optim`, `Plots`, `DataFrames`, `Symbolics`, `IJulia`
- [ ] Probar que **un notebook funciona en Google Colab gratuito** sin tocar nada (instalación al vuelo de Julia con `%%capture`)
- [ ] Crear devcontainer para VS Code / Codespaces (clase universitaria sin instalar nada)
- [ ] Documentar **plan B** offline: instalador único de Anaconda + JuliaUp para aulas sin internet fiable

### 1.4. Comunicación interna del equipo

- [ ] Canal de Slack / Teams del proyecto (AR + AB)
- [ ] Tablero Kanban (GitHub Projects) con columnas: `Backlog`, `Este sprint`, `En curso`, `Revisión`, `Hecho`
- [ ] Calendario compartido con hitos del cronograma INNOVA26
- [ ] Plantilla de acta de reunión en `/docs/actas/PLANTILLA.md`
- [ ] Acuerdo de cadencia: reunión quincenal de 45 min con AB; mensual de equipo completo

**DOCUMENTACIÓN PARALELA (Fase 0):**
- [ ] `docs/infraestructura.md`: decisiones técnicas justificadas (por qué Colab + Julia, por qué MIT, por qué Zenodo)
- [ ] `docs/onboarding.md`: cómo darse de alta cualquier docente nuevo en el repo

---

## 2. MAPEO LIBRO → PIPELINE COMPUTACIONAL (referencia transversal)

Esta tabla es el corazón operativo del proyecto. Cada fila se cierra cuando las 3 columnas + bitácora + prompts están verdes.

| # | Capítulo del libro (Bongers/Gómez/Torres 2019) | Modelo | Excel original | Apéndice MATLAB/DYNARE de verificación | Versión Python/Colab | Versión Julia | Bitácora plantilla | Prompts curados | Estado |
|---|---|---|---|---|---|---|---|---|---|
| P0 | Cap. 1 — Introduction to computational dynamic systems | Sistema 2 ecuaciones genérico | [ ] localizar `.xlsx` del libro | App. B (MATLAB) + App. C (DYNARE) | [x] `practicas/00/python.ipynb` | [ ] `practicas/00/julia.ipynb` | [ ] | [ ] | [~] Python listo y verificado (2026-06-17); falta Excel, Julia, bitácora y prompts |
| P1 | Cap. 2 — The dynamic IS-LM model | IS-LM dinámico + Phillips | [ ] | App. D (MATLAB) + App. E (DYNARE) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2 | Cap. 3 — Exchange rate overshooting | Dornbusch overshooting | [ ] | App. F (DYNARE) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3 | Cap. 4 — Consumption-saving optimal decision | Hogar consumo-ahorro | [ ] | App. G (MATLAB) + App. H (Newton) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4 | Cap. 5 — Consumption-saving + leisure | Hogar con oferta de trabajo | [ ] | App. I (MATLAB) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P5 | Cap. 6 — Government and fiscal policy | Impuestos + cotizaciones | [ ] | App. J (MATLAB) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P6 | Cap. 7 — Firm/investment, Tobin's Q | Tobin Q | [ ] | App. K (DYNARE) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P7 | Cap. 8 — Basic Dynamic General Equilibrium | DGE básico | [ ] | App. L (MATLAB) + App. M (DYNARE) + App. N (DSGE) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P8 | Cap. 9 — Neoclassical exogenous growth | Solow-Swan | [ ] | App. O (MATLAB) | [ ] | [ ] | [ ] | [ ] | [ ] |
| P9 | Cap. 10 — Ramsey's optimal growth | Ramsey | [ ] | App. P (DYNARE) | [ ] | [ ] | [ ] | [ ] | [ ] |
| X1 | Extra Cabello — Optimización lineal/no lineal | (a definir con JMC) | n/a | n/a | [ ] | [ ] | [ ] | [ ] | [ ] |
| X2 | Extra Cabello — Matemáticas financieras (rentas, amortización) | (a definir con JMC) | n/a | n/a | [ ] | [ ] | [ ] | [ ] | [ ] |
| X3 | Extra Cabello — SymPy en métodos matemáticos | (a definir con JMC) | n/a | n/a | [ ] | [ ] | [ ] | [ ] | [ ] |

**Regla de oro**: una práctica solo se "cierra" cuando un alumno externo al equipo la ejecuta en Colab y reproduce los gráficos esperados sin ayuda. Esto se valida en la **Fase II piloto**.

---

## 3. FASE I — DISEÑO DE MATERIALES, PROMPTING Y ENTORNOS (Meses 1-6)

> Objetivo: tener antes del Mes 7 **todas las prácticas P0-P9 en Excel + Python listas para usar en aula**, y **P0-P3 también en Julia** (las del Nivel 3 más complejas, P4-P9 en Julia, se terminan en S2). Catálogo de prompts publicado. Web abierta.

### 3.1. Hito 1 — Compilación y refinamiento de scripts base

#### 3.1.1. Material original del libro

- [ ] Pedir a Aneli el `.docx` del libro completo y la carpeta de hojas de cálculo originales (`ICM-1-xls`, `ICM-2-xls`, ..., `ICM-10-xls`) (AB → AR)
- [ ] Subir las hojas de cálculo a `practicas/0X/excel/` con README explicando qué hace cada celda clave
- [ ] Recopilar los códigos de los apéndices del libro (MATLAB + DYNARE) en `practicas/0X/referencia/` — son nuestro oráculo numérico
- [ ] Para cada capítulo, listar **outputs esperados** (valores estado estacionario, gráficas) que cualquier portabilidad debe reproducir → `practicas/0X/oraculo.md`

#### 3.1.2. Portar capítulos a Python — bloque básico (Meses 1-3)

> Orden de ataque, de menor a mayor dificultad:

- [x] **P0** Cap. 1 — sistema dinámico genérico (AR) — completado 2026-06-17 (ver [`docs/WIKI.md`](docs/WIKI.md))
  - [x] Notebook Colab con celdas de teoría → calibración → solución → gráficas
  - [x] Validación cruzada con App. B MATLAB del libro (y App. C DYNARE, caso punto de silla)
  - [x] Widget `ipywidgets` para que el alumno mueva parámetros en vivo
- [ ] **P1** Cap. 2 — IS-LM dinámico (AB + AR)
  - [ ] Notebook con shock monetario y fiscal en `scipy.integrate.solve_ivp`
  - [ ] Diagrama de fase generado con `matplotlib`
  - [ ] Verificación contra App. D + App. E (DYNARE)
- [ ] **P2** Cap. 3 — Overshooting de Dornbusch (AB + AR)
  - [ ] Notebook con shock monetario permanente
  - [ ] Reproducir figura de overshooting del libro al pixel

#### 3.1.3. Portar capítulos a Python — bloque DGE (Meses 3-5)

- [ ] **P3** Cap. 4 — Consumo-ahorro (AB + JLT + AR)
  - [ ] Resolver con `scipy.optimize.fsolve` replicando Newton del App. H
  - [ ] Versión alternativa con `cvxpy` para que el alumno vea el problema como optimización
- [ ] **P4** Cap. 5 — Consumo-ocio (JLT + AR)
- [ ] **P5** Cap. 6 — Gobierno y fiscalidad (JLT + AR)
- [ ] **P6** Cap. 7 — Tobin Q (JLT + AR)
- [ ] **P7** Cap. 8 — DGE básico (JLT + AB + AR) — pieza central, máximo cuidado

#### 3.1.4. Portar capítulos a Python — bloque crecimiento (Mes 5-6)

- [ ] **P8** Cap. 9 — Solow-Swan (AR)
  - [ ] Versión limpia traducida de App. O
  - [ ] Shocks de tasa de ahorro y de crecimiento poblacional
- [ ] **P9** Cap. 10 — Ramsey (JLT + AR) — usar `scipy.integrate.solve_bvp` para el problema de contorno

#### 3.1.5. Portar a Julia — primer empujón (Mes 6)

- [ ] **P0, P1, P8** en Julia (las tres más sencillas como prueba de concepto)
  - [ ] Comparar tiempos y elegancia frente a Python en una "nota técnica" → entra como sección del manual

#### 3.1.6. Modelos extra de Cabello (Meses 4-6)

- [ ] Reunión específica con JMC para definir X1, X2, X3 (modelos exactos, dataset)
- [ ] Acta con decisión sobre qué SymPy se enseña y a qué grupo
- [ ] X1: Optimización con `scipy.optimize.linprog` + versión SymPy + versión Julia (`JuMP.jl`)
- [ ] X2: Matemáticas financieras (rentas, TIR/VAN, amortización francesa/americana) en Python con `numpy_financial`
- [ ] X3: Notebook didáctico SymPy → derivadas, sistemas no lineales, transformada de Laplace

**DOCUMENTACIÓN PARALELA (Hito 1):**
- [ ] `docs/manual-prompting/0X-cap-Y.md`: para cada capítulo, **explicación didáctica** de la portabilidad (qué fue fácil, qué fue trampa)
- [ ] `docs/decisiones-tecnicas.md`: por qué `scipy` y no `casadi`, por qué `Plots.jl` y no `Makie.jl`, etc.
- [ ] `docs/guia-estilo-codigo.md`: guía de estilo en 2 páginas orientada al alumno, con ejemplos ✅ correcto / ❌ incorrecto. Se distribuye en la Sesión 0 del piloto.

### 3.2. Hito 2 — Guion de laboratorio: del libro de química al notebook

> Este es **tu aportación diferencial como PTGAS**. Adaptamos el formato físico de los guiones de Química Orgánica al laboratorio virtual.

#### 3.2.1. Plantilla maestra de guion de laboratorio

- [ ] Crear `practicas/_plantilla/GUION.md` con secciones obligatorias:
  - [ ] **Título y código** (ej. `LAB-P1: Respuesta dinámica del modelo IS-LM ante shock monetario`)
  - [ ] **Objetivos didácticos** (3 máximo, verbos de Bloom)
  - [ ] **Conocimientos previos requeridos** (con enlaces a otras prácticas)
  - [ ] **Tiempo estimado** y nivel (Grado / Posgrado)
  - [ ] **"Reactivos" digitales** (librerías, versiones, dataset)
  - [ ] **Procedimiento paso a paso** (numerado, una acción por paso)
  - [ ] **Reacciones esperadas** (valores numéricos, formas de las curvas, comportamientos límite)
  - [ ] **Posibles "accidentes de laboratorio"** (errores típicos del alumno y cómo identificarlos)
  - [ ] **Cuestionario de bitácora** (preguntas que el alumno responde en su cuaderno)
  - [ ] **Variantes / extensiones para ABP**
  - [ ] **Referencias** (capítulo del libro, lecturas adicionales)
- [ ] Validar la plantilla con un guion de Química Orgánica real (AR) para confirmar paralelismo
- [ ] Aplicar la plantilla a P0, P1, P8 como prueba piloto
- [ ] Iterar y aplicar al resto

#### 3.2.2. Sistema de identificación y trazabilidad

- [ ] Cada guion lleva ID único `LAB-PX-vY.Z` (versión semántica)
- [ ] Cambios significativos suben Y (minor) o Z (patch); reescritura total sube X (no debería pasar)
- [ ] `CHANGELOG.md` por práctica

**DOCUMENTACIÓN PARALELA (Hito 2):**
- [ ] `docs/metodologia-laboratorio.md`: artículo corto (3-4 páginas) explicando el paralelismo química→economía con ejemplos. Es el **borrador 0 de la primera publicación**.

### 3.3. Hito 3 — Catálogo de prompts y web del proyecto

#### 3.3.1. Framework de prompting estructurado

Diseño en 3 capas:

**Capa A — System prompts institucionales** (uno por asignatura)
- [ ] `prompts/system-prompts/intro-macro.md`
- [ ] `prompts/system-prompts/macro-intermedia.md`
- [ ] `prompts/system-prompts/macro-avanzada.md`
- [ ] `prompts/system-prompts/macro-computacional.md`
- [ ] `prompts/system-prompts/teoria-crecimiento.md`
- [ ] `prompts/system-prompts/optimizacion.md`
- [ ] `prompts/system-prompts/metodos-matematicos.md`
- [ ] `prompts/system-prompts/matematicas-financieras.md`

Cada system prompt incluye obligatoriamente:
- Rol del asistente ("tutor socrático, no resolutor")
- Restricciones (no dar la respuesta directa, hacer preguntas guía)
- Estilo (citar el capítulo del libro pertinente)
- Tono (formal pero accesible, en español)
- Cláusula anti-alucinación matemática (ver §8.3)
- **Cláusula de buenas prácticas**: *"Todo el código que escribas sigue PEP 8 (Python) o BlueStyle (Julia). Las funciones llevan docstring. La lógica del modelo se separa de la visualización. Si el alumno te pide un bloque monolítico de 100 líneas, pregúntale primero cómo lo dividiría en funciones."*

**Capa B — Megaprompts por práctica**
- [ ] `prompts/megaprompts/LAB-PX/depuracion-codigo.md`
- [ ] `prompts/megaprompts/LAB-PX/explicacion-modelo.md`
- [ ] `prompts/megaprompts/LAB-PX/interpretacion-resultados.md`
- [ ] `prompts/megaprompts/LAB-PX/variantes-abp.md`

**Capa C — Mini-prompts de bolsillo** (chuleta para el alumno)
- [ ] `prompts/catalogo-tutor/quick-reference.pdf` — una página

#### 3.3.2. Web pública en GitHub Pages

- [ ] Tema MkDocs Material o Quarto (Quarto encaja mejor con notebooks)
- [ ] Estructura: Home / Prácticas / Manual prompting / Equipo / Publicaciones / Contacto
- [ ] Cada práctica navegable con renderizado del notebook + descarga `.ipynb` y `.xlsx`
- [ ] Botón "Abrir en Colab" en cada notebook (badge oficial)
- [ ] Buscador integrado
- [ ] Analytics privacy-friendly (Plausible o Umami, no GA)

**DOCUMENTACIÓN PARALELA (Hito 3):**
- [ ] `docs/manual-prompting/00-introduccion.md`: marco teórico del prompting científico → segunda contribución publicable
- [ ] Listar revistas objetivo concretas con deadlines: *e-pública*, *Journal of Economic Education*, *Computers & Education*

### 3.4. CHECKPOINT FIN DE FASE I (Mes 6)

- [ ] Reunión de equipo con review honesto: ¿qué hitos están realmente cerrados?
- [ ] Demo de 30 min con AB y JLT navegando la web pública
- [ ] **Audit de calidad de código** (AR): ejecutar `black --check`, `ruff check` y `pytest` en todo el repo — el resultado entra en el acta del checkpoint
- [ ] Confirmar que todos los notebooks pasan "Restart & Run All" sin error
- [ ] Confirmar que `src/macroaicomp` y `src/MacroAIComp` están instalables y con coverage ≥ 80%
- [ ] **Decisión Go/No-Go para empezar piloto en aula en S2** — si algo no está listo, decidir si se hace o se posterga

---

## 4. FASE II — IMPLEMENTACIÓN PILOTO I: EXCEL + PYTHON EN AULA (Meses 7-12)

> Objetivo: probar el Nivel 1 (Excel) y Nivel 2 (Python/Colab) en asignaturas de grado durante 1 cuatrimestre. Recoger datos.

### 4.1. Hito 4 — Despliegue de Nivel 1 y Nivel 2 en grado

#### 4.1.1. Selección de asignaturas piloto (Mes 7)

- [ ] AB y JLT eligen 2-3 asignaturas para el piloto (recomendación: una de Grado básica + una intermedia)
- [ ] Para cada asignatura: identificar 3-4 prácticas concretas a inyectar en el cronograma docente
- [ ] Acordar **grupo control** (grupo del mismo curso sin las prácticas) para comparar después → **clave para el KPI de mejora del 15%**

#### 4.1.2. Onboarding del alumnado (primera semana de docencia)

- [ ] Sesión 0 de 1h: "Qué es Colab, qué es Julia, qué es un cuaderno de bitácora"
- [ ] Test rápido de competencias previas (10 ítems, pre-test DigComp) — recopilamos en Excel anonimizado
- [ ] Cada alumno crea su carpeta `bitacoras/grupo-X/alumno-NN/` en un Drive compartido o repo privado de aula
- [ ] Distribuir el catálogo de prompts en PDF (Capa C)

#### 4.1.3. Sesiones prácticas (semanas 2-N)

- [ ] Cada sesión sigue el ritual: **(1)** pre-lab (vídeo o lectura de aula invertida) → **(2)** apertura de guion → **(3)** ejecución con bitácora abierta → **(4)** cierre con cuestionario de bitácora → **(5)** entrega
- [ ] Asistencia técnica del PTGAS al menos en las 2 primeras sesiones por grupo (presencial o vía Discord/Slack)
- [ ] Recopilar **incidencias técnicas** en `evaluacion/incidencias-piloto-1.md` (qué falla, en qué Colab/SO, etc.) — feedback directo para mejorar las prácticas

### 4.2. Hito 5 — Talleres co-curriculares

- [ ] Diseño de un curso voluntario de 12h: "Uso de IA y Programación Científica en Ciencias Cuantitativas"
- [ ] Captar 30-40 alumnos vía email institucional y redes UMA
- [ ] Repartir en 6 sesiones de 2h durante el cuatrimestre
- [ ] Acreditación: certificado de aprovechamiento de la UMA si se cumple 80% asistencia + entrega final
- [ ] Material del taller integrable al repo (refuerza el Open Educational Resources)

### 4.3. Hito 6 — Primera encuesta de evaluación

#### 4.3.1. Diseño (Mes 7-8, antes del piloto)

- [ ] **Pre-test** (semana 0): autopercepción competencias DigComp + competencia matemática + actitud hacia IA (escala Likert 1-5)
- [ ] Items obligatorios para que sirva en publicación científica (validar Cronbach >0.7)
- [ ] JMC valida estadísticamente el diseño antes de aplicar
- [ ] Aprobación del Comité de Ética / Bioética UMA si aplica (datos de menores no; pero datos académicos sí merecen consentimiento informado)

#### 4.3.2. Aplicación y análisis (Mes 11-12)

- [ ] **Post-test** (última semana docencia)
- [ ] Análisis estadístico por JMC con `R` o `statsmodels`:
  - Diferencia pre-post (Wilcoxon o t pareado según normalidad)
  - Comparación con grupo control (Mann-Whitney o t independiente)
  - Tamaño del efecto (Cohen's d)
- [ ] Informe interno en `evaluacion/informes/piloto-1-Sxx.pdf`

### 4.4. CHECKPOINT FIN DE FASE II (Mes 12)

- [ ] Workshop interno (medio día) con todos los hallazgos del piloto
- [ ] Identificar **las 3 prácticas mejor evaluadas y las 3 peor evaluadas** — refactorizar estas últimas antes de Fase III
- [ ] **Borrador 1 del primer paper** (basado en metodología de laboratorio + piloto I) — enviar a *e-pública* en Mes 13-14

**DOCUMENTACIÓN PARALELA (Fase II):**
- [ ] `evaluacion/dataset-piloto-1/` con datos anonimizados (cumpliendo RGPD)
- [ ] `docs/lecciones-aprendidas-piloto-1.md`

---

## 5. FASE III — IMPLEMENTACIÓN PILOTO II: JULIA Y ABP AVANZADO (Meses 13-18)

> Objetivo: subir al Nivel 3 (Julia) en asignaturas avanzadas y posgrado. Introducir Aprendizaje Basado en Proyectos con IA.

### 5.1. Hito 7 — Despliegue de Julia en cursos superiores

#### 5.1.1. Cerrar el portado a Julia de P4-P9 (Meses 13-14)

> Trabajo pendiente de la Fase I, ahora con urgencia porque entra en docencia.

- [ ] **P4** Cap. 5 — Consumo-ocio en Julia (`Optim.jl`)
- [ ] **P5** Cap. 6 — Gobierno fiscal en Julia
- [ ] **P6** Cap. 7 — Tobin Q en Julia (`DifferentialEquations.jl` para el ODE)
- [ ] **P7** Cap. 8 — DGE básico en Julia (`NLsolve.jl` para el sistema no lineal)
- [ ] **P9** Cap. 10 — Ramsey en Julia (`BoundaryValueDiffEq.jl`)
- [ ] **Bonus Nivel 3**: introducir DSGE estocástico con `DynamicSSE.jl` o portar Appendix N
- [ ] Cada notebook Julia con benchmark de velocidad frente al equivalente Python → tabla en el manual

#### 5.1.2. Despliegue en aula avanzada

- [ ] Asignaturas piloto Nivel 3: Macro Avanzada, Macro Computacional, Teoría del Crecimiento, Posgrado
- [ ] **Estrategia "puente Python→Julia"**: las primeras 2 sesiones se compara código equivalente lado a lado para que el alumno vea que es el mismo modelo
- [ ] Asistencia técnica del PTGAS en las 3 primeras sesiones

### 5.2. Hito 8 — Aprendizaje Basado en Proyectos con IA

#### 5.2.1. Diseño del banco de retos ABP

- [ ] Catálogo de **12 retos** (1 por mes de docencia) en `practicas/abp/`. Ejemplos:
  - "Calibrar un modelo Ramsey para reproducir el ciclo económico español 2008-2024"
  - "Simular el impacto de una reforma fiscal en un DGE básico"
  - "Comparar 3 reglas de política monetaria en un IS-LM dinámico ante shock energético"
  - "Optimización de cartera con SymPy + JuMP (X1)"
  - "Modelo financiero de hipoteca variable vs fija (X2)"
- [ ] Cada reto: enunciado + dataset + rúbrica + ejemplo de solución (sólo para profesores)

#### 5.2.2. Rúbricas ABP (JMC + AR)

- [ ] Rúbrica de 5 ejes, 4 niveles (insuficiente, en desarrollo, competente, excelente):
  1. **Rigor del modelo** (fundamento teórico correcto, parámetros calibrados y justificados)
  2. **Calidad del código** — eje principal del §0.3:
     - Insuficiente: código en un solo bloque, sin funciones, sin comentarios, no ejecuta limpio
     - En desarrollo: funciones presentes pero sin docstring ni type hints; mezcla lógica y visualización
     - Competente: código PEP 8 / BlueStyle, funciones con docstring, lógica separada de plots, ejecuta "Restart & Run All" sin errores
     - Excelente: módulo en `src/` reutilizable, tests unitarios, README de práctica, nombres de variables coherentes con la notación del libro
  3. **Higiene IA** (uso crítico, prompts trazados en bitácora, verificación manual de al menos un resultado clave)
  4. **Reproducibilidad** (otro alumno clona el repo, ejecuta el notebook y obtiene los mismos resultados sin tocar nada)
  5. **Comunicación de resultados** (gráficas con títulos/ejes/leyenda, interpretación económica clara, conclusiones conectadas con la teoría del curso)
- [ ] Calibración entre evaluadores: AB, JLT, JMC y AR puntúan 3 trabajos piloto y se discute hasta consenso

### 5.3. Hito 9 — Evaluación formativa continua

- [ ] **Bitácoras revisadas en cortes mensuales** con feedback breve al alumno (1 párrafo)
- [ ] Mini-encuestas (5 ítems, 2 min) cada mes para detectar atascos tempranos
- [ ] Reuniones de equipo bimensuales para ajustar guiones si emergen problemas
- [ ] Grupo focal cualitativo de 8-10 alumnos al final del cuatrimestre (entrevista de 45 min, transcripción y análisis temático)

### 5.4. CHECKPOINT FIN DE FASE III (Mes 18)

- [ ] Repositorio cerrado en su versión 1.0 (release con DOI Zenodo)
- [ ] Manuales en abierto en versión preliminar (PDF + web)
- [ ] Datos piloto II analizados
- [ ] **Borrador 2 del segundo paper** (Julia vs Python en docencia económica, o ABP+IA)

**DOCUMENTACIÓN PARALELA (Fase III):**
- [ ] `evaluacion/dataset-piloto-2/`
- [ ] `docs/lecciones-aprendidas-piloto-2.md`
- [ ] `docs/comparativa-python-julia.md` (datos del benchmark)

---

## 6. FASE IV — EVALUACIÓN, TRANSFERENCIA, PUBLICACIONES Y CIERRE (Meses 19-24)

### 6.1. Hito 10 — Análisis de rendimiento académico

- [ ] Comparación de calificaciones del grupo experimental vs grupos históricos de los últimos 3 cursos
- [ ] Test estadístico (ANOVA o no paramétrico según distribución)
- [ ] **Objetivo declarado a INNOVA26**: +15% en preguntas cuantitativas. Reportar honestamente aunque no se alcance.
- [ ] Tasa de abandono comparada con cohorte histórica
- [ ] Análisis de uso del repositorio: clones, estrellas, países (datos GitHub Insights)
- [ ] Informe en `evaluacion/informe-final-rendimiento.pdf`

### 6.2. Hito 11 — Publicaciones científicas

Plan de publicación (3 papers como mínimo según presupuesto APC):

- [ ] **Paper 1** — *e-pública* o similar en español: "Adaptación de la metodología de laboratorio experimental al aula de Macroeconomía Computacional con IA" — autores: AR, AB, JLT
- [ ] **Paper 2** — *Journal of Economic Education*: "From Excel to Julia: an incremental computational pipeline for teaching dynamic macroeconomics with AI tutors" — autores: AB, JLT, AR, JMC
- [ ] **Paper 3** — *Computers & Education* o *International Journal of Educational Technology in Higher Education*: "AI as a scientific copilot: evaluating prompting frameworks for economics undergraduates" — autores: AR, JMC, AB
- [ ] Preprints en SSRN / EconStor antes de envío
- [ ] Releases con DOI separados para los datasets de cada paper

### 6.3. Hito 12 — Memoria técnica final y seminario

- [ ] **Seminario abierto en la UMA** (mes 22): medio día con 4 charlas:
  1. AB — Visión del proyecto y resultados
  2. AR — La metodología de laboratorio en aulas no experimentales
  3. JLT — Cómo cambian los exámenes cuando los alumnos saben Julia
  4. JMC — Lo que dicen los datos
- [ ] Vídeo del seminario en abierto (YouTube/Vimeo + bajo CC BY)
- [ ] **Memoria técnica final** ante Vicerrectorado y Santander:
  - Resumen ejecutivo (2 pág)
  - Cumplimiento de objetivos OE1-OE8 (tabla)
  - KPIs cuantitativos con dashboard
  - Recursos consumidos vs presupuesto
  - Impacto interdepartamental (testimonios CE Económicas + Facultad Ciencias)
  - Próximos pasos / sostenibilidad
- [ ] Presentación de 20 min ante el comité INNOVA26

### 6.4. CHECKLIST FINAL DE CIERRE (último mes)

- [ ] Release `v2.0` del repo con DOI definitivo
- [ ] Archivo de los datasets en Zenodo / Figshare con licencia CC
- [ ] Traspaso del mantenimiento del repo a la UMA institucional (responsable docente identificado)
- [ ] Manual de prompting en versión definitiva, ISBN si se publica como libro abierto en *Vernon Press* o editorial UMA
- [ ] Acta de cierre del proyecto firmada por todo el equipo
- [ ] Justificación económica completa al Vicerrectorado

---

## 7. FRAMEWORK DE PROMPTING (transversal — núcleo PTGAS)

> Esta sección expande el OE5 y es uno de los entregables más visibles del PTGAS. Hay que tratarlo con la misma seriedad que un protocolo de laboratorio: si la receta es mala, los resultados son malos.

### 7.1. Principios

- [ ] La IA es **tutor**, no resolutor. Los prompts están diseñados para hacer pensar, no para entregar respuesta.
- [ ] **Trazabilidad obligatoria**: cada vez que un alumno usa IA en una práctica, copia el prompt y la respuesta a su bitácora con timestamp.
- [ ] **Higiene matemática**: la IA puede equivocarse. La bitácora exige al alumno **verificar al menos un cálculo a mano o en Excel** antes de aceptar la respuesta.

### 7.2. Estructura tipo del megaprompt (Capa B)

```
[CONTEXTO]
Eres un tutor de macroeconomía computacional especializado en el modelo {NOMBRE_MODELO}
del capítulo {N} del libro "Introduction to Computational Macroeconomics" de Bongers,
Gómez y Torres (Vernon Press, 2019).

[ROL]
Tu objetivo es guiar al estudiante a través de pasos socráticos para que él mismo
resuelva el modelo. No le entregues la solución directa.

[RESTRICCIONES]
- Pregunta primero qué ha intentado y qué error obtiene.
- Si pide código, escribe pseudocódigo paso a paso antes de Python/Julia.
- Si detectas una pregunta que copia literalmente el enunciado, recuérdale el cuestionario
  de bitácora antes de avanzar.
- Nunca inventes parámetros. Si faltan, pídelos.
- Si la pregunta excede el modelo del capítulo {N}, dilo explícitamente.

[ESTILO]
Idioma: {ES/EN según asignatura}.
Tono: formal cercano, profesoral.
Formato: respuestas cortas, máximo 200 palabras antes de devolver el turno al alumno.

[VERIFICACIÓN]
Recuerda al alumno verificar cualquier número con Excel o cálculo manual y registrarlo
en su bitácora (sección "Higiene IA").
```

### 7.3. Cláusula anti-alucinación matemática

- [ ] Prompts incluyen: *"Si tu respuesta contiene una expresión matemática que no figura en el libro citado, márcala explícitamente como 'derivación propia (no verificada)' y sugiere al alumno comprobarla con SymPy."*
- [ ] Documentar 5 ejemplos reales de alucinación que detectemos durante el desarrollo → entrada principal del Paper 3

### 7.4. Mantenimiento del catálogo

- [ ] Versión semántica de prompts (`v1.0`, `v1.1`...)
- [ ] Cada cambio en un megaprompt requiere PR con tests A/B mínimos (probar el prompt con 5 preguntas tipo y comparar respuestas antes/después)
- [ ] Revisión trimestral por AR + AB

---

## 8. PROTOCOLO DE CUADERNO DE BITÁCORA DIGITAL (transversal)

### 8.1. Plantilla

- [ ] Crear `bitacora/plantilla-bitacora.ipynb` con secciones:
  1. **Cabecera**: nombre, fecha, ID práctica, versión del guion usada
  2. **Hipótesis de partida** (predicción cualitativa antes de ejecutar)
  3. **Parámetros calibrados** (tabla con justificación)
  4. **Ejecución y observaciones** (celdas de código + comentario inmediato)
  5. **Anomalías detectadas** (sección obligatoria — si vacía, también)
  6. **Sección "Higiene IA"** (todos los prompts usados + verificación cruzada)
  7. **Reflexión final** (¿coincidió con la hipótesis? ¿por qué?)
  8. **Firma digital** (commit hash del notebook si va por repo, o timestamp+hash si Drive)

### 8.2. Convenciones de entrega

- [ ] Los alumnos entregan `.ipynb` ejecutado (con outputs) + PDF generado automáticamente
- [ ] Tamaño máximo del repo de bitácoras por alumno (200 MB) — política contra subir datasets enormes
- [ ] Datos privados se enlazan, no se suben

### 8.3. Evaluación de bitácora

- [ ] La bitácora es **30% de la nota de la práctica** en las asignaturas piloto (consensuar con AB y JLT)
- [ ] Rúbrica específica de bitácora en `evaluacion/rubricas/bitacora.md`

---

## 9. RÚBRICAS Y EVALUACIÓN COMPETENCIAL (responsable: JMC, soporte AR)

- [ ] Rúbrica de **bitácora** (§8.3)
- [ ] Rúbrica de **práctica de laboratorio** (correctitud técnica + reproducibilidad)
- [ ] Rúbrica de **proyecto ABP** (§5.2.2)
- [ ] Rúbrica de **competencia digital** (alineada con DigComp 2.2: Information & Data Literacy, Communication, Digital Content Creation, Safety, Problem Solving)
- [ ] Rúbrica de **uso crítico de IA** (instrumento original del proyecto, candidato a publicación)
- [ ] **Banco de items** del cuestionario competencial validado por JMC con análisis factorial

---

## 10. KPIs Y DASHBOARD DE SEGUIMIENTO

Construcción de un panel ligero (puede ser un notebook que se ejecuta mensual o un Streamlit/Quarto dashboard en GitHub Pages):

| KPI | Fuente del dato | Frecuencia | Meta declarada en propuesta |
|---|---|---|---|
| Calificación media en preguntas cuantitativas | Actas asignatura | Cuatrimestral | +15% vs histórico |
| Tasa de abandono | Secretaría / SIIU | Cuatrimestral | Reducción |
| Estrellas y clones del repo | GitHub API | Semanal | Crecimiento sostenido |
| Visitas únicas web | Analytics | Mensual | Crecimiento sostenido |
| Cuestionario DigComp (autopercepción) | Encuesta pre/post | Cuatrimestral | Mejora significativa |
| Bitácoras entregadas a tiempo | Repo alumnos | Por sesión | >80% |
| Incidencias técnicas reportadas | Issue tracker repo | Continuo | Decreciente |
| Citas / descargas papers | Google Scholar / repos | Semestral | n/a (registro) |

- [ ] Construir `evaluacion/dashboard-kpi/` con notebook que pinta todos los KPIs y se actualiza con un workflow nocturno de GitHub Actions
- [ ] Página pública en la web (subset de KPIs apropiado para publicar)

---

## 11. PLAN DE DIFUSIÓN MÁS DETALLADO (cubre OE8)

### 11.1. Congresos objetivo (presupuesto B — 1.425 €)

- [ ] **Año 1**: *Jornadas de Docencia en Economía* (España) — comunicación oral de Hito 1+2
- [ ] **Año 2**: *Congreso Internacional de Innovación Docente Universitaria* (CIIDU)
- [ ] **Año 2**: encuentro internacional con foco IA en educación superior (EDULEARN, ICERI o similar) si el presupuesto lo permite
- [ ] **Año 2**: comunicación en la **Asociación Española de Economía** (jornadas docentes)

### 11.2. Redes y comunidad

- [ ] Cuenta del proyecto en Bluesky / Mastodon (científicas) con anuncios de releases
- [ ] Lista de correo de profesores interesados en replicar (alta vía formulario en la web)
- [ ] Grupo de Discord o foro Discourse para preguntas técnicas de docentes que adopten el material

### 11.3. Open Educational Resources

- [ ] Subir todos los materiales también a **MERLOT** y **OER Commons**
- [ ] Buscar federación con el **portal RIUMA** de la UMA

---

## 12. RIESGOS Y PLAN DE MITIGACIÓN

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Algún capítulo del libro no se porta bien a Julia | Media | Medio | Tener siempre la versión Python como red de seguridad; documentar honestamente la limitación |
| Alumnos sin equipos suficientes | Media | Alto | Todo funciona en Colab gratuito; reservar un aula informática para fallos puntuales |
| Encuestas con n bajo (no significativo) | Media | Alto | Diseñar la encuesta para que también sirva con n=30; combinar cuantitativo con cualitativo |
| Cambio en la política de Anthropic/OpenAI durante el proyecto | Alta | Medio | Probar prompts en al menos 2 modelos distintos; tener fallback con modelo abierto (Llama, Mistral) |
| Salida de algún miembro del equipo | Baja | Alto | Documentación exhaustiva; cada práctica tiene 2 responsables nominales |
| Problemas con consentimiento informado / RGPD en encuestas | Media | Alto | Trabajar con el DPD de la UMA desde Mes 1 |
| Retraso en la financiación efectiva | Media | Medio | Las herramientas core (Colab, GitHub, Julia, Python) son gratuitas; el grueso del trabajo no depende del dinero |

- [ ] Revisar esta tabla trimestralmente y añadir nuevos riesgos detectados

---

## 13. REUNIONES Y GOBERNANZA

### 13.1. Cadencia

- [ ] **Quincenal AR↔AB** (45 min, online): estado técnico, bloqueos
- [ ] **Mensual equipo completo** (1h, presencial cuando se pueda): hitos, decisiones
- [ ] **Trimestral con Cabello (JMC)** específica para evaluación y estadística
- [ ] **Anual con dirección de Departamento** y representantes de Vicerrectorado: presentación de progreso

### 13.2. Plantilla de acta

`docs/actas/AAAA-MM-DD-tipo.md`:

```
# Acta {tipo} — {fecha}
Asistentes: {lista}
Ausentes: {lista}

## Estado de hitos abiertos
- [hito]: estado y bloqueos

## Decisiones tomadas
1. ...
2. ...

## Acciones (con responsable y deadline)
- [ ] {acción} — @{persona} — para {fecha}

## Próxima reunión
{fecha y hora}
```

- [ ] Cada acta se commitea al repo al cierre de la reunión

---

## 14. SOSTENIBILIDAD POST-PROYECTO

- [ ] **Plan de mantenimiento** del repo: responsable docente designado tras Mes 24
- [ ] **Acuerdo de coautoría** para futuras evoluciones (Mes 22): cómo se gestionan PRs externos, cómo se acepta nuevo profesorado al núcleo
- [ ] **Vías de continuidad**: convocatoria INNOVA siguiente, búsqueda de financiación europea (Erasmus+ KA2, NextGenerationEU TF/RD para digitalización docente)
- [ ] **Integración curricular permanente**: propuesta formal a Comisiones de Grado para que las prácticas figuren en las guías docentes oficiales

---

## 15. APÉNDICE A — CALENDARIO RESUMIDO (vista linealizada)

```
2026  NOV  -- M01  Fase I arranca · Hito 1.1 (Cap 1-3 Python)
      DIC  -- M02  Hito 1.2 (Cap 4-6 Python)
2027  ENE  -- M03  Hito 1.3 (Cap 7-8 Python)
      FEB  -- M04  Hito 1.4 (Cap 9-10 Python) + Cabello X1
      MAR  -- M05  Hito 1.5 (Julia P0-P3) + Cabello X2-X3
      ABR  -- M06  Hito 2 (Guion plantilla) + Hito 3 (Prompts + web) · CHECKPOINT
      MAY  -- M07  Fase II arranca · Onboarding alumnos
      JUN  -- M08  Sesiones piloto 1 + Taller co-curricular
      JUL  -- M09  (descanso parcial) revisión incidencias
      AGO  -- M10  Análisis pre-test
      SEP  -- M11  Continuación piloto / inicio nuevo curso
      OCT  -- M12  Post-test piloto I · CHECKPOINT · Paper 1 borrador
      NOV  -- M13  Fase III arranca · Julia P4-P7
      DIC  -- M14  Julia P9 + DSGE opcional
2028  ENE  -- M15  Despliegue Julia en avanzada/posgrado
      FEB  -- M16  ABP banco de retos lanzado
      MAR  -- M17  Evaluación formativa intermedia
      ABR  -- M18  CHECKPOINT · Paper 2 borrador
      MAY  -- M19  Fase IV · Análisis rendimiento
      JUN  -- M20  Submission Paper 1
      JUL  -- M21  Submission Paper 2 · Manual final
      AGO  -- M22  Seminario UMA · Vídeo
      SEP  -- M23  Memoria técnica final
      OCT  -- M24  CIERRE · Release v2.0 con DOI · Acta final
```

---

## 16. APÉNDICE B — CHECKLIST RÁPIDA "ESTOY EMPEZANDO HOY"

Si vuelves a este documento y no sabes por dónde retomar, haz esta secuencia:

1. [ ] Abre el Kanban de GitHub Projects → mira la columna `En curso`
2. [ ] Lee la última acta en `docs/actas/`
3. [ ] Revisa los issues abiertos con etiqueta `prioridad-alta`
4. [ ] Lanza el dashboard de KPIs para ver si hay alguna métrica en rojo
5. [ ] Si todo está limpio, ataca el siguiente checkbox sin marcar de la fase en curso de este plan

---

## 17. CONTACTOS DEL EQUIPO

| Rol | Nombre | Contacto | Especialidad |
|---|---|---|---|
| IP / Coordinadora | Dra. Anelí Bongers | _(rellenar)_ | Macroeconomía computacional, IA en docencia |
| Modelización macro | Dr. José L. Torres Chacón | _(rellenar)_ | DGE, crecimiento, Julia avanzado |
| Evaluación y matemáticas | Dr. José M. Cabello González (Che) | _(rellenar)_ | Evaluación competencial, SymPy, optimización, estadística |
| Técnico / PTGAS | D. Antonio F. Romero Carrasco | _(rellenar)_ | Infraestructura, prompting, bitácoras, control de calidad IA |

---

*Plan vivo. Actualizar este documento es parte del trabajo, no un extra.*
