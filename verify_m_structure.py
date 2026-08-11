import os
import sys
import re
import importlib
import pandas as pd
from pathlib import Path
from python_calamine import CalamineWorkbook

base_dir = Path(r"c:\Proyectos Python\Detallados")
sys.path.insert(0, str(base_dir))

# Load machine exceptions
comp_mod = importlib.import_module("01_Control_Interno_ETL.compilar_control_interno")
load_machine_exceptions = comp_mod.load_machine_exceptions
exceptions_map = load_machine_exceptions(base_dir / "Estructura base" / "Rockdrill_Control_Operaciones" / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx")

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

simulated_m_rows = []

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
        
        # STEP 1: FillDown Date on RAW Grid
        raw_grid_data = []
        curr_date = None
        
        for r in grid_rows:
            v_date = r[0] if len(r) > 0 else None
            if v_date is not None and str(v_date).strip() != "":
                try:
                    curr_date = pd.to_datetime(v_date).date()
                except:
                    pass
            if curr_date is not None:
                raw_grid_data.append((curr_date, r))
                
        # STEP 2: Index per Date on RAW Grid & Assign TURNO_ESTANDAR
        raw_date_counter = {}
        processed_raw_rows = []
        
        for curr_date, r in raw_grid_data:
            raw_date_counter[curr_date] = raw_date_counter.get(curr_date, 0) + 1
            seq = raw_date_counter[curr_date]
            
            raw_sond = str(r[1]).strip() if len(r) > 1 and r[1] is not None else ""
            raw_t = str(r[7]).strip().upper() if len(r) > 7 and r[7] is not None else ""
            raw_g = str(r[8]).strip().upper() if len(r) > 8 and r[8] is not None else ""
            val_met = r[9] if len(r) > 9 else None
            
            try:
                metraje = float(str(val_met).replace(",", ".")) if val_met is not None and str(val_met).strip() != "" else 0.0
            except:
                metraje = 0.0
                
            val_hasta = str(r[6]).strip() if len(r) > 6 and r[6] is not None else ""
            val_desde = str(r[5]).strip() if len(r) > 5 and r[5] is not None else ""
            
            # TURNO_ESTANDAR calculation on raw grid
            if ctr_name == "AMERICANA":
                if raw_t == "B" and raw_g in ("1", "1.0", "1,0"):
                    t_std = "A"
                elif raw_t == "C" and raw_g in ("2", "2.0", "2,0"):
                    t_std = "B"
                elif raw_t in ("1", "1.0", "A", "D", "DIA", "G1"):
                    t_std = "A"
                elif raw_t in ("2", "2.0", "B", "N", "NOCHE", "G2"):
                    t_std = "B"
                elif raw_g in ("1", "1.0"):
                    t_std = "A"
                elif raw_g in ("2", "2.0"):
                    t_std = "B"
                else:
                    t_std = "A" if seq == 1 else "B"
            else:
                if raw_t in ("1", "1.0", "1,0", "A", "D", "DIA", "G1"):
                    t_std = "A"
                elif raw_t in ("2", "2.0", "2,0", "B", "N", "NOCHE", "G2"):
                    t_std = "B"
                elif raw_g in ("1", "1.0"):
                    t_std = "A"
                elif raw_g in ("2", "2.0"):
                    t_std = "B"
                else:
                    t_std = "A" if seq == 1 else "B"
                    
            processed_raw_rows.append({
                "FECHA": curr_date,
                "RAW_ROW": r,
                "TURNO_ESTANDAR": t_std,
                "METRAJE": metraje,
                "HASTA": val_hasta,
                "DESDE": val_desde
            })
            
        # STEP 3: Apply FilaFiltrada AFTER TURNO_ESTANDAR is assigned
        for item in processed_raw_rows:
            metraje = item["METRAJE"]
            val_hasta = item["HASTA"]
            val_desde = item["DESDE"]
            
            has_met = metraje > 0
            has_range = (val_hasta != "" and val_hasta != "0" and val_hasta != "0.0") or (val_desde != "" and val_desde != "0" and val_desde != "0.0")
            
            if has_met or has_range:
                def norm_key(s):
                    return re.sub(r'[^A-Z0-9]', '', str(s).upper().strip())
                lookup = (norm_key(ctr_name), norm_key(sheet_name))
                official_maq = exceptions_map.get(lookup, sheet_name.strip())
                
                fecha_iso = item["FECHA"].strftime("%Y-%m-%d")
                t_std = item["TURNO_ESTANDAR"]
                clave = f"{fecha_iso}|{ctr_name}|{official_maq}|{t_std}"
                
                simulated_m_rows.append({
                    "FECHA": fecha_iso,
                    "CTR": ctr_name,
                    "MAQUINA": official_maq,
                    "TURNO_ESTANDAR": t_std,
                    "METRAJE": metraje,
                    "ID_CLAVE_UNICA": clave
                })

df_det_m = pd.DataFrame(simulated_m_rows)

# Load CI
df_ci = comp_mod.run_compilacion_control_interno()
df_ci["CTR_CLEAN"] = df_ci["CTR"].replace({"CUCULII": "CUCULI", "CUCULÍ": "CUCULI"})
df_ci["ID_CLAVE_UNICA"] = df_ci.apply(lambda r: f"{r['FECHA']}|{r['CTR_CLEAN']}|{r['MAQUINA']}|{r['TURNO_ESTANDAR']}", axis=1)

det_grp = df_det_m.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE"].sum().rename(columns={"METRAJE": "MET_DET"})
ci_grp = df_ci.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE_CI"].sum().rename(columns={"METRAJE_CI": "MET_CI"})

merged = pd.merge(det_grp, ci_grp, on="ID_CLAVE_UNICA", how="outer").fillna(0)
merged["DIF"] = (merged["MET_DET"] - merged["MET_CI"]).round(2)
disc = merged[merged["DIF"].abs() >= 0.01].copy()

print(f"\nTotal Claves Únicas en M simulado: {len(merged)}")
print(f"Total Discrepancias en M simulado: {len(disc)}")
disc["CTR"] = disc["ID_CLAVE_UNICA"].apply(lambda x: x.split("|")[1] if "|" in str(x) else "OTRO")
print("\nDiscrepancias por CTR:")
print(disc["CTR"].value_counts())

print("\nDetalle de TODAS las discrepancias restantes en M simulado:")
print(disc.to_string())
