"""
Script de inspección detallada de las filas 20 a 35 de AMERICANA XRD50U-002
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_AMERICANA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -JULIO.xlsx")
wb = CalamineWorkbook.from_path(str(path))
sheet = wb.get_sheet_by_name("XRD50U-002")
rows = sheet.to_python()

print(f"Total filas: {len(rows)}")
for idx in range(20, min(35, len(rows))):
    print(f"Fila {idx+1} (index {idx}): {rows[idx][:25]}")
