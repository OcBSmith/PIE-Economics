# Wiki técnica — MACRO-AI-COMP

Registro vivo de **decisiones técnicas, hallazgos sobre el material fuente y
progreso real**, día a día. Complementa al
[`PLAN_MAESTRO_MACRO_AI_COMP.md`](../PLAN_MAESTRO_MACRO_AI_COMP.md) (que
define QUÉ hay que hacer y lleva los checkboxes oficiales) y a las futuras
actas de `docs/actas/` (que documentarán decisiones formales con Aneli,
Torres y Cabello). Esta wiki es el cuaderno de trabajo del PTGAS: el CÓMO,
el POR QUÉ de cada elección, y lo que se va descubriendo sobre la marcha.

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
