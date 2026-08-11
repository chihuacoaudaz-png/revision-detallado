import json

transcript_path = r"C:\Users\PERDLAP33\.gemini\antigravity-ide\brain\c4b1f947-d72c-4609-be55-ee00321fd2af\.system_generated\logs\transcript_full.jsonl"

found_codes = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if "codigo_m_detallados.txt" in line and "write_to_file" in line:
            try:
                data = json.loads(line)
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    args = tc.get("args", {})
                    content = args.get("CodeContent", "")
                    target = args.get("TargetFile", "")
                    if "codigo_m_detallados.txt" in target and content:
                        found_codes.append(content)
            except Exception as e:
                pass

print(f"Found {len(found_codes)} versions in full transcript")
for i, code in enumerate(found_codes):
    print(f"Version {i}: length {len(code)} lines: {code.count(chr(10))}")
    with open(rf"c:\Proyectos Python\Detallados\codigo_m\codigo_m_detallados_v{i}.txt", "w", encoding="utf-8") as out:
        out.write(code)
