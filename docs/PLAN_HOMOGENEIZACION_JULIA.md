# Plan de Homogeneización Pedagógica: Notebooks Julia = Python

> **Objetivo**: Los notebooks Julia deben ser estructural y pedagógicamente idénticos a los Python. Mismo contenido, mismas secciones, mismas visualizaciones, misma interactividad. Solo cambia el lenguaje de programación.

---

## ESTADO — EMPEZAR AQUÍ

**Commiteado y verificado** (ver `git log`): Bloque K, Bloque A, Bloque B,
Bloque C+D, Bloque G+H completos.

**Siguiente**: Bloque I (calibración informativa), luego Bloque E
(visualización — el más grande, ~3 días), F, J, M.

---

## TIPO A — Errores de copy-paste (texto no adaptado a Julia)

- [x] A1. Buscar/reemplazar `.py` → `.jl` en secciones "Buenas Prácticas" (P0-P9) — vía `scratch/md_extractor.py` (P0 no usa md_extractor y ya no contenía el término)
- [x] A2. Buscar/reemplazar `cvxpy` → `solve_direct_optim` en texto Julia (P3, P4, P5) — case-insensitive, cubre también "CVXPY" en mayúsculas
- [x] A3. Buscar/reemplazar `pytest` → `Test.jl` en texto Julia (P3, P4)
- [x] A4. Buscar/reemplazar `SciPy fsolve` → `NLsolve.jl` en texto Julia (P7, P9)
- [x] A5. Limpiar tags `(Julia)` mal pegadas al final de objetivos (P3, P4, P5, P8, P9) — el tag ahora se añade solo a la primera línea (título), no al final de toda la celda
- [x] A6. Corregir "Simulación Python" → "Simulación Julia" en tabla verificación P2
- [x] A7. Corregir `DornbuschParameters` → `DornbuschParams` en P2 Buenas Prácticas
- [x] A8. Corregir `RamseyParameters` → `RamseyParams` en P9 referencias

## TIPO B — Celda de instalación no funcional

- [x] B1. Hacer funcional la celda de setup en P0 (detección Colab + Pkg.activate) — la celda placeholder (100% comentada) se reemplazó por una explicación honesta de Binder vs Colab, y la celda real ahora llama `Pkg.instantiate()` (antes nunca se ejecutaba, solo aparecía dentro de un comentario muerto)
- [x] B2. Hacer funcional la celda de setup en P1
- [x] B3. Hacer funcional la celda de setup en P2
- [x] B4. Hacer funcional la celda de setup en P3
- [x] B5. Hacer funcional la celda de setup en P4
- [x] B6. Hacer funcional la celda de setup en P5
- [x] B7. Hacer funcional la celda de setup en P6
- [x] B8. Hacer funcional la celda de setup en P7
- [x] B9. Hacer funcional la celda de setup en P8
- [x] B10. Hacer funcional la celda de setup en P9

## TIPO C — Celda de bienvenida ausente

- [x] C1. Copiar "GUÍA RÁPIDA PARA DUMMIES" de Python a Julia en P0
- [x] C2. Copiar celda de bienvenida de Python a Julia en P1 — ya estaba en el generador (`md_cells[1]`); se había perdido en el notebook por drift/autosave y se restauró al regenerar

## TIPO D — Contenido teórico recortado

- [x] D1. P1: Añadir sección 1.2 (Reducción a sistema de ODEs) con derivación paso a paso — ya estaba copiada vía `md_cells[2]` (toda la Sección 1 viene en una sola celda markdown en el Python original); solo necesitaba que el notebook se regenerase desde el script
- [x] D2. P1: Añadir glosario de parámetros con tabla formateada
- [x] D3. P1: Añadir derivación analítica de estado estacionario con aritmética explícita — igual que D1, ya estaba en `md_cells[3]`, solo necesitaba regenerarse
- [x] D4. P1: Añadir sección "Detrás de la Escena" (RK45, solve_ivp, función comentada) — ya estaba en `md_cells[4]` + la celda `custom_system_dynamics!`, solo necesitaba regenerarse
- [x] D5. P2: Implementar `simulate_dornbusch_manual()` en Julia (equivalente a las 59 líneas de Python) — incluye verificación cruzada contra `simulate_shock()` (diferencia máxima < 1e-8)

