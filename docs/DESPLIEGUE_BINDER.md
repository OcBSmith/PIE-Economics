# ☁️ Guía de Ejecución y Despliegue en MyBinder

**MyBinder.org** es un servicio libre que permite abrir y ejecutar nuestros cuadernos Jupyter interactivos en la nube, directamente en el navegador, **sin tener que instalar nada localmente**. Es ideal para compartir el laboratorio virtual con alumnos y otros docentes.

---

## 🕹️ 1. Cómo acceder y usar el entorno interactivo

Para abrir los cuadernos de prácticas en Binder con todo el entorno preconfigurado (Python, Julia y deslizadores interactivos), solo tienes que hacer clic en el siguiente enlace:

👉 **[Abrir Laboratorios Virtuales en MyBinder](https://mybinder.org/v2/gh/OcBSmith/PIE-Economics/main?labpath=practicas)**

### 💡 Qué ocurre al abrir el enlace:
1. **MyBinder** creará de forma transparente una máquina virtual en la nube.
2. Leerá las dependencias de Python (`requirements.txt`) e instalará paquetes como `numpy`, `scipy` y `matplotlib`.
3. Leerá el entorno de Julia (`Project.toml` y `Manifest.toml`) e instalará el lenguaje Julia y sus resolvedores.
4. Te redirigirá a una interfaz de **Jupyter Lab** donde verás la carpeta `practicas/` con todas las carpetas (P0 a P9).
5. Podrás abrir los cuadernos `.ipynb` de Julia o Python y ejecutar las celdas usando **`Shift + Enter`** en tiempo real.

---

## 🛠️ 2. Cómo desplegar tus propios cambios en MyBinder

Si realizas modificaciones en el código o en los cuadernos del repositorio local y deseas actualizar la versión en la nube para tus compañeros, sigue estos sencillos pasos:

### Paso A: Sube tus cambios a GitHub
Desde tu terminal local, registra y sube los cambios al repositorio público:
```bash
git add .
git commit -m "feat: descripción de tus cambios"
git push origin main
```

### Paso B: Binder compilará la nueva versión automáticamente
Al ser un repositorio público conectado, MyBinder detectará el nuevo commit. La próxima vez que alguien haga clic en tu enlace de Binder:
* Binder iniciará una fase de compilación (**building phase**) automática de la nueva imagen de Docker.
* Esto tarda unos pocos minutos. Una vez completado, todo el mundo accederá a la nueva versión actualizada.

---

## 🔗 3. Cómo personalizar tu enlace de Binder
Si quieres generar enlaces específicos (por ejemplo, para que los alumnos entren directamente a la práctica de Ramsey o IS-LM):

1. Ve a [mybinder.org](https://mybinder.org/).
2. En **GitHub repository name or URL**, pega la dirección de tu repositorio:
   `https://github.com/OcBSmith/PIE-Economics`
3. En **Path to a notebook file**, selecciona `URL` en lugar de `File` e introduce:
   `lab/tree/practicas/09-ramsey/python.ipynb` (por ejemplo, para abrir el cuaderno de Python de Ramsey directamente).
4. Copia el enlace acortado que Binder genera abajo en la sección **"Copy the URL below to share this Binder"** y compártelo.
