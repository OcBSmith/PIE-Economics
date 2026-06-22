import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# 1. CABECERA DIDÁCTICA Y METADATOS
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""# LAB-P0: Introducción a los sistemas dinámicos computacionales (Julia)

- **ID de práctica:** LAB-P0-v1.0-julia
- **Capítulo del libro:** Cap. 1 — *An introduction to computational dynamic systems* (Bongers, Gómez y Torres, 2019)
- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers
- **Fecha:** 2026-06-19
- **Versión:** 1.0
- **Licencia:** CC BY-SA 4.0 (este notebook) / MIT (el código de `MacroAIComp`)

Modelo de carrera de armamentos de Richardson: un sistema dinámico lineal de
dos ecuaciones que sirve de introducción a los conceptos de estado
estacionario, autovalores y estabilidad antes de abordar modelos
macroeconómicos concretos (IS-LM, Dornbusch, DGE...). Versión en Julia.
"""
    )
)

# 1.5. BIENVENIDA Y GUÍA RÁPIDA DE INICIO
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""> **👋 BIENVENIDA A LA PRÁCTICA - LEER ANTES DE EMPEZAR**
>
> *   **¿Nunca has usado Jupyter?** No te preocupes. Este cuaderno es interactivo. Haz clic en cualquier celda de código y pulsa **`Shift + Enter`** para ejecutarla. Ve de arriba a abajo en orden.
> *   **¿Se ha congelado o sale un asterisco `[*]` eterno?** Ve al menú superior y dale a `Kernel` ➔ `Restart`.
> *   **El objetivo** de esta práctica es que juegues con la economía. Cambia los números del código que representan impuestos, dinero o tecnología, vuelve a ejecutar y mira los gráficos. ¡No puedes romper nada!
> *   **📋 Antes de empezar**, consulta `GUION.md` (en esta misma carpeta): objetivos, tiempo estimado y conocimientos previos de esta práctica.
>

### 🕹️ GUÍA RÁPIDA DE INICIO - Sistemas Dinámicos
*   **¿Qué estamos haciendo aquí?** Estamos estudiando cómo una variable cambia a lo largo del tiempo usando reglas matemáticas sencillas. Imagina que es el crecimiento de una población o el saldo de tu cuenta bancaria.
*   **Puntos de Equilibrio (Estado Estacionario):** Es el valor donde la variable se queda quieta (no sube ni baja).
*   **Estabilidad:** Si perturbas el sistema (le das un empujón), ¿vuelve al equilibrio (estable) o se dispara al infinito (inestable)?
*   **¡Prueba esto!** Busca donde se definen las matrices o ecuaciones, ejecuta las celdas con `Shift + Enter` y observa cómo las flechas del diagrama de fases te indican hacia dónde viaja el sistema.
"""
    )
)

# 2. CONFIGURACIÓN DEL ENTORNO
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# Este cuaderno depende del paquete `MacroAIComp` (Project.toml/Manifest.toml
# en la raíz del repositorio). En MyBinder (ver docs/DESPLIEGUE_BINDER.md) y en
# tu entorno local, el kernel ya arranca dentro del repositorio clonado, así
# que la celda siguiente activa e instancia el proyecto automáticamente.
# Nota: Google Colab no soporta Julia de forma nativa desde un notebook .ipynb;
# para la versión Julia de esta práctica usa MyBinder.
"""
    )
)

# 3. IMPORTACIONES Y CONFIGURACIÓN
nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# "using X" trae a este cuaderno todo el código público del paquete X, para
# no tener que reescribirlo (es el equivalente Julia de "import X" en
# Python, pero sin necesidad de poner un alias para usar sus funciones).
# Pkg.activate("../..") le dice a Julia "usa el entorno (versiones de
# librerías) definido en Project.toml/Manifest.toml de la raíz del repo, no
# el entorno global de la máquina" — así todo el mundo ejecuta con las
# mismas versiones. Pkg.instantiate() descarga/instala lo que falte de ese
# entorno (la primera vez puede tardar; las siguientes es instantáneo).
using Pkg
Pkg.activate("../..")
Pkg.instantiate()

# MacroAIComp separa, igual que el paquete Python: la lógica matemática del
# modelo vive en src/models/ArmsRace.jl (matrices, estado estacionario,
# simulación) y la visualización se hace aquí con Plots.jl. El notebook solo
# llama funciones ya probadas, no reimplementa fórmulas (ver Sección 10).
using MacroAIComp
using Plots
# "import Plots: mm" es más selectivo que "using Plots": solo trae el
# nombre "mm" (una unidad de medida para márgenes) en vez de todo el
# paquete, que ya importamos en la línea anterior — aquí se hace así porque
# `mm` no se exporta por defecto con "using Plots".
import Plots: mm          # Para usar unidades de margen (p.ej. top_margin=10mm)
default(gridalpha=0.6, gridstyle=:dot)  # estilo de grid consistente con la versión Python
using LinearAlgebra
using BenchmarkTools
"""
    )
)

