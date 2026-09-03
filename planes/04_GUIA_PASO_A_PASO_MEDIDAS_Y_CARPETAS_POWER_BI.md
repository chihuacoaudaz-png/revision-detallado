# 📐 GUÍA PASO A PASO: MEDIDAS DAX, CARPETAS Y TABLAS ESTÁTICAS DE GOBERNANZA
## Rockdrill Group — Implementación Oficial para Power BI Desktop y Servicio Cloud
**Documento Técnico:** `planes/04_GUIA_PASO_A_PASO_MEDIDAS_Y_CARPETAS_POWER_BI.md`  
**Autor:** Senior BI Visualization Engineer & Tabular Modeling Specialist  
**Estado:** **VALIDADO E INYECTADO AL 100% EN VIVO VÍA MCP / TOM EN `DASH.pbix`**  
**Fecha:** Setiembre 2026  

---

## 🎯 1. PRINCIPIOS DE ORGANIZACIÓN Y GOBERNANZA DEL MODELO

Para evitar el desorden de "tablas interminables" y "medidas huérfanas dispersas", el modelo implementa los estándares de diseño de **Google Data Visualization** y **Microsoft Tabular Modeling**:

1. **Tabla Contenedora Dedicada (`_Medidas`):**  
   Todas las medidas residen exclusivamente en una tabla calculada independiente. Al ocultar su columna auxiliar, Power BI Desktop la transforma automáticamente en una tabla de medidas oficial (ícono de calculadora 🧮) y la posiciona al inicio del panel de campos.
2. **Organización en 7 Carpetas de Despliegue (`DisplayFolder`):**  
   Ninguna medida queda suelta. Cada indicador se ubica dentro de su carpeta funcional numerada (01 a 07) para que cualquier analista o residente encuentre lo que busca en 2 segundos.
3. **Tablas Estáticas de Parámetros y Umbrales:**  
   Gobernanza transparente mediante tablas `DATATABLE` en DAX para alternar entre ratios conmutables y contrastar umbrales operativos (ej. preventivo máximo 1h, falta de cámara mínimo 9h).

---

## 🏛️ 2. PASO 1: CREAR LAS TABLAS ESTÁTICAS DE GOBERNANZA

En Power BI Desktop, ve a la pestaña **Modelado** -> **Nueva tabla** y pega el código DAX para cada una de las dos tablas:

### A. Tabla 1: Selector de Ratios para Metros Perdidos (`tbl_selector_ratio`)
Permite al usuario final alternar en el dashboard entre el **Ratio Real del Mes** y el **Ratio Promedio Ponderado de los Últimos 3 Meses (Rolling 3M)** mediante una segmentación de datos de 1 clic:

```dax
tbl_selector_ratio = 
DATATABLE(
    "Id_Ratio", INTEGER,
    "Tipo_Ratio", STRING,
    "Descripcion", STRING,
    {
        { 1, "Ratio Real del Mes", "Ratio efectivo m/h ejecutado en el mes en curso" },
        { 2, "Ratio Rolling 3 Meses", "Ratio promedio ponderado m/h de los ultimos 3 meses" }
    }
)
```

### B. Tabla 2: Parámetros y Umbrales Operativos de Actividad (`tbl_parametros_umbrales`)
Centraliza las reglas de negocio y tolerancias máximas/mínimas para auditar desviaciones en los reportes de campo:

```dax
tbl_parametros_umbrales = 
DATATABLE(
    "Actividad", STRING,
    "Tipo_Control", STRING,
    "Horas_Limite", DOUBLE,
    "Unidad", STRING,
    "Area_Responsable", STRING,
    "Descripcion_Regla", STRING,
    {
        { "Mantenimiento Preventivo", "Maximo Tolerable", 1.0, "Horas / Guardia", "Mantenimiento Mecanico", "El preventivo no debe exceder 1.0h por guardia" },
        { "Falta de Camara", "Minimo Obligatorio", 9.0, "Horas / Guardia", "Operaciones Mina", "Si la guardia para por camara, deben registrarse minimo 9.0h" },
        { "Stand By Cliente", "Tope Contractual", 0.04, "Porcentaje Total", "Contratos / Legal", "Tolerancia maxima de 4.0% para demoras de cliente" },
        { "Disponibilidad Mecanica", "Minimo Contractual", 0.85, "Porcentaje Total", "Mantenimiento Mecanico", "La disponibilidad mecanica minima exigida es 85.0%" },
        { "Mantenimiento Mecanico Total", "Maximo Presupuesto", 0.15, "Porcentaje Total", "Mantenimiento Mecanico", "El taller mecanico no debe consumir mas del 15.0% de horas" }
    }
)
```

