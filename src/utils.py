"""
Funciones Utilitarias y Normalización de Datos (Rockdrill)
==========================================================
Módulo con validaciones XML, normalización diacrítica, limpieza numérica
y carga del Maestro de Máquinas SAP.
"""

import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Tuple, Set

import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook


def get_visible_sheet_names(excel_path: Path) -> Set[str]:
    """
    Extrae los nombres de hojas VISIBLES de un archivo Excel .xlsx usando zipfile y XML.
    Ignora hojas ocultas (hidden / veryHidden) replicando el filtro nativo de Power Query.
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


def clean_number_value(val: any) -> Optional[float]:
    """
    Convierte cualquier valor heterogéneo a float válido o None.
    Maneja formatos estándar (1,234.56, 1234.56) y europeos (1.234,56, 1234,56),
    espacios, valores nulos y errores de fórmula de Excel.
    """
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)

    s = str(val).strip()
    if not s:
        return None

    # Excel error codes and null strings
    if s.upper() in (
        "-", "--", "N/A", "NA", "NULL", "NONE",
        "#VALUE!", "#N/A", "#REF!", "#DIV/0!", "#NUM!", "#NAME?", "#NULL!", "#N/D"
    ):
        return None

    # Remove internal spaces
    s = re.sub(r'\s+', '', s)
    if not s or s in ("-", "--"):
        return None

    # Punctuation formatting (US vs European)
    if "." in s and "," in s:
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_comma > last_dot:
            # European format: 1.234,56 -> remove dots, replace comma with dot
            s = s.replace(".", "").replace(",", ".")
        else:
            # US format: 1,234.56 -> remove commas
            s = s.replace(",", "")
    elif "," in s:
        # Only commas present
        if s.count(",") > 1:
            # Multiple commas: 1,234,567 -> thousands separator
            s = s.replace(",", "")
        else:
            # Single comma: 1234,56 or 1,234 -> decimal separator
            s = s.replace(",", ".")
    elif "." in s:
        # Only dots present
        if s.count(".") > 1:
            # Multiple dots: 1.234.567 -> thousands separator
            s = s.replace(".", "")

    try:
        v = float(s)
        return None if np.isnan(v) or np.isinf(v) else v
    except ValueError:
        return None


def normalize_ctr(raw_ctr: str) -> str:
    """
    Normaliza el nombre de un contrato minero (CTR) eliminando prefijos y acentos.
    """
    if not raw_ctr:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(raw_ctr).replace("CTR_", "").replace("_", " ").upper().strip())
    s = ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
    if "CUCUL" in s:
        return "CUCULI"
    if "SAN CRISTOBAL" in s:
        return "SAN CRISTOBAL"
    return s


KNOWN_FALLBACK_EXCEPTIONS: Dict[Tuple[str, str], str] = {
    ("TICLIO", "XRD150USS-001"): "XRD150U-007",
    ("TICLIO", "XRD150U-007"): "XRD150U-007",
    ("TAMBOJASA", "DE710ST-002"): "DE710T-002",
    ("YAULIYACU", "XRD50USS-001"): "XDR50USS-00T",
    ("YAULIYACU", "XRD50USS-00T"): "XDR50USS-00T",
    ("MOROCOCHA", "XRD90USS-002"): "XRD90USS-005",
    ("MOROCOCHA", "XRD150USS"): "XRD150USS-002",
    ("CHUNGAR", "XRD90U-003"): "XRD90U-021",
    ("ANDAYCHAGUA", "XRD90U-017"): "XRD150U-001",
    ("ANDAYCHAGUA", "LF90DST-002"): "LF90D ST-002",
    ("COBRIZA", "XRD90U-008"): "XRD150U-008",
    ("CATALINA HUANCA", "XRD50-003"): "XRD50U-003",
    ("CATALINA HUANCA", "XRD100U-01"): "XRD100U-001",
    ("INMACULADA", "XRD150-004"): "XRD150USS-004",
    ("INMACULADA", "XRD250-001"): "XRD250U-001",
    ("INMACULADA", "XRD80U-008"): "XRD80USS-008",
    ("INMACULADA", "XRD90U-012 (XRD150)"): "XRD90U-012",
}


def load_machine_exceptions(maestro_path: Path) -> Dict[Tuple[str, str], str]:
    """
    Carga la matriz oficial de excepciones de nombres de máquina del Maestro SAP (hoja 'Exepciones').
    Mapea (CTR, nombre_hoja_local) -> codigo_maquina_sap_oficial.
    """
    exepciones = dict(KNOWN_FALLBACK_EXCEPTIONS)
    if not maestro_path.exists():
        return exepciones
    try:
        cal = CalamineWorkbook.from_path(str(maestro_path))
        if "Exepciones" in cal.sheet_names:
            rows = cal.get_sheet_by_name("Exepciones").to_python()
            if len(rows) > 1:
                headers = [str(c or "").strip().upper() for c in rows[0]]
                df_ex = pd.DataFrame(rows[1:], columns=headers)
                for _, r in df_ex.iterrows():
                    ctr = normalize_ctr(str(r.iloc[0] or ""))
                    hoja = str(r.iloc[1] or "").strip().upper()
                    maq_sap = str(r.iloc[2] or "").strip().upper()
                    if ctr and hoja and maq_sap and hoja != "NONE" and maq_sap != "NONE":
                        exepciones[(ctr, hoja)] = maq_sap
    except Exception as e:
        print(f"  [WARN] No se pudo cargar excepciones de máquina: {e}")
    return exepciones
