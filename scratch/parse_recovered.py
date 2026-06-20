import os

path = "scratch/recovered/dornbusch.py_.system_generated_2026-06-19T10-53-58Z.py"
size = os.path.getsize(path)
print("File size on disk:", size)

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

print("Actual content length:", len(content))
print("Last 200 characters of content:")
print(repr(content[-200:]))
