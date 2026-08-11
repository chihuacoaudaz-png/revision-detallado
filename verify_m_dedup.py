import os
import sys
import re
import pandas as pd
from pathlib import Path
from python_calamine import CalamineWorkbook

base_dir = Path(r"c:\Proyectos Python\Detallados")
base_path = base_dir / "Estructura base" / "Rockdrill_Control_Operaciones"

detailed_files = []
for ctr_folder in sorted(base_path.glob("CTR_*")):
    if ctr_folder.name == "CTR_COLQUIJIRCA":
        continue
    ctr_name = ctr_folder.name.replace("CTR_", "").replace("_", " ")
    det_folder = ctr_folder / "02_Detallado"
    search_dir = det_folder if det_folder.exists() else ctr_folder
    for xlsx in search_dir.glob("*.xlsx"):
        if not xlsx.name.startswith("~$"):
            detailed_files.append((ctr_name, xlsx))

print(f"Total archivos detallados a probar: {len(detailed_files)}")

for ctr_name, filepath in detailed_files:
    try:
        wb = CalamineWorkbook.from_path(str(filepath))
        for sheet_name in wb.sheet_names:
            upper_s = sheet_name.upper()
            if upper_s in ["ADITIVOS", "GENERAL", "LISTAS", "TIEMPOS", "HOJA1", "HOJA2", "HOJA3", "RESUMEN", "TABLAS", "COMPA", "R. DETALLADO"] or upper_s.startswith("MAQUINA "):
                continue
            sheet = wb.get_sheet_by_name(sheet_name)
            rows = sheet.to_python()
            if len(rows) < 24:
                continue
            grid_rows = rows[23:]
            row1 = [str(x).strip() if x is not None else "" for x in grid_rows[0]]
            row2 = [str(x).strip() if x is not None else "" for x in grid_rows[1]] if len(grid_rows) > 1 else []
            headers = []
            for i in range(len(row1)):
                v1 = row1[i]
                v2 = row2[i] if i < len(row2) else ""
                if v1 != "" and v2 != "" and v1 != v2:
                    h = f"{v1}_{v2}"
                elif v1 != "":
                    h = v1
                else:
                    h = v2
                if h == "":
                    h = f"COL_{i+1}"
                headers.append(h)
                
            # Check duplicates in headers
            counts = {}
            for h in headers:
                counts[h] = counts.get(h, 0) + 1
            dups = [k for k, v in counts.items() if v > 1]
            if dups:
                print(f"[DUP HEADER] File: {filepath.name} | Sheet: {sheet_name} | Duplicates: {dups}")
    except Exception as e:
        print(f"Error reading {filepath.name}: {e}")
