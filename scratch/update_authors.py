import os
import subprocess


def update_authors():
    files = [f"generate_p{i}_julia_notebook.py" for i in range(10)]

    target = "- **Autores:** Antonio F. Romero Carrasco, Anelí Bongers"
    replacement = "- **Autores:** Dr. Antonio F. Romero Carrasco, Dra. Anelí Bongers"

    for filename in files:
        if os.path.exists(filename):
            print(f"Modificando {filename}...")
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            if target in content:
                content = content.replace(target, replacement)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  -> Modificado con éxito.")
            else:
                print(f"  -> No se encontró el texto exacto.")

            # Ejecutar el script para regenerar el notebook
            print(f"Regenerando notebook con {filename}...")
            subprocess.run([".venv\\Scripts\\python", filename], check=True)


if __name__ == "__main__":
    update_authors()
