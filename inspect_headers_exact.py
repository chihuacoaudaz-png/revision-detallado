"""
Inspección de las columnas producidas antes del renombrado
"""
from python_calamine import CalamineWorkbook
from pathlib import Path
import re

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_AMERICANA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -JULIO.xlsx")
wb = CalamineWorkbook.from_path(str(filepath))
sheet = wb.get_sheet_by_name("XRD50U-002")
rows = sheet.to_python()

# Row 22 (index 21) = Category headers ('AVANCE DIARIO', etc.)
# Row 23 (index 22) = Detail headers ('DESDE', 'HASTA', 'METRAJE', etc.)
# Row 24 (index 23) = Empty

print(f"Row 22 (idx 21): {rows[21][:15]}")
print(f"Row 23 (idx 22): {rows[22][:15]}")
print(f"Row 24 (idx 23): {rows[23][:15]}")
