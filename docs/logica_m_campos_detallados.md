# Especificación Técnica de Lógica ETL, Traducción Power Query M y Diccionario de Campos - Reportes Detallados

Este documento detalla la estructura lógica del proceso de limpieza de los **Reportes Detallados por Equipo**, identificando las equivalencias exactas en **Power Query M**, la arquitectura lógica agnóstica para su implementación en cualquier lenguaje, y el detalle de tipos de datos de cada campo.

---

## 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M

### Paso 1: Filtro de Archivos y Exclusión de CTRs (Excluido COLQUIJIRCA)
- **Lógica Agnóstica**: Escanear directorio raíz, filtrar subcarpetas `CTR_*`, excluir `CTR_COLQUIJIRCA` y seleccionar archivos `.xlsx` que no empiecen con `~$`.
- **Traducción Power Query M**:
```powerquery
let
    Origen = Folder.Files("C:\Users\PERDLAP33\OneDrive - ROCK DRILL\Rockdrill_Control_Operaciones"),
    FiltrarRuta = Table.SelectRows(Origen, each Text.Contains([Folder Path], "CTR_") and Text.Contains([Folder Path], "02_Detallado")),
    ExcluirColquijirca = Table.SelectRows(FiltrarRuta, each not Text.Contains(Text.Upper([Folder Path]), "COLQUIJIRCA")),
    FiltrarExcel = Table.SelectRows(ExcluirColquijirca, each Text.EndsWith([Name], ".xlsx") and not Text.StartsWith([Name], "~$"))
in
    FiltrarExcel
```

---

### Paso 2: Lectura de Hojas Operativas y Omisión de Encabezados (Skip 22)
- **Lógica Agnóstica**: Para cada archivo, listar pestañas, filtrar hojas excluidas (`GENERAL`, `ADITIVOS`, `LISTAS`, `Tiempos`, `Hoja1`), extraer filas y omitir las primeras 22 filas (Fila 23 como primarios y Fila 24 como secundarios).
- **Traducción Power Query M**:
```powerquery
fnProcesarHoja = (contenidoBinario as binary, nombreHoja as text) =>
let
    Workbook = Excel.Workbook(contenidoBinario, null, true),
    HojaData = Workbook{[Item=nombreHoja, Kind="Sheet"]}[Data],
    
    // Skip 22 equivalencia exacta:
    TablaBase = Table.Skip(HojaData, 22),
    
    Titulos23 = Record.FieldValues(TablaBase{0}),
    Titulos24 = Record.FieldValues(TablaBase{1}),
    
    // Forward-fill horizontal en Titulos23
    TitulosLlenos = List.Accumulate(Titulos23, {}, (state, current) =>
        let
            clean = Text.Trim(Text.From(current ?? "")),
            lastVal = if List.IsEmpty(state) then "XP" else List.Last(state),
            newVal = if clean <> "" then clean else lastVal
        in
            state & {newVal}
    ),
    
    // Combinar Primario_Secundario
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
    TablaConHeaders = Table.RenameColumns(DatosSinEncabezados, List.Zip({Table.ColumnNames(DatosSinEncabezados), EncabezadosUnicos}))
in
    TablaConHeaders
```

---

### Paso 3: Propagación de FECHA y SONDAJE (`FillDown` + `FillUp`) y Filtrado de Filas Operativas Reales

> [!CRITICAL]
> **REGLA DE ORO DE ASIGNACIÓN DE SONDAJE Y FILTRADO**:
> 1. **Propagación de Fecha**: Se ejecuta `Table.FillDown` en la columna `FECHA`.
> 2. **Propagación Secuencial de Sondaje (`FillDown` + `FillUp`)**:
>    - **Caso MOROCOCHA**: Filas intermedias sin sondaje (Turnos Noche B) heredan el sondaje del turno anterior mediante `Table.FillDown`.
>    - **Caso CHUNGAR (Máquina `LM110U-001`, Fila 46 — 06 de Julio Turno B)**: Se perforaron 1.50m (DESDE 0.00m a HASTA 1.50m) en el Turno B del 06-jul, pero el supervisor recién escribió el nombre del sondaje (`DDHUCH26001`) en la fila del 07-jul Turno A.
>    - **Por qué fallaba en Power Query solo con FillDown**: Como no había sondajes arriba del 26-jun al 06-jul Turno A (días inactivos), `Table.FillDown` dejaba la celda en `null`, dejando los 1.50m huérfanos sin sondaje.
>    - **Solución Completa en M**: Ejecutar `Table.FillDown` seguido inmediatamente de `Table.FillUp` en `SONDAJE`. Así, la fila del 06-jul Turno B absorbe `DDHUCH26001` hacia arriba automáticamente.
> 3. **Filtrado Operativo**: Descartar filas de sumatorias y pie de página (=SUMA) donde no existan metrajes ni datos de perforación.

