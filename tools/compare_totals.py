"""
Comparación preliminar de totales acumulados por CTR:
Detallados Consolidados vs Control Interno
"""
import pandas as pd
import numpy as np
import unicodedata
from python_calamine import CalamineWorkbook
from pathlib import Path

# 1. Cargar Detallados Consolidados
df_det = pd.read_csv("output/detallados_consolidados.csv")
det_totals = df_det.groupby("CTR")["METRAJE"].sum().reset_index()
det_totals.rename(columns={"METRAJE": "METRAJE_DETALLADOS"}, inplace=True)

# 2. Cargar Control Interno
path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")
wb = CalamineWorkbook.from_path(str(path))

ci_rows = []
for sheet_name in wb.sheet_names:
    if not sheet_name.replace(".", "").isdigit():
        continue
    sheet = wb.get_sheet_by_name(sheet_name)
    rows = sheet.to_python()
    
    current_ctr = None
    for r in rows[9:]:
        row_text = " ".join([str(v).upper().strip() for v in r if v is not None])
        if "TOTAL AVANCE" in row_text or "TOTAL ACUMULADO" in row_text:
            break
        if r[0] is not None and str(r[0]).strip() != "":
            raw_ctr = str(r[0]).strip()
            if not any(k in raw_ctr.upper() for k in ["CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"]):
                current_ctr = raw_ctr
        if len(r) > 2 and r[2] is not None and str(r[2]).strip() != "" and str(r[2]).strip().upper() not in ("EQUIPO", "SUB", "SUP"):
            try:
                met = float(str(r[6]).replace(",", ".")) if len(r) > 6 and r[6] is not None and str(r[6]).strip() != "" else 0.0
            except ValueError:
                met = 0.0
            
            # Normalizar CTR
            ctr_norm = str(current_ctr).replace("CUCULÍ", "CUCULI").replace("CUCUL", "CUCULI").upper().strip()
            if "SAN CRISTOBAL" in ctr_norm:
                ctr_norm = "SAN CRISTOBAL"
            
            ci_rows.append({"CTR": ctr_norm, "METRAJE": met})

df_ci = pd.DataFrame(ci_rows)
ci_totals = df_ci.groupby("CTR")["METRAJE"].sum().reset_index()
ci_totals.rename(columns={"METRAJE": "METRAJE_CONTROL_INTERNO"}, inplace=True)

# 3. Mergear y comparar
comp = pd.merge(det_totals, ci_totals, on="CTR", how="outer").fillna(0)
comp["DIFERENCIA (DETALLADOS - CI)"] = comp["METRAJE_DETALLADOS"] - comp["METRAJE_CONTROL_INTERNO"]
comp["DIFERENCIA (ROUND 2)"] = comp["DIFERENCIA (DETALLADOS - CI)"].round(2)

print("="*80)
print("COMPARACION GENERAL DE METRAJES ACUMULADOS POR CTR")
print("="*80)
print(comp.to_string(index=False))
