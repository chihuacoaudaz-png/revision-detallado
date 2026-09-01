# 🎯 Sistema de Metraje Perdido Ajustado (Ingeniería de ROP)

> [!IMPORTANT]
> **Objetivo del Modelo de Pérdida de Metros:**
> Cuantificar con exactitud cuántos metros de perforación diamantina se dejaron de ejecutar debido a eventos de **Stand By Cliente**, **Stand By Inoperativo (Falta de Personal)** y **Mantenimiento**, utilizando el rendimiento real en roca ($ROP_{\text{Efectivo}}$) ponderado por el factor de eficiencia operativa histórica de cada contrato ($f_{\text{efectivo}}$).

---

## 1. Fundamento Matemático

$$\text{Metros Perdidos} = \text{Horas de StandBy} \times \text{Ratio Ajustado}$$

Donde:

$$\text{Ratio Ajustado} = \text{ROP}_{\text{Efectivo}} \times f_{\text{efectivo}}$$

### A. $\text{ROP}_{\text{Efectivo}}$ (Velocidad Neta de Penetración en Roca)
$$\text{ROP}_{\text{Efectivo}} = \frac{\sum \text{Metros Perforados en el Periodo}}{\sum \text{Horas Efectivas de PERFORACION en el Periodo}}$$

### B. $f_{\text{efectivo}}$ (Factor de Corrección por Eficiencia de Guardia)
Refleja la proporción real de horas que la máquina logra perforar dentro de un turno nominal según las condiciones históricas del CTR en los **últimos 3 meses cerrados**:

$$f_{\text{efectivo}} = \frac{\text{Promedio de Horas Efectivas de Perforación por Turno (Últimos 3 Meses)}}{\text{Horas Nominales del Turno del CTR}}$$

#### 🕒 Tabla de Horas Nominales de Turno por Proyecto:
| CTR / Proyecto | Horas Nominales del Turno | Justificación Operativa |
| :--- | :---: | :--- |
| **YAULIYACU** | **11.00 hrs** | Jornada operativa reducida por traslados internos mina. |
| **CATALINA HUANCA** | **10.15 hrs** | Horario especial de guardia y refrigerio pactado. |
| **Todos los demás CTRs** | **12.00 hrs** | Turno estándar de guardia minera (12x12). |

---

## 2. Implementación de Fórmulas DAX

### 1️⃣ `[Medidas].[ROP_Efectivo]`
```dax
ROP_Efectivo = 
VAR _CurrentCTR = 
    COALESCE(
        SELECTEDVALUE('Fact_Tiempos'[CTR]), 
        SELECTEDVALUE('Dim_CTR'[CTR])
    )

VAR _Metros = 
    IF(
        ISBLANK(_CurrentCTR),
        CALCULATE(
            SUM('Fact_Metraje'[METRAJE_X_GUARDIA]),
            REMOVEFILTERS('Fact_Tiempos'[Actividad]),
            REMOVEFILTERS('Fact_Tiempos'[Categoria])
        ),
        CALCULATE(
            SUM('Fact_Metraje'[METRAJE_X_GUARDIA]),
            REMOVEFILTERS('Fact_Tiempos'[Actividad]),
            REMOVEFILTERS('Fact_Tiempos'[Categoria]),
            'Fact_Metraje'[CTR] = _CurrentCTR
        )
    )

VAR _HorasPerforacion = 
    CALCULATE(
        SUM('Fact_Tiempos'[Horas]),
        'Fact_Tiempos'[Actividad] = "PERFORACION",
        REMOVEFILTERS('Fact_Tiempos'[Actividad]),
        REMOVEFILTERS('Fact_Tiempos'[Categoria])
    )

RETURN
    DIVIDE(_Metros, _HorasPerforacion, 0)
```

---

### 2️⃣ `[Medidas].[f_efectivo]`
```dax
f_efectivo = 
VAR _CTR = 
    COALESCE(
        SELECTEDVALUE('Fact_Tiempos'[CTR]), 
        SELECTEDVALUE('Dim_CTR'[CTR])
    )

// 1. Horas nominales del turno según CTR
VAR _HorasTurno = 
    SWITCH(
        TRUE(),
        _CTR = "YAULIYACU", 11,
        _CTR = "CATALINA HUANCA" || _CTR = "CATALINA", 10.15,
        12
    )

// 2. Ventana de últimos 3 meses históricos
VAR _FechaMax = 
    CALCULATE(
        MAX('Fact_Tiempos'[FECHA]), 
        ALL('Fact_Tiempos'), 
        ALL('Dim_Calendario')
    )
VAR _FechaMin = EDATE(_FechaMax, -3)

// 3. Promedio de horas de perforación por turno para este CTR
VAR _HorasPerfPromedio = 
    CALCULATE(
        AVERAGEX(
            KEEPFILTERS(VALUES('Fact_Tiempos'[KEY_OPERACION])),
            CALCULATE(
                SUM('Fact_Tiempos'[Horas]),
                'Fact_Tiempos'[Actividad] = "PERFORACION"
            )
        ),
        ALL('Dim_Calendario'),
        'Fact_Tiempos'[FECHA] > _FechaMin,
        'Fact_Tiempos'[FECHA] <= _FechaMax,
        REMOVEFILTERS('Fact_Tiempos'[Actividad]),
        REMOVEFILTERS('Fact_Tiempos'[Categoria])
    )

RETURN
    DIVIDE(_HorasPerfPromedio, _HorasTurno, 0)
```

---

### 3️⃣ `[Medidas].[m_perdido_ajustado]` *(Con Corrección de Totales para Múltiples CTRs)*
```dax
m_perdido_ajustado = 
IF(
    HASONEVALUE('Fact_Tiempos'[CTR]) || HASONEVALUE('Dim_CTR'[CTR]),
    // 1. En cada fila individual (CTR, Categoría o Actividad)
    SUM('Fact_Tiempos'[Horas]) * ([ROP_Efectivo] * [f_efectivo]),
    
    // 2. En la fila de TOTAL GENERAL (Suma exacta de lo que da cada CTR)
    SUMX(
        VALUES('Fact_Tiempos'[CTR]),
        CALCULATE(
            SUM('Fact_Tiempos'[Horas]) * ([ROP_Efectivo] * [f_efectivo])
        )
    )
)
```

---

## 3. Matriz Visual en Power BI

### Configuración del Visual
* **Tipo:** Matriz (`Matrix`)
* **Filas:**
  1. `Fact_Tiempos[CTR]`
  2. `Fact_Tiempos[Categoria]`
  3. `Fact_Tiempos[Actividad]`
* **Valores:**
  * `Suma de Horas` (o `[Total Horas]`)
  * `[m_perdido_ajustado]`
* **Filtro de Segmentación (Slicers):**
  * `Dim_Calendario[Año Operativo]` (ej. 2026)
  * `Dim_Calendario[Mes Operativo]` (ej. AGOSTO)
  * `Dim_CTR[CTR]` (Selección múltiple admitida)