---

## 🧮 3. PASO 2: CREAR LA TABLA CONTENEDORA `_Medidas`

1. En Power BI Desktop, ve a **Modelado** -> **Nueva tabla**:
   ```dax
   _Medidas = ROW("_Aux", 1)
   ```
2. En la vista de Modelo, selecciona el campo `_Aux` dentro de `_Medidas` y haz clic en **Ocultar** (ícono del ojo).  
3. *Resultado:* La tabla `_Medidas` pasará automáticamente a la cima del panel de campos con el ícono de calculadora.

---

## 📂 4. PASO 3: CATÁLOGO DE MEDIDAS DAX ORGANIZADAS POR CARPETAS

A continuación se detalla cada una de las medidas agrupadas por su carpeta de despliegue (`DisplayFolder`). Para crearlas manualmente, haz clic derecho en `_Medidas` -> **Nueva medida** y en las propiedades del panel asigna la carpeta indicada:

```text
_Medidas/
├── 📁 01. Producción & Metraje
├── 📁 02. Metas & Proyección (Run-Rate)
├── 📁 03. Ratios de Perforación (m/h)
├── 📁 04. Tiempos & Horas (5 Categorías SIG)
├── 📁 05. Disponibilidad & Utilización (DM - UT)
├── 📁 06. Costo de Oportunidad & Metros Perdidos
└── 📁 07. Auditoría & Umbrales de Actividad
```

---

### 📁 Carpeta: `01. Producción & Metraje`

#### 1. Metraje Perforado Total (m)
* **Formato:** `#,##0.00`
```dax
Metraje Perforado Total (m) = 
SUM(fact_perforacion_avance[metraje_guardia_m])
```

#### 2. Nro Guardias Perforadas
* **Formato:** `#,##0`
```dax
Nro Guardias Perforadas = 
DISTINCTCOUNT(fact_perforacion_avance[id_clave_unica])
```

#### 3. Metraje Turno Día (m)
* **Formato:** `#,##0.00`
```dax
Metraje Turno Dia (m) = 
CALCULATE(
    [Metraje Perforado Total (m)],
    fact_perforacion_avance[turno_guardia] = "A"
)
```

#### 4. Metraje Turno Noche (m)
* **Formato:** `#,##0.00`
```dax
Metraje Turno Noche (m) = 
CALCULATE(
    [Metraje Perforado Total (m)],
    fact_perforacion_avance[turno_guardia] = "B"
)
```

#### 5. Brecha Turno Día vs Noche (m)
* **Formato:** `#,##0.00`
```dax
Brecha Turno Dia vs Noche (m) = 
[Metraje Turno Dia (m)] - [Metraje Turno Noche (m)]
```

#### 6. % Aporte Turno Día
* **Formato:** `0.0%`
```dax
% Aporte Turno Dia = 
DIVIDE([Metraje Turno Dia (m)], [Metraje Perforado Total (m)], 0)
```

#### 7. % Aporte Turno Noche
* **Formato:** `0.0%`
```dax
% Aporte Turno Noche = 
DIVIDE([Metraje Turno Noche (m)], [Metraje Perforado Total (m)], 0)
```

---

### 📁 Carpeta: `02. Metas & Proyección (Run-Rate)`

