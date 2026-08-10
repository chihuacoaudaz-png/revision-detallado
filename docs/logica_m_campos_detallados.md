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

### Paso 3: Forward-Fill de FECHA y Filtrado de Filas Operativas Reales (Omisión de Totales de Pie de Página)

> [!CRITICAL]
> **REGLA DE ORO DE FILTRADO**:
> 1. Se debe realizar `Table.FillDown` en `FECHA` primero.
> 2. No filtrar únicamente por `SONDAJE <> ""`, ya que en guardias secundarias el supervisor dejaba `SONDAJE` en blanco manteniendo el metraje perforado.
> 3. Descartar filas de sumatorias/fórmulas de pie de página (donde `SONDAJE`, `TURNO`, `GRUPO`, `HASTA` y `PERFORISTA` son todos nulos/vacíos).

- **Traducción Power Query M**:
```powerquery
    ColumnaFecha = Table.RenameColumns(TablaConHeaders, {{Table.ColumnNames(TablaConHeaders){0}, "FECHA"}}),
    ReemplazarVacios = Table.ReplaceValue(ColumnaFecha, "", null, Replacer.ReplaceValue, {"FECHA"}),
    FillDownFecha = Table.FillDown(ReemplazarVacios, {"FECHA"}),
    
    // Filldown de SONDAJE a nivel de hoja para conservar el código en filas secundarias
    FillDownSondaje = Table.FillDown(Table.ReplaceValue(FillDownFecha, "", null, Replacer.ReplaceValue, {"SONDAJE"}), {"SONDAJE"}),
    
    // Filtrado de Filas Operativas Reales: Excluye filas vacías de plantilla y fórmulas de pie de página (=SUMA)
    FiltrarFilasValidas = Table.SelectRows(FillDownSondaje, each 
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

### Paso 4: Estandarización de Turno A/B y Clave Única
- **Lógica Agnóstica**: Convertir turnos a `A` (Día) o `B` (Noche). Construir `ID_CLAVE_UNICA = FECHA|CTR|MAQUINA|TURNO_ESTANDAR`.
- **Traducción Power Query M**:
```powerquery
    AgregarTurnoStd = Table.AddColumn(FiltrarFilasValidas, "TURNO_ESTANDAR", each 
        let
            rawT = Text.Upper(Text.From([#"TURNO (A=1;B=2)"]? ?? "")),
            rawG = Text.Upper(Text.From([GRUPO]? ?? ""))
        in
            if List.Contains({"1", "1.0", "A", "D", "DIA"}, rawT) or List.Contains({"1", "1.0"}, rawG) then "A"
            else if List.Contains({"2", "2.0", "B", "N", "NOCHE"}, rawT) or List.Contains({"2", "2.0"}, rawG) then "B"
            else "A", type text),
            
    AgregarClaveUnica = Table.AddColumn(AgregarTurnoStd, "ID_CLAVE_UNICA", each 
        Date.ToText([FECHA], "yyyy-MM-dd") & "|" & Text.Upper([CTR]) & "|" & Text.Upper([MAQUINA]) & "|" & [TURNO_ESTANDAR], type text)
```

---

## 2. Hallazgos Empíricos de Auditoría y Ajuste de M

Tras la auditoría empírica realizada día a día y turno a turno mediante `ID_CLAVE_UNICA`:

1. **CHUNGAR y MOROCOCHA**: Muestran **0.00 m de diferencia acumulada** en metraje total respecto a Control Interno (Chungar 2,347.55m vs 2,347.55m; Morococha 1,842.80m vs 1,842.80m).
2. **Distribución por Turno Día/Noche**: Las diferencias puntuales diarias (ej. +32.80m en Turno A y -32.80m en Turno B) corresponden a asignaciones en la planilla del supervisor donde se registraron múltiples corridas en la primera fila de la hoja en lugar de separar por turno. El acumulado diario es idéntico.
3. **YAULIYACU (+125.40m)**: Presenta la única discrepancia real debido a la operación de **taladro paralelo** en la máquina `XRD125USS-001` entre el 17 y 25 de julio.
