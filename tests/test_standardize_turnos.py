"""
Prueba de estandarización de turnos A y B en Detallados
"""
import pandas as pd
import numpy as np

df = pd.read_csv("output/detallados_consolidados.csv")

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

# Probar por cada CTR
seq_counter = {}
std_turnos = []
for idx, row in df.iterrows():
    key = (row["FECHA"], row["CTR"], row["MAQUINA"])
    seq_counter[key] = seq_counter.get(key, 0) + 1
    seq = seq_counter[key]
    std_t = get_std_turno(row, seq)
    std_turnos.append(std_t)

df["TURNO_ESTANDAR"] = std_turnos

print("Distribución de TURNO_ESTANDAR por CTR:")
print(df.groupby(["CTR", "TURNO_ESTANDAR"]).size().unstack(fill_value=0))
