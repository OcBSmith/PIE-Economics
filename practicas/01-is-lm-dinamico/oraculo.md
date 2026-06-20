# Oráculo Numérico: Modelo IS-LM Dinámico (P1)

Este documento registra los valores esperados extraídos del libro original (Capítulo 2 y Apéndices D/E) para su uso como oráculo de verificación en los tests automáticos y en el notebook del alumno.

## Ecuaciones del modelo

- **Curva LM (Mercado de dinero):** $M - P = \psi Y - \theta i \Rightarrow i = \frac{P - M + \psi Y}{\theta}$
- **Curva IS (Demanda Agregada):** $Y^d = \beta_0 - \beta_1(i - \Delta P)$
- **Curva de Phillips (Inflación):** $\Delta P = \mu(Y - \bar{Y})$
- **Ajuste de la producción:** $\Delta Y = \nu(Y^d - Y)$

## Calibración base (Appendix D)

| Parámetro | Valor | Descripción |
| :--- | :--- | :--- |
| $\theta$ | 0.5 | Sensibilidad de la demanda de dinero al tipo de interés |
| $\psi$ | 0.01 | Sensibilidad de la demanda de dinero a la renta |
| $\beta_1$ | 50 | Sensibilidad de la inversión al tipo de interés real |
| $\mu$ (`Mi`) | 0.01 | Sensibilidad de la inflación a la brecha de producción |
| $\nu$ (`Ni`) | 0.2 | Velocidad de ajuste de la producción |
| $\beta_0$ | 2100 | Demanda agregada autónoma |
| $M_0$ | 100 | Oferta monetaria inicial |
| $\bar{Y}$ (`ypot0`) | 2000 | Producción potencial |

> **Nota sobre discrepancias**: En el Apéndice D (MATLAB) se usa `Psi = 0.01`, mientras que en el Apéndice E (DYNARE) se muestra `psi = 0.05`. Tomaremos la calibración de MATLAB como primaria, pero la función de python debe soportar ambas calibraciones.

## Estado Estacionario (Steady State)

Sustituyendo los parámetros base en las fórmulas de estado estacionario obtenemos:
- $Y = \bar{Y} = 2000$
- $P = \frac{\theta \beta_0}{\beta_1} + M_0 - (\psi + \frac{\theta}{\beta_1})\bar{Y} = \frac{0.5 \cdot 2100}{50} + 100 - (0.01 + \frac{0.5}{50}) \cdot 2000 = 21 + 100 - 0.02 \cdot 2000 = 121 - 40 = 81$
- $i = \frac{P - M_0 + \psi Y}{\theta} = \frac{81 - 100 + 0.01 \cdot 2000}{0.5} = \frac{-19 + 20}{0.5} = 2$
- $Y^d = \beta_0 - \beta_1(i - 0) = 2100 - 50 \cdot 2 = 2000$
- $\Delta P = 0$
- $\Delta Y = 0$

## Shock Numérico (Validación Dinámica)

Ante un shock monetario permanente de $M_1 = 101$ en $t=1$, el nuevo estado estacionario a largo plazo debe ser:
- $Y_{new} = 2000$
- $P_{new} = \frac{0.5 \cdot 2100}{50} + 101 - 0.02 \cdot 2000 = 21 + 101 - 40 = 82$ (Los precios suben exactamente igual que la oferta monetaria).
- $i_{new} = 2$
