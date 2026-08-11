"""
Inspección profunda de las diferencias en Morococha:
1. 2026-06-27 (XRD80USS-011)
2. 2026-07-04 (XRD80USS-011)
3. 2026-07-18 (XRD150USS-002 / XRD150USS)
4. 2026-07-21 (XRD150USS-002 / XRD150USS)
"""
from python_calamine import CalamineWorkbook
from pathlib import Path

path_moro = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\CTR_MOROCOCHA\02_Detallado\RD.402.P.01.F.01  Reporte Detallado de Avance MOROCOCHA - JULIO.xlsx")
wb_moro = CalamineWorkbook.from_path(str(path_moro))

for sname in ["XRD80USS-011", "XRD150USS"]:
    if sname in wb_moro.sheet_names:
        sheet = wb_moro.get_sheet_by_name(sname)
        rows = sheet.to_python()
        print("\n" + "="*90)
        print(f"TODAS LAS FILAS CON DATOS EN MOROCOCHA - HOJA: {sname}")
        print("="*90)
        for i in range(22, min(90, len(rows))):
            r = rows[i]
            if any(v is not None and str(v).strip() != "" for v in r):
                fecha = r[0] if len(r) > 0 else ""
                sondaje = r[1] if len(r) > 1 else ""
                desde = r[5] if len(r) > 5 else ""
                hasta = r[6] if len(r) > 6 else ""
                turno = r[7] if len(r) > 7 else ""
                grupo = r[8] if len(r) > 8 else ""
                metraje = r[9] if len(r) > 9 else ""
                horas_ex = r[10] if len(r) > 10 else ""
                print(f"Fila {i+1:2d} (idx {i:2d}): FECHA={fecha!r:15s} | SONDAJE={sondaje!r:15s} | DESDE={desde!r:6s} | HASTA={hasta!r:6s} | METRAJE={metraje!r:6s} | TURNO={turno!r:4s} | GRUPO={grupo!r:4s}")
