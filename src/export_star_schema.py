"""
Generador de Esquema Estrella para Power BI (Rockdrill)
======================================================
Transforma la tabla ancha canónica (135 columnas) de 'detallados_consolidados'
en las tablas de Hechos y Dimensiones normalizadas del modelo Power BI (RESIDENTES.pbix):
  1. Fact_Metraje.csv
  2. Fact_Tiempos.csv (Unpivot de las columnas de tiempo con Categoría, Responsable y Afecta_Disp)
  3. Dim_Maquina.csv
  4. Dim_Personal.csv
  5. Dim_Sondaje.csv
  6. Dim_CTR.csv
  7. Fact_Personal_Asignado.csv (Puente M:M para perforistas y ayudantes)
"""

import re
import unicodedata
from pathlib import Path
from typing import Dict, Tuple, List
import pandas as pd
import numpy as np

# Mapeo oficial de Columnas de Tiempo a Categoría, Afecta_Disponibilidad y Responsable
# Basado en la taxonomía de ACTY.xlsx y RESIDENTES.pbix
CATALOGO_ACTIVIDADES_DETALLADO: Dict[str, Tuple[str, str, str]] = {
    # (Nombre_Columna_Detallado): (Categoria, Afecta_Disp, Responsable)
    "Perforación": ("EFECTIVAS", "NO AFECTA", "OPERACIONES"),
    "Rimado": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Asentado / Retiro DE REVESTIMIENTO (CASING)": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Calibración de pozo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Corte de Testigo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Despeje de pozo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Medición de Trayectoria / Orientación de Testigo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Prueba de Presión Lugeon / Lefranc": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Recuperación de Pozo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Tapón de Pozo": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Inspección Prevencional / IPERC / OPT / Charlas": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Traslado e Instalación": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Maniobra de Barras y Tuberias": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Abastecimiento de Agua": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Movilización / Desmovilización": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Limpieza de Área / Desbroce / Poza de Lodos": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Desarmado de Tuberías y Equipos": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Esperas Operativas": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Tendido de Tuberías": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Recuperación de Herramientas": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Trabajos Auxiliares": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Mantenimiento Mecánico": ("MANTENIMIENTO", "AFECTA", "MANTENIMIENTO"),
    "Mantenimiento Eléctrico": ("MANTENIMIENTO", "AFECTA", "MANTENIMIENTO"),
    "Check List Pre Uso": ("MANTENIMIENTO", "NO AFECTA", "OPERACIONES"),
    "Mantenimiento Programado": ("MANTENIMIENTO", "AFECTA", "MANTENIMIENTO"),
    "Falta de Agua": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Falta de Personal": ("STAND BY INOPERATIVO", "AFECTA", "GESTION HUMANA"),
    "Condiciones Climáticas Adversas": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Parada por Seguridad / Bloqueo": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Traslado de Personal": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Parada por Medio Ambiente": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Falta de Insumos / Herramientas": ("STAND BY INOPERATIVO", "AFECTA", "LOGISTICA"),
    "Falta de Frente / Área": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Tiempos Muertos": ("STAND BY INOPERATIVO", "AFECTA", "OPERACIONES"),
    "Charla Integral / Comité / Capacitación": ("OPERATIVO", "NO AFECTA", "OPERACIONES"),
    "Falla Mecánica": ("STAND BY INOPERATIVO", "AFECTA", "MANTENIMIENTO"),
    "Falla Eléctrica": ("STAND BY INOPERATIVO", "AFECTA", "MANTENIMIENTO"),
    "Falla Hidráulica": ("STAND BY INOPERATIVO", "AFECTA", "MANTENIMIENTO"),
    "Esperas Inoperativas": ("STAND BY INOPERATIVO", "AFECTA", "OPERACIONES"),
    "Falla de Accesorios / Herramientas": ("STAND BY INOPERATIVO", "AFECTA", "OPERACIONES"),
    "Falla de Bomba de Agua": ("STAND BY INOPERATIVO", "AFECTA", "OPERACIONES"),
    "Falla de Grupo Electrógeno": ("STAND BY INOPERATIVO", "AFECTA", "OPERACIONES"),
    "Parada Solicitada por Cliente": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Parada por Geología / Supervisión": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Falta de Acceso / Transporte Cliente": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Parada por Comunidad / Social": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
    "Espera de Decisiones del Cliente": ("STAND BY CLIENTE", "AFECTA", "CLIENTE"),
}


