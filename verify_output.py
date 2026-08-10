"""
Verificación de los datos consolidados finales en output/detallados_consolidados.csv
"""
import pandas as pd

df = pd.read_csv("output/detallados_consolidados.csv")

print(f"Total registros: {len(df)}")
print(f"Columnas: {len(df.columns)}")
print(f"Primeras 10 filas:")
cols_to_show = ["N°", "ZONA", "CTR", "MAQUINA", "TURNO (A=1;B=2)", "GRUPO", "MES", "FECHA", "SONDAJE", "PROFUNDIDAD DE SONDAJE", "LINEA", "INCLINACIÓN", "DESDE", "HASTA", "METRAJE", "HORAS EXTRAS"]
print(df[cols_to_show].head(15))

print("\nVerificación de tipos de datos en METRAJE:")
print(f"Valores nulos en METRAJE: {df['METRAJE'].isna().sum()}")
print(f"Muestras de METRAJE: {df['METRAJE'].dropna().head(10).tolist()}")

print("\nVerificación de fechas nulas:")
print(f"Valores nulos en FECHA: {df['FECHA'].isna().sum()}")

print("\nResumen por CTR de filas y metraje total:")
gb = df.groupby("CTR")["METRAJE"].agg(["count", "sum"]).reset_index()
print(gb)
