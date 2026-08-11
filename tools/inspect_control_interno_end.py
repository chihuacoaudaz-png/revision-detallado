"""
Inspección de filas 40 a 140 para ubicar TOTAL AVANCE en Control Interno
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")

wb = CalamineWorkbook.from_path(str(path))
sheet = wb.get_sheet_by_name("26.06")
rows = sheet.to_python()

print("Buscando 'TOTAL' o final de tabla:")
for i, r in enumerate(rows[9:], start=10):
    text_line = " | ".join([f"C{col}:{val}" for col, val in enumerate(r[:10]) if val is not None and str(val).strip() != ""])
    if "TOTAL" in text_line.upper() or i > 120:
        print(f"Fila {i}: {text_line}")