# 4. INTRODUCCIÓN TEÓRICA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 1. Teoría

El modelo se escribe como un sistema dinámico lineal de dos variables
endógenas (ecs. 1.7-1.11 del libro):

$$
\begin{bmatrix} \Delta x_{1,t} \\ \Delta x_{2,t} \end{bmatrix}
= \underbrace{\begin{bmatrix} -\alpha & \beta \\ \gamma & -\delta \end{bmatrix}}_{A}
\begin{bmatrix} x_{1,t} \\ x_{2,t} \end{bmatrix}
+ \underbrace{\begin{bmatrix} \theta & 0 \\ 0 & \eta \end{bmatrix}}_{B}
\begin{bmatrix} z_{1,t} \\ z_{2,t} \end{bmatrix}
$$

donde $x_{1,t}$ y $x_{2,t}$ son el stock de armamento de los países 1 y 2.
El **estado estacionario** es $\bar{\mathbf{x}} = -A^{-1}B\mathbf{z}$ (ec. 1.14),
y la **estabilidad** depende de los autovalores de $A$: el sistema es
globalmente estable si $|\lambda_i + 1| < 1$ para ambos autovalores, y
presenta un **punto de silla** si solo uno de los dos cumple esa condición
(Apéndice A).
"""))

# 5. CALIBRACIÓN
nb.cells.append(
    nbf.v4.new_markdown_cell(
        r"""## 2. Calibración — Caso 1: estabilidad global (Tablas 1.1 y 1.2)
"""
    )
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# Esta celda solo FIJA NÚMEROS (Tabla 1.1 y 1.2 del libro): todavía no
# calcula nada. ArmsRaceParams es un struct (definido en
# src/models/ArmsRace.jl): una "ficha" con 6 casillas con nombre, igual que
# el dataclass de Python, pero en Julia los structs normales se construyen
# con argumentos POSICIONALES (sin nombre): el primer número va a la
# primera casilla del struct (alpha), el segundo a la segunda (beta), etc.
# Por eso aquí SÍ es importante mantener el orden exacto y comentamos cada
# posición — si dos números se intercambiasen, Julia no avisaría de nada
# porque para ella son solo números en el orden correcto de argumentos.
params_global = ArmsRaceParams(
    0.50,  # alpha: sensibilidad de Delta x1 a su propio nivel x1
    0.25,  # beta: reacción de Delta x1 al stock de armamento x2
    0.25,  # gamma: reacción de Delta x2 al stock de armamento x1
    0.50,  # delta: sensibilidad de Delta x2 a su propio nivel x2
    1.00,  # theta: impacto de la variable exógena z1 sobre Delta x1
    1.00   # eta: impacto de la variable exógena z2 sobre Delta x2
)
# [1.0, 1.0] crea un Vector{Float64} (un array de números en Julia, similar
# al np.array de Python): z1 y z2, las dos variables exógenas.
z_initial = [1.0, 1.0]

# Equivalente al asdict(params_global) de Python: muestra cada campo con su
# nombre. La sintaxis (alpha=..., beta=..., ...) crea aquí una NamedTuple
# -- una tupla normal pero donde cada posición además tiene un nombre--
# SOLO para que se imprima de forma legible; no cambia los datos guardados
# en params_global. Al ejecutar esta celda veremos esos 6 valores impresos:
# es una comprobación visual de que no hay errores de tecleo.
(alpha=params_global.alpha, beta=params_global.beta, gamma=params_global.gamma,
 delta=params_global.delta, theta=params_global.theta, eta=params_global.eta)
"""
    )
)

