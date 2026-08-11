"""
Inspección de Excepciones del Maestro de Máquinas
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

maestro_path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Maestro_Maquinas\Maestros_Maquinas.xlsx")
wb = CalamineWorkbook.from_path(str(maestro_path))
sheet = wb.get_sheet_by_name("Exepciones")
rows = sheet.to_python()

print(f"Total filas en Exepciones: {len(rows)}")
for idx, r in enumerate(rows):
    print(f"Fila {idx+1}: {r}")
