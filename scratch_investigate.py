import os
import sys
import re
import pandas as pd
import numpy as np
from pathlib import Path

base_dir = Path(r"c:\Proyectos Python\Detallados")
sys.path.insert(0, str(base_dir))

# Read detailed output
df_det = pd.read_csv(base_dir / "output" / "detallados_consolidados.csv", low_memory=False)

print("=== ESTRUCTURA DE DETALLADOS ===")
print("Total filas en Detallados:", len(df_det))

# Run CI compilation
import importlib
comp_mod = importlib.import_module("01_Control_Interno_ETL.compilar_control_interno")
run_compilacion_control_interno = comp_mod.run_compilacion_control_interno
df_ci = run_compilacion_control_interno()

print("\n=== ESTRUCTURA DE CONTROL INTERNO ===")
print("Total filas en Control Interno:", len(df_ci))

# Aggregate both by ID_CLAVE_UNICA
det_grp = df_det.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE"].sum().rename(columns={"METRAJE": "MET_DET"})
ci_grp = df_ci.groupby("ID_CLAVE_UNICA", as_index=False)["METRAJE_CI"].sum().rename(columns={"METRAJE_CI": "MET_CI"})

merged = pd.merge(det_grp, ci_grp, on="ID_CLAVE_UNICA", how="outer").fillna(0)
merged["DIF"] = (merged["MET_DET"] - merged["MET_CI"]).round(2)
discrepancies = merged[merged["DIF"].abs() >= 0.01]

print(f"\nTotal Claves Únicas: {len(merged)}")
print(f"Total Discrepancias en Python: {len(discrepancies)}")
print("\nDiscrepancias por CTR:")
discrepancies["CTR"] = discrepancies["ID_CLAVE_UNICA"].apply(lambda x: x.split("|")[1] if isinstance(x, str) and "|" in x else "DESCONOCIDO")
print(discrepancies["CTR"].value_counts())

print("\nDetalle de discrepancias (todas):")
print(discrepancies.to_string())
