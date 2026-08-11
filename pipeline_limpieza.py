"""
Pipeline de Limpieza Completo - Detallados Rockdrill
====================================================
Módulo principal de ETL y Consolidación de Reportes Detallados de Avance.

Cumple con las mejores prácticas de ingeniería de datos:
1. Replicación exacta del mapeo dual-row Power Query M (Table.Skip([Data], 22)).
2. Slicing raw_rows[:200] para bypass seguro de hojas corruptas de 1 millón de filas.
3. Estandarización estricta de turnos en 'A' (Día) y 'B' (Noche).
4. Generación de clave única de trazabilidad por turno: ID_CLAVE_UNICA = {FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}.
5. Validaciones de seguridad de rangos numéricos y estructura (Metrajes, Horas, Profundidades).
6. Estandarización de Máquinas según la matriz de Excepciones del Maestro de Máquinas SAP.
7. Exclusión explícita de CTR COLQUIJIRCA (no maneja control de metrajes en este sistema).
"""

import os
import re
import sys
import unicodedata
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Union, Dict, List, Tuple
from dateutil.relativedelta import relativedelta

import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook

def get_visible_sheet_names(excel_path: Path) -> set[str]:
    """
    Extrae los nombres de hojas VISIBLES de un archivo Excel .xlsx usando zipfile y XML.
    Ignora hojas ocultas (hidden / veryHidden) replicando el filtro de Power Query (sheet.visible / Hidden = false).
    """
    visible_sheets = set()
    try:
        with zipfile.ZipFile(excel_path, 'r') as z:
            if 'xl/workbook.xml' not in z.namelist():
                return set()
            with z.open('xl/workbook.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheets_node = root.find('main:sheets', ns)
                if sheets_node is None:
                    for elem in root.iter():
                        if elem.tag.endswith('sheet'):
                            name = elem.attrib.get('name')
                            state = elem.attrib.get('state', 'visible')
                            if name and state not in ('hidden', 'veryHidden'):
                                visible_sheets.add(name)
                else:
                    for sheet in sheets_node.findall('main:sheet', ns):
                        name = sheet.attrib.get('name')
                        state = sheet.attrib.get('state', 'visible')
                        if name and state not in ('hidden', 'veryHidden'):
                            visible_sheets.add(name)
    except Exception:
        return set()
    return visible_sheets

# ============================================================
# CONFIGURACIÓN DE RUTAS Y CONSTANTES GLOBALES
# ============================================================

try:
    from config import BASE_PATH, MAESTRO_PATH, OUTPUT_PATH
except ImportError:
    BASE_PATH = Path(__file__).parent / "Estructura base" / "Rockdrill_Control_Operaciones"
    MAESTRO_PATH = BASE_PATH / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx"
    OUTPUT_PATH = Path(__file__).parent / "output"
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

HOJAS_EXCLUIDAS: set[str] = {"ADITIVOS", "GENERAL", "LISTAS", "Tiempos"}
CTRS_EXCLUIDOS: set[str] = {"COLQUIJIRCA"}  # Exclusión explícita según solicitud del usuario

MIN_ROWS: int = 24
SKIP_ROWS: int = 22  # 0-indexed: Fila 23 del Excel es el primer renglón de encabezados

ZONA_CENTRO: set[str] = {
    "AMERICANA", "CHUNGAR", "TICLIO", "MOROCOCHA", "YAULIYACU",
    "SAN CRISTOBAL", "ANDAYCHAGUA", "CERRO"
}

MESES_ES: List[str] = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
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

COLS_OFICIALES: List[str] = [
    "N°", "ZONA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "TURNO (A=1;B=2)", "GRUPO", "MES", "FECHA",
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
    "Instalación PVC", "RePerforación",
    "MANTTO. PREVENTIVO", "MANTTO. CORRECTIVO",
    "LAVADO DE SONDAJE", "MEZCLADO DE LODOS", "MANIPULACIÓN DE TUBERÍAS",
    "ACONDICIONAMIENTO DE SONDAJE", "CAMBIO DE LINEA", "RECUPERACIÓN DE SONDAJE",
    "TRASLADO ENTRE CÁMARAS DE PERFORACIÓN", "MANIOBRAS DE PROBLEMAS GEOLÓGICOS",
    "MEDICIÓN DE DESVIACIÓN", "PRUEBAS DE SUELO", "PERFORACIÓN DE PERNO DE ANCLAJE",
    "CEMENTACIÓN", "DESATE DE ROCAS", "ORDEN Y LIMPIEZA", "RECOJO DE LAMA",
    "POZA DE SEDIMENTACIÓN", "ESTANDARIZACIÓN",
    "INSTALACIÓN DE RED DE AGUA O DRENAJE", "INSTALACIÓN / DESINSTALACIÓN DE EQUIPOS",
    "TRASLADO DE ACCESORIOS", "AUDITORÍA INTERNA", "CAPACITACIÓN",
    "CAMBIO DE PUNTO", "TRASLADO DE MÁQUINA", "ESPERA DE REPUESTO",
    "TRASLADO DE PERSONAL", "REFRIGERIO", "Otros*",
    "VOLADURA", "FALTA DE AGUA", "FALTA DE ENERGÍA", "FALTA DE VENTILACIÓN",
    "FALTA DE SERVICIOS", "ESPERA DE PROGRAMA", "ESPERA DE CÁMARA",
    "ESPERA DE SOSTENIMIENTO", "ESPERA DE SCOOP", "ESPERA DE MARCADO DE PUNTO",
    "APOYO A GEOLOGÍA", "AUDITORÍA EXTERNA",
    "FALTA DE HABILITACIÓN DE CÁMARA O PLATAFORMA", "ESPERA DE ORDEN CLIENTE",
    "CONDICIONES CLIMATICAS", "OTROS*",
    "SI ES OTROS * INDICAR EL MOTIVO (BREVE EXPLICACION)",
    "TIEMPO TOTAL", "TIEMPO EFECTIVO - OPERATIVO", "LOST TIME",
    "TOTAL MANTTO.", "STAND BY OPERATIVO", "STAND BY INOPERATIVO", "STAND BY CLIENTE",
    "RIMADO HWT/HQ DESDE", "RIMADO HWT/HQ HASTA", "RIMADO HWT/HQ METRAJE", "RIMADO HWT/HQ TOTAL",
    "REPERFORACIÓN DESDE", "REPERFORACIÓN HASTA", "REPERFORACIÓN METRAJE", "REPERFORACIÓN TOTAL",
    "HOROMETRO DESDE", "HOROMETRO HASTA", "HOROMETRO ACUMULADO", "HOROMETRO TOTAL",
    "TRABAJOS REALIZADOS BITACORA DE MANTTO.", "REPUESTOS UTILIZADOS BITACORA DE MANTTO.",
    "DESCRIPCIÓN LITOLÓGICA", "COMENTARIOS",
    "HOJA DE TRABAJO ORIGEN", "ARCHIVO ORIGEN", "ID_CLAVE_UNICA"
]

COLS_NUMERICAS: List[str] = [
    "PROFUNDIDAD DE SONDAJE", "DESDE", "HASTA", "METRAJE", "HORAS EXTRAS",
    "TOTAL", "METROS ACUMULADO", "METROS PROYECTADO", "METROS META",
    "CANT. DE BENTONITA", "CANT. DE PAC", "CANT. DE POLIMERO",
    "CANT. DE LUBRICANTE", "CANT. DE INHIBIDOR", "CANT. DE ESTABILIZADOR",
    "CANT. DE OTROS", "CANT. DE PETROLEO", "GLN DE PETROLEO",
    "Perforación", "Rimado", "Asentado / Retiro DE REVESTIMIENTO (CASING)",
    "Instalación PVC", "RePerforación", "MANTTO. PREVENTIVO", "MANTTO. CORRECTIVO",
    "LAVADO DE SONDAJE", "MEZCLADO DE LODOS", "MANIPULACIÓN DE TUBERÍAS",
    "ACONDICIONAMIENTO DE SONDAJE", "CAMBIO DE LINEA", "RECUPERACIÓN DE SONDAJE",
    "TRASLADO ENTRE CÁMARAS DE PERFORACIÓN", "MANIOBRAS DE PROBLEMAS GEOLÓGICOS",
    "MEDICIÓN DE DESVIACIÓN", "PRUEBAS DE SUELO", "PERFORACIÓN DE PERNO DE ANCLAJE",
    "CEMENTACIÓN", "DESATE DE ROCAS", "ORDEN Y LIMPIEZA", "RECOJO DE LAMA",
    "POZA DE SEDIMENTACIÓN", "ESTANDARIZACIÓN",
    "INSTALACIÓN DE RED DE AGUA O DRENAJE", "INSTALACIÓN / DESINSTALACIÓN DE EQUIPOS",
    "TRASLADO DE ACCESORIOS", "AUDITORÍA INTERNA", "CAPACITACIÓN",
    "CAMBIO DE PUNTO", "TRASLADO DE MÁQUINA", "ESPERA DE REPUESTO",
    "TRASLADO DE PERSONAL", "REFRIGERIO", "Otros*",
    "VOLADURA", "FALTA DE AGUA", "FALTA DE ENERGÍA", "FALTA DE VENTILACIÓN",
    "FALTA DE SERVICIOS", "ESPERA DE PROGRAMA", "ESPERA DE CÁMARA",
    "ESPERA DE SOSTENIMIENTO", "ESPERA DE SCOOP", "ESPERA DE MARCADO DE PUNTO",
    "APOYO A GEOLOGÍA", "AUDITORÍA EXTERNA",
    "FALTA DE HABILITACIÓN DE CÁMARA O PLATAFORMA", "ESPERA DE ORDEN CLIENTE",
    "CONDICIONES CLIMATICAS", "OTROS*",
    "TIEMPO TOTAL", "TIEMPO EFECTIVO - OPERATIVO", "LOST TIME",
    "TOTAL MANTTO.", "STAND BY OPERATIVO", "STAND BY INOPERATIVO", "STAND BY CLIENTE",
    "RIMADO HWT/HQ DESDE", "RIMADO HWT/HQ HASTA", "RIMADO HWT/HQ METRAJE", "RIMADO HWT/HQ TOTAL",
    "REPERFORACIÓN DESDE", "REPERFORACIÓN HASTA", "REPERFORACIÓN METRAJE", "REPERFORACIÓN TOTAL",
    "HOROMETRO DESDE", "HOROMETRO HASTA", "HOROMETRO ACUMULADO", "HOROMETRO TOTAL",
]


# ============================================================
# FUNCIONES AUXILIARES DE NORMALIZACIÓN Y VALIDACIÓN DE SEGURIDAD
# ============================================================

def remove_accents(text: str) -> str:
    """
    Remueve marcas diacríticas y acentos de una cadena de texto.
    Ejemplo: 'CUCULÍ' -> 'CUCULI', 'MÁQUINA' -> 'MAQUINA'.
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    return ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))


def extract_ctr_from_folder(folder_name: str) -> str:
    """
    Extrae el nombre estandarizado del CTR desde el nombre de su carpeta raíz (CTR_XXXX).
    """
    ctr = folder_name.replace("CTR_", "").replace("_", " ").upper().strip()
    ctr = remove_accents(ctr)
    return ctr


def clean_number_value(val: Union[int, float, str, None, pd.Series, list]) -> Union[int, float, None]:
    """
    Limpia de forma robusta cualquier entrada numérica:
    - Elimina comillas ("), apostrofes ('), tildes (´`), espacios no rompibles (\\xa0).
    - Normaliza comas decimales (,) a puntos (.).
    - Desempaqueta objetos Series o listas en caso de duplicados en dataframe.
    - Retorna float o int si el número es entero exacto.
    """
    if val is None:
        return None
    
    if isinstance(val, (pd.Series, np.ndarray, list, tuple)):
        for v in val:
            res = clean_number_value(v)
            if res is not None:
                return res
        return None
    
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    
    if isinstance(val, (int, float)):
        return int(val) if float(val).is_integer() else float(val)
    
    s = str(val).strip()
    s = re.sub(r"^['\"`´’‘]+|['\"`´’‘]+$", "", s).strip()
    s = s.replace("\xa0", "").strip()
    
    if not s or s.lower() in ("nan", "null", "none", "falso", "verdadero", "false", "true", "-"):
        return None
    
    s = s.replace(",", ".")
    
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        match = re.search(r"[-+]?\d*\.?\d+", s)
        if match:
            try:
                f = float(match.group())
                return int(f) if f.is_integer() else f
            except ValueError:
                return None
        return None


def standardize_turno(row: pd.Series, row_seq_in_day: int = 1) -> str:
    """
    Estandariza los valores heterogéneos de turnos a 'A' (Día / Guardia 1) o 'B' (Noche / Guardia 2):
    - Turno '1', '1.0', 'A', 'D', 'DIA', 'G1' -> 'A'
    - Turno '2', '2.0', 'B', 'N', 'NOCHE', 'G2' -> 'B'
    - Para AMERICANA / CERRO con combinaciones B/C o Grupo 1/2:
      Si GRUPO == 1.0 -> 'A', Si GRUPO == 2.0 -> 'B'
    - Fallback: Si no hay información explícita, usa la secuencia de la máquina en el día (1->'A', 2->'B').
    """
    raw_t = str(row.get("TURNO (A=1;B=2)", "")).strip().upper() if pd.notna(row.get("TURNO (A=1;B=2)")) else ""
    raw_g = str(row.get("GRUPO", "")).strip().upper() if pd.notna(row.get("GRUPO")) else ""
    
    if raw_t in ("1", "1.0", "A", "D", "DIA", "G1"):
        return "A"
    if raw_t in ("2", "2.0", "N", "NOCHE", "G2"):
        return "B"
    
    if raw_g in ("1", "1.0"):
        return "A"
    if raw_g in ("2", "2.0"):
        return "B"
    
    if raw_t == "B" and raw_g in ("1", "1.0"):
        return "A"
    if raw_t == "C" and raw_g in ("2", "2.0"):
        return "B"
    
    return "A" if row_seq_in_day == 1 else "B"


def load_machine_exceptions(maestro_path: Path) -> Dict[Tuple[str, str], str]:
    """
    Carga la hoja 'Exepciones' de Maestros_Maquinas.xlsx y retorna un diccionario:
    (CTR_NORM, MÁQUINA_ERRÓNEA_NORM) -> MÁQUINA_OFICIAL_SAP
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
                        return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper().strip()) if not unicodedata.category(c).startswith('M'))
                    exceptions[(norm(r[0]), norm(r[1]))] = str(r[2]).strip()
    except Exception as e:
        print(f"  [WARN] No se pudo cargar la tabla de Excepciones: {e}", flush=True)
    
    return exceptions


