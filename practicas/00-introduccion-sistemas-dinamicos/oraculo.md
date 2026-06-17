# Oráculo numérico — P0: Introducción a los sistemas dinámicos computacionales

Capítulo 1 del libro (Bongers, Gómez y Torres, 2019). Modelo de carrera de
armamentos de Richardson. Valores tomados directamente del texto del libro
(Secciones 1.4, 1.5, 1.6) y de `referencia/m1.m` (Apéndice B) y
`referencia/m1d.mod` (Apéndice C). Cualquier port a Python o Julia debe
reproducir estos números.

## Caso 1 — Calibración base (estabilidad global)

Parámetros (Tabla 1.1): α=0.50, β=0.25, γ=0.25, δ=0.50, θ=1.00, η=1.00.
Variables exógenas (Tabla 1.2): z₁=1, z₂=1.

| Magnitud | Valor esperado |
|---|---|
| Estado estacionario inicial (x̄₁, x̄₂) | (4, 4) |
| Autovalores (λ₁, λ₂) | (−0.25, −0.75) |
| Módulos (\|λ+1\|) | (0.75, 0.25) — ambos < 1 ⇒ estabilidad global |

### Shock: z₁ pasa de 1 a 2 (Sección 1.5)

| Magnitud | Valor esperado |
|---|---|
| Nuevo estado estacionario (x̄₁, x̄₂) | (6.67, 5.33) |
| Forma de la trayectoria | Monótona, convergente, nuevo SS alcanzado ≈ periodo 15 |

### Sensibilidad: α pasa de 0.50 a 0.70, mismo shock no aplicado (Sección 1.6.1)

| Magnitud | Valor esperado |
|---|---|
| Estado estacionario (x̄₁, x̄₂) | (2.61, 3.30) |
| Autovalores (λ₁, λ₂) | (−0.33, −0.87) |
| Estabilidad | Global (ambos módulos < 1: 0.67 y 0.13) |

## Caso 2 — Calibración de punto de silla (Sección 1.6.2)

Parámetros (Tabla 1.3): α=0.25, β=0.50, γ=0.50, δ=0.25, θ=1.00, η=1.00.
Variables exógenas (Tabla 1.4): z₁=−1, z₂=−1.

| Magnitud | Valor esperado |
|---|---|
| Estado estacionario inicial (x̄₁, x̄₂) | (4, 4) |
| Autovalores (λ₁, λ₂) | (−0.75, 0.25) |
| Módulos (\|λ+1\|) | (0.25, 1.25) — uno < 1 y otro > 1 ⇒ punto de silla |

### Shock: z₁ pasa de −1 a −0.5, x₁ es la variable de salto (jump variable)

| Magnitud | Valor esperado |
|---|---|
| Nuevo estado estacionario (x̄₁, x̄₂) | (3.33, 2.67) |
| Salto instantáneo de x₁ en el periodo del shock | 2.00 |
| x₂ en el periodo del shock | sin cambio (4.00), se ajusta a partir del periodo siguiente |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_arms_race.py`) se admite una
tolerancia absoluta de 1e-2 frente a los valores redondeados del libro, y
1e-6 frente a los valores exactos derivados analíticamente (estado
estacionario con calibración base).
