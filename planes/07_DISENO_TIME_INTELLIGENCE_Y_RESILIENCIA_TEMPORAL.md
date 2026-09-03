# ⏱️ GUÍA TÉCNICA DE TIME INTELLIGENCE & RESILIENCIA TEMPORAL (CICLO OPERATIVO 26 AL 25)
## Rockdrill Group — Tabular Modeling & Visual Engineering Specialist
**Documento Oficial:** `planes/07_DISENO_TIME_INTELLIGENCE_Y_RESILIENCIA_TEMPORAL.md`  
**Modelo Relacional:** Esquema Estrella Kimball (`DASH.pbix`, VertiPaq Activo)  
**Versión:** 1.0.0 — Enterprise Grade  
**Fecha:** Setiembre 2026  

---

### 📋 RESUMEN EJECUTIVO & DIRECTIVA ESTRATÉGICA

El usuario ha formalizado una directiva clave de analítica temporal:
> *"también tomar en cuenta que es necesario realizar un monitoreo no solo puntual sino también basado en el tiempo, por eso en la slide 2 se incorpora el año op y el mes op pero ante la construcción del gráfico el día mes no está ordenado y tampoco se muestra la fecha como tal; en general revisa si los gráficos sobre todo de magnitudes que son comparables históricamente están diseñados para aguantar la comparación con el tiempo como dentro de un mes todos los días o la comparación del ciclo operativo anterior o mes operativo anterior etc. también adoptemos ese enfoque."*

En la industria minera subterránea y de diamantina (DDH), **el mes civil (1 al 31) no coincide con el mes operativo contable (día 26 del mes $M-1$ al día 25 del mes $M$)**.  
Por tanto:
1. **Las funciones DAX estándar de Time Intelligence** (`SAMEPERIODLASTYEAR`, `PREVIOUSMONTH`, `DATEADD(..., -1, MONTH)`) **fracasan** o generan desfases de corte que mezclan días de ciclos distintos.
2. **El eje X diario** no puede ser simplemente `dia_mes` (números del 1 al 31), pues colocaría los días 1 al 25 al inicio y los días 26 al 31 al final, desarticulando la secuencia cronológica del ciclo.
3. Se requiere una arquitectura tabular con **ejes cronológicos estrictos**, **medidas MoM (Month-over-Month) basadas en llaves operativas enteras**, **sincronización de segmentadores entre slides** y **resiliencia multimensual/multianual**.

---

## 1. 📅 EJE TEMPORAL DIARIO: CRONOLOGÍA ESTRICTA Y CONFIGURACIÓN DEL EJE X

### 1.1 Diagnóstico de la Desincronización del Eje Diario
* **Causa Raíz:** Al utilizar `dim_tiempo_calendario[dia_mes]` como Eje X, Power BI ordena numéricamente:  
  `1, 2, 3, ..., 25, 26, 27, 28, 29, 30, 31`.
  En el ciclo minero de Setiembre (26 de Agosto al 25 de Setiembre), esto produce que el 1 de Setiembre aparezca al principio y el 26 de Agosto aparezca al final de la gráfica, rompiendo la curva de evolución.
* Además, el usuario no sabe a qué mes pertenece el "1" o el "26" porque solo ve dígitos aislados.
* Si se usa un texto simple sin ordenar, Power BI aplica orden alfabético (`"01-Set"`, `"02-Set"`, `"10-Set"`, ..., `"26-Ago"`).

### 1.2 Nuevas Columnas Cronológicas en `dim_tiempo_calendario`

#### Columna A: `fecha_corta_label` (Para Monitoreo Intra-Mes con Fechas Reales)
* **Objetivo:** Mostrar la fecha con formato legible (ej. `"26-Ago"`, `"27-Ago"`, ..., `"01-Set"`, ..., `"25-Set"`).
* **Fórmula DAX (Columna Calculada):**
```dax
fecha_corta_label = 
IF(
    dim_tiempo_calendario[calendario_sk] = -1,
    "N/D",
    FORMAT(dim_tiempo_calendario[fecha_dt], "dd-mmm", "es-ES")
)
```
*(En Power Query M: `Date.ToText([fecha_dt], "dd-MMM", "es-ES")`)*
* **Configuración Crítica en Power BI:**
  1. Seleccionar la columna `fecha_corta_label`.
  2. Pestaña superior **Herramientas de columnas (*Column Tools*)** ➔ **Ordenar por columna (*Sort by Column*)**.
  3. Seleccionar: **`calendario_sk`** (o `fecha_dt`).  
  *Garantía Matemática:* Al estar ordenada por `calendario_sk` (`20260826 < 20260827 < ... < 20260901 < ... < 20260925`), el Eje X seguirá de forma inquebrantable el curso del tiempo.