## TIPO E — Visualización inferior o distinta

- [x] E1. Añadir grid a todos los gráficos de P0 — Plots.jl ya muestra grid por defecto (`gridalpha=0.1`, sólido), pero era casi invisible comparado con el `ax.grid(True, linestyle=':', alpha=0.6)` de matplotlib; añadido `default(gridalpha=0.6, gridstyle=:dot)` global en la celda de imports, una sola vez por notebook, aplica a todos los gráficos
- [x] E2. Añadir grid a todos los gráficos de P1
- [x] E3. Añadir grid a todos los gráficos de P2
- [x] E4. Añadir grid a todos los gráficos de P3
- [x] E5. Añadir grid a todos los gráficos de P4
- [x] E6. Añadir grid a todos los gráficos de P5
- [x] E7. Añadir grid a todos los gráficos de P6
- [x] E8. Añadir grid a todos los gráficos de P7
- [x] E9. Añadir grid a todos los gráficos de P8
- [x] E10. Añadir grid a todos los gráficos de P9
- [~] E11. Añadir línea vertical de shock (vline! en t=shock) en P1 — **no aplica**: el modelo es de tiempo continuo y el shock se aplica desde t=0 (todo el tramo simulado es post-shock), Python tampoco tiene esta línea en ningún panel
- [x] E12. Añadir línea vertical de shock en P2
- [x] E13. Añadir línea vertical de shock en P7 — de paso se corrigió un bug real de indexado: el shock se aplicaba en t=0 (índice 1 de Julia) en vez de t=1 (índice 2), un período antes que en Python
- [x] E14. Añadir línea vertical de shock en P8 (unificar t_shock=5)
- [x] E15. Añadir línea vertical de shock en P9 (unificar t_shock=5)
- [x] E16. P1: Añadir Panel 3 (diagrama de fases con quiver, loci Ydot=0, Pdot=0) — ya estaba en el generador
- [x] E17. P2: Añadir anotación de flecha "Jump" en diagrama de fases
- [x] E18. P6: Añadir streamplot/campo vectorial en diagrama de fases
- [x] E19. P6: Añadir Saddle Path como línea dibujada explícitamente
- [x] E20. P6: Añadir punto de salto naranja + flecha de salto
- [x] E21. P6: Añadir flechas direccionales sobre trayectoria dinámica
- [x] E22. P6: Añadir sombreado de inversión neta (fill_between equivalente)
- [x] E23. P6: Añadir línea de depreciación (δK_t) en panel de inversión
- [x] E24. P8: Añadir Panel 4 (tasa de crecimiento g_y)
- [x] E25. P8: Cambiar diagrama de Regla de Oro al estilo curva consumo-ahorro — reescrito como `c̄(s)` con regiones sombreadas de (in)eficiencia dinámica, igual que Python
- [x] E26. P3, P4, P5: Migrar sombreado acreedor/deudor a fillrange condicional — ya estaba hecho (usan `max./min.` + `fillrange=0`, el equivalente idiomático de Plots.jl al `fill_between(..., where=)` de matplotlib)
- [~] E27. Unificar colores con paleta UMA en P0 — **no aplica**: el Python original de P0 usa estilo neutro en escala de grises (`color="0.25"`, `"0.3"`, `"black"` en `src/macroaicomp/plotting/phase_diagram.py`), no la paleta UMA; no hay nada que unificar
- [x] E28. Unificar colores con paleta UMA en P1 — Y→#004C97, P→#8EAD3A, trayectoria→#7A3E9F, locus P_dot=0→#D95319, locus Y_dot=0→#0072BD
- [x] E29. Unificar colores con paleta UMA en P2 — s/trayectoria→#7A3E9F, p→#8EAD3A, i→#004C97, yd/ypot→#D95319
- [x] E30. Unificar colores con paleta UMA en P3 — C→#7A3E9F, W→#8EAD3A, B→#004C97, U/deuda→#D95319
- [x] E31. Unificar colores con paleta UMA en P4 — C→#7A3E9F, W·L→#8EAD3A, L→#E05A47, O(ocio)→#3BB193, B→#004C97, deudor→#D95319
- [x] E32. Unificar colores con paleta UMA en P5 — colores distintos por sección (lump-sum/distorsionador/SS) igual que Python: C→#7A3E9F, ingreso→#8EAD3A, L→#E05A47, O→#3BB193, B distorsionador→#004C97/#D95319, B privado SS→#D95319, Fondo SS→#8EAD3A
- [x] E33. Unificar colores con paleta UMA en P6 — q→#7A3E9F, K→#004C97, I→#D95319 (la sección de diagrama de fases ya usaba estos mismos hex de antes; el scatter "Salto Inicial" se deja en `:orange` porque Python también usa el 'orange' genérico ahí, no el hex)
- [x] E34. Unificar colores con paleta UMA en P7 — Y→#004C97, C→#7A3E9F, I→#D95319, K→#8EAD3A (de paso se corrigió J4: la celda de comparación BK-vs-no-lineal mostraba K y un "error absoluto" en vez de C y K con error relativo, como hace Python)
- [x] E35. Unificar colores con paleta UMA en P8 — corregido un mapeo de colores "desordenado" (k usaba azul, y usaba púrpura, c usaba verde — ninguno coincidía con Python): k→#8EAD3A, y→#004C97, c→#7A3E9F, gy→#D95319; SS Final corregido de negro a rojo; panel de Regla de Oro con las regiones pastel exactas de Python (#E6F2FF/#FFE6E6) y el punto de la Regla de Oro en #8EAD3A
- [x] E36. Unificar colores con paleta UMA en P9 — Y→#004C97, C→#7A3E9F, I→#D95319, K→#8EAD3A; SS Final corregido de negro a rojo (coincidiendo con P8)
- [~] E37. Unificar etiquetas/títulos/leyendas descriptivos en P0 — **no aplica**: la librería reutilizable `src/macroaicomp/plotting/phase_diagram.py` usa texto en inglés ("Periods", "Phase Diagram"); los títulos en español ya existentes en Julia son pedagógicamente más consistentes con el resto del proyecto (100% en español) que replicar ese inglés
- [x] E38. Unificar etiquetas/títulos/leyendas descriptivos en P1 — títulos y ylabels (antes "Y"/"P" sueltos) ahora coinciden con Python: "Producción (Y)", "Nivel de Precios (P)"
- [x] E39. Unificar etiquetas/títulos/leyendas descriptivos en P2 — "Trayectorias Temporales (s y p)", "Escala Logarítmica", "Tipos de Interés y Demanda Agregada"
- [x] E40. Unificar etiquetas/títulos/leyendas descriptivos en P3 — títulos completos ("...a lo largo del Ciclo de Vida", "...Financieros", "...por Periodo") y ylabel "Unidades de Bienes"
- [x] E41. Unificar etiquetas/títulos/leyendas descriptivos en P4 — mismos ajustes que P3 más "Asignación del Tiempo (Trabajo vs Ocio)"
- [x] E42. Unificar etiquetas/títulos/leyendas descriptivos en P5 — títulos y ylabels de las 3 secciones (lump-sum/distorsionador/SS) alineados con los 3 paneles de Python ("Consumo de Bienes", "Oferta de Trabajo (L)", "Acumulación de Activos", "Decisión de Consumo Óptimo")
- [x] E43. Unificar etiquetas/títulos/leyendas descriptivos en P6 — añadidos los ylabels que faltaban en los 3 paneles ("Ratio q", "Capital (K)", "Inversión (I)") y corregidos títulos ("Ratio Q de Tobin", "Dinámica de Inversión", "Comparación: ...")
- [x] E44. Unificar etiquetas/títulos/leyendas descriptivos en P7 — añadidos los ylabels que faltaban (Y, C, I, K) y corregidos los 4 títulos para que coincidan con Python ("Evolución de la Producción (PIB)", etc.)
- [x] E45. Unificar etiquetas/títulos/leyendas descriptivos en P8 — añadidos ylabels (k, y, c) y corregidos títulos ("Stock de Capital per cápita", "Producción per cápita (PIB p.c.)")
- [x] E46. Unificar etiquetas/títulos/leyendas descriptivos en P9 — corregidos títulos ("Evolución de la Producción...", "Respuesta de Consumo...(Salto)", etc.) y ylabels a minúsculas (y,c,i,k) igual que Python; corregida también la falta de acento en "Períodos"
- [~] E47. Añadir etiquetas 'SS Inicial' / 'SS Final' en P1-P9 — P6 y P9 ya lo tenían; añadido en P1 (Panel de Precios, antes "P inicial"/"P final") y P8 (las hlines iniciales tenían `label=""` vacío). **No aplica igual en el resto**: P2 muestra 2 variables (s, p) en el mismo panel y la distinción por variable (`s Inicial`, `p Inicial`) es más clara que un genérico "SS"; P3/P4/P5/P7 son modelos de horizonte finito (ciclo de vida, DGE) que no tienen una comparación de estado estacionario inicial/final del mismo tipo que P1/P6/P8/P9

