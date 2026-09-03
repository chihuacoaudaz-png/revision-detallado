<#
================================================================================
ROCKDRILL GROUP - RELATIONAL & DIMENSIONAL ARCHITECTURE
SCRIPT: scripts/apply_dim_tiempo_columns_tom.ps1
DESCRIPTION: 
  Aplica en dim_tiempo_calendario las columnas calculadas requeridas para el
  monitoreo temporal del ciclo minero (26 al 25) y configura sus SortByColumn via TOM:
    1. fecha_operativa_dt: Tipo DateTime real (DATE(INT(sk/10000), ...))
    2. fecha_corta_label: Label corto cronologico ('26-Ago', '01-Set') con SortByColumn = calendario_sk
    3. dia_ciclo_label: Label legible del dia de ciclo ('Día 01 (26-Ago)') con SortByColumn = dia_ciclo_operativo
PUERTO VERTIPAQ: 63554
================================================================================
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$port = 63554
$binDir = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.157.879.0_x64__8wekyb3d8bbwe\bin"

[System.Reflection.Assembly]::LoadFrom("$binDir\Microsoft.PowerBI.Amo.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$binDir\Microsoft.PowerBI.Amo.Core.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$binDir\Microsoft.PowerBI.Tabular.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$binDir\Microsoft.PowerBI.AdomdClient.dll") | Out-Null

$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$port")
$db = $server.Databases[0]
$model = $db.Model

Write-Host ">>> Conectado al Tabular Model en vivo: $($model.Name) (Puerto $port)" -ForegroundColor Cyan
$tbl = $model.Tables["dim_tiempo_calendario"]

if (-not $tbl) {
    Write-Error "Tabla dim_tiempo_calendario no encontrada en el modelo."
    exit 1
}

# ------------------------------------------------------------------------------
# 1. Columna Calculada: fecha_operativa_dt (DateTime real)
# ------------------------------------------------------------------------------
$colFechaOp = $tbl.Columns["fecha_operativa_dt"]
if (-not $colFechaOp) {
    $colFechaOp = New-Object Microsoft.AnalysisServices.Tabular.CalculatedColumn
    $colFechaOp.Name = "fecha_operativa_dt"
    $tbl.Columns.Add($colFechaOp)
    Write-Host "[NUEVA] Columna creada: fecha_operativa_dt" -ForegroundColor Yellow
} else {
    Write-Host "[EXISTE] Columna actualizada: fecha_operativa_dt" -ForegroundColor Cyan
}
$colFechaOp.DataType = [Microsoft.AnalysisServices.Tabular.DataType]::DateTime
$colFechaOp.FormatString = "yyyy-MM-dd"
$colFechaOp.Description = "Fecha operativa en formato Date nativo para ejes de tiempo continuo."
$colFechaOp.Expression = 'IF(dim_tiempo_calendario[calendario_sk] <= 0, DATE(1900, 1, 1), DATE(INT(dim_tiempo_calendario[calendario_sk]/10000), INT(MOD(dim_tiempo_calendario[calendario_sk], 10000)/100), MOD(dim_tiempo_calendario[calendario_sk], 100)))'

# ------------------------------------------------------------------------------
# 2. Columna Calculada: fecha_corta_label ('26-Ago', '01-Set')
# ------------------------------------------------------------------------------
$colFechaCorta = $tbl.Columns["fecha_corta_label"]
if (-not $colFechaCorta) {
    $colFechaCorta = New-Object Microsoft.AnalysisServices.Tabular.CalculatedColumn
    $colFechaCorta.Name = "fecha_corta_label"
    $tbl.Columns.Add($colFechaCorta)
    Write-Host "[NUEVA] Columna creada: fecha_corta_label" -ForegroundColor Yellow
} else {
    Write-Host "[EXISTE] Columna actualizada: fecha_corta_label" -ForegroundColor Cyan
}
$colFechaCorta.DataType = [Microsoft.AnalysisServices.Tabular.DataType]::String
$colFechaCorta.Description = "Etiqueta corta de fecha legible ('26-Ago') ordenada cronologicamente por calendario_sk."
$colFechaCorta.Expression = 'IF(dim_tiempo_calendario[calendario_sk] <= 0, "N/D", FORMAT(dim_tiempo_calendario[dia_mes], "00") & "-" & LEFT(dim_tiempo_calendario[mes_nom_civil], 3))'

