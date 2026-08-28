"""
Módulo de Reconciliación y Matriz Comparativa de Metrajes
=========================================================
Realiza el cruce 'Full Outer Join' entre los metrajes de los Reportes Detallados
y el Consolidado de Control Interno por ID_CLAVE_UNICA ({FECHA}-{MAQUINA}-{TURNO}).
Genera:
  1. Matriz completa de auditoría por clave.
  2. Subconjunto filtrado de discrepancias reales (> 0.01 m).
  3. Resumen acumulado de metraje y diferencias por Contrato Minero (CTR).
"""

from pathlib import Path
from typing import Optional, Tuple, Union
import pandas as pd


def clasificar_discrepancia(
    dif: float,
    det: float,
    ci: float,
    is_intercambio_turno: bool
) -> str:
    """
    Clasifica un registro individual en una de las 5 categorías oficiales acordadas:
      - 'Sin Discrepancia': |DIFERENCIA| <= 0.01m
      - 'Intercambio de Turno (Suma Diaria Idéntica)': Misma CTR, máquina y fecha con diferencia neta 0.00m
      - 'Faltante de Correo en Origen': Detallado ausente/0m pero presente en Control Interno (ej. correos no recibidos)
      - 'Sondaje Paralelo / Cero Histórico en Control Interno': Detallado con avance pero CI ausente/0m
      - 'Ajuste Retroactivo de Administradora / Variación Decimal': Variación decimal menor o ajustes retroactivos
    """
    if abs(dif) <= 0.01:
        return "Sin Discrepancia"
    if is_intercambio_turno:
        return "Intercambio de Turno (Suma Diaria Idéntica)"
    if det <= 0.01 and ci > 0.01:
        return "Faltante de Correo en Origen"
    if det > 0.01 and ci <= 0.01:
        return "Sondaje Paralelo / Cero Histórico en Control Interno"
    return "Ajuste Retroactivo de Administradora / Variación Decimal"