## TIPO F — Falta de interactividad (widgets)

- [x] F1. P0: Implementar @manipulate con slider en vez de función estática
- [x] F2. P1: Implementar @manipulate con ambos sliders (m0 + beta0)
- [x] F3. Añadir descripciones en español a sliders en P3, P4, P5, P6, P7, P8, P9 — vía `slider(rango; value=..., label="...")` de Interact.jl, con el mismo texto que el `description=` de Python; aplicado también a P0/P1/P2 donde aplicaba

## TIPO G — Rangos de sliders diferentes

- [x] G1. P0: Unificar z1_final default a 2.0, rango -2.0:0.25:4.0 — vía `slider(-2.0:0.25:4.0; value=2.0)`
- [x] G2. P1: Unificar m0_shock default a 110.0, rango 80:2:120 — el rango real de Python es `80.0:1.0:120.0` (el "2" del checklist era impreciso); fijado el default explícito a 110.0 vía `slider(...; value=110.0)`
- [x] G3. P3: Extender β max a 0.999 (desde 0.99) — vía `slider([0.90:0.01:0.99; 0.999]; value=0.97)`
- [x] G4. P4: Extender β max a 0.999 (desde 0.99) — mismo fix que G3
- [x] G5. P5: Unificar τss max a 0.60, τr max a 0.80
- [x] G6. P6: Unificar R range 0.01:0.005:0.08, φ max 30, δ range 0.01:0.01:0.15, α max 0.50
- [x] G7. P7: Permitir ε negativos (-0.05:0.01:0.05), ρ 0.0:0.05:0.99 — vía `slider(-0.05:0.005:0.05; value=0.01)` y `slider(0.0:0.05:0.99; value=0.80)`
- [x] G8. P9: Unificar A_final default a 1.05, rango 0.90:0.01:1.20
- [x] G9. P9: Unificar β_final default a 0.97, A comparación rango 0.70:0.02:1.30 — vía `slider(0.92:0.01:0.99; value=0.97)`

