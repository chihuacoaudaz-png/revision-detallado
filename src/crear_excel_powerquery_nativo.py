"""
Script Oficial Definitivo: Generación de Excel con Power Query M Nativo y Datos Iniciales
Foco Estratégico Exclusivo: Horas y Metros de Perforación
Rockdrill Group
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Forzar UTF-8
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

def generar_excel_powerquery_completo(
    output_path: str = r"C:\Proyectos Python\Detallados\output\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
    ruta_base: str = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones",
    datos_consolidados_path: str = r"C:\Proyectos Python\Detallados\output\detallados_consolidados.xlsx"
):
    import win32com.client
    
    print("=" * 80)
    print("🚀 GENERANDO LIBRO OFICIAL EXCEL CON POWER QUERY M NATIVO")
    print(f"📁 Destino: {output_path}")
    print(f"📁 Origen de Datos: {ruta_base}")
    print("=" * 80)

    output_file = Path(output_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Cargar datos consolidados iniciales enfocados estrictamente en HORAS Y METROS
    print("  [1/4] Preparando datos iniciales de Horas y Metros...")
    df_src = pd.read_excel(datos_consolidados_path)
    
    # Columnas core de horas y metros
    cols_interes = [
        "CTR", "MAQUINA", "FECHA", "TURNO (A=1;B=2)", "GRUPO", "SONDAJE", 
        "DESDE", "HASTA", "METRAJE", "PERFORACION", "TOTAL MANTTO.", 
        "TOTAL STAND BY OPERATIVO", "TOTAL STAND BY INOPERATIVO", 
        "TOTAL STAND BY CLIENTE", "TOTAL OPERATIVO", "TOTAL INOPERATIVO", "TOTAL"
    ]
    cols_existentes = [c for c in cols_interes if c in df_src.columns]
    df_horas_metros = df_src[cols_existentes].copy()

    # Formatear fecha
    if "FECHA" in df_horas_metros.columns:
        df_horas_metros["FECHA"] = pd.to_datetime(df_horas_metros["FECHA"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Guardar archivo inicial con openpyxl / pandas
    temp_excel = output_file.parent / "temp_consolidador.xlsx"
    with pd.ExcelWriter(temp_excel, engine="openpyxl") as writer:
        df_horas_metros.to_excel(writer, sheet_name="CONSOLIDADO_HORAS_METROS", index=False)

    print(f"  [2/4] Datos estructurados: {len(df_horas_metros)} filas x {len(cols_existentes)} columnas.")

    # 2. Inyectar Consultas y Parámetros Nativos de Power Query mediante COM
    print("  [3/4] Inyectando Parámetros y Consultas M en el catálogo Mashup de Excel...")
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(str(temp_excel))
        ws = wb.Sheets("CONSOLIDADO_HORAS_METROS")

        # Crear ListObject (Tabla oficial) sobre los datos
        last_row = len(df_horas_metros) + 1
        last_col = len(cols_existentes)
        rng = ws.Range(ws.Cells(1, 1), ws.Cells(last_row, last_col))
        tbl = ws.ListObjects.Add(1, rng, None, 1) # 1 = xlSrcRange
        tbl.Name = "Tabla_Consolidado_Horas_Metros"
        tbl.TableStyle = "TableStyleMedium9"

        # Inyectar Parámetros Power Query
        m_ruta_origen = f'"{ruta_base}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
        wb.Queries.Add("RutaOrigenLocal", m_ruta_origen, "Ruta local de la carpeta de operaciones")

        m_tipo_origen = '"LOCAL" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
        wb.Queries.Add("TipoOrigen", m_tipo_origen, "Conmutador de origen (LOCAL o CLOUD)")

        m_url_sp = '"https://rockdrillgroup.sharepoint.com/sites/Operaciones/Rockdrill_Control_Operaciones" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]'
        wb.Queries.Add("UrlSharePoint", m_url_sp, "URL de SharePoint para producción en la nube")

        # Inyectar Función Transformadora M
        m_fn_procesar = """let
    fn_ProcesarHojaDetallado = (contenidoBinario as binary, nombreHoja as text, ctrNombre as text) as table =>
    let
        Workbook = Excel.Workbook(contenidoBinario, null, true),
        HojaData = Workbook{[Item=nombreHoja, Kind="Sheet"]}[Data],
        TablaBase = Table.Skip(HojaData, 22),
        Titulos23 = Record.FieldValues(TablaBase{0}),
        Titulos24 = Record.FieldValues(TablaBase{1}),
        
        TitulosLlenos = List.Accumulate(Titulos23, {}, (state, current) =>
            let
                clean = Text.Trim(Text.From(current ?? "")),
                lastVal = if List.IsEmpty(state) then "XP" else List.Last(state),
                newVal = if clean <> "" then clean else lastVal
            in
                state & {newVal}
        ),
        
        EncabezadosCombinados = List.Transform(List.Zip({TitulosLlenos, Titulos24}), each 
            let
                t1 = _{0},
                t2 = Text.Trim(Text.From(_{1} ?? ""))
            in
                if t1 = "XP" then (if t2 <> "" then t2 else "XP")
                else if t2 = "" then t1
                else t1 & "_" & t2
        ),
        
        EncabezadosUnicos = List.Accumulate(EncabezadosCombinados, {}, (state, current) =>
            let
                count = List.Count(List.Select(state, each _ = current or Text.StartsWith(_, current & "_"))),
                name = if count = 0 then current else current & "_" & Text.From(count)
            in
                state & {name}
        ),
        
        DatosSinEncabezados = Table.Skip(TablaBase, 2),
        TablaConHeaders = Table.RenameColumns(DatosSinEncabezados, List.Zip({Table.ColumnNames(DatosSinEncabezados), EncabezadosUnicos})),
        Col0 = Table.ColumnNames(TablaConHeaders){0},
        TablaConFecha = Table.RenameColumns(TablaConHeaders, {{Col0, "FECHA"}}),
        FechaLlenada = Table.FillDown(TablaConFecha, {"FECHA"}),
        FilasOperativas = Table.SelectRows(FechaLlenada, each [FECHA] <> null and [FECHA] <> "" and not Text.Contains(Text.Upper(Text.From([FECHA])), "TOTAL") and not Text.Contains(Text.Upper(Text.From([FECHA])), "RESUMEN")),
        ConCTR = Table.AddColumn(FilasOperativas, "CTR", each ctrNombre, type text),
        ConMaquina = Table.AddColumn(ConCTR, "MAQUINA", each nombreHoja, type text)
    in
        ConMaquina
