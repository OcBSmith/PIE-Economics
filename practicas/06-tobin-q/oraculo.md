# Oráculo numérico — P6: La empresa y la decisión de inversión (Q de Tobin)

Capítulo 7 del libro (Bongers, Gómez y Torres, 2019). Modelo de inversión
con costes de ajuste y Q de Tobin. Valores tomados del texto del libro y
Apéndice K (DYNARE). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base

Parámetros: α=0.35, β=0.97, δ=0.06, R=0.04, φ=10.0.

| Magnitud | Valor esperado |
|---|---|
| Q de Tobin en SS (q*) | 1.0 |
| Stock de capital en SS (K*) | 6.8711236 |
| Inversión en SS (I* = δK*) | 0.06 × 6.8711236 ≈ 0.412267 |
| Producción en SS (Y* = K*^α) | 6.8711236^0.35 ≈ 1.96 |

## Estabilidad

| Magnitud | Valor esperado |
|---|---|
| Autovalor estable λ₁ (log-desviación) | −0.060658 |
| Autovalor inestable λ₂ (log-desviación) | 0.107158 |
| Módulo estable en niveles \|1+λ₁\| | 0.939342 (< 1) |
| Módulo inestable en niveles \|1+λ₂\| | 1.107158 (> 1) |
| Clasificación | Punto de silla |

## Identidad de la fórmula de salto

| Magnitud | Valor esperado |
|---|---|
| θ (fórmula simplificada) vs θ_book (fórmula del libro) | Idénticos (tolerancia 1e-12) para todo R∈{0.02,0.03,0.04,0.05}, φ∈{5,10,15} |

## Shock permanente de tipo de interés: R de 4% → 3%

| Magnitud | Valor esperado |
|---|---|
| K₀ (predeterminado, sin salto) | K* en R=4% ≈ 6.871 |
| q₀ (salto inicial, forward-looking) | ≈ 1.1033 (>1.0, la inversión se estimula) |
| K en el largo plazo | K* en R=3% (mayor que el inicial) |
| q en el largo plazo | 1.0 (converge de vuelta) |
| Consistencia lineal vs no lineal | K y q coinciden con rtol 1e-2 |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_tobin_q.py`) se admite una
tolerancia de 1e-6 para estado estacionario y autovalores, 1e-4 para el
salto de q, 1e-3 para la convergencia de largo plazo.
