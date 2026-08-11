"""
================================================================================
CONFIGURACIÓN CENTRALIZADA DE RUTAS - REVISION DETALLADO
================================================================================
Este archivo centraliza las rutas para permitir el trabajo PORTABLE entre la
CASA y la OFICINA sin romper el código.

OPCIONES DE ENTORNO ("MODO_ENTORNO"):
  - "AUTO"     : Autodetecta la mejor ruta existente (Recomendado).
  - "PORTABLE" : Usa la carpeta 'Estructura base' dentro del repositorio clonado.
  - "CUSTOM"   : Usa la ruta personalizada definida en RUTA_CUSTOM.
================================================================================
"""

import os
from pathlib import Path
from typing import Tuple

# ------------------------------------------------------------------------------
# 1. SELECCIÓN DE MODO Y RUTA PERSONALIZADA
# ------------------------------------------------------------------------------
MODO_ENTORNO: str = "AUTO"  # Opciones: "AUTO", "PORTABLE", "CUSTOM"

# Si usas MODO_ENTORNO = "CUSTOM", define aquí la ruta raíz de tus datos:
RUTA_CUSTOM: Path = Path(r"C:\Proyectos Pyhton\rddata\Rockdrill_Control_Operaciones")


# ------------------------------------------------------------------------------
# 2. RESOLUCIÓN AUTOMÁTICA DE RUTAS
# ------------------------------------------------------------------------------
REPO_ROOT: Path = Path(__file__).parent.resolve()

def resolve_base_data_path() -> Path:
    """
    Resuelve la carpeta base 'Rockdrill_Control_Operaciones' según el modo seleccionado.
    """
    if MODO_ENTORNO == "CUSTOM" and RUTA_CUSTOM.exists():
        return RUTA_CUSTOM
    
    if MODO_ENTORNO == "PORTABLE":
        portable_path = REPO_ROOT / "Estructura base" / "Rockdrill_Control_Operaciones"
        if portable_path.exists():
            return portable_path

    # Modo AUTO: Probar carpetas conocidas por orden de preferencia
    candidates = [
        REPO_ROOT / "Estructura base" / "Rockdrill_Control_Operaciones",
        Path(r"c:\Proyectos Pyhton\rddata\Rockdrill_Control_Operaciones"),
        Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones"),
        REPO_ROOT.parent / "Estructura base" / "Rockdrill_Control_Operaciones",
    ]
    
    for p in candidates:
        if p.exists():
            return p
            
    # Fallback por defecto a la carpeta portable del repo
    return candidates[0]

# ------------------------------------------------------------------------------
# 3. CONSTANTES GLOBALES DE RUTAS PARA EL PROYECTO
# ------------------------------------------------------------------------------
BASE_PATH: Path = resolve_base_data_path()
MAESTRO_PATH: Path = BASE_PATH / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx"
CONTROL_INTERNO_PATH: Path = BASE_PATH / "00_Control_Interno" / "RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx"

# Carpeta de salidas (output)
OUTPUT_PATH: Path = REPO_ROOT / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

CONTROL_INTERNO_OUTPUT_DIR: Path = REPO_ROOT / "01_Control_Interno_ETL" / "output"
CONTROL_INTERNO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Archivos CSV consolidados finales
DETALLADOS_CSV: Path = OUTPUT_PATH / "detallados_consolidados.csv"
CONTROL_INTERNO_CSV: Path = CONTROL_INTERNO_OUTPUT_DIR / "control_interno_compilado.csv"


if __name__ == "__main__":
    print("=" * 80)
    print("ESTADO DE CONFIGURACIÓN DE RUTAS")
    print("=" * 80)
    print(f"Modo seleccionado:           {MODO_ENTORNO}")
    print(f"Raíz del Repositorio:        {REPO_ROOT}")
    print(f"Carpeta Base de Datos:       {BASE_PATH} (Existe: {BASE_PATH.exists()})")
    print(f"Maestro de Máquinas:         {MAESTRO_PATH} (Existe: {MAESTRO_PATH.exists()})")
    print(f"Control Interno Excel:       {CONTROL_INTERNO_PATH} (Existe: {CONTROL_INTERNO_PATH.exists()})")
    print(f"Carpeta Output Detallados:   {OUTPUT_PATH}")
    print(f"Carpeta Output C. Interno:   {CONTROL_INTERNO_OUTPUT_DIR}")
