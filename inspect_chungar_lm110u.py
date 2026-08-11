"""
Inspección detallada de LM110U-001 en CHUNGAR (Filas 38 a 48)
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path_chungar = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_CHUNGAR\02_Detallado\RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR - JULIO.xlsx")
wb_chungar = CalamineWorkbook.from_path(str(path_chungar))
sheet = wb_chungar.get_sheet_by_name("LM110U-001")
rows = sheet.to_python()

print("MUESTRA COMPLETA DE LM110U-001 (Filas 35 a 55):")
for i in range(35, 55):
    r = rows[i]
    print(f"Fila {i+1} (idx {i}): FECHA={r[0]!r} | SONDAJE={r[1]!r} | DESDE={r[5]!r} | HASTA={r[6]!r} | TURNO={r[7]!r} | GRUPO={r[8]!r} | METRAJE={r[9]!r}")