#### Columna B: `dia_ciclo_label` (Para Superposición y Comparación Normalizada entre Ciclos)
* **Objetivo:** Alinear el Día 1 de cualquier mes con el Día 1 de otro mes (ej. `"Día 01"`, `"Día 02"`, ..., `"Día 31"`).
* **Fórmula DAX (Columna Calculada):**
```dax
dia_ciclo_label = 
IF(
    dim_tiempo_calendario[calendario_sk] = -1,
    "N/D",
    "Día " & FORMAT(dim_tiempo_calendario[dia_ciclo_operativo], "00")
)
```
* **Configuración Crítica en Power BI:**
  1. Seleccionar la columna `dia_ciclo_label`.
  2. Pestaña superior **Herramientas de columnas (*Column Tools*)** ➔ **Ordenar por columna (*Sort by Column*)**.
  3. Seleccionar: **`dia_ciclo_operativo`** (entero del 1 al 31).

---

### 1.3 Paso a Paso para Configurar el Eje X en el Visual (Curva S / Producción Diaria)

Para asegurar que el gráfico **NUNCA** se desordene al interactuar con filtros:

1. **Campos del Visual:**
   * **Eje X (*X-Axis*):** Arrastrar `dim_tiempo_calendario[fecha_corta_label]` (o `dia_ciclo_label` si se desea comparar múltiples ciclos superpuestos).
   * **Eje Y (*Y-Axis*):** `_Medidas[Metraje Acumulado Real (m)]` y `_Medidas[Meta Acumulada (m)]`.
2. **Menú de Opciones del Visual (Los 3 Puntos `...` en la esquina superior del gráfico):**
   * Clic en **`...`** ➔ **Ordenar eje (*Sort axis*)** ➔ Seleccionar **`fecha_corta_label`** (o `dia_ciclo_label`).  
     *(⚠️ NUNCA dejar ordenado por la medida `Metraje Acumulado Real (m)`, pues colocaría los días de mayor producción primero).*
   * Clic en **`...`** ➔ Seleccionar **Orden ascendente (*Sort ascending*)**.
3. **Panel de Formato del Objeto Visual (*Format Visual*):**
   * Sección **Eje X (*X-Axis*)**:
     * **Tipo (*Type*):** Cambiar de *"Continuo"* a **"Categórico" (*Categorical*)**. Esto fuerza a Power BI a tratar cada fecha como un hito cronológico discreto, respetando el `Sort by Column` sin aplicar interpolaciones ni saltos de escala.
     * **Concatenar etiquetas (*Concatenate labels*):** Desactivado (*Off*).

---

## 2. 🧮 MEDIDAS DAX DE TIME INTELLIGENCE OPERATIVO (CICLO 26 AL 25)

Al utilizarse `periodo_operativo_sort` (formato entero $YYYYMM$, ej. `202609` para el ciclo del 26-Ago al 25-Set), el cálculo del período anterior debe gestionar con precisión la transición de fin de año ($202601 \rightarrow 202512$).

### 2.1 Medida 1: Metraje Mes Operativo Anterior (m)
Calcula el avance perforado total del ciclo operativo inmediatamente anterior ($M-1$), respetando los filtros de contrato, perforadora y cuadrilla.

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
Metraje Mes Operativo Anterior (m) = 
VAR _PeriodoActual = MAX(dim_tiempo_calendario[periodo_operativo_sort])
VAR _Anio = INT(_PeriodoActual / 100)
VAR _Mes = MOD(_PeriodoActual, 100)
VAR _PeriodoAnterior = 
    IF(
        _Mes = 1,
        (_Anio - 1) * 100 + 12,
        _PeriodoActual - 1
    )
RETURN
    IF(
        NOT ISBLANK(_PeriodoActual) && _PeriodoActual > 190001,
        CALCULATE(
            [Metraje Perforado Total (m)],
            REMOVEFILTERS(dim_tiempo_calendario),
            dim_tiempo_calendario[periodo_operativo_sort] = _PeriodoAnterior
        )
    )