# 6. RESOLUCIÓN
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 3. Resolución: estado estacionario y estabilidad
""")
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# steady_state() es una FUNCIÓN: le pasamos dos argumentos entre paréntesis
# y nos devuelve un resultado que guardamos con "=" en x_bar. Por dentro
# resuelve x_bar = -A^{-1} B z (ec. 1.14): el punto donde Delta x1 = Delta
# x2 = 0, es decir, donde ninguno de los dos países cambia ya su stock de
# armamento. No necesitamos saber CÓMO lo calcula para usarla, solo qué
# entra y qué sale.
x_bar = steady_state(params_global, z_initial)
# eigenvalues() da los autovalores de A. Lo que importa para la estabilidad
# no es su signo sino el módulo |lambda + 1| (Apéndice A): si es < 1 para
# AMBOS autovalores, cualquier perturbación se amortigua y el sistema vuelve
# al estado estacionario (estabilidad global); si solo uno cumple esa
# condición, es un punto de silla (lo veremos en la Sección 8).
lambdas = eigenvalues(params_global)

# El "." antes de un paréntesis o un operador (round.(...), .+ 1.0) es
# BROADCASTING: aplica esa operación a CADA elemento del array por
# separado, en vez de a todo el array de golpe. round.(x_bar, digits=2)
# redondea cada componente de x_bar a 2 decimales SOLO para que se imprima
# más corto; el valor real guardado en la variable no cambia.
println("Estado estacionario (x1_bar, x2_bar) = ", round.(x_bar, digits=2))
# sort() ordena los dos autovalores de menor a mayor, para que siempre se
# impriman en el mismo orden sin importar en qué orden los devuelva Julia.
println("Autovalores (lambda1, lambda2)        = ", round.(sort(lambdas), digits=2))
println("Moduli |lambda + 1|                   = ", round.(abs.(sort(lambdas) .+ 1.0), digits=2))
println("Punto de silla                        = ", is_saddle_path(params_global))
# Resultado esperado con esta calibración: SS en (4, 4), autovalores
# negativos con módulo < 1 (estabilidad global) y punto de silla = false.
"""
    )
)

# 7. VERIFICACIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 4. Verificación frente al oráculo

Comparamos contra los valores reportados en el libro y reproducidos por el
código MATLAB del Apéndice B (`referencia/m1.m`), recogidos en
`oraculo.md`: estado estacionario $(4, 4)$ y autovalores $(-0.25, -0.75)$.

**Caso 1 — Calibración base (Tabla 1.1: α=0.50, β=0.25, γ=0.25, δ=0.50, θ=1.00, η=1.00; z₁=z₂=1):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Estado estacionario inicial $(\bar x_1, \bar x_2)$ | (4, 4) |
| Autovalores $(\lambda_1, \lambda_2)$ | (−0.25, −0.75) |
| Nuevo SS tras shock $z_1: 1 \to 2$ (Sección 5) | (6.67, 5.33) |
| Nuevo SS tras sensibilidad $\alpha: 0.50 \to 0.70$ (Sección 7) | (2.61, 3.30) |

