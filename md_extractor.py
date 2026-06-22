import json
import re

# Reemplazos de texto copy-paste que no aplican a Julia (Bloque A del plan de
# homogeneización, docs/PLAN_HOMOGENEIZACION_JULIA.md). Se aplican a todas
# las celdas markdown porque estos términos solo aparecen en contextos donde
# el texto Python no es correcto para la versión Julia (nombres de archivo,
# librerías de testing/optimización/resolución de sistemas, nombres de tipos).
_TEXT_REPLACEMENTS = [
    (r"\.py\b", ".jl", 0),
    (r"\bcvxpy\b", "solve_direct_optim", re.IGNORECASE),
    (r"\bpytest\b", "Test.jl", re.IGNORECASE),
    (r"SciPy fsolve", "NLsolve.jl", 0),
    (r"scipy\.optimize\.fsolve", "NLsolve.jl", 0),
    (r"\bDornbuschParameters\b", "DornbuschParams", 0),
    (r"\bRamseyParameters\b", "RamseyParams", 0),
    (r"Simulación Python", "Simulación Julia", 0),
]


def _adapt_text_for_julia(source):
    for pattern, replacement, flags in _TEXT_REPLACEMENTS:
        source = re.sub(pattern, replacement, source, flags=flags)
    return source


def get_markdown_cells(notebook_path):
    """
    Reads a Jupyter Notebook and returns a list of all markdown cells' source text,
    adaptado al texto y terminología de la versión Julia.
    """
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    md_cells = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown":
            source = "".join(cell.get("source", []))
            # Adaptación del título: solo en la primera línea, para no
            # pegar " (Julia)" al final de objetivos u otro contenido que
            # pueda venir en la misma celda que el título.
            if source.startswith("# Práctica"):
                lines = source.split("\n", 1)
                lines[0] = lines[0].replace("Práctica", "LAB-") + " (Julia)"
                source = "\n".join(lines)
            source = _adapt_text_for_julia(source)
            md_cells.append(source)

    return md_cells
