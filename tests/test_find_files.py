"""
Imprimir archivos encontrados por find_detallado_files
"""
from pipeline_limpieza import find_detallado_files, BASE_PATH

files = find_detallado_files(BASE_PATH)
print(f"Total archivos encontrados: {len(files)}")
for f in files:
    print(f"  CTR: {f['ctr']:20s} | File: {f['filename']}")