Así puedes comparar a simple vista, sin abrir `oraculo.md`, el número que
debería salir en cada celda siguiente con el que realmente sale.
"""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# isapprox(a, b; atol=...) compara dos valores (o dos arrays, elemento a
# elemento) y da `true` solo si la diferencia es menor que la tolerancia
# atol. No usamos "==" porque el ordenador casi nunca da resultados
# EXACTAMENTE iguales en aritmética con decimales (errores de redondeo
# internos), aunque la fórmula esté bien aplicada — comparar con un margen
# pequeño es la forma correcta de verificar números reales.
# @assert condicion no hace NADA si la condición es true: es un PUNTO DE
# CONTROL silencioso. Si el port a Julia tuviera un error, @assert lanzaría
# un AssertionError y detendría la ejecución aquí mismo, antes de seguir
# construyendo gráficos sobre un resultado incorrecto.
@assert isapprox(x_bar, [4.0, 4.0]; atol=1e-6)
@assert isapprox(sort(lambdas), [-0.75, -0.25]; atol=1e-6)
println("OK: coincide con el oráculo MATLAB (Apéndice B).")
"""
    )
)

# 8. SHOCK
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 5. Análisis de shock (Sección 1.5)

Aumentamos la variable exógena $z_1$ de 1 a 2 y observamos la transición
hacia el nuevo estado estacionario.
"""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# A partir de aquí cambiamos la variable exógena: el país 1 pasa de z1=1 a
# z1=2 (más hostilidad/gasto autónomo). simulate() reproduce la recursión
# periodo a periodo x[t+1] = x[t] + (A*x[t] + B*z_t), empezando en el SS
# anterior y usando z_final desde el periodo 2 (el 4º argumento, shock_period,
# en convención 1-based de Julia) — no resuelve el nuevo SS de golpe, lo
# alcanza simulando. simulate() devuelve DOS resultados a la vez; escribir
# dos nombres separados por coma a la izquierda del "=" hace que Julia
# reparta esa tupla: x1_path recibe el primero, x2_path el segundo.
z_final_shock = [2.0, 1.0]
x1_path, x2_path = simulate(params_global, z_initial, z_final_shock, 30, 2)

# x1_path[end] usa la palabra clave "end": significa "el último elemento
# del array" (en vez de tener que saber cuántos hay, como con x1_path[30]).
# Es el equivalente Julia del x1_path[-1] de Python.
println("Nuevo estado estacionario (x1_bar, x2_bar) = (",
        round(x1_path[end], digits=2), ", ", round(x2_path[end], digits=2),
        ")  (esperado: 6.67, 5.33)")

# Gráfico de respuesta a impulso — equivalente a plot_irf() del notebook Python.
# Como la calibración es globalmente estable, la trayectoria debería verse
# monótona y convergente (sin oscilar) hacia el nuevo SS, alcanzándolo hacia
# el periodo ~15.
t = 0:29
p1 = plot(t, x1_path,
          label="x1", color=:steelblue, linewidth=2.5, marker=:circle, markersize=3,
          title="Variable x1", xlabel="Periodos", ylabel="Stock de armamento")

p2 = plot(t, x2_path,
          label="x2", color=:forestgreen, linewidth=2.5, marker=:circle, markersize=3,
          title="Variable x2", xlabel="Periodos", ylabel="Stock de armamento")

# top_margin reserva espacio para el plot_title y evita solapamiento con los títulos de subplot
plot(p1, p2, layout=(1, 2), size=(800, 400),
     plot_title="Respuesta dinámica a un aumento de z1 (1 -> 2)",
     top_margin=10mm)
"""
    )
)

