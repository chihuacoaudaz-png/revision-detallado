"""
Prueba de corrección de ffill en SONDAJE y filtro de filas operativas reales
"""
import pandas as pd
import numpy as np

# Probar la corrección en pipeline_limpieza.py y ver los resultados en Chungar y Morococha
from pipeline_limpieza import run_pipeline

print("Ejecutando pipeline con la corrección...")
df_res = run_pipeline()