in
    fn_ProcesarHojaDetallado"""
        wb.Queries.Add("fn_ProcesarHojaDetallado", m_fn_procesar, "Procesador modular de hojas de detallado")

        # Inyectar Consulta Consolidadora M
        m_consolidado = """let
    Origen = if TipoOrigen = "LOCAL" then
        Folder.Files(RutaOrigenLocal)
    else
        SharePoint.Files(UrlSharePoint, [ApiVersion = 15]),
        
    FiltrarRuta = Table.SelectRows(Origen, each Text.Contains([Folder Path], "CTR_") and Text.Contains([Folder Path], "02_Detallado")),
    ExcluirColquijirca = Table.SelectRows(FiltrarRuta, each not Text.Contains(Text.Upper([Folder Path]), "COLQUIJIRCA")),
    FiltrarExcel = Table.SelectRows(ExcluirColquijirca, each Text.EndsWith([Name], ".xlsx") and not Text.StartsWith([Name], "~$")),
    
    AgregarCTR = Table.AddColumn(FiltrarExcel, "CTR_Nombre", each 
        let 
            partes = Text.Split([Folder Path], "\\"),
            ctrFolder = List.Select(partes, each Text.StartsWith(_, "CTR_")){0},
            cleanName = Text.Replace(ctrFolder, "CTR_", "")
        in 
            cleanName, type text
    ),
    
    LeerLibros = Table.AddColumn(AgregarCTR, "DatosLibro", each Excel.Workbook([Content], null, true)),
    ExpandirHojas = Table.ExpandTableColumn(LeerLibros, "DatosLibro", {"Name", "Kind", "Hidden"}, {"Sheet_Name", "Kind", "Hidden"}),
    FiltrarHojas = Table.SelectRows(ExpandirHojas, each [Kind] = "Sheet" and [Hidden] = false and not List.Contains({"ADITIVOS", "GENERAL", "LISTAS", "Tiempos", "RESUMEN", "GRAFICOS", "MAESTRO"}, [Sheet_Name])),
    ProcesarHojas = Table.AddColumn(FiltrarHojas, "ContenidoProcesado", each fn_ProcesarHojaDetallado([Content], [Sheet_Name], [CTR_Nombre])),
    TablasValidas = List.Select(ProcesarHojas[ContenidoProcesado], each Value.Is(_, type table)),
    TablaConsolidada = Table.Combine(TablasValidas),
    ColumnasRelevantes = Table.SelectColumns(TablaConsolidada, {"CTR", "MAQUINA", "FECHA", "SONDAJE", "DESDE", "HASTA", "METRAJE", "TURNO (A=1;B=2)", "PERFORACION", "TOTAL MANTTO.", "TOTAL STAND BY OPERATIVO", "TOTAL STAND BY INOPERATIVO", "TOTAL STAND BY CLIENTE", "TOTAL OPERATIVO", "TOTAL INOPERATIVO", "TOTAL"}, MissingField.Ignore)
in
    ColumnasRelevantes"""
        wb.Queries.Add("Consolidado_Horas_y_Metros", m_consolidado, "Consulta consolidada de horas y metros de perforación")

        print("  [4/4] Guardando libro final...")
        wb.SaveAs(str(output_file), 51)
        wb.Close(False)

        # Eliminar temporal
        if temp_excel.exists():
            temp_excel.unlink()

        print("=" * 80)
        print(f"✅ EXCEL CON DATOS Y POWER QUERY NATIVO GENERADO EXITOSAMENTE EN:\n   {output_file}")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ Error en COM: {e}")
        return False
    finally:
        excel.Quit()

if __name__ == "__main__":
    generar_excel_powerquery_completo()
