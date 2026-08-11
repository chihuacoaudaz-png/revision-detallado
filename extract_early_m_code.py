import json
import re

transcript_path = r"C:\Users\PERDLAP33\.gemini\antigravity-ide\brain\c4b1f947-d72c-4609-be55-ee00321fd2af\.system_generated\logs\transcript.jsonl"

found_codes = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if "codigo_m_detallados.txt" in line and "CodeContent" in line:
            try:
                data = json.loads(line)
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    args = tc.get("args", {})
                    if "codigo_m_detallados.txt" in args.get("TargetFile", ""):
                        found_codes.append(args.get("CodeContent", ""))
            except Exception as e:
                pass

print(f"Found {len(found_codes)} versions of codigo_m_detallados.txt in transcript!")
if found_codes:
    print("Version 0 length:", len(found_codes[0]))
    with open(r"c:\Proyectos Python\Detallados\codigo_m\codigo_m_detallados_v0.txt", "w", encoding="utf-8") as out:
        out.write(found_codes[0])
    print("Saved version 0 to codigo_m_detallados_v0.txt")