def reconciliar_metrajes(
    df_det: pd.DataFrame,
    df_ci: pd.DataFrame,
    output_path: Optional[Union[Path, str]] = None,
    fecha_corte: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cruza los datos de Detallados y Control Interno, clasifica las discrepancias operativas,
    genera la matriz comparativa y exporta a Excel en las hojas Conciliacion_Completa,
    Discrepancias y Resumen_Por_CTR.
    """
    if df_det.empty or df_ci.empty:
        print("  [AVISO] No se puede conciliar: falta datos de Detallados o Control Interno.", flush=True)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Acotar Detallados y Control Interno al rango de fechas evaluado
    min_date = df_ci["FECHA"].min()
    max_date = fecha_corte if fecha_corte else df_ci["FECHA"].max()
    
    if pd.notna(min_date) and pd.notna(max_date):
        df_det = df_det[(df_det["FECHA"] >= min_date) & (df_det["FECHA"] <= max_date)].copy()
        df_ci = df_ci[(df_ci["FECHA"] >= min_date) & (df_ci["FECHA"] <= max_date)].copy()

    det_sum = df_det.groupby(["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"])["METRAJE"].sum().reset_index()
    det_sum.rename(columns={"METRAJE": "METRAJE_DETALLADO"}, inplace=True)

    ci_sum = df_ci.groupby(["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"])["METRAJE_CI"].sum().reset_index()

    comp = pd.merge(
        det_sum, ci_sum,
        on=["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"],
        how="outer"
    ).fillna(0.0)

    comp["METRAJE_DETALLADO"] = comp["METRAJE_DETALLADO"].round(2)
    comp["METRAJE_CI"] = comp["METRAJE_CI"].round(2)
    comp["DIFERENCIA"] = (comp["METRAJE_DETALLADO"] - comp["METRAJE_CI"]).round(2)

    # Auto-resolución dictada por usuario: Si la suma diaria coincide (dif_diaria == 0) pero
    # hay diferencias por turno, se asume que la distribución correcta es la de CI (resolución de swap).
    sum_det_diaria = comp.groupby(["FECHA", "CTR", "MAQUINA"])["METRAJE_DETALLADO"].transform("sum")
    sum_ci_diaria = comp.groupby(["FECHA", "CTR", "MAQUINA"])["METRAJE_CI"].transform("sum")
    dif_diaria = (sum_det_diaria - sum_ci_diaria).round(2)
    
    is_intercambio = (dif_diaria.abs() <= 0.01) & (comp["DIFERENCIA"].abs() > 0.01)
    
    # Pre-clasificamos
    comp["CAUSA_DISCREPANCIA"] = [
        clasificar_discrepancia(d, m_det, m_ci, False)
        for d, m_det, m_ci in zip(
            comp["DIFERENCIA"],
            comp["METRAJE_DETALLADO"],
            comp["METRAJE_CI"]
        )
    ]
    
    # Auto-resolución dictada por usuario
    if is_intercambio.any():
        comp.loc[is_intercambio, "CAUSA_DISCREPANCIA"] = "Intercambio de Turno (Auto-Resuelto a CI)"
        comp.loc[is_intercambio, "METRAJE_DETALLADO"] = comp.loc[is_intercambio, "METRAJE_CI"]
        comp.loc[is_intercambio, "DIFERENCIA"] = 0.0

    # Filtrar solo lo que sea diferente o auto-resuelto (para no desperdiciar recursos con lo que ya está igual)
    discrepancias_y_forzados = comp[(comp["DIFERENCIA"].abs() > 0.01) | (comp["CAUSA_DISCREPANCIA"] == "Intercambio de Turno (Auto-Resuelto a CI)")].copy()

    resumen_ctr = comp.groupby("CTR").agg(
        METRAJE_DETALLADO=("METRAJE_DETALLADO", "sum"),
        METRAJE_CI=("METRAJE_CI", "sum"),
        DIFERENCIA=("DIFERENCIA", "sum"),
        TOTAL_CLAVES=("ID_CLAVE_UNICA", "count"),
        COINCIDENCIAS=("DIFERENCIA", lambda s: (s.abs() <= 0.01).sum()),
        DISCREPANCIAS=("DIFERENCIA", lambda s: (s.abs() > 0.01).sum())
    ).reset_index()
    resumen_ctr["METRAJE_DETALLADO"] = resumen_ctr["METRAJE_DETALLADO"].round(2)
    resumen_ctr["METRAJE_CI"] = resumen_ctr["METRAJE_CI"].round(2)
    resumen_ctr["DIFERENCIA"] = resumen_ctr["DIFERENCIA"].round(2)
    resumen_ctr["PORCENTAJE_COINCIDENCIA"] = ((resumen_ctr["COINCIDENCIAS"] / resumen_ctr["TOTAL_CLAVES"]) * 100).round(2)

    # Exportación oficial si se proporciona ruta
    if output_path is not None:
        target = Path(output_path)
        matriz_file = target if target.suffix == ".xlsx" else target / "matriz_comparativa_metrajes.xlsx"
        matriz_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with pd.ExcelWriter(str(matriz_file), engine="openpyxl") as writer:
                discrepancias_y_forzados.to_excel(writer, sheet_name="Alertas_y_Discrepancias", index=False)
                resumen_ctr.to_excel(writer, sheet_name="Resumen_Por_CTR", index=False)
        except PermissionError:
            fallback_file = matriz_file.parent / f"{matriz_file.stem}_actualizada.xlsx"
            print(f"  [AVISO] '{matriz_file.name}' está abierto en Excel. Guardando copia en '{fallback_file.name}'", flush=True)
            with pd.ExcelWriter(str(fallback_file), engine="openpyxl") as writer:
                discrepancias_y_forzados.to_excel(writer, sheet_name="Alertas_y_Discrepancias", index=False)
                resumen_ctr.to_excel(writer, sheet_name="Resumen_Por_CTR", index=False)

    return comp, discrepancias_y_forzados, resumen_ctr

# Alias para retrocompatibilidad
run_conciliacion = reconciliar_metrajes

