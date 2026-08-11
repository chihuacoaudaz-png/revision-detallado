"""
Inspección profunda de filas RAW en Excel para:
1. CHUNGAR: LM110U-001 (especialmente alrededor del 2026-07-05)
2. MOROCOCHA: XRD80USS-011 y XRD150USS-002 (para todas las fechas de junio y julio)
"""
from python_calamine import CalamineWorkbook
from pathlib import Path
import pandas as pd

# 1. Inspeccionar CHUNGAR - LM110U-001
path_chungar = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_CHUNGAR\02_Detallado\RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR - JULIO.xlsx")
wb_chungar = CalamineWorkbook.from_path(str(path_chungar))
sheet_c = wb_chungar.get_sheet_by_name("LM110U-001")
rows_c = sheet_c.to_python()

print("="*80)
print("RAW ROWS CHUNGAR - LM110U-001 (Filas 20 a 60):")
print("="*80)
for i in range(20, min(70, len(rows_c))):
    r = rows_c[i]
    non_empty = {col_idx: str(val) for col_idx, val in enumerate(r) if val is not None and str(val).strip() != ""}
    if non_empty:
        print(f"Fila {i+1} (idx {i}): FECHA={r[0]} | SONDAJE={r[1]} | DESDE={r[5] if len(r)>5 else ''} | HASTA={r[6] if len(r)>6 else ''} | METRAJE={r[9] if len(r)>9 else ''} | TURNO={r[7] if len(r)>7 else ''} | GRUPO={r[8] if len(r)>8 else ''}")

# 2. Inspeccionar MOROCOCHA - XRD80USS-011 y XRD150USS
path_moro = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_MOROCOCHA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance MOROCOCHA - JULIO.xlsx")
wb_moro = CalamineWorkbook.from_path(str(path_moro))

for sname in ["XRD80USS-011", "XRD150USS"]:
    if sname in wb_moro.sheet_names:
        sheet_m = wb_moro.get_sheet_by_name(sname)
        rows_m = sheet_m.to_python()
        print("\n" + "="*80)
        print(f"RAW ROWS MOROCOCHA - {sname}:")
        print("="*80)
        for i in range(20, min(80, len(rows_m))):
            r = rows_m[i]
            non_empty = {col_idx: str(val) for col_idx, val in enumerate(r) if val is not None and str(val).strip() != ""}
            if non_empty:
                print(f"Fila {i+1} (idx {i}): FECHA={r[0]} | SONDAJE={r[1]} | DESDE={r[5] if len(r)>5 else ''} | HASTA={r[6] if len(r)>6 else ''} | METRAJE={r[9] if len(r)>9 else ''} | TURNO={r[7] if len(r)>7 else ''} | GRUPO={r[8] if len(r)>8 else ''}")
