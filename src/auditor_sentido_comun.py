"""
Módulo de Auditoría de Sentido Común y Conciliación 1-a-1
Rockdrill Group - Sistema de Calidad y Gobierno de Datos
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

# Forzar UTF-8 en salida estándar de Windows
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

class AuditorSentidoComun:
    """
    Auditor riguroso que cuestiona sistemáticamente los resultados de conciliación
    y verifica el cumplimiento del banco de pruebas canónico (Benchmark de Verificación).
    """
    def __init__(
        self,
        ruta_detallados: str = "output/detallados_consolidados.xlsx",
        ruta_ci: str = "output/control_interno/control_interno_compilado.xlsx",
        ruta_matriz: str = "output/matriz_comparativa_metrajes.xlsx"
    ):
        self.ruta_det = Path(ruta_detallados).resolve()
        self.ruta_ci = Path(ruta_ci).resolve()
        
        # Fallback a matriz actualizada si la principal estaba bloqueada
        mat_path = Path(ruta_matriz).resolve()
        mat_alt = mat_path.parent / "matriz_comparativa_metrajes_actualizada.xlsx"
        if mat_alt.exists() and mat_alt.stat().st_mtime > mat_path.stat().st_mtime:
            self.ruta_matriz = mat_alt
        else:
            self.ruta_matriz = mat_path
            
        self.alertas: List[Dict[str, Any]] = []

    def ejecutar_auditoria_completa(self) -> Dict[str, Any]:
        """
        Ejecuta todas las pruebas de sentido común y validación cuantitativa.
        """
        print("=" * 80)
        print("🔍 INICIANDO AUDITORÍA DE SENTIDO COMÚN (AUDIT_COMMON_SENSE_AGENT)")
        print(f"📁 Archivo de Matriz Auditado: {self.ruta_matriz.name}")
        print("=" * 80)
        
        veredicto = {
            "estado_general": "PENDIENTE",
            "benchmark_americana_xrd50u002": False,
            "benchmark_americana_xrd50uss001": False,
            "tasa_coincidencia_exacta": 0.0,
            "total_claves_evaluadas": 0,
            "alertas_criticas": []
        }

        if not self.ruta_matriz.exists():
            print(f"❌ No se encontró la matriz de conciliación en {self.ruta_matriz}")
            veredicto["estado_general"] = "ERROR_MATRIZ_INEXISTENTE"
            return veredicto

        try:
            df_mat = pd.read_excel(self.ruta_matriz, sheet_name=None)
        except Exception as e:
            print(f"❌ Error al abrir matriz de conciliación: {e}")
            veredicto["estado_general"] = "ERROR_LECTURA_EXCEL"
            return veredicto

        sheet_name = "Alertas_y_Discrepancias" if "Alertas_y_Discrepancias" in df_mat else list(df_mat.keys())[0]
        df_disc = df_mat[sheet_name]

        print(f"📋 Analizando hoja: {sheet_name} ({len(df_disc)} filas)")

        # 1. Benchmark AMERICANA / XRD50U-002 (Debe ser 100% exacto)
        df_ame_002 = df_disc[df_disc["MAQUINA"].astype(str).str.contains("XRD50U-002", case=False, na=False)]
        if df_ame_002.empty:
            print("  ✅ AMERICANA / XRD50U-002: 0 discrepancias registradas (Cuadratura 100.00% confirmada al milímetro).")
            veredicto["benchmark_americana_xrd50u002"] = True
        else:
            diff_002 = df_ame_002["DIFERENCIA"].abs().sum()
            if diff_002 == 0.0:
                print("  ✅ AMERICANA / XRD50U-002: Coincidencia exacta al milímetro (0.00 m).")
                veredicto["benchmark_americana_xrd50u002"] = True
            else:
                print(f"  ❌ ALERTA: AMERICANA / XRD50U-002 presenta diferencias no esperadas: {diff_002:.2f}m")
                veredicto["alertas_criticas"].append(f"XRD50U-002 falló benchmark con diff={diff_002:.2f}m")

        # 2. Benchmark AMERICANA / XRD50USS-001 (Debe registrar la omisión de 35m)
        df_ame_001 = df_disc[df_disc["MAQUINA"].astype(str).str.contains("XRD50USS-001", case=False, na=False)]
        omision_detectada = False
        for _, r in df_ame_001.iterrows():
            diff_val = abs(float(r.get("DIFERENCIA", 0.0)))
            if abs(diff_val - 35.0) < 0.1:
                omision_detectada = True
                print(f"  ✅ AMERICANA / XRD50USS-001: Omisión real de 35.00m detectada y aislada correctamente en fecha {r.get('FECHA')}.")
                break
                
        if omision_detectada:
            veredicto["benchmark_americana_xrd50uss001"] = True
        else:
            print("  ⚠️ AMERICANA / XRD50USS-001: No se identificó la discrepancia exacta de 35m de campo.")
            veredicto["alertas_criticas"].append("XRD50USS-001 no reflejó la omisión exacta de 35m")

        # 3. Veredicto Final
        if veredicto["benchmark_americana_xrd50u002"] and veredicto["benchmark_americana_xrd50uss001"]:
            veredicto["estado_general"] = "APROBADO_CON_CUADRATURA_COMPROBADA"
        elif veredicto["benchmark_americana_xrd50u002"]:
            veredicto["estado_general"] = "APROBADO_CON_OBSERVACIONES_AISLADAS"
        else:
            veredicto["estado_general"] = "RECHAZADO"

        print("=" * 80)
        print(f"🏁 RESULTADO DE AUDITORÍA: {veredicto['estado_general']}")
        print("=" * 80)
        return veredicto

if __name__ == "__main__":
    auditor = AuditorSentidoComun()
    res = auditor.ejecutar_auditoria_completa()
