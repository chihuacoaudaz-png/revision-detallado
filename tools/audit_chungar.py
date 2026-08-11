"""
Auditoria profunda de Chungar y Morococha
Compara fila a fila del Excel original vs el resultado extraído por Python vs Control Interno
"""
import pandas as pd
from python_calamine import CalamineWorkbook
from pathlib import Path
import unicodedata
import re

# 1. INSPECCIONAR CHUNGAR
path_chungar = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_CHUNGAR\02_Detallado\RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR - JULIO.xlsx")
wb_c = CalamineWorkbook.from_path(str(path_chungar))

print("="*90)
print("AUDITORIA CHUNGAR - HOJAS OPERATIVAS:")
print("="*90)
for sname in wb_c.sheet_names:
    if sname in ("ADITIVOS", "GENERAL", "LISTAS", "Tiempos", "Hoja1"):
        continue
    sheet = wb_c.get_sheet_by_name(sname)
    rows = sheet.to_python()
    rows_valid = [r for r in rows[24:] if any(v is not None and str(v).strip() != "" for v in r)]
    
    # Sumar metraje directo de la columna 9 (o index 9 / index 6 según columna)
    # Veamos los encabezados primero
    h23 = rows[22] if len(rows) > 22 else []
    h24 = rows[23] if len(rows) > 23 else []
    
    print(f"\nHoja '{sname}' (Total filas de datos: {len(rows_valid)}):")
    for idx, r in enumerate(rows_valid):
        fecha = r[0] if len(r) > 0 else None
        sondaje = r[1] if len(r) > 1 else None
        desde = r[5] if len(r) > 5 else None
        hasta = r[6] if len(r) > 6 else None
        turno = r[7] if len(r) > 7 else None
        grupo = r[8] if len(r) > 8 else None
        metraje = r[9] if len(r) > 9 else None
        
        # Buscar el 05-07 o fechas cercanas
        if str(fecha) in ("2026-07-05", "2026-07-04", "2026-07-06") or "05/07" in str(fecha) or "2026-07-05 00:00:00" in str(fecha):
            print(f"  Fila {idx+25}: FECHA={fecha} | SONDAJE={sondaje} | DESDE={desde} | HASTA={hasta} | METRAJE={metraje} | TURNO={turno} | GRUPO={grupo}")

