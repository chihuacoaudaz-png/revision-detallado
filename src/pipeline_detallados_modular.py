"""
Pipeline Maestro Modular de Ingesta, Limpieza, Detección de Anomalías y Generación de Esquema Estrella
Rockdrill Group - Sistema de Producción para Detallados
"""
import os
import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple, Set
from python_calamine import CalamineWorkbook

# Forzar UTF-8 en salida estándar de Windows
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

# Asegurar importación de módulos hermanos
base_module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base_module_dir not in sys.path:
    sys.path.insert(0, base_module_dir)

try:
    from src.etl_detallados import (
        build_dual_row_headers_from_rows,
        assign_daily_turnos_fast,
        clean_number_value,
        COLS_OFICIALES,
        COLUMN_RENAME_DICT,
        SKIP_ROWS,
        MIN_ROWS
    )
    from src.utils import get_visible_sheet_names
except ImportError:
    from etl_detallados import (
        build_dual_row_headers_from_rows,
        assign_daily_turnos_fast,
        clean_number_value,
        COLS_OFICIALES,
        COLUMN_RENAME_DICT,
        SKIP_ROWS,
        MIN_ROWS
    )
    from utils import get_visible_sheet_names

class PipelineDetalladosModular:
    """
    Orquestador de producción para lectura recursiva por CTR, resolución de anomalías,
    generación del Log de Rectificación de Campo y exportación del Esquema Estrella.
    """
    def __init__(self, directorio_base_ctrs: str = "data_in/CTRs", directorio_salida: str = "output"):
        self.directorio_base = Path(directorio_base_ctrs).resolve()
        self.directorio_salida = Path(directorio_salida).resolve()
        self.dir_star_schema = self.directorio_salida / "star_schema"
        self.dir_star_schema.mkdir(parents=True, exist_ok=True)
        
        # Estructuras de hechos consolidadas
        self.registros_avance: List[Dict[str, Any]] = []
        self.registros_horas: List[Dict[str, Any]] = []
        self.anomalias_detectadas: List[Dict[str, Any]] = []
        
        # Catálogos maestros dinámicos
        self.personal_dict: Dict[str, int] = {"[NO ESPECIFICADO / PERSONAL PENDIENTE]": -1}
        self.sondajes_dict: Dict[str, int] = {"[SONDAJE NO ASIGNADO]": -1}
        self.ctrs_dict: Dict[str, int] = {"[CTR NO ASIGNADO]": -1}
        self.maquinas_dict: Dict[str, int] = {"[EQUIPO NO DEFINIDO]": -1}
        self.counter_personal = 1
        self.counter_sondajes = 1
        self.counter_ctrs = 1
        self.counter_maquinas = 1

    def procesar_todos_los_ctrs(self) -> pd.DataFrame:
        """
        Escanea y procesa todos los libros de trabajo en las carpetas de CTRs.
        """
        all_dfs = []
        ctr_dirs = sorted([d for d in self.directorio_base.iterdir() if d.is_dir()])
        
        print(f"📦 Se detectaron {len(ctr_dirs)} carpetas de CTRs en {self.directorio_base}")

        for ctr_dir in ctr_dirs:
            ctr_name = ctr_dir.name
            excel_files = [f for f in ctr_dir.glob("*.xls*") if not f.name.startswith("~$")]
            
            for excel_file in excel_files:
                try:
                    visible_sheets = get_visible_sheet_names(excel_file)
                    wb = CalamineWorkbook.from_path(str(excel_file))
                except Exception as e:
                    print(f"  [ERROR] No se pudo leer {excel_file.name}: {e}")
                    self.anomalias_detectadas.append({
                        "Fecha": "N/A", "CTR": ctr_name, "Maquina": "N/A", "Guardia": "N/A",
                        "Codigo_Anomalia": "ERR_LECTURA_EXCEL", "Detalle": str(e), "Accion": "Reenviar archivo"
                    })
                    continue

                for sheet_name in wb.sheet_names:
                    sn_up = sheet_name.strip().upper()
                    if sn_up in ("RESUMEN", "METAS", "PARAMETROS", "GLOSARIO", "INFORME", "CARATULA", "ADITIVOS", "LISTAS") or sheet_name not in visible_sheets:
                        continue

                    try:
                        raw_rows = wb.get_sheet_by_name(sheet_name).to_python()
                    except Exception:
                        continue

                    # Slicing de seguridad (primeras 200 filas)
                    rows = raw_rows[:200]
                    if len(rows) <= MIN_ROWS:
                        continue

                    headers = build_dual_row_headers_from_rows(rows, skip=SKIP_ROWS)
                    if not headers:
                        continue

                    # Asegurar que la columna 0 sea FECHA
                    if headers and (headers[0].startswith("XP_") or "DÍA" in headers[0].upper() or "DIA" in headers[0].upper()):
                        headers[0] = "FECHA"

                    data_rows = rows[SKIP_ROWS + 2:]
                    max_col = len(headers)
                    normalized_rows = []
                    for r in data_rows:
                        row_len = len(r)
                        if row_len < max_col:
                            normalized_rows.append(list(r) + [None] * (max_col - row_len))
                        elif row_len > max_col:
                            normalized_rows.append(list(r[:max_col]))
                        else:
                            normalized_rows.append(list(r))

                    df = pd.DataFrame(normalized_rows, columns=headers)

                    # Columna FECHA en posición 0 o por nombre
                    col_fecha = "FECHA" if "FECHA" in df.columns else df.columns[0]
                    df["FECHA"] = df[col_fecha].replace(r'^\s*$', np.nan, regex=True).ffill()
                    df = df[df["FECHA"].notna()].copy()
                    if df.empty:
                        continue

                    # Filtrar filas operativas reales (descarte de pie de página)
                    col_desde = next((c for c in df.columns if c.startswith("DESDE")), None)
                    col_hasta = next((c for c in df.columns if c.startswith("HASTA")), None)
                    col_met = next((c for c in df.columns if "METRAJE" in c.upper()), None)
                    col_sondaje = next((c for c in df.columns if "SONDAJE" in c.upper() or "NOMBRE" in c.upper()), None)

                    valid_mask = []
                    for _, r_val in df.iterrows():
                        met_val = clean_number_value(r_val.get(col_met)) if col_met else None
                        if met_val is not None and met_val > 0:
                            valid_mask.append(True); continue
                        d_val = str(r_val.get(col_desde, "")).strip() if col_desde else ""
                        h_val = str(r_val.get(col_hasta, "")).strip() if col_hasta else ""
                        if d_val or h_val:
                            valid_mask.append(True); continue
                        valid_mask.append(False)

                    df = df[valid_mask].copy()
                    if df.empty:
                        continue

                    if col_sondaje:
                        df[col_sondaje] = df[col_sondaje].replace(r'^\s*$', np.nan, regex=True).ffill().bfill().fillna("SIN SONDAJE")

                    # Renombrar columnas
                    rename_map = {}
                    for old_name, new_name in COLUMN_RENAME_DICT.items():
                        if old_name in df.columns:
                            rename_map[old_name] = new_name
                    df.rename(columns=rename_map, inplace=True)

                    maquina_clean = sheet_name.strip().upper()
                    df["MAQUINA"] = maquina_clean
                    df["CTR"] = ctr_name
                    df["HOJA ORIGEN"] = sheet_name
                    df["ARCHIVO ORIGEN"] = excel_file.name

                    df["FECHA_NORM"] = pd.to_datetime(df["FECHA"], errors="coerce").dt.strftime("%Y-%m-%d")
                    df = df[df["FECHA_NORM"].notna()].copy()
                    if df.empty:
                        continue

                    # Asignación de turnos A/B con algoritmo inteligente
                    col_grupo = next((c for c in df.columns if "GRUPO" in c), None)
                    col_turno = next((c for c in df.columns if "TURNO" in c), None)
                    col_perf = next((c for c in df.columns if "PERFORISTA" in c), None)

                    df["TURNO_ESTANDAR"] = "A"
                    for _, idxs in df.groupby("FECHA_NORM", sort=False).groups.items():
                        sub = df.loc[idxs]
                        g_list = sub[col_grupo].tolist() if col_grupo else [None] * len(sub)
                        t_list = sub[col_turno].tolist() if col_turno else [None] * len(sub)
                        p_list = sub[col_perf].tolist() if col_perf else [None] * len(sub)
                        df.loc[idxs, "TURNO_ESTANDAR"] = assign_daily_turnos_fast(g_list, t_list, p_list)

                    all_dfs.append(df)
                    print(f"    [OK] {ctr_name} / {sheet_name}: {len(df)} filas extraídas")

        if not all_dfs:
            print("⚠️ No se encontraron filas operativas en los archivos.")
            return pd.DataFrame()

        df_consolidado = pd.concat(all_dfs, ignore_index=True)
        return df_consolidado

    def ejecutar_pipeline_completo(self) -> Dict[str, str]:
        """Ejecuta el pipeline completo de punta a punta."""
        print("=" * 80)
        print("🚀 INICIANDO PIPELINE MODULAR DE PRODUCCIÓN (ENTREGABLE 1 - PYTHON)")
        print(f"📦 Origen: {self.directorio_base}")
        print("=" * 80)

        df_raw = self.procesar_todos_los_ctrs()
        if df_raw.empty:
            print("❌ No se pudieron consolidar datos.")
            return {}

        print(f"\n📊 TOTAL EXTRAÍDO: {len(df_raw):,} registros de {df_raw['CTR'].nunique()} CTRs.")

        # Construir tablas de hechos y dimensiones con SKs
        for idx, row in df_raw.iterrows():
            f_norm = str(row.get("FECHA_NORM", "")).strip()
            cal_sk = int(f_norm.replace("-", "")) if f_norm and f_norm != "nan" else -1
            
            ctr_name = str(row.get("CTR", "[CTR NO ASIGNADO]")).strip().upper()
            maq_name = str(row.get("MAQUINA", "[EQUIPO NO DEFINIDO]")).strip().upper()
            turno = str(row.get("TURNO_ESTANDAR", "A")).strip().upper()
            grupo = str(row.get("GRUPO", "1")).strip().replace(".0", "")
            perf_name = str(row.get("PERFORISTA", "[NO ESPECIFICADO / PERSONAL PENDIENTE]")).strip().upper()
            if perf_name in ("", "NAN", "NONE", "0", "0.0", "FALSO"):
                perf_name = "[NO ESPECIFICADO / PERSONAL PENDIENTE]"
                
            sond_name = str(row.get("SONDAJE", "[SONDAJE NO ASIGNADO]")).strip().upper()
            if sond_name in ("", "NAN", "NONE", "0", "0.0", "SIN SONDAJE"):
                sond_name = "[SONDAJE NO ASIGNADO]"

            # Asignar SKs
            if ctr_name not in self.ctrs_dict:
                self.ctrs_dict[ctr_name] = self.counter_ctrs; self.counter_ctrs += 1
            ctr_sk = self.ctrs_dict[ctr_name]

            if maq_name not in self.maquinas_dict:
                self.maquinas_dict[maq_name] = self.counter_maquinas; self.counter_maquinas += 1
            maq_sk = self.maquinas_dict[maq_name]

            if perf_name not in self.personal_dict:
                self.personal_dict[perf_name] = self.counter_personal; self.counter_personal += 1
            perf_sk = self.personal_dict[perf_name]

            if sond_name not in self.sondajes_dict:
                self.sondajes_dict[sond_name] = self.counter_sondajes; self.counter_sondajes += 1
            sond_sk = self.sondajes_dict[sond_name]

            # Avance
            desde = float(pd.to_numeric(clean_number_value(row.get("DESDE")), errors="coerce") or 0.0)
            hasta = float(pd.to_numeric(clean_number_value(row.get("HASTA")), errors="coerce") or 0.0)
            metraje = float(pd.to_numeric(clean_number_value(row.get("METRAJE")), errors="coerce") or 0.0)
            if metraje == 0.0 and hasta > desde:
                metraje = round(hasta - desde, 2)

            # Detección de Anomalías
            tiene_anom = False
            cod_anom = "OK"
            if hasta < desde:
                tiene_anom = True
                cod_anom = "ERR_MONOTONIA_COTAS"
                self.anomalias_detectadas.append({
                    "Fecha": f_norm, "CTR": ctr_name, "Maquina": maq_name, "Guardia": turno,
                    "Codigo_Anomalia": cod_anom, "Detalle": f"HASTA ({hasta}m) < DESDE ({desde}m)",
                    "Accion": "Rectificar cotas en mina"
                })
            elif perf_name == "[NO ESPECIFICADO / PERSONAL PENDIENTE]":
                tiene_anom = True
                cod_anom = "ERR_PERFORISTA_NULO"
                self.anomalias_detectadas.append({
                    "Fecha": f_norm, "CTR": ctr_name, "Maquina": maq_name, "Guardia": turno,
                    "Codigo_Anomalia": cod_anom, "Detalle": "Campo Perforista en blanco",
                    "Accion": "Solicitar fotocheck a campo"
                })

            obs_txt = str(row.get("OBSERVACIONES", "")).upper() + " " + str(row.get("COMENTARIOS", "")).upper()
            es_reperf = "REPERFO" in obs_txt
            tipo_pase = "REPERFORACION" if es_reperf else "AVANCE_VIRGEN"

            # Fact Avance
            self.registros_avance.append({
                "avance_id": len(self.registros_avance) + 1,
                "calendario_sk": cal_sk, "contrato_sk": ctr_sk, "equipo_sk": maq_sk,
                "sondaje_sk": sond_sk, "linea_sk": 1, "perforista_sk": perf_sk,
                "turno_guardia": turno, "grupo_rotativo": grupo, "tipo_pase_perforacion": tipo_pase,
                "es_reperforacion": es_reperf, "desde_m": desde, "hasta_m": hasta,
                "metraje_guardia_m": metraje, "horas_extras_guardia": 0.0,
                "tiene_anomalia": tiene_anom, "codigo_anomalia_campo": cod_anom,
                "codigo_guardia": f"{ctr_name}-{maq_name}-{f_norm}-{turno}"
            })

            # Fact Horas
            h_perfo = float(pd.to_numeric(clean_number_value(row.get("Perforación")), errors="coerce") or 0.0)
            if h_perfo == 0.0 and metraje > 0: h_perfo = 8.0
            h_mtto = float(pd.to_numeric(clean_number_value(row.get("TOTAL MANTTO.")), errors="coerce") or 0.0)
            h_sbc = float(pd.to_numeric(clean_number_value(row.get("TOTAL STAND BY CLIENTE")), errors="coerce") or 0.0)

            if h_perfo > 0:
                self.registros_horas.append({
                    "hora_evento_id": len(self.registros_horas) + 1, "calendario_sk": cal_sk,
                    "contrato_sk": ctr_sk, "equipo_sk": maq_sk, "sondaje_sk": sond_sk, "actividad_sk": 1,
                    "turno_guardia": turno, "grupo_rotativo": grupo, "horas_reportadas": h_perfo,
                    "es_cobrable": True, "categoria_disponibilidad": "OPERATIVO_COBRABLE", "tiene_desbalance_guardia": False
                })
            if h_mtto > 0:
                self.registros_horas.append({
                    "hora_evento_id": len(self.registros_horas) + 1, "calendario_sk": cal_sk,
                    "contrato_sk": ctr_sk, "equipo_sk": maq_sk, "sondaje_sk": sond_sk, "actividad_sk": 21,
                    "turno_guardia": turno, "grupo_rotativo": grupo, "horas_reportadas": h_mtto,
                    "es_cobrable": False, "categoria_disponibilidad": "MANTENIMIENTO_NO_COBRABLE", "tiene_desbalance_guardia": False
                })
            if h_sbc > 0:
                self.registros_horas.append({
                    "hora_evento_id": len(self.registros_horas) + 1, "calendario_sk": cal_sk,
                    "contrato_sk": ctr_sk, "equipo_sk": maq_sk, "sondaje_sk": sond_sk, "actividad_sk": 50,
                    "turno_guardia": turno, "grupo_rotativo": grupo, "horas_reportadas": h_sbc,
                    "es_cobrable": True, "categoria_disponibilidad": "STANDBY_CLIENTE_COBRABLE", "tiene_desbalance_guardia": False
                })

        # Exportar CSVs y Excels
        rutas = {}
        df_fa = pd.DataFrame(self.registros_avance)
        ruta_fa = self.dir_star_schema / "fact_perforacion_avance.csv"
        df_fa.to_csv(str(ruta_fa), index=False, encoding="utf-8-sig")
        rutas["fact_perforacion_avance"] = str(ruta_fa)

        df_fh = pd.DataFrame(self.registros_horas)
        ruta_fh = self.dir_star_schema / "fact_horas_operativas.csv"
        df_fh.to_csv(str(ruta_fh), index=False, encoding="utf-8-sig")
        rutas["fact_horas_operativas"] = str(ruta_fh)

        # Dimensiones
        df_ctr = pd.DataFrame([{"contrato_sk": sk, "contrato_cd": k, "nombre_contrato": k} for k, sk in self.ctrs_dict.items()])
        ruta_ctr = self.dir_star_schema / "dim_contrato_minero.csv"
        df_ctr.to_csv(str(ruta_ctr), index=False, encoding="utf-8-sig")
        rutas["dim_contrato_minero"] = str(ruta_ctr)

        df_maq = pd.DataFrame([{"equipo_sk": sk, "equipo_cd": k, "modelo_fabricante": k, "horas_dia_planeadas": 24} for k, sk in self.maquinas_dict.items()])
        ruta_maq = self.dir_star_schema / "dim_equipo_perforadora.csv"
        df_maq.to_csv(str(ruta_maq), index=False, encoding="utf-8-sig")
        rutas["dim_equipo_perforadora"] = str(ruta_maq)

        df_per = pd.DataFrame([{"personal_sk": sk, "personal_cd": k, "nombre_completo": k, "rol_estandarizado": "PERFORISTA"} for k, sk in self.personal_dict.items()])
        ruta_per = self.dir_star_schema / "dim_personal.csv"
        df_per.to_csv(str(ruta_per), index=False, encoding="utf-8-sig")
        rutas["dim_personal"] = str(ruta_per)

        df_sdj = pd.DataFrame([{"sondaje_sk": sk, "sondaje_cd": k, "profundidad_programada_m": 300.0, "tipo_taladro": "ORIGINAL"} for k, sk in self.sondajes_dict.items()])
        ruta_sdj = self.dir_star_schema / "dim_sondaje_taladro.csv"
        df_sdj.to_csv(str(ruta_sdj), index=False, encoding="utf-8-sig")
        rutas["dim_sondaje_taladro"] = str(ruta_sdj)

        # Anomalias
        df_anom = pd.DataFrame(self.anomalias_detectadas)
        ruta_anom = self.directorio_salida / "reporte_anomalias_campo.xlsx"
        df_anom.to_excel(str(ruta_anom), index=False, engine="openpyxl")
        rutas["reporte_anomalias_campo"] = str(ruta_anom)

        # Consolidado
        ruta_cons = self.directorio_salida / "detallados_consolidados.xlsx"
        df_fa.to_excel(str(ruta_cons), index=False, engine="openpyxl")
        rutas["detallados_consolidados"] = str(ruta_cons)

        print("\n" + "=" * 80)
        print("🏁 PROCESAMIENTO COMPLETADO EXITOSAMENTE:")
        print(f"   • {len(df_fa):,} registros de avance generados.")
        print(f"   • {len(df_fh):,} registros de horas operativas generadas.")
        print(f"   • {len(df_anom):,} anomalías detectadas en campo.")
        print(f"   • Salida Excel Consolidada: {ruta_cons}")
        print(f"   • Salida Reporte Anomalías: {ruta_anom}")
        print("=" * 80)
        return rutas

if __name__ == "__main__":
    pipeline = PipelineDetalladosModular()
    res = pipeline.ejecutar_pipeline_completo()
