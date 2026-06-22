# Oráculo numérico — P3: Decisión óptima de consumo-ahorro

Capítulo 4 del libro (Bongers, Gómez y Torres, 2019). Modelo de decisión
intertemporal de consumo y ahorro del hogar representativo. Valores tomados
del texto del libro, Apéndice G (MATLAB) y Apéndice H (Newton). Cualquier
port a Python o Julia debe reproducir estos números.

## Calibración base

Parámetros: β=0.97, R=0.02, T=30, perfil de ingresos constante (W_t=10).
Tasa de descuento efectiva: β(1+R)=0.97×1.02=0.9894<1 ⇒ pendiente de
consumo negativa.

| Magnitud | Valor esperado |
|---|---|
| Activos terminales B_T (ambos solvers) | 0.0 (tolerancia 1e-6) |
| Equivalencia fsolve vs optimización directa (cvxpy) | Consumo y activos idénticos (rtol 1e-4) |

## Perfil de ingresos creciente (W_t crece de 10 a 10+T−1)

| Magnitud | Valor esperado |
|---|---|
| Activos iniciales B₀ | Negativos (endeudamiento juvenil) |
| Pendiente del consumo | Negativa (β(1+R)<1 domina al perfil de ingresos) |

## Perfil de jubilación (W_t=10 en t<20, W_t=0 en t≥20)

| Magnitud | Valor esperado |
|---|---|
| Pico de activos | En t=19 (fin de vida laboral, índice 19 en Python) |
| Activos durante vida laboral | Positivos (acumulación) |
| Activos durante jubilación | Desacumulación (pendiente negativa) |

## Sensibilidad a la tasa de descuento

Con β=0.99 (y R=0.02): β(1+R)=0.99×1.02=1.0098>1 ⇒ pendiente de consumo
**positiva** (consumo creciente a lo largo del ciclo vital).

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_consumption_savings.py`) se
admite una tolerancia absoluta de 1e-6 para la condición terminal, 1e-4
para la equivalencia entre solvers.
