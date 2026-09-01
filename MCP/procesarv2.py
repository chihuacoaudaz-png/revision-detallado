import polars as pl
import os
import re
import time
from unidecode import unidecode

# --- CONFIGURACIÓN DE RUTAS ---
NOMBRE_ARCHIVO = "C:/Users/PERDLAP140.VILBRAGROUP/OneDrive - ROCK DRILL/REPORTES BI EXCEL/BD/HISTORICO-PERDLAP140.xlsx"
NOMBRE_HOJA = "BD_DETALLADO"
SALIDA_FOLDER = r"C:/Users/PERDLAP140.VILBRAGROUP/OneDrive - ROCK DRILL/REPORTES BI EXCEL/BD"
ARCHIVO_ACTIVIDADES = "C:/Users/PERDLAP140.VILBRAGROUP/OneDrive - ROCK DRILL/REPORTES BI EXCEL/BD/ACTY.xlsx"

# --- FUNCIONES ---

def normalizar_nombre(nombre):
    """Normaliza nombres: mayúsculas, sin acentos, sin puntos, espacios limpios"""
    if nombre is None or str(nombre).strip() == "" or str(nombre).upper() == "NAN": 
        return ""
    n = str(nombre).strip().upper()
    n = unidecode(n)
    n = re.sub(r'[,\.]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def limpiar_key(texto):
    """Estandariza texto para evitar duplicados en actividades o llaves"""
    if texto is None: return ""
    t = str(texto).upper().replace('\u00a0', ' ').strip()
    t = t.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    t = re.sub(r'[\(\)\.]', '', t) 
    t = re.sub(r'\s+', '_', t) 
    return t.strip('_')

def normalizar_cols_excel(cols):
    """Normaliza nombres de columnas del Excel"""
    new_cols = []
    conteo = {} 
    for c in cols:
        clean = limpiar_key(c)
        if clean in conteo:
            conteo[clean] += 1
            final = f"{clean}_{conteo[clean]}" 
        else:
            conteo[clean] = 0
            final = clean
        new_cols.append(final)
    return new_cols

def procesar_data():
    start_time = time.time()
    print("🚀 INICIANDO PROCESO (RESTAURACIÓN TOTAL DE COLUMNAS)...")
    
    if not os.path.exists(SALIDA_FOLDER): 
        os.makedirs(SALIDA_FOLDER)

    try:
        # --- PASO A: MAESTRO DE ACTIVIDADES ---
        df_act = pl.read_excel(ARCHIVO_ACTIVIDADES, infer_schema_length=0)
        df_act.columns = [c.upper().strip() for c in df_act.columns]
        df_act = df_act.with_columns(
            pl.col("ACTIVIDAD").map_elements(limpiar_key, return_dtype=pl.Utf8).alias("JOIN_KEY")
        )
        df_master = df_act.select(["JOIN_KEY", "TIPO", "DG", "TRASLADO", "AREA"]).unique(subset=["JOIN_KEY"])

        # --- PASO B: HISTÓRICO ---
        df = pl.read_excel(source=NOMBRE_ARCHIVO, sheet_name=NOMBRE_HOJA, engine="calamine", infer_schema_length=0)
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))
        df.columns = normalizar_cols_excel(df.columns)

        # --- PASO C: TRANSFORMACIONES ---
        df = df.with_columns(
            pl.col('FECHA').str.strptime(pl.Date, "%Y-%m-%d %H:%M:%S", strict=False)
            .fill_null(pl.col('FECHA').str.strptime(pl.Date, "%d/%m/%Y", strict=False))
        ).filter(pl.col('FECHA').is_not_null())

        # Identificar ayudantes y columnas especiales
        cols_ayudantes = [c for c in df.columns if 'AYUDANTE' in c]
        col_prof_prog = next((c for c in df.columns if 'PROFUNDIDAD' in c and 'SONDAJE' in c), None)
        col_met = 'METRAJE_X_GUARDIA' if 'METRAJE_X_GUARDIA' in df.columns else 'METRAJE'

        # Normalización de personal en sus columnas originales
        df = df.with_columns(pl.col("PERFORISTA").map_elements(normalizar_nombre, return_dtype=pl.Utf8))
        for col_ay in cols_ayudantes:
            df = df.with_columns(pl.col(col_ay).map_elements(normalizar_nombre, return_dtype=pl.Utf8))

        # Crear KEY_OPERACION
        df = df.with_columns(
            pl.concat_str([
                pl.col('FECHA').dt.strftime('%Y%m%d'), pl.lit("-"),
                pl.col('MAQUINA').fill_null('ND'), pl.lit("-"),
                pl.col('TURNO').fill_null('ND')
            ]).alias('KEY_OPERACION')
        )

        # --- LISTA MAESTRA DE COLUMNAS DE IDENTIDAD (NO BORRAR NI RENOMBRAR) ---
        lista_cols_base = ['KEY_OPERACION', 'FECHA', 'MAQUINA', 'CTR', 'TURNO', 'SONDAJE', 'PERFORISTA', 'GRUPO', 'LINEA', 'AÑO', 'GUARDIAS']
        cols_id = [c for c in lista_cols_base if c in df.columns] + cols_ayudantes

        # --- PASO D: FACT_TIEMPOS ---
        keys_maestro_set = set(df_master["JOIN_KEY"].to_list())
        cols_act = [c for c in df.columns if re.sub(r'_\d+$', '', c) in keys_maestro_set]
        
        if cols_act:
            df_tiempos = df.with_columns([pl.col(c).cast(pl.Float64, strict=False).fill_null(0) for c in cols_act])
            fact_tiempos = df_tiempos.unpivot(index=cols_id, on=cols_act, variable_name='Actividad_Raw', value_name='Horas').filter(pl.col('Horas') > 0)
            fact_tiempos = fact_tiempos.with_columns(pl.col("Actividad_Raw").str.replace(r'_\d+$', '').alias("JOIN_KEY_EXCEL"))
            fact_tiempos = fact_tiempos.join(df_master, left_on="JOIN_KEY_EXCEL", right_on="JOIN_KEY", how="left")
            fact_tiempos.write_csv(f"{SALIDA_FOLDER}/Fact_Tiempos.csv")

        # --- PASO E: EXPORTACIONES ---
        
        # 1. Dim_Maquina
        dim_maquina = df.select([c for c in ['MAQUINA', 'GRUPO', 'LINEA'] if c in df.columns]).unique().drop_nulls()
        dim_maquina.write_csv(f"{SALIDA_FOLDER}/Dim_Maquina.csv")

        # 2. Fact_Metraje
        if col_met in df.columns:
            fact_metraje = df.select([c for c in cols_id + [col_met] if c in df.columns])
            fact_metraje.write_csv(f"{SALIDA_FOLDER}/Fact_Metraje.csv")

        # 3. Dim_Personal (NOMBRE DE COLUMNA: PERFORISTA)
        stack_p = [df.select(pl.col("PERFORISTA"))]
        for c_ay in cols_ayudantes:
            stack_p.append(df.select(pl.col(c_ay).alias("PERFORISTA")))
        dim_personal = pl.concat(stack_p).unique().drop_nulls().filter(pl.col("PERFORISTA") != "")
        dim_personal.write_csv(f"{SALIDA_FOLDER}/Dim_Personal.csv")

        # 4. Dim_Sondaje (RESTAURADO: PROFUNDIDAD_PROGRAMADA y CTR_A_CARGO)
        if 'SONDAJE' in df.columns:
            aggs = [
                pl.col("FECHA").min().alias("FECHA_INICIO_REAL"),
                pl.col("FECHA").max().alias("FECHA_FIN_REAL"),
                pl.col(col_met).cast(pl.Float64).sum().alias("AVANCE_ACUMULADO"),
                pl.col("MAQUINA").first().alias("MAQUINA_PRINCIPAL"),
                pl.col("CTR").first().alias("CTR_A_CARGO")
            ]
            if col_prof_prog:
                aggs.append(pl.col(col_prof_prog).cast(pl.Float64, strict=False).max().alias("PROFUNDIDAD_PROGRAMADA"))
            
            dim_sondaje = df.group_by("SONDAJE").agg(aggs).filter(pl.col("SONDAJE") != "")
            dim_sondaje.write_csv(f"{SALIDA_FOLDER}/Dim_Sondaje.csv")

        # 5. Dim_CTR (Opcional, pero se mantiene para estabilidad)
        if 'CTR' in df.columns:
            dim_ctr = df.select(['CTR']).unique().drop_nulls()
            dim_ctr.write_csv(f"{SALIDA_FOLDER}/Dim_CTR.csv")

        elapsed_time = time.time() - start_time
        print(f"\n✅ PROCESO FINALIZADO EN {elapsed_time:.2f}s")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    procesar_data()