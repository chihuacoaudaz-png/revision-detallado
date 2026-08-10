"""
Drilldown día a día y máquina a máquina de las discrepancias en:
1. CHUNGAR (+1.5 m)
2. CONDESTABLE (-196.1 m)
3. CUCULI (-117.65 m)
4. MOROCOCHA (+46.4 m)
5. YAULIYACU (-125.4 m)
"""
import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook
from pathlib import Path
import unicodedata

def normalize_str(s):
    if not s or pd.isna(s):
        return ""
    nfkd = unicodedata.normalize('NFKD', str(s).upper().strip())
    s_clean = ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
    return re.sub(r'[^A-Z0-9]', '', s_clean)

import re

# 1. Cargar Detallados
df_det = pd.read_csv("output/detallados_consolidados.csv")
df_det["CTR_NORM"] = df_det["CTR"].apply(lambda x: "CUCULI" if "CUCUL" in str(x).upper() else str(x).upper().strip())

# Estandarización de máquinas en Detallados
maestro_path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Maestro_Maquinas\Maestros_Maquinas.xlsx")
exceptions_map = {}
if maestro_path.exists():
    wb_m = CalamineWorkbook.from_path(str(maestro_path))
    if "Exepciones" in wb_m.sheet_names:
        sheet_m = wb_m.get_sheet_by_name("Exepciones")
        m_rows = sheet_m.to_python()
        for r in m_rows[1:]:
            if len(r) >= 3 and r[0] and r[1] and r[2]:
                def norm(s):
                    return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper().strip()) if not unicodedata.category(c).startswith('M'))
                exceptions_map[(norm(r[0]), norm(r[1]))] = str(r[2]).strip()

# Agrupar Detallados por (FECHA, CTR_NORM, MAQUINA)
det_grouped = df_det.groupby(["FECHA", "CTR_NORM", "MAQUINA"])["METRAJE"].sum().reset_index()
det_grouped.rename(columns={"METRAJE": "METRAJE_DETALLADOS"}, inplace=True)

# 2. Cargar Control Interno
path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")
wb = CalamineWorkbook.from_path(str(path))

ci_rows = []
for sheet_name in wb.sheet_names:
    if not re.match(r'^\d{2}\.\d{2}$', sheet_name):
        continue
    
    day_str, month_str = sheet_name.split(".")
    fecha_iso = f"2026-{month_str}-{day_str}"
    
    sheet = wb.get_sheet_by_name(sheet_name)
    rows = sheet.to_python()
    
    current_ctr = None
    maq_turn_counter = {}
    
    for r in rows[9:]:
        row_text = " ".join([str(v).upper().strip() for v in r if v is not None])
        if "TOTAL AVANCE" in row_text or "TOTAL ACUMULADO" in row_text:
            break
        
        if r[0] is not None and str(r[0]).strip() != "":
            raw_ctr = str(r[0]).strip()
            if not any(k in raw_ctr.upper() for k in ["CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"]):
                current_ctr = raw_ctr
        
        if len(r) > 2 and r[2] is not None and str(r[2]).strip() != "" and str(r[2]).strip().upper() not in ("EQUIPO", "SUB", "SUP"):
            raw_maq = str(r[2]).strip()
            
            # Estandarizar máquina usando exceptions_map
            def norm_key(s):
                return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper().strip()) if not unicodedata.category(c).startswith('M'))
            
            lookup_key = (norm_key(current_ctr), norm_key(raw_maq))
            official_maq = exceptions_map.get(lookup_key, raw_maq)
            
            try:
                met = float(str(r[6]).replace(",", ".")) if len(r) > 6 and r[6] is not None and str(r[6]).strip() != "" else 0.0
            except ValueError:
                met = 0.0
            
            ctr_norm = str(current_ctr).replace("CUCULÍ", "CUCULI").replace("CUCUL", "CUCULI").upper().strip()
            if "SAN CRISTOBAL" in ctr_norm:
                ctr_norm = "SAN CRISTOBAL"
            
            se_perforo = str(r[4]).strip().upper() if len(r) > 4 and r[4] is not None else ""
            
            ci_rows.append({
                "FECHA": fecha_iso,
                "CTR_NORM": ctr_norm,
                "MAQUINA": official_maq,
                "MAQUINA_RAW_CI": raw_maq,
                "SE_PERFORO": se_perforo,
                "METRAJE": met
            })

df_ci = pd.DataFrame(ci_rows)
ci_grouped = df_ci.groupby(["FECHA", "CTR_NORM", "MAQUINA"])["METRAJE"].sum().reset_index()
ci_grouped.rename(columns={"METRAJE": "METRAJE_CONTROL_INTERNO"}, inplace=True)

# 3. Mergear y encontrar diferencias
merged = pd.merge(det_grouped, ci_grouped, on=["FECHA", "CTR_NORM", "MAQUINA"], how="outer").fillna(0)
merged["DIFERENCIA"] = (merged["METRAJE_DETALLADOS"] - merged["METRAJE_CONTROL_INTERNO"]).round(2)

diffs = merged[merged["DIFERENCIA"] != 0].sort_values(by=["CTR_NORM", "FECHA", "MAQUINA"])

target_ctrs = ["CHUNGAR", "CONDESTABLE", "CUCULI", "MOROCOCHA", "YAULIYACU"]

print("="*90)
print("DISCREPANCIAS DETALLADAS DÍA A DÍA POR MÁQUINA")
print("="*90)
for ctr in target_ctrs:
    ctr_diffs = diffs[diffs["CTR_NORM"] == ctr]
    print(f"\n>>> CTR: {ctr} (Total Discrepancia: {ctr_diffs['DIFERENCIA'].sum():.2f} m)")
    print("-" * 75)
    print(ctr_diffs[["FECHA", "MAQUINA", "METRAJE_DETALLADOS", "METRAJE_CONTROL_INTERNO", "DIFERENCIA"]].to_string(index=False))

