"""
Módulo Principal de Ingeniería de Datos - Pipeline Rockdrill
============================================================
Paquete con los submódulos de extracción, estandarización y conciliación:
  - utils: Funciones de soporte, parseo XML y normalizaciones.
  - etl_detallados: Limpieza de Reportes Detallados (RD.402.P.01.F.01).
  - etl_control_interno: Compilación de Control Interno (RD.402.P.01.F.04).
  - reconciliacion: Matriz comparativa y auditoría de metrajes.
  - pipeline: Orquestador integral de ejecución.
"""

from .utils import (
    get_visible_sheet_names,
    clean_number_value,
    normalize_ctr,
    load_machine_exceptions
)
from .etl_detallados import run_etl_detallados
from .etl_control_interno import run_etl_control_interno
from .reconciliacion import run_conciliacion, reconciliar_metrajes
from .pipeline import run_full_pipeline

__all__ = [
    "get_visible_sheet_names",
    "clean_number_value",
    "normalize_ctr",
    "load_machine_exceptions",
    "run_etl_detallados",
    "run_etl_control_interno",
    "run_conciliacion",
    "reconciliar_metrajes",
    "run_full_pipeline",
]