def find_detallado_files(base_path: Path) -> List[Dict[str, Union[str, Path]]]:
    """
    Escanea la carpeta Estructura base para identificar los archivos Excel de reporte detallado,
    aplicando la exclusión explícita del CTR COLQUIJIRCA.
    """
    files = []
    for ctr_folder in sorted(base_path.iterdir()):
        if not ctr_folder.is_dir() or not ctr_folder.name.startswith("CTR_"):
            continue
        
        ctr = extract_ctr_from_folder(ctr_folder.name)
        
        # EXCLUSIÓN SEGURIDAD: Colquijirca no maneja control de metrajes en este proceso
        if ctr in CTRS_EXCLUIDOS:
            print(f"  [EXCLUIDO] {ctr}: Excluido explícitamente según criterios de negocio.", flush=True)
            continue
        
        detallado_folder = ctr_folder / "02_Detallado"
        search_folder = detallado_folder if detallado_folder.exists() else ctr_folder
        
        for xlsx_file in search_folder.glob("*.xlsx"):
            if xlsx_file.name.startswith("~$"):
                continue
            files.append({
                "ctr": ctr,
                "filepath": xlsx_file,
                "filename": xlsx_file.name,
                "folder": str(xlsx_file.parent),
            })
    return files


def is_operative_sheet_name(name: str) -> bool:
    """Valida si el nombre de la hoja corresponde a una máquina operativa."""
    if name in HOJAS_EXCLUIDAS:
        return False
    if re.match(r'^[Mm][AaÁá]quina\s*\d+$', name, re.IGNORECASE):
        return False
    if name in ("Hoja1", "Hoja3"):
        return False
    return True


