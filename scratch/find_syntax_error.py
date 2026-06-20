import ast

with open('generate_notebook.py', 'r', encoding='utf-8') as f:
    code = f.read()

try:
    ast.parse(code)
    print("No AST compile errors found!")
except SyntaxError as e:
    print(f"SyntaxError found: {e}")
    print(f"Line: {e.lineno}, Offset: {e.offset}")
    print(f"Text: {e.text}")
