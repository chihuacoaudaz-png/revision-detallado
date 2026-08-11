from python_calamine import CalamineWorkbook
from pathlib import Path
import time

filepath = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_SAN_CRISTOBAL\02_Detallado\RD.402.P.01.F.01 Reporte Detallado de Avance SAN CRISTOBAL -JULIO.xlsx")
t0 = time.time()
wb = CalamineWorkbook.from_path(str(filepath))
sheet = wb.get_sheet_by_name("XRD90U-010")

t1 = time.time()
r1 = sheet.to_python()
print(f"Normal to_python(): {time.time()-t1:.2f}s ({len(r1)} rows)")

t2 = time.time()
r2 = sheet.to_python(skip_empty_area=True)
print(f"skip_empty_area=True: {time.time()-t2:.2f}s ({len(r2)} rows)")