def clean_person_name(name: any) -> str:
    if name is None or pd.isna(name):
        return ""
    n = str(name).strip().upper()
    if n in ("", "NAN", "NONE", "NULL", "0", "0.0", "FALSO", "NO"):
        return ""
    nfkd = unicodedata.normalize('NFKD', n)
    n_clean = ''.join(c for c in nfkd if not unicodedata.category(c).startswith('M'))
    n_clean = re.sub(r'[\,\.]', '', n_clean)
    n_clean = re.sub(r'\s+', ' ', n_clean).strip()
    return n_clean


def exportar_esquema_estrella_powerbi(df_det: pd.DataFrame, output_dir: Path):
    """
    Genera el paquete de archivos CSV para Power BI en modo Importación.
    """
    pbi_dir = output_dir / "powerbi_star_schema"
    pbi_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("  GENERANDO ESQUEMA ESTRELLA PARA POWER BI (RESIDENTES.pbix)")
    print("=" * 80, flush=True)

    # 1. Fact_Metraje
    cols_base = ["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR", "SONDAJE", "PERFORISTA", "LINEA"]
    cols_met = [c for c in cols_base if c in df_det.columns]
    
    df_metraje = df_det[cols_met].copy()
    df_metraje.rename(columns={"ID_CLAVE_UNICA": "KEY_OPERACION", "TURNO_ESTANDAR": "TURNO"}, inplace=True)
    df_metraje["METRAJE_X_GUARDIA"] = pd.to_numeric(df_det["METRAJE"], errors="coerce").fillna(0.0).round(2) if "METRAJE" in df_det.columns else 0.0
    df_metraje["Nº_BROCA"] = df_det["Nº BROCA"].fillna("ND").astype(str) if "Nº BROCA" in df_det.columns else "ND"
    df_metraje["SERIE_DE_BROCA"] = df_det["SERIE DE BROCA"].fillna("").astype(str) if "SERIE DE BROCA" in df_det.columns else ""
    df_metraje["MARCA_BROCA"] = df_det["MARCA BROCA"].fillna("").astype(str) if "MARCA BROCA" in df_det.columns else ""
    df_metraje["AYUDANTE_1"] = df_det["AYUDANTE"].map(clean_person_name) if "AYUDANTE" in df_det.columns else ""
    df_metraje["AYUDANTE_2"] = df_det["AYUDANTE 2"].map(clean_person_name) if "AYUDANTE 2" in df_det.columns else ""
    df_metraje["COMENTARIOS"] = df_det["COMENTARIOS"].fillna("").astype(str) if "COMENTARIOS" in df_det.columns else ""
    df_metraje["AÑO"] = pd.to_datetime(df_metraje["FECHA"], errors="coerce").dt.year if "FECHA" in df_metraje.columns else None
    df_metraje["GUARDIAS"] = 1
    
    f_met_path = pbi_dir / "Fact_Metraje.csv"
    df_metraje.to_csv(f_met_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Fact_Metraje.csv: {len(df_metraje):,} filas -> {f_met_path.name}", flush=True)

    # 2. Fact_Tiempos (Unpivot dinámico)
    time_records = []
    for _, row in df_det.iterrows():
        key_op = row.get("ID_CLAVE_UNICA", "")
        fecha = row.get("FECHA", "")
        ctr = row.get("CTR", "")
        maquina = row.get("MAQUINA", "")
        turno = row.get("TURNO_ESTANDAR", "")
        sondaje = row.get("SONDAJE", "")
        perforista = clean_person_name(row.get("PERFORISTA", ""))
        linea = row.get("LINEA", "")
        ay1 = clean_person_name(row.get("AYUDANTE", ""))
        ay2 = clean_person_name(row.get("AYUDANTE 2", ""))
        marca_broca = str(row.get("MARCA BROCA", "") or "")
        comentarios = str(row.get("COMENTARIOS", "") or "")
        año = pd.to_datetime(fecha).year if pd.notna(fecha) else None

        for col_act, (categoria, afecta, resp) in CATALOGO_ACTIVIDADES_DETALLADO.items():
            if col_act in row:
                val = row[col_act]
                try:
                    horas = float(val) if pd.notna(val) else 0.0
                except (ValueError, TypeError):
                    horas = 0.0

                if horas > 0:
                    time_records.append({
                        "KEY_OPERACION": key_op,
                        "FECHA": fecha,
                        "MAQUINA": maquina,
                        "CTR": ctr,
                        "TURNO": turno,
                        "SONDAJE": sondaje,
                        "PERFORISTA": perforista,
                        "LINEA": linea,
                        "AÑO": año,
                        "GUARDIAS": 1,
                        "Actividad": col_act.upper().replace(" ", "_").replace("/", "_"),
                        "Horas": round(horas, 2),
                        "Categoria": categoria,
                        "Afecta_Disp": afecta,
                        "Responsable": resp,
                        "Tipo_Movimiento": "OPERATIVO",
                        "JOIN_KEY_EXCEL": col_act.upper().replace(" ", "_"),
                        "AYUDANTE_1": ay1,
                        "AYUDANTE_2": ay2,
                        "MARCA_BROCA": marca_broca,
                        "COMENTARIOS": comentarios
                    })

    df_tiempos = pd.DataFrame(time_records)
    f_tiempos_path = pbi_dir / "Fact_Tiempos.csv"
    df_tiempos.to_csv(f_tiempos_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Fact_Tiempos.csv: {len(df_tiempos):,} filas unpivoteadas -> {f_tiempos_path.name}", flush=True)

    # 3. Dim_Maquina
    if "MAQUINA" in df_det.columns:
        df_maquinas = df_det[["MAQUINA"]].drop_duplicates().dropna().sort_values("MAQUINA")
    else:
        df_maquinas = pd.DataFrame(columns=["MAQUINA"])
    dim_maq_path = pbi_dir / "Dim_Maquina.csv"
    df_maquinas.to_csv(dim_maq_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Dim_Maquina.csv: {len(df_maquinas):,} máquinas únicas", flush=True)

    # 4. Dim_Personal y Fact_Personal_Asignado (Puente M:M)
    personal_list = []
    puente_list = []
    for _, row in df_det.iterrows():
        key_op = row.get("ID_CLAVE_UNICA", "")
        perf = clean_person_name(row.get("PERFORISTA", ""))
        ay1 = clean_person_name(row.get("AYUDANTE", ""))
        ay2 = clean_person_name(row.get("AYUDANTE 2", ""))

        if perf:
            personal_list.append({"PERFORISTA": perf, "PUESTO": "PERFORISTA"})
            puente_list.append({"KEY_OPERACION": key_op, "ROL_EN_REPORTE": "PERFORISTA", "NOMBRE_TRABAJADOR": perf})
        if ay1:
            personal_list.append({"PERFORISTA": ay1, "PUESTO": "AYUDANTE"})
            puente_list.append({"KEY_OPERACION": key_op, "ROL_EN_REPORTE": "AYUDANTE 1", "NOMBRE_TRABAJADOR": ay1})
        if ay2:
            personal_list.append({"PERFORISTA": ay2, "PUESTO": "AYUDANTE"})
            puente_list.append({"KEY_OPERACION": key_op, "ROL_EN_REPORTE": "AYUDANTE 2", "NOMBRE_TRABAJADOR": ay2})

    df_personal = pd.DataFrame(personal_list).drop_duplicates(subset=["PERFORISTA"]).sort_values("PERFORISTA") if personal_list else pd.DataFrame(columns=["PERFORISTA", "PUESTO"])
    dim_pers_path = pbi_dir / "Dim_Personal.csv"
    df_personal.to_csv(dim_pers_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Dim_Personal.csv: {len(df_personal):,} trabajadores únicos", flush=True)

    df_puente = pd.DataFrame(puente_list).drop_duplicates() if puente_list else pd.DataFrame(columns=["KEY_OPERACION", "ROL_EN_REPORTE", "NOMBRE_TRABAJADOR"])
    fact_puente_path = pbi_dir / "Fact_Personal_Asignado.csv"
    df_puente.to_csv(fact_puente_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Fact_Personal_Asignado.csv: {len(df_puente):,} asignaciones guardia-persona", flush=True)

    # 5. Dim_Sondaje (Acumulados y profundidades)
    if "SONDAJE" in df_det.columns and not df_det.empty:
        agg_kwargs = {}
        if "FECHA" in df_det.columns:
            agg_kwargs["FECHA_INICIO_REAL"] = ("FECHA", "min")
            agg_kwargs["FECHA_FIN_REAL"] = ("FECHA", "max")
        if "METRAJE" in df_det.columns:
            agg_kwargs["AVANCE_ACUMULADO"] = ("METRAJE", "sum")
        if "MAQUINA" in df_det.columns:
            agg_kwargs["MAQUINA_PRINCIPAL"] = ("MAQUINA", "first")
        if "CTR" in df_det.columns:
            agg_kwargs["CTR_A_CARGO"] = ("CTR", "first")
        if "PROFUNDIDAD DE SONDAJE" in df_det.columns:
            agg_kwargs["PROFUNDIDAD_PROGRAMADA"] = ("PROFUNDIDAD DE SONDAJE", "max")

        if agg_kwargs:
            df_sond = df_det.groupby("SONDAJE").agg(**agg_kwargs).reset_index()
        else:
            df_sond = df_det[["SONDAJE"]].drop_duplicates()

        if "CTR_A_CARGO" not in df_sond.columns:
            df_sond["CTR_A_CARGO"] = "ND"
        df_sond["SONDAJE"] = df_sond["SONDAJE"].astype(str)
        df_sond["CTR_A_CARGO"] = df_sond["CTR_A_CARGO"].astype(str)
        df_sond["Etiqueta_Gantt"] = df_sond["SONDAJE"] + " (" + df_sond["CTR_A_CARGO"] + ")"
    else:
        df_sond = pd.DataFrame(columns=["SONDAJE", "FECHA_INICIO_REAL", "FECHA_FIN_REAL", "AVANCE_ACUMULADO", "MAQUINA_PRINCIPAL", "CTR_A_CARGO", "PROFUNDIDAD_PROGRAMADA", "Etiqueta_Gantt"])
    dim_sond_path = pbi_dir / "Dim_Sondaje.csv"
    df_sond.to_csv(dim_sond_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Dim_Sondaje.csv: {len(df_sond):,} sondajes catalogados", flush=True)

    # 6. Dim_CTR
    ctr_cols = [c for c in ["CTR", "ZONA"] if c in df_det.columns]
    if ctr_cols:
        df_ctr = df_det[ctr_cols].drop_duplicates().dropna().sort_values("CTR" if "CTR" in ctr_cols else ctr_cols[0])
    else:
        df_ctr = pd.DataFrame(columns=["CTR", "ZONA"])
    dim_ctr_path = pbi_dir / "Dim_CTR.csv"
    df_ctr.to_csv(dim_ctr_path, index=False, encoding="utf-8-sig")
    print(f"  [OK] Dim_CTR.csv: {len(df_ctr):,} centros de trabajo", flush=True)

    print("=" * 80)
    print(f"  [OK] ESQUEMA ESTRELLA COMPLETO EXPORTADO EN: {pbi_dir}")
    print("=" * 80 + "\n", flush=True)
