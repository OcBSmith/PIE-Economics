# Plan de Web Interactiva — MACRO-AI-COMP

> ⚠️ **SUPERSEDED (2026-06-25).** Se evaluó Quarto pero finalmente se
> implementó con **MkDocs Material** (`mkdocs.yml` + `build_site.py` en la
> raíz del repo, plugin `mkdocs-jupyter`), ya en producción en
> https://ocbsmith.github.io/PIE-Economics/. No existe ningún `_quarto.yml`
> en el repo. Este documento queda como registro histórico de la
> evaluación inicial — no es el plan vigente. El plan activo de la web es
> [`docs/PLAN_THEBE_INTERACTIVO.md`](PLAN_THEBE_INTERACTIVO.md). Ver
> Decisión técnica #10 en `docs/WIKI.md`.

> Publicar las prácticas como sitio web navegable manteniendo el código
> visible, manipulable y pedagógicamente intacto.

---

## 🎯 Objetivo

Un sitio web público donde el alumno:
1. Navega por las 10 prácticas desde un menú lateral
2. Lee teoría, código comentado (con resaltado de sintaxis) y ecuaciones
   renderizadas en un formato editorial pulido
3. Ve tablas de oráculo y gráficos estáticos como referencia
4. Pulsa un botón **"▶ Ejecutar en Binder"** que lanza un JupyterLab con
   todo ejecutado, listo para manipular sliders y tocar código

---

## 🔧 Tecnología: Quarto

**Por qué Quarto y no Jupyter Book:**
- Soporta Python y Julia de forma nativa (Jupyter Book nació solo para Python)
- Renderiza `.ipynb` directamente sin conversión intermedia
- Genera HTML estático desplegable en GitHub Pages
- Tema visual limpio, índice lateral automático, buscador, modo oscuro
- Botón "Launch Binder" integrado en cada página
- Código coloreado con resaltado de sintaxis para ambos lenguajes
- Ecuaciones MathJax idénticas a Jupyter

---

## 📐 Estructura del sitio

```
macro-ai-comp/
├── _quarto.yml                  # Configuración global
├── index.qmd                    # Portada
├── 00-introduccion.qmd          # Práctica P0
├── 01-islm.qmd                  # P1
├── 02-dornbusch.qmd             # P2
├── ...
├── 09-ramsey.qmd                # P9
├── guia-profesor.qmd            # GUION.md unificado
└── styles/
    └── uma-colors.scss          # Paleta UMA
```

Cada `.qmd` es un archivo Quarto Markdown que **incluye** el notebook
correspondiente:

```yaml
---
title: "P1: IS-LM Dinámico"
jupyter: python3
execute:
  enabled: false                  # No ejecutar; ya viene ejecutado del .ipynb
---
```

Opcionalmente, se puede enlazar el `.ipynb` directamente con `embed`:

```yaml
---
title: "P1: IS-LM Dinámico"
format:
  html:
    code-tools: true              # Botón "Show code" / "Hide code"
---
{{< embed practicas/01-is-lm-dinamico/python.ipynb >}}
```

---

## 🕹️ Flujo del alumno

```
┌──────────────────────────────────────────────────┐
│  macroaicomp.uma.es                              │
│  ┌────────────┐ ┌──────────────────────────────┐ │
│  │ 📖 Teoría  │ │                              │ │
│  │ 💻 Código  │ │  Contenido renderizado       │ │
│  │ 📊 Gráficos│ │  con ecuaciones, tablas,     │ │
│  │ ▶ Binder   │ │  gráficos y código comentado │ │
│  │ 🔍 Buscar  │ │                              │ │
│  │ 🌙 Modo    │ │                              │ │
│  │   oscuro   │ │                              │ │
│  └────────────┘ └──────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                           │
                           │ Pulsa "▶ Ejecutar en Binder"
                           ▼
┌──────────────────────────────────────────────────┐
│  MyBinder.org                                    │
│  ┌──────────────────────────────────────────────┐│
│  │  JupyterLab con kernel Python/Julia         ││
│  │  Celda de imports ejecutada                 ││
│  │  Sliders de ipywidgets/@manipulate activos  ││
│  │  Código editable por el alumno              ││
│  └──────────────────────────────────────────────┘│
└──────────────────────────────────────────────────┘
```

---

## 📦 Plan de trabajo (~2 días)

### Día 1 — Infraestructura + primeras prácticas

1. [ ] Instalar Quarto CLI en la máquina de desarrollo
2. [ ] Crear `_quarto.yml` con:
   - Título, autoría UMA, licencia
   - Tema visual con paleta UMA (`#004C97`, `#8EAD3A`, `#7A3E9F`, `#D95319`)
   - Navegación lateral con las 10 prácticas + GUION
   - Botón de Binder global (hereda la URL base del repo)
3. [ ] Crear `index.qmd` (portada con logo, equipo, índice de prácticas)
4. [ ] Publicar P0 como prueba piloto:
   - Crear `00-introduccion.qmd` que embea `practicas/00.../python.ipynb`
   - Configurar que el código se muestre por defecto
   - Verificar que los gráficos y tablas de oráculo se ven bien
   - Verificar el botón de Binder enlaza correctamente
5. [ ] Desplegar a `docs/` y configurar GitHub Pages (gratuito, dominio `xxx.github.io`)
6. [ ] Repetir para P1

### Día 2 — Resto de prácticas + pulido

1. [ ] Migrar P2-P9 (4 Python, 4 Julia — o por pares)
2. [ ] Crear `guia-profesor.qmd` con el contenido fusionado de los GUION.md
3. [ ] Añadir a cada página:
   - Badge "Abrir en Colab" (solo Python)
   - Badge "Abrir en Binder" (Python + Julia)
   - Tiempo estimado de lectura
   - Pie con licencia CC BY-SA 4.0
4. [ ] Verificar renderizado en móvil (responsive)
5. [ ] Revisar buscador, modo oscuro, código coloreado
6. [ ] Revisar que las ecuaciones MathJax se vean bien (backslashes, underscores)
7. [ ] PR y merge a `main`

---

## 🚀 Despliegue en GitHub Pages

1. Quarto compila el sitio a `docs/` (HTML estático)
2. GitHub Pages servido desde la carpeta `docs/` de la rama `main`
3. `gh run` ejecuta `quarto render` en cada push y publica automáticamente
4. URL pública: `https://OcBSmith.github.io/PIE-Economics`
5. Si se compra dominio UMA: `https://macroaicomp.uma.es` → CNAME a GitHub Pages

---

## 💰 Coste

| Concepto | Coste |
|---|---|
| Quarto CLI | Gratis (open source) |
| GitHub Pages | Gratis (incluido en GitHub) |
| MyBinder | Gratis (límites generosos para docencia) |
| Dominio `macroaicomp.uma.es` | Gratis (UMA) |
| **Total** | **0 €** |

---

## 📋 Verificación

- [ ] `quarto render` compila sin errores
- [ ] Las 10 prácticas navegables desde el menú lateral
- [ ] Código Python/Julia con resaltado de sintaxis
- [ ] Ecuaciones MathJax renderizadas correctamente
- [ ] Tablas de oráculo visibles
- [ ] Gráficos estáticos visibles
- [ ] Botón "Launch Binder" funcional en cada práctica
- [ ] Navegación responsive en móvil
- [ ] Modo oscuro funcional
- [ ] `pytest tests/python/` sigue en verde (el plan no toca código)
- [ ] CI actualizado: `quarto render` como paso adicional en GitHub Actions

---

*Plan creado: 2026-06-23.*