```

### 2.2 Medida 2: Variación Absoluta vs Mes Anterior (m)
Diferencia en metros perforados respecto al ciclo previo.

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
Variacion vs Mes Anterior (m) = 
VAR _RealActual = [Metraje Perforado Total (m)]
VAR _RealAnterior = [Metraje Mes Operativo Anterior (m)]
RETURN
    IF(
        NOT ISBLANK(_RealActual) && NOT ISBLANK(_RealAnterior),
        _RealActual - _RealAnterior
    )
```

### 2.3 Medida 3: % Variación vs Mes Anterior (MoM)
Tasa porcentual de crecimiento o decrecimiento intermensual.

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
% Variacion vs Mes Anterior (MoM) = 
VAR _RealActual = [Metraje Perforado Total (m)]
VAR _RealAnterior = [Metraje Mes Operativo Anterior (m)]
RETURN
    DIVIDE(_RealActual - _RealAnterior, _RealAnterior)
```
*(Formato: `+0.0%;-0.0%;0.0%`)*

### 2.4 Medida 4: Meta Mes Operativo Anterior (m)
Presupuesto asignado al ciclo operativo previo.

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
Meta Mes Operativo Anterior (m) = 
VAR _PeriodoActual = MAX(dim_tiempo_calendario[periodo_operativo_sort])
VAR _Anio = INT(_PeriodoActual / 100)
VAR _Mes = MOD(_PeriodoActual, 100)
VAR _PeriodoAnterior = 
    IF(
        _Mes = 1,
        (_Anio - 1) * 100 + 12,
        _PeriodoActual - 1
    )
RETURN
    IF(
        NOT ISBLANK(_PeriodoActual) && _PeriodoActual > 190001,
        CALCULATE(
            SUM(fact_metas_mensuales[meta_metraje_m]),
            REMOVEFILTERS(dim_tiempo_calendario),
            fact_metas_mensuales[periodo_operativo_sort] = _PeriodoAnterior
        )
    )
```

### 2.5 Medida 5: % Cumplimiento Mes Operativo Anterior
Eficacia del cierre operacional del mes previo.

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
% Cumplimiento Mes Operativo Anterior = 
DIVIDE(
    [Metraje Mes Operativo Anterior (m)],
    [Meta Mes Operativo Anterior (m)]
)
```
*(Formato: `0.0%`)*

---

### 2.6 Medida Estratégica Adicional: Metraje Mes Anterior a la Fecha (MTD Like-for-Like)
> **💡 Insight de Ingeniería:** Si el mes en curso está en el **Día 6** (ej. 7,502 m), comparar contra el total de 31 días del mes previo (ej. 45,000 m) genera una caída aparente de -83% que distorsiona la toma de decisiones.  
> Esta medida calcula el metraje acumulado del mes anterior **exactamente hasta el mismo día del ciclo** ($\le \text{Día 6}$):

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
Metraje Mes Anterior a la Fecha (m) = 
VAR _PeriodoActual = MAX(dim_tiempo_calendario[periodo_operativo_sort])
VAR _DiaCicloActual = MAX(dim_tiempo_calendario[dia_ciclo_operativo])
VAR _Anio = INT(_PeriodoActual / 100)
VAR _Mes = MOD(_PeriodoActual, 100)
VAR _PeriodoAnterior = 
    IF(
        _Mes = 1,
        (_Anio - 1) * 100 + 12,
        _PeriodoActual - 1
    )
RETURN
    IF(
        NOT ISBLANK(_PeriodoActual) && _PeriodoActual > 190001,
        CALCULATE(
            [Metraje Perforado Total (m)],
            REMOVEFILTERS(dim_tiempo_calendario),
            dim_tiempo_calendario[periodo_operativo_sort] = _PeriodoAnterior,
            dim_tiempo_calendario[dia_ciclo_operativo] <= _DiaCicloActual
        )
    )
```

```dax
-- Carpeta: 08. Comparabilidad Histórica (Ciclo Minero)
% Variacion vs Mes Anterior MTD = 
DIVIDE(
    [Metraje Perforado Total (m)] - [Metraje Mes Anterior a la Fecha (m)],
    [Metraje Mes Anterior a la Fecha (m)]
)
```

---

## 3. 🔄 SINCRONIZACIÓN Y PRESENCIA DE SLICERS EN SLIDE 2

Para dar cumplimiento exacto al requerimiento:  
> *"por eso en la slide 2 se incorpora el ano top y el mes op..."*

