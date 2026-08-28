param(
    [string]$OutputPath = "C:\Proyectos Python\Detallados\output\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx",
    [string]$RutaBase = "C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones"
)

# Forzar UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================================"
Write-Host "ROCKDRILL GROUP - GENERADOR DE EXCEL CON POWER QUERY NATIVO"
Write-Host "Destino: $OutputPath"
Write-Host "================================================================================"

$outputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

if (Test-Path $OutputPath) {
    try {
        Remove-Item -Path $OutputPath -Force
    } catch {
        Write-Host "Aviso: Archivo ocupado, guardando en version actualizada..."
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
    Write-Host "  [1/4] Inyectando Parametro Power Query: RutaOrigenLocal..."
    $m_RutaOrigen = "`"$RutaBase`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=true]"
    $wb.Queries.Add("RutaOrigenLocal", $m_RutaOrigen, "Ruta local de la carpeta de operaciones")

    Write-Host "  [2/4] Inyectando Parametro Power Query: TipoOrigen..."
    $m_TipoOrigen = "`"LOCAL`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=true]"
    $wb.Queries.Add("TipoOrigen", $m_TipoOrigen, "Conmutador de origen (LOCAL o CLOUD)")

    Write-Host "  [3/4] Inyectando Parametro Power Query: UrlSharePoint..."
    $m_UrlSharePoint = "`"https://rockdrillgroup.sharepoint.com/sites/Operaciones/Rockdrill_Control_Operaciones`" meta [IsParameterQuery=true, Type=`"Text`", IsParameterQueryRequired=false]"
    $wb.Queries.Add("UrlSharePoint", $m_UrlSharePoint, "URL de SharePoint para produccion en la nube")

    # --------------------------------------------------------------------------
    # 2. INYECTAR FUNCIÓN MODULAR (FOCO: HORAS Y METROS)
    # --------------------------------------------------------------------------
    Write-Host "  [4/4] Inyectando Funcion y Consultas M de Horas y Metros..."
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
        FilasOperativas = Table.SelectRows(FechaLlenada, each [FECHA] <> null and [FECHA] <> ""),
        ConCTR = Table.AddColumn(FilasOperativas, "CTR", each ctrNombre, type text),
        ConMaquina = Table.AddColumn(ConCTR, "MAQUINA", each nombreHoja, type text)
    in
        ConMaquina
in
    fn_ProcesarHojaDetallado
'@
    $wb.Queries.Add("fn_ProcesarHojaDetallado", $m_fnProcesar, "Procesador de hojas de detallados")

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
    ProcesarHojas = Table.AddColumn(FiltrarHojas, "ContenidoProcesado", each fn_ProcesarHojaDetallado([Content], [Sheet_Name], [CTR_Nombre]))
in
    ProcesarHojas
'@
    $wb.Queries.Add("Consolidado_Horas_y_Metros", $m_Consolidado, "Consulta consolidada de avance y horas operativas")

    # Guardar libro
    Write-Host "  • Guardando libro Excel con consultas M y parametros nativos..."
    $wb.SaveAs($OutputPath, 51)
    $wb.Close($false)
    
    Write-Host "================================================================================"
    Write-Host "EXITO: Libro Excel con Power Query Nativo creado en: $OutputPath"
    Write-Host "================================================================================"
} catch {
    Write-Host "Error en generacion COM: $_"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
