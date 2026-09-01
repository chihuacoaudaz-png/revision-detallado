"""
Orquestador Principal del Pipeline ETL y Modelado Dimensional (Rockdrill)
========================================================================
Coordina de principio a fin los 5 pasos del flujo de datos empresarial:
  1. ETL de Detallados (18 CTRs) -> output/detallados_consolidados.xlsx/csv
  2. ETL de Control Interno -> output/control_interno/control_interno_compilado.xlsx/csv
  3. Reconciliación 1-a-1 de Metrajes -> output/matriz_comparativa_metrajes.xlsx
  4. Modelado Dimensional Kimball (Facts & Dims) -> output/powerbi_star_schema/ (.parquet, .csv, .xlsx)
  5. Auditoría de Gobernanza QA/QC (5 Quality Gates) -> output/reporte_anomalias_campo.xlsx
"""

import time
from pathlib import Path
from typing import Optional, Set, Tuple
import pandas as pd

from .etl_detallados import run_etl_detallados
from .etl_control_interno import run_etl_control_interno
from .reconciliacion import reconciliar_metrajes
from .modelado_dimensional import construir_modelo_dimensional
from .validador_qaqc import ejecutar_auditoria_qaqc


def run_full_pipeline(
    base_path: Path,
    maestro_path: Path,
    control_interno_path: Path,
    output_path: Path,
    hojas_excluidas: Set[str],
    ctrs_excluidos: Set[str],
    solo_detallados: bool = False,
    solo_ci: bool = False,
    solo_conciliacion: bool = False,
    fecha_corte: Optional[str] = None,
    export_star_schema: bool = True,
    generar_pdf: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el pipeline integral de datos (Detallados + Control Interno + Conciliación + Modelo Dimensional + QA/QC).
    """
    output_path.mkdir(parents=True, exist_ok=True)
    ci_output_dir = output_path / "control_interno"
    ci_output_dir.mkdir(parents=True, exist_ok=True)

    df_det = pd.DataFrame()
    df_ci = pd.DataFrame()

    # Paso 1: Detallados
    if not solo_ci and not solo_conciliacion:
        print("\n" + "=" * 80, flush=True)
        print("  PASO 1: PROCESANDO REPORTES DETALLADOS (18 CTRs)", flush=True)
        print("=" * 80, flush=True)
        df_det = run_etl_detallados(
            base_path=base_path,
            maestro_path=maestro_path,
            hojas_excluidas=hojas_excluidas,
            ctrs_excluidos=ctrs_excluidos
        )
        if not df_det.empty:
            det_xlsx = output_path / "detallados_consolidados.xlsx"
            det_csv = output_path / "detallados_consolidados.csv"
            try:
                df_det.to_excel(str(det_xlsx), index=False, sheet_name="R. DETALLADO", engine="openpyxl")
            except PermissionError:
                det_xlsx_fallback = output_path / "detallados_consolidados_actualizada.xlsx"
                print(f"  [AVISO] '{det_xlsx.name}' está abierto en Excel. Guardando copia en '{det_xlsx_fallback.name}'", flush=True)
                df_det.to_excel(str(det_xlsx_fallback), index=False, sheet_name="R. DETALLADO", engine="openpyxl")
            df_det.to_csv(str(det_csv), index=False, encoding="utf-8-sig")
            print(f"  [OK DETALLADOS] {len(df_det):,} registros | {df_det['CTR'].nunique()} CTRs | {df_det['MAQUINA'].nunique()} Máquinas", flush=True)
            print(f"  Exportado en: {det_xlsx}", flush=True)

    # Paso 2: Control Interno
    if not solo_detallados and not solo_conciliacion:
        print("\n" + "=" * 80, flush=True)
        print("  PASO 2: COMPILANDO CONTROL INTERNO", flush=True)
        print("=" * 80, flush=True)
        df_ci = run_etl_control_interno(
            control_interno_path=control_interno_path,
            maestro_path=maestro_path,
            ctrs_excluidos=ctrs_excluidos
        )
        if not df_ci.empty:
            ci_xlsx = ci_output_dir / "control_interno_compilado.xlsx"
            ci_csv = ci_output_dir / "control_interno_compilado.csv"
            try:
                df_ci.to_excel(str(ci_xlsx), index=False)
            except PermissionError:
                ci_xlsx_fallback = ci_output_dir / "control_interno_compilado_actualizada.xlsx"
                print(f"  [AVISO] '{ci_xlsx.name}' está abierto en Excel. Guardando copia en '{ci_xlsx_fallback.name}'", flush=True)
                df_ci.to_excel(str(ci_xlsx_fallback), index=False)
            df_ci.to_csv(str(ci_csv), index=False, encoding="utf-8-sig")
            print(f"  [OK CONTROL INTERNO] {len(df_ci):,} registros compilados", flush=True)
            print(f"  Exportado en: {ci_xlsx}", flush=True)

    # Paso 3: Reconciliación
    if not solo_detallados and not solo_ci:
        print("\n" + "=" * 80, flush=True)
        print("  PASO 3: CONCILIACIÓN Y MATRIZ DE DISCREPANCIAS", flush=True)
        print("=" * 80, flush=True)
        if df_det.empty:
            det_csv = output_path / "detallados_consolidados.csv"
            if det_csv.exists():
                df_det = pd.read_csv(det_csv, low_memory=False)
        if df_ci.empty:
            ci_csv = ci_output_dir / "control_interno_compilado.csv"
            if ci_csv.exists():
                df_ci = pd.read_csv(ci_csv, low_memory=False)

        if not df_det.empty and not df_ci.empty:
            corte = fecha_corte
            if not corte:
                if "FECHA" in df_ci.columns and df_ci["FECHA"].notna().any():
                    corte = str(df_ci["FECHA"].max())
                else:
                    corte = "2026-08-30"

            comp, disc, res_ctr = reconciliar_metrajes(df_det, df_ci, output_path, fecha_corte=corte)
            coincidencias = len(comp) - len(disc)
            pct = (coincidencias / len(comp) * 100) if len(comp) > 0 else 0.0
            print(f"  [OK CONCILIACIÓN (Hasta {corte})] Total Claves Evaluadas: {len(comp):,}", flush=True)
            print(f"  Coincidencia Exacta (0.00 m): {coincidencias:,} ({pct:.2f}%)", flush=True)
            print(f"  Discrepancias Reales: {len(disc)} claves", flush=True)
            print(f"  Exportado en: {output_path / 'matriz_comparativa_metrajes.xlsx'}", flush=True)

    # Paso 4: Modelado Dimensional Kimball para Power BI / SQL Warehouse
    if export_star_schema:
        print("\n" + "=" * 80, flush=True)
        print("  PASO 4: MODELADO DIMENSIONAL KIMBALL (ESTRELLA EMPRESARIAL)", flush=True)
        print("=" * 80, flush=True)
        if df_det.empty:
            det_csv = output_path / "detallados_consolidados.csv"
            if det_csv.exists():
                df_det = pd.read_csv(det_csv, low_memory=False)
        if not df_det.empty:
            star_dir = output_path / "powerbi_star_schema"
            tablas_estrella = construir_modelo_dimensional(df_det, maestro_path, star_dir)
            
            # Paso 5: Validación QA/QC
            print("\n" + "=" * 80, flush=True)
            print("  PASO 5: VALIDACIÓN DE GOBERNANZA QA/QC (5 QUALITY GATES)", flush=True)
            print("=" * 80, flush=True)
            reporte_anomalias_path = output_path / "reporte_anomalias_campo.xlsx"
            ejecutar_auditoria_qaqc(tablas_estrella, df_det, reporte_anomalias_path)

    # Paso 6: Generación de PDF (Opcional)
    if generar_pdf:
        print("\n" + "=" * 80, flush=True)
        print("  PASO 6: GENERANDO INFORME TÉCNICO EN PDF", flush=True)
        print("=" * 80, flush=True)
        from generar_pdf_propuesta import generar_pdf as compilar_pdf
        compilar_pdf(output_path)

    return df_det, df_ci