Se adopta el patrón de **Sync Slicers Bidireccionales Visibles**, garantizando coherencia global sin duplicar esfuerzos del usuario.

### 3.1 Procedimiento en Power BI Desktop (Sync Slicers)

1. En la cinta superior de opciones, ir a la pestaña **Ver (*View*)**.
2. Marcar la casilla **Sincronizar segmentadores (*Sync Slicers*)**. Se abrirá el panel lateral correspondiente.
3. Configuración para **`anio_operativo`**:
   * Seleccionar el segmentador `anio_operativo` en **Slide 1**.
   * En el panel *Sincronizar segmentadores*, activar:
     * **Slide 1:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Activado`
     * **Slide 2:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Activado`
     * **Slide 3:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Opcional`
     * **Slide 4:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Opcional`
4. Configuración para **`mes_nom_operativo`**:
   * Seleccionar el segmentador `mes_nom_operativo` en **Slide 1**.
   * En el panel *Sincronizar segmentadores*, activar:
     * **Slide 1:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Activado`
     * **Slide 2:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Activado`
     * **Slide 3:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Opcional`
     * **Slide 4:** Sincronizar (🔄) = `Activado` | Visible (👁️) = `Opcional`
5. Configuración para **`nombre_contrato_limpio`**:
   * Activar Sincronizar (🔄) y Visible (👁️) en **Slide 1, Slide 2, Slide 3 y Slide 4**.

### 3.2 Maquetación del Header Superior en Slide 2
El encabezado superior de Slide 2 ($Y = 10 \text{px}$ a $75 \text{px}$, Altura $= 65 \text{px}$) se compone de 5 controles horizontales compactos:

| Posición | Campo | Objeto Visual | Formato / Estilo | Dimensiones |
| :---: | :--- | :--- | :--- | :---: |
| **Control 1** | `dim_tiempo_calendario[anio_operativo]` | Segmentador Nativo | Mosaico (*Tile*): `2025` \| `2026` | $140 \times 45 \text{ px}$ |
| **Control 2** | `dim_tiempo_calendario[mes_nom_operativo]` | Segmentador Nativo | Menú desplegable (*Dropdown*) | $160 \times 45 \text{ px}$ |
| **Control 3** | `dim_contrato_minero[nombre_contrato_limpio]` | Segmentador Nativo | Dropdown con barra de búsqueda | $200 \times 45 \text{ px}$ |
| **Control 4** | `fact_perforacion_avance[turno_guardia]` | Segmentador Nativo | Mosaico (*Tile*): `A Día` \| `B Noche` | $160 \times 45 \text{ px}$ |
| **Control 5** | `dim_equipo_perforadora[codigo_maquina_limpio]`| Segmentador Nativo | Dropdown con barra de búsqueda | $190 \times 45 \text{ px}$ |

*Resultado Operativo:* Si el Jefe de Operaciones selecciona *"Setiembre"* en Slide 1, al navegar a Slide 2 el reporte ya está filtrado en Setiembre. Si luego cambia a *"Agosto"* en Slide 2 para auditar una anomalía, Slide 1 se actualiza automáticamente a Agosto.

---

## 4. 🛡️ AUDITORÍA DE RESILIENCIA HISTÓRICA MULTIMENSUAL (2025 - 2026)

¿Qué ocurre si el Directorio o el usuario retira el filtro de mes para analizar la tendencia completa de los 21 períodos disponibles ($202501 \dots 202609$)?

### 4.1 Matriz de Comportamiento por Objeto Visual

| Objeto Visual | Campo en Eje / Contexto | Comportamiento sin Filtro de Mes | ¿Soporta Multimes? | Recomendación de Maquetación |
| :--- | :--- | :--- | :---: | :--- |
| **Tarjetas KPI (Slide 1)** | `Metraje`, `Meta`, `DM`, `UT` | Suma el metraje de todos los meses seleccionados; `Meta Mensual` utiliza `TREATAS` y totaliza las metas de los 21 meses con precisión | ✅ **100% Robusto** | La tarjeta muestra el acumulado del horizonte temporal filtrado |
| **Curva S (Slide 1)** | Eje X: `dia_ciclo_operativo` | Si no hay filtro de mes, sumaría el Día 1 de todos los meses en un solo punto, distorsionando la curva | ⚠️ **Requiere Guardián** | **Solución A:** Guardián DAX con `HASONEVALUE`.<br>**Solución B:** Colocar `mes_anio_operativo` en la **Leyenda** para superponer las curvas S de cada mes |
| **Evolución Diaria (Slide 2)** | Eje X: `fecha_corta_label` | Si se seleccionan 12 meses, renderizar 365 barras genera saturación visual ("efecto peine") | ⚠️ **Ajustar Jerarquía** | Implementar **Jerarquía de Tiempo** en el Eje X:<br>Nivel 1: `anio_operativo`<br>Nivel 2: `mes_anio_operativo`<br>Nivel 3: `fecha_corta_label` |
| **Matriz de Máquinas** | Filas: CTR ➔ Máquina | Agrupa los totales acumulados del período; calcula ratios ponderados reales | ✅ **100% Robusto** | Permite evaluar qué máquinas mantuvieron alto metraje en el año |
| **Scatter Plot (Slide 2)** | Burbujas: Máquinas | $X = \text{Horas Efectivas}$, $Y = \text{Ratio Real}$, $Tamaño = \text{Metros}$. Ratios matemáticamente ponderados | ✅ **100% Robusto** | Identifica cuadrillas y equipos con estabilidad operativa en el tiempo |
| **Top 10 Perforistas (Slide 2)**| Eje Y: Perforistas | Identifica el Top 10 histórico del año completo según los filtros de tiempo | ✅ **100% Robusto** | Ranking dinámico siempre ordenado de mayor a menor |
| **Cascada de Pérdidas (Slide 4)**| Categoría: Pasos | Suma las pérdidas acumuladas en horas/metros de todo el período | ✅ **100% Robusto** | Muestra el impacto consolidado anual de paradas mecánicas y operativas |

### 4.2 Blindaje DAX para la Curva S ante Selecciones Multimensuales

Para que la Curva S no colapse si el usuario selecciona múltiples meses sin leyenda:

```dax
-- Carpeta: 02. Metas & Proyección (Run-Rate)
Metraje Acumulado Real (m) = 
VAR _PeriodoUnico = HASONEVALUE(dim_tiempo_calendario[periodo_operativo_sort])
VAR _DiaActual = MAX(dim_tiempo_calendario[dia_ciclo_operativo])
VAR _MaxDiaConAvance = 
    MAXX(
        FILTER(
            ALLSELECTED(dim_tiempo_calendario[dia_ciclo_operativo]),
            CALCULATE([Metraje Perforado Total (m)]) > 0
        ),
        dim_tiempo_calendario[dia_ciclo_operativo]
    )
