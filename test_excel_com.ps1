$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
Write-Host "Excel Version: $($excel.Version)"
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
