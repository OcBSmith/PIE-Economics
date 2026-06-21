# Plan de Homogeneización Pedagógica: Notebooks Julia = Python

> **Objetivo**: Los notebooks Julia deben ser estructural y pedagógicamente idénticos a los Python. Mismo contenido, mismas secciones, mismas visualizaciones, misma interactividad. Solo cambia el lenguaje de programación.

---

## TIPO A — Errores de copy-paste (texto no adaptado a Julia)

- [ ] A1. Buscar/reemplazar `.py` → `.jl` en secciones "Buenas Prácticas" (P0-P9)
- [ ] A2. Buscar/reemplazar `cvxpy` → `solve_direct_optim` en texto Julia (P3, P4, P5)
- [ ] A3. Buscar/reemplazar `pytest` → `Test.jl` en texto Julia (P3, P4)
- [ ] A4. Buscar/reemplazar `SciPy fsolve` → `NLsolve.jl` en texto Julia (P7, P9)
- [ ] A5. Limpiar tags `(Julia)` mal pegadas al final de objetivos (P3, P4, P5, P8, P9)
- [ ] A6. Corregir "Simulación Python" → "Simulación Julia" en tabla verificación P2
- [ ] A7. Corregir `DornbuschParameters` → `DornbuschParams` en P2 Buenas Prácticas
- [ ] A8. Corregir `RamseyParameters` → `RamseyParams` en P9 referencias

## TIPO B — Celda de instalación no funcional

- [ ] B1. Hacer funcional la celda de setup en P0 (detección Colab + Pkg.activate)
- [ ] B2. Hacer funcional la celda de setup en P1
- [ ] B3. Hacer funcional la celda de setup en P2
- [ ] B4. Hacer funcional la celda de setup en P3
- [ ] B5. Hacer funcional la celda de setup en P4
- [ ] B6. Hacer funcional la celda de setup en P5
- [ ] B7. Hacer funcional la celda de setup en P6
- [ ] B8. Hacer funcional la celda de setup en P7
- [ ] B9. Hacer funcional la celda de setup en P8
- [ ] B10. Hacer funcional la celda de setup en P9

## TIPO C — Celda de bienvenida ausente

- [ ] C1. Copiar "GUÍA RÁPIDA PARA DUMMIES" de Python a Julia en P0
- [ ] C2. Copiar celda de bienvenida de Python a Julia en P1

## TIPO D — Contenido teórico recortado

- [ ] D1. P1: Añadir sección 1.2 (Reducción a sistema de ODEs) con derivación paso a paso
- [ ] D2. P1: Añadir glosario de parámetros con tabla formateada
- [ ] D3. P1: Añadir derivación analítica de estado estacionario con aritmética explícita
- [ ] D4. P1: Añadir sección "Detrás de la Escena" (RK45, solve_ivp, función comentada)
- [ ] D5. P2: Implementar `simulate_dornbusch_manual()` en Julia (equivalente a las 59 líneas de Python)

## TIPO E — Visualización inferior o distinta

