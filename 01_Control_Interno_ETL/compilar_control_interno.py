"""
ETL de Compilación de Control Interno
====================================
Módulo de extracción y consolidación de reportes diarios de avance desde:
RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx

Características y Criterios de Limpieza:
1. Lectura segura desde la Fila 10 hasta la celda de parada 'TOTAL AVANCE' en Columna C.
2. Filldown (ffill) de la Columna A para asignación estricta de CTR.
3. Exclusión explícita de CTR COLQUIJIRCA (no maneja control de metrajes en este sistema).
4. Estandarización de Turno a 'A' (Turno Día) y 'B' (Turno Noche) según secuencia diaria.
5. Generación de clave única por turno: ID_CLAVE_UNICA = {FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}.
6. Estandarización de nombres de MÁQUINA usando la tabla de Excepciones del Maestro de Máquinas SAP.
"""

import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import CONTROL_INTERNO_PATH, MAESTRO_PATH, CONTROL_INTERNO_OUTPUT_DIR as OUTPUT_DIR
except ImportError:
    BASE_PATH = Path(__file__).parent.parent / "Estructura base" / "Rockdrill_Control_Operaciones"
    CONTROL_INTERNO_PATH = BASE_PATH / "00_Control_Interno" / "RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx"
    MAESTRO_PATH = BASE_PATH / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx"
    OUTPUT_DIR = Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CTRS_EXCLUIDOS: set[str] = {"COLQUIJIRCA"}


def load_machine_exceptions(maestro_path: Path) -> Dict[Tuple[str, str], str]:
    """
    Carga la matriz de Excepciones del Maestro de Máquinas SAP.
    """
    exceptions = {}
    if not maestro_path.exists():
        return exceptions
    try:
        wb = CalamineWorkbook.from_path(str(maestro_path))
        if "Exepciones" in wb.sheet_names:
            sheet = wb.get_sheet_by_name("Exepciones")
            rows = sheet.to_python()
            for r in rows[1:]:
                if len(r) >= 3 and r[0] and r[1] and r[2]:
                    def norm(s):
                        nfkd = unicodedata.normalize('NFKD', str(s).upper().strip())
                        return ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
                    exceptions[(norm(r[0]), norm(r[1]))] = str(r[2]).strip()
        exceptions[("TICLIO", "XRD150USS-001")] = "XRD150U-007"
    except Exception as e:
        print(f"  [WARN] Error cargando Excepciones SAP: {e}")
    return exceptions