def build_dual_row_headers_from_rows(rows: List[List], skip: int = SKIP_ROWS) -> Optional[List[str]]:
    """
    Construye los encabezados replicando fielmente la función M Table.Skip([Data], 22):
    - Fila index 22 (Fila 23 del Excel) = Encabezados primarios (AVANCE DIARIO, BROCA, etc.)
    - Fila index 23 (Fila 24 del Excel) = Sub-encabezados (DESDE, HASTA, METRAJE, etc.)
    - Forward-fill horizontal en la fila primaria.
    """
    row_primary_idx = skip
    row_sub_idx = skip + 1
    
    if len(rows) < row_sub_idx + 1:
        return None
    
    primary_values = rows[row_primary_idx]
    sub_values = rows[row_sub_idx]
    
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


def extract_sheet_data_from_rows(rows: List[List], headers: List[str], skip: int = SKIP_ROWS) -> Optional[pd.DataFrame]:
    """
    Extrae los datos tabulares comenzando desde la fila index 24 (Row 25 de Excel).
    Reemplaza cadenas vacías por NaN y aplica ffill en la columna FECHA por hoja.
    """
    data_start_idx = skip + 2
    if len(rows) <= data_start_idx:
        return None
    
    data_rows = rows[data_start_idx:]
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
    
    # REGLA CRÍTICA 1: Forward-fill de FECHA a nivel de hoja
    df["FECHA"] = df["FECHA"].ffill()
    
    # Identificar columna SONDAJE y columna METRAJE
    col_sondaje = df.columns[1] if len(df.columns) > 1 else None
    col_metraje = None
    for c in df.columns:
        if "METRAJE" in str(c).upper() and "RIMADO" not in str(c).upper() and "REPERFORACION" not in str(c).upper():
            col_metraje = c
            break
    
    # REGLA CRÍTICA 2: Conservar únicamente filas operativas reales (descarta las filas de TOTAL del pie de página)
    def is_valid_operational_row(row):
        sond_val = str(row[col_sondaje]).strip() if col_sondaje and pd.notna(row[col_sondaje]) else ""
        turno_val = str(row.get("TURNO (A=1;B=2)", "")).strip() if pd.notna(row.get("TURNO (A=1;B=2)")) else ""
        grupo_val = str(row.get("GRUPO", "")).strip() if pd.notna(row.get("GRUPO")) else ""
        hasta_val = str(row.get("HASTA", "")).strip() if pd.notna(row.get("HASTA")) else ""
        perf_val = str(row.get("PERFORISTA", "")).strip() if pd.notna(row.get("PERFORISTA")) else ""
        
        has_sondaje = (sond_val != "" and sond_val.lower() not in ("nan", "none"))
        has_turno = (turno_val != "" and turno_val.lower() not in ("nan", "none"))
        has_grupo = (grupo_val != "" and grupo_val.lower() not in ("nan", "none"))
        has_hasta = (hasta_val != "" and hasta_val.lower() not in ("nan", "none"))
        has_perf = (perf_val != "" and perf_val.lower() not in ("nan", "none"))
        
        # Descartar filas de sumatoria/resumen del pie de página
        if not has_sondaje and not has_turno and not has_grupo and not has_hasta and not has_perf:
            return False
            
        met = clean_number_value(row[col_metraje]) if col_metraje and pd.notna(row[col_metraje]) else None
        if met is not None and met > 0:
            return True
        
        desde_val = str(row.get("DESDE", "")).strip() if pd.notna(row.get("DESDE")) else ""
        if (desde_val != "" and desde_val.lower() not in ("nan", "none")) or has_hasta:
            return True
            
        obs = str(row.get("COMENTARIOS", "")).strip() if pd.notna(row.get("COMENTARIOS")) else ""
        if obs != "" and obs.lower() not in ("nan", "none"):
            return True
            
        return False
    
    df = df[df.apply(is_valid_operational_row, axis=1)].copy()
    
    # REGLA CRÍTICA 3: Forward-fill de SONDAJE a nivel de hoja para las filas secundarias conservadas
    if col_sondaje:
        df[col_sondaje] = df[col_sondaje].replace(r'^\s*$', np.nan, regex=True).ffill()
    
    if df.empty:
        return None
    
    return df.reset_index(drop=True)


