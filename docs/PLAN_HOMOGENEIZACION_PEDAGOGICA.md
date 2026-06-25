# Plan de Homogeneización Pedagógica: P1-P9 = plantilla P0

> **Objetivo**: replicar en P1-P9 (Python y Julia) lo ya hecho en P0 —
> rigor económico (oráculo visible en el notebook) + comentarios de
> programación (QUÉ/POR QUÉ/QUÉ VERÁS, incluida sintaxis) + `GUION.md` por
> práctica — usando P0 como plantilla de referencia (Decisión técnica #7,
> `docs/WIKI.md`). Mismo espíritu que `docs/PLAN_HOMOGENEIZACION_JULIA.md`
> (ya cerrado), pero para el eje pedagógico en vez del eje Julia↔Python.

---

## ESTADO — EMPEZAR AQUÍ

**COMPLETO.** P0 completo (referencia, no tocar salvo bugs reales) y
bloques A-G todos `[x]`, incluido el Bloque D (comentarios de programación),
que se dio como "diferido" en la sesión 23 (2026-06-22) pero se terminó
después en la sesión 23-24 — ver la cabecera del propio Bloque D más abajo.
Corregido este párrafo el 2026-06-25 porque seguía describiendo el estado a
mitad de sesión en vez del cierre real. Ver `git log` y `docs/WIKI.md` para
el detalle completo.

---

## Hallazgo de partida (cambia el alcance frente a lo que parecía a simple vista)

- **Solo P0 y P1 tienen `oraculo.md`.** P2-P9 no lo tienen. Pero los
  valores numéricos **ya existen**, hardcodeados con buena precisión, en
  `tests/python/test_*.py` (confirmado leyendo `test_dornbusch.py`: estado
  estacionario, autovalores y trayectoria de shock, con comentarios que
  citan el libro). Crear el oráculo de P2-P9 es sobre todo **transcribir
  esos tests** + citar el apéndice correspondiente, no re-derivar desde
  cero la economía.
- **P2-P9 (Python) no tienen NINGUNA celda de verificación real** (ni
  `assert` ni comparación numérica) contra el libro — solo simulan y
  grafican. P0 y P1 sí la tienen.
- **"dummies" sigue en el título de la guía rápida** de los 18 notebooks
  restantes (confirmado por grep) — mismo arreglo que ya se hizo en P0
  ("GUÍA RÁPIDA DE INICIO").
- **Generadores**: P1 y P2 (Python) son notebooks editados a mano, como
  P0 — cualquier cambio va directo al `.ipynb`. **P3-P9 (Python)** y
  **P1-P9 (Julia)** SÍ tienen generador (`generate_pX_notebook.py` /
  `generate_pX_julia_notebook.py`) — los cambios van AHÍ, nunca solo al
  `.ipynb` regenerado (bug recurrente ya documentado en memoria y en el
  plan de homogeneización Julia).

| Práctica | Test (fuente del oráculo) | Apéndice del libro | ¿Tiene `oraculo.md`? | Generador Python | Generador Julia |
|---|---|---|---|---|---|
| P1 IS-LM | `test_islm.py` | App. D (MATLAB) + E (DYNARE) | Sí | No (a mano) | `generate_p1_julia_notebook.py` |
| P2 Dornbusch | `test_dornbusch.py` | App. F (DYNARE) | No | No (a mano) | `generate_p2_julia_notebook.py` |
| P3 Consumo-ahorro | `test_consumption_savings.py` | App. G (MATLAB) + H (Newton) | No | `generate_p3_notebook.py` | `generate_p3_julia_notebook.py` |
| P4 Consumo-ocio | `test_consumption_leisure.py` | App. I (MATLAB) | No | `generate_p4_notebook.py` | `generate_p4_julia_notebook.py` |
| P5 Gobierno fiscal | `test_fiscal_policy.py` | App. J (MATLAB) | No | `generate_p5_notebook.py` | `generate_p5_julia_notebook.py` |
| P6 Tobin Q | `test_tobin_q.py` | App. K (DYNARE) | No | `generate_p6_notebook.py` | `generate_p6_julia_notebook.py` |
| P7 DGE básico | `test_dge.py` | App. L (MATLAB) + M (DYNARE) + N (DSGE) | No | `generate_p7_notebook.py` | `generate_p7_julia_notebook.py` |
| P8 Solow-Swan | `test_growth.py` | App. O (MATLAB) | No | `generate_p8_notebook.py` | `generate_p8_julia_notebook.py` |
| P9 Ramsey | `test_ramsey.py` | App. P (DYNARE) | No | `generate_p9_notebook.py` | `generate_p9_julia_notebook.py` |

---

## BLOQUE A — Oráculo + verificación real (fundamento, hacer primero)

- [x] A1. P2 (Dornbusch): crear `practicas/02-overshooting-dornbusch/oraculo.md` a partir de `test_dornbusch.py` (SS, autovalores, shock monetario con overshooting) + Apéndice F (DYNARE); añadir celdas `assert`/`@assert` en `python.ipynb` y `julia.ipynb`
- [x] A2. P3 (consumo-ahorro): `oraculo.md` desde `test_consumption_savings.py` + Apéndices G/H; asserts en ambos notebooks
- [x] A3. P4 (consumo-ocio): `oraculo.md` desde `test_consumption_leisure.py` + Apéndice I; asserts
- [x] A4. P5 (gobierno fiscal): `oraculo.md` desde `test_fiscal_policy.py` + Apéndice J; asserts (cuidado: P5 tiene 3 sub-escenarios — lump-sum, distorsionador, Seguridad Social — el oráculo debe cubrir los 3)
- [x] A5. P6 (Tobin Q): `oraculo.md` desde `test_tobin_q.py` + Apéndice K (DYNARE); asserts
- [x] A6. P7 (DGE básico): `oraculo.md` desde `test_dge.py` + Apéndices L/M/N; asserts (cubrir tanto Blanchard-Khan como la simulación no lineal, ya que el notebook compara ambas)
- [x] A7. P8 (Solow-Swan): `oraculo.md` desde `test_growth.py` + Apéndice O; asserts
- [x] A8. P9 (Ramsey): `oraculo.md` desde `test_ramsey.py` + Apéndice P (DYNARE); asserts
- [x] A9. P1 (IS-LM): comprobar si `python.ipynb`/`julia.ipynb` ya verifican contra el `oraculo.md` existente con un `assert` real; si no, añadirlo (no asumir que por tener `oraculo.md` ya está verificado en código)