## TIPO H — Parámetros económicos distintos

- [x] H1. P5: Unificar R=0.05 (desde 0.02) — en las 3 secciones (lump-sum, distorsionador, SS)
- [x] H2. P5: Unificar γ=0.40 (desde 0.50) — en la sección distorsionadora (Python no sobreescribe γ en lump-sum/SS, se deja el default 0.5 ahí)
- [x] H3. P5: Unificar W lumpsum=10.0, distortionary=100.0
- [x] H4. P5: Unificar perfil salarial SS creciente (10+t) en vez de constante
- [x] H5. P6: Unificar α=0.35 (desde 0.33)
- [x] H6. P8: Unificar n=0.02 en benchmark (desde 0.015)

**Bug real corregido de paso (P5):** el widget de impuestos distorsionadores
pasaba los argumentos posicionales de `FiscalPolicyParameters(...)` en el
orden equivocado (struct real: T, beta, R, gamma, B0, tauw, tauc, taur,
tau_ss, t_star) — el slider `taur_val` (impuesto al capital) no tenía ningún
efecto y `tauc_val` se filtraba al campo `B0` (activos iniciales). Corregido
junto con H1-H4. Verificado: la comprobación de Equivalencia Ricardiana de
la Sección 1 imprime una diferencia de consumo de `0.0` exacto.

