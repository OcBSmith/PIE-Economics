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
│  │  │  docs/javascripts/thebe.js                 │  ││
│  │  │  Convierte celdas <pre> en editables + Run │  ││
│  │  └──┬──────────────────────────────────────┬──┘  ││
│  └─────┼──────────────────────────────────────┼─────┘│
└────────┼──────────────────────────────────────┼──────┘
   Python │ (Pyodide, en el propio navegador)   │ Julia (WebSocket/HTTP)
         ▼                                      ▼
┌──────────────────────┐         ┌──────────────────────────────────────┐
│  Pyodide (WebAssembly)│         │  MyBinder.org (gratis)                │
│  Corre en el navegador│         │  ┌──────────────────────────────────┐│
│  del alumno, sin red  │         │  │  Jupyter Kernel (Julia 1.10)    ││
│  ni servidor          │         │  │  Ejecuta el código y devuelve   ││
│                       │         │  │  outputs                        ││
└──────────────────────┘         │  └──────────────────────────────────┘│
                                   └──────────────────────────────────────┘
```

---

## ⚠️ Nota de arquitectura (2026-06-25, actualizada el mismo día)

La librería `thebe` estándar se probó y se **abandonó** (commit `b12a1c6`):
su loader AMD no cargaba de forma fiable en la página. `docs/javascripts/thebe.js`
pasó a ser un cliente propio que hablaba directamente con la API REST/WebSocket
de un servidor Binder para ambos lenguajes.

Tras varias pruebas reales con el usuario (build de Binder de varios
minutos, conexión SSE cortada a mitad), se decidió ir más lejos para
Python: **ya no usa Binder en absoluto**. Corre con **Pyodide**
(Python/WebAssembly) directamente en el navegador del alumno — sin
servidor, sin red salvo la descarga inicial del runtime. **Julia se queda
en Binder** porque no existe un runtime WASM de producción equivalente
(ver Decisión técnica #13 en `docs/WIKI.md`). El nombre del archivo
(`thebe.js`) se conserva por continuidad aunque ya no usa la librería
`thebe` ni, para Python, ningún servidor remoto.

## 📋 Plan de trabajo (~2 días)

### Fase 1 — Infraestructura de ejecución en vivo (~3 h)

1. [x] ~~Añadir `thebe` y `thebe-lite` a `mkdocs.yml` como JS/CSS~~ —
   reemplazado por `docs/javascripts/thebe.js`: Python vía Pyodide
   (sin servidor), Julia vía cliente WebSocket propio contra Binder. Sin
   dependencia de la librería `thebe`/`thebe-lite` en ningún caso;
   `extra_css`/`extra_javascript` de `mkdocs.yml` no cargan nada de eso
2. [x] Configurar la conexión con BinderHub (**solo Julia** desde
   2026-06-25) — `EventSource` a `mybinder.org/build/gh/OcBSmith/PIE-Economics/main`
   (stream de Server-Sent Events, no polling), luego `POST api/kernels` +
   `WebSocket` a `api/kernels/<id>/channels` (ver `connectKernel`/
   `launchKernel` en `thebe.js`). Python ya no contacta a Binder — ver
   `connectPython`/`loadPyodideScript` en el mismo archivo
3. [x] Añadir botón "Activar kernel Python" / "Activar kernel Julia" al
   inicio de cada página de práctica — barra `#kernel-bar` insertada por
   `thebe.js`, con botón "▶ Run" inyectado en cada celda de código real
   (`.highlight-ipynb pre`) al conectar
4. [ ] Probar con P0 Python: que una celda simple ejecute y muestre output
   — **sin verificar en navegador real** (no hay browser tool disponible
   en esta sesión; pendiente de verificación manual del usuario). Tras el
   cambio a Pyodide (2026-06-25) esto ya no depende de Binder
5. [ ] Probar con P0 Julia: misma validación — pendiente, sigue dependiendo de Binder

### Fase 2 — Conversión de notebooks (~3 h)

6. [~] Modificar `build_site.py` para que los notebooks copiados tengan
   metadatos compatibles con Thebe — **no aplica**: ni Pyodide (Python) ni
   el cliente WebSocket propio (Julia) necesitan metadatos especiales;
   `thebe.js` lee el código directamente de los bloques `<pre>` que
   `mkdocs-jupyter`/Pygments ya renderiza (sin `<code>` interior — ver
   commit `3786ac9`)
7. [x] Separar notebooks Python y Julia en páginas distintas — ya estaba
   hecho en `mkdocs.yml` (secciones "Prácticas Python"/"Prácticas Julia")
   desde el commit del sitio MkDocs, antes de este plan
8. [!] Añadir selector de kernel al inicio de cada notebook — **hallazgo
   pendiente de arreglar**: `thebe.js` muestra SIEMPRE los dos botones
   ("Activar Python" y "Activar Julia") en cualquier página, incluida una
   página de notebook Julia (donde el código no es Python y viceversa).
   Debería mostrar solo el botón del kernel que corresponde al lenguaje de
   esa página. Sigue sin corregir
9. [ ] Probar P1-P9 Python: ejecutar celdas clave (estado estacionario,
   simulación, gráficos) y confirmar que las celdas con `cvxpy` (P3/P4/P5)
   muestran el aviso en vez de fallar
10. [ ] Probar P1-P9 Julia: ejecutar celdas clave (sigue vía Binder)

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

> **Nota 2026-06-25**: Python ya **no** depende de Binder — corre en
> Pyodide (WebAssembly) directamente en el navegador del alumno (ver
> Decisión técnica #13 en `docs/WIKI.md`). Las filas de "cold start"
> de abajo aplican solo a **Julia**, que sigue usando Binder.

| Funcionalidad | ¿Funciona? | Nota |
|---|---|---|
| Ejecutar celda Python y ver output | ✅ | Pyodide local; texto y gráficos matplotlib (PNG), sin red salvo la carga inicial del runtime |
| Celdas Python con `cvxpy` (P3/P4/P5) | ❌ | `cvxpy` no tiene build para WebAssembly; se muestra un aviso en vez de un traceback. Sí funciona en Binder o en local |
| Ejecutar celda Julia y ver output | ✅ | Vía Binder, como antes |
| Gráficos Plots.jl (Julia) | ✅ | Se renderizan como PNG/SVG debajo de la celda |
| Sliders ipywidgets / Interact.jl | ❌ | No soportados en ningún caso (ni Pyodide ni nuestro cliente WebSocket a Binder) — necesitan widgets de Jupyter reales, solo disponibles abriendo Binder/JupyterLab completo |
| `@manipulate` de Julia | ❌ | Ídem |
| Cold start Python (primera vez) | ⚡ segundos | Descarga de Pyodide + numpy/scipy/matplotlib, no hay servidor de por medio |
| Cold start Julia (primera vez tras cada push) | 🐢 varios min | Lo pone el build de Docker de Binder (repo2docker); no se puede acelerar desde el JS. Mitigado desde 2026-06-25: el job `warm-binder` de `.github/workflows/ci.yml` lanza ese build justo tras cada deploy, así que normalmente ya está cacheado cuando un visitante real entra |
| Cold start Julia si el caché de Binder ha expirado | 🐢 varios min | Puede pasar si nadie visita la web durante un tiempo largo; el pre-calentado solo cubre justo después de cada push |
| Julia caliente (ya arrancado) | ⚡ instantáneo | Mientras el kernel no se duerma (10 min) |

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
