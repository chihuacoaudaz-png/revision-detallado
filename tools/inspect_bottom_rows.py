"""
Inspeccionar filas de pie de página (totales) en Chungar y Morococha
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path_c = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_CHUNGAR\02_Detallado\RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR - JULIO.xlsx")
wb_c = CalamineWorkbook.from_path(str(path_c))

print("FILAS AL FINAL DE LA HOJA EN CHUNGAR - LM110U-001 (Filas 50 a 70):")
sheet = wb_c.get_sheet_by_name("LM110U-001")
rows = sheet.to_python()
for i in range(50, len(rows)):
    r = rows[i]
    if any(v is not None and str(v).strip() != "" for v in r):
        print(f"Fila {i+1} (idx {i}): {r[:10]}")