## TIPO I — Calibración menos informativa

- [x] I1. P0: Añadir printing formateado de calibración con tabla — Python solo usa `asdict(params_global)`; equivalente en Julia con un NamedTuple explícito (muestra nombre de cada campo)
- [x] I2. P2: Añadir printing formateado de calibración con tabla y descripciones
- [x] I3. P3: Añadir printing formateado de calibración con θ calculado
- [x] I4. P4: Añadir printing formateado de calibración con θ calculado
- [x] I5. P5: Añadir printing formateado de calibración con tabla — Python no tiene un equivalente exacto aquí (no construye un único objeto de calibración con print formateado); se añadió la misma tabla con glosario usada en P1/P2 para mantener la coherencia pedagógica

## TIPO J — Verificación más pobre

- [x] J1. P2: Igualar tolerancias @assert con las del texto markdown — la tabla decía "tolerancia < 1e-6" pero el código usaba 1e-5/1e-3; ajustado a 1e-6 (Python no tiene assert real, solo la tabla, así que se verificó que el valor computado en Julia sí alcanza esa precisión)
- [x] J2. P3: Añadir valores C(0), C(T-1), B(T-1) ambos solvers + ✅/❌
- [x] J3. P4: Añadir valores C(0), L(0), B(T-1) ambos solvers + ✅/❌
- [x] J4. P7: Añadir cálculo e impresión de error relativo máximo (C y K) — corregido de paso al unificar colores (E34): la celda solo comparaba K con un "error absoluto" en un panel separado; ahora compara C y K igual que Python, con el error relativo máximo de ambos impreso
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
- [!] M3. P7: Añadir checkbox use_matlab_timing — **bug en Python ya corregido** (se quitó el kwarg `use_matlab_timing=...` de las llamadas a `solve_blanchard_khan`/`solve_nonlinear_simulation` en `generate_p7_notebook.py`, que lanzaban `TypeError` si se ejecutaban; verificado con `nbconvert --execute` que la celda ahora corre limpia). El checkbox sigue en el Python original pero ya **no tiene ningún efecto real** — nunca se implementó un `use_matlab_timing` que cambie el comportamiento del modelo en ninguno de los dos lenguajes. Añadir un checkbox equivalente en Julia solo replicaría un control decorativo sin función; queda sin hacer hasta que (si alguna vez se quiere) se diseñe e implemente el toggle real en ambos lenguajes — eso sería trabajo nuevo, no homogeneización.
- [x] M4. P7: Añadir slider de δ (actualmente hardcodeado) — `delta_val` estaba fijo a 0.05 en `DGEParams(alpha_val, beta_val, 0.05, rho_val, 1.0)`; añadido como slider interactivo igual que en Python

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
