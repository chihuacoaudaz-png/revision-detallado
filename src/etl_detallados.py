"""
ETL de Reportes Detallados de Avance (RD.402.P.01.F.01)
======================================================
Módulo de extracción y estandarización ultrarrápido (Rust Calamine + Slicing Seguro):
  1. Construcción de cabeceras dual-row (Filas 23 y 24 de Excel) con filldown horizontal.
  2. Slicing de seguridad (primeras 200 filas por hoja para bypass de hojas gigantes vacías).
  3. Extracción de datos desde fila 25 con filldown vertical de FECHA por hoja.
  4. Filtrado de filas operativas reales (descarte de pie de página).
  5. Propagación bidireccional de SONDAJE (ffill/bfill).
  6. Diccionario de renombrado de 53 columnas canónicas.
  7. Asignación inteligente y posicional de turnos (A/B) por bloque diario.
  8. Formateo y tipado estricto de las 135 columnas oficiales.
"""

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

COLS_OFICIALES: List[str] = [
    "N°", "ZONA", "CTR", "MAQUINA", "TURNO (A=1;B=2)", "GRUPO", "MES", "FECHA",
    "SONDAJE", "PROFUNDIDAD DE SONDAJE", "LINEA", "INCLINACIÓN", "DESDE", "HASTA",
    "METRAJE", "HORAS EXTRAS", "PERFORISTA", "AYUDANTE", "AYUDANTE 2",
    "TOTAL", "METROS ACUMULADO", "METROS PROYECTADO", "METROS META",
    "MARCA BROCA", "SERIE DE BROCA", "Nº BROCA", "ESTADO DE LA BROCA",
    "MARCA ESCARIADOR", "Nº ESCARIADOR", "ESTADO DEL ESCARIADOR",
    "BENTONITA", "CANT. DE BENTONITA", "UND. DE BENTONITA",
    "PAC", "CANT. DE PAC", "UND. DE PAC",
    "POLIMERO", "CANT. DE POLIMERO", "UND. DE POLIMERO",
    "LUBRICANTES", "CANT. DE LUBRICANTE", "UND. DE LUBRICANTE",
    "INHIBIDORES", "CANT. DE INHIBIDOR", "UND. DE INHIBIDOR",
    "ESTABILIZADOR", "CANT. DE ESTABILIZADOR", "UND. DE ESTABILIZADOR",
    "CLASIFICACIÓN OTROS", "OTROS PRODUCTOS", "CANT. DE OTROS", "UND. DE OTROS",
    "CANT. DE PETROLEO", "GLN DE PETROLEO",
    "Perforación", "Rimado", "Asentado / Retiro DE REVESTIMIENTO (CASING)",
    "Calibración de pozo", "Corte de Testigo", "Despeje de pozo",
    "Medición de Trayectoria / Orientación de Testigo", "Prueba de Presión Lugeon / Lefranc",
    "Recuperación de Pozo", "Tapón de Pozo", "TOTAL OPERACIÓN",
    "Inspección Prevencional / IPERC / OPT / Charlas", "Traslado e Instalación",
    "Maniobra de Barras y Tuberias", "Abastecimiento de Agua", "Movilización / Desmovilización",
    "Limpieza de Área / Desbroce / Poza de Lodos", "Desarmado de Tuberías y Equipos",
    "Esperas Operativas", "Tendido de Tuberías", "Recuperación de Herramientas",
    "Trabajos Auxiliares", "TOTAL PREPARACIÓN",
    "Mantenimiento Mecánico", "Mantenimiento Eléctrico", "Check List Pre Uso",
    "Mantenimiento Programado", "TOTAL MANTTO.",
    "Falta de Agua", "Falta de Personal", "Condiciones Climáticas Adversas",
    "Parada por Seguridad / Bloqueo", "Traslado de Personal", "Parada por Medio Ambiente",
    "Falta de Insumos / Herramientas", "Falta de Frente / Área", "Tiempos Muertos",
    "Charla Integral / Comité / Capacitación", "TOTAL STAND BY OPERATIVO",
    "Falla Mecánica", "Falla Eléctrica", "Falla Hidráulica", "Esperas Inoperativas",
    "Falla de Accesorios / Herramientas", "Falla de Bomba de Agua", "Falla de Grupo Electrógeno",
    "TOTAL STAND BY INOPERATIVO",
    "Parada Solicitada por Cliente", "Parada por Geología / Supervisión",
    "Falta de Acceso / Transporte Cliente", "Parada por Comunidad / Social",
    "Espera de Decisiones del Cliente", "TOTAL STAND BY CLIENTE",
    "Total Horas Trabajadas", "STAND BY OPERATIVO", "STAND BY INOPERATIVO", "STAND BY CLIENTE",
    "TOTAL OPERATIVO", "TOTAL INOPERATIVO", "TOTAL GENERAL HORAS",
    "HOROMETRO INICIAL", "HOROMETRO FINAL", "TOTAL HOROMETRO",
    "HORAS EFECTIVAS", "HORAS OPERATIVAS", "TOTAL HORAS OPERATIVAS",
    "DISPONIBILIDAD MECANICA", "UTILIZACION",
    "OBSERVACIONES", "DESCRIPCIÓN LITOLÓGICA", "COMENTARIOS",
    # 6 Metadatos al final
    "HOJA DE TRABAJO ORIGEN", "ARCHIVO ORIGEN", "TURNO_ESTANDAR",
    "ID_CLAVE_UNICA", "SONDAJE_PARALELO", "Alerta_Comentarios"
]

