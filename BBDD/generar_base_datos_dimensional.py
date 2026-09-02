"""
================================================================================
ROCKDRILL GROUP - PIPELINE DE BASE DE DATOS DIMENSIONAL (MODELO ESTRELLA KIMBALL)
================================================================================
Propósito:
  Transforma la base de datos oficial consolidada por Power Query:
  'CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx' (176 columnas) en un
  Esquema Estrella Dimensional Kimball (Data Warehouse) de alto rendimiento.
  Genera 7 Dimensiones, 3 Tablas de Hechos y 1 Tabla Puente en formatos CSV, Parquet y Excel.

Autor: Squad de Datos y Business Intelligence - Rockdrill Group
Fecha: Septiembre 2026
================================================================================
"""

import os
import sys
import time
from pathlib import Path
import warnings
import unicodedata
import pandas as pd
import numpy as np

# Suprimir avisos de fragmentación de Pandas en DataFrames anchos (176 columnas)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

def strip_accents(text):
    """Normaliza texto eliminando tildes y diacríticos."""
    if pd.isna(text):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(text)) if unicodedata.category(c) != 'Mn')

# Soporte de codificación segura para Windows Console (PowerShell / CMD)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# =============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES DEL SISTEMA (MODIFICAR SEGÚN EL ENTORNO)
# =============================================================================
# 1. RUTA OFICIAL DEL ARCHIVO CONSOLIDADOR POWERQUERY:
#    Este es el archivo consolidado oficial generado por Power Query con las 176 columnas.
#
#    -> RUTA EN DISCO LOCAL (Actual):
#    RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
#
#    -> RUTA EN LA NUBE / ONEDRIVE (Para ejecutar sincronizado en OneDrive del trabajo):
#    Reemplace 'TU_USUARIO' por su usuario de Windows o la ruta exacta donde sincroniza su OneDrive:
#    RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Users\TU_USUARIO\OneDrive - Rockdrill Group\...\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
RUTA_CARPETA_OPERACIONES    = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones"

# 2. RUTA DEL ARCHIVO MAESTRO DE METAS MENSUALES:
#    Archivo maestro de planeamiento con las metas mensuales por contrato y máquina:
#    Columnas: CTR, MES OPERATIVO, MAQUINA, TIPO_MAQUINA, META METRAJE.
#    -> RUTA LOCAL:
#    RUTA_ARCHIVO_METAS = r"C:\Proyectos Python\Detallados\METAS.xlsx"
#    -> RUTA EN LA NUBE / ONEDRIVE:
#    RUTA_ARCHIVO_METAS = r"C:\Users\TU_USUARIO\OneDrive - Rockdrill Group\...\METAS.xlsx"
RUTA_ARCHIVO_METAS          = r"C:\Proyectos Python\Detallados\METAS.xlsx"

# 3. RUTA DE DESTINO PARA LA BASE DE DATOS DIMENSIONAL (Esquema Estrella):
#    Por defecto se guarda de manera dinámica en la subcarpeta 'output_star_schema' dentro del
#    directorio donde resida este script (así funciona idéntico en Local y en OneDrive sin cambios):
DIRECTORIO_BBDD             = Path(__file__).resolve().parent
RUTA_DESTINO_BBDD           = str(DIRECTORIO_BBDD / "output_star_schema")

# 4. FORMATOS DE EXPORTACIÓN (Activar con True o desactivar con False):
GENERAR_ARCHIVOS_CSV        = True
GENERAR_ARCHIVOS_PARQUET    = True
GENERAR_EXCEL_MAESTRO      = True

# 5. HOJAS DE LECTURA DENTRO DE LOS ARCHIVOS EXCEL:
HOJA_CONSOLIDADA_EXCEL      = "Consolidado_Operaciones"
HOJA_METAS_EXCEL            = "Hoja1"
# =============================================================================


