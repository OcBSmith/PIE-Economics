# Oráculo numérico — P5: Gobierno y política fiscal

Capítulo 6 del libro (Bongers, Gómez y Torres, 2019). Tres escenarios:
impuestos de suma fija (§6.2), impuestos distorsionadores (§6.3) y Seguridad
Social de capitalización (§6.4). Valores tomados del texto del libro y
Apéndice J (MATLAB). Cualquier port a Python o Julia debe reproducir estos
números.

## Calibración base común

Parámetros: β=0.97, R=0.05, γ=0.40, T=30.

---

## Sección 1 — Impuestos de suma fija (lump-sum, no distorsionador)

| Magnitud | Valor esperado |
|---|---|
| **Equivalencia Ricardiana**: τ_w=0.40 con devolución de transferencias vs sin impuestos | Consumo y activos idénticos (rtol 1e-6) |
| τ_w=0.40 SIN devolución de transferencias | C cae y \|B\| cae respecto al caso sin impuestos |

---

## Sección 2 — Impuestos distorsionadores

Calibración: τ_w=0.10, τ_c=0.0, τ_r=0.0, salario W=100 (constante en t).

| Magnitud | Valor esperado |
|---|---|
| Equivalencia FOC (fsolve) vs optimización directa (cvxpy) | C, L, B idénticos (rtol 1e-4) — tanto con return_transfers=True como False |
| τ_w sube de 0.10 → 0.40 (con devolución, efecto sustitución puro) | L media disminuye |
| τ_c sube de 0.0 → 0.30 (con devolución, efecto sustitución puro) | L media disminuye |

---

## Sección 3 — Impuesto al capital

Calibración: τ_r sube de 0.0 → 0.50 (sin devolución de transferencias).

| Magnitud | Valor esperado |
|---|---|
| Activos medios con τ_r=0.50 | Menores que con τ_r=0.0 (ahorro desincentivado) |
| Pendiente del consumo (C_T/C_0) con τ_r=0.50 | Más plana (menor crecimiento) que con τ_r=0.0 |

---

## Sección 4 — Seguridad Social de capitalización

Calibración: τ_ss=0.36, t_star=26 (edad de jubilación), salario constante
W=10 durante vida laboral (t<26), W=0 en jubilación.

| Magnitud | Valor esperado |
|---|---|
| Sustitución perfecta SS vs modelo equivalente sin SS | Consumo idéntico (rtol 1e-6) |
| Ahorro privado B durante vida laboral | Negativo al inicio (el agente reduce ahorro voluntario sabiendo que tiene pensión) |

## Tolerancia de verificación

Para los tests automáticos (`tests/python/test_fiscal_policy.py`) se admite
una tolerancia de 1e-6 para la equivalencia Ricardiana y de SS, 1e-4 para
la equivalencia entre solvers distorsionadores.
