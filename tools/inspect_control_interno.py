"""
Inspección del archivo de Control Interno
Consolidado de Avance Julio.xlsx
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")

wb = CalamineWorkbook.from_path(str(path))
print(f"Hojas disponibles ({len(wb.sheet_names)}): {wb.sheet_names}")

# Inspeccionar la primera hoja diaria '26.06'
sheet_name = wb.sheet_names[0]
sheet = wb.get_sheet_by_name(sheet_name)
rows = sheet.to_python()

print(f"\nHoja '{sheet_name}' (Total filas: {len(rows)}):")
for i in range(min(45, len(rows))):
    r = rows[i]
    non_empty = {col_idx: str(val) for col_idx, val in enumerate(r[:10]) if val is not None and str(val).strip() != ""}
    if non_empty:
        print(f"Fila {i+1} (idx {i}): {non_empty}")
