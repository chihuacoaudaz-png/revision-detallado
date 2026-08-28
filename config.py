"""
================================================================================
CONFIGURACIÓN CENTRAL DEL PROYECTO - ROCKDRILL CONTROL OPERACIONES
================================================================================
Este archivo centraliza TODOS los parámetros de rutas, modos de ejecución y
opciones del proyecto. 

Cualquier usuario (incluso sin conocimientos de programación) puede ajustar
aquí los parámetros para que todo el proyecto funcione en su computadora o
en su carpeta compartida de OneDrive.

--------------------------------------------------------------------------------
GUÍA RÁPIDA DE CONFIGURACIÓN:
--------------------------------------------------------------------------------
1. MODO_ENTORNO:
   - "AUTO"     : Autodetecta si la carpeta existe en local o en OneDrive (RECOMENDADO).
   - "PORTABLE" : Usa la carpeta 'Estructura base' dentro del proyecto.
   - "CUSTOM"   : Usa la ruta manual que tú escribas en 'RUTA_CUSTOM'.

2. RUTA_CUSTOM:
   - Si eliges MODO_ENTORNO = "CUSTOM", escribe aquí la ruta exacta a tu carpeta
     de OneDrive o red compartida.
================================================================================
"""

import os
import sys
from pathlib import Path
from typing import Set

# ==============================================================================
# ⚙️ 1. SELECCIÓN DE ENTORNO Y RUTAS PRINCIPALES
# ==============================================================================

# Opciones: "AUTO" | "PORTABLE" | "CUSTOM"
MODO_ENTORNO: str = "AUTO"

# Si usas MODO_ENTORNO = "CUSTOM", especifica aquí la ruta exacta de tu OneDrive:
RUTA_CUSTOM: Path = Path(r"C:\Users\tu_usuario\OneDrive - ROCKDRILL GROUP\Rockdrill_Control_Operaciones")


# ==============================================================================
# ⚙️ 2. OPCIONES OPERATIVAS Y FILTROS DEL PIPELINE ETL
# ==============================================================================

# Contratos mineros excluidos del control de metrajes (según regla corporativa)
CTRS_EXCLUIDOS: Set[str] = {"COLQUIJIRCA", "CAPITANA"}

# Hojas no operativas a ignorar en los libros Excel
HOJAS_EXCLUIDAS: Set[str] = {
    "ADITIVOS", "GENERAL", "LISTAS", "Tiempos", "RESUMEN", "GRAFICOS", "MAESTRO"
}

# Parámetros de cabecera en los archivos Excel
SKIP_ROWS: int = 22   # Fila 23 del Excel (0-indexed = 22) es el primer nivel de encabezado
MIN_ROWS: int = 24    # Hojas con menos de 24 filas no tienen datos operativos


# ==============================================================================
# 🔍 3. RESOLUCIÓN AUTOMÁTICA DE RUTAS DEL SISTEMA
# ==============================================================================

REPO_ROOT: Path = Path(__file__).parent.resolve()

def resolve_base_data_path() -> Path:
    """
    Resuelve la carpeta 'Rockdrill_Control_Operaciones' según el modo configurado.
    """
    if MODO_ENTORNO == "CUSTOM" and RUTA_CUSTOM.exists():
        return RUTA_CUSTOM

    if MODO_ENTORNO == "PORTABLE":
        portable_path = REPO_ROOT / "Estructura base" / "Rockdrill_Control_Operaciones"
        if portable_path.exists():
            return portable_path

    # Modo AUTO: Buscar en las ubicaciones estándar
    candidatos = [
        REPO_ROOT / "Estructura base" / "Rockdrill_Control_Operaciones",
        Path.home() / "OneDrive - ROCKDRILL GROUP" / "Rockdrill_Control_Operaciones",
        Path.home() / "OneDrive" / "Rockdrill_Control_Operaciones",
        Path(r"C:\Proyectos Python\rddata\Rockdrill_Control_Operaciones"),
        REPO_ROOT.parent / "Estructura base" / "Rockdrill_Control_Operaciones",
    ]

    for p in candidatos:
        if p.exists():
            return p

    # Fallback por defecto a la carpeta portable
    return candidatos[0]


def resolve_control_interno_path(base_path: Path) -> Path:
    """
    Busca dinámicamente el libro maestro de Control Interno dentro de '00_Control_Interno'.
    """
    ci_dir = base_path / "00_Control_Interno"
    if ci_dir.exists():
        candidatos = [f for f in ci_dir.glob("*.xlsx") if not f.name.startswith("~$")]
        if candidatos:
            candidatos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return candidatos[0]
    return base_path / "00_Control_Interno" / "RD.402.P.01.F.04  Consolidado de Avance.xlsx"


# ==============================================================================
# 📂 4. CONSTANTES GLOBALES EXPORTADAS PARA TODO EL PROYECTO
# ==============================================================================

BASE_PATH: Path = resolve_base_data_path()
MAESTRO_PATH: Path = BASE_PATH / "Maestro_Maquinas" / "Maestros_Maquinas.xlsx"
CONTROL_INTERNO_PATH: Path = resolve_control_interno_path(BASE_PATH)

OUTPUT_PATH: Path = REPO_ROOT / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Archivos de salida consolidados
DETALLADOS_XLSX: Path = OUTPUT_PATH / "detallados_consolidados.xlsx"
DETALLADOS_CSV: Path = OUTPUT_PATH / "detallados_consolidados.csv"
MATRIZ_COMPARATIVA_XLSX: Path = OUTPUT_PATH / "matriz_comparativa_metrajes.xlsx"
AUDITORIA_DESCARGAS_DIR: Path = OUTPUT_PATH / "auditoria_descargas"


if __name__ == "__main__":
    print("=" * 80)
    print("  ESTADO DE CONFIGURACIÓN Y RUTAS - ROCKDRILL CONTROL OPERACIONES")
    print("=" * 80)
    print(f"  Modo de entorno:            {MODO_ENTORNO}")
    print(f"  Directorio del proyecto:    {REPO_ROOT}")
    print(f"  Carpeta de datos operativos: {BASE_PATH} (Existe: {BASE_PATH.exists()})")
    print(f"  Maestro de Máquinas:        {MAESTRO_PATH} (Existe: {MAESTRO_PATH.exists()})")
    print(f"  Control Interno Excel:      {CONTROL_INTERNO_PATH} (Existe: {CONTROL_INTERNO_PATH.exists()})")
    print(f"  Carpeta de entregables:     {OUTPUT_PATH}")
    print("=" * 80)
