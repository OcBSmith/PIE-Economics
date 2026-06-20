import os
import json

log_path = r"C:\Users\AntonioRC\.gemini\antigravity-ide\brain\0fdfe251-07a4-4597-9b29-043dac53e81a\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_num, line in enumerate(f):
        if "tobin_q.py" in line and "write_to_file" in line:
            try:
                data = json.loads(line)
                for tc in data.get("tool_calls", []):
                    if tc.get("name") == "write_to_file":
                        args = tc.get("arguments", tc.get("args", {}))
                        target = args.get("TargetFile", "")
                        if "tobin_q.py" in target:
                            code = args.get("CodeContent", "")
                            print(f"Line {line_num}: target={target}, code_length={len(code)}")
                            if len(code) > 100:
                                print("START OF CODE:")
                                print(code[:200])
                                print("END OF CODE:")
                                print(code[-200:])
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}")
