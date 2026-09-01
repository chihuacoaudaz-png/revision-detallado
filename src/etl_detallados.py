"""
ETL de Reportes Detallados de Avance (RD.402.P.01.F.01) - 168 Columnas Canónicas
=================================================================================
Módulo de extracción y recopilación completa (Rust Calamine + 168 Columnas):
  1. Extracción íntegra de las 168 columnas (Columna A hasta Columna FL) según el estándar SIG.
  2. Slicing de seguridad (primeras 200 filas por hoja para bypass de hojas gigantes vacías).
  3. Extracción de datos desde fila 25 con filldown vertical de FECHA por hoja.
  4. Filtrado de filas operativas reales (descarte de pie de página y totales).
  5. Propagación bidireccional de SONDAJE (ffill/bfill).
  6. Asignación inteligente y posicional de turnos (A/B) por bloque diario.
  7. Generación de ID_CLAVE_UNICA (YYYYMMDD-MAQUINA-TURNO).
  8. Preservación del 100% de la información operativa sin descartar columnas ni procesamiento artificial.
"""

import os
import sys
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Union
from datetime import datetime, date

import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook

from .utils import (
    get_visible_sheet_names,
    clean_number_value,
    normalize_ctr,
    load_machine_exceptions
)

MIN_ROWS: int = 24
SKIP_ROWS: int = 22  # 0-indexed (Fila 23 de Excel)

ZONA_CENTRO: Set[str] = {
    "AMERICANA", "CHUNGAR", "TICLIO", "MOROCOCHA", "YAULIYACU",
    "SAN CRISTOBAL", "ANDAYCHAGUA", "CERRO"
}

