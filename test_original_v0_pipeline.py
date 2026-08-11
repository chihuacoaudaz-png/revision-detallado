import os
import sys
import re
import importlib
import pandas as pd
from pathlib import Path

base_dir = Path(r"c:\Proyectos Python\Detallados")
sys.path.insert(0, str(base_dir))

comp_mod = importlib.import_module("01_Control_Interno_ETL.compilar_control_interno")
load_machine_exceptions = comp_mod.load_machine_exceptions
exceptions_map = load_machine_exceptions(base_dir / "Estructura base" / "Rockdrill_Control_Operaciones" / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx")

v0_path = base_dir / "codigo_m" / "codigo_m_detallados_v0.txt"
with open(v0_path, "r", encoding="utf-8") as f:
    v0_code = f.read()

print(f"Loaded original v0 M code ({len(v0_code)} bytes)")
