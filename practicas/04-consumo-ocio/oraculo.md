# Oráculo numérico — P4: Decisión óptima de consumo-ocio

Capítulo 5 del libro (Bongers, Gómez y Torres, 2019). Modelo de elección
conjunta de consumo-ahorro (decisión intertemporal) y consumo-ocio (decisión
intratemporal de oferta de trabajo). Valores tomados del texto del libro y
Apéndice I (MATLAB). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base

Parámetros: β=0.97, R=0.02, γ=0.50, T=30, salario constante W_t=30.
Tasa de descuento efectiva: β(1+R)=0.97×1.02=0.9894<1.

| Magnitud | Valor esperado |
|---|---|
| Activos terminales B_T (ambos solvers) | 0.0 (tolerancia 1e-6) |
| Equivalencia fsolve vs optimización directa (cvxpy) | C, L, B idénticos (rtol 1e-4) |
| Oferta de trabajo L_t | 0 ≤ L_t < 1.0 para todo t |
| Ocio O_t | 0 < O_t ≤ 1.0 para todo t |

## Sensibilidad a las preferencias

| Magnitud | Valor esperado |
|---|---|
| γ=0.40 vs γ=0.60 (mayor peso del consumo en utilidad) | L media mayor con γ=0.60 |
| R=0.05 (con β=0.97): β(1+R)=1.0185>1 | Pendiente de consumo positiva creciente |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_consumption_leisure.py`) se
admite una tolerancia absoluta de 1e-6 para la condición terminal, 1e-4
para la equivalencia entre solvers.
