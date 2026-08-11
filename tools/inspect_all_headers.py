"""
Script para inspeccionar las filas 21, 22, 23, 24, 25 de TODAS las hojas operativas de TODOS los CTRs.
"""
from python_calamine import CalamineWorkbook
from pathlib import Path
import re

BASE_PATH = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones")
HOJAS_EXCLUIDAS = {"ADITIVOS", "GENERAL", "LISTAS", "Tiempos"}

def extract_ctr_from_folder(folder_name: str) -> str:
    return folder_name.replace("CTR_", "").replace("_", " ").upper().strip()

def find_detallado_files(base_path: Path):
    files = []
    for ctr_folder in sorted(base_path.iterdir()):
        if not ctr_folder.is_dir() or not ctr_folder.name.startswith("CTR_"):
            continue
        ctr = extract_ctr_from_folder(ctr_folder.name)
        detallado_folder = ctr_folder / "02_Detallado"
        search_folder = detallado_folder if detallado_folder.exists() else ctr_folder
        for xlsx_file in search_folder.glob("*.xlsx"):
            if xlsx_file.name.startswith("~$"):
                continue
            files.append((ctr, xlsx_file))
    return files

files = find_detallado_files(BASE_PATH)

for ctr, filepath in files:
    print(f"\n{'='*80}")
    print(f"CTR: {ctr} | Archivo: {filepath.name}")
    print(f"{'='*80}")
    wb = CalamineWorkbook.from_path(str(filepath))
    for name in wb.sheet_names:
        if name in HOJAS_EXCLUIDAS or re.match(r'^[Mm][AaÁá]quina\s*\d+$', name, re.IGNORECASE) or name in ("Hoja1", "Hoja3"):
            continue
        sheet = wb.get_sheet_by_name(name)
        rows = sheet.to_python()
        if len(rows) <= 24:
            continue
        
        print(f"\n  Hoja '{name}' (Total filas: {len(rows)}):")
        # Mostrar filas 21, 22, 23, 24, 25 (0-indexed 20, 21, 22, 23, 24)
        for idx in range(20, min(26, len(rows))):
            non_empty = [(col_idx, str(val)) for col_idx, val in enumerate(rows[idx][:20]) if val is not None and str(val).strip() != ""]
            print(f"    Fila {idx+1} (idx {idx}): {non_empty[:8]}")
