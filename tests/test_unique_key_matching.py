"""
Prueba de cruce por ID_CLAVE_UNICA entre Detallados y Control Interno
"""
import pandas as pd
from python_calamine import CalamineWorkbook
from pathlib import Path
import re
import unicodedata

# 1. Cargar Detallados
df_det = pd.read_csv("output/detallados_consolidados.csv")
df_det = df_det[df_det["CTR"].str.upper() != "COLQUIJIRCA"].copy()

# Asignar TURNO_ESTANDAR en Detallados
def get_std_turno(row, seq_in_day):
    raw_t = str(row.get("TURNO (A=1;B=2)", "")).strip().upper() if pd.notna(row.get("TURNO (A=1;B=2)")) else ""
    raw_g = str(row.get("GRUPO", "")).strip().upper() if pd.notna(row.get("GRUPO")) else ""
    
    if raw_t in ("1", "1.0", "A", "D", "DIA", "G1"):
        return "A"
    if raw_t in ("2", "2.0", "N", "NOCHE", "G2"):
        return "B"
    if raw_g in ("1", "1.0"):
        return "A"
    if raw_g in ("2", "2.0"):
        return "B"
    if raw_t == "B" and raw_g in ("1", "1.0"):
        return "A"
    if raw_t == "C" and raw_g in ("2", "2.0"):
        return "B"
    return "A" if seq_in_day == 1 else "B"

seq_counter = {}
std_turnos = []
for idx, row in df_det.iterrows():
    key = (row["FECHA"], row["CTR"], row["MAQUINA"])
    seq_counter[key] = seq_counter.get(key, 0) + 1
    std_t = get_std_turno(row, seq_counter[key])
    std_turnos.append(std_t)

df_det["TURNO_ESTANDAR"] = std_turnos
df_det["ID_CLAVE_UNICA"] = df_det["FECHA"].astype(str) + "|" + df_det["CTR"].astype(str).str.upper() + "|" + df_det["MAQUINA"].astype(str) + "|" + df_det["TURNO_ESTANDAR"]

# 2. Cargar Control Interno
ci_path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")
wb = CalamineWorkbook.from_path(str(ci_path))

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
exceptions_map[("TICLIO", "XRD150USS-001")] = "XRD150U-007"

ci_rows = []
for sheet_name in wb.sheet_names:
    if not re.match(r'^\d{2}\.\d{2}$', sheet_name):
        continue
    day_str, month_str = sheet_name.split(".")
    fecha_iso = f"2026-{month_str}-{day_str}"
    
    sheet = wb.get_sheet_by_name(sheet_name)
    rows = sheet.to_python()
    
    current_ctr = None
    maq_seq = {}
    
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
            ctr_clean = str(current_ctr).replace("CUCULÍ", "CUCULI").replace("CUCUL", "CUCULI").upper().strip()
            if "SAN CRISTOBAL" in ctr_clean:
                ctr_clean = "SAN CRISTOBAL"
            if ctr_clean == "COLQUIJIRCA":
                continue
            
            def norm_key(s):
                nfkd = unicodedata.normalize('NFKD', str(s).upper().strip())
                return ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
            
            lookup_key = (norm_key(ctr_clean), norm_key(raw_maq))
            official_maq = exceptions_map.get(lookup_key, raw_maq)
            
            # Secuencia en el día para la máquina (1 -> 'A', 2 -> 'B')
            turn_key = (fecha_iso, ctr_clean, official_maq)
            maq_seq[turn_key] = maq_seq.get(turn_key, 0) + 1
            t_std = "A" if maq_seq[turn_key] == 1 else "B"
            
            try:
                met = float(str(r[6]).replace(",", ".")) if len(r) > 6 and r[6] is not None and str(r[6]).strip() != "" else 0.0
            except ValueError:
                met = 0.0
            
            clave_unica = f"{fecha_iso}|{ctr_clean}|{official_maq}|{t_std}"
            ci_rows.append({
                "FECHA": fecha_iso,
                "CTR": ctr_clean,
                "MAQUINA": official_maq,
                "TURNO_ESTANDAR": t_std,
                "ID_CLAVE_UNICA": clave_unica,
                "METRAJE_CI": met
            })

df_ci = pd.DataFrame(ci_rows)

# Cruzar por ID_CLAVE_UNICA
det_sum = df_det.groupby("ID_CLAVE_UNICA")["METRAJE"].sum().reset_index().rename(columns={"METRAJE": "METRAJE_DET"})
ci_sum = df_ci.groupby("ID_CLAVE_UNICA")["METRAJE_CI"].sum().reset_index()

merged_keys = pd.merge(det_sum, ci_sum, on="ID_CLAVE_UNICA", how="outer").fillna(0)
merged_keys["DIFERENCIA"] = (merged_keys["METRAJE_DET"] - merged_keys["METRAJE_CI"]).round(2)

print(f"Total claves únicas en Detallados: {df_det['ID_CLAVE_UNICA'].nunique()}")
print(f"Total claves únicas en Control Interno: {df_ci['ID_CLAVE_UNICA'].nunique()}")
print(f"Coincidencias perfectas (Diferencia = 0): {(merged_keys['DIFERENCIA'] == 0).sum()}")
print(f"Discrepancias por clave única: {(merged_keys['DIFERENCIA'] != 0).sum()}")

print("\nMuestra de coincidencia por clave única:")
print(merged_keys.head(10))