## BLOQUE B — Tablas de oráculo visibles en el notebook

Depende de A. Para P1-P9: extender (o crear) la celda markdown de
verificación con la tabla completa de `oraculo.md`, igual que las
Secciones 4 y 8 de P0 (que son el modelo a seguir literalmente).

- [x] B1...B9 — una por práctica (P1 a P9)

## BLOQUE C — Wording: quitar "dummies"

Independiente del resto, se puede hacer ya, en paralelo a todo. Cambiar
"GUÍA RÁPIDA PARA DUMMIES" → "GUÍA RÁPIDA DE INICIO" (mismo texto que P0).

- [x] C1...C9 — `python.ipynb` y `julia.ipynb` de cada práctica (18
  archivos). En P3-P9 (Python) y P1-P9 (Julia) editar el **generador**, no
  solo el `.ipynb`; en P1-P2 (Python) editar el `.ipynb` directamente.

## BLOQUE D — Comentarios de programación (el bloque más grande)

No depende de A/B, pero tiene más sentido hacerlo después de B (para
comentar también las celdas de `assert` ya añadidas). Por cada celda de
código: comentarios QUÉ hace / POR QUÉ / QUÉ VERÁS, incluida sintaxis
básica (imports/`using`, structs/dataclasses, indexado 0-based vs.
1-based, f-strings/interpolación, broadcasting, tuplas...) igual que P0.

- [x] D1...D9 — **COMPLETADO** (2026-06-22, Sesión 23-24). Comentarios QUÉ/POR
  QUÉ/QUÉ VERÁS + sintaxis añadidos en los 18 notebooks (P1-P9 × Python/Julia)
  siguiendo los patrones de P0: explicación de imports, dataclasses/structs,
  indexado 0-based vs 1-based, f-strings/interpolación, broadcasting, funciones
  de verificación, widgets y benchmarks. 3 agentes en paralelo + post-procesamiento.

## BLOQUE E — `GUION.md` por práctica

Depende de A (necesita los valores reales del oráculo para "Reacciones
esperadas"). Crear `practicas/0X.../GUION.md` a partir de
`practicas/_plantilla/GUION.md`, con contenido específico de cada modelo:
objetivos con verbos de Bloom, prerrequisitos, accidentes de laboratorio
propios de ESE modelo (no genéricos), 5-6 preguntas de bitácora y 2-3
extensiones para ABP.

- [x] E1...E9

## BLOQUE F — Enlazar el GUION desde cada notebook

Depende de E. Añadir las 2 líneas (bienvenida + conclusión) apuntando a
`GUION.md`, igual que P0 — sin tocar ninguna celda de código.

- [x] F1...F9 — COMPLETADO. P1-P2 y P4-P6 con enlaces en `.ipynb`. P3, P7-P9 notebooks regenerados heredan enlaces vía md_extractor desde los Python. Los `GUION.md` existen en todas las carpetas.

## BLOQUE G — Verificación y cierre (continuo, no al final)

- [x] G1. `nbconvert --to notebook --execute --inplace` en cada notebook
  tras completarlo (leer el log completo, no solo el exit code) —
  verificar práctica por práctica, no esperar a las 9
- [x] G2. Actualizar `PLAN_MAESTRO_MACRO_AI_COMP.md`: columna "Bitácora
  plantilla" de P1-P9 en la tabla §2 a medida que cada `GUION.md` se cree;
  marcar "Aplicar la plantilla a P1, P8" en §3.2.1 cuando les toque
- [x] G3. Actualizar `docs/WIKI.md` con una entrada por práctica o por
  bloque completado (no esperar al final)
- [x] G4. Commits por práctica o por bloque — igual que en la
  homogeneización Julia (14 commits en su momento), no todo de golpe

---

## Orden de ejecución recomendado

1. **Bloque C** (wording "dummies", las 9 prácticas) → ~0.5 días,
   independiente, hacerlo ya
2. **Bloque A** (oráculo + verificación real, P2-P9 + revisar P1) →
   ~2-3 días, es el fundamento de B y E
3. **Bloque B** (tablas de oráculo visibles) → ~1 día
4. **Bloque E** (`GUION.md`) → ~1.5-2 días
5. **Bloque F** (enlaces notebook → GUION) → ~0.5 días
6. **Bloque D** (comentarios de programación — el más largo) →
   ~4-5 días, práctica por práctica
7. **Bloque G** en paralelo a todo lo anterior, no al final

## Verificación

- `nbconvert --execute` por notebook tras cada cambio relevante, log
  completo leído (no solo el exit code) — mismo estándar que el plan de
  homogeneización Julia.
- Los valores nuevos de cada `oraculo.md` deben coincidir EXACTAMENTE con
  los de su `test_*.py` correspondiente (son la misma fuente; si no
  coinciden, hay un error en la transcripción, no en el test).
- `pytest tests/python/` sigue en verde durante todo el proceso — este
  plan no toca código de `src/`, solo notebooks y documentación.
