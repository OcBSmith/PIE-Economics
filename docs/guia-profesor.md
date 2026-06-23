# Guía del Profesor — MACRO-AI-COMP

!!! warning "Este documento es material de referencia para el profesor"
    El alumno encuentra todo lo necesario (objetivos, prerrequisitos, tiempo,
    cuestionario de bitácora y extensiones ABP) dentro del propio notebook.

## Estructura del repositorio

```
practicas/            # Una carpeta por capítulo (P0-P9)
  0X-nombre/
    python.ipynb      # Notebook Python
    julia.ipynb       # Notebook Julia
    oraculo.md         # Valores numéricos esperados
    referencia/        # Código MATLAB/DYNARE original
src/macroaicomp/      # Paquete Python (models/, plotting/)
src/MacroAIComp/      # Paquete Julia
tests/python/          # Tests pytest
tests/julia/           # Tests Julia
```

## Erratas detectadas en el libro

| Práctica | Capítulo | Errata | Corregida |
|---|---|---|---|
| P2 | Cap. 3 | Ecuación de $s^*$ usa $\beta_2$ en lugar de $\beta_1$ | ✅ |
| P3 | Cap. 4 | Código MATLAB del Apéndice G: condición terminal $B_T=W_T$ en vez de $B_T=0$ | ✅ |
| P4 | Cap. 5 | Apéndice I: indexado out-of-bounds en $f(2T-1)$ | ✅ |
| P6 | Cap. 7 | Fórmula extendida del salto de Uhlig simplificable a $\hat{q}_1 = \phi \lambda_1 \hat{k}_1$ | ✅ |
| P7 | Cap. 8 | Indexado temporal de la PTF (MATLAB vs DYNARE) | ✅ |
| P9 | Cap. 10 | Ecuación 10.72: falta factor $(1+n)$ en denominador | ✅ |

## Archivos GUION.md

Cada práctica tiene un `GUION.md` con:
- Reactivos digitales (librerías, versiones, oráculo)
- Posibles accidentes de laboratorio (chuleta para el TA)
- Referencias bibliográficas
