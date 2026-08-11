import os
import sys
import re
import pandas as pd
from pathlib import Path
from python_calamine import CalamineWorkbook

base_dir = Path(r"c:\Proyectos Python\Detallados")
base_path = base_dir / "Estructura base" / "Rockdrill_Control_Operaciones"

print("="*80)
print("INSPECCIÓN DE VALORES RAW EN COLUMNA TURNO POR PROYECTO (CTR)")
print("="*80)

ctr_turn_values = {}

for ctr_folder in sorted(base_path.glob("CTR_*")):
    if ctr_folder.name == "CTR_COLQUIJIRCA":
        continue
    ctr_name = ctr_folder.name.replace("CTR_", "").replace("_", " ")
    det_folder = ctr_folder / "02_Detallado"
    search_dir = det_folder if det_folder.exists() else ctr_folder
    
    ctr_turn_values[ctr_name] = set()
    
    for xlsx in search_dir.glob("*.xlsx"):
        if xlsx.name.startswith("~$"):
            continue
        try:
            wb = CalamineWorkbook.from_path(str(xlsx))
            for sheet_name in wb.sheet_names:
                upper_s = sheet_name.upper()
                if upper_s in ["ADITIVOS", "GENERAL", "LISTAS", "TIEMPOS", "HOJA1", "HOJA2", "HOJA3", "RESUMEN", "TABLAS", "COMPA", "R. DETALLADO"] or upper_s.startswith("MAQUINA "):
                    continue
                sheet = wb.get_sheet_by_name(sheet_name)
                rows = sheet.to_python()
                if len(rows) < 24:
                    continue
                grid_rows = rows[24:]
                for r in grid_rows:
                    val_t = str(r[7]).strip().upper() if len(r) > 7 and r[7] is not None else ""
                    if val_t != "":
                        ctr_turn_values[ctr_name].add(val_t)
        except Exception as e:
            pass

for ctr, val_set in sorted(ctr_turn_values.items()):
    print(f"CTR: {ctr:<20} | Valores RAW de TURNO: {sorted(list(val_set))}")
