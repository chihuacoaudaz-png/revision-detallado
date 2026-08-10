# Especificación Técnica de Lógica ETL, Traducción Power Query M y Diccionario de Campos - Control Interno

Este documento detalla la estructura lógica del proceso de extracción, compilación y auditoría de **Control Interno** (`RD.402.P.01.F.04 Consolidado de Avance Julio.xlsx`), su traducción a **Power Query M**, la arquitectura lógica agnóstica para su replicación en cualquier plataforma de datos, y los tipos de datos de salida.

---

## 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M

### Paso 1: Selección de Hojas Diarias (`26.06` a `25.07`)
- **Lógica Agnóstica**: Abrir el libro maestro de Control Interno, filtrar las pestañas cuyos nombres coincidan con el patrón regex de fecha `^\d{2}\.\d{2}$` (ej. `26.06`, `27.06`, ..., `25.07`).
- **Traducción Power Query M**:
```powerquery
let
    OrigenBinario = File.Contents("C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\00_Control_Interno\RD.402.P.01.F.04  Consolidado de Avance Julio.xlsx"),
    Workbook = Excel.Workbook(OrigenBinario, null, true),
    FiltrarHojasDiarias = Table.SelectRows(Workbook, each [Kind] = "Sheet" and Text.Length([Name]) = 5 and Text.Middle([Name], 2, 1) = ".")
in
    FiltrarHojasDiarias
```

---

### Paso 2: Lectura Adaptativa desde Fila 10 hasta 'TOTAL AVANCE'
- **Lógica Agnóstica**: Omitir las primeras 9 filas (iniciar en fila 10, index 9). Leer fila por fila y detener la lectura cuando cualquier celda de la fila contenga el texto `"TOTAL AVANCE"` o `"TOTAL ACUMULADO"`.
- **Traducción Power Query M**:
```powerquery
fnProcesarHojaCI = (tablaHoja as table, nombreHoja as text) =>
let
    // Omitir primeras 9 filas (Filas 1 a 9)
    FilasDatos = Table.Skip(tablaHoja, 9),
    
    // Identificar posición de la celda de parada 'TOTAL AVANCE'
    PosicionTotal = List.PositionOf(Table.Column(FilasDatos, "Column3"), "TOTAL AVANCE", Occurrence.First, (value, criteria) => Text.Contains(Text.Upper(Text.From(value ?? "")), "TOTAL AVANCE")),
    
    // Recortar tabla hasta antes del TOTAL AVANCE
    TablaAcotada = if PosicionTotal <> -1 then Table.FirstN(FilasDatos, PosicionTotal) else FilasDatos
in
    TablaAcotada
```

---

### Paso 3: Propagación de CTR (Columna A Filldown) y Estandarización
- **Lógica Agnóstica**: La Columna A contiene el nombre del contrato en la primera fila de su bloque. Reemplazar valores vacíos o de títulos por nulo y aplicar *filldown*. Excluir registros del CTR `COLQUIJIRCA`.
- **Traducción Power Query M**:
```powerquery
    ColumnaA = Table.RenameColumns(TablaAcotada, {{"Column1", "CTR_RAW"}, {"Column3", "MAQUINA_RAW"}, {"Column5", "SE_PERFORO"}, {"Column7", "METRAJE_CI"}}),
    
    // Reemplazar títulos de cabecera en Column1 por nulo
    LimpiarCTR = Table.ReplaceValue(ColumnaA, each [CTR_RAW], each if List.Contains({"CONTRATO", "EQUIPO", "AVANCE", "SISTEMA", "TOTAL"}, Text.Upper(Text.From([CTR_RAW] ?? ""))) then null else [CTR_RAW], Replacer.ReplaceValue, {"CTR_RAW"}),
    FillDownCTR = Table.FillDown(LimpiarCTR, {"CTR_RAW"}),
    
    // Excluir filas donde MAQUINA_RAW sea nula o título
    FiltrarMaquinas = Table.SelectRows(FillDownCTR, each [MAQUINA_RAW] <> null and not List.Contains({"EQUIPO", "SUB", "SUP"}, Text.Upper(Text.From([MAQUINA_RAW])))),
    
    // Excluir COLQUIJIRCA
    ExcluirColquijirca = Table.SelectRows(FiltrarMaquinas, each not Text.Contains(Text.Upper(Text.From([CTR_RAW])), "COLQUIJIRCA"))
```

---

