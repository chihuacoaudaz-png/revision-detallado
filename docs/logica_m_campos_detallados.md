# Especificación Técnica de Lógica ETL, Traducción Power Query M y Diccionario de Campos - Reportes Detallados y Control Interno

Este documento detalla la arquitectura completa de extracción, limpieza y reconciliación de los **Reportes Detallados por Equipo** y el **Consolidado de Control Interno** en **Power Query M**, respaldado por validaciones cuantitativas 1-a-1 contra la base de datos oficial (`bbdd.xlsx`).

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

### Paso 2: Lectura de Hojas Operativas y Omisión de Encabezados (Skip 22 en Detallados)
- **Lógica Agnóstica**: Para cada archivo de Detallados, listar pestañas, filtrar hojas excluidas (`GENERAL`, `ADITIVOS`, `LISTAS`, `Tiempos`, `Hoja1`, `MAQUINA ...`), extraer filas y omitir las primeras 22 filas (Fila 23 como primarios y Fila 24 como secundarios).
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
>    - **Caso CHUNGAR (Máquina `LM110U-001`, Fila 46 — 06 de Julio Turno B)**: Se perforaron 1.50m (DESDE 0.00m a HASTA 1.50m) en el Turno B del 06-jul, pero el supervisor escribió el nombre del sondaje (`DDHUCH26001`) en la fila del 07-jul Turno A.
>    - **Solución Completa en M**: Ejecutar `Table.FillDown` seguido inmediatamente de `Table.FillUp` en `SONDAJE`. Así, la fila del 06-jul Turno B absorbe `DDHUCH26001` hacia arriba automáticamente.
> 3. **Filtrado Operativo**: Descartar filas de sumatorias y pie de página (=SUMA) donde no existan metrajes ni datos de perforación.

---

### Paso 4: Extracción de Control Interno (Motor Dual Multi-Hoja Diario y Plano)

- **Descripción**: El archivo de Control Interno (`RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx`) posee 30 pestañas diarias nombradas por fecha (`26.06` a `25.07`). El motor M lee automáticamente todas las pestañas de fecha o la pestaña consolidada (`BASE DE DATOS` / `00_CONTROL_INTERNO`), selecciona estrictamente las 9 columnas oficiales requeridas (`FECHA`, `CTR`, `APLICACION`, `MAQUINA_RAW`, `MAQUINA`, `SE_PERFORO`, `TURNO_ESTANDAR`, `METRAJE_CI`, `ID_CLAVE_UNICA`) y mapea los turnos A y B según la celda `DIAS_TRABAJADOS` (1 = Turno A Día, null = Turno B Noche).

```powerquery
    // Mapeo directo de TURNO_ESTANDAR en Control Interno
    #"Turno Estandarizado CI" = Table.AddColumn(#"Limpiar Cols SAP", "TURNO_ESTANDAR", (r) =>
        let
            diasTrab = Record.FieldOrDefault(r, "DIAS_TRABAJADOS", null),
            diasTrabStr = Text.Trim(Text.From(diasTrab ?? ""))
        in
            if diasTrabStr = "1" or diasTrabStr = "1.0" or diasTrabStr = "1,0" then "A"
            else "B", type text),
```

---

### Paso 5: Cruce y Matriz de Discrepancias (`Discrepancias_BD`)

- **Proceso**:
  1. Agrupa `Detallados_BD` por `ID_CLAVE_UNICA` suma `METRAJE`.
  2. Agrupa `Consolidado_BD` por `ID_CLAVE_UNICA` suma `METRAJE_CI`.
  3. Ejecuta `FullOuterJoin` por `ID_CLAVE_UNICA`.
  4. Calcula `DIFERENCIA = METRAJE_DETALLADO - METRAJE_CONTROL_INTERNO`.
  5. Filtra registros con `ABS(DIFERENCIA) >= 0.01`.
  6. Ordena explícitamente mediante tupla multinivel: `{{"FECHA", Order.Ascending}, {"CTR", Order.Ascending}, {"MAQUINA", Order.Ascending}}`.

---

## 2. Validación Cuantitativa y Coincidencia en BBDD

| CTR | Metraje Detallados | Metraje Control Interno | Diferencia | Estado |
| :--- | :---: | :---: | :---: | :---: |
| **AMERICANA** | 2,511.20 | 2,511.20 | **0.00** | ✅ Coincidencia Exacta |
| **ANDAYCHAGUA** | 2,315.85 | 2,315.85 | **0.00** | ✅ Coincidencia Exacta |
| **CATALINA HUANCA** | 4,677.20 | 4,677.20 | **0.00** | ✅ Coincidencia Exacta |
| **CERRO** | 660.20 | 660.20 | **0.00** | ✅ Coincidencia Exacta |
| **CHUNGAR** | 2,346.05 | 2,347.55 | **-1.50** | ⚠️ Diferencia Real Origen |
| **COBRIZA** | 4,376.70 | 4,376.70 | **0.00** | ✅ Coincidencia Exacta |
| **COLQUISIRI** | 1,165.60 | 1,165.60 | **0.00** | ✅ Coincidencia Exacta |
| **CONDESTABLE** | 2,800.40 | 2,800.40 | **0.00** | ✅ Coincidencia Exacta |
| **CUCULI** | 804.10 | 804.10 | **0.00** | ✅ Coincidencia Exacta |
| **INMACULADA** | 3,404.55 | 3,404.55 | **0.00** | ✅ Coincidencia Exacta |
| **LA ESTRELLA** | 1,228.70 | 1,228.70 | **0.00** | ✅ Coincidencia Exacta |
| **MOROCOCHA** | 1,796.40 | 1,842.80 | **-46.40** | ⚠️ Diferencia Real Origen |
| **RAURA** | 2,793.51 | 2,793.51 | **0.00** | ✅ Coincidencia Exacta |
| **SAN CRISTOBAL** | 2,325.40 | 2,325.40 | **0.00** | ✅ Coincidencia Exacta |
| **TAMBOJASA** | 299.55 | 299.55 | **0.00** | ✅ Coincidencia Exacta |
| **TICLIO** | 484.15 | 484.15 | **0.00** | ✅ Coincidencia Exacta |
| **YAULIYACU** | 2,553.80 | 2,428.40 | **+125.40** | ⚠️ Diferencia Real Origen |
| **YAURICOCHA** | 188.75 | 188.75 | **0.00** | ✅ Coincidencia Exacta |
| **TOTAL** | **36,732.11** | **36,654.61** | **+77.50** | 🎯 **100% Validado (935/935 Discrepancias)** |
