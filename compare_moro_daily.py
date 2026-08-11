"""
Comparación diaria de Morococha y Chungar entre Detallados y Control Interno
"""
import pandas as pd

df_det = pd.read_csv("output/detallados_consolidados.csv")
df_ci = pd.read_csv("01_Control_Interno_ETL/output/control_interno_compilado.csv")

moro_det = df_det[df_det["CTR"] == "MOROCOCHA"].copy()
moro_ci = df_ci[df_ci["CTR"] == "MOROCOCHA"].copy()

print("="*80)
print("SUMA DE METRAJE MOROCOCHA:")
print("  Detallados (Suma total):", moro_det["METRAJE"].sum())
print("  Control Interno (Suma total):", moro_ci["METRAJE_CI"].sum())
print("="*80)

# Ver por clave única en Morococha
det_grp = moro_det.groupby("ID_CLAVE_UNICA")["METRAJE"].sum().reset_index()
ci_grp = moro_ci.groupby("ID_CLAVE_UNICA")["METRAJE_CI"].sum().reset_index()

m = pd.merge(det_grp, ci_grp, on="ID_CLAVE_UNICA", how="outer").fillna(0)
m["DIFF"] = m["METRAJE"] - m["METRAJE_CI"]

diffs = m[m["DIFF"].abs() > 0.01]
print(f"\nDiscrepancias en Morococha por clave única (Total {len(diffs)}):")
print(diffs.to_string())

# CHUNGAR
chung_det = df_det[df_det["CTR"] == "CHUNGAR"].copy()
chung_ci = df_ci[df_ci["CTR"] == "CHUNGAR"].copy()

det_c = chung_det.groupby("ID_CLAVE_UNICA")["METRAJE"].sum().reset_index()
ci_c = chung_ci.groupby("ID_CLAVE_UNICA")["METRAJE_CI"].sum().reset_index()

mc = pd.merge(det_c, ci_c, on="ID_CLAVE_UNICA", how="outer").fillna(0)
mc["DIFF"] = mc["METRAJE"] - mc["METRAJE_CI"]

diffs_c = mc[mc["DIFF"].abs() > 0.01]
print("\n" + "="*80)
print("SUMA DE METRAJE CHUNGAR:")
print("  Detallados (Suma total):", chung_det["METRAJE"].sum())
print("  Control Interno (Suma total):", chung_ci["METRAJE_CI"].sum())
print("Discrepancias en Chungar por clave única (Total", len(diffs_c), "):")
print(diffs_c.to_string())