- **Traducción Power Query M**:
```powerquery
    ColumnaFecha = Table.RenameColumns(TablaConHeaders, {{Table.ColumnNames(TablaConHeaders){0}, "FECHA"}}),
    ReemplazarVaciosFecha = Table.ReplaceValue(ColumnaFecha, "", null, Replacer.ReplaceValue, {"FECHA"}),
    FillDownFecha = Table.FillDown(ReemplazarVaciosFecha, {"FECHA"}),
    
    // Propagación combinada FillDown + FillUp para Sondajes Vacíos (Morococha y Chungar)
    ReemplazarVaciosSondaje = Table.ReplaceValue(FillDownFecha, "", null, Replacer.ReplaceValue, {"SONDAJE"}),
    FillDownSondaje = Table.FillDown(ReemplazarVaciosSondaje, {"SONDAJE"}),
    FillUpSondaje = Table.FillUp(FillDownSondaje, {"SONDAJE"}),
    
    // Filtrado de Filas Operativas Reales (excluye pie de página)
    FiltrarFilasValidas = Table.SelectRows(FillUpSondaje, each 
        let
            sond = Text.Trim(Text.From([SONDAJE] ?? "")),
            turno = Text.Trim(Text.From([#"TURNO (A=1;B=2)"]? ?? "")),
            grupo = Text.Trim(Text.From([GRUPO]? ?? "")),
            hasta = Text.Trim(Text.From([HASTA]? ?? "")),
            perf = Text.Trim(Text.From([PERFORISTA]? ?? "")),
            met = try Number.From(Text.Replace(Text.Trim(Text.From([METRAJE]? ?? "")), ",", ".")) otherwise null,
            
            hasMetadata = sond <> "" or turno <> "" or grupo <> "" or hasta <> "" or perf <> "",
            hasMetraje = met <> null and met > 0
        in
            hasMetadata and (hasMetraje or hasta <> "" or sond <> "")
    )
```

---

### Paso 4: Estandarización de Turno A/B, Clave Única y Sondaje Paralelo

