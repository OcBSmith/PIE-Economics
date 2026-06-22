# Oráculo numérico — P2: Exchange rate overshooting (Dornbusch)

Capítulo 3 del libro (Bongers, Gómez y Torres, 2019). Modelo de overshooting
del tipo de cambio de Dornbusch. Valores tomados del texto del libro y del
Apéndice F (DYNARE). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base

Parámetros (Cap. 3): β₀=500, β₁=50, θ=0.5, ψ=0.01, μ=0.01, ν=0.2,
m₀=100, ypot₀=2000, i_ext=3.0, y_ext=2000.0.

| Magnitud | Valor esperado |
|---|---|
| Estado estacionario inicial p* | 1.5 |
| Estado estacionario inicial s* | 76.515 |
| Tipo de interés inicial i* | 3.0 |
| Demanda agregada inicial yd* | 2000.0 |
| Δs en SS | 0.0 |
| Δp en SS | 0.0 |

## Estabilidad

| Magnitud | Valor esperado |
|---|---|
| Autovalor estable λ₁ | −0.7415 |
| Autovalor inestable λ₂ | 0.5395 |
| Clasificación | Punto de silla (un |λ+1|<1 y otro >1) |

## Shock monetario: m₀ de 100 → 101 en t=1

| Magnitud | Valor esperado |
|---|---|
| p en t=1 (sticky, sin cambio inmediato) | 1.5 |
| s en t=1 (overshooting, salto instantáneo) | 80.215 |
| i en t=1 (cae por el shock expansivo) | 1.0 |
| p en el largo plazo (nuevo SS) | 2.5 |
| s en el largo plazo (nuevo SS) | 77.515 |
| i en el largo plazo (neutro, vuelve al nivel inicial) | 3.0 |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_dornbusch.py`) se admite una
tolerancia absoluta de 1e-4 para el estado estacionario y autovalores, 1e-3
para el salto de s en el shock, y 1e-2 para los valores de largo plazo.