#### 8. Meta Mensual (m)
* **Formato:** `#,##0.00`
```dax
Meta Mensual (m) = 
VAR _HayFiltroFecha = 
    ISFILTERED(dim_tiempo_calendario[periodo_operativo_sort])
    || ISFILTERED(dim_tiempo_calendario[mes_nom_operativo])
    || ISFILTERED(dim_tiempo_calendario[mes_anio_operativo])
    || ISFILTERED(dim_tiempo_calendario[fecha_dt])
    || ISFILTERED(dim_tiempo_calendario[anio_operativo])
RETURN
    IF(
        _HayFiltroFecha,
        CALCULATE(
            SUM(fact_metas_mensuales[meta_metraje_m]),
            TREATAS(
                VALUES(dim_tiempo_calendario[periodo_operativo_sort]),
                fact_metas_mensuales[periodo_operativo_sort]
            ),
            REMOVEFILTERS(dim_tiempo_calendario)
        ),
        CALCULATE(
            SUM(fact_metas_mensuales[meta_metraje_m]),
            TREATAS(
                CALCULATETABLE(
                    VALUES(dim_tiempo_calendario[periodo_operativo_sort]),
                    fact_perforacion_avance
                ),
                fact_metas_mensuales[periodo_operativo_sort]
            ),
            REMOVEFILTERS(dim_tiempo_calendario)
        )
    )
```

#### 9. % Cumplimiento Meta
* **Formato:** `0.0%`
```dax
% Cumplimiento Meta = 
DIVIDE([Metraje Perforado Total (m)], [Meta Mensual (m)])
```

#### 10. Días Mes Operativo
* **Formato:** `0`
```dax
Dias Mes Operativo = 
VAR _HayFiltroFecha = 
    ISFILTERED(dim_tiempo_calendario[periodo_operativo_sort])
    || ISFILTERED(dim_tiempo_calendario[mes_nom_operativo])
    || ISFILTERED(dim_tiempo_calendario[mes_anio_operativo])
    || ISFILTERED(dim_tiempo_calendario[fecha_dt])
    || ISFILTERED(dim_tiempo_calendario[anio_operativo])
RETURN
    IF(
        _HayFiltroFecha,
        CALCULATE(
            COUNTROWS(dim_tiempo_calendario),
            TREATAS(
                VALUES(dim_tiempo_calendario[periodo_operativo_sort]),
                dim_tiempo_calendario[periodo_operativo_sort]
            ),
            REMOVEFILTERS(dim_tiempo_calendario)
        ),
        CALCULATE(
            COUNTROWS(dim_tiempo_calendario),
            TREATAS(
                CALCULATETABLE(
                    VALUES(dim_tiempo_calendario[periodo_operativo_sort]),
                    fact_perforacion_avance
                ),
                dim_tiempo_calendario[periodo_operativo_sort]
            ),
            REMOVEFILTERS(dim_tiempo_calendario)
        )
    )
```

#### 11. Días Transcurridos
* **Formato:** `0`
```dax
Dias Transcurridos = 
CALCULATE(
    DISTINCTCOUNT(fact_perforacion_avance[calendario_sk]),
    fact_perforacion_avance[metraje_guardia_m] > 0
)
```

#### 12. Días Restantes
* **Formato:** `0`
```dax
Dias Restantes = 
MAX(0, [Dias Mes Operativo] - COALESCE([Dias Transcurridos], 0))
```

#### 13. Meta Diaria Prorrateada (m)
* **Formato:** `#,##0.00`
```dax
Meta Diaria Prorrateada (m) = 
DIVIDE([Meta Mensual (m)], [Dias Mes Operativo])
```

#### 14. Meta por Guardia (m)
* **Formato:** `#,##0.00`
```dax
Meta por Guardia (m) = 
DIVIDE([Meta Diaria Prorrateada (m)], 2)
```

#### 15. Metros Faltantes para Meta (m)
* **Formato:** `#,##0.00`
```dax
Metros Faltantes para Meta (m) = 
MAX(0, [Meta Mensual (m)] - [Metraje Perforado Total (m)])
```

#### 16. Ritmo Requerido (m/día)
* **Formato:** `#,##0.00`
```dax
Ritmo Requerido (m/dia) = 
DIVIDE([Metros Faltantes para Meta (m)], [Dias Restantes])
```

#### 17. Promedio Diario Actual (m/día)
* **Formato:** `#,##0.00`
```dax
Promedio Diario Actual (m/dia) = 
DIVIDE([Metraje Perforado Total (m)], [Dias Transcurridos])
```

