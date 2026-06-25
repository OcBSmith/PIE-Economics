# MACRO-AI-COMP

[![CI](https://github.com/OcBSmith/PIE-Economics/actions/workflows/ci.yml/badge.svg)](https://github.com/OcBSmith/PIE-Economics/actions/workflows/ci.yml)

Material docente del proyecto **MACRO-AI-COMP** (convocatoria INNOVA26,
UMA / Banco Santander): itinerario incremental Excel → Python → Julia,
asistido por IA generativa, para portar los modelos del libro
*An Introduction to Computational Macroeconomics* (Bongers, Gómez y
Torres, Vernon Press, 2019) a código abierto.

▶ **Web pública**: https://ocbsmith.github.io/PIE-Economics/ (las 10
prácticas en Python y Julia, navegables, con ejecución de código en vivo
desde el navegador). ▶ **Repo**: https://github.com/OcBSmith/PIE-Economics

Ver [`PLAN_MAESTRO_MACRO_AI_COMP.md`](PLAN_MAESTRO_MACRO_AI_COMP.md) para el
plan de ejecución completo (con sus checkboxes de progreso),
[`docs/WIKI.md`](docs/WIKI.md) para el registro técnico día a día
(decisiones, hallazgos sobre el libro, qué se hizo en cada sesión), y
[`PROPUESTA DE PROYECTO DE INNOVACIÓN
EDUCATIVA-2.docx`](<PROPUESTA DE PROYECTO DE INNOVACIÓN EDUCATIVA-2.docx>)
para la propuesta oficial de la convocatoria.

## Equipo

| Rol | Nombre |
|---|---|
| IP / Coordinadora | Dra. Anelí Bongers |
| Modelización macro | Dr. José L. Torres Chacón |
| Evaluación y matemáticas | Dr. José M. Cabello González |
| Técnico / PTGAS | Dr. Antonio F. Romero Carrasco |

## Estructura del repositorio

```
practicas/            # Una carpeta por capítulo del libro (P0 a P9)
  0X-nombre/
    python.ipynb       # Notebook Python de la práctica
    julia.ipynb         # Notebook Julia equivalente
    GUION.md             # Guion de laboratorio (objetivos, bitácora, ABP)
    oraculo.md            # Valores numéricos esperados (verificación)
    referencia/             # Código MATLAB/DYNARE original del libro (oráculo)
src/macroaicomp/      # Paquete Python instalable con la lógica de los modelos
  models/              # Un módulo por modelo (arms_race.py, islm.py, ...)
  plotting/            # Funciones de visualización reutilizables
src/                  # Paquete Julia `MacroAIComp` (models/, equivalente a macroaicomp)
tests/python/          # Tests pytest que verifican cada modelo contra el oráculo
tests/julia/           # Tests Test.jl equivalentes
docs/                  # Web pública (MkDocs Material); ver más abajo
```

Cada práctica sigue la regla de oro del proyecto: las funciones
reutilizables viven en `src/`, no en el notebook; el notebook es solo el
frontend didáctico. Ver `PLAN_MAESTRO_MACRO_AI_COMP.md` §0.3 para los
estándares de código completos.

### Sobre `docs/index.md` y `docs/guia-profesor.md`

**No editar esos dos archivos directamente.** Son artefactos generados por
`build_site.py` a partir de los `index.md` y `guia-profesor.md` de la
**raíz** (la fuente real), están en `.gitignore` y se sobrescriben en cada
build. Si necesitas cambiar la portada o la guía del profesor, edita los
de la raíz.

## Cómo arrancar

```bash
python -m venv .venv
.venv/Scripts/activate          # En Linux/Mac: source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/python/
jupyter notebook practicas/00-introduccion-sistemas-dinamicos/python.ipynb

# Julia
julia --project=. -e "using Pkg; Pkg.instantiate()"
julia --project=. tests/julia/runtests.jl

# Previsualizar la web localmente
python build_site.py
mkdocs serve
```

## Estado

**Fase I (diseño) prácticamente cerrada**: las 10 prácticas (P0-P9) están
completas en Python y Julia — código, tests (44/44 pytest, suite completa
en verde en Julia), `oraculo.md` y `GUION.md` por práctica. El repositorio
es público en GitHub (`OcBSmith/PIE-Economics`) con CI (lint + tests Python
y Julia + deploy automático a GitHub Pages). Trabajo en curso: ejecución de
código en vivo desde la web (Thebe conectado a un kernel de Binder, ver
`docs/PLAN_THEBE_INTERACTIVO.md`). Pendiente: Nivel 1 (Excel/hojas de
cálculo originales del libro), modelos extra de Cabello (X1-X3), e
infraestructura de `prompts/`, `bitacora/`, `evaluacion/` del plan maestro
§1.2. Detalle completo en `PLAN_MAESTRO_MACRO_AI_COMP.md` §2 y
`docs/WIKI.md`.
