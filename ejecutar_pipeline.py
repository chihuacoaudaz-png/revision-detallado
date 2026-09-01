"""
================================================================================
EJECUTOR PRINCIPAL DEL PIPELINE ETL - ROCKDRILL CONTROL OPERACIONES
================================================================================
Este script ejecuta el procesamiento completo de datos:
  1. Extracción y Limpieza de Reportes Detallados (RD.402.P.01.F.01) de los 18 CTRs.
  2. Compilación de Control Interno (RD.402.P.01.F.04).
  3. Reconciliación Diaria, Clasificación de Discrepancias y Matriz Comparativa.
  4. Modelado Dimensional Kimball (Facts & Dims en .parquet, .csv y .xlsx).
  5. Auditoría Formal de Gobernanza QA/QC (5 Quality Gates).
  6. (Opcional) Compilación de Informe Editorial en PDF de Propuesta Técnica.

MODO DE USO:
  python ejecutar_pipeline.py                         # Flujo completo integral estándar
  python ejecutar_pipeline.py --fecha-corte 2026-08-30 # Define fecha límite de conciliación
  python ejecutar_pipeline.py --generar-pdf           # Genera informe técnico en PDF
  python ejecutar_pipeline.py --solo-detallados       # Solo procesa reportes detallados
  python ejecutar_pipeline.py --solo-ci               # Solo compila Control Interno
  python ejecutar_pipeline.py --solo-conciliar        # Solo regenera matriz de conciliación
================================================================================
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from config import (
    BASE_PATH,
    MAESTRO_PATH,
    CONTROL_INTERNO_PATH,
    OUTPUT_PATH,
    HOJAS_EXCLUIDAS,
    CTRS_EXCLUIDOS
)
from src import run_full_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline ETL de Limpieza, Conciliación, Modelado Dimensional y QA/QC - Rockdrill Group",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--solo-detallados", action="store_true", help="Solo procesar Reportes Detallados")
    parser.add_argument("--solo-ci", action="store_true", help="Solo compilar Control Interno")
    parser.add_argument("--solo-conciliar", action="store_true", help="Solo regenerar matriz de conciliación")
    parser.add_argument(
        "--fecha-corte",
        type=str,
        default=None,
        help="Fecha de corte para la conciliación (Formato YYYY-MM-DD)"
    )
    parser.add_argument(
        "--export-star-schema",
        "--star-schema",
        action="store_true",
        default=True,
        help="Generar esquema estrella para Power BI (Facts, Dims, Bridge) [Por defecto: True]"
    )
    parser.add_argument(
        "--no-star-schema",
        action="store_false",
        dest="export_star_schema",
        help="Omitir generación del esquema estrella"
    )
    parser.add_argument(
        "--generar-pdf",
        action="store_true",
        help="Compilar informe ejecutivo de propuesta técnica en PDF"
    )

    args = parser.parse_args()

    t_inicio = time.time()
    print("=" * 85, flush=True)
    print("  ROCKDRILL GROUP - PIPELINE ETL INTEGRAL DE OPERACIONES", flush=True)
    print(f"  Inicio:             {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"  Carpeta de datos:   {BASE_PATH}", flush=True)
    print(f"  Carpeta de salidas: {OUTPUT_PATH}", flush=True)
    if args.fecha_corte:
        print(f"  Fecha de corte:     {args.fecha_corte}", flush=True)
    print("=" * 85, flush=True)

    run_full_pipeline(
        base_path=BASE_PATH,
        maestro_path=MAESTRO_PATH,
        control_interno_path=CONTROL_INTERNO_PATH,
        output_path=OUTPUT_PATH,
        hojas_excluidas=HOJAS_EXCLUIDAS,
        ctrs_excluidos=CTRS_EXCLUIDOS,
        solo_detallados=args.solo_detallados,
        solo_ci=args.solo_ci,
        solo_conciliacion=args.solo_conciliar,
        fecha_corte=args.fecha_corte,
        export_star_schema=args.export_star_schema,
        generar_pdf=args.generar_pdf
    )

    t_total = time.time() - t_inicio
    print("\n" + "=" * 85, flush=True)
    print(f"  PIPELINE COMPLETADO EXITOSAMENTE en {t_total:.2f} segundos", flush=True)
    print(f"  Entregables listos en: {OUTPUT_PATH}", flush=True)
    print("=" * 85 + "\n", flush=True)


if __name__ == "__main__":
    main()