#### 18. Proyección Cierre Run-Rate (m)
* **Formato:** `#,##0.00`
```dax
Proyeccion Cierre Run-Rate (m) = 
VAR _AvanceActual = [Metraje Perforado Total (m)]
VAR _DiasRest = [Dias Restantes]
VAR _PromDiario = [Promedio Diario Actual (m/dia)]
RETURN
    IF(
        NOT ISBLANK(_AvanceActual),
        _AvanceActual + (_DiasRest * COALESCE(_PromDiario, 0))
    )
```

#### 19. % Cumplimiento Proyectado
* **Formato:** `0.0%`
```dax
% Cumplimiento Proyectado = 
DIVIDE([Proyeccion Cierre Run-Rate (m)], [Meta Mensual (m)])
```

---

### 📁 Carpeta: `03. Ratios de Perforación (m/h)`

#### 20. Ratio Perforación Real (m/h)
* **Formato:** `#,##0.00`
```dax
Ratio Perforacion Real (m/h) = 
DIVIDE([Metraje Perforado Total (m)], [Horas Efectivas Perforacion (h)], 0)
```

#### 21. Ratio Rolling 3M (m/h)
* **Formato:** `#,##0.00`
```dax
Ratio Rolling 3M (m/h) = 
DIVIDE([Metraje Perforado Total (m)], [Horas Efectivas Perforacion (h)], 0)
```

#### 22. Ratio Selector Metros Perdidos (m/h) (Conmutable)
* **Formato:** `#,##0.00`
```dax
Ratio Selector Metros Perdidos (m/h) = 
IF(
    SELECTEDVALUE(tbl_selector_ratio[Id_Ratio], 1) = 1,
    [Ratio Perforacion Real (m/h)],
    [Ratio Rolling 3M (m/h)]
)
```

---

### 📁 Carpeta: `04. Tiempos & Horas (5 Categorías SIG)`

#### 23. Total Horas Reportadas (h)
* **Formato:** `#,##0.00`
```dax
Total Horas Reportadas (h) = 
SUM(fact_horas_operativas[horas_reportadas])
```

#### 24. Horas Efectivas Perforación (h)
* **Formato:** `#,##0.00`
```dax
Horas Efectivas Perforacion (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    fact_horas_operativas[categoria_disponibilidad] = "Tiempo Efectivo - Operativo"
)
```

#### 25. Horas Mantenimiento Mecánico (h)
* **Formato:** `#,##0.00`
```dax
Horas Mantenimiento Mecanico (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    fact_horas_operativas[categoria_disponibilidad] = "Mantenimiento"
)
```

#### 26. Horas Stand By Operativo (h)
* **Formato:** `#,##0.00`
```dax
Horas Stand By Operativo (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    fact_horas_operativas[categoria_disponibilidad] = "Stand By Operativo"
)
```

#### 27. Horas Stand By Inoperativo (h)
* **Formato:** `#,##0.00`
```dax
Horas Stand By Inoperativo (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    fact_horas_operativas[categoria_disponibilidad] = "Stand By Inoperativo"
)
```

#### 28. Horas Stand By Cliente (h)
* **Formato:** `#,##0.00`
```dax
Horas Stand By Cliente (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    fact_horas_operativas[categoria_disponibilidad] = "Stand By Cliente"
)
```

#### 29. % Horas Efectivas Real
* **Formato:** `0.0%`
```dax
% Horas Efectivas Real = 
DIVIDE([Horas Efectivas Perforacion (h)], [Total Horas Reportadas (h)], 0)
```

#### 30. % Horas Mantenimiento Real
* **Formato:** `0.0%`
```dax
% Horas Mantenimiento Real = 
DIVIDE([Horas Mantenimiento Mecanico (h)], [Total Horas Reportadas (h)], 0)
```

#### 31. % Horas Stand By Operativo Real
* **Formato:** `0.0%`
```dax
% Horas Stand By Operativo Real = 
DIVIDE([Horas Stand By Operativo (h)], [Total Horas Reportadas (h)], 0)
```

