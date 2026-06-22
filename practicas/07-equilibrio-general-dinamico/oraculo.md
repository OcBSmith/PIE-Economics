# Oráculo numérico — P7: Equilibrio General Dinámico (DGE) básico

Capítulo 8 del libro (Bongers, Gómez y Torres, 2019). Modelo de equilibrio
general dinámico con hogar representativo, empresa y gobierno. Valores
tomados del texto del libro, Apéndice L (MATLAB), Apéndice M (DYNARE) y
Apéndice N (DSGE). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base

Parámetros: α=0.35, β=0.97, δ=0.06, ρ=0.80, A=1.0.

| Magnitud | Valor esperado (Tabla 8.2 del libro) |
|---|---|
| Capital en SS (K*) | 6.698596 |
| Producción en SS (Y*) | 1.945783 |
| Consumo en SS (C*) | 1.543867 |
| Inversión en SS (I*) | 0.401916 |
| Tipo de interés en SS (R*) | 0.10166666666666667 |

## Estabilidad — Blanchard-Khan

| Magnitud | Valor esperado |
|---|---|
| Autovalor estable μ₁ (módulo < 1) | 0.90399 |
| Autovalor inestable μ₂ (módulo > 1) | 1.15229 |
| Clasificación | Punto de silla (exactamente 1 raíz estable) |

## Shock temporal de PTF: +1% con persistencia ρ=0.8

| Magnitud | Valor esperado |
|---|---|
| K₁ = K₀ (predeterminado, no salta) | = K* ≈ 6.6986 |
| C₁ (salta al alza en impacto) | > C* |
| Y₁ (salta al alza en impacto) | > Y* |
| I₁ (salta al alza en impacto) | > I* |
| Pico de K (hump, ocurre con retardo) | Entre periodos 2 y 12 |
| Convergencia de largo plazo (C, K) | Vuelven al SS inicial (tolerancia 1e-3) |
| Consistencia Blanchard-Khan vs simulación no lineal | K y C coinciden con rtol 1e-2 |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_dge.py`) se admite una
tolerancia de 1e-6 para el estado estacionario, 1e-5 para los autovalores
BK, 1e-3 para la convergencia de largo plazo.