# 9. DIAGRAMA DE FASES
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 6. Diagrama de fases (Figura B.1 del Apéndice B)
""")
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# coefficient_matrices() reconstruye A y B (ec. 1.7-1.8) a partir de los
# mismos parámetros — las necesitamos sueltas porque, a diferencia de
# Python (que usa plot_phase_diagram() de la librería), aquí dibujamos el
# campo vectorial Delta x = A*x + B*z a mano con quiver() sobre una malla de
# puntos (x1, x2), no solo en la trayectoria simulada.
a, b = coefficient_matrices(params_global)

# Crear la malla de puntos para x1 y x2
x1_vals = range(0, 10, length=11)
x2_vals = range(0, 10, length=11)

# Float64[] crea un array VACÍO de números de punto flotante; lo iremos
# rellenando con push! dentro del bucle. En Julia, una función que termina
# en "!" (push!, plot!, scatter!) MODIFICA su primer argumento en el sitio
# en vez de devolver una copia nueva — es una convención del lenguaje, no
# una obligación, pero se respeta casi siempre.
x = Float64[]
y = Float64[]
u = Float64[]
v = Float64[]

# "for xi in x1_vals, yi in x2_vals" son DOS bucles anidados en una sola
# línea: recorre todas las combinaciones (xi, yi) de las dos listas, igual
# que un doble "for" normal. Para cada punto de la malla calculamos hacia
# dónde "empuja" el sistema (dx1, dx2) y lo guardamos como una flecha
# (u, v) que saldrá de ese punto.
for xi in x1_vals, yi in x2_vals
    dx = a * [xi, yi] + b * z_initial
    push!(x, xi)
    push!(y, yi)
    push!(u, dx[1])
    push!(v, dx[2])
end

# Escalamos las flechas (si no, su longitud real tapa el gráfico) solo para
# que se vean bien — no afecta a los valores numéricos de dx, solo al dibujo.
scale = 0.1
arrow_u = u .* scale
arrow_v = v .* scale

plt = plot(x, y, seriestype=:scatter, markersize=1, color=:gray, label="",
           title="Diagrama de Fases (Richardson)", xlabel="Variable x1", ylabel="Variable x2")
quiver!(x, y, quiver=(arrow_u, arrow_v), color=:gray)
# El punto negro marca el estado estacionario (x_bar). Si todas las flechas
# alrededor apuntan hacia ese punto, es estable — exactamente lo que
# esperamos aquí, reproduciendo la Figura B.1 del Apéndice B.
scatter!([x_bar[1]], [x_bar[2]], color=:black, markersize=8, label="Estado Estacionario")
plot!(size=(500, 500))
"""
    )
)

# 10. SENSIBILIDAD
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 7. Análisis de sensibilidad (Sección 1.6.1)

Aumentamos $\alpha$ de 0.50 a 0.70: el país 1 se vuelve más sensible a su
propio stock de armamento, lo que reduce el estado estacionario de ambos
países y rompe la simetría entre ellos.
""")
)

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""# Repetimos el mismo cálculo de la Sección 3 (steady_state + eigenvalues)
# pero con alpha más alto. Interpretación económica: alpha mide cuánto le
# "pesa" al país 1 su propio stock de armamento (fatiga/coste de
# mantenimiento) — si sube, el país 1 modera su propia carrera armamentística,
# lo que reduce SU estado estacionario y, por la interacción del sistema,
# también el del país 2 (que ya no necesita responder a tanto armamento).
# Como ya no es alpha=delta, además se rompe la simetría x1_bar=x2_bar del Caso 1.
# Creamos un ArmsRaceParams NUEVO en vez de modificar params_global (de
# hecho, en Julia los structs definidos como en este proyecto son
# inmutables por defecto: ni se podría modificar un campo después de
# crearlo). El nombre de la variable (params_sensitivity) deja claro que es
# una calibración distinta, no una corrección de la anterior.
params_sensitivity = ArmsRaceParams(0.70, 0.25, 0.25, 0.50, 1.00, 1.00)
x_bar_sensitivity = steady_state(params_sensitivity, z_initial)
lambdas_sensitivity = eigenvalues(params_sensitivity)

println("Estado estacionario (x1_bar, x2_bar) = ", round.(x_bar_sensitivity, digits=2), " (esperado: 2.61, 3.30)")
println("Autovalores                          = ", round.(sort(lambdas_sensitivity), digits=2), " (esperado: -0.87, -0.33)")
println("Punto de silla                       = ", is_saddle_path(params_sensitivity), " (esperado: false)")

# Igual que en la Sección 4: si el cálculo no coincide con el oráculo, esta
# celda detiene la ejecución con AssertionError en vez de dejar pasar un
# resultado numérico incorrecto.
@assert isapprox(x_bar_sensitivity, [2.61, 3.30]; atol=1e-2)
@assert isapprox(sort(lambdas_sensitivity), [-0.87, -0.33]; atol=1e-2)
"""
    )
)