# ------------------------------------------------------------------------------
# CATÁLOGO CANÓNICO DE 168 COLUMNAS OFICIALES (COL A HASTA COL FL)
# ------------------------------------------------------------------------------
COLS_OFICIALES_168: List[str] = [
    # 1-5: Identificación y Sondaje (Cols A:E)
    "FECHA", "SONDAJE", "PROFUNDIDAD", "LINEA", "INCLINACIÓN",
    # 6-15: Avance Diario y Cuadrilla (Cols F:O)
    "DESDE", "HASTA", "TURNO (A=1;B=2)", "GRUPO", "METRAJE",
    "HORAS EXTRAS", "PERFORISTA", "AYUDANTE 1", "AYUDANTE 2", "TOTAL metraje del dia",
    # 16-18: Comparativo y Metas (Cols P:R)
    "ACUMULADO", "PROYECTADO", "META",
    # 19-25: Herramientas de Corte (Cols S:Y)
    "MARCA BROCA", "SERIE BROCA", "Nº BROCA", "ESTADO DE LA BROCA",
    "MARCA ESCARIADOR", "Nº ESCARIADOR", "ESTADO DEL ESCARIADOR",
    # 26-50: Consumo de Aditivos (Cols Z:AX)
    "BENTONITA - PRODUCTO", "BENTONITA - CANT.", "BENTONITA - UND.",
    "PAC - PRODUCTO", "PAC - CANT.", "PAC - UND.",
    "POLIMERO - PRODUCTO", "POLIMERO - CANT.", "POLIMERO - UND.",
    "LUBRICANTES - PRODUCTO", "LUBRICANTES - CANT.", "LUBRICANTES - UND.",
    "CONTROLADOR DE PH Y DUREZA - PRODUCTO", "CONTROLADOR DE PH Y DUREZA - CANT.", "CONTROLADOR DE PH Y DUREZA - UND.",
    "INHIBIDORES - PRODUCTO", "INHIBIDORES - CANT.", "INHIBIDORES - UND.",
    "ESTABILIZADOR - PRODUCTO", "ESTABILIZADOR - CANT.", "ESTABILIZADOR - UND.",
    "OTROS - CLASIFICACIÓN", "OTROS - PRODUCTO", "OTROS - CANT.", "OTROS - UND.",
    # 51-52: Combustible Diésel (Cols AY:AZ)
    "PETROLEO - CANT.", "PETROLEO - GLN",
    # 53-56: Tiempos Operativos Directos (Cols BA:BD)
    "Perforación", "Rimado", "Asentado / Retiro de revestimiento (Casing)", "RePerforación",
    # 57-58: Tiempos de Mantenimiento (Cols BE:BF)
    "Preventivo", "Correctivo",
    # 59-77: Maniobras Operativas (Cols BG:BY)
    "Lavado de sondaje", "Mezclado de lodos", "Manipulación de tuberías", "Acondicionamiento de sondaje",
    "Cambio de línea", "Recuperación de sondaje por problemas geologicos",
    "Recuperación de materiales y o maniobras por atrapamiento",
    "Maniobras por descarga y carga de tuberías (por problemas geologicos)",
    "Perforación en fallas y/o terrenos altamente fracturados", "Medición de Desviación",
    "Traslado entre cámaras de perforación", "Cambio de punto de perforacion",
    "Anclado de máquina de perforación", "Perforación de perno de anclaje",
    "Cementación de perno de anclaje y fraguado", "Cementado y fraguado de sondaje",
    "Obturación/Sellado de sondaje con packer", "Sellado de Sondaje", "Inyección de lechada de cemento",
    # 78-97: Ensayos Geotécnicos e Hidrogeológicos (Cols BZ:CS)
    "Ensayo Lefranc", "Ensayo Lugeon", "Prueba SPT", "Prueba Shelby", "Pruebas Geotécnicas",
    "Prueba de nivel freático", "Ensayo Air Lift", "Ensayo Slug Test",
    "Instalación de piezómetro Casagrande", "Instalación de piezómetro de cuerda vibrante",
    "Instalación de inclinómetro", "Instalación de piezómetro multinivel",
    "Instrumentación, toma de presión de agua y caudal", "Prueba de lectura de inclinómetro",
    "Toma de lecturas cuerda vibrante", "SBO1", "SBO2", "SBO3", "SBO4", "SBO5",
    # 98-118: Actividades de Soporte y Seguridad (Cols CT:DN)
    "Desate de rocas", "Orden y limpieza", "Recojo de lama", "Poza de sedimentación",
    "Estandarización y Desestandarización", "Instalación de red de agua o drenaje",
    "Instalación / Desinstalación de maquina", "Traslado de accesorios", "Auditoría Interna",
    "Charla, reparto de guardia, llenado de herramientas y reportes", "Espera de repuestos mecánicos",
    "Espera de materiales e insumos de perforación", "Traslado de personal", "Refrigerio",
    "Falta de personal", "Paralización por fiestas", "Pare RD/ seguridad",
    "SBI1", "SBI2", "SBI3", "SBI4",
    # 119-145: Condiciones Cliente y Entorno Minero (Cols DO:EO)
    "Voladura", "Falta de agua", "Falta de energía", "Falta de ventilación", "Falta de servicios",
    "Espera Orden Cliente", "Espera de programa", "Espera de cámara", "Espera de sostenimiento",
    "Espera de scoop", "Espera de marcado de punto", "Espera de Topografía", "Espera de grúa",
    "Espera por puebas de permeabilidad y/o ensayos", "Auditoría externa/ Osinergmin",
    "Capacitación (Externa Cliente)", "Falta de habilitación de cámara o plataforma",
    "Espera de orden cliente", "Condiciones climáticas", "Inundación",
    "Paralización por estrés térmico o alta temperatura", "Parada por sismo/microsismo",
    "Conflicto social", "SBC1", "SBC2", "SBC3", "SBC4",
    # 146-152: Resumen y Consolidación de Horas (Cols EP:EV)
    "TIEMPO TOTAL", "TIEMPO EFECTIVO - OPERATIVO", "LOST TIME",
    "Mantenimiento", "Stand By Operativo", "Stand By Inoperativo", "Stand By Cliente",
    # 153-156: Rimado con Casing HWT/HQ (Cols EW:EZ)
    "RIMADO CASING HWT/HQ - DESDE", "RIMADO CASING HWT/HQ - HASTA",
    "RIMADO CASING HWT/HQ - METRAJE", "RIMADO CASING HWT/HQ - TOTAL",
    # 157-160: Re-Perforación (Cols FA:FD)
    "RE-PERFORACIÓN - DESDE", "RE-PERFORACIÓN - HASTA",
    "RE-PERFORACIÓN - METRAJE", "RE-PERFORACIÓN - TOTAL",
    # 161-164: Control de Horómetros (Cols FE:FH)
    "HOROMETRO - DESDE", "HOROMETRO - HASTA", "HOROMETRO - ACUMULADO", "HOROMETRO - TOTAL",
    # 165-168: Bitácora y Observaciones (Cols FI:FL)
    "BITACORA - TRABAJOS REALIZADOS", "BITACORA - REPUESTOS UTILIZADOS",
    "DESCRIPCIÓN LITOLÓGICA", "COMENTARIOS"
]

