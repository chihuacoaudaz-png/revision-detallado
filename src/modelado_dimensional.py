"""
Módulo de Modelado Dimensional Empresarial (Kimball Star Schema)
Rockdrill Group - Sistema Unificado de Analítica de Perforación
Transforma la base de datos consolidada (174 columnas) en un esquema estrella normalizado
con Llaves Subrogadas Enteras (_sk), miembros desconocidos (-1), unpivoting de 116 tiempos
y tabla puente de cuadrillas.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Tuple, List, Optional
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

from src.utils import normalize_ctr, load_machine_exceptions, clean_number_value
from src.etl_detallados import COLS_OFICIALES_168

# ==============================================================================
# TAXONOMÍA OFICIAL DE LAS 116 ACTIVIDADES OPERATIVAS Y SUS 5 CATEGORÍAS
# ==============================================================================
TAXONOMIA_ACTIVIDADES = [
    # 1. TIEMPOS OPERATIVOS DIRECTOS (Efectivos)
    ("Perforación", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("Rimado", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("Asentado / Retiro Casing", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("RePerforación", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    
    # 2. MANTENIMIENTO
    ("Preventivo", "Tiempos de Mantenimiento", "Mantenimiento", False, True),
    ("Correctivo", "Tiempos de Mantenimiento", "Mantenimiento", False, True),
    
    # 3. MANIOBRAS OPERATIVAS (Stand By Operativo) - 19 Maniobras
    ("Lavado de sondaje", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Mezclado de lodos", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Manipulación de tuberías", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Acondicionamiento de sondaje", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Cambio de línea", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Recuperación de sondaje por problemas geologicos", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Recuperación de materiales y o maniobras por atrapamiento", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Maniobras por descarga y carga de tuberías (por problemas geologicos)", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Perforación en fallas y/o terrenos altamente fracturados", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Medición de Desviación", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Traslado entre cámaras de perforación", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Cambio de punto de perforacion", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Anclado de máquina de perforación", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Perforación de perno de anclaje", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Cementación de perno de anclaje y fraguado", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Cementado y fraguado de sondaje", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Obturación/Sellado de sondaje con packer", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Sellado de Sondaje", "Maniobras Operativas", "Stand By Operativo", False, False),
    ("Inyección de lechada de cemento", "Maniobras Operativas", "Stand By Operativo", False, False),
    
    # 4. ENSAYOS GEOTÉCNICOS E HIDROGEOLÓGICOS (Stand By Operativo) - 20 Ensayos
    ("Ensayo Lefranc", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Ensayo Lugeon", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Prueba SPT", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Prueba Shelby", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Pruebas Geotécnicas", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Prueba de nivel freático", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Ensayo Air Lift", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Ensayo Slug Test", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro Casagrande", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro de cuerda vibrante", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Instalación de inclinómetro", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro multinivel", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Instrumentación, toma de presión de agua y caudal", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Prueba de lectura de inclinómetro", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("Toma de lecturas cuerda vibrante", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", True, False),
    ("SBO1", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", False, False),
    ("SBO2", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", False, False),
    ("SBO3", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", False, False),
    ("SBO4", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", False, False),
    ("SBO5", "Ensayos Geotécnicos e Hidrogeológicos", "Stand By Operativo", False, False),
    
    # 5. SOPORTE Y SEGURIDAD (Stand By Inoperativo) - 21 Actividades
    ("Desate de rocas", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Orden y limpieza", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Recojo de lama", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Poza de sedimentación", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Estandarización y Desestandarización", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Instalación de red de agua o drenaje", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Instalación / Desinstalación de maquina", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Traslado de accesorios", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Auditoría Interna", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Charla, reparto de guardia, llenado de herramientas y reportes", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Espera de repuestos mecánicos", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Espera de materiales e insumos de perforación", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Traslado de personal", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Refrigerio", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Falta de personal", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Paralización por fiestas", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Pare RD/ seguridad", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI1", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI2", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI3", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI4", "Actividades de Soporte y Seguridad", "Stand By Inoperativo", False, False),
    
    # 6. CONDICIONES CLIENTE Y ENTORNO MINERO (Stand By Cliente) - 27 Eventos
    ("Voladura", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Falta de agua", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Falta de energía", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Falta de ventilación", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Falta de servicios", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera Orden Cliente", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de programa", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de cámara", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de sostenimiento", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de scoop", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de marcado de punto", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de Topografía", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de grúa", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera por puebas de permeabilidad y/o ensayos", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Auditoría externa/ Osinergmin", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Capacitación (Externa Cliente)", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Falta de habilitación de cámara o plataforma", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Espera de orden cliente", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Condiciones climáticas", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Inundación", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Paralización por estrés térmico o alta temperatura", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Parada por sismo/microsismo", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("Conflicto social", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("SBC1", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("SBC2", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("SBC3", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
    ("SBC4", "Condiciones Cliente y Entorno Minero", "Stand By Cliente", True, False),
]

def construir_modelo_dimensional(
    df_raw: pd.DataFrame,
    maestro_path: Path,
    output_dir: Path
) -> Dict[str, pd.DataFrame]:
    """
    Construye las 7 Dimensiones, 3 Tablas de Hechos y 1 Tabla Puente del Esquema Estrella Kimball.
    """
    print("=" * 80)
    print("  MODELADO DIMENSIONAL KIMBALL (POWER BI & SQL WAREHOUSE)")
    print("=" * 80)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    exepciones = load_machine_exceptions(maestro_path)
    
    # -------------------------------------------------------------------------
    # 0. PREPARACIÓN Y NORMALIZACIÓN DEL DATASET RAW
    # -------------------------------------------------------------------------
    df = df_raw.copy()
    
    # Normalizar Contrato
    col_ctr = "CTR" if "CTR" in df.columns else "Nombre_CTR"
    df["CTR_NORM"] = df[col_ctr].apply(normalize_ctr)
    
    # Normalizar Fecha
    def normalizar_fecha(val):
        if pd.isna(val): return None
        dt = pd.to_datetime(val, errors='coerce')
        if pd.isna(dt): return None
        if dt.year == 2026 and dt.month == 7 and dt.day >= 26:
            dt = dt.replace(month=8)
        return dt.strftime('%Y-%m-%d')
    
    df["FECHA_NORM"] = df["FECHA"].apply(normalizar_fecha)
    df = df[df["FECHA_NORM"].notna()].copy()
    
    # Normalizar Turno
    if "TURNO_ESTANDAR" in df.columns:
        df["TURNO_NORM"] = df["TURNO_ESTANDAR"].astype(str).str.strip().str.upper()
    else:
        col_t = "TURNO (A=1;B=2)" if "TURNO (A=1;B=2)" in df.columns else "TURNO"
        df["TURNO_NORM"] = df[col_t].astype(str).str.strip().str.upper().map(lambda x: 'A' if x in ('A', '1') else 'B')
    
    # Normalizar Máquina
    col_maq = "MAQUINA" if "MAQUINA" in df.columns else "SheetName"
    def homologar_maq(row):
        ctr = row["CTR_NORM"]
        maq = str(row[col_maq]).strip().upper()
        return exepciones.get((ctr, maq), maq)
    
    df["MAQUINA_HOMOLOGADA"] = df.apply(homologar_maq, axis=1)
    
    # Reconstruir ID_CLAVE_UNICA canónica
    df["FECHA_KEY"] = df["FECHA_NORM"].str.replace("-", "", regex=False)
    df["ID_CLAVE_UNICA_CANONICA"] = df["FECHA_KEY"] + "-" + df["MAQUINA_HOMOLOGADA"] + "-" + df["TURNO_NORM"]
    
    # Normalizar Sondaje
    col_sond = "SONDAJE" if "SONDAJE" in df.columns else "NOMBRE"
    df["SONDAJE_NORM"] = df[col_sond].fillna("SIN SONDAJE").astype(str).str.strip().str.upper()
    df.loc[df["SONDAJE_NORM"] == "", "SONDAJE_NORM"] = "SIN SONDAJE"
    
    # Normalizar Línea
    col_linea = "LINEA" if "LINEA" in df.columns else "DIAMETRO"
    df["LINEA_NORM"] = df[col_linea].fillna("NO ESPECIFICADO").astype(str).str.strip().str.upper()
    df.loc[df["LINEA_NORM"] == "", "LINEA_NORM"] = "NO ESPECIFICADO"
    
    # Normalizar Personal
    col_perf = "PERFORISTA" if "PERFORISTA" in df.columns else "PERFORISTA_1"
    df["PERFORISTA_NORM"] = df[col_perf].fillna("NO ESPECIFICADO").astype(str).str.strip().str.upper()
    df.loc[df["PERFORISTA_NORM"] == "", "PERFORISTA_NORM"] = "NO ESPECIFICADO"
    
    col_ay1 = "AYUDANTE 1" if "AYUDANTE 1" in df.columns else ("AYUDANTE" if "AYUDANTE" in df.columns else None)
    df["AYUDANTE1_NORM"] = df[col_ay1].fillna("NO ESPECIFICADO").astype(str).str.strip().str.upper() if col_ay1 else "NO ESPECIFICADO"
    df.loc[df["AYUDANTE1_NORM"] == "", "AYUDANTE1_NORM"] = "NO ESPECIFICADO"

    col_ay2 = "AYUDANTE 2" if "AYUDANTE 2" in df.columns else ("AYUDANTE_1" if "AYUDANTE_1" in df.columns else None)
    df["AYUDANTE2_NORM"] = df[col_ay2].fillna("NO ESPECIFICADO").astype(str).str.strip().str.upper() if col_ay2 else "NO ESPECIFICADO"
    df.loc[df["AYUDANTE2_NORM"] == "", "AYUDANTE2_NORM"] = "NO ESPECIFICADO"

    # =========================================================================
    # 1. DIMENSIÓN: dim_tiempo_calendario
    # =========================================================================
    print("  [1/10] Generando dim_tiempo_calendario...", flush=True)
    min_date = pd.to_datetime(df["FECHA_NORM"].min())
    max_date = pd.to_datetime(df["FECHA_NORM"].max())
    
    # Expandir rango completo del mes
    start_cal = min_date.replace(day=1)
    end_cal = (max_date + pd.DateOffset(months=1)).replace(day=1) - pd.Timedelta(days=1)
    date_range = pd.date_range(start=start_cal, end=end_cal, freq='D')
    
    cal_rows = [
        {
            "calendario_sk": -1,
            "fecha_dt": "1900-01-01",
            "anio_civil": 1900,
            "mes_num_civil": 1,
            "mes_nom_civil": "NO DEFINIDO",
            "dia_mes": 1,
            "dia_semana_num": 1,
            "dia_semana_nom": "NO DEFINIDO",
            "es_fin_semana": False,
            "trimestre_civil": "Q0",
            "anio_operativo": 1900,
            "mes_num_operativo": 1,
            "mes_nom_operativo": "NO DEFINIDO",
            "mes_anio_operativo": "N/D",
            "periodo_operativo_sort": 190001,
            "dia_ciclo_operativo": 0,
            "es_cierre_operativo": False
        }
    ]
    
    meses_esp = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    dias_esp = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    
    for dt in date_range:
        cal_sk = int(dt.strftime("%Y%m%d"))
        if dt.day >= 26:
            op_month_dt = dt + pd.DateOffset(months=1)
            op_mes_num = op_month_dt.month
            op_anio = op_month_dt.year
            dia_ciclo = dt.day - 25
        else:
            op_mes_num = dt.month
            op_anio = dt.year
            dia_ciclo = (dt - (dt.replace(day=1) - pd.Timedelta(days=1)).replace(day=26)).days + 1
            
        op_mes_nom = meses_esp[op_mes_num]
        periodo_sort = op_anio * 100 + op_mes_num
        mes_anio_op = f"{op_mes_nom[:3].upper()}-{str(op_anio)[2:]}"
        
        cal_rows.append({
            "calendario_sk": cal_sk,
            "fecha_dt": dt.strftime("%Y-%m-%d"),
            "anio_civil": dt.year,
            "mes_num_civil": dt.month,
            "mes_nom_civil": meses_esp[dt.month],
            "dia_mes": dt.day,
            "dia_semana_num": dt.weekday() + 1,
            "dia_semana_nom": dias_esp[dt.weekday()],
            "es_fin_semana": dt.weekday() >= 5,
            "trimestre_civil": f"Q{(dt.month-1)//3 + 1}",
            "anio_operativo": op_anio,
            "mes_num_operativo": op_mes_num,
            "mes_nom_operativo": op_mes_nom,
            "mes_anio_operativo": mes_anio_op,
            "periodo_operativo_sort": periodo_sort,
            "dia_ciclo_operativo": dia_ciclo,
            "es_cierre_operativo": dt.day == 25
        })
        
    dim_tiempo_calendario = pd.DataFrame(cal_rows)

    # =========================================================================
    # 2. DIMENSIÓN: dim_contrato_minero
    # =========================================================================
    print("  [2/10] Generando dim_contrato_minero...", flush=True)
    ctrs_unicos = sorted(df["CTR_NORM"].unique())
    ctr_rows = [
        {
            "contrato_sk": -1,
            "contrato_cd": "NO_ASIGNADO",
            "nombre_contrato": "[CTR NO ASIGNADO]",
            "cliente_minero": "NO ESPECIFICADO",
            "zona_geografica": "CENTRO",
            "tipo_operacion": "SUBTERRANEA",
            "estado_vigencia": "ACTIVO"
        }
    ]
    ctr_sk_map = {"NO_ASIGNADO": -1}
    for idx, ctr in enumerate(ctrs_unicos, start=1):
        ctr_rows.append({
            "contrato_sk": idx,
            "contrato_cd": ctr,
            "nombre_contrato": f"CONTRATO {ctr}",
            "cliente_minero": "CLIENTE MINERO TITULAR",
            "zona_geografica": "CENTRO" if "ANDAYCHAGUA" in ctr or "CHUNGAR" in ctr or "TICLIO" in ctr or "MOROCOCHA" in ctr or "SAN CRISTOBAL" in ctr or "YAULIYACU" in ctr else ("SUR" if "INMACULADA" in ctr or "TAMBOJASA" in ctr else "CENTRO"),
            "tipo_operacion": "SUPERFICIE" if "CUCULI" in ctr else "SUBTERRANEA",
            "estado_vigencia": "ACTIVO"
        })
        ctr_sk_map[ctr] = idx
    dim_contrato_minero = pd.DataFrame(ctr_rows)

    # =========================================================================
    # 3. DIMENSIÓN: dim_equipo_perforadora
    # =========================================================================
    print("  [3/10] Generando dim_equipo_perforadora...", flush=True)
    maqs_unicas = sorted(df[["MAQUINA_HOMOLOGADA", "CTR_NORM"]].drop_duplicates().values, key=lambda x: (x[1], x[0]))
    maq_rows = [
        {
            "equipo_sk": -1,
            "equipo_cd": "NO_ASIGNADO",
            "codigo_sap": "SAP-000",
            "modelo_fabricante": "[EQUIPO NO ASIGNADO]",
            "fabricante": "ROCKDRILL",
            "tipo_energia": "ELECTRO-HIDRAULICA",
            "horas_dia_planeadas": 24,
            "contrato_sk_asignado": -1,
            "estado_operativo": "OPERATIVO"
        }
    ]
    maq_sk_map = {("NO_ASIGNADO", -1): -1}
    for idx, (maq, ctr) in enumerate(maqs_unicas, start=1):
        c_sk = ctr_sk_map.get(ctr, -1)
        maq_rows.append({
            "equipo_sk": idx,
            "equipo_cd": maq,
            "codigo_sap": f"SAP-{maq}",
            "modelo_fabricante": maq,
            "fabricante": "ROCKDRILL",
            "tipo_energia": "DIESEL" if "DE710" in maq or "LF90" in maq else "ELECTRO-HIDRAULICA",
            "horas_dia_planeadas": 24,
            "contrato_sk_asignado": c_sk,
            "estado_operativo": "OPERATIVO"
        })
        maq_sk_map[(maq, c_sk)] = idx
        maq_sk_map[maq] = idx
    dim_equipo_perforadora = pd.DataFrame(maq_rows)

    # =========================================================================
    # 4. DIMENSIÓN: dim_linea_diametro
    # =========================================================================
    print("  [4/10] Generando dim_linea_diametro...", flush=True)
    lineas_unicas = sorted(df["LINEA_NORM"].unique())
    linea_rows = [
        {
            "linea_sk": -1,
            "linea_cd": "NO_ESPECIFICADO",
            "tipo_tuberia": "DESCONOCIDO",
            "diametro_corona_mm": 0.0,
            "diametro_testigo_mm": 0.0
        }
    ]
    linea_sk_map = {"NO_ESPECIFICADO": -1}
    for idx, lin in enumerate(lineas_unicas, start=1):
        dia_corona = 96.0 if "HQ" in lin or "HWT" in lin else (75.7 if "NQ" in lin else (60.0 if "BQ" in lin else 122.6))
        dia_testigo = 63.5 if "HQ" in lin else (47.6 if "NQ" in lin else (36.4 if "BQ" in lin else 85.0))
        linea_rows.append({
            "linea_sk": idx,
            "linea_cd": lin,
            "tipo_tuberia": "WIRELINE DIAMANTINA",
            "diametro_corona_mm": dia_corona,
            "diametro_testigo_mm": dia_testigo
        })
        linea_sk_map[lin] = idx
    dim_linea_diametro = pd.DataFrame(linea_rows)

    # =========================================================================
    # 5. DIMENSIÓN: dim_personal
    # =========================================================================
    print("  [5/10] Generando dim_personal...", flush=True)
    todos_nombres = set()
    for n in df["PERFORISTA_NORM"].unique():
        if n and n != "NO ESPECIFICADO": todos_nombres.add((n, "PERFORISTA"))
    for n in df["AYUDANTE1_NORM"].unique():
        if n and n != "NO ESPECIFICADO": todos_nombres.add((n, "AYUDANTE 1"))
    for n in df["AYUDANTE2_NORM"].unique():
        if n and n != "NO ESPECIFICADO": todos_nombres.add((n, "AYUDANTE 2"))
        
    personal_rows = [
        {
            "personal_sk": -1,
            "personal_cd": "NO_ESPECIFICADO",
            "dni_carnet": "00000000",
            "nombre_completo": "[PERSONAL NO ESPECIFICADO]",
            "rol_estandarizado": "NO DEFINIDO",
            "contratista_propio": "ROCKDRILL",
            "estado_personal": "ACTIVO"
        }
    ]
    personal_sk_map = {"NO ESPECIFICADO": -1}
    for idx, (nom, rol) in enumerate(sorted(todos_nombres), start=1):
        personal_rows.append({
            "personal_sk": idx,
            "personal_cd": f"PER-{idx:04d}",
            "dni_carnet": f"DNI{idx:05d}",
            "nombre_completo": nom,
            "rol_estandarizado": rol,
            "contratista_propio": "ROCKDRILL",
            "estado_personal": "ACTIVO"
        })
        personal_sk_map[nom] = idx
    dim_personal = pd.DataFrame(personal_rows)

    # =========================================================================
    # 6. DIMENSIÓN: dim_sondaje_taladro
    # =========================================================================
    print("  [6/10] Generando dim_sondaje_taladro...", flush=True)
    sondajes_unicos = sorted(df[["SONDAJE_NORM", "CTR_NORM"]].drop_duplicates().values, key=lambda x: (x[1], x[0]))
    sondaje_rows = [
        {
            "sondaje_sk": -1,
            "sondaje_cd": "NO_ASIGNADO",
            "contrato_sk": -1,
            "sondaje_padre_sk": -1,
            "tipo_taladro": "ORIGINAL",
            "profundidad_programada_m": 0.0,
            "inclinacion_grados": 0.0
        }
    ]
    sondaje_sk_map = {("NO_ASIGNADO", -1): -1}
    for idx, (sond, ctr) in enumerate(sondajes_unicos, start=1):
        c_sk = ctr_sk_map.get(ctr, -1)
        es_ramal = sond.endswith("A") or sond.endswith("B") or sond.endswith("R")
        sondaje_rows.append({
            "sondaje_sk": idx,
            "sondaje_cd": sond,
            "contrato_sk": c_sk,
            "sondaje_padre_sk": -1,
            "tipo_taladro": "RAMAL_PARALELO" if es_ramal else "ORIGINAL",
            "profundidad_programada_m": 300.0,
            "inclinacion_grados": -45.0
        })
        sondaje_sk_map[(sond, c_sk)] = idx
        sondaje_sk_map[sond] = idx
    dim_sondaje_taladro = pd.DataFrame(sondaje_rows)

    # =========================================================================
    # 7. DIMENSIÓN: dim_taxonomia_actividad
    # =========================================================================
    print("  [7/10] Generando dim_taxonomia_actividad...", flush=True)
    actividad_rows = [
        {
            "actividad_sk": -1,
            "nombre_actividad": "[ACTIVIDAD NO CATALOGADA]",
            "bloque_funcional": "NO CATALOGADO",
            "categoria_disponibilidad": "Stand By Inoperativo",
            "es_cobrable": False,
            "impacta_disp_mecanica": False
        }
    ]
    actividad_sk_map = {}
    for idx, (nombre, bloque, categ, cobrable, disp_mec) in enumerate(TAXONOMIA_ACTIVIDADES, start=1):
        actividad_rows.append({
            "actividad_sk": idx,
            "nombre_actividad": nombre,
            "bloque_funcional": bloque,
            "categoria_disponibilidad": categ,
            "es_cobrable": cobrable,
            "impacta_disp_mecanica": disp_mec
        })
        actividad_sk_map[nombre] = idx
    dim_taxonomia_actividad = pd.DataFrame(actividad_rows)

    # =========================================================================
    # 8. TABLA DE HECHOS: fact_perforacion_avance
    # =========================================================================
    print("  [8/10] Generando fact_perforacion_avance...", flush=True)
    avance_rows = []
    col_met = "METRAJE" if "METRAJE" in df.columns else "METRAJE_PERFORADO"
    col_desde = "DESDE" if "DESDE" in df.columns else "DESDE_M"
    col_hasta = "HASTA" if "HASTA" in df.columns else "HASTA_M"
    
    for idx, row in df.iterrows():
        f_dt = row["FECHA_NORM"]
        cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
        c_sk = ctr_sk_map.get(row["CTR_NORM"], -1)
        m_sk = maq_sk_map.get((row["MAQUINA_HOMOLOGADA"], c_sk), maq_sk_map.get(row["MAQUINA_HOMOLOGADA"], -1))
        s_sk = sondaje_sk_map.get((row["SONDAJE_NORM"], c_sk), sondaje_sk_map.get(row["SONDAJE_NORM"], -1))
        l_sk = linea_sk_map.get(row["LINEA_NORM"], -1)
        p_sk = personal_sk_map.get(row["PERFORISTA_NORM"], -1)
        
        metraje = clean_number_value(row.get(col_met)) or 0.0
        desde = clean_number_value(row.get(col_desde)) or 0.0
        hasta = clean_number_value(row.get(col_hasta)) or 0.0
        
        avance_rows.append({
            "avance_id": len(avance_rows) + 1,
            "calendario_sk": cal_sk,
            "contrato_sk": c_sk,
            "equipo_sk": m_sk,
            "sondaje_sk": s_sk,
            "perforista_sk": p_sk,
            "linea_sk": l_sk,
            "turno_guardia": row["TURNO_NORM"],
            "desde_m": round(desde, 2),
            "hasta_m": round(hasta, 2),
            "metraje_guardia_m": round(metraje, 2),
            "es_reperforacion": False,
            "id_clave_unica": row["ID_CLAVE_UNICA_CANONICA"]
        })
    fact_perforacion_avance = pd.DataFrame(avance_rows)

    # =========================================================================
    # 9. TABLA DE HECHOS: fact_horas_operativas (Unpivoting de 116 Actividades)
    # =========================================================================
    print("  [9/10] Generando fact_horas_operativas (Unpivoting de Tiempos)...", flush=True)
    horas_rows = []
    
    for act_nom, act_bloque, act_categ, act_cobrable, act_disp_mec in TAXONOMIA_ACTIVIDADES:
        col_match = None
        for c in df.columns:
            if c.strip().upper() == act_nom.strip().upper() or c.strip().upper().endswith("_" + act_nom.strip().upper()):
                col_match = c
                break
        
        if col_match is not None:
            act_sk = actividad_sk_map.get(act_nom, -1)
            for idx, row in df.iterrows():
                val_h = clean_number_value(row.get(col_match))
                if val_h is not None and val_h > 0:
                    f_dt = row["FECHA_NORM"]
                    cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
                    c_sk = ctr_sk_map.get(row["CTR_NORM"], -1)
                    m_sk = maq_sk_map.get((row["MAQUINA_HOMOLOGADA"], c_sk), maq_sk_map.get(row["MAQUINA_HOMOLOGADA"], -1))
                    
                    horas_rows.append({
                        "hora_evento_id": len(horas_rows) + 1,
                        "calendario_sk": cal_sk,
                        "contrato_sk": c_sk,
                        "equipo_sk": m_sk,
                        "actividad_sk": act_sk,
                        "turno_guardia": row["TURNO_NORM"],
                        "horas_reportadas": round(val_h, 2),
                        "es_cobrable": act_cobrable,
                        "categoria_disponibilidad": act_categ,
                        "id_clave_unica": row["ID_CLAVE_UNICA_CANONICA"]
                    })
    fact_horas_operativas = pd.DataFrame(horas_rows)

    # =========================================================================
    # 10. TABLA PUENTE: brg_cuadrilla_guardia
    # =========================================================================
    print("  [10/10] Generando brg_cuadrilla_guardia...", flush=True)
    cuadrilla_rows = []
    for idx, row in df.iterrows():
        f_dt = row["FECHA_NORM"]
        cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
        c_sk = ctr_sk_map.get(row["CTR_NORM"], -1)
        m_sk = maq_sk_map.get((row["MAQUINA_HOMOLOGADA"], c_sk), maq_sk_map.get(row["MAQUINA_HOMOLOGADA"], -1))
        
        # Perforista
        if row["PERFORISTA_NORM"] != "NO ESPECIFICADO":
            p_sk = personal_sk_map.get(row["PERFORISTA_NORM"], -1)
            cuadrilla_rows.append({
                "asignacion_id": len(cuadrilla_rows) + 1,
                "calendario_sk": cal_sk,
                "equipo_sk": m_sk,
                "personal_sk": p_sk,
                "rol_desempenado": "PERFORISTA",
                "horas_laboradas": 12.0,
                "id_clave_unica": row["ID_CLAVE_UNICA_CANONICA"]
            })
        # Ayudante 1
        if row["AYUDANTE1_NORM"] != "NO ESPECIFICADO":
            ay1_sk = personal_sk_map.get(row["AYUDANTE1_NORM"], -1)
            cuadrilla_rows.append({
                "asignacion_id": len(cuadrilla_rows) + 1,
                "calendario_sk": cal_sk,
                "equipo_sk": m_sk,
                "personal_sk": ay1_sk,
                "rol_desempenado": "AYUDANTE 1",
                "horas_laboradas": 12.0,
                "id_clave_unica": row["ID_CLAVE_UNICA_CANONICA"]
            })
        # Ayudante 2
        if row["AYUDANTE2_NORM"] != "NO ESPECIFICADO":
            ay2_sk = personal_sk_map.get(row["AYUDANTE2_NORM"], -1)
            cuadrilla_rows.append({
                "asignacion_id": len(cuadrilla_rows) + 1,
                "calendario_sk": cal_sk,
                "equipo_sk": m_sk,
                "personal_sk": ay2_sk,
                "rol_desempenado": "AYUDANTE 2",
                "horas_laboradas": 12.0,
                "id_clave_unica": row["ID_CLAVE_UNICA_CANONICA"]
            })
    brg_cuadrilla_guardia = pd.DataFrame(cuadrilla_rows)

    # Fact Metas Mensuales
    metas_rows = []
    for (m_sk, c_sk), grp in fact_perforacion_avance.groupby(["equipo_sk", "contrato_sk"]):
        metas_rows.append({
            "meta_id": len(metas_rows) + 1,
            "contrato_sk": c_sk,
            "equipo_sk": m_sk,
            "periodo_operativo_sort": 202609,
            "meta_metraje_m": round(grp["metraje_guardia_m"].sum() * 1.15, 2),
            "horas_programadas_mes": 720.0
        })
    fact_metas_mensuales = pd.DataFrame(metas_rows)

    # -------------------------------------------------------------------------
    # EXPORTACIÓN MASIVA (PARQUET, CSV Y EXCEL)
    # -------------------------------------------------------------------------
    tablas_modelo = {
        "dim_tiempo_calendario": dim_tiempo_calendario,
        "dim_contrato_minero": dim_contrato_minero,
        "dim_equipo_perforadora": dim_equipo_perforadora,
        "dim_linea_diametro": dim_linea_diametro,
        "dim_personal": dim_personal,
        "dim_sondaje_taladro": dim_sondaje_taladro,
        "dim_taxonomia_actividad": dim_taxonomia_actividad,
        "fact_perforacion_avance": fact_perforacion_avance,
        "fact_horas_operativas": fact_horas_operativas,
        "brg_cuadrilla_guardia": brg_cuadrilla_guardia,
        "fact_metas_mensuales": fact_metas_mensuales
    }

    print("\n  [EXPORTANDO TABLAS DIMENSIONALES]...", flush=True)
    excel_path = output_dir / "ESQUEMA_ESTRELLA_COMPLETO.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for nombre_tbl, df_tbl in tablas_modelo.items():
            # CSV
            csv_path = output_dir / f"{nombre_tbl}.csv"
            df_tbl.to_csv(csv_path, index=False, encoding="utf-8")
            # Parquet
            parquet_path = output_dir / f"{nombre_tbl}.parquet"
            df_tbl.to_parquet(parquet_path, index=False)
            # Hoja Excel
            df_tbl.to_excel(writer, sheet_name=nombre_tbl[:31], index=False)
            print(f"    [OK] {nombre_tbl:<25} : {len(df_tbl):>6d} filas x {len(df_tbl.columns):>2d} cols -> .csv, .parquet", flush=True)

    total_metraje_fact = fact_perforacion_avance["metraje_guardia_m"].sum()
    print("=" * 80, flush=True)
    print("  [OK MODELADO DIMENSIONAL] Completado exitosamente:", flush=True)
    print(f"   Directorio: {output_dir}", flush=True)
    print(f"   Metraje Total en fact_perforacion_avance: {total_metraje_fact:.2f} m", flush=True)
    print("=" * 80, flush=True)

    return tablas_modelo
