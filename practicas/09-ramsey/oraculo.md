# Oráculo numérico — P9: Crecimiento óptimo de Ramsey

Capítulo 10 del libro (Bongers, Gómez y Torres, 2019). Modelo de crecimiento
óptimo con hogar representativo que elige consumo y ahorro
intertemporalmente. Valores tomados del texto del libro y Apéndice P
(DYNARE). Cualquier port a Python o Julia debe reproducir estos números.

## Calibración base

Parámetros: α=0.35, β=0.97, δ=0.06, n=0.02, A=1.0.

| Magnitud | Valor esperado (Tabla 10.2 del libro) |
|---|---|
| Capital per cápita en SS (k*) | 7.9537 |
| Producción per cápita en SS (y*) | 2.0663 |
| Consumo per cápita en SS (c*) | 1.4300 |
| Inversión per cápita en SS (i*) | 0.6363 |
| Tipo de interés en SS (R*) | 0.0909 |

## Estabilidad — Blanchard-Khan log-linealizado

| Magnitud | Valor esperado |
|---|---|
| Raíz estable λ₁ (log-desviación) | −0.0907 |
| Raíz inestable λ₂ (log-desviación) | 0.1115 |
| Módulo estable en niveles \|1+λ₁\| | 0.9093 (< 1) |
| Módulo inestable en niveles \|1+λ₂\| | 1.1115 (> 1) |
| Pendiente de salto θ (Δĉ/Δk̂ sobre senda estable) | 0.5751 |

## Shock permanente de PTF: A de 1.00 → 1.05 en t=5

| Magnitud | Valor esperado |
|---|---|
| k en t_shock (predeterminado, no salta) | = k* inicial ≈ 7.9537 |
| ĉ en t_shock (salto sobre senda estable) | = k̂ × θ ≈ k̂ × 0.5751 (tolerancia 1e-3) |
| k en el largo plazo | k* con A=1.05 (mayor que inicial) |
| c en el largo plazo | c* con A=1.05 (mayor que inicial) |
| Consistencia lineal vs no lineal | k y c coinciden con atol 5e-2, rtol 1e-2 |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_ramsey.py`) se admite una
tolerancia absoluta de 1e-4 para el estado estacionario y autovalores, 1e-2
para la convergencia de largo plazo de la simulación no lineal.