# Alias para compatibilidad con código que use COLS_OFICIALES
COLS_OFICIALES = COLS_OFICIALES_168


def build_dual_row_headers_from_rows(rows: List[List], skip: int = SKIP_ROWS) -> Optional[List[str]]:
    """
    Construye cabeceras únicas a partir de las filas 23 y 24 de Excel con filldown horizontal.
    """
    if len(rows) < skip + 2:
        return None

    primary_values = rows[skip]
    sub_values = rows[skip + 1]

    filled_primary = []
    for val in primary_values:
        if val is not None and str(val).strip() != "":
            filled_primary.append(str(val).strip())
        else:
            if filled_primary:
                filled_primary.append(filled_primary[-1])
            else:
                filled_primary.append("XP")

    headers = []
    for i in range(len(filled_primary)):
        t1 = filled_primary[i]
        t2_raw = sub_values[i] if i < len(sub_values) else None
        t2 = str(t2_raw).strip() if t2_raw is not None else ""

        if t1 == "XP":
            headers.append(t2 if t2 else f"XP_{i}")
        elif t2 == "":
            headers.append(t1)
        else:
            headers.append(f"{t1}_{t2}")

    seen = {}
    unique_headers = []
    for h in headers:
        if h in seen:
            seen[h] += 1
            unique_headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            unique_headers.append(h)

    return unique_headers


def normalize_turno_val(val: any) -> str:
    s = str(val or "").strip().upper()
    if s in ("1", "1.0", "1,0", "A", "D", "DIA", "G1"): return "A"
    if s in ("2", "2.0", "2,0", "B", "N", "NOCHE", "G2"): return "B"
    if s in ("3", "3.0", "3,0", "C", "G3"): return "C"
    return s


