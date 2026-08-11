"""
Verificación de sumas por CTR en detallados_consolidados.csv
"""
import pandas as pd

df = pd.read_csv("output/detallados_consolidados.csv")
print("Sumas en detallados_consolidados.csv:")
print(df.groupby("CTR")["METRAJE"].sum())
