# 🚀 Guía de Macroeconomía Computacional para Principiantes (¡Para Dummies!)

¡Hola! Si estás aquí, probablemente seas estudiante de economía y tal vez no tengas ni idea de programación ni de matemáticas súper avanzadas. **No te preocupes.** Esta guía está diseñada para que entiendas el proyecto desde cero, sin tecnicismos raros.

---

## 🧭 1. ¿Qué es un "Modelo Macroeconómico" en un Ordenador?

Imagínate que la economía es como un **simulador de vuelo** o un videojuego de estrategia (como *SimCity*). No podemos experimentar con la economía real (no podemos subir los impuestos un 50% solo para ver qué pasa, porque arruinaríamos a la gente). 

Por eso, los economistas creamos una "maqueta" matemática de la economía en el ordenador. En esta maqueta hay:

*   **Los Controles (Parámetros y Exógenas):** Son las palancas que tú puedes tocar. Por ejemplo: cuánto ahorra la gente, los impuestos que pone el gobierno o la cantidad de dinero que imprime el banco central.
*   **Los Indicadores (Variables Endógenas):** Son los resultados que calcula la maqueta. Por ejemplo: el PIB (la riqueza del país), el empleo, los precios de las cosas o el tipo de cambio de la moneda.
*   **El Shock:** Es un evento repentino. Imagina que el banco central imprime un montón de billetes de golpe (un "shock monetario") o que el gobierno decide gastar el doble en carreteras (un "shock fiscal"). El simulador nos muestra la película de cómo reacciona la economía día a día tras ese evento.

---

## 📓 2. Tu Consola de Control: ¿Qué es Jupyter Notebook?

Para jugar con estos simuladores usamos una herramienta llamada **Jupyter Notebook**. 
Piensa en Jupyter como un documento interactivo en tu navegador web. Tiene dos tipos de bloques (llamados **Celdas**):

1.  **Celdas de Texto:** Te explican la teoría de forma sencilla, con gráficos y fórmulas.
2.  **Celdas de Código:** Tienen código de programación (en un lenguaje llamado Julia). **No tienes que saber programar para usarlas.** Solo son las tripas del simulador.

### 🕹️ Los 3 Controles Básicos que Debes Conocer:

*   **El botón de "Play" (`Shift + Enter`):** Para hacer que una celda funcione, haz clic en ella y presiona las teclas **`Shift` y `Enter`** a la vez en tu teclado. Verás que se ejecuta el código y pasa a la siguiente celda. **Debes ir ejecutándolas en orden de arriba a abajo.**
*   **El asterisco `[*]`:** Cuando ejecutas una celda de código, verás que a la izquierda aparece `In [*]`. Eso significa que el ordenador está calculando. Cuando termina, el asterisco se cambia por un número (ej. `In [5]`).
*   **El Botón de Emergencia (Reiniciar Kernel):** Si el ordenador se queda colgado, o el asterisco `[*]` no desaparece tras un minuto, ve al menú superior de Jupyter y haz clic en **`Kernel` ➔ `Restart`** (o en el botón con una flecha circular). Esto reiniciará el motor del simulador para que puedas empezar de nuevo limpio.

---

## 📈 3. ¿Cómo hacer tu primera simulación y cambiar parámetros?

Hagamos un experimento rápido. Si estás viendo un cuaderno de simulación (como el de Dornbusch o el de IS-LM):

1.  Busca una celda de código donde se definan los valores iniciales. Se verá algo así:
    ```julia
    # z = [gasto_gobierno, dinero, productividad, ...]
    z_initial = [500.0, 100.0, 2000.0, 3.0, 0.0]
    z_final   = [500.0, 101.0, 2000.0, 3.0, 0.0]
    ```
2.  **¡Cambia los números!** Si quieres ver qué pasa si el gobierno gasta mucho más, cambia ese `500.0` por `600.0` en `z_final`.
3.  Vuelve a pulsar **`Shift + Enter`** en esa celda y en las celdas de gráficos de abajo.
4.  **¡Mira el gráfico!** El gráfico se actualizará automáticamente mostrando la nueva trayectoria de la economía con tu cambio.

---

## 📊 4. ¿Cómo leer los gráficos resultantes?

Cuando el simulador dibuja las respuestas de la economía, verás gráficos de este estilo:

*   **Eje Horizontal (Eje X):** Representa el tiempo (pueden ser trimestres, meses o años). El shock suele ocurrir en el periodo 1 o 5.
*   **Eje Vertical (Eje Y):** Muestra el valor de la variable (el PIB, la tasa de interés, etc.).
*   **El "Salto" (Overshooting):** En algunos modelos (como el de Dornbusch), verás que tras el shock, la línea morada del tipo de cambio da un salto enorme hacia arriba de golpe y luego va bajando poco a poco. Eso es el "overshooting": el mercado financiero reacciona de forma exagerada al principio porque los precios de las tiendas tardan meses en subir.
*   **El Largo Plazo:** Al final del gráfico (hacia la derecha), verás que las líneas se estabilizan. Ese es el nuevo "estado estacionario", el destino final donde descansa la economía una vez que pasa la tormenta del shock.
