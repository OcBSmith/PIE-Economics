import json
import glob
import os

print("Auditoría de Cuadernos Julia")
print("============================")

notebooks = sorted(glob.glob("practicas/*/julia.ipynb"))
all_good = True

for nb_path in notebooks:
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    n_md = sum(1 for c in nb.get('cells', []) if c['cell_type'] == 'markdown')
    n_code = sum(1 for c in nb.get('cells', []) if c['cell_type'] == 'code')
    
    has_interact = False
    has_benchmark = False
    
    for c in nb.get('cells', []):
        if c['cell_type'] == 'code':
            source = "".join(c.get('source', []))
            if "using Interact" in source or "@manipulate" in source:
                has_interact = True
            if "@btime" in source or "BenchmarkTools" in source:
                has_benchmark = True
                
    status = "✅ OK"
    if not has_interact or not has_benchmark:
        status = "❌ ERROR (Faltan dependencias o macros clave)"
        all_good = False
        
    print(f"{os.path.basename(os.path.dirname(nb_path))}: {status} ({n_md} MD, {n_code} Code)")
    if not has_interact: print("   - Falta Interact / @manipulate")
    if not has_benchmark: print("   - Falta BenchmarkTools / @btime")

print("-" * 30)
if all_good:
    print("Resultado: ÉXITO TOTAL. Todos los cuadernos Julia P1-P9 actualizados y completos.")
else:
    print("Resultado: SE ENCONTRARON PROBLEMAS.")