- [ ] E1. Añadir grid a todos los gráficos de P0
- [ ] E2. Añadir grid a todos los gráficos de P1
- [ ] E3. Añadir grid a todos los gráficos de P2
- [ ] E4. Añadir grid a todos los gráficos de P3
- [ ] E5. Añadir grid a todos los gráficos de P4
- [ ] E6. Añadir grid a todos los gráficos de P5
- [ ] E7. Añadir grid a todos los gráficos de P6
- [ ] E8. Añadir grid a todos los gráficos de P7
- [ ] E9. Añadir grid a todos los gráficos de P8
- [ ] E10. Añadir grid a todos los gráficos de P9
- [ ] E11. Añadir línea vertical de shock (vline! en t=shock) en P1
- [ ] E12. Añadir línea vertical de shock en P2
- [ ] E13. Añadir línea vertical de shock en P7
- [x] E14. Añadir línea vertical de shock en P8 (unificar t_shock=5)
- [x] E15. Añadir línea vertical de shock en P9 (unificar t_shock=5)
- [ ] E16. P1: Añadir Panel 3 (diagrama de fases con quiver, loci Ydot=0, Pdot=0)
- [ ] E17. P2: Añadir anotación de flecha "Jump" en diagrama de fases
- [x] E18. P6: Añadir streamplot/campo vectorial en diagrama de fases
- [x] E19. P6: Añadir Saddle Path como línea dibujada explícitamente
- [x] E20. P6: Añadir punto de salto naranja + flecha de salto
- [x] E21. P6: Añadir flechas direccionales sobre trayectoria dinámica
- [x] E22. P6: Añadir sombreado de inversión neta (fill_between equivalente)
- [x] E23. P6: Añadir línea de depreciación (δK_t) en panel de inversión
- [x] E24. P8: Añadir Panel 4 (tasa de crecimiento g_y)
- [ ] E25. P8: Cambiar diagrama de Regla de Oro al estilo curva consumo-ahorro
- [ ] E26. P3, P4, P5: Migrar sombreado acreedor/deudor a fillrange condicional
- [ ] E27. Unificar colores con paleta UMA en P0
- [ ] E28. Unificar colores con paleta UMA en P1
- [ ] E29. Unificar colores con paleta UMA en P2
- [ ] E30. Unificar colores con paleta UMA en P3
- [ ] E31. Unificar colores con paleta UMA en P4
- [ ] E32. Unificar colores con paleta UMA en P5
- [ ] E33. Unificar colores con paleta UMA en P6
- [ ] E34. Unificar colores con paleta UMA en P7
- [ ] E35. Unificar colores con paleta UMA en P8
- [ ] E36. Unificar colores con paleta UMA en P9
- [ ] E37. Unificar etiquetas/títulos/leyendas descriptivos en P0
- [ ] E38. Unificar etiquetas/títulos/leyendas descriptivos en P1
- [ ] E39. Unificar etiquetas/títulos/leyendas descriptivos en P2
- [ ] E40. Unificar etiquetas/títulos/leyendas descriptivos en P3
- [ ] E41. Unificar etiquetas/títulos/leyendas descriptivos en P4
- [ ] E42. Unificar etiquetas/títulos/leyendas descriptivos en P5
- [ ] E43. Unificar etiquetas/títulos/leyendas descriptivos en P6
- [ ] E44. Unificar etiquetas/títulos/leyendas descriptivos en P7
- [ ] E45. Unificar etiquetas/títulos/leyendas descriptivos en P8
- [ ] E46. Unificar etiquetas/títulos/leyendas descriptivos en P9
- [ ] E47. Añadir etiquetas 'SS Inicial' / 'SS Final' en P1-P9

## TIPO F — Falta de interactividad (widgets)

- [ ] F1. P0: Implementar @manipulate con slider en vez de función estática
- [ ] F2. P1: Implementar @manipulate con ambos sliders (m0 + beta0)
- [ ] F3. Añadir descripciones en español a sliders en P3, P4, P5, P6, P7, P8, P9

## TIPO G — Rangos de sliders diferentes

- [ ] G1. P0: Unificar z1_final default a 2.0, rango -2.0:0.25:4.0
- [ ] G2. P1: Unificar m0_shock default a 110.0, rango 80:2:120
- [ ] G3. P3: Extender β max a 0.999 (desde 0.99)
- [ ] G4. P4: Extender β max a 0.999 (desde 0.99)
- [ ] G5. P5: Unificar τss max a 0.60, τr max a 0.80
- [x] G6. P6: Unificar R range 0.01:0.005:0.08, φ max 30, δ range 0.01:0.01:0.15, α max 0.50
- [ ] G7. P7: Permitir ε negativos (-0.05:0.01:0.05), ρ 0.0:0.05:0.99
- [x] G8. P9: Unificar A_final default a 1.05, rango 0.90:0.01:1.20
- [ ] G9. P9: Unificar β_final default a 0.97, A comparación rango 0.70:0.02:1.30

## TIPO H — Parámetros económicos distintos

