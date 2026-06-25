"""Build the MkDocs site: copy notebooks into docs/, then run mkdocs build."""

import glob
import os
import shutil

# Clean and recreate docs/practicas
if os.path.exists("docs/practicas"):
    shutil.rmtree("docs/practicas")

# Copy all practice folders
for practice_dir in sorted(glob.glob("practicas/*/")):
    dest = os.path.join("docs", practice_dir)
    shutil.copytree(
        practice_dir,
        dest,
        ignore=shutil.ignore_patterns(".ipynb_checkpoints", "__pycache__", "*.pyc"),
    )
    print(f"Copied: {practice_dir} -> {dest}")

# Copy root index.md and guia-profesor.md into docs/.
# The root files are the source of truth; docs/index.md and
# docs/guia-profesor.md are gitignored build artifacts overwritten here.
for f in ["index.md", "guia-profesor.md"]:
    if os.path.exists(f):
        shutil.copy(f, os.path.join("docs", f))
        print(f"Copied: {f} -> docs/{f}")

print("Done. Run: .venv/Scripts/python.exe -m mkdocs build --site-dir site")
