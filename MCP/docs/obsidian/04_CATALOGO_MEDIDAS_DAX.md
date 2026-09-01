# 📐 Catálogo Exhaustivo de Medidas DAX

> [!NOTE]
> Este catálogo contiene las **116 medidas DAX** documentadas y clasificadas por dominio funcional de negocio.

---

## 📂 Índice de Familias de Medidas

1. [[#1. Cluster de Rendimiento y ROP (Rate of Penetration)]]
2. [[#2. Cluster de Metraje y Avance Físico]]
3. [[#3. Cluster de Metas y Cumplimiento de Programa]]
4. [[#4. Cluster de Control de Tiempos y Horas Operativas]]
5. [[#5. Cluster de Metraje Perdido y Disponibilidad Global]]
6. [[#6. Cluster de Costos y Control Presupuestal]]
7. [[#7. Cluster de Brocas y Consumo de Insumos]]

---
## 1. Cluster de Rendimiento y ROP (Rate of Penetration)

### 🔹 `[Medidas].[Rendimiento Promedio (m/und)]`
```dax
DIVIDE([Total Metros], [Cantidad Brocas], 0)
```

### 🔹 `[Medidas].[ROP (m/hr)]`
```dax
DIVIDE([Total Metros], [Horas Operativas], 0)
```

### 🔹 `[Medidas].[ROP Mes Anterior]`
```dax
CALCULATE(
    [ROP (m/hr)], 
    DATEADD('Dim_Calendario'[Date], -1, MONTH)
)
```

### 🔹 `[Medidas].[ROP Variacion]`
```dax
[ROP (m/hr)] - [ROP Mes Anterior]
```

### 🔹 `[Medidas].[ROP Icono]`
```dax
VAR Diff = [ROP Variacion]
RETURN
SWITCH(TRUE(),
    Diff > 0, "▲",  -- Flecha arriba si subió
    Diff < 0, "▼",  -- Flecha abajo si bajó
    "-"             -- Guión si es igual
)
```

### 🔹 `[Medidas].[ROP Color]`
```dax
VAR Diff = [ROP Variacion]
RETURN
SWITCH(TRUE(),
    Diff > 0, "#008000", -- Verde (Hexadecimal)
    Diff < 0, "#FF0000", -- Rojo (Hexadecimal)
    "#808080"            -- Gris si no hay cambio
)
```

### 🔹 `[Medidas].[ROP Etiqueta Final]`
```dax
VAR ValorFormateado = FORMAT([ROP (m/hr)], "0.00") -- "0.00" asegura dos decimales
VAR Flecha = [ROP Icono]                           -- Usa la medida que creamos antes
RETURN 
ValorFormateado & " " & Flecha
```

### 🔹 `[Medidas].[ROP perforista (m/hr)]`
```dax
VAR CurrentPerforista = SELECTEDVALUE(Dim_Personal[PERFORISTA], BLANK())
RETURN
IF(
    ISBLANK(CurrentPerforista),
    BLANK(),
    DIVIDE(
        CALCULATE(
            SUM('Fact_Metraje'[METRAJE_X_GUARDIA]),
            'Fact_Metraje'[PERFORISTA] = CurrentPerforista
        ),
        CALCULATE(
            SUM('Fact_Tiempos'[Horas]),
            'Fact_Tiempos'[PERFORISTA] = CurrentPerforista,
            'Fact_Tiempos'[Categoria] IN { "OPERATIVO", "EFECTIVAS" }
        ),
        0
    )
)
```

### 🔹 `[Medidas].[ROP EFECTIVAS (m/hr)]`
```dax
DIVIDE([Total Metros], [Horas Efectivas], 0)
```

### 🔹 `[Medidas].[Rendimiento promedio]`
```dax
[Total Metros] / [Consumo Cantidad]
```

### 🔹 `[Medidas].[ROP (m/hr) Corregido]`
```dax
CALCULATE(
    DIVIDE([Total Metros], [Horas Operativas], 0),
    TREATAS(
        VALUES('Consumo Consolidado'[Serie]), 
        'Fact_Metraje'[Nº_BROCA]
    )
)
```

### 🔹 `[Medidas].[Rendimiento Promedio (m/und) Corregido]`
```dax
CALCULATE(
    DIVIDE([Total Metros], [Cantidad Brocas CONSUMO], 0),
    TREATAS(
        VALUES('Consumo Consolidado'[Serie]), 
        'Fact_Metraje'[Nº_BROCA]
    )
)
```

### 🔹 `[Medidas].[Ratio ideal]`
```dax
DIVIDE( [Meta Mensual por maquina] , 16 )
```

### 🔹 `[Medidas].[ROP Solo Perforacion (m/hr)]`
```dax
VAR _Metros = SUM('Fact_Metraje'[METRAJE_X_GUARDIA])
VAR _HorasPerforacion = 
    CALCULATE(
        SUM('Fact_Tiempos'[Horas]),
        'Fact_Tiempos'[Actividad] = "PERFORACION"
    )
RETURN
    DIVIDE(_Metros, _HorasPerforacion, 0)
```

### 🔹 `[Medidas].[ROP Horas Totales Disponibles (m/hr)]`
```dax
VAR _Metros = SUM('Fact_Metraje'[METRAJE_X_GUARDIA])

// 1. Última fecha donde se registró metraje en el mes/filtro seleccionado
VAR _UltimaFechaData = MAX('Fact_Metraje'[FECHA])

// 2. Horas totales teóricas (2 guardias * 12 hrs = 24 hrs por día transcurrido)
// Evalúa máquina por máquina para que cuadre exacto tanto a nivel individual como en el Total
VAR _HorasTotalesReloj = 
    SUMX(
        VALUES('Fact_Metraje'[MAQUINA]),
        VAR _DiasTranscurridos = 
            CALCULATE(
                COUNTROWS('Dim_Calendario'),
                'Dim_Calendario'[Date] <= _UltimaFechaData
            )
        RETURN
            _DiasTranscurridos * 24  // 2 guardias * 12 horas por día
    )

RETURN
    DIVIDE(_Metros, _HorasTotalesReloj, 0)
```

## 2. Cluster de Metraje y Avance Físico

### 🔹 `[Medidas].[Total Metros]`
```dax
SUM(Fact_Metraje[METRAJE_X_GUARDIA])
```

### 🔹 `[Medidas].[Ejecutado Acumulado]`
```dax
VAR UltimaFechaGrafico = MAX('Dim_Calendario'[Date])

RETURN
    CALCULATE(
        [Total Metros], -- Tu medida base de suma de metros
        FILTER(
            ALLSELECTED('Dim_Calendario'), -- Mira todos los días seleccionados en tu filtro
            'Dim_Calendario'[Date] <= UltimaFechaGrafico -- Suma solo hasta la fecha que mira el gráfico
        )
    )
```

### 🔹 `[Medidas].[Metros con Promedio Total]`
```dax
IF(
    ISINSCOPE('Fact_Metraje'[Nº_BROCA]), 
    SUM(Fact_Metraje[METRAJE_X_GUARDIA]), 
    AVERAGEX(
        VALUES('Fact_Metraje'[Nº_BROCA]), 
        CALCULATE(SUM(Fact_Metraje[METRAJE_X_GUARDIA]))
    )
)
```

### 🔹 `[Medidas].[Promedio Avance Mensual 80-10]`
```dax
VAR MaquinaNombre = "XRD80USS-010"  // <--- EDITA AQUÍ EL NOMBRE DE TU MÁQUINA

RETURN
CALCULATE(
    AVERAGEX(
        VALUES('Dim_Calendario'[Mes Año]),  -- Lista los meses del rango seleccionado (Jun-Feb)
        CALCULATE(SUM('Fact_Metraje'[METRAJE_X_GUARDIA])) -- Calcula el total de cada mes
    ),
    'Fact_Metraje'[MAQUINA] = MaquinaNombre -- Filtra solo para la máquina específica
)
```

### 🔹 `[Medidas].[Promedio Avance Mensual 017]`
```dax
VAR MaquinaNombre = "XRD90U-017"  // <--- EDITA AQUÍ EL NOMBRE DE TU MÁQUINA

RETURN
CALCULATE(
    AVERAGEX(
        VALUES('Dim_Calendario'[Mes Año]),  -- Lista los meses del rango seleccionado (Jun-Feb)
        CALCULATE(SUM('Fact_Metraje'[METRAJE_X_GUARDIA])) -- Calcula el total de cada mes
    ),
    'Fact_Metraje'[MAQUINA] = MaquinaNombre -- Filtra solo para la máquina específica
)
```

### 🔹 `[Medidas].[Cantidad Consumo x Metro ($/m)]`
```dax
DIVIDE(
    [Total Metros],
    [Consumo Cantidad],  
    0
)
```

### 🔹 `[Tabla].[Metros Restantes]`
```dax
[Meta Mensual Ajustada] - [Total Metros]
```

### 🔹 `[Medidas].[Metraje Faltante]`
```dax
VAR Diferencia = [Meta Mensual por maquina] - [Total Metros]
RETURN
IF(Diferencia > 0, Diferencia, 0)
```

### 🔹 `[Medidas].[Metros promedio por perforista]`
```dax
[ROP EFECTIVAS (m/hr)] + [Promedio Horas efectivas Por Dia]
```

### 🔹 `[Medidas].[% Avance Gantt]`
```dax
DIVIDE(
    [Ejecutado Acumulado], 
    MAX('Dim_Sondaje'[PROFUNDIDAD_PROGRAMADA]), 
    0
)
```

### 🔹 `[Medidas].[Etiqueta Avance]`
```dax
FORMAT([Ejecutado Acumulado], "0.0") & " m / " & 
FORMAT(MAX('Dim_Sondaje'[PROFUNDIDAD_PROGRAMADA]), "0.0") & " m"
```

### 🔹 `[Medidas].[Cantidad Brocas (Con Metraje)]`
```dax
CALCULATE(
    DISTINCTCOUNT('Consumo Consolidado'[Serie]),
    'Consumo Consolidado'[Serie] <> "0",
    'Consumo Consolidado'[Serie] <> "ND",
    'Consumo Consolidado'[Serie] <> "",
    // Esto asegura que la serie exista también en Fact_Metraje
    TREATAS(
        VALUES('Fact_Metraje'[Nº_BROCA]), 
        'Consumo Consolidado'[Serie]
    )
)
```

### 🔹 `[Disponibilidad global].[Metros DG]`
```dax
// Paso 1: Identificar el tipo de máquina
    VAR Tipo_maquina_texto = SELECTEDVALUE(Fact_Metas[TIPO_MAQUINA]) 
    VAR Tipo_maquina = 
        SWITCH(
            Tipo_maquina_texto,
            "mina", 14,
            "superficie", 16,
            BLANK() 
        )

    // Paso 2: Calcular metros por día
    VAR Metros_por_dia = 
        DIVIDE( [Meta Mensual por maquina], 30 )

    // Paso 3: Calcular el ratio esperado
    VAR Ratio_esperado = 
        DIVIDE( Metros_por_dia, Tipo_maquina )

    // Paso 4: Calcular las horas afectadas solo para la actividad de esta fila
    VAR Horas_disminuyen_dg = 
        CALCULATE(
            SUM(fact_tiempos[horas]),
            fact_tiempos[Afecta_disp] = "AFECTA"
        )
        
    // Paso 5: CORRECCIÓN. Usamos la variable 'Ratio_esperado' 
    // en lugar de llamar a la medida externa '[Ratio ideal]'
    VAR Metros_perdidos = 
        Ratio_esperado * Horas_disminuyen_dg

// Retornamos los metros perdidos para que cuadre con tu matriz visual
RETURN 
    Metros_perdidos
```

### 🔹 `[Medidas].[metros_Grafico]`
```dax
VAR MetrosReales = SUM(Fact_Metraje[METRAJE_X_GUARDIA])

-- Verifica si existe un registro en la base de datos para esa fecha y turno
VAR ExisteRegistro = NOT ISEMPTY(Fact_Metraje) 

RETURN 
    IF(
        ExisteRegistro,
        -- Aumentamos a 1 para forzar que Power BI dibuje al menos un bloque visible
        IF(MetrosReales = 0 || ISBLANK(MetrosReales), 1, MetrosReales),
        BLANK()
    )
```

### 🔹 `[Disponibilidad global].[Metros_por_guardia_ideales]`
```dax
DIVIDE( [Meta Mensual por maquina], 60 )
```

### 🔹 `[Disponibilidad global].[Metros NO PERFORADOS]`
```dax
calculate([Turnos Sin Perforar]*[Metros_por_guardia_ideales])
```

### 🔹 `[Medidas].[Metros Dejados de Perforar]`
```dax
// 1. Horas de la fila actual (ya sea la Categoría completa o la Actividad)
VAR _HorasFila = SUM('Fact_Tiempos'[Horas])

// 2. ROP de Perforación aislado del filtro de la actividad/categoría
VAR _ROP_Efectivo = 
    CALCULATE(
        [ROP Solo Perforacion (m/hr)],
        REMOVEFILTERS('Fact_Tiempos'[Actividad], 'Fact_Tiempos'[Categoria])
    )

// 3. Cálculo de metros no perforados
RETURN
    _HorasFila * _ROP_Efectivo
```

## 3. Cluster de Metas y Cumplimiento de Programa

### 🔹 `[Medidas].[Meta Diaria Lineal]`
```dax
VAR MetaDelPeriodo = 
    CALCULATE(
        SUM('Fact_Metas'[META METRAJE]),
        // ERROR CORREGIDO: Solo dejamos columnas de Dim_Calendario aquí.
        // El filtro de Dim_CTR se mantiene solo, no hace falta mencionarlo.
        ALLEXCEPT('Dim_Calendario', 'Dim_Calendario'[Periodo Sort])
    )

VAR DiasEnElPeriodo = 
    CALCULATE(
        COUNTROWS('Dim_Calendario'), 
        // Contamos cuántos días tiene este periodo operativo (26 al 25)
        ALLEXCEPT('Dim_Calendario', 'Dim_Calendario'[Periodo Sort])
    )

RETURN
    DIVIDE(MetaDelPeriodo, DiasEnElPeriodo, 0)
```

### 🔹 `[Medidas].[Meta Acumulada Periodo]`
```dax
-- 1. SUMA DE TODAS LAS MÁQUINAS DEL MES
-- Usamos ALLSELECTED para que la bolsa de metros sea total y no se filtre por día
VAR MetaTotalFlota = 
    CALCULATE(
        SUM('Fact_Metas'[META METRAJE]), 
        ALLSELECTED('Dim_Calendario')
    )

-- 2. CANTIDAD DE DÍAS OPERATIVOS DEL PERIODO
VAR DiasTotalesPeriodo = 
    CALCULATE(
        COUNTROWS('Dim_Calendario'), 
        ALLSELECTED('Dim_Calendario')
    )

-- 3. META DIARIA (División)
VAR MetaDiaria = DIVIDE(MetaTotalFlota, DiasTotalesPeriodo)

-- 4. SUMA ACUMULADA POR DÍAS TRANSCURRIDOS
VAR FechaInicio = CALCULATE(MIN('Dim_Calendario'[Date]), ALLSELECTED('Dim_Calendario'))
VAR FechaEjeX = MAX('Dim_Calendario'[Date])
VAR DiasTranscurridos = DATEDIFF(FechaInicio, FechaEjeX, DAY) + 1

VAR ResultadoAcumulado = MetaDiaria * DiasTranscurridos

-- 5. VALIDACIÓN FINAL
-- Solo mostramos la meta si estamos dentro del rango del periodo seleccionado
RETURN 
IF(
    FechaEjeX >= FechaInicio && FechaEjeX <= CALCULATE(MAX('Dim_Calendario'[Date]), ALLSELECTED('Dim_Calendario')),
    ResultadoAcumulado,
    BLANK()
)
```

### 🔹 `[Medidas].[Desviación %]`
```dax
DIVIDE( [Total Metros] - [Meta Metraje a la Fecha CONDICIONAL], [Meta Metraje a la Fecha CONDICIONAL], 0 )
```

### 🔹 `[Medidas].[Meta Costo CTR]`
```dax
-- 1. Identificamos el CTR activo en el contexto (ya sea por filtro de máquina o de proyecto)
VAR _CTR_Seleccionado = SELECTEDVALUE('fact_tiempos'[CTR])

-- 2. Buscamos el costo en la DIM_CTR usando LOOKUPVALUE para evitar conflictos de relación
VAR _ValorMeta = 
    LOOKUPVALUE(
        'DIM_CTR'[Costo por metro], 
        'DIM_CTR'[CTR], 
        _CTR_Seleccionado
    )

-- 3. Si el CTR no tiene meta (celdas vacías), usamos el promedio de los CTRs con data
VAR _PromedioSeguridad = 
    CALCULATE(
        AVERAGE('DIM_CTR'[Costo por metro]), 
        ALLSELECTED('DIM_CTR')
    )

RETURN 
    IF(ISBLANK(_ValorMeta), _PromedioSeguridad, _ValorMeta)
```

### 🔹 `[Tabla].[Ritmo Base Diario]`
```dax
DIVIDE( SUM(Fact_Metas[META METRAJE]), 30 )
```

### 🔹 `[Tabla].[Meta Mensual Ajustada]`
```dax
VAR DiasEnMes = COUNTROWS(ALLSELECTED('Dim_Calendario')) -- Cuenta días del mes filtrado
VAR RitmoDiario = [Ritmo Base Diario] -- Tu cálculo de Meta/30
RETURN
RitmoDiario * DiasEnMes
```

### 🔹 `[Tabla].[Meta Dinámica Proyectada]`
```dax
VAR DiasRestantes = COUNTROWS( FILTER(Dim_Calendario, Dim_Calendario[Date] > TODAY()) )
RETURN
DIVIDE([Metros Restantes], DiasRestantes) * 7  -- Multiplicamos por 7 para ver la meta de la semana
```

### 🔹 `[Tabla].[Meta Mensual]`
```dax
CALCULATE(
    SUM('Fact_Metas'[META METRAJE]),
    KEEPFILTERS('Dim_Calendario'[Periodo Sort])
)
```

### 🔹 `[Tabla].[Meta Semanal Ajustada]`
```dax
VAR MetaTotalMes = [Meta Mensual]

-- 1. Calculamos lo perforado hasta la semana ANTERIOR a la que se muestra en el gráfico
VAR MetrosHechos = 
    CALCULATE(
        [Total Metros], 
        FILTER(
            ALLSELECTED('Dim_Calendario'), 
            'Dim_Calendario'[Semana Num] < MAX('Dim_Calendario'[Semana Num])
        )
    )

-- 2. Cuántas semanas quedan por trabajar (incluyendo la actual) en este mes
VAR SemanasRestantes = 
    CALCULATE(
        DISTINCTCOUNT('Dim_Calendario'[Semana Num]),
        FILTER(
            ALLSELECTED('Dim_Calendario'),
            'Dim_Calendario'[Semana Num] >= MAX('Dim_Calendario'[Semana Num])
        )
    )

-- 3. Repartimos lo que falta entre las semanas que quedan
VAR Resultado = DIVIDE(MetaTotalMes - MetrosHechos, SemanasRestantes)

-- Evitamos negativos si ya se pasó la meta
RETURN IF(Resultado < 0, 0, Resultado)
```

### 🔹 `[Medidas].[Meta Mensual por maquina]`
```dax
VAR DiasEnMes = COUNTROWS('Dim_Calendario')
-- Usamos MAX para que no sume metas de diferentes meses o registros
VAR MetaBase = MAX('fact_metas'[META METRAJE]) 

RETURN
DIVIDE(MetaBase, 30) * DiasEnMes
```

### 🔹 `[Tabla].[Meta Dinamica Semanal]`
```dax
-- 1. Meta Total del Mes (los 2,053.33)
VAR MetaTotalMes = CALCULATE([Meta Mensual], ALLSELECTED('Dim_Calendario'))

-- 2. Identificamos los días de la semana actual (pueden ser 7 o menos si es la última)
VAR FechaInicioSemana = MIN('Dim_Calendario'[Date])
VAR DiasEnEstaSemana = COUNTROWS('Dim_Calendario')

-- 3. Identificamos el inicio y fin del periodo completo (26 al 25)
VAR FechaFinPeriodo = CALCULATE(MAX('Dim_Calendario'[Date]), ALLEXCEPT('Dim_Calendario', 'Dim_Calendario'[Periodo Sort]))

-- 4. RECALCULO: Metros hechos ANTES de esta semana
VAR MetrosHechosPasado = 
    CALCULATE(
        [Total Metros],
        FILTER(
            ALLSELECTED('Dim_Calendario'),
            'Dim_Calendario'[Date] < FechaInicioSemana
        )
    )

-- 5. Días operativos que quedan desde el INICIO de esta semana hasta el cierre (25)
VAR DiasRestantesMes = 
    COUNTROWS(
        FILTER(
            ALLSELECTED('Dim_Calendario'),
            'Dim_Calendario'[Date] >= FechaInicioSemana && 
            'Dim_Calendario'[Date] <= FechaFinPeriodo
        )
    )

-- 6. LA LOGICA: Meta Diaria Base (del resto del mes) * Días de esta semana
VAR MetaDiariaBaseRecalculada = DIVIDE(MetaTotalMes - MetrosHechosPasado, DiasRestantesMes)
VAR Resultado = MetaDiariaBaseRecalculada * DiasEnEstaSemana

RETURN
IF(
    ISINSCOPE('Dim_Calendario'[Semana Operativa]),
    Resultado,
    MetaTotalMes -- El Total de la tabla mostrará el objetivo mensual completo
)
```

### 🔹 `[Tabla].[Ritmo Diario Requerido]`
```dax
VAR PeriodoActual = SELECTEDVALUE('Dim_Calendario'[Periodo Sort])

-- 1. Buscamos el último día del periodo operativo (el 25)
VAR FinDePeriodo = 
    CALCULATE(
        MAX('Dim_Calendario'[Date]), 
        ALLEXCEPT('Dim_Calendario', 'Dim_Calendario'[Periodo Sort])
    )

-- 2. Metros que faltan
VAR MetaTotal = CALCULATE([Meta Mensual], ALLSELECTED('Dim_Calendario'))
VAR AvanceActual = [Total Metros]
VAR MetrosFaltantes = MetaTotal - AvanceActual

-- 3. CAMBIO CLAVE: Identificamos la última fecha donde HUBO metros
-- Reemplaza 'Tabla_Hechos'[Fecha] por tu columna real de perforación
VAR UltimaFechaData = CALCULATE(MAX('Fact_Metraje'[FECHA]), ALLSELECTED('Fact_Metraje'))

-- 4. Días desde la última data hasta el cierre
VAR DiasRestantes = 
    COUNTROWS(
        FILTER(
            ALL('Dim_Calendario'),
            'Dim_Calendario'[Date] > UltimaFechaData && 
            'Dim_Calendario'[Date] <= FinDePeriodo &&
            'Dim_Calendario'[Periodo Sort] = PeriodoActual
        )
    )

RETURN
IF(
    MetrosFaltantes <= 0, 0, 
    DIVIDE(MetrosFaltantes, DiasRestantes, 0)
)
```

### 🔹 `[Medidas].[Desviación % dinamica]`
```dax
DIVIDE( [Total Metros] - [Meta Dinamica Semanal], [Meta Dinamica Semanal], 0 )
```

### 🔹 `[Medidas].[Meta Acumulada]`
```dax
VAR UltimaFechaGrafico = MAX('Dim_Calendario'[Date])

-- Calculamos qué día "número" es (ej: el día 5 del periodo, el día 10, etc.)
VAR DiasTranscurridos = 
    CALCULATE(
        COUNTROWS('Dim_Calendario'),
        FILTER(
            ALLSELECTED('Dim_Calendario'),
            'Dim_Calendario'[Date] <= UltimaFechaGrafico
        )
    )

RETURN
    [Meta Diaria Lineal] * DiasTranscurridos
```

### 🔹 `[Medidas].[Meta al Día]`
```dax
VAR PeriodoActual = SELECTEDVALUE(dim_calendario[periodo sort])
-- Usamos TODAY() para que en el dashboard publicado siempre sepa qué día es hoy
VAR FechaHoy = TODAY() 

-- 1. Días totales del mes operativo (ej. del 26 al 25)
VAR DiasTotalesPeriodo = 
    CALCULATE(
        COUNTROWS(dim_calendario),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[periodo sort] = PeriodoActual
    )

-- 2. Días que han pasado desde el inicio del periodo (26) hasta hoy
VAR DiasTranscurridos = 
    CALCULATE(
        COUNTROWS(dim_calendario),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[periodo sort] = PeriodoActual,
        dim_calendario[Date] <= FechaHoy
    )

RETURN
IF(
    ISBLANK(PeriodoActual), 
    0, 
    DIVIDE([Meta Acumulada], DiasTotalesPeriodo, 0) * DiasTranscurridos
)
```

### 🔹 `[Medidas].[Meta Metraje a la Fecha CONDICIONAL]`
```dax
-- 1. Obtenemos la meta total del mes operativo actual
VAR MetaTotalMes = SUM(Fact_Metas[META METRAJE])

-- 2. Identificamos la última fecha con datos en Fact_Metraje
VAR UltimaFechaData = MAX(Fact_Metraje[FECHA])

-- 3. Identificamos el Mes Operativo actual
VAR MesOperativoActual = SELECTEDVALUE(Fact_Metas[MES OPERATIVO])

-- 4. Calculamos la fecha de inicio operativa (día 26 del mes anterior)
VAR FechaInicioOperativa = 
    DATE(
        YEAR(MesOperativoActual), 
        MONTH(MesOperativoActual) - 1, 
        26
    )

-- 5. Lógica para la máquina específica XRD80ITH-001
VAR MaquinaActual = SELECTEDVALUE(Fact_Metraje[MAQUINA]) -- Ajusta el nombre de la columna si es necesario

VAR DiasTranscurridos = 
    IF(
        MaquinaActual = "XRD80ITH-001",
        -- Si es la máquina especial, contamos solo días de lunes a viernes
        COUNTROWS(
            FILTER(
                CALENDAR(FechaInicioOperativa, UltimaFechaData),
                WEEKDAY([Date], 2) < 6 -- 1=Lunes, 5=Viernes. 6 y 7 son Sábado y Domingo
            )
        ),
        -- Para las demás máquinas, mantenemos el cálculo lineal
        DATEDIFF(FechaInicioOperativa, UltimaFechaData, DAY) + 1
    )

-- 6. Aplicamos la fórmula: (Meta / 30) * Días Transcurridos
RETURN
    IF(
        NOT ISBLANK(MetaTotalMes),
        DIVIDE(MetaTotalMes, [Dias Mes Operativo]) * DiasTranscurridos
    )
```

### 🔹 `[Medidas].[Proyección base]`
```dax
([ROP (m/hr)] * [Dias Operativos Restantes]*[Promedio Horas Por Dia])+ [Total Metros]
```

### 🔹 `[Medidas].[Desviación Proyectado %]`
```dax
DIVIDE(
    [Proyección base], 
    [Meta Mensual por maquina], 
    0
)
```

### 🔹 `[Medidas].[Metraje segun meta]`
```dax
[Meta Mensual por maquina] - [Total Metros]
```

### 🔹 `[Presupuesto].[Cumplimiento % Operativo]`
```dax
VAR MetrosReales = [Total Metros]
VAR MetaAFecha = [Meta Acumulada Periodo]
RETURN
DIVIDE(
    MetrosReales,
    MetaAFecha,
    0
)
```

### 🔹 `[Presupuesto].[Cumplimiento % Hace 2 Periodos]`
```dax
-- 1. Identificamos el periodo operativo que se está visualizando en el reporte
VAR PeriodoActual = SELECTEDVALUE(Dim_Calendario[Mes Num Operativo])
VAR AnioActual = SELECTEDVALUE(Dim_Calendario[Año Operativo])

-- 2. Calculamos cuál sería el periodo objetivo (2 meses atrás)
VAR PeriodoObjetivo = PeriodoActual - 2

RETURN
IF(
    -- Validamos que estemos dentro de un rango válido (por ejemplo, que no dé negativo en los primeros meses del año)
    PeriodoObjetivo > 0,
    
    -- 3. Desplazamos el contexto para Metros y Metas usando CALCULATE
    VAR MetrosHace2Periodos = 
        CALCULATE(
            [Total Metros],
            ALLEXCEPT(Dim_Calendario, Dim_Calendario[Año Operativo]), -- Limpiamos filtros de mes del calendario
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivo
        )
        
    VAR MetaHace2Periodos = 
        CALCULATE(
            [Meta Acumulada Periodo],
            ALLEXCEPT(Dim_Calendario, Dim_Calendario[Año Operativo]),
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivo
        )
        
    RETURN
    DIVIDE(MetrosHace2Periodos, MetaHace2Periodos, 0),
    
    -- 4. Si el periodo objetivo cae en el año anterior (ej. si estás en Enero/Febrero), manejamos la lógica de cambio de año
    VAR AnioObjetivoAjustado = AnioActual - 1
    VAR PeriodoObjetivoAjustado = PeriodoActual + 12 - 2 -- Ajusta el índice para ir al cierre del año pasado
    
    VAR MetrosAnioPasado = 
        CALCULATE(
            [Total Metros],
            REMOVEFILTERS(Dim_Calendario),
            Dim_Calendario[Año Operativo] = AnioObjetivoAjustado,
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivoAjustado
        )
        
    VAR MetaAnioPasado = 
        CALCULATE(
            [Meta Acumulada Periodo],
            REMOVEFILTERS(Dim_Calendario),
            Dim_Calendario[Año Operativo] = AnioObjetivoAjustado,
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivoAjustado
        )
        
    RETURN
    DIVIDE(MetrosAnioPasado, MetaAnioPasado, 0)
)
```

### 🔹 `[Presupuesto].[metaCosto por Metro CTR]`
```dax
VAR CostoAsignado = MAX(Dim_CTR[Costo por metro])
RETURN
IF(
    ISBLANK(CostoAsignado),
    0, -- O puedes dejarlo como BLANK() si prefieres que las celdas vacías no muestren nada
    CostoAsignado
)
```

### 🔹 `[Presupuesto].[Cumplimiento % Hace 1 Periodo]`
```dax
-- 1. Identificamos el periodo operativo que se está visualizando en el reporte
VAR PeriodoActual = SELECTEDVALUE(Dim_Calendario[Mes Num Operativo])
VAR AnioActual = SELECTEDVALUE(Dim_Calendario[Año Operativo])

-- 2. Calculamos cuál sería el periodo objetivo (1 mes atrás)
VAR PeriodoObjetivo = PeriodoActual - 1

RETURN
IF(
    -- Validamos que estemos dentro del mismo año operativo (Periodo > 0)
    PeriodoObjetivo > 0,
    
    -- 3. Desplazamos el contexto para Metros y Metas usando CALCULATE
    VAR MetrosHace1Periodo = 
        CALCULATE(
            [Total Metros],
            ALLEXCEPT(Dim_Calendario, Dim_Calendario[Año Operativo]), -- Limpiamos filtros de mes del calendario
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivo
        )
        
    VAR MetaHace1Periodo = 
        CALCULATE(
            [Meta Acumulada Periodo],
            ALLEXCEPT(Dim_Calendario, Dim_Calendario[Año Operativo]),
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivo
        )
        
    RETURN
    DIVIDE(MetrosHace1Periodo, MetaHace1Periodo, 0),
    
    -- 4. Si el periodo objetivo cae en el año anterior (ej. si el reporte está en Enero), saltamos al cierre del año pasado
    VAR AnioObjetivoAjustado = AnioActual - 1
    VAR PeriodoObjetivoAjustado = PeriodoActual + 12 - 1 -- Ajusta el índice para ir a Diciembre del año anterior
    
    VAR MetrosAnioPasado = 
        CALCULATE(
            [Total Metros],
            REMOVEFILTERS(Dim_Calendario),
            Dim_Calendario[Año Operativo] = AnioObjetivoAjustado,
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivoAjustado
        )
        
    VAR MetaAnioPasado = 
        CALCULATE(
            [Meta Acumulada Periodo],
            REMOVEFILTERS(Dim_Calendario),
            Dim_Calendario[Año Operativo] = AnioObjetivoAjustado,
            Dim_Calendario[Mes Num Operativo] = PeriodoObjetivoAjustado
        )
        
    RETURN
    DIVIDE(MetrosAnioPasado, MetaAnioPasado, 0)
)
```

### 🔹 `[Presupuesto].[Valor Meta]`
```dax
SUMX(
    VALUES(dim_ctr[CTR]),
    VAR _CostoContrato = CALCULATE(MAX(dim_ctr[Costo por metro]))
    RETURN
    SUMX(
        VALUES('Consumo Consolidado'[Familia]), -- Iteramos la columna que manejas en tu hoja
        VAR _FamiliaActual = 'Consumo Consolidado'[Familia]
        VAR _Porcentaje = 
            CALCULATE(
                MAX(Dim_Familias[%]),
                Dim_Familias[ID_FAMILIA] = _FamiliaActual -- Forzamos el filtro hacia la dimensión
            )
        RETURN
        _CostoContrato * _Porcentaje
    )
)
```

### 🔹 `[Medidas].[Desviación al fin de mes %]`
```dax
-- 1. Obligamos a DAX a sumar las proyecciones evaluando máquina por máquina
VAR TotalProyeccion = 
    SUMX(
        VALUES('Dim_Maquina'[MAQUINA]), 
        [Proyección base]
    )

-- 2. Obligamos a DAX a sumar las metas evaluando máquina por máquina
VAR TotalMeta = 
    SUMX(
        VALUES('Dim_Maquina'[MAQUINA]), 
        [Meta Mensual por maquina]
    )

-- 3. Hacemos la división final segura
RETURN
    DIVIDE(
        TotalProyeccion, 
        TotalMeta, 
        0
    )
```

## 4. Cluster de Control de Tiempos y Horas Operativas

### 🔹 `[Medidas].[Horas Operativas]`
```dax
CALCULATE(
    SUM('Fact_Tiempos'[Horas]),
    'Fact_Tiempos'[Categoria] IN { "OPERATIVO", "EFECTIVAS" }
)
```

### 🔹 `[Medidas].[Horas Perforando con filtro]`
```dax
CALCULATE(
    SUM('Fact_Tiempos'[Horas]),
    KEEPFILTERS('Fact_Tiempos'[Actividad] = "PERFORACION")
)
```

### 🔹 `[Medidas].[Horas Perforando / 6]`
```dax
DIVIDE(CALCULATE(
    SUM('Fact_Tiempos'[Horas]),
    'Fact_Tiempos'[Actividad] = "PERFORACION"
),6)
```

### 🔹 `[Medidas].[Promedio Horas por Turno Perforado]`
```dax
VAR HorasTotales = [Horas Operativas] -- Tu medida original

VAR CantidadTurnosConPerfo = 
    CALCULATE(
        DISTINCTCOUNTNOBLANK('Fact_Tiempos'[KEY_OPERACION]), 
        'Fact_Tiempos'[Actividad] = "PERFORACION"
    )

RETURN
    DIVIDE(HorasTotales, CantidadTurnosConPerfo)
```

### 🔹 `[Medidas].[Promedio Horas Perforando (Sobre Total Turnos)]`
```dax
VAR HorasTotales = [Horas Operativas] -- Tu medida original (ya filtrada por "PERFORACION")

VAR TotalTurnosOperativos = 
    DISTINCTCOUNTNOBLANK('Fact_Tiempos'[KEY_OPERACION])

RETURN
    DIVIDE(HorasTotales, TotalTurnosOperativos)
```

### 🔹 `[Medidas].[Promedio Horas Por Dia]`
```dax
AVERAGEX(
    VALUES('Fact_Tiempos'[Fecha]), -- 1. Crea una lista única de días
    [Horas Operativas]              -- 2. Suma las actividades de cada día
)
```

### 🔹 `[Medidas].[Total Horas]`
```dax
SUM(Fact_Tiempos[Horas])
```

### 🔹 `[Tabla].[Ritmo Base Diario]`
```dax
DIVIDE( SUM(Fact_Metas[META METRAJE]), 30 )
```

### 🔹 `[Tabla].[Ritmo Diario Requerido]`
```dax
VAR PeriodoActual = SELECTEDVALUE('Dim_Calendario'[Periodo Sort])

-- 1. Buscamos el último día del periodo operativo (el 25)
VAR FinDePeriodo = 
    CALCULATE(
        MAX('Dim_Calendario'[Date]), 
        ALLEXCEPT('Dim_Calendario', 'Dim_Calendario'[Periodo Sort])
    )

-- 2. Metros que faltan
VAR MetaTotal = CALCULATE([Meta Mensual], ALLSELECTED('Dim_Calendario'))
VAR AvanceActual = [Total Metros]
VAR MetrosFaltantes = MetaTotal - AvanceActual

-- 3. CAMBIO CLAVE: Identificamos la última fecha donde HUBO metros
-- Reemplaza 'Tabla_Hechos'[Fecha] por tu columna real de perforación
VAR UltimaFechaData = CALCULATE(MAX('Fact_Metraje'[FECHA]), ALLSELECTED('Fact_Metraje'))

-- 4. Días desde la última data hasta el cierre
VAR DiasRestantes = 
    COUNTROWS(
        FILTER(
            ALL('Dim_Calendario'),
            'Dim_Calendario'[Date] > UltimaFechaData && 
            'Dim_Calendario'[Date] <= FinDePeriodo &&
            'Dim_Calendario'[Periodo Sort] = PeriodoActual
        )
    )

RETURN
IF(
    MetrosFaltantes <= 0, 0, 
    DIVIDE(MetrosFaltantes, DiasRestantes, 0)
)
```

### 🔹 `[Medidas].[Dias Mes Operativo]`
```dax
CALCULATE(
    COUNTROWS('Dim_Calendario'),
    ALLEXCEPT('Dim_Calendario', 'dim_Calendario'[Periodo Sort])
)
```

### 🔹 `[Medidas].[Dias Operativos Transcurridos]`
```dax
VAR FechaHoy = TODAY()
VAR PeriodoActual = SELECTEDVALUE(dim_calendario[periodo sort])

RETURN
    CALCULATE(
        COUNTROWS(dim_calendario),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[periodo sort] = PeriodoActual,
        dim_calendario[Date] <= FechaHoy
    )-1
```

### 🔹 `[Medidas].[Dias Operativos Restantes]`
```dax
// 1. Obtenemos la última fecha con registros reales en la tabla de hechos
VAR UltimaFechaDatos = LASTDATE(fact_metraje[fecha])

// 2. Identificamos el periodo al que pertenece esa última fecha
VAR PeriodoActual = 
    CALCULATE(
        SELECTEDVALUE(dim_calendario[periodo sort]),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[Date] = UltimaFechaDatos
    )

-- Calculamos el total de días del periodo seleccionado
VAR DiasTotalesPeriodo = 
    CALCULATE(
        COUNTROWS(dim_calendario),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[periodo sort] = PeriodoActual
    )

-- Calculamos los días que ya pasaron hasta la última actualización
VAR DiasTranscurridos = 
    CALCULATE(
        COUNTROWS(dim_calendario),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[periodo sort] = PeriodoActual,
        dim_calendario[Date] <= UltimaFechaDatos
    )

-- El resultado es la diferencia
RETURN
    DiasTotalesPeriodo - DiasTranscurridos
```

### 🔹 `[Medidas].[Horas Efectivas]`
```dax
CALCULATE(
    SUM('Fact_Tiempos'[Horas]),
    'Fact_Tiempos'[Categoria] IN {"EFECTIVAS" }
)
```

### 🔹 `[Medidas].[Promedio Horas efectivas Por Dia]`
```dax
AVERAGEX(
    VALUES('Fact_Tiempos'[Fecha]), -- 1. Crea una lista única de días
    [Horas Efectivas]              -- 2. Suma las actividades de cada día
)
```

### 🔹 `[Medidas].[Semana Operativa Actual]`
```dax
nan
```

### 🔹 `[Presupuesto].[Semana Operativa proyectada]`
```dax
// 1. Obtenemos la última fecha con registros reales como valor escalar
VAR UltimaFechaDatos = INT(MAX(fact_metraje[fecha]))

// 2. Sumamos 5 días a esa fecha limpia
VAR FechaProyectada = UltimaFechaDatos+5
// 3. Identificamos la semana operativa a la que pertenece esa nueva fecha futura
VAR SemanaSiguiente = 
    CALCULATE(
        SELECTEDVALUE(dim_calendario[semana operativa]),
        REMOVEFILTERS(dim_calendario),
        dim_calendario[Date] = FechaProyectada 
    )

-- Retornamos el valor de la semana operativa proyectada
RETURN
    SemanaSiguiente
```

### 🔹 `[Presupuesto].[Semana Operativa proyectada 987 987 987]`
```dax
// 1. Obtenemos la última fecha con registros reales como valor escalar
VAR UltimaFechaDatos = MAX(fact_metraje[fecha])

// 2. Sumamos 5 días a esa última fecha
VAR FechaProyectada = UltimaFechaDatos + 5
RETURN (FechaProyectada)
```

### 🔹 `[Disponibilidad global].[VAR Horas_disminuyen_dg]`
```dax
CALCULATE(
            SUM(fact_tiempos[horas]),
            fact_tiempos[Afecta_disp] = "AFECTA"
        )
```

### 🔹 `[Disponibilidad global].[Metros_por_guardia_ideales]`
```dax
DIVIDE( [Meta Mensual por maquina], 60 )
```

### 🔹 `[Disponibilidad global].[Dias Sin Perforar]`
```dax
// 1. Encontramos la última fecha donde los metros fueron mayores a 0 en todo el contexto
VAR UltimaFechaPerforacion = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]), 
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

// 2. Definimos la fecha de referencia (Último registro de la tabla en lugar de Hoy)
VAR FechaActual = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        ALLSELECTED('Fact_Metraje')
    )

// 3. Calculamos la diferencia en días
VAR DiferenciaDias = 
    DATEDIFF(UltimaFechaPerforacion, FechaActual, DAY)

RETURN
    IF(ISBLANK(UltimaFechaPerforacion), BLANK(), DiferenciaDias)
```

### 🔹 `[Disponibilidad global].[Turnos Sin Perforar]`
```dax
// 1. Buscamos la última FECHA con perforación (metros > 0) en todo el contexto del reporte
VAR UltimaFechaPerforacion = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

// 2. Buscamos cuál fue el último TURNO con perforación de esa fecha
VAR UltimoTurnoRegistrado = 
    CALCULATE(
        MAX('Fact_Metraje'[Turno]),
        'Fact_Metraje'[Fecha] = UltimaFechaPerforacion,
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

VAR UltimoTurnoNum = 
    IF(UltimoTurnoRegistrado = "Noche" || UltimoTurnoRegistrado = "2", 2, 1)


// =========================================================================
// 4. NUEVA LÓGICA: Definimos el momento de referencia según el último dato de la tabla
// =========================================================================

// Buscamos la última fecha absoluta registrada en la base de datos para el reporte
VAR FechaActual = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        ALLSELECTED('Fact_Metraje')
    )

// Buscamos cuál fue el último turno registrado en esa fecha máxima
VAR TurnoActualRegistrado = 
    CALCULATE(
        MAX('Fact_Metraje'[Turno]),
        'Fact_Metraje'[Fecha] = FechaActual,
        ALLSELECTED('Fact_Metraje')
    )

VAR TurnoActualNum = 
    IF(TurnoActualRegistrado = "Noche" || TurnoActualRegistrado = "2", 2, 1)


// 5. Calculamos la diferencia matemática en turnos
VAR DiferenciaDias = DATEDIFF(UltimaFechaPerforacion, FechaActual, DAY)
VAR DiferenciaTurnos = (DiferenciaDias * 2) + (TurnoActualNum - UltimoTurnoNum)

RETURN
    IF(ISBLANK(UltimaFechaPerforacion), BLANK(), DiferenciaTurnos)
```

## 5. Cluster de Metraje Perdido y Disponibilidad Global

### 🔹 `[Tabla].[Metros Perdidos]`
```dax
-- 1. Variables de Referencia
VAR _ROP_General = 
    CALCULATE(
        [ROP (m/hr)], 
        REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
    )

VAR _ActividadFila = SELECTEDVALUE('fact_tiempos'[ACTIVIDAD])
VAR _CategoriaFila = SELECTEDVALUE('fact_tiempos'[Categoria])
VAR _HorasFila = [Total Horas]

-- 2. CÁLCULO PARA PÉRDIDAS DIRECTAS (Categoría o Actividad específica)
VAR _EsPerdidaDirecta = 
    _CategoriaFila = "STAND BY CLIENTE" || 
    _ActividadFila IN {
        "FALTA_DE_PERSONAL", 
        "FALTA_CAMIONETA_Y/O_CAMIÓN", 
        "FALTA/PROBLEMAS_MATERIALES", 
        "FALTA_DE_CISTERNA"
    }

VAR _MetrosDirectosFila = IF(_EsPerdidaDirecta, _HorasFila * _ROP_General, 0)

-- 3. LÓGICA DE MANTENIMIENTO
-- Cálculo de horas totales de Preventivo en el contexto actual (ej. por Máquina/Contrato)
VAR _HorasPrevTotal = 
    CALCULATE(
        [Total Horas], 
        'fact_tiempos'[ACTIVIDAD] = "MANTTO_PREVENTIVO",
        REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
    )

VAR _ExcesoPrevTotal = MAX(_HorasPrevTotal - 30, 0)

-- Asignación por fila
VAR _MetrosManttoFila = 
    SWITCH(_ActividadFila,
        "MANTTO_PREVENTIVO", (_ExcesoPrevTotal * _ROP_General) * DIVIDE(_HorasFila, _HorasPrevTotal, 0),
        "MANTTO_CORRECTIVO", _HorasFila * _ROP_General,
        0
    )

-- 4. RESULTADO FINAL (Gestión de Totales)
RETURN
IF(
    ISINSCOPE('fact_tiempos'[ACTIVIDAD]),
    _MetrosDirectosFila + _MetrosManttoFila, 
    
    -- Cálculo para el Total General
    VAR _HorasDirectasTotal = 
        CALCULATE(
            [Total Horas], 
            'fact_tiempos'[Categoria] = "STAND BY CLIENTE" || 
            'fact_tiempos'[ACTIVIDAD] IN {
                "FALTA_DE_PERSONAL", "FALTA_CAMIONETA_Y/O_CAMIÓN", 
                "FALTA/PROBLEMAS_MATERIALES", "FALTA_DE_CISTERNA"
            },
            REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
        )
    VAR _HorasCorrectivoTotal = 
        CALCULATE(
            [Total Horas], 
            'fact_tiempos'[ACTIVIDAD] = "MANTTO_CORRECTIVO",
            REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
        )
    
    RETURN 
        (_HorasDirectasTotal * _ROP_General) + 
        (_HorasCorrectivoTotal * _ROP_General) + 
        (_ExcesoPrevTotal * _ROP_General)
)
```

### 🔹 `[Disponibilidad global].[Metros Perdidos DG]`
```dax
-- 1. Variables de Referencia
-- IMPORTANTE: Usamos REMOVEFILTERS en el ROP para que no dé 0 al estar en una fila sin producción
VAR _ROP_General = 
    CALCULATE(
        [ROP (m/hr)], 
        REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
    )

VAR _ActividadFila = SELECTEDVALUE('fact_tiempos'[ACTIVIDAD])
VAR _CategoriaFila = SELECTEDVALUE('fact_tiempos'[Categoria])

-- 2. CÁLCULO PARA PÉRDIDAS DIRECTAS (Lógica OR: Categoría o Actividad)
VAR _EsPerdidaDirecta = 
    _CategoriaFila = "STAND BY CLIENTE" || 
    _ActividadFila IN {
        "FALTA_DE_PERSONAL", 
        "FALTA_DE_CAMIONETA_Y/O_CAMION", 
        "FALTA/PROBLEMAS_MATERIALES", 
        "FALTA_DE_CISTERNA"
    }

VAR _MetrosDirectosFila = 
    IF(
        _EsPerdidaDirecta,
        [Total Horas] * _ROP_General,
        0
    )

-- 3. CÁLCULO PARA MANTENIMIENTO (Mantenemos tu lógica original del 5%)
VAR _TotalHorasReloj = 
    CALCULATE(
        [Total Horas], 
        REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
    )

VAR _LimiteMantto = _TotalHorasReloj * 0.05 

VAR _HorasManttoTotal = 
    CALCULATE(
        [Total Horas], 
        'fact_tiempos'[ACTIVIDAD] IN {"MANTTO_PREVENTIVO", "MANTTO_CORRECTIVO"},
        REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
    )

VAR _ExcesoManttoGlobal = MAX(_HorasManttoTotal - _LimiteMantto, 0)

-- Distribuimos el exceso proporcionalmente en las filas de mantenimiento
VAR _MetrosManttoFila = 
    IF(
        _ActividadFila IN {"MANTTO_PREVENTIVO", "MANTTO_CORRECTIVO"},
        (_ExcesoManttoGlobal * _ROP_General) * DIVIDE([Total Horas], _HorasManttoTotal, 0),
        0
    )

-- 4. RESULTADO FINAL
RETURN
IF(
    ISINSCOPE('fact_tiempos'[ACTIVIDAD]),
    _MetrosDirectosFila + _MetrosManttoFila, 
    
    -- Valor para el Total (Suma de directos + exceso de mantenimiento):
    VAR _HorasDirectasTotal = 
        CALCULATE(
            [Total Horas], 
            'fact_tiempos'[Categoria] = "STAND BY CLIENTE" || 
            'fact_tiempos'[ACTIVIDAD] IN {
                "FALTA_DE_PERSONAL", 
                "FALTA_DE_CAMIONETA_Y/O_CAMION", 
                "FALTA/PROBLEMAS_MATERIALES", 
                "FALTA_DE_CISTERNA"
            },
            REMOVEFILTERS('fact_tiempos'[ACTIVIDAD], 'fact_tiempos'[Categoria])
        )
    RETURN 
        (_HorasDirectasTotal * _ROP_General) + (_ExcesoManttoGlobal * _ROP_General)
)
```

### 🔹 `[Disponibilidad global].[Metros DG]`
```dax
// Paso 1: Identificar el tipo de máquina
    VAR Tipo_maquina_texto = SELECTEDVALUE(Fact_Metas[TIPO_MAQUINA]) 
    VAR Tipo_maquina = 
        SWITCH(
            Tipo_maquina_texto,
            "mina", 14,
            "superficie", 16,
            BLANK() 
        )

    // Paso 2: Calcular metros por día
    VAR Metros_por_dia = 
        DIVIDE( [Meta Mensual por maquina], 30 )

    // Paso 3: Calcular el ratio esperado
    VAR Ratio_esperado = 
        DIVIDE( Metros_por_dia, Tipo_maquina )

    // Paso 4: Calcular las horas afectadas solo para la actividad de esta fila
    VAR Horas_disminuyen_dg = 
        CALCULATE(
            SUM(fact_tiempos[horas]),
            fact_tiempos[Afecta_disp] = "AFECTA"
        )
        
    // Paso 5: CORRECCIÓN. Usamos la variable 'Ratio_esperado' 
    // en lugar de llamar a la medida externa '[Ratio ideal]'
    VAR Metros_perdidos = 
        Ratio_esperado * Horas_disminuyen_dg

// Retornamos los metros perdidos para que cuadre con tu matriz visual
RETURN 
    Metros_perdidos
```

### 🔹 `[Disponibilidad global].[VAR Horas_disminuyen_dg]`
```dax
CALCULATE(
            SUM(fact_tiempos[horas]),
            fact_tiempos[Afecta_disp] = "AFECTA"
        )
```

### 🔹 `[Disponibilidad global].[Valor Perdido]`
```dax
SUMX(
        DIM_CTR,
        [Metros DG] * DIM_CTR[P.U. PROMEDIO]
    )
```

### 🔹 `[Disponibilidad global].[Dias Sin Perforar]`
```dax
// 1. Encontramos la última fecha donde los metros fueron mayores a 0 en todo el contexto
VAR UltimaFechaPerforacion = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]), 
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

// 2. Definimos la fecha de referencia (Último registro de la tabla en lugar de Hoy)
VAR FechaActual = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        ALLSELECTED('Fact_Metraje')
    )

// 3. Calculamos la diferencia en días
VAR DiferenciaDias = 
    DATEDIFF(UltimaFechaPerforacion, FechaActual, DAY)

RETURN
    IF(ISBLANK(UltimaFechaPerforacion), BLANK(), DiferenciaDias)
```

### 🔹 `[Disponibilidad global].[Valor no ganado]`
```dax
SUMX(
        DIM_CTR,
        [Metros NO PERFORADOS]* DIM_CTR[P.U. PROMEDIO]
    )
```

### 🔹 `[Disponibilidad global].[Turnos Sin Perforar]`
```dax
// 1. Buscamos la última FECHA con perforación (metros > 0) en todo el contexto del reporte
VAR UltimaFechaPerforacion = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

// 2. Buscamos cuál fue el último TURNO con perforación de esa fecha
VAR UltimoTurnoRegistrado = 
    CALCULATE(
        MAX('Fact_Metraje'[Turno]),
        'Fact_Metraje'[Fecha] = UltimaFechaPerforacion,
        'Fact_Metraje'[METRAJE_X_GUARDIA] > 0,
        ALLSELECTED('Fact_Metraje')
    )

VAR UltimoTurnoNum = 
    IF(UltimoTurnoRegistrado = "Noche" || UltimoTurnoRegistrado = "2", 2, 1)


// =========================================================================
// 4. NUEVA LÓGICA: Definimos el momento de referencia según el último dato de la tabla
// =========================================================================

// Buscamos la última fecha absoluta registrada en la base de datos para el reporte
VAR FechaActual = 
    CALCULATE(
        MAX('Fact_Metraje'[Fecha]),
        ALLSELECTED('Fact_Metraje')
    )

// Buscamos cuál fue el último turno registrado en esa fecha máxima
VAR TurnoActualRegistrado = 
    CALCULATE(
        MAX('Fact_Metraje'[Turno]),
        'Fact_Metraje'[Fecha] = FechaActual,
        ALLSELECTED('Fact_Metraje')
    )

VAR TurnoActualNum = 
    IF(TurnoActualRegistrado = "Noche" || TurnoActualRegistrado = "2", 2, 1)


// 5. Calculamos la diferencia matemática en turnos
VAR DiferenciaDias = DATEDIFF(UltimaFechaPerforacion, FechaActual, DAY)
VAR DiferenciaTurnos = (DiferenciaDias * 2) + (TurnoActualNum - UltimoTurnoNum)

RETURN
    IF(ISBLANK(UltimaFechaPerforacion), BLANK(), DiferenciaTurnos)
```

### 🔹 `[Medidas].[Metros Perdidos Stand By Servicios Cliente]`
```dax
// 1. ROP de Perforación aislado de filtros de actividad/categoría de la fila
VAR _ROP_Efectivo = 
    CALCULATE(
        [ROP Solo Perforacion (m/hr)],
        REMOVEFILTERS('Fact_Tiempos'[Actividad], 'Fact_Tiempos'[Categoria])
    )

// 2. Horas registradas en las actividades de falta de servicios del cliente
VAR _HorasServiciosCliente = 
    CALCULATE(
        SUM('Fact_Tiempos'[Horas]),
        'Fact_Tiempos'[Actividad] IN { "FALTA_DE_AGUA", "FALTA_DE_ENERGIA", "FALTA_DE_VENTILACION" }
    )

// 3. Metros no perforados a causa de estas paradas
RETURN
    _HorasServiciosCliente * _ROP_Efectivo
```

### 🔹 `[Medidas].[Metros Perdidos Falta de Personal]`
```dax
// 1. ROP de Perforación aislado de filtros de actividad/categoría de la fila
VAR _ROP_Efectivo = 
    CALCULATE(
        [ROP Solo Perforacion (m/hr)],
        REMOVEFILTERS('Fact_Tiempos'[Actividad], 'Fact_Tiempos'[Categoria])
    )

// 2. Horas registradas en la actividad falta de personal
VAR _HorasFaltaPersonal = 
    CALCULATE(
        SUM('Fact_Tiempos'[Horas]),
        'Fact_Tiempos'[Actividad] = "FALTA_DE_PERSONAL"
    )

// 3. Metros no perforados a causa de falta de personal
RETURN
    _HorasFaltaPersonal * _ROP_Efectivo
```

## 6. Cluster de Costos y Control Presupuestal

### 🔹 `[Medidas].[Costo Abastecimiento ($)]`
```dax
CALCULATE(
    SUM('Fact_Abastecimiento'[TOTAL])
)
```

### 🔹 `[Medidas].[Costo Consumo  ($)]`
```dax
CALCULATE(
    SUM('Consumo Consolidado'[Total])
)
```

### 🔹 `[Medidas].[Costo Consumo x Metro ($/m)]`
```dax
DIVIDE(
    [Costo Consumo  ($)], 
    [Total Metros], 
    0
)
```

### 🔹 `[Medidas].[Costo Abastecimiento x Metro ($/m)]`
```dax
DIVIDE(
    [Costo Abastecimiento MTD Operativo ($)], 
    [Total Metros], 
    0
)
```

### 🔹 `[Medidas].[Costo Cantidad]`
```dax
[Consumo Cantidad] * [Total Metros]
```

### 🔹 `[Medidas].[Costo total]`
```dax
SUMX(
    'Consumo Consolidado', 
    'Consumo Consolidado'[Cant] * 'Consumo Consolidado'[Costo]
)
```

### 🔹 `[Medidas].[Abastecimiento Cantidad]`
```dax
SUM('Fact_Abastecimiento'[CANT])
```

### 🔹 `[Medidas].[Meta Costo CTR]`
```dax
-- 1. Identificamos el CTR activo en el contexto (ya sea por filtro de máquina o de proyecto)
VAR _CTR_Seleccionado = SELECTEDVALUE('fact_tiempos'[CTR])

-- 2. Buscamos el costo en la DIM_CTR usando LOOKUPVALUE para evitar conflictos de relación
VAR _ValorMeta = 
    LOOKUPVALUE(
        'DIM_CTR'[Costo por metro], 
        'DIM_CTR'[CTR], 
        _CTR_Seleccionado
    )

-- 3. Si el CTR no tiene meta (celdas vacías), usamos el promedio de los CTRs con data
VAR _PromedioSeguridad = 
    CALCULATE(
        AVERAGE('DIM_CTR'[Costo por metro]), 
        ALLSELECTED('DIM_CTR')
    )

RETURN 
    IF(ISBLANK(_ValorMeta), _PromedioSeguridad, _ValorMeta)
```

### 🔹 `[Medidas].[CXM ADIT]`
```dax
[Meta Costo CTR]*.1833
```

### 🔹 `[Medidas].[CXM PDD]`
```dax
[Meta Costo CTR]*.2083
```

### 🔹 `[Presupuesto].[metaCosto por Metro CTR]`
```dax
VAR CostoAsignado = MAX(Dim_CTR[Costo por metro])
RETURN
IF(
    ISBLANK(CostoAsignado),
    0, -- O puedes dejarlo como BLANK() si prefieres que las celdas vacías no muestren nada
    CostoAsignado
)
```

### 🔹 `[Presupuesto].[Presupuesto]`
```dax
-- 1. Capturamos el presupuesto total base
VAR PresupuestoTotal = [metaCosto por Metro CTR] * [Meta Acumulada Periodo]

-- 2. Capturamos el porcentaje de la familia en la fila actual
VAR PorcentajeFamilia = SUM(Dim_Familias[%]) 

RETURN
IF(
    -- Validamos que exista un presupuesto base para calcular
    NOT(ISBLANK(PresupuestoTotal)) && PresupuestoTotal <> 0,
    
    -- Multiplicamos el total por el peso de la familia (ej. $11,000 * 0.1667)
    PresupuestoTotal * PorcentajeFamilia,
    
    BLANK()
)
```

### 🔹 `[Presupuesto].[Presupuesto Proyectado 15 días V2]`
```dax
-- =========================================================================
-- PASO 1: BASE DE PRESUPUESTO MONETARIO A 15 DÍAS
-- =========================================================================
VAR PresupuestoMensual = [Presupuesto]
VAR Presupuesto15DiasBase = DIVIDE(PresupuestoMensual, 1, 0)

-- =========================================================================
-- PASO 2: FACTOR 1 - PROMEDIO HISTÓRICO (HACE 1 Y 2 PERIODOS)
-- =========================================================================
VAR HistorialPeriodo1 = [Cumplimiento % Hace 1 Periodo]
VAR HistorialPeriodo2 = [Cumplimiento % Hace 2 Periodos]

VAR FactorCumplimientoHistorico = 
    DIVIDE(
        HistorialPeriodo1 + HistorialPeriodo2, 
        2, 
        0
    )

-- =========================================================================
-- PASO 3: FACTOR 2 - PROYECCIÓN FÍSICA BASADA EN TERRENO (INGENIERÍA)
-- =========================================================================
-- Usamos COALESCE para blindar la fórmula y evitar vacíos (BLANK) si no hay días/horas pendientes
VAR ROP = COALESCE([ROP (m/hr)], 0)
VAR DiasRestantes = COALESCE([Dias Operativos Restantes], 0)
VAR PromedioHoras = COALESCE([Promedio Horas Por Dia], 0)
VAR MetrosActuales = COALESCE([Total Metros], 0)

-- Calculamos la estimación de metros al cierre según rendimiento en campo
VAR MetrosProyectadosRendimiento = (ROP * DiasRestantes * PromedioHoras) + MetrosActuales

-- Convertimos esa proyección física en un porcentaje de cumplimiento respecto a la meta
VAR FactorCumplimientoRendimiento = 
    DIVIDE(
        MetrosProyectadosRendimiento, 
        [Meta Acumulada Periodo], 
        0
    )

-- =========================================================================
-- PASO 4: PROMEDIO DE AMBOS ENFOQUES DE EFICIENCIA (CORREGIDO)
-- =========================================================================
VAR FactorCombinadoPromedio = 
    IF(
        -- Si no quedan días operativos restantes, ignoramos la proyección de campo
        -- y nos quedamos al 100% con la eficiencia histórica de los periodos previos
        [Dias Operativos Restantes] <= 0 || ISBLANK([Dias Operativos Restantes]),
        FactorCumplimientoHistorico,
        
        -- Si aún hay días en el periodo, hacemos el promedio balanceado original
        DIVIDE(FactorCumplimientoHistorico + FactorCumplimientoRendimiento, 2, 0)
    )
-- =========================================================================
-- PASO 5: RESULTADO MONETARIO FINAL
-- =========================================================================
RETURN
IF(
    NOT(ISBLANK(PresupuestoMensual)),
    
    -- Multiplicamos la base monetaria por el factor final balanceado
    Presupuesto15DiasBase * FactorCombinadoPromedio,
    
    BLANK()
)
```

### 🔹 `[Consumo Consolidado].[Presupuesto PDD]`
```dax
[metaCosto por Metro CTR] *[Meta Acumulada Periodo]*.2088
```

### 🔹 `[Presupuesto].[Presupuesto pdd S]`
```dax
[metaCosto por Metro CTR] *[Meta Acumulada Periodo]*.2083/4
```

### 🔹 `[Presupuesto].[Presupuesto Semanal PDD Ajustado]`
```dax
-- 1. Contamos las semanas totales del mes operativo en curso
VAR SemanasMesOperativo = 
    CALCULATE(
        DISTINCTCOUNT('Dim_Calendario'[Semana Num]),
        ALLSELECTED('Dim_Calendario')
    )

-- 2. Capturamos el presupuesto filtrando por el nombre exacto de la familia
VAR PresupuestoPDD = 
    CALCULATE(
        [PRESUPUESTO FINAL],
        'Dim_Familias'[ID_FAMILIA] = "PDD" 
    )

-- 5. Dividimos el presupuesto ajustado entre la cantidad de semanas
RETURN
IF(
    NOT(ISBLANK(PresupuestoPDD)) && SemanasMesOperativo > 0,
    DIVIDE([PRESUPUESTO FINAL], SemanasMesOperativo, BLANK()),
    BLANK()
)
```

### 🔹 `[Presupuesto].[Valor Meta]`
```dax
SUMX(
    VALUES(dim_ctr[CTR]),
    VAR _CostoContrato = CALCULATE(MAX(dim_ctr[Costo por metro]))
    RETURN
    SUMX(
        VALUES('Consumo Consolidado'[Familia]), -- Iteramos la columna que manejas en tu hoja
        VAR _FamiliaActual = 'Consumo Consolidado'[Familia]
        VAR _Porcentaje = 
            CALCULATE(
                MAX(Dim_Familias[%]),
                Dim_Familias[ID_FAMILIA] = _FamiliaActual -- Forzamos el filtro hacia la dimensión
            )
        RETURN
        _CostoContrato * _Porcentaje
    )
)
```

### 🔹 `[Medidas].[Costo Abastecimiento MTD Operativo ($)]`
```dax
VAR MaxFecha = MAX('Fact_Abastecimiento'[FECHA])

RETURN
CALCULATE(
    SUM('Fact_Abastecimiento'[TOTAL]),
    
    -- Filtro original: Acumulado de fechas (MTD) respetando otros filtros
    FILTER(
        ALLSELECTED('Fact_Abastecimiento'[FECHA]),
        'Fact_Abastecimiento'[FECHA] <= MaxFecha
    ),
    
    -- Nuevo filtro: Solo toma en cuenta los valores SO, TD, RP en la columna TRA
    'Fact_Abastecimiento'[TRA] IN {"SO", "TD", "RP"}
)
```

### 🔹 `[Presupuesto].[Presupuesto Proyectado 15 días V3]`
```dax
-- =========================================================================
-- PASO 1: BASE DE PRESUPUESTO MONETARIO AJUSTADO A 15 DÍAS
-- =========================================================================
VAR PresupuestoMensual = [Presupuesto]
VAR CostoAbastecimientoMTD = [Costo Abastecimiento MTD Operativo ($)]

-- Restamos el costo acumulado operativo al presupuesto antes de la proyección
VAR PresupuestoAjustado = PresupuestoMensual - CostoAbastecimientoMTD
VAR Presupuesto15DiasBase = DIVIDE(PresupuestoAjustado, 1, 0)

-- =========================================================================
-- PASO 2: FACTOR 1 - PROMEDIO HISTÓRICO (HACE 1 Y 2 PERIODOS)
-- =========================================================================
VAR HistorialPeriodo1 = [Cumplimiento % Hace 1 Periodo]
VAR HistorialPeriodo2 = [Cumplimiento % Hace 2 Periodos]

VAR FactorCumplimientoHistorico = 
    DIVIDE(
        HistorialPeriodo1 + HistorialPeriodo2, 
        2, 
        0
    )

VAR CONDICIONAL = 
    IF(
        PresupuestoAjustado <= CostoAbastecimientoMTD,
        0, 
        PresupuestoAjustado * FactorCumplimientoHistorico
    )
    
RETURN
    IF(
        NOT(ISBLANK(PresupuestoMensual)),
        -- Multiplicamos la base neta monetaria por el factor final de eficiencia de campo/histórica
        CONDICIONAL,
        BLANK()
    )
```

### 🔹 `[Presupuesto].[Ptto - abast]`
```dax
VAR PresupuestoFila = [Presupuesto]
VAR CostoFila = [Costo Abastecimiento MTD Operativo ($)]

RETURN
IF(
    NOT(ISBLANK(PresupuestoFila)),
    PresupuestoFila - CostoFila, -- Presupuesto menos lo gastado
    BLANK()
)
```

### 🔹 `[Presupuesto].[Presupuesto Proyectado 15 días V4]`
```dax
VAR PresupuestoMensual = [Presupuesto]
VAR CostoAbastecimientoMTD = [Costo Abastecimiento MTD Operativo ($)]
VAR PresupuestoRestatnte= 0
-- Restamos el costo acumulado operativo al presupuesto antes de la proyección
VAR PresupuestoAjustado = PresupuestoMensual - CostoAbastecimientoMTD
VAR Presupuesto15DiasBase = DIVIDE(PresupuestoAjustado, 1, 0)

-- =========================================================================
-- PASO 2: FACTOR 1 - PROMEDIO HISTÓRICO (HACE 1 Y 2 PERIODOS)
-- =========================================================================
VAR HistorialPeriodo1 = [Cumplimiento % Hace 1 Periodo]
VAR HistorialPeriodo2 = [Cumplimiento % Hace 2 Periodos]

VAR FactorCumplimientoHistorico = 
    DIVIDE(
        HistorialPeriodo1 + HistorialPeriodo2, 
        2, 
        0
    )

VAR CONDICIONAL = 
    IF(
        PresupuestoAjustado <= CostoAbastecimientoMTD,
        0, 
        PresupuestoAjustado * FactorCumplimientoHistorico
    )
    
RETURN
    IF(
        NOT(ISBLANK(PresupuestoMensual)),
        -- Multiplicamos la base neta monetaria por el factor final de eficiencia de campo/histórica
        CONDICIONAL,
        BLANK()
    )
```

### 🔹 `[Presupuesto].[PRESUPUESTO FINAL]`
```dax
VAR SEMANA = [Semana Operativa proyectada]
VAR PRESUPUESTOBASE = [Presupuesto]
VAR HACE1 = [Cumplimiento % Hace 1 Periodo]
VAR HACE2 = [Cumplimiento % Hace 2 Periodos]
VAR ABASTECIMIENTO = [Costo Abastecimiento MTD Operativo ($)]

-- Protegemos la desviación por si esa medida es la que está arrojando el error
VAR DESVIACION = IFERROR([Desviación al fin de mes %], 0) 

-- =========================================================
-- PRIMERA QUINCENA (Semanas 1 y 2)
-- =========================================================
VAR FACTORHISTORICO =
    DIVIDE(
        HACE1 + HACE2,
        2,
        0
    )

VAR PPTOAJUSTADO = FACTORHISTORICO * PRESUPUESTOBASE
VAR AJUSTE_ABASTE = PPTOAJUSTADO - ABASTECIMIENTO
VAR ERR = 
    IF (AJUSTE_ABASTE <= 0,
        0,
        AJUSTE_ABASTE
    )
VAR PPTOQUINCENA1 = ERR / 2

-- =========================================================
-- SEGUNDA QUINCENA (Semanas 3, 4 y 5)
-- =========================================================
VAR PPTOAJUSTADO2 = PRESUPUESTOBASE * DESVIACION
VAR AJUSTE_ABASTE2 = PPTOAJUSTADO2 - ABASTECIMIENTO
VAR PPTOQUINCENA2 = 
    IF(
        AJUSTE_ABASTE2 <= 0,  
        0,                  
        AJUSTE_ABASTE2        
    )

-- =========================================================
-- RESULTADO FINAL (Selección dinámica)
-- =========================================================
RETURN
    IF(
        SEMANA IN {"SEM 01", "SEM 02"},
        PPTOQUINCENA1,
        PPTOQUINCENA2
    )
```

## 7. Cluster de Brocas y Consumo de Insumos

### 🔹 `[Medidas].[Cantidad Brocas]`
```dax
CALCULATE(
    DISTINCTCOUNT('Fact_Metraje'[Nº_BROCA]),
    // IMPORTANTE: El "0" debe ir entre comillas porque la columna ahora es Texto
    'Fact_Metraje'[Nº_BROCA] <> "0",
    'Fact_Metraje'[Nº_BROCA] <> "ND",
    'Fact_Metraje'[Nº_BROCA] <> ""
)
```

### 🔹 `[Medidas].[Cantidad Brocas Usadas]`
```dax
CALCULATE(
    COUNTROWS('Reporte_Brocas'),
    TREATAS(VALUES('Dim_Broca'[Serie]), 'Reporte_Brocas'[Nº_BROCA])
)
```

### 🔹 `[Medidas].[Consumo Cantidad]`
```dax
SUM('Consumo Consolidado'[Cant])
```

### 🔹 `[Medidas].[Prom Cantidad]`
```dax
AVERAGE('Consumo Consolidado'[Cant])
```

### 🔹 `[Medidas].[Cantidad Maquinas Activas]`
```dax
CALCULATE(
    DISTINCTCOUNT('Fact_Metraje'[MAQUINA]),
    'Fact_Metraje'[METRAJE_X_GUARDIA] > 0
)
```

### 🔹 `[Medidas].[Abastecimiento Cantidad]`
```dax
SUM('Fact_Abastecimiento'[CANT])
```

### 🔹 `[Medidas].[Ocultar Sondajes Sin Datos]`
```dax
IF(
    ISBLANK(SUM('Fact_Metraje'[METRAJE_X_GUARDIA])) && 
    ISBLANK(SUM('Fact_Tiempos'[Horas])), 
    0, 
    1
)
```

### 🔹 `[Medidas].[Consumo_Sondaje]`
```dax
-- 1. Identificamos las fechas del sondaje seleccionado en el Gantt
VAR FechaInicioSondaje = MIN(Dim_Sondaje[FECHA_INICIO_REAL])
VAR FechaFinSondaje = MAX(Dim_Sondaje[FECHA_FIN_REAL])
VAR MaquinaSeleccionada = SELECTEDVALUE(Dim_Maquina[MAQUINA])

RETURN
CALCULATE(
    SUM('Consumo Consolidado'[Total]), -- O la columna de costo que uses
    -- 2. Forzamos que el filtro viaje de la Dim_Maquina al Consumo
    CROSSFILTER(Dim_Maquina[MAQUINA], 'Consumo Consolidado'[Maquina], Both),
    -- 3. Filtramos explícitamente el rango de tiempo del sondaje
    'Consumo Consolidado'[Fecha] >= FechaInicioSondaje,
    'Consumo Consolidado'[Fecha] <= FechaFinSondaje
)
```

### 🔹 `[Medidas].[Cantidad_Sondaje]`
```dax
-- 1. Identificamos las fechas del sondaje seleccionado
VAR FechaInicioSondaje = MIN(Dim_Sondaje[FECHA_INICIO_REAL])
VAR FechaFinSondaje = MAX(Dim_Sondaje[FECHA_FIN_REAL])

RETURN
CALCULATE(
    SUM('Consumo Consolidado'[Cant]), -- Cambia [Cantidad] por el nombre real de tu columna de unidades
    -- 2. Mantenemos la relación bidireccional para filtrar por máquina
    CROSSFILTER(Dim_Maquina[MAQUINA], 'Consumo Consolidado'[Maquina], Both),
    -- 3. Filtramos por el rango de fechas del sondaje
    'Consumo Consolidado'[Fecha] >= FechaInicioSondaje,
    'Consumo Consolidado'[Fecha] <= FechaFinSondaje
)
```

### 🔹 `[Consumo Consolidado].[Cantidad Brocas consumidas]`
```dax
CALCULATE(
    DISTINCTCOUNT('Consumo Consolidado'[Serie]),
    TREATAS(
        VALUES('Fact_Metraje'[Nº_BROCA]), 
        'Consumo Consolidado'[Serie]
    )
)
```

### 🔹 `[Medidas].[Cantidad Brocas CONSUMO]`
```dax
CALCULATE(
    DISTINCTCOUNT('Consumo Consolidado'[Serie]),
    'Consumo Consolidado'[Serie] <> "0",
    'Consumo Consolidado'[Serie] <> "ND",
    'Consumo Consolidado'[Serie] <> ""
)
```

### 🔹 `[Medidas].[Cantidad Brocas (Con Metraje)]`
```dax
CALCULATE(
    DISTINCTCOUNT('Consumo Consolidado'[Serie]),
    'Consumo Consolidado'[Serie] <> "0",
    'Consumo Consolidado'[Serie] <> "ND",
    'Consumo Consolidado'[Serie] <> "",
    // Esto asegura que la serie exista también en Fact_Metraje
    TREATAS(
        VALUES('Fact_Metraje'[Nº_BROCA]), 
        'Consumo Consolidado'[Serie]
    )
)
```

