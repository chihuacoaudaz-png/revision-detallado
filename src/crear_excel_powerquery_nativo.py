"""
Script Oficial Definitivo: Generación de Excel con Power Query M Nativo y Base de Datos Completa (168 Columnas)
Rockdrill Group - Sistema de Consolidación Operativa
"""
import os
import sys
from pathlib import Path

# Ajustar sys.path para importación modular
ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Forzar UTF-8
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import pandas as pd
from src.etl_detallados import COLS_OFICIALES_168

def generar_excel_powerquery_completo(
    output_path: str = r"C:\Proyectos Python\Detallados\output\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
    ruta_base: str = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones",
    datos_consolidados_path: str = r"C:\Proyectos Python\Detallados\output\detallados_consolidados.xlsx"
):
    import win32com.client
    
    print("=" * 80)
    print("🚀 GENERANDO LIBRO OFICIAL EXCEL CON POWER QUERY M NATIVO (168 COLUMNAS)")
    print(f"📁 Destino: {output_path}")
    print(f"📁 Origen de Datos: {ruta_base}")
    print("=" * 80)

    output_file = Path(output_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Cargar o generar datos consolidados completos (168 columnas canónicas + metadatos)
    print("  [1/4] Preparando base de datos consolidada (168 columnas)...")
    if os.path.exists(datos_consolidados_path):
        df_src = pd.read_excel(datos_consolidados_path)
    else:
        from src.etl_detallados import run_etl_detallados
        from config import BASE_PATH, MAESTRO_PATH, HOJAS_EXCLUIDAS, CTRS_EXCLUIDOS
        df_src = run_etl_detallados(BASE_PATH, MAESTRO_PATH, HOJAS_EXCLUIDAS, CTRS_EXCLUIDOS)
        df_src.to_excel(datos_consolidados_path, index=False)

    # Formatear fecha
    if "FECHA" in df_src.columns:
        df_src["FECHA"] = pd.to_datetime(df_src["FECHA"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Guardar archivo inicial temporal
    temp_excel = output_file.parent / "temp_consolidador.xlsx"
    with pd.ExcelWriter(temp_excel, engine="openpyxl") as writer:
        df_src.to_excel(writer, sheet_name="CONSOLIDADO_DETALLADOS", index=False)

    print(f"  [2/4] Base de datos estructurada: {len(df_src)} filas x {len(df_src.columns)} columnas.")

    # 2. Inyectar Consultas y Parámetros Nativos de Power Query mediante COM
    print("  [3/4] Inyectando Parámetros y Consultas M en el catálogo Mashup de Excel...")
    
    m_column_renames = []
    for i, col in enumerate(COLS_OFICIALES_168):
        safe_col = col.replace('"', '""')
        m_column_renames.append(f'        {{"Column{i+1}", "{safe_col}"}}')
    m_renames_str = ",\n".join(m_column_renames)

    m_fn_procesar = f"""let
    fn_ProcesarHojaDetallado = (hojaTabla as table, nombreHoja as text, ctrNombre as text) as table =>
    let
        Procesado = try
            let
                FilasDatos = Table.Skip(hojaTabla, 24),
                ColNames = Table.ColumnNames(FilasDatos),
                Cols168Names = List.FirstN(ColNames, 168),
                Tabla168Cols = Table.SelectColumns(FilasDatos, Cols168Names, MissingField.Ignore),
                RenombrarCols = Table.RenameColumns(Tabla168Cols, {{
{m_renames_str}
                }}, MissingField.Ignore),
                FechaLlenada = Table.FillDown(RenombrarCols, {{"FECHA"}}),
                ColSondaje = if Table.HasColumns(FechaLlenada, {{"SONDAJE"}}) then "SONDAJE" else "NOMBRE",
                SondajeLlenado = if Table.HasColumns(FechaLlenada, {{ColSondaje}}) then 
                    Table.FillUp(Table.FillDown(FechaLlenada, {{ColSondaje}}), {{ColSondaje}})
                else 
                    FechaLlenada,
                FilasOperativas = Table.SelectRows(SondajeLlenado, each 
                    [FECHA] <> null and 
                    Text.Trim(Text.From([FECHA])) <> "" and 
                    not Text.Contains(Text.Upper(Text.From([FECHA])), "TOTAL") and 
                    not Text.Contains(Text.Upper(Text.From([FECHA])), "RESUMEN") and
                    not Text.StartsWith(Text.Trim(Text.From(Record.FieldOrDefault(_, ColSondaje, ""))), ">") and
                    not List.Contains({{"TOTAL", "TOTAL GENERAL", "RESUMEN", "PROMEDIO", "SUMA", "TOTAL AVANCE"}}, Text.Upper(Text.Trim(Text.From(Record.FieldOrDefault(_, ColSondaje, "")))))
                ),
                ConCTR = Table.AddColumn(FilasOperativas, "CTR", each ctrNombre, type text),
                ConMaquina = Table.AddColumn(ConCTR, "MAQUINA", each nombreHoja, type text),
                ReordenarMetadatos = Table.ReorderColumns(ConMaquina, {{"CTR", "MAQUINA"}} & List.RemoveItems(Table.ColumnNames(ConMaquina), {{"CTR", "MAQUINA"}}))
            in
                ReordenarMetadatos
        otherwise
            #table({{"CTR", "MAQUINA", "FECHA"}}, {{}})
    in
        Procesado
in
    fn_ProcesarHojaDetallado"""

    m_consolidado = """let
    Origen = if TipoOrigen = "LOCAL" then
        Folder.Files(RutaOrigenLocal)
    else
        SharePoint.Files(UrlSharePoint, [ApiVersion = 15]),
        
    FiltrarRuta = Table.SelectRows(Origen, each Text.Contains([Folder Path], "CTR_") and Text.Contains([Folder Path], "02_Detallado")),
    ExcluirExcluidos = Table.SelectRows(FiltrarRuta, each not Text.Contains(Text.Upper([Folder Path]), "COLQUIJIRCA")),
    FiltrarExcel = Table.SelectRows(ExcluirExcluidos, each (Text.EndsWith([Name], ".xlsx") or Text.EndsWith([Name], ".xlsm")) and not Text.StartsWith([Name], "~$")),
    
    AgregarCTR = Table.AddColumn(FiltrarExcel, "CTR_Nombre", each 
        let 
            partes = Text.Split([Folder Path], "\\"),
            ctrFolder = List.Select(partes, each Text.StartsWith(Text.Upper(_), "CTR_")),
            cleanName = if List.IsEmpty(ctrFolder) then "CTR_DESCONOCIDO" else Text.Replace(ctrFolder{0}, "CTR_", "")
        in 
            cleanName, type text
    ),
    
    LeerLibros = Table.AddColumn(AgregarCTR, "DatosLibro", each Excel.Workbook([Content], null, true)),
    ExpandirHojas = Table.ExpandTableColumn(LeerLibros, "DatosLibro", {"Name", "Kind", "Hidden", "Data"}, {"Sheet_Name", "Kind", "Hidden", "Data"}),
    FiltrarHojas = Table.SelectRows(ExpandirHojas, each [Kind] = "Sheet" and [Hidden] = false and not List.Contains({"ADITIVOS", "GENERAL", "LISTAS", "TIEMPOS", "RESUMEN", "GRAFICOS", "MAESTRO", "PARAMETROS", "GLOSARIO"}, Text.Upper([Sheet_Name]))),
    ProcesarHojas = Table.AddColumn(FiltrarHojas, "ContenidoProcesado", each fn_ProcesarHojaDetallado([Data], [Sheet_Name], [CTR_Nombre])),
    TablasValidas = List.Select(ProcesarHojas[ContenidoProcesado], each Value.Is(_, type table) and not Table.IsEmpty(_)),
    TablaConsolidada = Table.Combine(TablasValidas)
in
    TablaConsolidada"""

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(str(temp_excel))
        ws = wb.Sheets("CONSOLIDADO_DETALLADOS")

        # Crear ListObject (Tabla oficial de Excel) sobre la totalidad de columnas
        last_row = len(df_src) + 1
        last_col = len(df_src.columns)
        rng = ws.Range(ws.Cells(1, 1), ws.Cells(last_row, last_col))
        tbl = ws.ListObjects.Add(1, rng, None, 1) # 1 = xlSrcRange
        tbl.Name = "Tabla_Consolidado_Detallados"
        tbl.TableStyle = "TableStyleMedium9"

        # Inyectar Parámetros Power Query
        m_ruta_origen = f'"{ruta_base}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
        wb.Queries.Add("RutaOrigenLocal", m_ruta_origen, "Ruta local de la carpeta de operaciones")

        m_tipo_origen = '"LOCAL" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
        wb.Queries.Add("TipoOrigen", m_tipo_origen, "Conmutador de origen (LOCAL o CLOUD)")

        m_url_sp = '"https://rockdrillgroup.sharepoint.com/sites/Operaciones/Rockdrill_Control_Operaciones" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]'
        wb.Queries.Add("UrlSharePoint", m_url_sp, "URL de SharePoint para producción en la nube")

        # Inyectar Función Transformadora M
        wb.Queries.Add("fn_ProcesarHojaDetallado", m_fn_procesar, "Procesador modular de 168 columnas de detallado")

        # Inyectar Consulta Consolidadora M Completa
        wb.Queries.Add("Consolidado_Detallados", m_consolidado, "Consulta consolidada completa de reportes detallados (168 columnas)")

        print("  [4/4] Guardando libro final...")
        wb.SaveAs(str(output_file), 51)
        wb.Close(False)

        # Eliminar temporal
        if temp_excel.exists():
            temp_excel.unlink()

        print("=" * 80)
        print(f"✅ EXCEL CON BASE DE DATOS COMPLETA (168 COLS) Y POWER QUERY GENERADO EN:\n   {output_file}")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ Error en COM: {e}")
        return False
    finally:
        excel.Quit()

if __name__ == "__main__":
    generar_excel_powerquery_completo()