COLUMN_RENAME_DICT: Dict[str, str] = {
    "NOMBRE": "SONDAJE",
    "PROFUNDIDAD": "PROFUNDIDAD DE SONDAJE",
    "ACUMULADO": "METROS ACUMULADO",
    "PROYECTADO": "METROS PROYECTADO",
    "META": "METROS META",
    "MARCA": "MARCA BROCA",
    "SERIE": "SERIE DE BROCA",
    "MARCA_1": "MARCA ESCARIADOR",
    "MARCA_2": "MARCA ESCARIADOR",
    "HORAS EXTAS": "HORAS EXTRAS",
    "PERFORISTA": "PERFORISTA",
    "AYUDANTE": "AYUDANTE",
    "AYUDANTE_1": "AYUDANTE 2",
    "BENTONITA_PRODUCTO": "BENTONITA",
    "BENTONITA_CANT.": "CANT. DE BENTONITA",
    "BENTONITA_UND.": "UND. DE BENTONITA",
    "PAC_PRODUCTO": "PAC",
    "PAC_CANT.": "CANT. DE PAC",
    "PAC_UND.": "UND. DE PAC",
    "POLIMERO_PRODUCTO": "POLIMERO",
    "POLIMERO_CANT.": "CANT. DE POLIMERO",
    "POLIMERO_UND.": "UND. DE POLIMERO",
    "LUBRICANTES_PRODUCTO": "LUBRICANTES",
    "LUBRICANTES_CANT.": "CANT. DE LUBRICANTE",
    "LUBRICANTES_UND.": "UND. DE LUBRICANTE",
    "INHIBIDORES_PRODUCTO": "INHIBIDORES",
    "INHIBIDORES_CANT.": "CANT. DE INHIBIDOR",
    "INHIBIDORES_UND.": "UND. DE INHIBIDOR",
    "ESTABILIZADOR_PRODUCTO": "ESTABILIZADOR",
    "ESTABILIZADOR_CANT.": "CANT. DE ESTABILIZADOR",
    "ESTABILIZADOR_UND.": "UND. DE ESTABILIZADOR",
    "OTROS_CLASIFICACIÓN": "CLASIFICACIÓN OTROS",
    "OTROS_PRODUCTO": "OTROS PRODUCTOS",
    "OTROS_CANT.": "CANT. DE OTROS",
    "OTROS_UND.": "UND. DE OTROS",
    "PETROLEO_CANT.": "CANT. DE PETROLEO",
    "PETROLEO_GLN": "GLN DE PETROLEO",
    "Mantenimiento": "TOTAL MANTTO.",
    "Stand By Operativo": "STAND BY OPERATIVO",
    "Stand By Inoperativo": "STAND BY INOPERATIVO",
    "Stand By Cliente": "STAND BY CLIENTE",
    "DESCRIPCIÒN LITOLÓGICA": "DESCRIPCIÓN LITOLÓGICA",
}


