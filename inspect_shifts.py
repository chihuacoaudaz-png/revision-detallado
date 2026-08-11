"""
Inspección de la columna TURNO en detallados_consolidados.csv y en Control Interno
"""
import pandas as pd
from python_calamine import CalamineWorkbook
from pathlib import Path
import re

df_det = pd.read_csv("output/detallados_consolidados.csv")

print("Valores únicos de TURNO (A=1;B=2) por CTR en Detallados:")
for ctr, group in df_det.groupby("CTR"):
    val_counts = group["TURNO (A=1;B=2)"].value_counts(dropna=False).to_dict()
    grupo_counts = group["GRUPO"].value_counts(dropna=False).to_dict()
    print(f"  {ctr:20s} -> TURNO: {val_counts} | GRUPO: {grupo_counts}")
