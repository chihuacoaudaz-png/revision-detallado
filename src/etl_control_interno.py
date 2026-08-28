"""
ETL de Compilación de Control Interno (RD.402.P.01.F.04)
======================================================
Módulo encargado de:
  1. Lectura de las pestañas diarias del consolidado oficial de Control Interno (formato dd.mm).
  2. Extracción desde la Fila 10 hasta la celda de parada 'TOTAL AVANCE' o 'TOTAL ACUMULADO'.
  3. Filldown de CTR (Columna A) y lectura de máquina (Columna C) y metraje por guardia (Columna G).
  4. Secuenciación automática de turnos en 'A' (Día / Guardia 1) y 'B' (Noche / Guardia 2).
  5. Estandarización de nombres de máquina según la matriz de Excepciones del Maestro SAP.
"""

import re
import unicodedata
from pathlib import Path
from datetime import datetime, date
from typing import Set
import pandas as pd
from python_calamine import CalamineWorkbook

from .utils import (
    clean_number_value,
    normalize_ctr,
    load_machine_exceptions
)


def run_etl_control_interno(
    control_interno_path: Path,
    maestro_path: Path,
    ctrs_excluidos: Set[str]
) -> pd.DataFrame:
    """
    Extrae y compila las pestañas diarias del libro maestro de Control Interno.
    """
    if not control_interno_path.exists():
        print(f"  [AVISO] No existe Control Interno en: {control_interno_path}", flush=True)
        return pd.DataFrame(columns=["FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"])

    exceptions_map = load_machine_exceptions(maestro_path)
    try:
        wb = CalamineWorkbook.from_path(str(control_interno_path))
    except Exception as e:
        print(f"  [WARN] Error abriendo Control Interno ({control_interno_path}): {e}", flush=True)
        return pd.DataFrame(columns=["FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"])

    # Filtrar solo hojas con formato dd.mm
    sheet_names = [s for s in wb.sheet_names if re.match(r'^\d{1,2}\.\d{1,2}$', str(s).strip())]
    if not sheet_names:
        print("  [WARN] No se encontraron hojas con formato de fecha (dd.mm).", flush=True)
        return pd.DataFrame(columns=["FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"])

    # Inferir año base
    m_match = re.search(r'20\d{2}', control_interno_path.name)
    base_year = int(m_match.group(0)) if m_match else datetime.now().year

    compiled_rows = []
    prev_m = None
    current_year = base_year

    for sheet_name in sheet_names:
        parts = str(sheet_name).strip().split(".")
        try:
            d_int, m_int = int(parts[0]), int(parts[1])
            # Manejo de fin de año
            temp_year = current_year
            if prev_m is not None and m_int < prev_m and prev_m == 12:
                temp_year += 1
            fecha_dt = datetime(temp_year, m_int, d_int)
            current_year = temp_year
            prev_m = m_int
            fecha_iso = f"{current_year:04d}-{m_int:02d}-{d_int:02d}"
        except (ValueError, OverflowError):
            print(f"  [WARN] Pestaña con fecha inválida '{sheet_name}', omitiendo.", flush=True)
            continue

        sheet = wb.get_sheet_by_name(sheet_name)
        rows = sheet.to_python()

        current_ctr = None
        machine_turn_counter = {}

        for row_idx in range(9, len(rows)):
            r = rows[row_idx]
            if not r or len(r) < 3:
                continue

            row_text = " ".join([str(val).upper().strip() for val in r if val is not None])
            if "TOTAL AVANCE" in row_text or "TOTAL ACUMULADO" in row_text or "TOTAL GENERAL" in row_text:
                break

            # Columna 0 (A): CTR con filldown
            val_ctr = r[0] if len(r) > 0 else None
            if val_ctr is not None and str(val_ctr).strip() != "":
                raw_ctr = str(val_ctr).strip()
                if not any(k in raw_ctr.upper() for k in ["CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"]):
                    current_ctr = raw_ctr

            # Columna 2 (C): MÁQUINA
            if len(r) <= 2 or r[2] is None or str(r[2]).strip() == "":
                continue

            maquina_raw = str(r[2]).strip()
            if maquina_raw.upper() in ("EQUIPO", "SUB", "SUP", "MAQUINA", "NONE", "-"):
                continue

            ctr_clean = normalize_ctr(current_ctr)
            if ctr_clean in ctrs_excluidos or not ctr_clean:
                continue

            # Columna 4 (E): SE PERFORO
            val_perf = r[4] if len(r) > 4 else None
            se_perforo = str(val_perf).strip().upper() if val_perf is not None else ""

            # Columna 6 (G): METRAJE
            val_met = r[6] if len(r) > 6 else None
            metraje = clean_number_value(val_met) or 0.0

            # Estandarización de máquina
            official_maq = exceptions_map.get((ctr_clean, maquina_raw.upper()), maquina_raw.upper())

            # Asignación de turno A (1ra fila) / B (2da fila)
            turn_key = (fecha_iso, ctr_clean, official_maq)
            machine_turn_counter[turn_key] = machine_turn_counter.get(turn_key, 0) + 1
            seq_num = machine_turn_counter[turn_key]
            t_std = "A" if seq_num == 1 else "B"

            maq_clean_code = re.sub(r'[^A-Za-z0-9_-]', '', str(official_maq).strip())
            clave_unica = f"{fecha_dt.strftime('%Y%m%d')}-{maq_clean_code}-{t_std}"

            compiled_rows.append({
                "HOJA_FECHA": sheet_name,
                "FECHA": fecha_iso,
                "CTR": ctr_clean,
                "MAQUINA": official_maq,
                "TURNO_ESTANDAR": t_std,
                "METRAJE_CI": metraje,
                "SE_PERFORO": se_perforo,
                "ID_CLAVE_UNICA": clave_unica
            })

    if not compiled_rows:
        return pd.DataFrame(columns=["FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "METRAJE_CI", "SE_PERFORO", "ID_CLAVE_UNICA"])

    df_ci = pd.DataFrame(compiled_rows)
    return df_ci