# 11. PUNTO DE SILLA
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 8. Punto de silla (Sección 1.6.2)

Con $\beta, \gamma > \alpha, \delta$ (Tabla 1.3) el sistema tiene un
autovalor estable y otro inestable: el estado estacionario es un punto de
silla. La variable $x_1$ se asume "de salto" (forward-looking) y se
reajusta instantáneamente sobre la senda estable ante una perturbación
(ec. 1.39), mientras $x_2$ evoluciona de forma estándar.

**Caso 2 — Calibración de punto de silla (Tabla 1.3: α=0.25, β=0.50, γ=0.50, δ=0.25; z₁=z₂=−1 → z₁=−0.5):**

| Magnitud | Valor esperado (oráculo) |
|---|---|
| Estado estacionario inicial $(\bar x_1, \bar x_2)$ | (4, 4) |
| Autovalores $(\lambda_1, \lambda_2)$ | (−0.75, 0.25) — uno estable y otro inestable |
| Salto instantáneo de $x_1$ en el periodo del shock | 2.00 |
| Nuevo estado estacionario $(\bar x_1, \bar x_2)$ | (3.33, 2.67) |
"""))

nb.cells.append(
    nbf.v4.new_code_cell(
        r"""params_saddle = ArmsRaceParams(0.25, 0.50, 0.50, 0.25, 1.00, 1.00)
z_initial_saddle = [-1.0, -1.0]
z_final_saddle = [-0.5, -1.0]

# Confirmamos que esta calibración SÍ produce un punto de silla antes de
# llamar a simulate_saddle_path() (esa función lanza un error si no lo fuera).
println("Punto de silla = ", is_saddle_path(params_saddle), " (esperado: true)")

# simulate_saddle_path() trata las dos variables de forma distinta en el
# periodo del shock (el último argumento, 1, es jump_variable en convención
# 1-based de Julia -> x1 es la variable de salto): x2 (predeterminada) sigue
# evolucionando con su valor anterior, como en simulate(); x1
# (forward-looking) NO usa la recursión estándar, sino que se recalcula para
# caer exactamente sobre la senda estable asociada al autovalor estable —
# por eso "salta" en un solo periodo en vez de converger gradualmente.
x1_saddle, x2_saddle = simulate_saddle_path(
    params_saddle, z_initial_saddle, z_final_saddle, 30, 2, 1
)

# x1_saddle[2] es el SEGUNDO elemento del array: en Julia los índices
# empiezan en 1 (no en 0 como en Python), así que el primer elemento es
# x1_saddle[1] (el estado estacionario inicial) y x1_saddle[2] es el
# periodo del shock — el equivalente exacto del x1_saddle[1] de Python.
println("Salto instantáneo de x1 en el periodo del shock = ", round(x1_saddle[2], digits=2), " (esperado: 2.00)")
println("Nuevo estado estacionario (x1, x2) = (",
        round(x1_saddle[end], digits=2), ", ", round(x2_saddle[end], digits=2),
        ")  (esperado: 3.33, 2.67)")

@assert isapprox(x1_saddle[2], 2.0; atol=1e-2)
@assert isapprox([x1_saddle[end], x2_saddle[end]], [3.33, 2.67]; atol=1e-2)

