"""
Script de inyección y depuración de M con actualización por conexión individual
"""
import win32com.client
from pathlib import Path
import time

file_path = Path(r"c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\bbdd.xlsx").resolve()

def update_and_refresh_m(m_detallados: str, m_consolidado: str, m_discrepancias: str):
    print("=" * 80)
    print(f"Inyectando código M en {file_path.name}...")
    print("=" * 80)
    
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    
    try:
        wb = excel.Workbooks.Open(str(file_path))
        
        # 1. Inyectar en Detallados_BD
        q_det = wb.Queries.Item("Detallados_BD")
        q_det.Formula = m_detallados
        print("[OK] Detallados_BD M inyectado.")
        
        # 2. Inyectar en Consolidado_BD
        q_ci = wb.Queries.Item("Consolidado_BD")
        q_ci.Formula = m_consolidado
        print("[OK] Consolidado_BD M inyectado.")
        
        # 3. Inyectar en Discrepancias_BD
        q_disc = wb.Queries.Item("Discrepancias_BD")
        q_disc.Formula = m_discrepancias
        print("[OK] Discrepancias_BD M inyectado.")
        
        # Desactivar BackgroundQuery en todas las conexiones para forzar ejecución síncrona
        for i in range(1, wb.Connections.Count + 1):
            conn = wb.Connections.Item(i)
            try:
                if conn.Type in (1, 2, 7): # OLEDB/ODBC/Model
                    conn.OLEDBConnection.BackgroundQuery = False
            except Exception:
                pass

        # Refrescar conexiones individualmente
        print("\nRefrescando conexiones secuencialmente...")
        for i in range(1, wb.Connections.Count + 1):
            conn = wb.Connections.Item(i)
            print(f"  Refrescando Conexión {i}: [{conn.Name}]...")
            t0 = time.time()
            try:
                conn.Refresh()
                t1 = time.time()
                print(f"    [OK] Conexión [{conn.Name}] actualizada en {t1 - t0:.2f} s")
            except Exception as e:
                print(f"    [ERROR] Falló actualización de [{conn.Name}]: {e}")

        # Inspeccionar la hoja Discrepancias_BD
        ws_disc = wb.Worksheets("Discrepancias_BD")
        tbl_disc = ws_disc.ListObjects("Discrepancias_BD")
        rowCount = tbl_disc.ListRows.Count
        
        print(f"\n==================================================")
        print(f"RESULTADO FINAL: {rowCount} filas en tabla Discrepancias_BD")
        print(f"==================================================")
        
        if rowCount > 0:
            headers = [col.Name for col in tbl_disc.ListColumns]
            print(f"Columnas: {headers}\n")
            print("Filas de discrepancias registradas:")
            for r_idx in range(1, rowCount + 1):
                row_vals = [tbl_disc.DataBodyRange.Cells(r_idx, c_idx).Value for c_idx in range(1, len(headers) + 1)]
                print(f"  Fila {r_idx}: {row_vals}")
        else:
            print("🎉 ¡ÉXITO TOTAL! 0 DISCREPANCIAS ENCONTRADAS EN LA TABLA M DE EXCEL 🎉")
            
        wb.Save()
        wb.Close(True)
        print("\n[OK] Archivo guardado y cerrado correctamente.")
        return rowCount
    finally:
        excel.Quit()