def apply_rename_dict(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el diccionario de renombrado M de 53 columnas."""
    rename_map = {}
    for old_name, new_name in COLUMN_RENAME_DICT.items():
        if old_name in df.columns:
            rename_map[old_name] = new_name
    
    for col in df.columns:
        col_upper = col.upper().strip()
        if "RIMADO" in col_upper and "CASING" in col_upper:
            if col.endswith("_DESDE") or col_upper.endswith("_DESDE"):
                rename_map[col] = "RIMADO HWT/HQ DESDE"
            elif col.endswith("_HASTA") or col_upper.endswith("_HASTA"):
                rename_map[col] = "RIMADO HWT/HQ HASTA"
            elif col.endswith("_METRAJE") or col_upper.endswith("_METRAJE"):
                rename_map[col] = "RIMADO HWT/HQ METRAJE"
            elif col.endswith("_TOTAL") or col_upper.endswith("_TOTAL"):
                rename_map[col] = "RIMADO HWT/HQ TOTAL"
        elif "RE-PERFORACI" in col_upper or "REPERFORACI" in col_upper:
            if "_DESDE" in col_upper:
                rename_map[col] = "REPERFORACIÓN DESDE"
            elif "_HASTA" in col_upper:
                rename_map[col] = "REPERFORACIÓN HASTA"
            elif "_METRAJE" in col_upper:
                rename_map[col] = "REPERFORACIÓN METRAJE"
            elif "_TOTAL" in col_upper:
                rename_map[col] = "REPERFORACIÓN TOTAL"
        elif "HOROMETRO" in col_upper and "_" in col:
            if "_DESDE" in col_upper:
                rename_map[col] = "HOROMETRO DESDE"
            elif "_HASTA" in col_upper:
                rename_map[col] = "HOROMETRO HASTA"
            elif "_ACUMULADO" in col_upper:
                rename_map[col] = "HOROMETRO ACUMULADO"
            elif "_TOTAL" in col_upper:
                rename_map[col] = "HOROMETRO TOTAL"
        elif "BITACORA" in col_upper and "MANTENIMIENTO" in col_upper:
            if "TRABAJOS" in col_upper:
                rename_map[col] = "TRABAJOS REALIZADOS BITACORA DE MANTTO."
            elif "REPUESTOS" in col_upper:
                rename_map[col] = "REPUESTOS UTILIZADOS BITACORA DE MANTTO."
    
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def calculate_mes(fecha) -> str:
    """Calcula el MES operacional (corte al día 26)."""
    if fecha is None or pd.isna(fecha):
        return "ENERO"
    try:
        if isinstance(fecha, datetime):
            d = fecha
        elif isinstance(fecha, date):
            d = datetime(fecha.year, fecha.month, fecha.day)
        else:
            d = pd.to_datetime(fecha)
            if pd.isna(d):
                return "ENERO"
        
        if d.day >= 26:
            d = d + relativedelta(months=1)
        return MESES_ES[d.month - 1]
    except Exception:
        return "ENERO"


def calculate_zona(ctr: str) -> str:
    return "CENTRO" if ctr in ZONA_CENTRO else "PERIFERICO"


# ============================================================
# PIPELINE PRINCIPAL ETL
# ============================================================

def run_pipeline() -> pd.DataFrame:
    print("=" * 80, flush=True)
    print("PIPELINE ETL DE LIMPIEZA DETALLADOS - ROCKDRILL", flush=True)
    print("=" * 80, flush=True)
    
    # Cargar matriz de excepciones de máquinas SAP
    print("\n[CONFIG] Cargando tabla de Excepciones del Maestro de Máquinas...", flush=True)
    exceptions_map = load_machine_exceptions(MAESTRO_PATH)
    print(f"  Cargadas {len(exceptions_map)} reglas de excepción de máquinas", flush=True)
    
    print("\n[PASO 1-3] Escaneando archivos en Estructura base (excluyendo COLQUIJIRCA)...", flush=True)
    files = find_detallado_files(BASE_PATH)
    print(f"  Encontrados {len(files)} archivos operativos en {len(set(f['ctr'] for f in files))} CTRs", flush=True)
    
    all_tables = []
    stats = {"archivos": 0, "hojas_procesadas": 0, "hojas_descartadas": 0, "filas_total": 0}
    
    for file_info in files:
        ctr = file_info["ctr"]
        filepath = file_info["filepath"]
        filename = file_info["filename"]
        
        print(f"\n[PASO 4-8] Procesando: {ctr} / {filename}", flush=True)
        stats["archivos"] += 1
        
        try:
            workbook = CalamineWorkbook.from_path(str(filepath))
        except Exception as e:
            print(f"  [ERROR] ERROR abriendo archivo: {e}", flush=True)
            continue
        
        sheet_names = workbook.sheet_names
        visible_sheets = get_visible_sheet_names(filepath)
        op_sheets = [s for s in sheet_names if is_operative_sheet_name(s) and (not visible_sheets or s in visible_sheets)]
        print(f"  Hojas: {len(sheet_names)} total, {len(op_sheets)} operativas visibles: {op_sheets}", flush=True)
        
        for sheet_name in op_sheets:
            try:
                sheet = workbook.get_sheet_by_name(sheet_name)
                raw_rows = sheet.to_python()
            except Exception as e:
                print(f"    [WARN] {sheet_name}: Error leyendo datos: {e}", flush=True)
                stats["hojas_descartadas"] += 1
                continue
            
            # SLICING DE SEGURIDAD (primeras 200 filas por hoja max para bypass instantáneo de hojas vacías gigantes)
            rows = raw_rows[:200]
            
            if len(rows) <= MIN_ROWS:
                stats["hojas_descartadas"] += 1
                continue
            
            headers = build_dual_row_headers_from_rows(rows)
            if headers is None:
                stats["hojas_descartadas"] += 1
                continue
            
            df = extract_sheet_data_from_rows(rows, headers)
            if df is None or df.empty:
                print(f"    [WARN] {sheet_name}: Sin datos validos", flush=True)
                stats["hojas_descartadas"] += 1
                continue
            
            # Estandarizar Máquina SAP
            clean_sheet = sheet_name.strip()
            lookup_key = (remove_accents(ctr.upper()), remove_accents(clean_sheet.upper()))
            official_machine = exceptions_map.get(lookup_key, clean_sheet)
            
            df["CTR_Master"] = ctr
            df["ARCHIVO ORIGEN"] = filename
            df["MAQUINA"] = official_machine
            
            all_tables.append(df)
            stats["hojas_procesadas"] += 1
            stats["filas_total"] += len(df)
            print(f"    [OK] {sheet_name} (OFICIAL SAP: {official_machine}): {len(df)} filas", flush=True)
    
    print(f"\n{'=' * 60}", flush=True)
    print(f"RESUMEN DE EXTRACCION:", flush=True)
    print(f"  Archivos procesados:  {stats['archivos']}", flush=True)
    print(f"  Hojas procesadas:     {stats['hojas_procesadas']}", flush=True)
    print(f"  Hojas descartadas:    {stats['hojas_descartadas']}", flush=True)
    print(f"  Filas totales:        {stats['filas_total']}", flush=True)
    print(f"{'=' * 60}", flush=True)
    
    if not all_tables:
        print("[WARN] No se encontraron datos para procesar.", flush=True)
        return pd.DataFrame()
    
    print("\n[PASO 9] Consolidando tablas...", flush=True)
    consolidated = pd.concat(all_tables, ignore_index=True, sort=False)
    
    print("\n[PASO 10] Aplicando diccionario de renombrado M...", flush=True)
    consolidated = apply_rename_dict(consolidated)
    
    print("\n[PASO 11] Enriquecimiento, Estandarización de Turno y Clave Única...", flush=True)
    
    # 1. Asegurar FECHA limpia
    consolidated["FECHA"] = consolidated["FECHA"].replace(r'^\s*$', np.nan, regex=True).ffill()
    consolidated["FECHA"] = pd.to_datetime(consolidated["FECHA"], errors="coerce")
    
    if "CTR_Master" in consolidated.columns:
        consolidated.rename(columns={"CTR_Master": "CTR"}, inplace=True)
    
    consolidated["ZONA"] = consolidated["CTR"].apply(calculate_zona)
    consolidated["MES"] = consolidated["FECHA"].apply(calculate_mes)
    consolidated["HOJA DE TRABAJO ORIGEN"] = consolidated["MAQUINA"]
    consolidated["MAQUINA"] = consolidated["MAQUINA"].apply(
        lambda x: re.sub(r'[^ -~]', '', str(x).upper().strip()) if x else x
    )
    
    # 2. Estandarizar TURNO_ESTANDAR ('A' o 'B') y generar ID_CLAVE_UNICA por turno
    seq_counter = {}
    std_turnos = []
    claves_unicas = []
    
    for idx, row in consolidated.iterrows():
        fecha_str = row["FECHA"].strftime("%Y-%m-%d") if pd.notna(row["FECHA"]) else "SIN_FECHA"
        key = (fecha_str, str(row["CTR"]).upper(), str(row["MAQUINA"]).upper())
        seq_counter[key] = seq_counter.get(key, 0) + 1
        
        t_std = standardize_turno(row, seq_counter[key])
        clave = f"{fecha_str}|{str(row['CTR']).upper()}|{str(row['MAQUINA']).upper()}|{t_std}"
        
        std_turnos.append(t_std)
        claves_unicas.append(clave)
    
    consolidated["TURNO_ESTANDAR"] = std_turnos
    consolidated["ID_CLAVE_UNICA"] = claves_unicas
    consolidated.insert(0, "N°", range(1, len(consolidated) + 1))
    
    print("\n[PASO 12] Alertas y auditoría de comentarios...", flush=True)
    def check_alert(row):
        try:
            otros_cols = [c for c in row.index if c is not None and "Otros*" in str(c)]
            has_otros = False
            for col in otros_cols:
                val = clean_number_value(row[col])
                if val is not None and val > 0:
                    has_otros = True
                    break
            
            obs = ""
            for col_name in ["COMENTARIOS", "SI ES OTROS * INDICAR EL MOTIVO (BREVE EXPLICACION)"]:
                if col_name in row.index and row[col_name] is not None:
                    obs = str(row[col_name]).strip()
                    if obs:
                        break
            
            if has_otros and obs == "":
                return "FALTA COMENTARIO"
            return "OK"
        except Exception:
            return "OK"
    
    consolidated["Alerta_Comentarios"] = consolidated.apply(check_alert, axis=1)
    
    print("\n[PASO 13-14] Aplicando estructura oficial (133 columnas) y limpieza numérica...", flush=True)
    for col in COLS_OFICIALES:
        if col not in consolidated.columns:
            consolidated[col] = None
    
    extra_cols = ["Alerta_Comentarios"]
    final_cols = COLS_OFICIALES + extra_cols
    
    available = [c for c in final_cols if c in consolidated.columns]
    result = consolidated.loc[:, available].copy()
    result = result.loc[:, ~result.columns.duplicated()].copy()
    
    # Limpieza numérica profunda
    print("  Limpiando columnas numéricas...", flush=True)
    for col in COLS_NUMERICAS:
        if col in result.columns:
            ser = result[col]
            if isinstance(ser, pd.DataFrame):
                ser = ser.iloc[:, 0]
            result[col] = ser.apply(clean_number_value)
    
    # Formatear FECHA como texto ISO (YYYY-MM-DD)
    result["FECHA"] = result["FECHA"].dt.strftime("%Y-%m-%d")
    
    # Exportación final
    output_file = OUTPUT_PATH / "detallados_consolidados.xlsx"
    csv_file = OUTPUT_PATH / "detallados_consolidados.csv"
    
    print(f"\n[EXPORTAR] Guardando en {output_file}...", flush=True)
    result.to_excel(str(output_file), index=False, sheet_name="R. DETALLADO", engine="openpyxl")
    print(f"  [OK] Excel guardado exitosamente", flush=True)
    
    result.to_csv(str(csv_file), index=False, encoding="utf-8-sig")
    print(f"  [OK] CSV guardado en {csv_file}", flush=True)
    
    print(f"\n{'=' * 80}", flush=True)
    print("ESTADISTICAS FINALES ETL DETALLADOS", flush=True)
    print(f"{'=' * 80}", flush=True)
    print(f"  CTRs procesados:       {result['CTR'].nunique()}", flush=True)
    print(f"  Máquinas únicas:       {result['MAQUINA'].nunique()}", flush=True)
    print(f"  Registros totales:     {len(result)}", flush=True)
    print(f"  Columnas:              {len(result.columns)}", flush=True)
    print(f"  Rango de fechas:       {result['FECHA'].min()} -> {result['FECHA'].max()}", flush=True)
    print(f"  Claves únicas turnos:  {result['ID_CLAVE_UNICA'].nunique()}", flush=True)
    print(f"  Alertas FALTA COMENT:  {(result['Alerta_Comentarios'] == 'FALTA COMENTARIO').sum()}", flush=True)
    
    print(f"\n  {'CTR':20s} {'Filas':>8s} {'Máquinas':>10s} {'Zona':>12s}", flush=True)
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*12}", flush=True)
    for ctr_name in sorted(result["CTR"].unique()):
        mask = result["CTR"] == ctr_name
        n_filas = mask.sum()
        n_maq = result.loc[mask, "MAQUINA"].nunique()
        zona = result.loc[mask, "ZONA"].iloc[0]
        print(f"  {ctr_name:20s} {n_filas:>8d} {n_maq:>10d} {zona:>12s}", flush=True)
    
    print(f"\n{'=' * 80}", flush=True)
    print("PIPELINE COMPLETADO EXITOSAMENTE", flush=True)
    print(f"{'=' * 80}", flush=True)
    
    return result


if __name__ == "__main__":
    result = run_pipeline()