- **`TURNO (A=1;B=2)`**: Permanece en su posición original en la matriz nativa (columna #5).
- **`TURNO_ESTANDAR`**, **`ID_CLAVE_UNICA`** y **`SONDAJE_PARALELO`**: Se agregan como columnas adicionales al final del dataset.

```powerquery
    // Estandarización de Turno Guardia 1/A -> 'A', Guardia 2/B -> 'B'
    AgregarTurnoStd = Table.AddColumn(FiltrarFilasValidas, "TURNO_ESTANDAR", each 
        let
            rawT = Text.Upper(Text.From([#"TURNO (A=1;B=2)"]? ?? "")),
            rawG = Text.Upper(Text.From([GRUPO]? ?? ""))
        in
            if List.Contains({"1", "1.0", "A", "D", "DIA"}, rawT) or List.Contains({"1", "1.0"}, rawG) then "A"
            else if List.Contains({"2", "2.0", "B", "N", "NOCHE"}, rawT) or List.Contains({"2", "2.0"}, rawG) then "B"
            else "A", type text),
            
    AgregarClaveUnica = Table.AddColumn(AgregarTurnoStd, "ID_CLAVE_UNICA", each 
        Date.ToText([FECHA], "yyyy-MM-dd") & "|" & Text.Upper([CTR]) & "|" & Text.Upper([MAQUINA]) & "|" & [TURNO_ESTANDAR], type text),

    // Indicador de Sondaje Paralelo (Default = 1)
    AgregarSondajeParalelo = Table.AddColumn(AgregarClaveUnica, "SONDAJE_PARALELO", each 1, Int64.Type)
```

---

### Paso 5: Gestión de Sondajes Paralelos No Cobrados (Ajuste de YAULIYACU +125.40 m)

- **Contexto de Negocio**: En **YAULIYACU**, la máquina `XRD125USS-001` operó un **sondaje paralelo / secundario** del 17 al 25 de julio acumunlando 125.40m perforados. Este avance se anotó en el parte detallado para control de consumos y avance físico, pero **no se sumó en Control Interno porque NO SE COBRABA al cliente**.
- **Regla en Power Query M para Conciliación 100% Exacta**:
```powerquery
    // Paso Opcional de Filtrado de Sondaje Paralelo No Cobrado en Yauliyacu
    AjustarSondajeParaleloYauliyacu = Table.ReplaceValue(
        AgregarSondajeParalelo,
        1,
        each if [CTR] = "YAULIYACU" and [MAQUINA] = "XRD125USS-001" and [FECHA] >= #date(2026, 7, 17) and [FECHA] <= #date(2026, 7, 25) then 0 else [SONDAJE_PARALELO],
        Replacer.ReplaceValue,
        {"SONDAJE_PARALELO"}
    )
```

---

## 2. Código M Maestro Completo de Power Query (Ready to Copy-Paste)

Copia y pega la siguiente consulta M completa en el Editor Avanzado de Power Query para procesar la carpeta de Reportes Detallados:

```powerquery
let
    // 1. Origen y Filtro de Archivos
    RutaCarpeta = "c:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones",
    Origen = Folder.Files(RutaCarpeta),
    FiltrarRuta = Table.SelectRows(Origen, each Text.Contains([Folder Path], "CTR_") and Text.Contains([Folder Path], "02_Detallado")),
    ExcluirColquijirca = Table.SelectRows(FiltrarRuta, each not Text.Contains(Text.Upper([Folder Path]), "COLQUIJIRCA")),
    FiltrarExcel = Table.SelectRows(ExcluirColquijirca, each Text.EndsWith([Name], ".xlsx") and not Text.StartsWith([Name], "~$")),

    // 2. Función de Procesamiento por Hoja
    fnProcesarArchivo = (contenidoBinario as binary, nombreArchivo as text) =>
    let
        Workbook = Excel.Workbook(contenidoBinario, null, true),
        HojasVisibles = Table.SelectRows(Workbook, each [Kind] = "Sheet" and [Hidden] = false and not List.Contains({"ADITIVOS", "GENERAL", "LISTAS", "Tiempos"}, [Item])),
        
        ProcesarHojas = Table.AddColumn(HojasVisibles, "DatosProcesados", each 
            let
                HojaData = [Data],
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
                
                DatosSinHeaders = Table.Skip(TablaBase, 2),
                TablaConHeaders = Table.RenameColumns(DatosSinHeaders, List.Zip({Table.ColumnNames(DatosSinHeaders), EncabezadosUnicos})),
                
                ColumnaFecha = Table.RenameColumns(TablaConHeaders, {{Table.ColumnNames(TablaConHeaders){0}, "FECHA"}}),
                ReplaceVaciosFecha = Table.ReplaceValue(ColumnaFecha, "", null, Replacer.ReplaceValue, {"FECHA"}),
                FillDownFecha = Table.FillDown(ReplaceVaciosFecha, {"FECHA"}),
                
                ReplaceVaciosSondaje = Table.ReplaceValue(FillDownFecha, "", null, Replacer.ReplaceValue, {"SONDAJE"}),
                FillDownSondaje = Table.FillDown(ReplaceVaciosSondaje, {"SONDAJE"}),
                FillUpSondaje = Table.FillUp(FillDownSondaje, {"SONDAJE"}),
                
                FiltrarOperativas = Table.SelectRows(FillUpSondaje, each 
                    let
                        sond = Text.Trim(Text.From([SONDAJE] ?? "")),
                        hasta = Text.Trim(Text.From([HASTA]? ?? "")),
                        met = try Number.From(Text.Replace(Text.Trim(Text.From([METRAJE]? ?? "")), ",", ".")) otherwise null
                    in
                        sond <> "" and (hasta <> "" or (met <> null and met > 0))
                )
            in
                FiltrarOperativas
        )
    in
        ProcesarHojas
in
    FiltrarExcel
```

---

## 3. Estructura Final de Columnas (135 Columnas)

| Posición | Campo | Tipo | Origen / Regla |
|---|---|---|---|
| 1 | `N°` | Int64 | Índice correlativo |
| 2 | `ZONA` | Text | 'CENTRO' o 'PERIFERICO' |
| 3 | `CTR` | Text | Nombre estandarizado del CTR |
| 4 | `MAQUINA` | Text | Nombre oficial de máquina SAP |
| 5 | `TURNO (A=1;B=2)` | Text | Valor nativo original de la matriz |
| 6 | `GRUPO` | Text | Valor nativo original |
| 7 | `MES` | Text | Mes operativo (corte día 26) |
| 8 | `FECHA` | Date | Fecha normalizada (YYYY-MM-DD) |
| 9 | `SONDAJE` | Text | Nombre de pozo (resuelto con FillDown+FillUp) |
| 10 - 129 | *(Campos nativos)* | Varios | Campos nativos de perforación, aditivos y bitácora |
| 130 | `HOJA DE TRABAJO ORIGEN` | Text | Nombre de pestaña Excel |
| 131 | `ARCHIVO ORIGEN` | Text | Nombre de archivo Excel |
| 132 | `TURNO_ESTANDAR` | Text | Turno normalizado ('A' o 'B') |
| 133 | `ID_CLAVE_UNICA` | Text | Clave `{FECHA}\|{CTR}\|{MAQUINA}\|{TURNO_ESTANDAR}` |
| 134 | `SONDAJE_PARALELO` | Int64 | Default `1` (0 para paralelos no cobrados) |
| 135 | `Alerta_Comentarios` | Text | 'OK' o 'FALTA COMENTARIO' |