# Graficar la trayectoria del punto de silla. x1 debería mostrar un escalón
# brusco en el periodo 1 (el salto) y luego converger con normalidad junto a x2.
t_axis = 0:29
p_s1 = plot(t_axis, x1_saddle,
            label="x1 (salto)", color=:purple, linewidth=2.5, marker=:circle, markersize=3,
            title="Variable x1", xlabel="Periodos", ylabel="Stock de armamento")

p_s2 = plot(t_axis, x2_saddle,
            label="x2", color=:orange, linewidth=2.5, marker=:circle, markersize=3,
            title="Variable x2", xlabel="Periodos", ylabel="Stock de armamento")

# top_margin reserva espacio para el plot_title y evita solapamiento
plot(p_s1, p_s2, layout=(1, 2), size=(800, 400),
     plot_title="Punto de silla: ajuste instantáneo de x1 ante el shock en z1",
     top_margin=10mm)
"""
    )
)

# 12. ANÁLISIS DE SENSIBILIDAD AL SHOCK Z1 (gráfico estático multi-escenario)
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 9. Análisis de sensibilidad al shock de z1

Comparamos la respuesta dinámica ante **cuatro magnitudes de shock** distintas sobre
$z_1^{\text{final}}$ (−1.0, 0.5, 2.0 y 3.5). Usamos un gráfico estático con varios
escenarios en vez de un slider interactivo de `Interact.jl`/`@manipulate`: ese widget
depende de `WebIO.jl`, que requiere una extensión de Jupyter que no está garantizada en
todos los entornos (local, Binder, Colab) y produce el aviso "WebIO not detected" cuando
falta. Este enfoque es equivalente pedagógicamente y funciona en cualquier entorno.
""")
)

nb.cells.append(
    nbf.v4.new_code_cell(r"""# Análisis de sensibilidad: 4 escenarios de shock sobre z1
# (equivalente al slider interactivo de Python, sin necesitar WebIO — ver
# celda markdown anterior para el motivo). En vez de mover un slider,
# llamamos a simulate() una vez por cada z1_final del array z1_scenarios y
# superponemos las 4 trayectorias resultantes en el mismo gráfico.
z1_scenarios = [-1.0, 0.5, 2.0, 3.5]
colors = ["#D95319", "#8EAD3A", "#004C97", "#7A3E9F"]  # paleta UMA, consistente con el resto del cuaderno
t_ax = 0:29

p_a = plot(title="Variable x1", xlabel="Periodos", ylabel="Stock de armamento", legend=:bottomright, legendfontsize=7)
p_b = plot(title="Variable x2", xlabel="Periodos", ylabel="Stock de armamento", legend=:topright, legendfontsize=7)

# zip empareja cada escenario de z1 con su color de la paleta UMA; plot!
# (con !, ver celda del diagrama de fases) añade una línea más al gráfico
# existente en vez de crear uno nuevo, por eso las 4 trayectorias terminan
# superpuestas en el mismo par de ejes. "$(z1_val)" dentro de las comillas
# es INTERPOLACIÓN DE CADENAS: mete el valor de z1_val dentro del texto del
# label — el equivalente Julia de los f-strings de Python.
for (z1_val, col) in zip(z1_scenarios, colors)
    x1_p, x2_p = simulate(params_global, z_initial, [z1_val, 1.0], 30, 2)
    plot!(p_a, t_ax, x1_p, label="z1 → $(z1_val)", color=col, linewidth=2.0)
    plot!(p_b, t_ax, x2_p, label="z1 → $(z1_val)", color=col, linewidth=2.0)
end

# Al ejecutar veremos 2 subplots (x1, x2) con 4 líneas cada uno: cuanto mayor
# el shock de z1, mayor el nuevo estado estacionario alcanzado por ambas
# variables (la dirección la marca theta/eta > 0 en la matriz B).
plot(p_a, p_b, layout=(1,2), size=(900,400),
     plot_title="Sensibilidad al shock de z1",
     plot_titlefontsize=11, top_margin=10mm)
""")
)

# 13. BUENAS PRÁCTICAS
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## 10. Buenas Prácticas Aplicadas en este Laboratorio

