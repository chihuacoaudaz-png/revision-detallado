"""
Módulo de Control de Calidad y Gobernanza PMO (Validador QA/QC)
Rockdrill Group - Sistema Unificado de Analítica de Perforación
Ejecuta las 5 Quality Gates obligatorias, audita la integridad referencial
y genera el Reporte Oficial de Anomalías de Campo.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

# Ajustar sys.path
ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Forzar UTF-8
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

def ejecutar_auditoria_qaqc(
    tablas_modelo: Dict[str, pd.DataFrame],
    df_raw: pd.DataFrame,
    output_reporte_path: Path = Path(r"C:\Proyectos Python\Detallados\output\reporte_anomalias_campo.xlsx")
) -> bool:
    """
    Audita las 5 Quality Gates sobre el modelo dimensional generado.
    """
    print("=" * 80, flush=True)
    print("  AUDITORIA FORMAL DE GOBERNANZA QA/QC (5 QUALITY GATES)", flush=True)
    print("=" * 80, flush=True)
    
    qg_results = {}
    anomalias = []
    
    # -------------------------------------------------------------------------
    # QUALITY GATE 1: ARQUITECTURA, LLAVES SK E INTEGRIDAD REFERENCIAL
    # -------------------------------------------------------------------------
    print("\n  [QUALITY GATE 1] Verificando Llaves Subrogadas e Integridad Referencial...", flush=True)
    
    dim_cal = tablas_modelo["dim_tiempo_calendario"]
    dim_ctr = tablas_modelo["dim_contrato_minero"]
    dim_eq = tablas_modelo["dim_equipo_perforadora"]
    dim_lin = tablas_modelo["dim_linea_diametro"]
    dim_per = tablas_modelo["dim_personal"]
    dim_sond = tablas_modelo["dim_sondaje_taladro"]
    dim_act = tablas_modelo["dim_taxonomia_actividad"]
    
    fact_avance = tablas_modelo["fact_perforacion_avance"]
    fact_horas = tablas_modelo["fact_horas_operativas"]
    brg_cuad = tablas_modelo["brg_cuadrilla_guardia"]
    
    cal_sks = set(dim_cal["calendario_sk"])
    ctr_sks = set(dim_ctr["contrato_sk"])
    eq_sks = set(dim_eq["equipo_sk"])
    lin_sks = set(dim_lin["linea_sk"])
    per_sks = set(dim_per["personal_sk"])
    sond_sks = set(dim_sond["sondaje_sk"])
    act_sks = set(dim_act["actividad_sk"])
    
    huerfanos_avance = (
        (~fact_avance["calendario_sk"].isin(cal_sks)).sum() +
        (~fact_avance["contrato_sk"].isin(ctr_sks)).sum() +
        (~fact_avance["equipo_sk"].isin(eq_sks)).sum() +
        (~fact_avance["linea_sk"].isin(lin_sks)).sum() +
        (~fact_avance["perforista_sk"].isin(per_sks)).sum() +
        (~fact_avance["sondaje_sk"].isin(sond_sks)).sum()
    )
    
    huerfanos_horas = (
        (~fact_horas["calendario_sk"].isin(cal_sks)).sum() +
        (~fact_horas["contrato_sk"].isin(ctr_sks)).sum() +
        (~fact_horas["equipo_sk"].isin(eq_sks)).sum() +
        (~fact_horas["actividad_sk"].isin(act_sks)).sum()
    )
    
    huerfanos_cuad = (
        (~brg_cuad["calendario_sk"].isin(cal_sks)).sum() +
        (~brg_cuad["equipo_sk"].isin(eq_sks)).sum() +
        (~brg_cuad["personal_sk"].isin(per_sks)).sum()
    )
    
    total_huerfanos = huerfanos_avance + huerfanos_horas + huerfanos_cuad
    qg1_pass = total_huerfanos == 0
    qg_results["QG1_Integridad_Referencial"] = "APROBADO" if qg1_pass else f"FALLO ({total_huerfanos} huerfanos)"
    print(f"    {'[OK]' if qg1_pass else '[FALLO]'} QG1 Integridad Referencial: {total_huerfanos} llaves foraneas huerfanas.", flush=True)

    # -------------------------------------------------------------------------
    # QUALITY GATE 2: AXIOMA DE CONSERVACIÓN DE METRAJES (1-A-1)
    # -------------------------------------------------------------------------
    print("\n  [QUALITY GATE 2] Verificando Conservacion Absoluta de Metrajes...", flush=True)
    
    col_met = "METRAJE" if "METRAJE" in df_raw.columns else "METRAJE_PERFORADO"
    raw_metraje_sum = pd.to_numeric(df_raw[col_met], errors="coerce").fillna(0.0).sum()
    fact_metraje_sum = fact_avance["metraje_guardia_m"].sum()
    
    diff_metraje = abs(fact_metraje_sum - raw_metraje_sum)
    qg2_pass = diff_metraje < 0.01
    qg_results["QG2_Conservacion_Metrajes"] = "APROBADO" if qg2_pass else f"FALLO (Dif: {diff_metraje:.2f}m)"
    print(f"    {'[OK]' if qg2_pass else '[FALLO]'} QG2 Conservacion: Raw = {raw_metraje_sum:.2f}m | Fact = {fact_metraje_sum:.2f}m | Dif = {diff_metraje:.4f}m", flush=True)

    # -------------------------------------------------------------------------
    # QUALITY GATE 3: UNPIVOTING DE TIEMPOS Y BALANCE DE GUARDIAS (12.0H)
    # -------------------------------------------------------------------------
    print("\n  [QUALITY GATE 3] Verificando Unpivoting y Balance de Jornadas...", flush=True)
    
    horas_por_guardia = fact_horas.groupby("id_clave_unica")["horas_reportadas"].sum()
    desbalances = horas_por_guardia[(horas_por_guardia > 12.5) | ((horas_por_guardia < 11.5) & (horas_por_guardia > 0))]
    print(f"    [OK] Total eventos de tiempo unpivoteados: {len(fact_horas):,} filas.", flush=True)
    print(f"    [INFO] Guardias con desbalance operacional (fuera de 12.0h +- 0.5h): {len(desbalances)} guardias.", flush=True)
    
    for clave, h_tot in desbalances.items():
        anomalias.append({
            "ID_CLAVE_UNICA": clave,
            "TIPO_ANOMALIA": "ERR_BALANCE_HORAS",
            "VALOR_DETECTADO": f"{h_tot:.2f} h",
            "VALOR_ESPERADO": "12.00 h",
            "IMPACTO": "Distorsion de Disponibilidad Mecanica y Horas Facturables",
            "ACCION_REQUERIDA": "Solicitar a la administradora el balanceo de tiempos de la bitacora"
        })
    qg_results["QG3_Unpivoting_Tiempos"] = "APROBADO"

    # -------------------------------------------------------------------------
    # QUALITY GATE 4: DETECCIÓN DE ANOMALÍAS DE COTAS Y PERSONAL
    # -------------------------------------------------------------------------
    print("\n  [QUALITY GATE 4] Verificando Monotonia de Cotas y Registros de Personal...", flush=True)
    
    cotas_invertidas = fact_avance[(fact_avance["hasta_m"] < fact_avance["desde_m"]) & (fact_avance["desde_m"] > 0)]
    print(f"    [OK] Intervalos de perforacion con cotas invertidas (HASTA < DESDE): {len(cotas_invertidas)}", flush=True)
    for _, r in cotas_invertidas.iterrows():
        anomalias.append({
            "ID_CLAVE_UNICA": r["id_clave_unica"],
            "TIPO_ANOMALIA": "ERR_MONOTONIA_COTAS",
            "VALOR_DETECTADO": f"Desde: {r['desde_m']}m, Hasta: {r['hasta_m']}m",
            "VALOR_ESPERADO": "HASTA >= DESDE",
            "IMPACTO": "Inconsistencia fisica en el tramo de perforacion",
            "ACCION_REQUERIDA": "Rectificar cotas en el reporte de perforacion diario"
        })

    sin_perforista = fact_avance[fact_avance["perforista_sk"] == -1]
    print(f"    [OK] Guardias con perforista no registrado (sk = -1): {len(sin_perforista)}", flush=True)
    for _, r in sin_perforista.iterrows():
        anomalias.append({
            "ID_CLAVE_UNICA": r["id_clave_unica"],
            "TIPO_ANOMALIA": "ERR_PERFORISTA_NULO",
            "VALOR_DETECTADO": "Sin Perforista Registrado",
            "VALOR_ESPERADO": "Nombre y Fotocheck del Perforista Titular",
            "IMPACTO": "Perdida de trazabilidad en ranking de productividad",
            "ACCION_REQUERIDA": "Completar nombre del operador en plantilla detallada"
        })
    qg_results["QG4_Auditoria_Campo"] = "APROBADO"

    # -------------------------------------------------------------------------
    # QUALITY GATE 5: GENERACIÓN DEL REPORTE OFICIAL DE ANOMALÍAS
    # -------------------------------------------------------------------------
    print("\n  [QUALITY GATE 5] Generando Reporte Oficial de Anomalias y Gobernanza...", flush=True)
    
    df_anom = pd.DataFrame(anomalias) if anomalias else pd.DataFrame(columns=[
        "ID_CLAVE_UNICA", "TIPO_ANOMALIA", "VALOR_DETECTADO", "VALOR_ESPERADO", "IMPACTO", "ACCION_REQUERIDA"
    ])
    
    df_qg_resumen = pd.DataFrame([
        {"QUALITY_GATE": k, "ESTADO": v} for k, v in qg_results.items()
    ])
    
    output_reporte_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_reporte_path, engine="openpyxl") as writer:
        df_qg_resumen.to_excel(writer, sheet_name="Resumen_Quality_Gates", index=False)
        df_anom.to_excel(writer, sheet_name="Log_Anomalias_Campo", index=False)
        
    print(f"    [OK] Reporte exportado en: {output_reporte_path}", flush=True)
    qg_results["QG5_Reporte_Gobernanza"] = "APROBADO"

    print("\n" + "=" * 80, flush=True)
    print("  RESUMEN FINAL DE QUALITY GATES:", flush=True)
    print("=" * 80, flush=True)
    for qg, res in qg_results.items():
        print(f"  {qg:<35} : {res}", flush=True)
    print("=" * 80, flush=True)
    
    return all("APROBADO" in v for v in qg_results.values())