- [ ] H1. P5: Unificar R=0.05 (desde 0.02)
- [ ] H2. P5: Unificar γ=0.40 (desde 0.50)
- [ ] H3. P5: Unificar W lumpsum=10.0, distortionary=100.0
- [ ] H4. P5: Unificar perfil salarial SS creciente (10+t) en vez de constante
- [x] H5. P6: Unificar α=0.35 (desde 0.33)
- [ ] H6. P8: Unificar n=0.02 en benchmark (desde 0.015)

## TIPO I — Calibración menos informativa

- [ ] I1. P0: Añadir printing formateado de calibración con tabla
- [ ] I2. P2: Añadir printing formateado de calibración con tabla y descripciones
- [ ] I3. P3: Añadir printing formateado de calibración con θ calculado
- [ ] I4. P4: Añadir printing formateado de calibración con θ calculado
- [ ] I5. P5: Añadir printing formateado de calibración con tabla

## TIPO J — Verificación más pobre

- [ ] J1. P2: Igualar tolerancias @assert con las del texto markdown
- [ ] J2. P3: Añadir valores C(0), C(T-1), B(T-1) ambos solvers + ✅/❌
- [ ] J3. P4: Añadir valores C(0), L(0), B(T-1) ambos solvers + ✅/❌
- [ ] J4. P7: Añadir cálculo e impresión de error relativo máximo (C y K)
- [x] J5. P9: Añadir cálculo e impresión de error relativo máximo

## TIPO K — Bugs de implementación

- [x] K1. P8: Corregir t_shock=5 (actualmente 10) — CRÍTICO
- [x] K2. P9: Corregir t_shock=5 (actualmente 1) — CRÍTICO
- [x] K3. P6: Corregir locus Δq̂=0 (debe tener pendiente, no ser vertical) — CRÍTICO
- [x] K4. P6: Migrar diagrama de fases a espacio de desviaciones logarítmicas — CRÍTICO
- [x] K5. P2: Corregir escala asimétrica del quiver (normalizar uniformemente) — ahora ambos ejes usan la misma fracción (5%) de su propio rango
- [x] K6. P5: Reubicar código de verificación Ricardiana antes del header Sección 2 — además corregido el desfase en cascada que arrastraba Seguridad Social bajo el header de Bitácora
- [ ] K7. P5: Actualizar texto de Actividades para que coincida con widgets reales de Julia — BLOQUEADO por M1 (Sección 1 de P5 no tiene widget interactivo en Julia todavía, así que el texto de "Activa la casilla Devolver recaudación" no tiene a qué referirse)
- [x] K8. P9: Unificar claves de diccionario minúsculas ("y","k","c","i") — ya satisfecho: `Ramsey.jl` devuelve ambas variantes de clave

## TIPO M — Diferencias estructurales

- [ ] M1. P5: Añadir simulación interactiva de lump-sum (Sección 1)
- [ ] M2. P5: Añadir verificación FOC vs optimización directa
- [ ] M3. P7: Añadir checkbox use_matlab_timing
- [ ] M4. P7: Añadir slider de δ (actualmente hardcodeado)

---

## Orden de ejecución recomendado

1. **Bloque K** (bugs críticos: P6, P8, P9) → 1 día
2. **Bloque A** (copy-paste: todos los notebooks) → 0.5 días
3. **Bloque C+D** (contenido faltante: P0, P1, P2) → 1 día
4. **Bloque B** (instalación funcional: todos) → 0.5 días
5. **Bloque G+H** (parámetros y rangos: todos) → 1 día
6. **Bloque I** (calibración: P0, P2, P3, P4, P5) → 0.5 días
7. **Bloque E** (visualización: todos) → 3 días
8. **Bloque F** (interactividad: P0, P1) → 0.5 días
9. **Bloque J** (verificación: P2, P3, P4, P7, P9) → 1 día
10. **Bloque M** (estructural: P5, P7) → 1 día

---

*Plan creado: 2026-06-21. Última actualización: 2026-06-21.*