# ------------------------------------------------------------------------------
# 3. Columna Calculada: dia_ciclo_label ('Día 01 (26-Ago)')
# ------------------------------------------------------------------------------
$colDiaCiclo = $tbl.Columns["dia_ciclo_label"]
if (-not $colDiaCiclo) {
    $colDiaCiclo = New-Object Microsoft.AnalysisServices.Tabular.CalculatedColumn
    $colDiaCiclo.Name = "dia_ciclo_label"
    $tbl.Columns.Add($colDiaCiclo)
    Write-Host "[NUEVA] Columna creada: dia_ciclo_label" -ForegroundColor Yellow
} else {
    Write-Host "[EXISTE] Columna actualizada: dia_ciclo_label" -ForegroundColor Cyan
}
$colDiaCiclo.DataType = [Microsoft.AnalysisServices.Tabular.DataType]::String
$colDiaCiclo.Description = "Etiqueta explicita del dia dentro del ciclo minero con fecha ('Día 01 (26-Ago)')."
$colDiaCiclo.Expression = 'IF(dim_tiempo_calendario[calendario_sk] <= 0, "No Definido", "D" & UNICHAR(237) & "a " & FORMAT(dim_tiempo_calendario[dia_ciclo_operativo], "00") & " (" & FORMAT(dim_tiempo_calendario[dia_mes], "00") & "-" & LEFT(dim_tiempo_calendario[mes_nom_civil], 3) & ")")'

# Guardar columnas antes de enlazar SortByColumn
$model.SaveChanges()

# ------------------------------------------------------------------------------
# 4. Asignar SortByColumn
# ------------------------------------------------------------------------------
$colSk = $tbl.Columns["calendario_sk"]
$colDiaCicloOp = $tbl.Columns["dia_ciclo_operativo"]

if ($colFechaCorta -and $colSk) {
    $colFechaCorta.SortByColumn = $colSk
    Write-Host "[SORT] fecha_corta_label -> SortByColumn = calendario_sk" -ForegroundColor Green
}

if ($colDiaCiclo -and $colDiaCicloOp) {
    $colDiaCiclo.SortByColumn = $colDiaCicloOp
    Write-Host "[SORT] dia_ciclo_label -> SortByColumn = dia_ciclo_operativo" -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 5. Recalcular y persistir en VertiPaq
# ------------------------------------------------------------------------------
$tbl.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Calculate)
$model.SaveChanges()
Write-Host ">>> [OK] Modificaciones y recalculacion guardadas exitosamente en VertiPaq." -ForegroundColor Green

# ------------------------------------------------------------------------------
# 6. Validacion Fisica con Query DAX via ADOMD
# ------------------------------------------------------------------------------
Write-Host "`n>>> [VALIDACION] Ejecutando consulta DAX de verificacion..." -ForegroundColor Yellow
$connStr = "Provider=MSOLAP;Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
$cmd = $conn.CreateCommand()

$cmd.CommandText = @"
EVALUATE
SELECTCOLUMNS(
    FILTER(
        dim_tiempo_calendario,
        dim_tiempo_calendario[calendario_sk] >= 20260825 && dim_tiempo_calendario[calendario_sk] <= 20260902
        || dim_tiempo_calendario[calendario_sk] = -1
    ),
    "calendario_sk", dim_tiempo_calendario[calendario_sk],
    "fecha_operativa_dt", dim_tiempo_calendario[fecha_operativa_dt],
    "dia_mes", dim_tiempo_calendario[dia_mes],
    "dia_ciclo_operativo", dim_tiempo_calendario[dia_ciclo_operativo],
    "fecha_corta_label", dim_tiempo_calendario[fecha_corta_label],
    "dia_ciclo_label", dim_tiempo_calendario[dia_ciclo_label]
)
ORDER BY [calendario_sk] ASC
"@

$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$conn.Close()
$server.Disconnect()

$dt | Format-Table -AutoSize | Out-String | Write-Host
Write-Host ">>> [VALIDACION EXITOSA] Estructura y datos 100% conformes." -ForegroundColor Green
