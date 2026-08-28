import json
import os

path = r"C:\Users\PERDLAP33\.gemini\antigravity-cli\brain\40306d3e-4f62-4ccc-8a7c-0a59dd1e21c4\.system_generated\logs\transcript.jsonl"
print("Searching for Gemini 3.7 and grill/plan...")
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if "gemini" in line.lower() or "3.7" in line.lower() or "flash" in line.lower():
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    print(f"USER: {data.get('content')[:1000]}")
            except Exception as e:
                pass
