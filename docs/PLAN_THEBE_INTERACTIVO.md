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

## ⚠️ Nota de arquitectura (2026-06-25)

La librería `thebe` estándar se probó y se **abandonó** (commit `b12a1c6`):
su loader AMD no cargaba de forma fiable en la página. `docs/javascripts/thebe.js`
es ahora un cliente propio que habla directamente con la API REST/WebSocket
de un servidor Binder (sin la librería `thebe`/`thebe-lite`). El nombre del
archivo se conserva por continuidad. El diagrama de arquitectura más abajo
sigue siendo correcto a alto nivel (web → WebSocket → kernel en Binder);
solo cambia que la pieza "Thebe (JS)" es código propio, no la librería.

## 📋 Plan de trabajo (~2 días)

### Fase 1 — Infraestructura de ejecución en vivo (~3 h)

1. [x] ~~Añadir `thebe` y `thebe-lite` a `mkdocs.yml` como JS/CSS~~ —
   reemplazado por `docs/javascripts/thebe.js` (cliente WebSocket propio,
   sin dependencia de la librería); `extra_css`/`extra_javascript` de
   `mkdocs.yml` ya no cargan `thebe.css` ni la librería `thebe`
2. [x] Configurar la conexión con BinderHub — `fetch` a
   `mybinder.org/build/gh/OcBSmith/PIE-Economics/main`, sondeo hasta
   `status: ready`, luego `POST api/kernels` + `WebSocket` a
   `api/kernels/<id>/channels` (ver `connectKernel`/`waitForBinder`/
   `launchKernel` en `thebe.js`)
3. [x] Añadir botón "Activar kernel Python" / "Activar kernel Julia" al
   inicio de cada página de práctica — barra `#kernel-bar` insertada por
   `thebe.js`, con botón "▶ Run" inyectado en cada bloque `<pre>` al
   conectar
4. [ ] Probar con P0 Python: que una celda simple ejecute y muestre output
   — **sin verificar en navegador real** (no hay browser tool disponible
   en esta sesión de unificación de documentación; pendiente de
   verificación manual, ver `docs/WIKI.md` Sesión 26)
5. [ ] Probar con P0 Julia: misma validación — pendiente, mismo motivo que 4

### Fase 2 — Conversión de notebooks (~3 h)

6. [~] Modificar `build_site.py` para que los notebooks copiados tengan
   metadatos compatibles con Thebe — **no aplica**: al abandonar la
   librería `thebe` (nota de arquitectura arriba), no hace falta ningún
   metadato especial; `thebe.js` lee el código directamente de los
   `<pre><code>` que `mkdocs-jupyter` ya renderiza
7. [x] Separar notebooks Python y Julia en páginas distintas — ya estaba
   hecho en `mkdocs.yml` (secciones "Prácticas Python"/"Prácticas Julia")
   desde el commit del sitio MkDocs, antes de este plan
8. [!] Añadir selector de kernel al inicio de cada notebook — **hallazgo
   pendiente de arreglar**: `thebe.js` muestra SIEMPRE los dos botones
   ("Activar Python" y "Activar Julia") en cualquier página, incluida una
   página de notebook Julia (donde el código no es Python y viceversa).
   Debería mostrar solo el botón del kernel que corresponde al lenguaje de
   esa página. No corregido en esta sesión (alcance: solo documentación)
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
| Cold start (primera vez tras cada push) | 🐢 varios min | Lo pone el build de Docker de Binder (repo2docker); no se puede acelerar desde el JS. Mitigado desde 2026-06-25: el job `warm-binder` de `.github/workflows/ci.yml` lanza ese build justo tras cada deploy, así que normalmente ya está cacheado cuando un visitante real entra |
| Cold start si el cache de Binder ha expirado | 🐢 varios min | Puede pasar si nadie visita la web durante un tiempo largo; el pre-calentado solo cubre justo después de cada push |
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