# =============================================================================
# TAXONOMÍA OFICIAL DE ACTIVIDADES (116 Tiempos en 5 Categorías de Disponibilidad)
# =============================================================================
TAXONOMIA_ACTIVIDADES = [
    # 1. Tiempos Operativos Directos (Tiempo Efectivo - Operativo) [COBRABLE]
    ("Perforación", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("Rimado", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("Asentado / Retiro de revestimiento (Casing)", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),
    ("RePerforación", "Tiempos Operativos Directos", "Tiempo Efectivo - Operativo", True, False),

    # 2. Tiempos de Mantenimiento [NO COBRABLE, IMPACTA DISPONIBILIDAD MECÁNICA]
    ("Preventivo", "Tiempos de Mantenimiento", "Mantenimiento", False, True),
    ("Correctivo", "Tiempos de Mantenimiento", "Mantenimiento", False, True),

    # 3. Maniobras Operativas (Stand By Operativo) [COBRABLE]
    ("Lavado de sondaje", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Mezclado de lodos", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Manipulación de tuberías", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Acondicionamiento de sondaje", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Cambio de línea", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Recuperación de sondaje por problemas geologicos", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Recuperación de materiales y o maniobras por atrapamiento", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Maniobras por descarga y carga de tuberías (por problemas geologicos)", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Perforación en fallas y/o terrenos altamente fracturados", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Medición de Desviación", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Traslado entre cámaras de perforación", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Cambio de punto de perforacion", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Anclado de máquina de perforación", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Perforación de perno de anclaje", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Cementación de perno de anclaje y fraguado", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Cementado y fraguado de sondaje", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Obturación/Sellado de sondaje con packer", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Sellado de Sondaje", "Maniobras Operativas", "Stand By Operativo", True, False),
    ("Inyección de lechada de cemento", "Maniobras Operativas", "Stand By Operativo", True, False),

    # 4. Ensayos Geotécnicos (Stand By Operativo) [COBRABLE]
    ("Ensayo Lefranc", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Ensayo Lugeon", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Prueba SPT", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Prueba Shelby", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Pruebas Geotécnicas", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Prueba de nivel freático", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Ensayo Air Lift", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Ensayo Slug Test", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro Casagrande", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro de cuerda vibrante", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Instalación de inclinómetro", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Instalación de piezómetro multinivel", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Instrumentación, toma de presión de agua y caudal", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Prueba de lectura de inclinómetro", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("Toma de lecturas cuerda vibrante", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("SBO1", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("SBO2", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("SBO3", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("SBO4", "Ensayos Geotécnicos", "Stand By Operativo", True, False),
    ("SBO5", "Ensayos Geotécnicos", "Stand By Operativo", True, False),

    # 5. Soporte y Seguridad (Stand By Inoperativo) [NO COBRABLE]
    ("Desate de rocas", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Orden y limpieza", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Recojo de lama", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Poza de sedimentación", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Estandarización y Desestandarización", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Instalación de red de agua o drenaje", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Instalación / Desinstalación de maquina", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Traslado de accesorios", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Auditoría Interna", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Charla, reparto de guardia, llenado de herramientas y reportes", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Espera de repuestos mecánicos", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Espera de materiales e insumos de perforación", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Traslado de personal", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Refrigerio", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Falta de personal", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Paralización por fiestas", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("Pare RD/ seguridad", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI1", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI2", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI3", "Soporte y Seguridad", "Stand By Inoperativo", False, False),
    ("SBI4", "Soporte y Seguridad", "Stand By Inoperativo", False, False),

    # 6. Condiciones Cliente (Stand By Cliente) [COBRABLE]
    ("Voladura", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Falta de agua", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Falta de energía", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Falta de ventilación", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Falta de servicios", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera Orden Cliente", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de programa", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de cámara", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de sostenimiento", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de scoop", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de marcado de punto", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de Topografía", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de grúa", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera por puebas de permeabilidad y/o ensayos", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Auditoría externa/ Osinergmin", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Capacitación (Externa Cliente)", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Falta de habilitación de cámara o plataforma", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Espera de orden cliente", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Condiciones climáticas", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Inundación", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Paralización por estrés térmico o alta temperatura", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Parada por sismo/microsismo", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("Conflicto social", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("SBC1", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("SBC2", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("SBC3", "Condiciones Cliente", "Stand By Cliente", True, False),
    ("SBC4", "Condiciones Cliente", "Stand By Cliente", True, False)
]

HOMOLOGACIONES_MAQUINAS = {
    ("SAN CRISTOBAL", "ST01"): "DE710-001",
    ("SAN CRISTOBAL", "ST02"): "DE710-002",
    ("SAN CRISTOBAL", "DE710ST01"): "DE710-001",
    ("SAN CRISTOBAL", "DE710ST02"): "DE710-002",
    ("ANDAYCHAGUA", "ST01"): "LF90D ST-001",
    ("ANDAYCHAGUA", "ST02"): "LF90D ST-002",
    ("ANDAYCHAGUA", "LF90DST01"): "LF90D ST-001",
    ("ANDAYCHAGUA", "LF90DST02"): "LF90D ST-002",
    ("TICLIO", "ST01"): "DE710-001",
    ("TICLIO", "DE710ST01"): "DE710-001",
    ("CTR_SAN CRISTOBAL", "ST01"): "DE710-001",
    ("CTR_SAN CRISTOBAL", "ST02"): "DE710-002",
    ("CTR_ANDAYCHAGUA", "ST01"): "LF90D ST-001",
    ("CTR_ANDAYCHAGUA", "ST02"): "LF90D ST-002",
    ("CTR_TICLIO", "ST01"): "DE710-001"
}


def clean_number(val):
    """Limpia cadenas o valores numéricos eliminando caracteres no válidos."""
    if pd.isna(val) or val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val) if not np.isnan(val) else None
    s = str(val).strip().replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def resolver_ruta_consolidador():
    """Localiza automáticamente el archivo CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx."""
    directorio_script = Path(__file__).resolve().parent
    
    rutas_a_probar = [
        Path(RUTA_CONSOLIDADOR_POWERQUERY),
        Path(RUTA_CARPETA_OPERACIONES) / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        directorio_script / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        directorio_script.parent / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        directorio_script.parent / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        directorio_script.parent / "Rockdrill_Control_Operaciones" / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        directorio_script.parent.parent / "Estructura base" / "Rockdrill_Control_Operaciones" / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        Path.home() / "OneDrive - ROCK DRILL" / "Archivos de Pedro Gamarra - CONTROL DE PROYECTOS" / "12. DASHBOARD" / "Rockdrill_Control_Operaciones" / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
        Path.home() / "OneDrive - ROCK DRILL" / "Archivos de Pedro Gamarra - CONTROL DE PROYECTOS" / "12. DASHBOARD" / "Base de datos" / "CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
    ]

    for p in rutas_a_probar:
        if p.exists() and p.is_file():
            return p

    # Búsqueda recursiva hacia arriba en carpetas padre
    curr = directorio_script
    for _ in range(4):
        candidatos = list(curr.glob("**/CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"))
        if candidatos:
            return candidatos[0]
        curr = curr.parent

    raise FileNotFoundError(
        f"\n[ERROR] No se encontro el archivo 'CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx'.\n"
        f"Verifique la variable RUTA_CONSOLIDADOR_POWERQUERY en este script.\n"
        f"Ruta configurada: {RUTA_CONSOLIDADOR_POWERQUERY}"
    )


def cargar_datos_consolidador():
    """Carga el DataFrame de operaciones desde CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx."""
    path_excel = resolver_ruta_consolidador()
    print(f"  [ORIGEN] Leyendo base oficial: {path_excel.resolve()}")
    df = pd.read_excel(path_excel, sheet_name=HOJA_CONSOLIDADA_EXCEL)
    print(f"  [ORIGEN] Filas cargadas: {len(df):,}, Columnas: {len(df.columns)}")
    return df.copy()


def resolver_ruta_metas():
    """Localiza automáticamente el archivo METAS.xlsx."""
    directorio_script = Path(__file__).resolve().parent
    rutas_a_probar = [
        Path(RUTA_ARCHIVO_METAS),
        directorio_script / "METAS.xlsx",
        directorio_script.parent / "METAS.xlsx",
        directorio_script.parent.parent / "METAS.xlsx",
        Path(RUTA_CARPETA_OPERACIONES) / "Base de datos" / "METAS.xlsx",
        Path(RUTA_CARPETA_OPERACIONES) / "METAS.xlsx",
        Path.home() / "OneDrive - ROCK DRILL" / "Archivos de Pedro Gamarra - CONTROL DE PROYECTOS" / "12. DASHBOARD" / "METAS.xlsx",
        Path.home() / "OneDrive - ROCK DRILL" / "Archivos de Pedro Gamarra - CONTROL DE PROYECTOS" / "12. DASHBOARD" / "Dashboard_Nuevo" / "METAS.xlsx"
    ]
    for p in rutas_a_probar:
        if p.exists() and p.is_file():
            return p

    curr = directorio_script
    for _ in range(4):
        candidatos = list(curr.glob("**/METAS.xlsx"))
        if candidatos:
            return candidatos[0]
        curr = curr.parent
    return None


def cargar_datos_metas():
    """Carga el DataFrame de metas mensuales desde METAS.xlsx si existe."""
    path_metas = resolver_ruta_metas()
    if path_metas is None:
        print("  [METAS] Aviso: No se encontro archivo METAS.xlsx. Se generara fact_metas_mensuales vacia.")
        return None
    print(f"  [ORIGEN] Leyendo metas de planeamiento: {path_metas.resolve()}")
    try:
        df_m = pd.read_excel(path_metas, sheet_name=HOJA_METAS_EXCEL)
    except Exception:
        df_m = pd.read_excel(path_metas)
    print(f"  [ORIGEN] Metas cargadas: {len(df_m):,} registros")
    return df_m.copy()


def ejecutar_pipeline_dimensional():
    """Ejecuta la separación dimensional y exporta el modelo estrella."""
    t_inicio = time.time()
    print("\n" + "=" * 80)
    print("  [INICIO] GENERACION DE BASE DE DATOS DIMENSIONAL (KIMBALL STAR SCHEMA)")
    print("  [FUENTE] CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx (176 Columnas)")
    print("=" * 80)

    # 1. Cargar datos de entrada y desfragmentar
    df = cargar_datos_consolidador()
    df = df.copy()

    # 2. Normalización de atributos clave
    print("\n  [PRE-PROCESAMIENTO] Normalizando atributos y claves canónicas...")
    if "CTR" in df.columns:
        df["CTR_NORM"] = df["CTR"].apply(strip_accents).str.strip().str.upper()
    else:
        df["CTR_NORM"] = "CTR_GENERAL"

    def norm_fecha(v):
        if pd.isna(v): return None
        d = pd.to_datetime(v, errors='coerce')
        if pd.isna(d): return None
        return d.strftime('%Y-%m-%d')

    col_f = "FECHA" if "FECHA" in df.columns else ("FECHA_ISO" if "FECHA_ISO" in df.columns else "FECHA_RAW")
    df["FECHA_NORM"] = df[col_f].apply(norm_fecha)
    df = df[df["FECHA_NORM"].notna()].copy()

    # Cargar metas mensuales de planeamiento
    df_metas = cargar_datos_metas()
    if df_metas is not None and not df_metas.empty:
        col_m_ctr = "CTR" if "CTR" in df_metas.columns else df_metas.columns[0]
        col_m_mes = "MES OPERATIVO" if "MES OPERATIVO" in df_metas.columns else df_metas.columns[1]
        col_m_maq = "MAQUINA" if "MAQUINA" in df_metas.columns else df_metas.columns[2]
        col_m_tip = "TIPO_MAQUINA" if "TIPO_MAQUINA" in df_metas.columns else ("TIPO MAQUINA" if "TIPO MAQUINA" in df_metas.columns else None)
        col_m_met = "META METRAJE" if "META METRAJE" in df_metas.columns else ("META_METRAJE" if "META_METRAJE" in df_metas.columns else "META")

        df_metas["CTR_NORM"] = df_metas[col_m_ctr].apply(strip_accents).str.strip().str.upper()
        df_metas["MAQUINA_HOMOLOGADA"] = df_metas[col_m_maq].astype(str).str.strip().str.upper()
        df_metas["MES_DT"] = pd.to_datetime(df_metas[col_m_mes], errors='coerce')
        df_metas["TIPO_MAQUINA_NORM"] = df_metas[col_m_tip].astype(str).str.strip().str.upper() if col_m_tip else "MINA"
        df_metas["META_VAL"] = df_metas[col_m_met].apply(clean_number)

    # Turno
    if "TURNO_ESTANDAR" in df.columns:
        df["TURNO_NORM"] = df["TURNO_ESTANDAR"].astype(str).str.strip().str.upper()
    else:
        col_t = "TURNO (A=1;B=2)" if "TURNO (A=1;B=2)" in df.columns else "TURNO"
        df["TURNO_NORM"] = df[col_t].astype(str).str.strip().str.upper().map(lambda x: 'A' if x in ('A', '1') else 'B')

    # Máquina
    if "MAQUINA_HOMOLOGADA" in df.columns:
        df["MAQUINA_HOMOLOGADA"] = df["MAQUINA_HOMOLOGADA"].astype(str).str.strip().str.upper()
    else:
        col_m = "MAQUINA" if "MAQUINA" in df.columns else "SheetName"
        def hom_maq(r):
            c = r["CTR_NORM"]
            m = str(r[col_m]).strip().upper()
            return HOMOLOGACIONES_MAQUINAS.get((c, m), m)
        df["MAQUINA_HOMOLOGADA"] = df.apply(hom_maq, axis=1)

    # Clave Única Canónica
    if "ID_CLAVE_UNICA" in df.columns and df["ID_CLAVE_UNICA"].notna().all():
        df["ID_CLAVE_UNICA_CANONICA"] = df["ID_CLAVE_UNICA"].astype(str).str.strip()
    else:
        df["FECHA_KEY"] = df["FECHA_NORM"].str.replace("-", "", regex=False)
        df["ID_CLAVE_UNICA_CANONICA"] = df["FECHA_KEY"] + "-" + df["CTR_NORM"] + "-" + df["MAQUINA_HOMOLOGADA"] + "-" + df["TURNO_NORM"]

    # Sondaje
    col_s = "NOMBRE" if "NOMBRE" in df.columns else ("SONDAJE" if "SONDAJE" in df.columns else "SONDAJE_NORM")
    df["SONDAJE_NORM"] = df[col_s].fillna("SIN SONDAJE").astype(str).str.strip().str.upper()
    df.loc[df["SONDAJE_NORM"] == "", "SONDAJE_NORM"] = "SIN SONDAJE"

    # Línea
    col_l = "LINEA" if "LINEA" in df.columns else "DIAMETRO"
    df["LINEA_NORM"] = df[col_l].fillna("HQ").astype(str).str.strip().str.upper()
    df["LINEA_NORM"] = df["LINEA_NORM"].replace({
        "HQ-3": "HQ", "HQ3": "HQ", "NQ-3": "NQ", "NQ3": "NQ", "PQ-3": "PQ", "PQ3": "PQ", "HWT/HQ": "HQ", "NW": "NQ"
    })
    lineas_validas = {"PQ", "HQ", "NQ", "BQ", "HWT"}
    df.loc[~df["LINEA_NORM"].isin(lineas_validas), "LINEA_NORM"] = "HQ"

    # Perforista
    col_p = "PERFORISTA" if "PERFORISTA" in df.columns else ("NOMBRE_PERFORISTA" if "NOMBRE_PERFORISTA" in df.columns else None)
    df["PERFORISTA_NORM"] = df[col_p].fillna("NO ASIGNADO").astype(str).str.strip().str.upper() if col_p else "NO ASIGNADO"
    df.loc[df["PERFORISTA_NORM"] == "", "PERFORISTA_NORM"] = "NO ASIGNADO"

    # =========================================================================
    # 1. DIMENSIÓN: dim_tiempo_calendario
    # =========================================================================
    print("  [1/10] Generando dim_tiempo_calendario (Semanas Civiles y Operativas)...")
    min_date = pd.to_datetime(df["FECHA_NORM"].min())
    max_date = pd.to_datetime(df["FECHA_NORM"].max())
    start_cal = min(pd.to_datetime("2025-01-01"), min_date.replace(day=1))
    end_cal = max(pd.to_datetime("2026-12-31"), (max_date + pd.DateOffset(months=1)).replace(day=1) - pd.Timedelta(days=1))
    date_range = pd.date_range(start=start_cal, end=end_cal, freq='D')

    cal_rows = [{
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
        "semana_calendario_num": -1,
        "semana_calendario_label": "N/D",
        "semana_operativa_num": -1,
        "semana_operativa_label": "N/D",
        "es_cierre_operativo": False
    }]

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

        semana_cal_num = int(dt.isocalendar().week)
        semana_cal_label = f"Sem {semana_cal_num:02d} ({dt.year})"
        sem_op_num = int(((dia_ciclo - 1) // 7) + 1)
        sem_op_label = f"Semana Op {sem_op_num}" if sem_op_num <= 4 else "Semana Op 5 (Cierre)"

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
            "semana_calendario_num": semana_cal_num,
            "semana_calendario_label": semana_cal_label,
            "semana_operativa_num": sem_op_num,
            "semana_operativa_label": sem_op_label,
            "es_cierre_operativo": dt.day == 25
        })
    dim_tiempo_calendario = pd.DataFrame(cal_rows)

    # =========================================================================
    # 2. DIMENSIÓN: dim_contrato_minero
    # =========================================================================
    print("  [2/10] Generando dim_contrato_minero (tipo_operacion: SUBTERRANEA)...")
    ctrs_ops = set(df["CTR_NORM"].unique())
    ctrs_metas = set(df_metas["CTR_NORM"].unique()) if df_metas is not None else set()
    ctrs_unicos = sorted((ctrs_ops | ctrs_metas) - {"", "NAN", "NONE"})

    ctr_rows = [{
        "contrato_sk": -1,
        "contrato_cd": "NO_ASIGNADO",
        "nombre_contrato": "[CTR NO ASIGNADO]",
        "cliente_minero": "NO ESPECIFICADO",
        "zona_geografica": "CENTRO",
        "tipo_operacion": "SUBTERRANEA",
        "estado_vigencia": "ACTIVO"
    }]
    ctr_sk_map = {"NO_ASIGNADO": -1}
    for idx, ctr in enumerate(ctrs_unicos, start=1):
        codigo_ctr = f"CTR_{ctr}" if not ctr.startswith("CTR_") else ctr
        ctr_rows.append({
            "contrato_sk": idx,
            "contrato_cd": codigo_ctr,
            "nombre_contrato": f"CONTRATO {ctr.replace('CTR_', '')}",
            "cliente_minero": "CLIENTE MINERO TITULAR",
            "zona_geografica": "CENTRO" if any(k in ctr for k in ["ANDAYCHAGUA", "CHUNGAR", "TICLIO", "MOROCOCHA", "SAN CRISTOBAL", "YAULIYACU"]) else ("SUR" if any(k in ctr for k in ["INMACULADA", "TAMBOJASA"]) else "CENTRO"),
            "tipo_operacion": "SUBTERRANEA",
            "estado_vigencia": "ACTIVO"
        })
        ctr_sk_map[ctr] = idx
        ctr_sk_map[codigo_ctr] = idx
    dim_contrato_minero = pd.DataFrame(ctr_rows)

    # =========================================================================
    # 3. DIMENSIÓN: dim_equipo_perforadora
    # =========================================================================
    print("  [3/10] Generando dim_equipo_perforadora (tipo_servicio: SUPERFICIE / MINA)...")
    ops_pairs = {(r[0], r[1]) for r in df[["MAQUINA_HOMOLOGADA", "CTR_NORM"]].drop_duplicates().values}
    if df_metas is not None:
        metas_pairs = {(r[0], r[1]) for r in df_metas[["MAQUINA_HOMOLOGADA", "CTR_NORM"]].drop_duplicates().values}
        all_pairs = sorted(ops_pairs | metas_pairs, key=lambda x: (x[1], x[0]))
    else:
        all_pairs = sorted(ops_pairs, key=lambda x: (x[1], x[0]))

    maq_rows = [{
        "equipo_sk": -1,
        "equipo_cd": "NO_ASIGNADO",
        "codigo_sap": "SAP-000",
        "modelo_fabricante": "[EQUIPO NO ASIGNADO]",
        "fabricante": "ROCKDRILL",
        "tipo_servicio": "NO DEFINIDO",
        "tipo_energia": "ELECTRO-HIDRAULICA",
        "horas_dia_planeadas": 24,
        "contrato_sk_asignado": -1,
        "estado_operativo": "OPERATIVO"
    }]
    maq_sk_map = {("NO_ASIGNADO", -1): -1}
    for idx, (maq, ctr) in enumerate(all_pairs, start=1):
        c_sk = ctr_sk_map.get(ctr, -1)
        tipo_serv = "SUPERFICIE" if ("DE710" in maq or "LF90" in maq or "CT20" in maq or "CUCULI" in ctr) else "INTERIOR MINA"
        maq_rows.append({
            "equipo_sk": idx,
            "equipo_cd": maq,
            "codigo_sap": f"SAP-{maq}",
            "modelo_fabricante": maq,
            "fabricante": "ROCKDRILL",
            "tipo_servicio": tipo_serv,
            "tipo_energia": "DIESEL" if "DE710" in maq or "LF90" in maq or "CT20" in maq else "ELECTRO-HIDRAULICA",
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
    print("  [4/10] Generando dim_linea_diametro...")
    lineas_unicas = sorted(df["LINEA_NORM"].unique())
    linea_rows = [{
        "linea_sk": -1,
        "linea_cd": "NO_DEFINIDO",
        "descripcion": "[LÍNEA NO DEFINIDA]",
        "diametro_corona_mm": 0.0,
        "diametro_testigo_mm": 0.0
    }]
    specs_linea = {
        "PQ": (122.6, 85.0),
        "HQ": (96.0, 63.5),
        "NQ": (75.7, 47.6),
        "BQ": (60.0, 36.4),
        "HWT": (114.3, 101.6)
    }
    linea_sk_map = {"NO_DEFINIDO": -1}
    for idx, lin in enumerate(lineas_unicas, start=1):
        c_mm, t_mm = specs_linea.get(lin, (0.0, 0.0))
        linea_rows.append({
            "linea_sk": idx,
            "linea_cd": lin,
            "descripcion": f"Línea de perforación {lin}",
            "diametro_corona_mm": c_mm,
            "diametro_testigo_mm": t_mm
        })
        linea_sk_map[lin] = idx
    dim_linea_diametro = pd.DataFrame(linea_rows)

    # =========================================================================
    # 5. DIMENSIÓN: dim_personal
    # =========================================================================
    print("  [5/10] Generando dim_personal...")
    perforistas = set(df["PERFORISTA_NORM"].dropna().unique())
    ayudantes_1 = set(df["AYUDANTE"].dropna().astype(str).str.strip().str.upper().unique()) if "AYUDANTE" in df.columns else set()
    ayudantes_2 = set(df["AYUDANTE_1"].dropna().astype(str).str.strip().str.upper().unique()) if "AYUDANTE_1" in df.columns else set()
    todos_personal = sorted(list((perforistas | ayudantes_1 | ayudantes_2) - {"", "NAN", "NONE"}))

    personal_rows = [{
        "personal_sk": -1,
        "personal_cd": "NO_ASIGNADO",
        "dni_carnet": "00000000",
        "nombre_completo": "[PERSONAL NO ASIGNADO]",
        "rol_estandarizado": "NO DEFINIDO",
        "contratista_propio": "ROCKDRILL",
        "estado_personal": "ACTIVO"
    }]
    personal_sk_map = {"NO_ASIGNADO": -1}
    for idx, nom in enumerate(todos_personal, start=1):
        rol = "PERFORISTA" if nom in perforistas else "AYUDANTE DE PERFORACION"
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
    # 6. DIMENSIÓN: dim_sondaje_taladro (Con Parámetros Geológicos de Diseño)
    # =========================================================================
    print("  [6/10] Generando dim_sondaje_taladro (Metas Geológicas, Línea e Inclinación)...")
    col_prof = "PROFUNDIDAD" if "PROFUNDIDAD" in df.columns else None
    col_inc = next((c for c in df.columns if "INCLINAC" in str(c).upper()), None)

    sondaje_rows = [{
        "sondaje_sk": -1,
        "sondaje_cd": "NO_ASIGNADO",
        "contrato_sk": -1,
        "sondaje_padre_sk": -1,
        "profundidad_programada_m": 0.0,
        "linea_programada": "NO ESPECIFICADO",
        "inclinacion_grados": 0.0,
        "tipo_taladro": "ORIGINAL"
    }]
    sondaje_sk_map = {("NO_ASIGNADO", -1): -1}

    sond_groups = df.groupby(["SONDAJE_NORM", "CTR_NORM"])
    for idx, ((sond, ctr), grp) in enumerate(sond_groups, start=1):
        c_sk = ctr_sk_map.get(ctr, -1)
        es_ramal = sond.endswith("A") or sond.endswith("B") or sond.endswith("R")

        prof_val = 0.0
        if col_prof and grp[col_prof].notna().any():
            prof_val = clean_number(grp[col_prof].dropna().iloc[0]) or 0.0

        linea_val = grp["LINEA_NORM"].dropna().iloc[0] if grp["LINEA_NORM"].notna().any() else "HQ"

        inc_val = -90.0
        if col_inc and grp[col_inc].notna().any():
            inc_val = clean_number(grp[col_inc].dropna().iloc[0]) or -90.0

        sondaje_rows.append({
            "sondaje_sk": idx,
            "sondaje_cd": sond,
            "contrato_sk": c_sk,
            "sondaje_padre_sk": -1,
            "profundidad_programada_m": round(prof_val, 2),
            "linea_programada": str(linea_val).strip().upper(),
            "inclinacion_grados": round(inc_val, 2),
            "tipo_taladro": "RAMAL_PARALELO" if es_ramal else "ORIGINAL"
        })
        sondaje_sk_map[(sond, c_sk)] = idx
        sondaje_sk_map[sond] = idx
    dim_sondaje_taladro = pd.DataFrame(sondaje_rows)

    # =========================================================================
    # 7. DIMENSIÓN: dim_taxonomia_actividad
    # =========================================================================
    print("  [7/10] Generando dim_taxonomia_actividad (5 Categorías de Disponibilidad)...")
    actividad_rows = [{
        "actividad_sk": -1,
        "nombre_actividad": "[ACTIVIDAD NO CATALOGADA]",
        "bloque_funcional": "NO CATALOGADO",
        "categoria_disponibilidad": "Stand By Inoperativo",
        "es_cobrable_estandar": False,
        "impacta_disp_mecanica": False
    }]
    actividad_sk_map = {}
    for idx, (nombre, bloque, categ, cobrable, disp_mec) in enumerate(TAXONOMIA_ACTIVIDADES, start=1):
        actividad_rows.append({
            "actividad_sk": idx,
            "nombre_actividad": nombre,
            "bloque_funcional": bloque,
            "categoria_disponibilidad": categ,
            "es_cobrable_estandar": cobrable,
            "impacta_disp_mecanica": disp_mec
        })
        actividad_sk_map[nombre] = idx
    dim_taxonomia_actividad = pd.DataFrame(actividad_rows)

    # =========================================================================
    # 8. TABLA DE HECHOS: fact_perforacion_avance
    # =========================================================================
    print("  [8/10] Generando fact_perforacion_avance (Avance, n_broca, Casing, Motor)...")
    avance_rows = []
    col_met = "METRAJE" if "METRAJE" in df.columns else "METRAJE_PERFORADO"
    col_desde = "DESDE" if "DESDE" in df.columns else "DESDE_M"
    col_hasta = "HASTA" if "HASTA" in df.columns else "HASTA_M"

    col_marca_broca = next((c for c in df.columns if str(c).strip().upper() == "MARCA"), None)
    col_serie_broca = next((c for c in df.columns if str(c).strip().upper() == "SERIE"), None)
    col_n_broca = next((c for c in df.columns if "BROCA" in str(c).upper() and any(k in str(c).upper() for k in ["N", "NUM", "N°", "Nº", "CORRELATIVO"])), None)
    col_estado_broca = next((c for c in df.columns if "ESTADO" in str(c).upper() and "BROCA" in str(c).upper()), None)

    col_marca_escar = next((c for c in df.columns if str(c).strip().upper() in ["MARCA_1", "MARCA ESCARIADOR"]), None)
    col_n_escar = next((c for c in df.columns if "ESCARIADOR" in str(c).upper() and any(k in str(c).upper() for k in ["N", "NUM", "N°", "Nº", "CORRELATIVO"])), None)
    col_estado_escar = next((c for c in df.columns if "ESTADO" in str(c).upper() and "ESCARIADOR" in str(c).upper()), None)

    col_casing_met = next((c for c in df.columns if "CASING" in str(c).upper() and "METRAJE" in str(c).upper()), None)
    col_reperfo_met = next((c for c in df.columns if any(k in str(c).upper() for k in ["REPERF", "RE-PERF"]) and "METRAJE" in str(c).upper()), None)
    col_horom_delta = next((c for c in df.columns if "HOROMETRO" in str(c).upper() and "TOTAL" in str(c).upper()), None)
    col_petroleo = next((c for c in df.columns if "PETROLEO" in str(c).upper() and "GLN" in str(c).upper()), None)
    col_litologia = next((c for c in df.columns if "LITOL" in str(c).upper()), None)
    col_comentarios = next((c for c in df.columns if "COMENTARIOS" in str(c).upper()), None)

    records = df.to_dict('records')

    for row in records:
        f_dt = row.get("FECHA_NORM")
        cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
        c_sk = ctr_sk_map.get(row.get("CTR_NORM"), -1)
        m_sk = maq_sk_map.get((row.get("MAQUINA_HOMOLOGADA"), c_sk), maq_sk_map.get(row.get("MAQUINA_HOMOLOGADA"), -1))
        s_sk = sondaje_sk_map.get((row.get("SONDAJE_NORM"), c_sk), sondaje_sk_map.get(row.get("SONDAJE_NORM"), -1))
        l_sk = linea_sk_map.get(row.get("LINEA_NORM"), -1)
        p_sk = personal_sk_map.get(row.get("PERFORISTA_NORM"), -1)

        metraje = clean_number(row.get(col_met)) or 0.0
        desde = clean_number(row.get(col_desde)) or 0.0
        hasta = clean_number(row.get(col_hasta)) or 0.0

        n_broca_val = clean_number(row.get(col_n_broca)) if col_n_broca else None
        n_broca_str = f"{int(n_broca_val)}" if (n_broca_val is not None and not pd.isna(n_broca_val)) else "SIN_NUMERO"

        n_escar_val = clean_number(row.get(col_n_escar)) if col_n_escar else None
        n_escar_str = f"{int(n_escar_val)}" if (n_escar_val is not None and not pd.isna(n_escar_val)) else "SIN_NUMERO"

        casing_m = clean_number(row.get(col_casing_met)) or 0.0
        reperfo_m = clean_number(row.get(col_reperfo_met)) or 0.0
        horom_d = clean_number(row.get(col_horom_delta)) or 0.0
        petro_g = clean_number(row.get(col_petroleo)) or 0.0

        avance_rows.append({
            "avance_id": len(avance_rows) + 1,
            "calendario_sk": cal_sk,
            "contrato_sk": c_sk,
            "equipo_sk": m_sk,
            "sondaje_sk": s_sk,
            "perforista_sk": p_sk,
            "linea_sk": l_sk,
            "turno_guardia": row.get("TURNO_NORM"),
            "desde_m": round(desde, 2),
            "hasta_m": round(hasta, 2),
            "metraje_guardia_m": round(metraje, 2),
            "marca_broca": str(row.get(col_marca_broca) or "NO REGISTRADO").strip().upper() if col_marca_broca else "NO REGISTRADO",
            "serie_broca": str(row.get(col_serie_broca) or "NO REGISTRADO").strip().upper() if col_serie_broca else "NO REGISTRADO",
            "n_broca": n_broca_str,
            "estado_broca": str(row.get(col_estado_broca) or "NO REGISTRADO").strip().upper() if col_estado_broca else "NO REGISTRADO",
            "marca_escariador": str(row.get(col_marca_escar) or "NO REGISTRADO").strip().upper() if col_marca_escar else "NO REGISTRADO",
            "n_escariador": n_escar_str,
            "estado_escariador": str(row.get(col_estado_escar) or "NO REGISTRADO").strip().upper() if col_estado_escar else "NO REGISTRADO",
            "casing_metraje_m": round(casing_m, 2),
            "reperfo_metraje_m": round(reperfo_m, 2),
            "horometro_delta": round(horom_d, 2),
            "petroleo_gln": round(petro_g, 2),
            "descripcion_litologica": str(row.get(col_litologia) or "").strip(),
            "comentarios_guardia": str(row.get(col_comentarios) or "").strip(),
            "es_reperforacion": reperfo_m > 0.0,
            "id_clave_unica": row.get("ID_CLAVE_UNICA_CANONICA")
        })
    fact_perforacion_avance = pd.DataFrame(avance_rows)

    # =========================================================================
    # 9. TABLA DE HECHOS: fact_horas_operativas (Unpivoting de 116 Tiempos)
    # =========================================================================
    print("  [9/10] Generando fact_horas_operativas (Unpivoting filtrado a horas > 0)...")
    horas_rows = []
    taxonomia_activa = []
    for act_nom, act_bloque, act_categ, act_cobrable, act_disp_mec in TAXONOMIA_ACTIVIDADES:
        col_match = None
        for c in df.columns:
            if c.strip().lower() == act_nom.strip().lower():
                col_match = c
                break
        if col_match:
            a_sk = actividad_sk_map.get(act_nom, -1)
            taxonomia_activa.append((col_match, a_sk, act_nom, act_categ, act_cobrable))

    for row in records:
        f_dt = row.get("FECHA_NORM")
        cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
        c_sk = ctr_sk_map.get(row.get("CTR_NORM"), -1)
        m_sk = maq_sk_map.get((row.get("MAQUINA_HOMOLOGADA"), c_sk), maq_sk_map.get(row.get("MAQUINA_HOMOLOGADA"), -1))
        t_guardia = row.get("TURNO_NORM")
        clave_u = row.get("ID_CLAVE_UNICA_CANONICA")

        for col_name, a_sk, act_nom, act_categ, act_cobrable in taxonomia_activa:
            raw_val = row.get(col_name)
            h_val = clean_number(raw_val)
            if h_val and h_val > 0.0:
                horas_rows.append({
                    "hora_evento_id": len(horas_rows) + 1,
                    "calendario_sk": cal_sk,
                    "contrato_sk": c_sk,
                    "equipo_sk": m_sk,
                    "actividad_sk": a_sk,
                    "turno_guardia": t_guardia,
                    "horas_reportadas": round(h_val, 2),
                    "es_cobrable": act_cobrable,
                    "categoria_disponibilidad": act_categ,
                    "id_clave_unica": clave_u
                })
    fact_horas_operativas = pd.DataFrame(horas_rows)

    # =========================================================================
    # 10. TABLA PUENTE: brg_cuadrilla_guardia Y HECHOS: fact_metas_mensuales
    # =========================================================================
    print("  [10/10] Generando brg_cuadrilla_guardia y fact_metas_mensuales...")
    brg_rows = []
    col_he = "HORAS EXTRAS" if "HORAS EXTRAS" in df.columns else "HORAS_EXTRAS"
    col_ay1 = "AYUDANTE" if "AYUDANTE" in df.columns else None
    col_ay2 = "AYUDANTE_1" if "AYUDANTE_1" in df.columns else None

    for row in records:
        f_dt = row.get("FECHA_NORM")
        cal_sk = int(f_dt.replace("-", "")) if f_dt else -1
        c_sk = ctr_sk_map.get(row.get("CTR_NORM"), -1)
        m_sk = maq_sk_map.get((row.get("MAQUINA_HOMOLOGADA"), c_sk), maq_sk_map.get(row.get("MAQUINA_HOMOLOGADA"), -1))
        he_val = clean_number(row.get(col_he)) or 0.0
        clave_u = row.get("ID_CLAVE_UNICA_CANONICA")

        # Perforista
        perf_nom = row.get("PERFORISTA_NORM")
        p_sk = personal_sk_map.get(perf_nom, -1)
        brg_rows.append({
            "asignacion_id": len(brg_rows) + 1,
            "calendario_sk": cal_sk,
            "equipo_sk": m_sk,
            "personal_sk": p_sk,
            "rol_desempenado": "PERFORISTA",
            "horas_laboradas": 12.0,
            "horas_extras": round(he_val, 2),
            "id_clave_unica": clave_u
        })

        # Ayudante 1
        if col_ay1 and row.get(col_ay1):
            ay1_nom = str(row.get(col_ay1)).strip().upper()
            if ay1_nom and ay1_nom != "NAN":
                ay1_sk = personal_sk_map.get(ay1_nom, -1)
                brg_rows.append({
                    "asignacion_id": len(brg_rows) + 1,
                    "calendario_sk": cal_sk,
                    "equipo_sk": m_sk,
                    "personal_sk": ay1_sk,
                    "rol_desempenado": "AYUDANTE DE PERFORACION",
                    "horas_laboradas": 12.0,
                    "horas_extras": round(he_val, 2),
                    "id_clave_unica": clave_u
                })

        # Ayudante 2
        if col_ay2 and row.get(col_ay2):
            ay2_nom = str(row.get(col_ay2)).strip().upper()
            if ay2_nom and ay2_nom != "NAN":
                ay2_sk = personal_sk_map.get(ay2_nom, -1)
                brg_rows.append({
                    "asignacion_id": len(brg_rows) + 1,
                    "calendario_sk": cal_sk,
                    "equipo_sk": m_sk,
                    "personal_sk": ay2_sk,
                    "rol_desempenado": "AYUDANTE DE PERFORACION",
                    "horas_laboradas": 12.0,
                    "horas_extras": round(he_val, 2),
                    "id_clave_unica": clave_u
                })
    brg_cuadrilla_guardia = pd.DataFrame(brg_rows)

    # =========================================================================
    # 10. TABLA DE HECHOS: fact_metas_mensuales (Alimentada desde METAS.xlsx)
    # =========================================================================
    print("  [10/10] Generando fact_metas_mensuales (desde METAS.xlsx)...")
    meta_rows = []
    if df_metas is not None and not df_metas.empty:
        for idx, row in enumerate(df_metas.to_dict(orient="records"), start=1):
            dt = pd.to_datetime(row.get("MES_DT") or row.get("MES OPERATIVO"), errors="coerce")
            if pd.isna(dt):
                continue
            cal_sk = int(dt.strftime("%Y%m%d"))
            periodo_sort = int(dt.year * 100 + dt.month)
            ctr_norm = row.get("CTR_NORM")
            maq_norm = row.get("MAQUINA_HOMOLOGADA")
            c_sk = ctr_sk_map.get(ctr_norm, -1)
            m_sk = maq_sk_map.get((maq_norm, c_sk), maq_sk_map.get(maq_norm, -1))
            t_maq = str(row.get("TIPO_MAQUINA_NORM") or row.get("TIPO_MAQUINA") or "MINA").strip().upper()
            meta_m = clean_number(row.get("META_VAL") or row.get("META METRAJE")) or 0.0

            meta_rows.append({
                "meta_id": idx,
                "calendario_sk": cal_sk,
                "periodo_operativo_sort": periodo_sort,
                "mes_operativo_dt": dt.strftime("%Y-%m-%d"),
                "contrato_sk": c_sk,
                "equipo_sk": m_sk,
                "tipo_maquina": t_maq,
                "meta_metraje_m": round(meta_m, 2),
                "proyectado_m": 0.0
            })
    fact_metas_mensuales = pd.DataFrame(meta_rows)

    # =========================================================================
    # EXPORTACIÓN DE RESULTADOS
    # =========================================================================
    out_dir = Path(RUTA_DESTINO_BBDD)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n  [EXPORTACIÓN] Guardando tablas en: {out_dir.resolve()}")

    tablas = {
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

    for name, t_df in tablas.items():
        if GENERAR_ARCHIVOS_CSV:
            t_df.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
        if GENERAR_ARCHIVOS_PARQUET:
            t_df.to_parquet(out_dir / f"{name}.parquet", index=False)
        print(f"    [OK] {name:<26}: {len(t_df):>6} filas x {len(t_df.columns):>2} cols")

    if GENERAR_EXCEL_MAESTRO:
        excel_path = out_dir / "ESQUEMA_ESTRELLA_COMPLETO.xlsx"
        print(f"\n  [EXCEL] Generando libro maestro consolidado: {excel_path.name}...")
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for name, t_df in tablas.items():
                sheet_name = name[:31]
                t_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"    [OK] Excel maestro generado exitosamente ({excel_path.stat().st_size / (1024*1024):.2f} MB)")

    # Auditoría cuantitativa
    total_metraje = fact_perforacion_avance["metraje_guardia_m"].sum()
    t_total = time.time() - t_inicio

    print("\n" + "=" * 80)
    print("  [OK] MODELADO DIMENSIONAL FINALIZADO EXITOSAMENTE")
    print(f"  [TIEMPO] Tiempo de ejecucion: {t_total:.2f} segundos")
    print(f"  [METRAJE] Metraje Total en fact_perforacion_avance: {total_metraje:.2f} m")
    print(f"  [SALIDA] Ubicacion de salida: {out_dir.resolve()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    ejecutar_pipeline_dimensional()
