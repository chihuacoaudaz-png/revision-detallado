"""
Script de prueba de extracción del archivo Control Interno:
RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx
"""
from python_calamine import CalamineWorkbook
from pathlib import Path
import pandas as pd
import numpy as np
import re
import unicodedata

path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx")
wb = CalamineWorkbook.from_path(str(path))

# Cargar tabla de excepciones de máquinas
maestro_path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Maestro_Maquinas\Maestros_Maquinas.xlsx")
exceptions_map = {}
if maestro_path.exists():
    wb_m = CalamineWorkbook.from_path(str(maestro_path))
    if "Exepciones" in wb_m.sheet_names:
        sheet_m = wb_m.get_sheet_by_name("Exepciones")
        m_rows = sheet_m.to_python()
        for r in m_rows[1:]:
            if len(r) >= 3 and r[0] and r[1] and r[2]:
                def norm(s):
                    return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper().strip()) if not unicodedata.category(c).startswith('M'))
                exceptions_map[(norm(r[0]), norm(r[1]))] = str(r[2]).strip()

print(f"Hojas diarias: {wb.sheet_names}")

all_rows = []

for sheet_name in wb.sheet_names:
    # Solo procesar hojas con formato dd.mm (ej: 26.06, 27.06 ... 25.07)
    if not re.match(r'^\d{2}\.\d{2}$', sheet_name):
        continue
    
    sheet = wb.get_sheet_by_name(sheet_name)
    rows = sheet.to_python()
    
    # Determinar la fecha real de la hoja:
    # Si sheet_name es '26.06' -> '2026-06-26'
    # Si sheet_name es '01.07' -> '2026-07-01'
    day_str, month_str = sheet_name.split(".")
    year_str = "2026"
    fecha_iso = f"{year_str}-{month_str}-{day_str}"
    
    # Las filas de datos comienzan en la fila 10 (index 9)
    current_ctr = None
    
    for row_idx in range(9, len(rows)):
        r = rows[row_idx]
        
        # Verificar si llegamos a TOTAL AVANCE
        row_text = " ".join([str(val).upper().strip() for val in r if val is not None])
        if "TOTAL AVANCE" in row_text or "TOTAL ACUMULADO" in row_text:
            break
        
        # Columna 0: CTR (si está en la fila)
        val_ctr = r[0] if len(r) > 0 else None
        if val_ctr is not None and str(val_ctr).strip() != "":
            raw_ctr = str(val_ctr).strip()
            # Ignorar palabras de títulos si aparecen
            if not any(k in raw_ctr.upper() for k in ["CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"]):
                current_ctr = raw_ctr
        
        # Columna 2: MÁQUINA
        val_maq = r[2] if len(r) > 2 else None
        if val_maq is None or str(val_maq).strip() == "" or str(val_maq).strip().upper() in ("EQUIPO", "SUB", "SUP"):
            continue
        
        maquina_raw = str(val_maq).strip()
        
        # Columna 4: SE PERFORO
        val_perf = r[4] if len(r) > 4 else None
        se_perforo = str(val_perf).strip().upper() if val_perf is not None else ""
        
        # Columna 6: METRAJE DIARIO
        val_met = r[6] if len(r) > 6 else None
        try:
            metraje = float(str(val_met).replace(",", ".")) if val_met is not None and str(val_met).strip() != "" else 0.0
        except ValueError:
            metraje = 0.0
            
        all_rows.append({
            "HOJA_FECHA": sheet_name,
            "FECHA": fecha_iso,
            "CTR_RAW": current_ctr,
            "MAQUINA_RAW": maquina_raw,
            "SE_PERFORO": se_perforo,
            "METRAJE": metraje,
            "ROW_IDX": row_idx + 1
        })

df = pd.DataFrame(all_rows)
print(f"Total registros extraídos: {len(df)}")
print(f"CTRs detectados: {df['CTR_RAW'].unique()}")
print(df.head(20))