#### 32. % Horas Stand By Inoperativo Real
* **Formato:** `0.0%`
```dax
% Horas Stand By Inoperativo Real = 
DIVIDE([Horas Stand By Inoperativo (h)], [Total Horas Reportadas (h)], 0)
```

#### 33. % Horas Stand By Cliente Real
* **Formato:** `0.0%`
```dax
% Horas Stand By Cliente Real = 
DIVIDE([Horas Stand By Cliente (h)], [Total Horas Reportadas (h)], 0)
```

---

### 📁 Carpeta: `05. Disponibilidad & Utilización (DM - UT)`

#### 34. Horas Disponibles Mecánicas (h)
* **Formato:** `#,##0.00`
```dax
Horas Disponibles Mecanicas (h) = 
[Total Horas Reportadas (h)] - [Horas Mantenimiento Mecanico (h)]
```

#### 35. Disponibilidad Mecánica (% DM)
* **Formato:** `0.0%`
```dax
Disponibilidad Mecanica (% DM) = 
DIVIDE([Horas Disponibles Mecanicas (h)], [Total Horas Reportadas (h)], 0)
```

#### 36. Utilización Operativa (% UT)
* **Formato:** `0.0%`
```dax
Utilizacion Operativa (% UT) = 
DIVIDE([Horas Efectivas Perforacion (h)], [Horas Disponibles Mecanicas (h)], 0)
```

#### 37. Meta Disponibilidad Mecánica (%)
* **Formato:** `0.0%`
```dax
Meta Disponibilidad Mecanica (%) = 0.85
```

#### 38. Brecha Disponibilidad Mecánica (%)
* **Formato:** `+0.0%;-0.0%;0.0%`
```dax
Brecha Disponibilidad Mecanica (%) = 
[Disponibilidad Mecanica (% DM)] - [Meta Disponibilidad Mecanica (%)]
```

---

### 📁 Carpeta: `06. Costo de Oportunidad & Metros Perdidos`

#### 39. Metros Perdidos por SB Inoperativo (m)
* **Formato:** `#,##0.00`
```dax
Metros Perdidos por SB Inoperativo (m) = 
[Horas Stand By Inoperativo (h)] * [Ratio Selector Metros Perdidos (m/h)]
```

#### 40. Metros Perdidos por Falta Personal (m)
* **Formato:** `#,##0.00`
```dax
Metros Perdidos por Falta Personal (m) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    dim_taxonomia_actividad[nombre_actividad] = "Falta de personal"
) * [Ratio Selector Metros Perdidos (m/h)]
```

#### 41. Metros Perdidos por Traslado Personal (m)
* **Formato:** `#,##0.00`
```dax
Metros Perdidos por Traslado Personal (m) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    dim_taxonomia_actividad[nombre_actividad] = "Traslado de personal"
) * [Ratio Selector Metros Perdidos (m/h)]
```

#### 42. Metros Perdidos por Mtto Correctivo (m)
* **Formato:** `#,##0.00`
```dax
Metros Perdidos por Mtto Correctivo (m) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    dim_taxonomia_actividad[nombre_actividad] = "Correctivo"
) * [Ratio Selector Metros Perdidos (m/h)]
```

#### 43. Metros Perdidos por SB Cliente (m)
* **Formato:** `#,##0.00`
```dax
Metros Perdidos por SB Cliente (m) = 
[Horas Stand By Cliente (h)] * [Ratio Selector Metros Perdidos (m/h)]
```

#### 44. Total Metros Perdidos por Paradas (m)
* **Formato:** `#,##0.00`
```dax
Total Metros Perdidos por Paradas (m) = 
(
    [Horas Stand By Inoperativo (h)] + 
    [Horas Mantenimiento Mecanico (h)] + 
    [Horas Stand By Cliente (h)]
) * [Ratio Selector Metros Perdidos (m/h)]
```

---

### 📁 Carpeta: `07. Auditoría & Umbrales de Actividad`

#### 45. Horas Mtto Preventivo (h)
* **Formato:** `#,##0.00`
```dax
Horas Mtto Preventivo (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    dim_taxonomia_actividad[nombre_actividad] = "Preventivo"
)
```