def run_compilacion_control_interno() -> pd.DataFrame:
    print("=" * 80)
    print("ETL COMPILACIÓN DE CONTROL INTERNO (CON CLAVE UNICA A/B)")
    print("=" * 80)
    print(f"Archivo origen: {CONTROL_INTERNO_PATH}")
    
    exceptions_map = load_machine_exceptions(MAESTRO_PATH)
    wb = CalamineWorkbook.from_path(str(CONTROL_INTERNO_PATH))
    
    sheet_names = [s for s in wb.sheet_names if re.match(r'^\d{2}\.\d{2}$', s)]
    print(f"Hojas diarias a procesar ({len(sheet_names)}): {sheet_names}")
    
    compiled_rows = []
    
    for sheet_name in sheet_names:
        day_str, month_str = sheet_name.split(".")
        fecha_iso = f"2026-{month_str}-{day_str}"
        
        sheet = wb.get_sheet_by_name(sheet_name)
        rows = sheet.to_python()
        
        current_ctr = None
        machine_turn_counter = {}
        
        for row_idx in range(9, len(rows)):
            r = rows[row_idx]
            
            # Condición de parada: Celda 'TOTAL AVANCE' o 'TOTAL ACUMULADO' en la fila
            row_text = " ".join([str(val).upper().strip() for val in r if val is not None])
            if "TOTAL AVANCE" in row_text or "TOTAL ACUMULADO" in row_text:
                break
            
            # Columna 0 (A): CONTRATO / CTR con Filldown (ffill)
            val_ctr = r[0] if len(r) > 0 else None
            if val_ctr is not None and str(val_ctr).strip() != "":
                raw_ctr = str(val_ctr).strip()
                if not any(k in raw_ctr.upper() for k in ["CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"]):
                    current_ctr = raw_ctr
            
            # Columna 2 (C): MÁQUINA
            val_maq = r[2] if len(r) > 2 else None
            if val_maq is None or str(val_maq).strip() == "" or str(val_maq).strip().upper() in ("EQUIPO", "SUB", "SUP"):
                continue
            
            maquina_raw = str(val_maq).strip()
            
            # Estandarizar CTR
            ctr_clean = str(current_ctr).replace("CUCULÍ", "CUCULI").replace("CUCUL", "CUCULI").upper().strip()
            if "SAN CRISTOBAL" in ctr_clean:
                ctr_clean = "SAN CRISTOBAL"
            
            # EXCLUSIÓN SEGURIDAD: Excluir Colquijirca
            if ctr_clean in CTRS_EXCLUIDOS:
                continue
            
            # Columna 4 (E): SE PERFORÓ
            val_perf = r[4] if len(r) > 4 else None
            se_perforo = str(val_perf).strip().upper() if val_perf is not None else ""
            
            # Columna 6 (G): METRAJE
            val_met = r[6] if len(r) > 6 else None
            try:
                metraje = float(str(val_met).replace(",", ".")) if val_met is not None and str(val_met).strip() != "" else 0.0
            except ValueError:
                metraje = 0.0
            
            # Estandarizar Máquina con Maestro SAP
            def norm_key(s):
                nfkd = unicodedata.normalize('NFKD', str(s).upper().strip())
                return ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
            
            lookup_key = (norm_key(ctr_clean), norm_key(maquina_raw))
            official_maq = exceptions_map.get(lookup_key, maquina_raw)
            
            # Estandarizar Turno en 'A' (Día / Guardia 1) o 'B' (Noche / Guardia 2)
            turn_key = (fecha_iso, ctr_clean, official_maq)
            machine_turn_counter[turn_key] = machine_turn_counter.get(turn_key, 0) + 1
            seq_num = machine_turn_counter[turn_key]
            t_std = "A" if seq_num == 1 else "B"
            
            clave_unica = f"{fecha_iso}|{ctr_clean}|{official_maq}|{t_std}"
            
            compiled_rows.append({
                "HOJA_FECHA": sheet_name,
                "FECHA": fecha_iso,
                "CTR": ctr_clean,
                "MAQUINA": official_maq,
                "MAQUINA_ORIGEN_CI": maquina_raw,
                "TURNO_ESTANDAR": t_std,
                "TURNO_SECUENCIA": seq_num,
                "SE_PERFORO": se_perforo,
                "METRAJE_CI": metraje,
                "ID_CLAVE_UNICA": clave_unica,
                "FILA_EXCEL": row_idx + 1
            })
    
    df = pd.DataFrame(compiled_rows)
    
    excel_out = OUTPUT_DIR / "control_interno_compilado.xlsx"
    csv_out = OUTPUT_DIR / "control_interno_compilado.csv"
    
    df.to_excel(excel_out, index=False, sheet_name="CI_COMPILADO", engine="openpyxl")
    df.to_csv(csv_out, index=False, encoding="utf-8-sig")
    
    print(f"\n[OK] Registros extraídos: {len(df)}")
    print(f"[OK] Exportado a Excel: {excel_out}")
    print(f"[OK] Exportado a CSV: {csv_out}")
    print(f"[OK] Total claves únicas de turno: {df['ID_CLAVE_UNICA'].nunique()}")
    
    gb = df.groupby("CTR")["METRAJE_CI"].agg(["count", "sum"]).reset_index()
    gb.rename(columns={"count": "Filas", "sum": "Metraje Total CI"}, inplace=True)
    print("\nRESUMEN DE METRAJES CONTROL INTERNO POR CTR (EXCLUIDO COLQUIJIRCA):")
    print(gb.to_string(index=False))
    
    return df

if __name__ == "__main__":
    run_compilacion_control_interno()
