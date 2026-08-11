"""
Script para probar los fixes de limpieza en AMERICANA
"""
import pandas as pd
import numpy as np
import re
from pathlib import Path
from python_calamine import CalamineWorkbook

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_AMERICANA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -JULIO.xlsx")
wb = CalamineWorkbook.from_path(str(filepath))
sheet = wb.get_sheet_by_name("XRD50U-002")
rows = sheet.to_python()

# Skip 22
row_primary = rows[22] # Row 23
row_sub = rows[23]     # Row 24

# Forward fill primary
filled_primary = []
for val in row_primary:
    if val is not None and str(val).strip() != "":
        filled_primary.append(str(val).strip())
    else:
        if filled_primary:
            filled_primary.append(filled_primary[-1])
        else:
            filled_primary.append("XP")

headers = []
for i in range(len(filled_primary)):
    t1 = filled_primary[i]
    t2_raw = row_sub[i] if i < len(row_sub) else None
    t2 = str(t2_raw).strip() if t2_raw is not None else ""
    if t1 == "XP":
        headers.append(t2 if t2 else f"XP_{i}")
    elif t2 == "":
        headers.append(t1)
    else:
        headers.append(f"{t1}_{t2}")

# Desduplicar
seen = {}
unique_headers = []
for h in headers:
    if h in seen:
        seen[h] += 1
        unique_headers.append(f"{h}_{seen[h]}")
    else:
        seen[h] = 0
        unique_headers.append(h)

data_rows = rows[24:]
max_col = len(unique_headers)
norm_rows = [list(r[:max_col]) + [None]*(max_col - len(r)) for r in data_rows]

df = pd.DataFrame(norm_rows, columns=unique_headers)
df.rename(columns={df.columns[0]: "FECHA"}, inplace=True)

# Reemplazar valores vacios por None/NaN
df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

# Fill-down de FECHA antes de filtrar o convertir
df["FECHA"] = df["FECHA"].ffill()

# Filtrar filas donde SONDAJE/segunda columna es nula
second_col = df.columns[1]
df = df[df[second_col].notna()].reset_index(drop=True)

print(f"Total filas filtradas: {len(df)}")
print(df[["FECHA", df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9], df.columns[10]]].head(10))