RETURN
    IF(
        _PeriodoUnico,
        -- Modo Mes Individual: Curva S estricta sin caídas
        IF(
            _DiaActual > 0 && _DiaActual <= _MaxDiaConAvance,
            CALCULATE(
                [Metraje Perforado Total (m)],
                FILTER(
                    ALLSELECTED(dim_tiempo_calendario[dia_ciclo_operativo]),
                    dim_tiempo_calendario[dia_ciclo_operativo] <= _DiaActual && dim_tiempo_calendario[dia_ciclo_operativo] > 0
                )
            ),
            BLANK()
        ),
        -- Modo Multimes: Si mes_anio_operativo está en la leyenda, evalúa cada línea independientemente
        CALCULATE(
            [Metraje Perforado Total (m)],
            FILTER(
                ALLSELECTED(dim_tiempo_calendario[dia_ciclo_operativo]),
                dim_tiempo_calendario[dia_ciclo_operativo] <= _DiaActual && dim_tiempo_calendario[dia_ciclo_operativo] > 0
            )
        )
    )
```

---

## 5. 🎯 BENEFICIOS ESTRATÉGICOS PARA EL USUARIO & DIRECTORIO

1. **Eje Cronológico Inalterable:** Elimina la confusión del orden de fechas; el ciclo siempre fluye del 26 al 25 con etiquetas reconocibles (`26-Ago`, `01-Set`).
2. **Time Intelligence Preciso para Minería:** Comparación real mes a mes (MoM) sin depender de calendarios civiles que distorsionan los cierres contables.
3. **Navegación Unificada:** El filtrado sincronizado en Slide 2 erradica la duplicidad de clics y preserva la coherencia del análisis.
4. **Resiliencia Operativa:** El modelo responde impecablemente tanto al monitoreo diario táctico como al análisis estratégico plurianual (2025 - 2026).
