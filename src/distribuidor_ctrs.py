"""
Módulo de Distribución Automatizada de Reportes Detallados por CTR
Rockdrill Group - Sistema de Ingesta Dinámica
"""
import os
import re
import shutil
import glob
from typing import Dict, List, Tuple

def normalizar_nombre_ctr(nombre_archivo: str) -> str:
    """
    Extrae y normaliza el nombre del CTR a partir del nombre del archivo Excel.
    """
    base = os.path.splitext(os.path.basename(nombre_archivo))[0].upper()
    
    # Limpiar prefijos comunes
    base = re.sub(r"^COPIA DE\s*", "", base)
    base = re.sub(r"^RD\.402\.P\.01\.F\.01\s*", "", base)
    base = re.sub(r"^REPORTE DETALLADO DE AVANCE\s*", "", base)
    base = re.sub(r"^REPORTE DETALLADO\s*", "", base)
    base = re.sub(r"^AVANCE DETALLADO\s*", "", base)
    base = re.sub(r"^DETALLADO\s*", "", base)
    base = re.sub(r"[-_]\s*SETIEMBRE.*$", "", base)
    base = re.sub(r"[-_]\s*SEPTIEMBRE.*$", "", base)
    base = re.sub(r"[-_]\s*AGOSTO.*$", "", base)
    base = re.sub(r"\(NUEVO\)", "", base)
    
    # Reemplazos específicos conocidos
    base = base.replace("-", " ").replace("_", " ").strip()
    
    mapeo_ctrs = {
        "COBRIZA": "COBRIZA",
        "MOROCOCHA": "MOROCOCHA",
        "TAMBOJASA": "TAMBOJASA",
        "CATALINA HUANCA": "CATALINA_HUANCA",
        "COLQUISIRI": "COLQUISIRI",
        "SAN CRISTOBAL": "SAN_CRISTOBAL",
        "AMERICANA": "AMERICANA",
        "ANDAYCHAGUA": "ANDAYCHAGUA",
        "CAPITANA": "CAPITANA",
        "CERRO": "CERRO_CORONA",
        "CHUNGAR": "CHUNGAR",
        "CONDESTABLE": "CONDESTABLE",
        "CUCULI": "CUCULI",
        "RAURA": "RAURA",
        "INMACULADA": "INMACULADA",
        "LA ESTRELLA": "LA_ESTRELLA",
        "TICLIO": "TICLIO",
        "YAULIYACU": "YAULIYACU",
        "YAURICOCHA": "YAURICOCHA",
        "COLQUIJIRCA": "COLQUIJIRCA",
        "TOROMOCHO": "TOROMOCHO"
    }
    
    for key, val in mapeo_ctrs.items():
        if key in base:
            return val
            
    # Si no coincide exactamente, limpiar caracteres no alfanuméricos
    ctr_limpio = re.sub(r"[^A-Z0-9]+", "_", base).strip("_")
    return ctr_limpio if ctr_limpio else "CTR_GENERAL"

def distribuir_detallados_en_carpetas_ctr(
    directorio_origen: str = "distribucion",
    directorio_destino_base: str = "data_in/CTRs"
) -> Dict[str, List[str]]:
    """
    Distribuye los archivos .xlsx de la carpeta de distribución en subcarpetas por cada CTR.
    Crea la estructura modular que permite auto-descubrimiento en Python y Power Query.
    """
    os.makedirs(directorio_destino_base, exist_ok=True)
    patron = os.path.join(directorio_origen, "*.xlsx")
    archivos = glob.glob(patron)
    
    distribucion_resumen = {}
    
    for ruta_archivo in archivos:
        nombre_archivo = os.path.basename(ruta_archivo)
        ctr_norm = normalizar_nombre_ctr(nombre_archivo)
        
        carpeta_ctr = os.path.join(directorio_destino_base, ctr_norm)
        os.makedirs(carpeta_ctr, exist_ok=True)
        
        ruta_destino = os.path.join(carpeta_ctr, nombre_archivo)
        shutil.copy2(ruta_archivo, ruta_destino)
        
        if ctr_norm not in distribucion_resumen:
            distribucion_resumen[ctr_norm] = []
        distribucion_resumen[ctr_norm].append(nombre_archivo)
        print(f"📁 [{ctr_norm}] -> {nombre_archivo}")
        
    return distribucion_resumen

if __name__ == "__main__":
    import sys
    # Configurar UTF-8 en consola
    if sys.stdout.encoding != 'utf-8':
        try: sys.stdout.reconfigure(encoding='utf-8')
        except Exception: pass
        
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    origen = os.path.join(base_dir, "distribucion")
    destino = os.path.join(base_dir, "data_in", "CTRs")
    
    print(f"🚀 Iniciando distribución modular desde: {origen}")
    res = distribuir_detallados_en_carpetas_ctr(origen, destino)
    print(f"✅ Se distribuyeron exitosamente {sum(len(v) for v in res.values())} archivos en {len(res)} CTRs.")