### Paso 4: Estandarización de Turno A/B por Secuencia de Máquina
- **Lógica Agnóstica**: Dado que cada máquina aparece exactamente 2 veces consecutivas por día (Turno Día y Turno Noche), indexar la secuencia de aparición de cada equipo dentro del día: 1ra aparición $\rightarrow$ **`A`**, 2da aparición $\rightarrow$ **`B`**.
- **Traducción Power Query M**:
```powerquery
    // Agregar índice de grupo por Máquina y Día
    AgruparPorMaquina = Table.Group(ExcluirColquijirca, {"MAQUINA_RAW"}, {
        {"FilasConTurno", (sub) => 
            let
                Indexado = Table.AddIndexColumn(sub, "Secuencia", 1, 1, Int64.Type),
                TurnoStd = Table.AddColumn(Indexado, "TURNO_ESTANDAR", each if [Secuencia] = 1 then "A" else "B", type text)
            in
                TurnoStd, type table}
    }),
    ExpandirTabla = Table.Combine(AgruparPorMaquina[FilasConTurno])
```

---

### Paso 5: Generación de `ID_CLAVE_UNICA` para Cruce de Auditoría
- **Lógica Agnóstica**: Concatenar `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}`.
- **Traducción Power Query M**:
```powerquery
    AgregarFechaISO = Table.AddColumn(ExpandirTabla, "FECHA_ISO", each "2026-" & Text.End(nombreHoja, 2) & "-" & Text.Start(nombreHoja, 2), type text),
    AgregarClaveUnicaCI = Table.AddColumn(AgregarFechaISO, "ID_CLAVE_UNICA", each [FECHA_ISO] & "|" & Text.Upper([CTR_RAW]) & "|" & Text.Upper([MAQUINA_RAW]) & "|" & [TURNO_ESTANDAR], type text)
```

---

## 2. Especificación de Campos y Tipos de Datos para Power Query (Control Interno)

A continuación se presenta el diccionario de datos compilados del flujo de Control Interno:

| Campo | Tipo Power Query M | Tipo SQL / Python | Permitir Null | Descripción / Reglas |
|---|---|---|---|---|
| `HOJA_FECHA` | `type text` | `VARCHAR(10)` | No | Nombre de la pestaña de origen (ej. `26.06`) |
| `FECHA` | `type date` | `DATE` | No | Fecha normalizada ISO (`YYYY-MM-DD`) |
| `CTR` | `type text` | `VARCHAR(50)` | No | Nombre estandarizado del contrato |
| `MAQUINA` | `type text` | `VARCHAR(50)` | No | Código estandarizado SAP de la máquina |
| `MAQUINA_ORIGEN_CI` | `type text` | `VARCHAR(50)` | No | Texto original del nombre de máquina en la pestaña |
| `TURNO_ESTANDAR` | `type text` | `VARCHAR(2)` | No | **`A`** (Guardia 1) o **`B`** (Guardia 2) |
| `TURNO_SECUENCIA` | `Int64.Type` | `INT` | No | `1` para 1er registro diario, `2` para 2do registro diario |
| `SE_PERFORO` | `type text` | `VARCHAR(10)` | Sí | `SI` o `NO` |
| `METRAJE_CI` | `type number` | `FLOAT` | No | Metraje reportado en la planilla de Control Interno |
| `ID_CLAVE_UNICA` | `type text` | `VARCHAR(150)` | No | Clave de auditoría: `{FECHA}\|{CTR}\|{MAQUINA}\|{TURNO}` |
| `FILA_EXCEL` | `Int64.Type` | `INT` | No | Número de fila original en la pestaña de Excel |

---

## 3. Consideraciones Críticas para Flujos de Power Query (Control Interno)

1. **Transformación Dinámica de Nombre de Hoja a Fecha**:
   - El nombre de la pestaña (ej. `26.06`) debe parsearse extrayendo los primeros 2 caracteres como Día y los 2 últimos como Mes para evitar confusiones de locale al interpretar fechas.
2. **Tratamiento de Celdas Combinadas en M**:
   - Cuando una celda combinada abarca múltiples filas en Excel, Power Query solo mantiene el valor en la primera celda y coloca `null` en las subsiguientes. El uso de `Table.FillDown` es estrictamente obligatorio para no perder la asociación de CTR.
3. **Manejo de Errores en Números Decimales**:
   - En Control Interno existen metrajes ingresados con coma (ej. `3,55`). Es indispensable aplicar `Text.Replace([METRAJE], ",", ".")` antes del casteo a `type number`.
