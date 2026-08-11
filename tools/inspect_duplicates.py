"""
Inspección de filas duplicadas en detallados_consolidados.csv
"""
import pandas as pd

df = pd.read_csv("output/detallados_consolidados.csv")
print("Total filas en detallados_consolidados.csv:", len(df))

moro = df[df["CTR"] == "MOROCOCHA"]
print("\nMuestra de MOROCOCHA en detallados_consolidados.csv:")
print(moro[["N°", "FECHA", "CTR", "MAQUINA", "SONDAJE", "DESDE", "HASTA", "METRAJE", "TURNO_ESTANDAR", "ID_CLAVE_UNICA"]].head(10))
