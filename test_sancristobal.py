from python_calamine import CalamineWorkbook
from pathlib import Path
import time

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_SAN_CRISTOBAL\02_Detallado\RD.402.P.01.F.01 Reporte Detallado de Avance SAN CRISTOBAL -JULIO.xlsx")
t0 = time.time()
wb = CalamineWorkbook.from_path(str(filepath))
print(f"wb loaded in {time.time()-t0:.2f}s, sheet names: {wb.sheet_names}")
for sheet_name in wb.sheet_names:
    t1 = time.time()
    s = wb.get_sheet_by_name(sheet_name)
    r = s.to_python()
    print(f"  Sheet '{sheet_name}' read in {time.time()-t1:.2f}s ({len(r)} rows)")
