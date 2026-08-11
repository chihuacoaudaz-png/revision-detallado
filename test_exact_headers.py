"""
Script de prueba para verificar que con row_primary_idx=22 (Fila 23) y row_sub_idx=23 (Fila 24),
los nombres de columnas coinciden EXACTAMENTE con el diccionario M y resultan 100% poblados.
"""
from python_calamine import CalamineWorkbook
from pathlib import Path
import pandas as pd
import numpy as np

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_AMERICANA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -JULIO.xlsx")
wb = CalamineWorkbook.from_path(str(filepath))
sheet = wb.get_sheet_by_name("XRD50U-002")
rows = sheet.to_python()

# Table.Skip([Data], 22) -> Row 23 is index 22, Row 24 is index 23
primary_values = rows[22]
sub_values = rows[23]

filled_primary = []
for val in primary_values:
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
    t2_raw = sub_values[i] if i < len(sub_values) else None
    t2 = str(t2_raw).strip() if t2_raw is not None else ""
    if t1 == "XP":
        headers.append(t2 if t2 else f"XP_{i}")
    elif t2 == "":
        headers.append(t1)
    else:
        headers.append(f"{t1}_{t2}")

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
norm_rows = [list(r[:max_col]) + [None]*(max_col - len(r)) for r in data_rows if any(v is not None and str(v).strip() != "" for v in r)]

df = pd.DataFrame(norm_rows, columns=unique_headers)
df.rename(columns={df.columns[0]: "FECHA"}, inplace=True)
df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
df["FECHA"] = df["FECHA"].ffill()

second_col = df.columns[1]
df = df[df[second_col].notna()].reset_index(drop=True)

print("Encabezados generados:")
print(unique_headers[:25])

# Renombrar con diccionario
rename_dict = {
    "NOMBRE": "SONDAJE",
    "PROFUNDIDAD": "PROFUNDIDAD DE SONDAJE",
    "HORAS EXTAS": "HORAS EXTRAS",
    "AYUDANTE_1": "AYUDANTE 2"
}
df.rename(columns=rename_dict, inplace=True)

print("\nPrimeras 5 filas con columnas renombradas:")
cols = ["FECHA", "SONDAJE", "PROFUNDIDAD DE SONDAJE", "LINEA", "INCLINACIÓN", "DESDE", "HASTA", "TURNO (A=1;B=2)", "GRUPO", "METRAJE", "HORAS EXTRAS", "PERFORISTA", "AYUDANTE", "AYUDANTE 2"]
print(df[cols].head(5))