Observa que `steady_state()`, `eigenvalues()`, `simulate()` y
`simulate_saddle_path()` están documentadas, tienen restricciones de tipo y viven en
`src/models/ArmsRace.jl` — no en este notebook. La lógica del modelo está separada
de la visualización. Cuando hagas tu ABP, haz lo mismo: funciones reutilizables a `src/`,
el notebook solo para exponer y narrar el análisis.
""")
)

# 14. CONCLUSIÓN
nb.cells.append(nbf.v4.new_markdown_cell(r"""## 11. Conclusión

El mismo sistema dinámico lineal puede mostrar dos comportamientos
cualitativamente distintos según el valor de sus parámetros: estabilidad
global, donde toda perturbación converge suavemente al nuevo equilibrio, o
un punto de silla, donde una variable debe "saltar" instantáneamente para
mantener la convergencia. Esta distinción —y el procedimiento para
detectarla a partir de los autovalores de $A$— es la base que reutilizaremos
en el resto de prácticas (IS-LM dinámico, Dornbusch, DGE) cuando los
sistemas dejen de ser ejemplos genéricos y representen economías reales.
Los resultados numéricos coinciden exactamente con el oráculo MATLAB del
Apéndice B, lo que valida el port a Julia.

**📋 Para terminar**, responde el cuestionario de bitácora de `GUION.md`
(en esta misma carpeta) y, si quieres ir más allá, prueba alguna de sus
extensiones para ABP.
"""))

# 7. BENCHMARK
nb.cells.append(
    nbf.v4.new_markdown_cell("""## 6. Benchmark de Rendimiento (Fase III)
Evaluamos la velocidad de simulación de las trayectorias usando `BenchmarkTools.jl`.""")
)

nb.cells.append(
    nbf.v4.new_code_cell(
        """# Benchmark simulation para un sistema 2D dinámico genérico (no es el modelo
# de Richardson, solo una recursión lineal x[:,t+1] = A*x[:,t] del mismo
# tamaño) — el objetivo es medir cuánto tarda Julia en simular una
# trayectoria de este tipo, para comparar con el tiempo equivalente en
# Python (Fase III del proyecto: rendimiento, no economía).
A_bench = [0.5 0.2; 0.1 0.8]
x0_bench = [1.0, 1.0]
T_bench = 50

# "function nombre(argumentos) ... end" define una FUNCIÓN reutilizable,
# igual que "def" en Python pero terminada con la palabra "end" en vez de
# por indentación. x[:, t] selecciona TODAS las filas (":") de la columna t
# -- aquí cada columna es un periodo de tiempo y cada fila una variable.
function simular_sistema(A_mat, init, T)
    n = length(init)
    x = zeros(n, T)
    x[:, 1] = init
    for t in 1:(T-1)
        x[:, t+1] = A_mat * x[:, t]
    end
    return x
end

# @btime (BenchmarkTools.jl) ejecuta la función muchas veces y muestra el
# tiempo mínimo/medio de ejecución y la memoria asignada — el $ delante de
# las variables evita que BenchmarkTools las trate como globales, lo que
# falsearía la medición de rendimiento.
@btime simular_sistema($A_bench, $x0_bench, $T_bench)
"""
    )
)

# METADATOS DEL CUADERNO (KERNEL DE JULIA)
nb.metadata = {
    "kernelspec": {
        "display_name": "Julia 1.12.6",
        "language": "julia",
        "name": "julia-1.12",
    },
    "language_info": {
        "file_extension": ".jl",
        "mimetype": "application/julia",
        "name": "julia",
        "version": "1.12.6",
    },
}

# Escribir el archivo
dir_path = "practicas/00-introduccion-sistemas-dinamicos/"
os.makedirs(dir_path, exist_ok=True)
notebook_path = os.path.join(dir_path, "julia.ipynb")
nbf.write(nb, notebook_path)
print(f"Notebook generado con éxito en {notebook_path}.")
