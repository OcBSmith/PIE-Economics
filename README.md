# MACRO-AI-COMP

Material docente del proyecto **MACRO-AI-COMP** (convocatoria INNOVA26,
UMA / Banco Santander): itinerario incremental Excel → Python → Julia,
asistido por IA generativa, para portar los modelos del libro
*An Introduction to Computational Macroeconomics* (Bongers, Gómez y
Torres, Vernon Press, 2019) a código abierto.

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
practicas/            # Una carpeta por capítulo del libro (P0, P1, ...)
  00-introduccion-sistemas-dinamicos/
    python.ipynb      # Notebook de la práctica
    oraculo.md         # Valores numéricos esperados (verificación)
    referencia/        # Código MATLAB/DYNARE original del libro (oráculo)
src/macroaicomp/      # Paquete Python instalable con la lógica de los modelos
  models/              # Un módulo por modelo (arms_race.py, islm.py, ...)
  plotting/            # Funciones de visualización reutilizables
tests/python/          # Tests pytest que verifican cada modelo contra el oráculo
```

Cada práctica sigue la regla de oro del proyecto: las funciones
reutilizables viven en `src/`, no en el notebook; el notebook es solo el
frontend didáctico. Ver `PLAN_MAESTRO_MACRO_AI_COMP.md` §0.3 para los
estándares de código completos.

## Cómo arrancar

```bash
python -m venv .venv
.venv/Scripts/activate          # En Linux/Mac: source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/python/
jupyter notebook practicas/00-introduccion-sistemas-dinamicos/python.ipynb
```

## Estado

Fase de diseño (Fase I del plan maestro). Práctica P0 (Cap. 1, modelo de
Richardson) completa y verificada en Python. El resto de prácticas (P1-P9 +
extras de Cabello) y la versión Julia están pendientes. Todavía no hay
repositorio remoto en GitHub ni CI configurado — se trabaja en local hasta
que haya suficiente contenido que merezca la pena publicar.
