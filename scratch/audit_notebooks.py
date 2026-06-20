import os
import json
import traceback
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat

def audit_all_notebooks():
    base_dir = 'practicas'
    notebooks = []
    
    # Collect all notebooks
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.ipynb') and not '.ipynb_checkpoints' in root:
                notebooks.append(os.path.join(root, file))
    
    print(f"Encontrados {len(notebooks)} cuadernos para auditar.")
    
    failures = []
    successes = []
    
    for nb_path in notebooks:
        print(f"\nAuditando: {nb_path}...")
        try:
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Setup preprocessor
            # We get the kernel name safely, defaulting to python3 if missing
            kernel_name = nb.metadata.get('kernelspec', {}).get('name', 'python3')
            ep = ExecutePreprocessor(timeout=60, kernel_name=kernel_name)
            
            # Execute
            ep.preprocess(nb, {'metadata': {'path': os.path.dirname(nb_path)}})
            
            # If we get here, it succeeded!
            # Let's save the executed notebook back
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
                
            print(f"[OK] {nb_path} ejecutado con éxito sin errores.")
            successes.append(nb_path)
            
        except Exception as e:
            print(f"[ERROR] en {nb_path}:")
            error_msg = str(e)
            print(error_msg[:1000]) # Print first 1000 chars of error
            failures.append({
                "path": nb_path,
                "error": error_msg
            })
            
    print("\n" + "="*50)
    print("RESUMEN DE AUDITORÍA:")
    print(f"Cuadernos exitosos: {len(successes)} / {len(notebooks)}")
    print(f"Cuadernos con errores: {len(failures)} / {len(notebooks)}")
    if failures:
        print("\nDetalle de fallos:")
        for f in failures:
            print(f"- {f['path']}: {f['error'][:200]}...")
    print("="*50)

if __name__ == '__main__':
    audit_all_notebooks()
