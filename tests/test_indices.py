"""
Verificación de indices sin skip_empty_area=True vs con skip_empty_area=True
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_AMERICANA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -JULIO.xlsx")
wb = CalamineWorkbook.from_path(str(filepath))
sheet = wb.get_sheet_by_name("XRD50U-002")

rows1 = sheet.to_python()
print("SIN skip_empty_area:")
print(f"  Fila index 22: {rows1[22][:5]}")
print(f"  Fila index 23: {rows1[23][:5]}")

rows2 = sheet.to_python(skip_empty_area=True)
print("\nCON skip_empty_area:")
print(f"  Fila index 22: {rows2[22][:5]}")
print(f"  Fila index 23: {rows2[23][:5]}")