def assign_daily_turnos_fast(grupos_list: list, turnos_list: list, perfs_list: list) -> List[str]:
    """
    Asignación universal y matemática de turnos operativos (A = Día / B = Noche).
    """
    n = len(turnos_list)
    if n == 0: return []

    raw_turnos = [normalize_turno_val(t) for t in turnos_list]
    raw_grupos = [str(g).strip().replace(".0", "") if pd.notna(g) and str(g).strip() not in ("", "nan", "None", "0.0", "0") else "" for g in grupos_list]
    raw_perfs = [str(p or "").strip().upper() for p in perfs_list]
    raw_perfs = [p if p not in ("", "FALSO", "0.0", "NAN", "NONE", "0") else "" for p in raw_perfs]

    # FFILL: Propagar valores por celdas combinadas en Turnos, Grupos y Perforistas
    for i in range(1, n):
        if not raw_turnos[i]: raw_turnos[i] = raw_turnos[i-1]
        if not raw_grupos[i]: raw_grupos[i] = raw_grupos[i-1]
        if not raw_perfs[i]: raw_perfs[i] = raw_perfs[i-1]

    # 1. Caso de 1 sola fila en el día
    if n == 1:
        t0 = raw_turnos[0]
        if t0 in ("B", "N", "2", "2.0"):
            return ["B"]
        return ["A"]

    # 2. Caso de 2 filas en el día: Corresponde a los 2 turnos secuenciales (A = Día, B = Noche)
    if n == 2:
        return ["A", "B"]

    # 3. Caso de n >= 3 filas (Multi-sondaje o múltiples tramos en el día)
    # 3.1 Transición por GRUPO de guardia
    if any(g != "" for g in raw_grupos):
        g0 = next((g for g in raw_grupos if g != ""), "")
        if g0 != "":
            for i in range(1, n):
                gi = raw_grupos[i]
                if gi != "" and gi != g0:
                    return ["A" if idx < i else "B" for idx in range(n)]

    # 3.2 Transición por PERFORISTA
    if any(p != "" for p in raw_perfs):
        p0 = next((p for p in raw_perfs if p != ""), "")
        if p0 != "":
            for i in range(1, n):
                pi = raw_perfs[i]
                if pi != "" and pi != p0:
                    return ["A" if idx < i else "B" for idx in range(n)]

    # 3.3 Transición declarada en Turno (ej. A -> B)
    if any(t == "B" for t in raw_turnos):
        for i in range(1, n):
            if raw_turnos[i] == "B" and raw_turnos[i-1] == "A":
                return ["A" if idx < i else "B" for idx in range(n)]

    # 3.4 Reparto secuencial 50/50
    split = max(1, n // 2)
    return ["A" if i < split else "B" for i in range(n)]


def run_etl_detallados(
    base_path: Path,
    maestro_path: Path,
    hojas_excluidas: Set[str],
    ctrs_excluidos: Set[str]
) -> pd.DataFrame:
    """
    Recopila y consolida todos los reportes detallados en las 168 columnas canónicas (A:FL).
    """
    machine_exepciones = load_machine_exceptions(maestro_path)
    all_dfs = []

    ctr_dirs = sorted([d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("CTR_")])

    for ctr_dir in ctr_dirs:
        ctr_name = normalize_ctr(ctr_dir.name)
        if ctr_name in ctrs_excluidos:
            continue

        det_dir = ctr_dir / "02_Detallado"
        if not det_dir.exists():
            continue

        excel_files = [f for f in det_dir.glob("*.xls*") if not f.name.startswith("~$")]
        if not excel_files:
            continue

        excel_file = excel_files[0]
        visible_sheets = get_visible_sheet_names(excel_file)

        try:
            wb = CalamineWorkbook.from_path(str(excel_file))
        except Exception as e:
            print(f"  [ERROR] No se pudo leer {excel_file.name}: {e}", flush=True)
            continue

        for sheet_name in wb.sheet_names:
            if sheet_name in hojas_excluidas or sheet_name not in visible_sheets:
                continue

            try:
                raw_rows = wb.get_sheet_by_name(sheet_name).to_python()
            except Exception:
                continue

            # Slicing de seguridad: primeras 200 filas para bypass de hojas gigantes vacías
            rows = raw_rows[:200]
            if len(rows) <= MIN_ROWS:
                continue

            data_rows = rows[24:]
            max_col = len(COLS_OFICIALES_168)
            normalized_rows = []
            for r in data_rows:
                r_list = list(r)
                if len(r_list) < max_col:
                    r_list += [None] * (max_col - len(r_list))
                elif len(r_list) > max_col:
                    r_list = r_list[:max_col]
                normalized_rows.append(r_list)

            df = pd.DataFrame(normalized_rows, columns=COLS_OFICIALES_168)

            df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            df["FECHA"] = df["FECHA"].ffill()

            # Columnas clave para filtrado operacional
            col_sondaje = "SONDAJE"
            col_metraje = "METRAJE"
            col_desde = "DESDE"
            col_hasta = "HASTA"
            col_obs = "COMENTARIOS"

            valid_mask = []
            for _, row in df.iterrows():
                f_val = str(row["FECHA"]).strip() if pd.notna(row["FECHA"]) else ""
                if not f_val or "TOTAL" in f_val.upper() or "RESUMEN" in f_val.upper():
                    valid_mask.append(False)
                    continue

                sond_s = str(row[col_sondaje]).strip() if pd.notna(row[col_sondaje]) else ""
                if sond_s.startswith(">") or sond_s.upper() in ("TOTAL", "TOTAL GENERAL", "RESUMEN", "PROMEDIO", "SUMA", "TOTAL AVANCE"):
                    valid_mask.append(False)
                    continue

                met_val = clean_number_value(row[col_metraje])
                if met_val is not None and met_val > 0:
                    valid_mask.append(True)
                    continue

                desde_s = str(row[col_desde]).strip() if pd.notna(row[col_desde]) else ""
                hasta_s = str(row[col_hasta]).strip() if pd.notna(row[col_hasta]) else ""
                if desde_s or hasta_s:
                    valid_mask.append(True)
                    continue

                obs_s = str(row[col_obs]).strip() if pd.notna(row[col_obs]) else ""
                if obs_s or (sond_s and sond_s != "SIN SONDAJE"):
                    valid_mask.append(True)
                    continue

                valid_mask.append(False)

            df = df[valid_mask].copy()
            if df.empty:
                continue

            df[col_sondaje] = df[col_sondaje].replace(r'^\s*$', np.nan, regex=True).ffill().bfill().fillna("SIN SONDAJE")

            sheet_clean = sheet_name.strip().upper()
            maquina_sap = machine_exepciones.get((ctr_name, sheet_clean), sheet_clean)

            # Insertar metadatos al inicio
            df.insert(0, "CTR", ctr_name)
            df.insert(1, "MAQUINA", maquina_sap)

            # Normalización de ciclo
            def _normalizar_fecha_ciclo(f_val):
                dt_obj = pd.to_datetime(f_val, errors="coerce")
                if pd.isna(dt_obj): return None
                if dt_obj.year == 2026 and dt_obj.month == 7 and dt_obj.day in (26, 27, 28, 29, 30, 31):
                    dt_obj = dt_obj.replace(month=8)
                return dt_obj.strftime("%Y-%m-%d")

            df["FECHA_NORM"] = df["FECHA"].apply(_normalizar_fecha_ciclo)
            df = df[df["FECHA_NORM"].notna()].copy()
            if df.empty:
                continue

            df["TURNO_ESTANDAR"] = ""
            for _, idxs in df.groupby("FECHA_NORM", sort=False).groups.items():
                sub = df.loc[idxs]
                g_list = sub["GRUPO"].tolist() if "GRUPO" in sub.columns else [None] * len(sub)
                t_list = sub["TURNO (A=1;B=2)"].tolist() if "TURNO (A=1;B=2)" in sub.columns else [None] * len(sub)
                p_list = sub["PERFORISTA"].tolist() if "PERFORISTA" in sub.columns else [None] * len(sub)
                df.loc[idxs, "TURNO_ESTANDAR"] = assign_daily_turnos_fast(g_list, t_list, p_list)

            maq_code = re.sub(r'[^A-Za-z0-9_-]', '', str(maquina_sap).strip())
            df["ID_CLAVE_UNICA"] = (
                df["FECHA_NORM"].str.replace("-", "") + "-" +
                maq_code + "-" +
                df["TURNO_ESTANDAR"]
            )
            df["FECHA"] = df["FECHA_NORM"]
            df.drop(columns=["FECHA_NORM"], inplace=True)

            df["ARCHIVO ORIGEN"] = excel_file.name
            df["HOJA DE TRABAJO ORIGEN"] = sheet_name

            all_dfs.append(df)
            print(f"    [OK] {ctr_name} / {sheet_name} ({maquina_sap}): {len(df)} filas", flush=True)

    if not all_dfs:
        return pd.DataFrame()

    consolidated = pd.concat(all_dfs, ignore_index=True)

    # Limpieza de columnas numéricas principales para consistencia analítica
    cols_numericas = [
        "METRAJE", "HASTA", "DESDE", "PROFUNDIDAD", "TOTAL metraje del dia",
        "ACUMULADO", "PROYECTADO", "META",
        "Perforación", "Rimado", "Asentado / Retiro de revestimiento (Casing)", "RePerforación",
        "Preventivo", "Correctivo", "TIEMPO TOTAL", "TIEMPO EFECTIVO - OPERATIVO", "LOST TIME",
        "Mantenimiento", "Stand By Operativo", "Stand By Inoperativo", "Stand By Cliente",
        "HOROMETRO - TOTAL"
    ]
    for num_col in cols_numericas:
        if num_col in consolidated.columns:
            consolidated[num_col] = pd.to_numeric(consolidated[num_col].apply(clean_number_value), errors="coerce").round(2)

    consolidated["FECHA"] = pd.to_datetime(consolidated["FECHA"]).dt.strftime("%Y-%m-%d")
    return consolidated
