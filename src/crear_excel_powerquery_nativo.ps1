param(
    [string]$OutputPath = "C:\Proyectos Python\Detallados\output\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
    [string]$RutaBase = "C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones"
)

# Forzar UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================================"
Write-Host "ROCKDRILL GROUP - GENERADOR OFICIAL DE EXCEL CON POWER QUERY M NATIVO"
Write-Host "Destino: $OutputPath"
Write-Host "Ruta Base: $RutaBase"
Write-Host "================================================================================"

$outputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Si el archivo está abierto o bloqueado, manejarlo
if (Test-Path $OutputPath) {
    try {
        Remove-Item -Path $OutputPath -Force
    } catch {
        Write-Host "Aviso: Archivo bloqueado, guardando versión alternativa..."
        $OutputPath = [System.IO.Path]::Combine($outputDir, "CONSOLIDADOR_DETALLADOS_POWERQUERY_ACTUALIZADO.xlsx")
    }
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Add()
    
    # --------------------------------------------------------------------------
    # 1. INYECTAR PARÁMETROS NATIVOS DE POWER QUERY
    # --------------------------------------------------------------------------
    Write-Host "  [1/4] Inyectando Parámetro Power Query: RutaOrigenLocal..."
    $m_RutaOrigen = "`"$RutaBase`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=true]"
    $wb.Queries.Add("RutaOrigenLocal", $m_RutaOrigen, "Ruta local de la carpeta de operaciones")

    Write-Host "  [2/4] Inyectando Parámetro Power Query: TipoOrigen..."
    $m_TipoOrigen = "`"LOCAL`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=true]"
    $wb.Queries.Add("TipoOrigen", $m_TipoOrigen, "Conmutador de origen (LOCAL o CLOUD)")

    Write-Host "  [3/4] Inyectando Parámetro Power Query: UrlSharePoint..."
    $m_UrlSharePoint = "`"https://rockdrillgroup.sharepoint.com/sites/Operaciones/Rockdrill_Control_Operaciones`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=false]"
    $wb.Queries.Add("UrlSharePoint", $m_UrlSharePoint, "URL de SharePoint para producción en la nube")

    # --------------------------------------------------------------------------
    # 2. INYECTAR FUNCIÓN MODULAR TRANSFORMADORA (FOCO: HORAS Y METROS)
    # --------------------------------------------------------------------------
    Write-Host "  [4/4] Inyectando Función y Consultas M con Table.Combine y Foco Horas y Metros..."
    $m_fnProcesar = @'
let
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
    fn_ProcesarHojaDetallado
'@
    $wb.Queries.Add("fn_ProcesarHojaDetallado", $m_fnProcesar, "Procesador de hojas individuales de detallado")

    # --------------------------------------------------------------------------
    # 3. INYECTAR CONSULTA CONSOLIDADORA EXPANDIDA (TABLE.COMBINE)
    # --------------------------------------------------------------------------
    $m_Consolidado = @'
let
    Origen = if TipoOrigen = "LOCAL" then
        Folder.Files(RutaOrigenLocal)
    else
        SharePoint.Files(UrlSharePoint, [ApiVersion = 15]),
        
    FiltrarRuta = Table.SelectRows(Origen, each Text.Contains([Folder Path], "CTR_") and Text.Contains([Folder Path], "02_Detallado")),
    ExcluirColquijirca = Table.SelectRows(FiltrarRuta, each not Text.Contains(Text.Upper([Folder Path]), "COLQUIJIRCA")),
    FiltrarExcel = Table.SelectRows(ExcluirColquijirca, each Text.EndsWith([Name], ".xlsx") and not Text.StartsWith([Name], "~$")),
    
    AgregarCTR = Table.AddColumn(FiltrarExcel, "CTR_Nombre", each 
        let 
            partes = Text.Split([Folder Path], "\"),
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
    ColumnasRelevantes
'@
    $wb.Queries.Add("Consolidado_Horas_y_Metros", $m_Consolidado, "Consolidado de avance y distribución de horas de perforación")

    # --------------------------------------------------------------------------
    # 4. CREAR TABLA VINCULADA Y REFRESCAR EN HOJA EXCEL
    # --------------------------------------------------------------------------
    Write-Host "  • Vinculando ListObject en hoja CONSOLIDADO_HORAS_METROS..."
    $ws = $wb.Sheets.Item(1)
    $ws.Name = "CONSOLIDADO_HORAS_METROS"
    
    $connString = "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=`$Workbook`$;Location=Consolidado_Horas_y_Metros;Extended Properties=`"`""
    $cmdText = "SELECT * FROM [Consolidado_Horas_y_Metros]"
    
    $conn = $wb.Connections.Add2(
        "Consulta - Consolidado_Horas_y_Metros",
        "Conexión activa a Power Query M para actualización interactiva con 1 clic",
        $connString,
        $cmdText,
        6, # xlCmdMashup
        $true,
        $false
    )

    $listObj = $ws.ListObjects.Add(
        0, # xlSrcExternal
        $conn,
        $true,
        1,
        $ws.Range("A1")
    )
    $listObj.Name = "Tabla_Consolidado_Horas_Metros"
    $listObj.TableStyle = "TableStyleMedium9"

    # Intentar ejecutar el refresco inicial síncrono
    Write-Host "  • Ejecutando refresco inicial de datos en Excel..."
    $listObj.QueryTable.BackgroundQuery = $false
    try {
        $listObj.QueryTable.Refresh()
        Write-Host "  ✅ Refresco inicial ejecutado con éxito."
    } catch {
        Write-Host "  ℹ️ Nota de refresco: el modelo se actualizará al hacer clic en Datos -> Actualizar Todo en Excel."
    }

    # Guardar libro
    Write-Host "  • Guardando libro Excel con consultas M y tabla conectada..."
    $wb.SaveAs($OutputPath, 51) # 51 = xlOpenXMLWorkbook (.xlsx)
    $wb.Close($false)
    
    Write-Host "================================================================================"
    Write-Host "✅ LIBRO EXCEL CON POWER QUERY NATIVO CREADO EXITOSAMENTE EN: $OutputPath"
    Write-Host "================================================================================"
} catch {
    Write-Host "❌ Error en generación COM: $_"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
