import os
import json

GUIDES = {
    "00": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Sistemas Dinámicos
*   **¿Qué estamos haciendo aquí?** Estamos estudiando cómo una variable cambia a lo largo del tiempo usando reglas matemáticas sencillas. Imagina que es el crecimiento de una población o el saldo de tu cuenta bancaria.
*   **Puntos de Equilibrio (Estado Estacionario):** Es el valor donde la variable se queda quieta (no sube ni baja).
*   **Estabilidad:** Si perturbas el sistema (le das un empujón), ¿vuelve al equilibrio (estable) o se dispara al infinito (inestable)?
*   **¡Prueba esto!** Busca donde se definen las matrices o ecuaciones, ejecuta las celdas con `Shift + Enter` y observa cómo las flechas del diagrama de fases te indican hacia dónde viaja el sistema.""",

    "01": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - IS-LM Dinámico
*   **¿Qué estamos haciendo aquí?** Simulamos una economía cerrada. El tipo de interés y la producción se ajustan según la oferta y demanda de bienes y dinero.
*   **Controles clave para cambiar:** 
    *   `m0`: La oferta de dinero (política monetaria).
    *   `beta0`: El gasto del gobierno (política fiscal).
*   **El Shock:** Si subes `m0` (imprimir dinero), verás que a corto plazo el PIB sube y los intereses bajan. Pero a largo plazo, el PIB vuelve a su sitio y solo suben los precios (neutralidad del dinero).
*   **¡Prueba esto!** Usa los deslizadores interactivos al final del cuaderno para arrastrar y ver la animación del shock en vivo.""",

    "02": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Overshooting de Dornbusch
*   **¿Qué estamos haciendo aquí?** Analizamos cómo responde el tipo de cambio (el valor de la moneda) ante un shock.
*   **La gran idea (Sobrerreacción):** Como los precios de los supermercados tardan mucho en cambiar (son rígidos), el mercado financiero (tipo de cambio) reacciona con un "salto" exagerado al principio para compensar.
*   **¡Prueba esto!** Cambia la oferta monetaria `m0` en la simulación y observa la línea del tipo de cambio dar un salto enorme antes de estabilizarse lentamente en su nuevo valor.""",

    "03": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Consumo y Ahorro
*   **¿Qué estamos haciendo aquí?** Decidiendo cómo un consumidor debe repartir su dinero entre consumir hoy y ahorrar para mañana a lo largo de su vida.
*   **El dilema:** Si consumes todo hoy, pasas hambre mañana. Si ahorras todo, pasas hambre hoy. El modelo calcula el equilibrio óptimo (suavización del consumo).
*   **¡Prueba esto!** Cambia la tasa de interés o la paciencia del consumidor (factor de descuento) y observa cómo cambia la curva de consumo a lo largo del tiempo.""",

    "04": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Consumo y Ocio
*   **¿Qué estamos haciendo aquí?** Decidiendo cuántas horas trabajar (para tener dinero y consumir) frente a cuántas horas descansar (ocio).
*   **Efecto Sustitución vs Efecto Renta:** Si te suben el sueldo, ¿trabajas más porque cada hora vale más (sustitución) o trabajas menos porque ya eres rico y quieres descansar (renta)?
*   **¡Prueba esto!** Modifica el salario base en el código y observa si el gráfico de horas trabajadas sube o baja.""",

    "05": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Gobierno y Política Fiscal
*   **¿Qué estamos haciendo aquí?** Estudiando cómo afectan los impuestos del gobierno a las decisiones de las personas.
*   **Impuestos Distorsionadores:** Cuando el gobierno cobra impuestos sobre el trabajo, la gente decide trabajar menos porque se queda con menos dinero neto.
*   **¡Prueba esto!** Incrementa la tasa impositiva (los impuestos) en el modelo y observa la caída en el consumo y en las horas de trabajo.""",

    "06": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Q de Tobin (Inversión)
*   **¿Qué estamos haciendo aquí?** Explicando cuándo decide una empresa comprar más maquinaria e invertir.
*   **La Regla de la Q:** Si la Q de Tobin es mayor que 1.0, significa que la empresa vale más en bolsa de lo que cuesta comprar sus máquinas. ¡Es hora de invertir y expandirse! Si es menor que 1.0, no conviene invertir.
*   **¡Prueba esto!** Cambia la tasa de interés y observa cómo el ratio Q cae o sube, arrastrando consigo la inversión de la empresa.""",

    "07": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Equilibrio General Dinámico (DGE)
*   **¿Qué estamos haciendo aquí?** Uniendo a los consumidores, empresas y mercado en un solo gran simulador macroeconómico.
*   **El Ciclo Económico:** Simulamos cómo un shock tecnológico (un aumento repentino de productividad) hace que aumenten a la vez el PIB, la inversión y el consumo.
*   **¡Prueba esto!** Ejecuta la celda del shock tecnológico y observa el gráfico en forma de "joroba" que muestra la propagación de la bonanza en la economía.""",

    "08": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Modelo de Crecimiento de Solow-Swan
*   **¿Qué estamos haciendo aquí?** Analizando por qué crecen los países a largo plazo y cómo acumulan capital (maquinaria).
*   **La Regla de Oro:** Ahorrar más es bueno porque permite comprar más máquinas, pero si ahorras demasiado, no te queda dinero para consumir. Existe una "tasa de ahorro óptima" que maximiza el bienestar.
*   **¡Prueba esto!** Sube la tasa de ahorro y observa cómo la economía transiciona hacia un nivel de riqueza permanente más alto.""",

    "09": """### 🕹️ GUÍA RÁPIDA PARA DUMMIES - Modelo de Ramsey-Cass-Koopmans
*   **¿Qué estamos haciendo aquí?** Es como el modelo de Solow, pero aquí la tasa de ahorro no es fija; la gente la elige libremente para maximizar su felicidad a lo largo de las generaciones.
*   **Senda Estable:** El modelo calcula la única trayectoria (saddle path) que evita que la economía se quede sin capital o acumule máquinas inútiles.
*   **¡Prueba esto!** Aplica un shock de productividad (TFP) y mira cómo las familias ajustan instantáneamente su consumo actual para situarse en la nueva senda de crecimiento estable."""
}

INTRO = """> **👋 BIENVENIDA A LA PRÁCTICA - LEER ANTES DE EMPEZAR**
> 
> *   **¿Nunca has usado Jupyter?** No te preocupes. Este cuaderno es interactivo. Haz clic en cualquier celda de código y pulsa **`Shift + Enter`** para ejecutarla. Ve de arriba a abajo en orden.
> *   **¿Se ha congelado o sale un asterisco `[*]` eterno?** Ve al menú superior y dale a `Kernel` ➔ `Restart`.
> *   **El objetivo** de esta práctica es que juegues con la economía. Cambia los números del código que representan impuestos, dinero o tecnología, vuelve a ejecutar y mira los gráficos. ¡No puedes romper nada!
>
"""

def inject_dummies_guide():
    base_dir = 'practicas'
    count = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.ipynb') and not '.ipynb_checkpoints' in root:
                filepath = os.path.join(root, file)
                # Find practice number from path (e.g. 01-is-lm-dinamico -> 01)
                parts = root.replace('\\', '/').split('/')
                folder_name = next((p for p in parts if p and p[0].isdigit() and len(p) >= 2), None)
                if not folder_name:
                    continue
                p_num = folder_name[:2]
                if p_num not in GUIDES:
                    continue
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
                
                # Check if we already injected it
                source_check = "BIENVENIDA A LA PRÁCTICA"
                already_injected = False
                for cell in notebook['cells']:
                    if cell['cell_type'] == 'markdown' and any(source_check in line for line in cell['source']):
                        already_injected = True
                        break
                
                if already_injected:
                    print(f"Ya inyectado en {filepath}")
                    continue
                
                # Create the dummies guide cell
                guide_content = INTRO + "\n" + GUIDES[p_num]
                new_cell = {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [line + "\n" for line in guide_content.split('\n')]
                }
                
                # Insert right after the header cell (usually index 1)
                notebook['cells'].insert(1, new_cell)
                
                # Write back
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(notebook, f, indent=1, ensure_ascii=False)
                print(f"¡Guía inyectada con éxito en {filepath}!")
                count += 1
    print(f"Proceso completado. Se han actualizado {count} cuadernos.")

if __name__ == '__main__':
    inject_dummies_guide()
