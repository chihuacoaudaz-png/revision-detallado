import os
import sys
import re
import importlib
import pandas as pd
from pathlib import Path
from python_calamine import CalamineWorkbook

base_dir = Path(r"c:\Proyectos Python\Detallados")
sys.path.insert(0, str(base_dir))

comp_mod = importlib.import_module("01_Control_Interno_ETL.compilar_control_interno")
load_machine_exceptions = comp_mod.load_machine_exceptions
exceptions_map = load_machine_exceptions(base_dir / "Estructura base" / "Rockdrill_Control_Operaciones" / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx")

def PositionalTurnFormula(raw_t, seq_in_day, ctr_name=""):
    """
    FÓRMULA POSICIONAL DE TURNO (IGNORA COMPLETAMENTE 'GRUPO'):
    1. Si TURNO es 1, 1.0, D, DIA -> 'A' (Día)
    2. Si TURNO es 2, 2.0, N, NOCHE -> 'B' (Noche)
    3. Si TURNO es 'C' -> 'A' (en plantillas de 3 letras como AMERICANA/CERRO C es día)
    4. Si TURNO es 'A' y 'B':
       - Si es AMERICANA/CERRO donde C=Día y A=Noche -> 'B'
       - En general, si seq_in_day == 1 -> 'A'
       - Si seq_in_day >= 2 -> 'B'
    5. Fallback Posicional puro:
       Renglón 1 del día -> 'A' (Turno Día)
       Renglón 2+ del día -> 'B' (Turno Noche)
    """
    raw_t = str(raw_t).strip().upper() if pd.notna(raw_t) else ""
    
    if raw_t in ("1", "1.0", "1,0", "1.00", "D", "DIA", "G1"):
        return "A"
    if raw_t in ("2", "2.0", "2,0", "2.00", "N", "NOCHE", "G2"):
        return "B"
        
    if raw_t == "C":
        return "A"
        
    if raw_t == "A":
        if "AMERICANA" in str(ctr_name).upper() or "CERRO" in str(ctr_name).upper():
            return "B"
        return "A" if seq_in_day == 1 else "B"
        
    if raw_t == "B":
        return "B"
        
    return "A" if seq_in_day == 1 else "B"

# --- PROCESAR DETALLADOS ---
base_path = base_dir / "Estructura base" / "Rockdrill_Control_Operaciones"
detailed_files = []
for ctr_folder in sorted(base_path.glob("CTR_*")):
    if ctr_folder.name == "CTR_COLQUIJIRCA":
        continue
    ctr_name = ctr_folder.name.replace("CTR_", "").replace("_", " ")
    det_folder = ctr_folder / "02_Detallado"
    search_dir = det_folder if det_folder.exists() else ctr_folder
    for xlsx in search_dir.glob("*.xlsx"):
        if not xlsx.name.startswith("~$"):
            detailed_files.append((ctr_name, xlsx))

det_rows = []
for ctr_name, filepath in detailed_files:
    try:
        wb = CalamineWorkbook.from_path(str(filepath))
    except Exception as e:
        continue
    for sheet_name in wb.sheet_names:
        upper_s = sheet_name.upper()
        if upper_s in ["ADITIVOS", "GENERAL", "LISTAS", "TIEMPOS", "HOJA1", "HOJA2", "HOJA3", "RESUMEN", "TABLAS", "COMPA", "R. DETALLADO"] or upper_s.startswith("MAQUINA "):
            continue
        sheet = wb.get_sheet_by_name(sheet_name)
        rows = sheet.to_python()
        if len(rows) < 24:
            continue
        grid_rows = rows[24:]
        curr_date = None
        date_seq_counter = {}
        for r in grid_rows:
            v_date = r[0] if len(r) > 0 else None
            if v_date is not None and str(v_date).strip() != "":
                try:
                    curr_date = pd.to_datetime(v_date).date()
                except:
                    pass
            if curr_date is None:
                continue
            date_seq_counter[curr_date] = date_seq_counter.get(curr_date, 0) + 1
            seq = date_seq_counter[curr_date]
            raw_t = r[7] if len(r) > 7 else ""
            val_met = r[9] if len(r) > 9 else None
            try:
                metraje = float(str(val_met).replace(",", ".")) if val_met is not None and str(val_met).strip() != "" else 0.0
            except:
                metraje = 0.0
            val_hasta = str(r[6]).strip() if len(r) > 6 and r[6] is not None else ""
            val_desde = str(r[5]).strip() if len(r) > 5 and r[5] is not None else ""
            
            t_std = PositionalTurnFormula(raw_t, seq, ctr_name)
            
            has_met = metraje > 0
            has_range = (val_hasta != "" and val_hasta != "0" and val_hasta != "0.0") or (val_desde != "" and val_desde != "0" and val_desde != "0.0")
            
            if has_met or has_range:
                def norm_key(s):
                    return re.sub(r'[^A-Z0-9]', '', str(s).upper().strip())
                lookup = (norm_key(ctr_name), norm_key(sheet_name))
                official_maq = exceptions_map.get(lookup, sheet_name.strip())
                fecha_iso = curr_date.strftime("%Y-%m-%d")
                clave = f"{fecha_iso}|{ctr_name}|{official_maq}|{t_std}"
                det_rows.append({
                    "FECHA": fecha_iso,
                    "CTR": ctr_name,
                    "MAQUINA": official_maq,
                    "TURNO_ESTANDAR": t_std,
                    "METRAJE": metraje,
                    "ID_CLAVE_UNICA": clave
                })

df_det_final = pd.DataFrame(det_rows)

# --- PROCESAR CONTROL INTERNO ---
df_ci_raw = comp_mod.run_compilacion_control_interno()
df_ci_raw["CTR_CLEAN"] = df_ci_raw["CTR"].replace({"CUCULII": "CUCULI", "CUCULÍ": "CUCULI"})

ci_seq_map = {}
ci_turnos = []
ci_claves = []

for idx, row in df_ci_raw.iterrows():
    fecha_str = str(row["FECHA"])
    ctr_str = str(row["CTR_CLEAN"]).upper()
    maq_str = str(row["MAQUINA"]).upper()
    key = (fecha_str, ctr_str, maq_str)
    ci_seq_map[key] = ci_seq_map.get(key, 0) + 1
    seq = ci_seq_map[key]
    
    raw_t = row.get("TURNO (A=1;B=2)")
    
    t_std = PositionalTurnFormula(raw_t, seq, ctr_str)
    ci_turnos.append(t_std)
    ci_claves.append(f"{fecha_str}|{ctr_str}|{maq_str}|{t_std}")

df_ci_raw["TURNO_ESTANDAR"] = ci_turnos
df_ci_raw["ID_CLAVE_UNICA"] = ci_claves

# Group and compare
det_grp = df_det_final.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE"].sum().rename(columns={"METRAJE": "MET_DET"})
ci_grp = df_ci_raw.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE_CI"].sum().rename(columns={"METRAJE_CI": "MET_CI"})

merged = pd.merge(det_grp, ci_grp, on="ID_CLAVE_UNICA", how="outer").fillna(0)
merged["DIF"] = (merged["MET_DET"] - merged["MET_CI"]).round(2)
disc = merged[merged["DIF"].abs() >= 0.01].copy()

print(f"\nTotal Claves Únicas: {len(merged)}")
print(f"Total Discrepancias tras Fórmula Posicional Pura (Sin GRUPO): {len(disc)}")
disc["CTR"] = disc["ID_CLAVE_UNICA"].apply(lambda x: x.split("|")[1] if "|" in str(x) else "OTRO")
print("\nDiscrepancias por CTR:")
print(disc["CTR"].value_counts())
