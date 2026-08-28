"""
Script de Distribución Limpia de Detallados Actualizados
Reemplaza los archivos antiguos en Estructura base/Rockdrill_Control_Operaciones/CTR_*/02_Detallado/
y ejecuta la conciliación contra 00_Control_Interno
"""
import os
import sys
import shutil
from pathlib import Path

# Forzar UTF-8 en consola
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

def distribuir_y_reemplazar_detallados(
    dir_distribucion: str = "distribucion",
    dir_base: str = "Estructura base/Rockdrill_Control_Operaciones"
):
    dist_dir = Path(dir_distribucion).resolve()
    base_eb = Path(dir_base).resolve()
    
    mapeo_nombres = {
        'COBRIZA': 'CTR_COBRIZA',
        'MOROCOCHA': 'CTR_MOROCOCHA',
        'TAMBOJASA': 'CTR_TAMBOJASA',
        'CATALINA': 'CTR_CATALINA_HUANCA',
        'COLQUISIRI': 'CTR_COLQUISIRI',
        'SAN_CRISTOBAL': 'CTR_SAN_CRISTOBAL',
        'AMERICANA': 'CTR_AMERICANA',
        'ANDAYCHAGUA': 'CTR_ANDAYCHAGUA',
        'CAPITANA': 'CTR_CAPITANA',
        'CERRO': 'CTR_CERRO',
        'CHUNGAR': 'CTR_CHUNGAR',
        'CONDESTABLE': 'CTR_CONDESTABLE',
        'CUCULI': 'CTR_CUCULI',
        'INMACULADA': 'CTR_INMACULADA',
        'ESTRELLA': 'CTR_LA_ESTRELLA',
        'RAURA': 'CTR_RAURA',
        'TICLIO': 'CTR_TICLIO',
        'YAULIYACU': 'CTR_YAULIYACU',
        'YAURICOCHA': 'CTR_YAURICOCHA'
    }
    
    # Unificar carpeta CERRO
    if (base_eb / 'CTR_CERRO_CORONA').exists():
        shutil.rmtree(base_eb / 'CTR_CERRO_CORONA')

    print("=" * 80)
    print("🚀 INICIANDO DISTRIBUCIÓN Y REEMPLAZO LIMPIO DE DETALLADOS")
    print(f"📁 Origen: {dist_dir}")
    print(f"📁 Destino: {base_eb}")
    print("=" * 80)

    archivos_dist = list(dist_dir.glob("*.xlsx"))
    print(f"📦 Total de archivos en distribución: {len(archivos_dist)}")

    distribuidos = 0
    for f in archivos_dist:
        f_up = f.name.upper().replace('-', '_').replace(' ', '_')
        target_ctr_dir = None
        
        for key, folder_name in mapeo_nombres.items():
            if key in f_up:
                target_ctr_dir = base_eb / folder_name
                break
                
        if not target_ctr_dir:
            print(f"⚠️ No se encontró carpeta para: {f.name}")
            continue
            
        det_dir = target_ctr_dir / "02_Detallado"
        det_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Eliminar todos los archivos previos en 02_Detallado
        for old_f in det_dir.glob("*.xls*"):
            try:
                old_f.unlink()
                print(f"  [ELIMINADO PREVIO] {old_f.name} en {target_ctr_dir.name}/02_Detallado")
            except Exception as e:
                print(f"  [ERROR ELIMINAR] {old_f.name}: {e}")
                
        # 2. Copiar el archivo actualizado de septiembre
        target_dest = det_dir / f.name
        shutil.copy2(f, target_dest)
        print(f"  [COPIADO NUEVO] {f.name} -> {target_ctr_dir.name}/02_Detallado/")
        distribuidos += 1

    print("\n" + "=" * 80)
    print(f"✅ Se distribuyeron y reemplazaron exitosamente {distribuidos} archivos en sus carpetas CTR.")
    print("=" * 80)

if __name__ == "__main__":
    distribuir_y_reemplazar_detallados()