def build_dual_row_headers_from_rows(rows: List[List], skip: int = SKIP_ROWS) -> Optional[List[str]]:
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

            # SLICING DE SEGURIDAD: Max 200 filas para bypass instantáneo de hojas vacías gigantes
            rows = raw_rows[:200]

            if len(rows) <= MIN_ROWS:
                continue

            headers = build_dual_row_headers_from_rows(rows, skip=SKIP_ROWS)
            if not headers:
                continue

            data_rows = rows[SKIP_ROWS + 2:]
            max_col = len(headers)
            normalized_rows = []
            for r in data_rows:
                row_len = len(r)
                if row_len < max_col:
                    r = list(r) + [None] * (max_col - row_len)
                elif row_len > max_col:
                    r = list(r[:max_col])
                normalized_rows.append(r)

            df = pd.DataFrame(normalized_rows, columns=headers)

            if len(df.columns) > 0:
                df.rename(columns={df.columns[0]: "FECHA"}, inplace=True)

            df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            df["FECHA"] = df["FECHA"].ffill()

            col_sondaje = df.columns[1] if len(df.columns) > 1 else None
            col_metraje = None
            for c in df.columns:
                if "METRAJE" in str(c).upper() and "RIMADO" not in str(c).upper() and "REPERFORACION" not in str(c).upper():
                    col_metraje = c
                    break

            sond_list = df[col_sondaje].tolist() if col_sondaje and col_sondaje in df.columns else [None] * len(df)
            turno_list = df["TURNO (A=1;B=2)"].tolist() if "TURNO (A=1;B=2)" in df.columns else [None] * len(df)
            grupo_list = df["GRUPO"].tolist() if "GRUPO" in df.columns else [None] * len(df)
            hasta_list = df["HASTA"].tolist() if "HASTA" in df.columns else [None] * len(df)
            desde_list = df["DESDE"].tolist() if "DESDE" in df.columns else [None] * len(df)
            perf_list = df["PERFORISTA"].tolist() if "PERFORISTA" in df.columns else [None] * len(df)
            met_list = df[col_metraje].tolist() if col_metraje and col_metraje in df.columns else [None] * len(df)
            obs_list = df["COMENTARIOS"].tolist() if "COMENTARIOS" in df.columns else [None] * len(df)

            valid_mask = []
            for sond, turno, grupo, hasta, desde, perf, met, obs in zip(
                sond_list, turno_list, grupo_list, hasta_list, desde_list, perf_list, met_list, obs_list
            ):
                sond_s = str(sond).strip() if pd.notna(sond) else ""
                turno_s = str(turno).strip() if pd.notna(turno) else ""
                grupo_s = str(grupo).strip() if pd.notna(grupo) else ""
                hasta_s = str(hasta).strip() if pd.notna(hasta) else ""
                perf_s = str(perf).strip() if pd.notna(perf) else ""

                # Filtrar filas de resumen / pie de plantilla
                if sond_s.startswith(">") or sond_s.upper() in ("TOTAL", "TOTAL GENERAL", "RESUMEN", "PROMEDIO", "SUMA", "TOTAL AVANCE"):
                    valid_mask.append(False)
                    continue

                if not (sond_s or turno_s or grupo_s or hasta_s or perf_s):
                    valid_mask.append(False)
                    continue

                met_val = clean_number_value(met)
                if met_val is not None and met_val > 0:
                    valid_mask.append(True)
                    continue

                desde_s = str(desde).strip() if pd.notna(desde) else ""
                if desde_s or hasta_s:
                    valid_mask.append(True)
                    continue

                obs_s = str(obs).strip() if pd.notna(obs) else ""
                if obs_s:
                    valid_mask.append(True)
                    continue

                valid_mask.append(False)

            df = df[valid_mask].copy()
            if df.empty:
                continue

            if col_sondaje:
                df[col_sondaje] = df[col_sondaje].replace(r'^\s*$', np.nan, regex=True).ffill().bfill().fillna("SIN SONDAJE")

            rename_map = {}
            for old_name, new_name in COLUMN_RENAME_DICT.items():
                if old_name in df.columns:
                    rename_map[old_name] = new_name
            df.rename(columns=rename_map, inplace=True)

            sheet_clean = sheet_name.strip().upper()
            maquina_sap = machine_exepciones.get((ctr_name, sheet_clean), sheet_clean)
            df["MAQUINA"] = maquina_sap
            df["CTR"] = ctr_name
            df["ZONA"] = "ZONA CENTRO" if ctr_name in ZONA_CENTRO else "ZONA SUR"
            df["HOJA DE TRABAJO ORIGEN"] = sheet_name
            df["ARCHIVO ORIGEN"] = excel_file.name

            # Normalización del ciclo operativo (Ciclo Setiembre: 26 Ago - 25 Set)
            def _normalizar_fecha_ciclo(f_val):
                dt_obj = pd.to_datetime(f_val, errors="coerce")
                if pd.isna(dt_obj): return None
                # Si la plantilla base trajo mes 7 en vez de mes 8 para el ciclo de Setiembre
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

            df["SONDAJE_PARALELO"] = 1
            df["Alerta_Comentarios"] = "OK"

            all_dfs.append(df)
            print(f"    [OK] {ctr_name} / {sheet_name} ({maquina_sap}): {len(df)} filas", flush=True)

    if not all_dfs:
        return pd.DataFrame()

    consolidated = pd.concat(all_dfs, ignore_index=True)

    # Reindexar con las 135 columnas oficiales para evitar fragmentación
    result = consolidated.reindex(columns=COLS_OFICIALES).copy()

    for num_col in ["METRAJE", "HASTA", "DESDE", "PROFUNDIDAD DE SONDAJE", "METROS ACUMULADO", "TOTAL OPERACIÓN", "TOTAL HOROMETRO"]:
        if num_col in result.columns:
            result[num_col] = pd.to_numeric(result[num_col].apply(clean_number_value), errors="coerce").round(2)

    result["FECHA"] = pd.to_datetime(result["FECHA"]).dt.strftime("%Y-%m-%d")
    return result
