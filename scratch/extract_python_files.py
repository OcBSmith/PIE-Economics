import os
import json

def decode_val(val):
    if isinstance(val, str):
        if val.startswith('"') and val.endswith('"'):
            try:
                return json.loads(val)
            except Exception as e:
                return val[1:-1].replace('\\\\', '\\').replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
    return val

brain_dir = r"C:\Users\AntonioRC\.gemini\antigravity-ide\brain"
recovered_dir = r"C:\Users\AntonioRC\Desktop\PIE\scratch\recovered"
os.makedirs(recovered_dir, exist_ok=True)

# Scan all logs
log_files = []
for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "transcript.jsonl":
            log_files.append(os.path.join(root, file))

for log_file in log_files:
    conv_id = os.path.basename(os.path.dirname(os.path.dirname(log_file)))
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                if "write_to_file" not in line:
                    continue
                try:
                    data = json.loads(line)
                    for tc in data.get("tool_calls", []):
                        if tc.get("name") == "write_to_file":
                            args = tc.get("args", tc.get("arguments", {}))
                            if not args:
                                continue
                            target = decode_val(args.get("TargetFile", ""))
                            code = decode_val(args.get("CodeContent", ""))
                            if target and code:
                                filename = os.path.basename(target)
                                if filename.endswith(".py"):
                                    timestamp = data.get("created_at", data.get("timestamp", ""))
                                    safe_time = timestamp.replace(":", "-")
                                    out_name = f"{filename}_{conv_id}_{safe_time}.py"
                                    out_path = os.path.join(recovered_dir, out_name)
                                    with open(out_path, 'w', encoding='utf-8') as out_f:
                                        out_f.write(code)
                                    print(f"Dumped {filename} from {conv_id} length={len(code)}")
                except Exception as e:
                    pass
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
