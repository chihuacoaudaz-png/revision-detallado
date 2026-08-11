"""
Matriz Comparativa de Metrajes entre Detallados y Control Interno (Por Clave Única y por Día)
"""
import pandas as pd
from pathlib import Path
from typing import Tuple

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import DETALLADOS_CSV, CONTROL_INTERNO_CSV as CI_CSV, CONTROL_INTERNO_OUTPUT_DIR as OUTPUT_DIR
except ImportError:
    repo_root = Path(__file__).parent.parent
    DETALLADOS_CSV = repo_root / "output" / "detallados_consolidados.csv"
    CI_CSV = Path(__file__).parent / "output" / "control_interno_compilado.csv"
    OUTPUT_DIR = Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_matriz_comparativa() -> Tuple[pd.DataFrame, pd.DataFrame]:
    print("=" * 80)
    print("GENERANDO MATRIZ COMPARATIVA DE METRAJES POR TURNO Y POR DIA")
    print("=" * 80)
    
    # 1. Cargar Detallados (Excluyendo Colquijirca)
    df_det = pd.read_csv(DETALLADOS_CSV, low_memory=False)
    df_det = df_det[df_det["CTR"].str.upper() != "COLQUIJIRCA"].copy()
    df_det["CTR"] = df_det["CTR"].apply(lambda x: "CUCULI" if "CUCUL" in str(x).upper() else str(x).upper().strip())
    
    det_shift = df_det.groupby(["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"])["METRAJE"].sum().reset_index()
    det_shift.rename(columns={"METRAJE": "METRAJE_DETALLADO"}, inplace=True)
    
    # 2. Cargar Control Interno (Excluyendo Colquijirca)
    df_ci = pd.read_csv(CI_CSV, low_memory=False)
    df_ci = df_ci[df_ci["CTR"].str.upper() != "COLQUIJIRCA"].copy()
    df_ci["CTR"] = df_ci["CTR"].apply(lambda x: "CUCULI" if "CUCUL" in str(x).upper() else str(x).upper().strip())
    
    ci_shift = df_ci.groupby(["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"])["METRAJE_CI"].sum().reset_index()
    
    # 3. Outer Join por ID_CLAVE_UNICA (Auditoría por Turno)
    comparativo = pd.merge(det_shift, ci_shift, on=["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"], how="outer")
    comparativo["METRAJE_DETALLADO"] = comparativo["METRAJE_DETALLADO"].fillna(0.0)
    comparativo["METRAJE_CONTROL_INTERNO"] = comparativo["METRAJE_CI"].fillna(0.0)
    comparativo.drop(columns=["METRAJE_CI"], inplace=True)
    
    comparativo["DIFERENCIA_METRAJE"] = (comparativo["METRAJE_DETALLADO"] - comparativo["METRAJE_CONTROL_INTERNO"]).round(2)
    
    # Clasificación por turno
    def classify_shift(row):
        diff = row["DIFERENCIA_METRAJE"]
        m_det = row["METRAJE_DETALLADO"]
        m_ci = row["METRAJE_CONTROL_INTERNO"]
        if abs(diff) < 0.01:
            return "COINCIDE OK"
        elif m_det > 0 and m_ci == 0:
            return "SOLO EN DETALLADO"
        elif m_det == 0 and m_ci > 0:
            return "SOLO EN CONTROL INTERNO"
        else:
            return "REPARTICION DE TURNO (DIA/NOCHE)"
            
    comparativo["ESTADO_TURNO"] = comparativo.apply(classify_shift, axis=1)
    
    # 4. Resumen Acumulado por CTR
    resumen_ctr = comparativo.groupby("CTR")[["METRAJE_DETALLADO", "METRAJE_CONTROL_INTERNO"]].sum().reset_index()
    resumen_ctr["DIFERENCIA_TOTAL"] = (resumen_ctr["METRAJE_DETALLADO"] - resumen_ctr["METRAJE_CONTROL_INTERNO"]).round(2)
    
    # Exportación
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_excel = OUTPUT_DIR / "matriz_comparativa_metrajes.xlsx"
    out_csv = OUTPUT_DIR / "discrepancias_diarias_detalladas.csv"
    out_resumen = OUTPUT_DIR / "resumen_discrepancias_ctr.csv"
    
    with pd.ExcelWriter(out_excel, engine="openpyxl") as writer:
        comparativo.to_excel(writer, sheet_name="Detalle_Por_Clave_Unica", index=False)
        resumen_ctr.to_excel(writer, sheet_name="Resumen_Por_CTR", index=False)
        
    comparativo.to_csv(out_csv, index=False, encoding="utf-8-sig")
    resumen_ctr.to_csv(out_resumen, index=False, encoding="utf-8-sig")
    
    print(f"\n[OK] Excel comparativo generado: {out_excel}")
    print(f"[OK] CSV discrepancias generado: {out_csv}")
    print(f"[OK] CSV resumen generado: {out_resumen}")
    
    print("\n" + "="*80)
    print("RESUMEN COMPARATIVO ACUMULADO POR CTR (EXCLUIDO COLQUIJIRCA):")
    print("="*80)
    print(resumen_ctr.to_string(index=False))
    
    return comparativo, resumen_ctr

if __name__ == "__main__":
    run_matriz_comparativa()
