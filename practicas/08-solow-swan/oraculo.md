# Oráculo numérico — P8: Crecimiento neoclásico exógeno (Solow-Swan)

Capítulo 9 del libro (Bongers, Gómez y Torres, 2019). Modelo de crecimiento
neoclásico con tasa de ahorro exógena. Valores tomados del texto del libro
y Apéndice O (MATLAB). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base

Parámetros: α=0.35, s=0.20, δ=0.06, n=0.02, A=1.0.

| Magnitud | Valor esperado (Tabla 9.3 del libro) |
|---|---|
| Capital per cápita en SS (k*) | 4.0946 |
| Producción per cápita en SS (y*) | 1.6378 |
| Consumo per cápita en SS (c*) | 1.3103 |
| Inversión per cápita en SS (i*) | 0.3276 |

## Shock de ahorro: s de 20% → 25% (permanente desde t=1)

| Magnitud | Valor esperado |
|---|---|
| k₀ | Parte de k* inicial ≈ 4.0946 |
| Trayectoria de k | Creciente monótona hacia nuevo SS |
| Trayectoria de y | Creciente monótona hacia nuevo SS |
| c en impacto (cae por mayor ahorro) | c₀ = 0.75 × y₀ < c* inicial |
| Largo plazo: k, y, c | Alcanzan SS con s=0.25 |
| c de largo plazo | > c* inicial (el sacrificio compensa) |
| Tasa de crecimiento g_y | 0 en t=0, positiva en t=1, decreciente hacia 0 |

## Regla de Oro

| Magnitud | Valor esperado |
|---|---|
| Tasa de ahorro que maximiza c* | s_gold = α = 0.35 |
| c* en s_gold | Máximo global de la curva c̄(s) |
| c* en s=0.20 (infra-acumulación) | < c*_gold |
| c* en s=0.50 (sobre-acumulación, ineficiencia dinámica) | < c*_gold |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_growth.py`) se admite una
tolerancia absoluta de 1e-4 para el estado estacionario, 1e-2 para la
convergencia de largo plazo.
