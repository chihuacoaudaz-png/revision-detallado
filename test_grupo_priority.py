import os
import sys
import importlib
import pandas as pd
from pathlib import Path

base_dir = Path(r"c:\Proyectos Python\Detallados")
sys.path.insert(0, str(base_dir))

# Read detailed output
df_det = pd.read_csv(base_dir / "output" / "detallados_consolidados.csv", low_memory=False)

def fix_std_turno_v2(row, seq_in_day):
    ctr = str(row.get("CTR", "")).upper()
    raw_t = str(row.get("TURNO (A=1;B=2)", "")).strip().upper() if pd.notna(row.get("TURNO (A=1;B=2)")) else ""
    raw_g = str(row.get("GRUPO", "")).strip().upper() if pd.notna(row.get("GRUPO")) else ""
    
    # Clean group string (e.g. '2.0' -> '2')
    try:
        g_num = float(raw_g)
        g_str = str(int(g_num)) if g_num.is_integer() else str(g_num)
    except ValueError:
        g_str = raw_g

    # 1. Caso especial AMERICANA: raw_t == 'B' y GRUPO 1.0 -> 'A' (Día), raw_t == 'C' y GRUPO 2.0 -> 'B' (Noche)
    if ctr == "AMERICANA":
        if raw_t == "B" and g_str == "1":
            return "A"
        if raw_t == "C" and g_str == "2":
            return "B"

    # 2. Si GRUPO es explícito (1 = Turno A, 2 = Turno B), GRUPO TIENE PRIORIDAD sobre letras ambiguas de turno
    if g_str == "1":
        return "A"
    if g_str == "2":
        return "B"
            
    # 3. Turno explícito por valor
    if raw_t in ("1", "1.0", "A", "D", "DIA", "G1"):
        return "A"
    if raw_t in ("2", "2.0", "B", "N", "NOCHE", "G2"):
        return "B"
        
    return "A" if seq_in_day == 1 else "B"

seq_counter = {}
std_turnos = []
claves = []

for idx, row in df_det.iterrows():
    fecha_str = str(row["FECHA"])
    ctr_str = str(row["CTR"]).upper()
    maq_str = str(row["MAQUINA"]).upper()
    key = (fecha_str, ctr_str, maq_str)
    seq_counter[key] = seq_counter.get(key, 0) + 1
    t = fix_std_turno_v2(row, seq_counter[key])
    std_turnos.append(t)
    claves.append(f"{fecha_str}|{ctr_str}|{maq_str}|{t}")

df_det["TURNO_ESTANDAR"] = std_turnos
df_det["ID_CLAVE_UNICA"] = claves

# Load CI
comp_mod = importlib.import_module("01_Control_Interno_ETL.compilar_control_interno")
df_ci = comp_mod.run_compilacion_control_interno()

det_grp = df_det.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE"].sum().rename(columns={"METRAJE": "MET_DET"})
ci_grp = df_ci.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE_CI"].sum().rename(columns={"METRAJE_CI": "MET_CI"})

merged = pd.merge(det_grp, ci_grp, on="ID_CLAVE_UNICA", how="outer").fillna(0)
merged["DIF"] = (merged["MET_DET"] - merged["MET_CI"]).round(2)
disc = merged[merged["DIF"].abs() >= 0.01].copy()

print(f"Total Claves Únicas: {len(merged)}")
print(f"Total Discrepancias tras priorizar GRUPO: {len(disc)}")
disc["CTR"] = disc["ID_CLAVE_UNICA"].apply(lambda x: x.split("|")[1] if "|" in str(x) else "OTRO")
print("\nDiscrepancias por CTR:")
print(disc["CTR"].value_counts())

print("\nDetalle de TODAS las discrepancias restantes:")
print(disc.to_string())
