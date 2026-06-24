# Plan de Web Interactiva con Thebe — Ejecución desde el navegador

> Sustituir los botones "Abrir en Binder" por ejecución de código **dentro de
> la propia página web**, sin salir del navegador. Las celdas pasan de ser
> estáticas a ser editables y ejecutables con un botón Run.

---

## 🎯 Objetivo

El alumno:
1. Abre la web de una práctica
2. Lee teoría, ve código **editable** con botón Run en cada celda
3. Cambia parámetros, modifica código y ejecuta — el resultado (texto, tabla,
   gráfico) aparece debajo
4. Si quiere interactividad completa (sliders, widgets), salta a Binder con un
   botón secundario
5. Todo esto **sin salir del navegador**, **sin instalar nada**, **sin login**

---

## 🔧 Arquitectura

```
┌──────────────────────────────────────────────────────┐
│  GitHub Pages (HTML estático)                         │
│                                                       │
│  ┌──────────────────────────────────────────────────┐│
│  │  MkDocs Material + tema UMA                      ││
│  │  ┌────────────────────────────────────────────┐  ││
│  │  │  Thebe (JS)                                │  ││
│  │  │  Convierte celdas <pre> en editables + Run │  ││
│  │  └──────────────┬─────────────────────────────┘  ││
│  └─────────────────┼────────────────────────────────┘│
└────────────────────┼─────────────────────────────────┘
                     │ WebSocket / HTTP
                     ▼
┌──────────────────────────────────────────────────────┐
│  MyBinder.org (gratis)                                │
│  ┌──────────────────────────────────────────────────┐│
│  │  Jupyter Kernel (Python 3.11 / Julia 1.10)       ││
│  │  Ejecuta el código y devuelve outputs            ││
│  └──────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

---

## 📋 Plan de trabajo (~2 días)

### Fase 1 — Infraestructura Thebe (~3 h)

1. [ ] Añadir `thebe` y `thebe-lite` a `mkdocs.yml` como JS/CSS
2. [ ] Configurar Thebe para conectar con BinderHub
3. [ ] Añadir botón "Activar kernel Python" / "Activar kernel Julia" al
   inicio de cada página de práctica
4. [ ] Probar con P0 Python: que una celda simple ejecute y muestre output
5. [ ] Probar con P0 Julia: misma validación

### Fase 2 — Conversión de notebooks (~3 h)

6. [ ] Modificar `build_site.py` para que los notebooks copiados tengan
   metadatos compatibles con Thebe (celdas de código marcadas como
   ejecutables)
7. [ ] Separar notebooks Python y Julia en páginas distintas (ya está
   hecho en mkdocs.yml)
8. [ ] Añadir selector de kernel al inicio de cada notebook
9. [ ] Probar P1-P9 Python: ejecutar celdas clave (estado estacionario,
   simulación, gráficos)
10. [ ] Probar P1-P9 Julia: ejecutar celdas clave

### Fase 3 — Manejo de widgets (~2 h)

11. [ ] Identificar las celdas que usan `ipywidgets.interact()` /
    `@manipulate Interact.jl` (no funcionan en Thebe)
12. [ ] Para cada práctica, añadir una celda de "versión sin widgets" que
    use parámetros fijos + botón Run
13. [ ] Añadir badge "Abrir en Binder" al lado del código para quien
    quiera sliders interactivos completos

### Fase 4 — Pulido (~2 h)

14. [ ] Indicador de estado del kernel (conectando, listo, error)
15. [ ] Botón "Restart kernel" en la barra superior de cada página
16. [ ] Timeout para kernels inactivos (liberar recursos de Binder)
17. [ ] Estilo UMA para los botones Run y las celdas de código
18. [ ] Verificar que 44/44 pytest siguen en verde
19. [ ] Actualizar CI para incluir la nueva configuración

---

## 📂 Archivos a modificar

| Archivo | Cambio |
|---|---|
| `mkdocs.yml` | Añadir `thebe` en extra_javascript |
| `build_site.py` | Inyectar metadatos Thebe en notebooks |
| `docs/stylesheets/extra.css` | Estilo para botones Run |
| `.github/workflows/ci.yml` | Sin cambios (el deploy ya funciona) |
| `docs/javascripts/thebe.js` | Configuración de Thebe (nuevo) |

---

## ⚠️ Limitaciones

| Funcionalidad | ¿Funciona? | Nota |
|---|---|---|
| Ejecutar celda y ver output | ✅ | Texto, tablas, prints |
| Gráficos matplotlib / Plots.jl | ✅ | Se renderizan como PNG/SVG debajo de la celda |
| Sliders ipywidgets / Interact.jl | ❌ | Necesitan WebSocket bidireccional (no soportado) |
| `@manipulate` de Julia | ❌ | Ídem |
| `interact()` de Python | ❌ | Ídem |
| Cold start (primera vez) | 🐢 1-2 min | Lo pone Binder, no hay forma de evitarlo |
| Caliente (ya arrancado) | ⚡ instantáneo | Mientras el kernel no se duerma (10 min) |

---

## 🕹️ Experiencia final

```
┌──────────────────────────────────────────────────────┐
│  P1: IS-LM Dinámico                         [🌙] [🔍] │
│  ┌──────────────────────────────────────────────────┐│
│  │ 🟢 Kernel Python listo    [🔄 Restart]            ││
│  └──────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────┤
│                                                       │
│  ## 2. Calibración                                   │
│                                                       │
│  ```python                          ┌──────────────┐ │
│  params = default_calibration()     │  ▶ Run       │ │
│  ss = steady_state(params)          └──────────────┘ │
│  print(f"Y* = {ss['Y']}")                            │
│  ```                                                  │
│  ──────────────────────────────────────────────────   │
│  Y* = 2000.0                                         │
│                                                       │
│  ## 3. Verificación                                   │
│                                                       │
│  ```python                          ┌──────────────┐ │
│  np.testing.assert_allclose(        │  ▶ Run       │ │
│      ss['Y'], 2000.0, atol=1e-6)    └──────────────┘ │
│  print("OK")                                         │
│  ```                                                  │
│  ──────────────────────────────────────────────────   │
│  OK                                                   │
│                                                       │
│  > 🎮 ¿Quieres sliders interactivos?                  │
│  > [Abrir en Binder] — JupyterLab completo            │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Despliegue

1. Push a `main`
2. CI compila el sitio MkDocs con la nueva config de Thebe
3. GitHub Pages actualiza la web automáticamente
4. El alumno abre la URL y ve el botón Run en cada celda

---

## 💰 Coste

| Concepto | Coste |
|---|---|
| Thebe (JS) | Gratis (open source, MIT) |
| Binder (backend) | Ya lo tienes, corre sobre recursos gratuitos de mybinder.org |
| GitHub Pages | Ya lo tienes |
| **Total** | **0 €** |

---

*Plan creado: 2026-06-24.*