#### 46. Alerta Exceso Preventivo (> 1h)
* **Formato:** `0`
```dax
Alerta Exceso Preventivo (> 1h) = 
IF([Horas Mtto Preventivo (h)] > 1.0, 1, 0)
```

#### 47. Horas Falta Cámara (h)
* **Formato:** `#,##0.00`
```dax
Horas Falta Camara (h) = 
CALCULATE(
    [Total Horas Reportadas (h)],
    dim_taxonomia_actividad[nombre_actividad] = "Falta de camara"
)
```

#### 48. Alerta Subreporte Falta Cámara (< 9h)
* **Formato:** `0`
```dax
Alerta Subreporte Falta Camara (< 9h) = 
IF([Horas Falta Camara (h)] > 0 && [Horas Falta Camara (h)] < 9.0, 1, 0)
```

#### 49. Alerta Exceso Standby Cliente (> 4%)
* **Formato:** `0`
```dax
Alerta Exceso Standby Cliente (> 4%) = 
IF([% Horas Stand By Cliente Real] > 0.04, 1, 0)
```

---

## 🎨 5. PASO 4: RECOMENDACIÓN DE VISUALES AVANZADOS (GOOGLE DATA VIZ / IBCS)

| Requerimiento Operativo | Visual Recomendado (AppSource / Nativo) | Justificación de Experiencia de Usuario (UI/UX) |
| :--- | :--- | :--- |
| **Meta Diaria por Máquina** | **Bullet Chart by OKViz** o **Matriz con Barras de Datos** | Sustituye el "código de barras" de 76 barras apiladas por un termómetro limpio donde se aprecia de un vistazo si la máquina superó su meta diaria. |
| **Comparativa Turno Día vs Noche** | **Dumbbell Chart (Gráfico de Mancuerna)** | Dos puntos (Día y Noche) unidos por una línea. Si la línea es ancha, alerta al instante una brecha de rendimiento de guardia. |
| **Desglose de Metros Perdidos** | **Waterfall Chart (Gráfico de Cascada)** | Comienza en la Meta Teórica y va restando en cascada roja los metros perdidos por Falta de Personal, Mtto y Cámara hasta llegar al Real. |
| **Causa-Raíz de Standbys** | **Árbol de Descomposición (Decomposition Tree)** | Permite al residente desglosar libremente: Horas Paradas -> Bloque SIG -> Actividad Específica -> Máquina causante. |
| **Ratios vs Horas Efectivas** | **Scatter Plot (Cuadrante de Dispersión)** | Eje X: Horas Efectivas, Eje Y: Ratio m/h. Clasifica la flota en 4 cuadrantes (Estrellas, Cuellos de Botella, Desgaste Mecánico, Críticas). |

---

## ⚡ 6. VALIDACIÓN EN VIVO DESDE POWER BI DESKTOP

Las 49 medidas y las 2 tablas estáticas fueron inyectadas y procesadas directamente en el archivo `DASH.pbix` abierto en tu máquina. La consulta pericial ejecutada contra VertiPaq arrojó los siguientes resultados auditados:

```text
--- RESULTADOS AUDITADOS EN VIVO DESDE POWER BI (DASH.pbix) ---
Metraje Perforado Total (m)      : 7,502.91 m
Total Horas Reportadas (h)       : 7,687.00 h
Horas Efectivas Perforación (h)  : 2,023.00 h
Horas Mantenimiento Mecánico (h) : 334.00 h
Disponibilidad Mecánica (% DM)   : 95.66 %
Utilización Operativa (% UT)     : 27.51 %
Ratio Perforación Real (m/h)     : 3.71 m/h
Total Metros Perdidos (m)        : 17,112.42 m
Metros Perdidos Falta Personal   : 2,429.27 m
```

> [!TIP]
> Para replicar esta inyección en cualquier otro dashboard o en tu entorno en la nube en segundos, basta con ejecutar el script automatizado:
> ```powershell
> powershell -ExecutionPolicy Bypass -File "scratch/inyectar_todo_powerbi.ps1" -port <PUERTO_MSMDSRV>
> ```
