# 📊 GUÍA MAESTRA SINCERADA: CONSTRUCCIÓN Y MAQUETACIÓN VISUAL DE SLIDES EN POWER BI
## Rockdrill Group — Control de Operaciones de Perforación Diamantina (DDH)
**Documento Técnico:** `planes/05_GUIA_PASO_A_PASO_CONSTRUCCION_SLIDES_Y_VISUALES_PBI.md`  
**Documento de Dictamen y Validación:** `planes/06_RESOLUCION_OBSERVACIONES_VISUALES_PBI.md`  
**Modelo Relacional:** `DASH.pbix` (Esquema Estrella Kimball, 11 Tablas, 52 Medidas DAX, Motor VertiPaq en Puerto 63554)  
**Estado:** **100% SINCERADO, PROBADO EN VIVO Y SIN ALUCINACIONES DE OBJETOS VISUALES**  
**Fecha de Emisión:** Setiembre 2026  

---

## 🎯 1. ARQUITECTURA DE LAS 4 SLIDES Y ESTRATEGIA DE SLICERS POR PÁGINA

El dashboard se compone de **4 Slides (Páginas)** con segmentadores sincronizados (*Sync Slicers*):

```text
SLIDE 1: TORRE DE CONTROL MACRO & CUMPLIMIENTO DE METAS CTR (Gerencia General)
├── Slicer 1: dim_tiempo_calendario[anio_operativo] (Estilo Mosaico / Tile: 2025, 2026)
├── Slicer 2: dim_tiempo_calendario[mes_nom_operativo] (Dropdown ordenado de 1 a 12)
├── Slicer 3: dim_contrato_minero[nombre_contrato_limpio] (Dropdown con búsqueda)
└── Badge de Cabecera: _Medidas[Badge Calendario Operativo] ("Día 6 de 31 | 25 días restantes")

SLIDE 2: DESEMPEÑO DE FLOTA, MÁQUINAS Y TURNOS DÍA VS NOCHE (Operaciones y Mina)
├── Slicer 1: dim_tiempo_calendario[anio_operativo] (Tile: 2025 | 2026 - Sincronizado con Slide 1)
├── Slicer 2: dim_tiempo_calendario[mes_nom_operativo] (Dropdown cronológico - Sincronizado con Slide 1)
├── Slicer 3: dim_contrato_minero[nombre_contrato_limpio] (Dropdown con búsqueda)
├── Slicer 4: fact_perforacion_avance[turno_guardia] (Tile: "A" Día | "B" Noche)
└── Slicer 5: dim_equipo_perforadora[codigo_maquina_limpio] (Dropdown con filtro de máquina activa)

SLIDE 3: TIEMPOS, DISPONIBILIDAD (% DM / % UT) Y TAXONOMÍA SIG (Mantenimiento Mecánico)
├── Slicer 1: dim_contrato_minero[nombre_contrato_limpio] (Dropdown con búsqueda)
├── Slicer 2: fact_horas_operativas[turno_guardia] (Estilo Tile: "A" Día | "B" Noche)
└── Slicer 3 (Solo para Pareto): dim_taxonomia_actividad[categoria_disponibilidad] (Vía Editar Interacciones)

SLIDE 4: COSTO DE OPORTUNIDAD Y METROS PERDIDOS POR PARADAS (Directorio y Contratos)
├── Slicer 1: dim_contrato_minero[nombre_contrato_limpio] (Dropdown con búsqueda)
└── Slicer 2: tbl_selector_ratio[Tipo_Ratio] (Estilo Tile: Ratio Real Mes | Ratio Rolling 3M)
```

---

## 🎨 2. CONFIGURACIÓN DEL LIENZO Y FORMATO SIN TRUNCAMIENTO DE DECIMALES

### A. Parámetros del Lienzo (Canvas Settings)
* **Tamaño del Lienzo:** 16:9 estándar (`1280 px` ancho × `720 px` alto).
* **Fondo del Lienzo:** Color blanco humo suave `#F8FAFC`, transparencia 0%.
* **Tipografía:** `Segoe UI` en todo el reporte (Títulos en 12-14 pt negrita, Tarjetas en 24-28 pt, Etiquetas en 9-10 pt).

### B. Regla de Oro para Tarjetas KPI (Evitar el "8 mil" o "7.5K")
En el objeto visual **Tarjeta Nueva (*New Card*)**:
1. Selecciona la tarjeta y ve al panel **Formato del objeto visual** (ícono de pincel).
2. Entra en **Valores de globo (*Callout values*)**.
3. **Mostrar unidades (*Display units*):** Cambia de *"Automático"* a **"Ninguno" (*None*)**.
4. **Posiciones decimales (*Value decimal places*):** Escribe **`2`**.
*Resultado:* Los números se muestran completos: `7,502.91` y `52,295.17`, sin abreviaciones que oculten metros.

---

## 🖥️ 3. SLIDE 1: TORRE DE CONTROL OPERATIVA & METAS CTR (MACRO)

### A. Fila de Tarjetas KPI Ejecutivas (Y: 65px, Alto: 100px)

1. **Tarjeta 1 — Metraje Total Perforado:**
   * **Campo:** `_Medidas[Metraje Perforado Total (m)]` (Valor: `7,502.91 m`)
   * **Subtítulo / Reference Label:** `_Medidas[Subtexto Meta Mes]` (Muestra: *"Meta Mes: 52,295.17 m"*)
   * **Etiqueta Secundaria:** `_Medidas[% Cumplimiento Meta]` (`14.3%`)

2. **Tarjeta 2 — Proyección Cierre Run-Rate:**
   * **Campo:** `_Medidas[Proyeccion Cierre Run-Rate (m)]` (Valor: `38,765.04 m`)
   * **Subtítulo / Reference Label:** `_Medidas[Subtexto Brecha Proyeccion]` (Muestra: *"Déficit proyectado: -13,530.13 m"*)
   * **Etiqueta Secundaria:** `_Medidas[% Cumplimiento Proyectado]` (`74.1%`)

3. **Tarjeta 3 — Ritmo Diario Requerido:**
   * **Campo:** `_Medidas[Ritmo Requerido (m/dia)]` (Valor: `1,791.69 m/dia`)
   * **Subtítulo / Reference Label:** `_Medidas[Subtexto Aceleracion Requerida]` (Muestra: *"Aceleración requerida: +541.21 m/día"*)
   * **Etiqueta Secundaria:** `_Medidas[Promedio Diario Actual (m/dia)]` (`1,250.49 m/dia`)

4. **Tarjeta 4 — Eficiencia Operativa (DM y UT en Primer Plano):**
   * **Visual:** Tarjeta Nueva configurada en **2 Columnas horizontales**.
   * **Campo 1:** `_Medidas[Disponibilidad Mecanica (% DM)]` (Valor grande: `95.7%`) | Subtexto: *"Meta DM: >= 85.0%"*
   * **Campo 2:** `_Medidas[Utilizacion Operativa (% UT)]` (Valor grande: `27.5%`) | Subtexto: *"Cuello botella en Mina"*

---

### B. Visual Principal Izquierdo: Cumplimiento de Metas por CTR (OKViz Bullet Chart)
* **Objeto Visual:** **Bullet Chart by OKViz** (AppSource).
* **Posición:** `X: 20px, Y: 180px, Ancho: 730px, Alto: 515px`.
* **Slots de Campos en OKViz:**
  * **Category:** `dim_contrato_minero[nombre_contrato_limpio]` (Muestra nombres limpios: "Catalina Huanca", "Cobriza", "Chungar")
  * **Value:** `_Medidas[Metraje Perforado Total (m)]`
  * **Target:** `_Medidas[Meta Mensual (m)]`
  * **Comparison Value:** `_Medidas[Proyeccion Cierre Run-Rate (m)]`
* **Formato Visual OKViz para Resaltar la Meta:**
  * En **Target**: Grosor de línea (*Stroke*) = **`4 px`**, Color = Rojo carmín `#D93025` o Negro `#1A202C`.
  * En **Qualitative Ranges**: Rango 1 (0-80% gris suave `#F1F5F9`), Rango 2 (80-100% gris medio `#E2E8F0`).
  * Ordenar por: `_Medidas[Meta Mensual (m)]` Descendente.

---

### C. Visual Principal Derecho: Curva S de Avance Acumulado (Line Chart)
* **Objeto Visual:** **Gráfico de líneas nativo**.
* **Posición:** `X: 770px, Y: 180px, Ancho: 490px, Alto: 515px`.
* **Slots de Campos:**
  * **Eje X (Opción 1 - Fecha Real):** `dim_tiempo_calendario[fecha_corta_label]` (Muestra: `"26-Ago"`, `"27-Ago"`... ordenado por `calendario_sk`).
  * **Eje X (Opción 2 - Día de Ciclo Normalizado):** `dim_tiempo_calendario[dia_ciclo_operativo]` (Días 1 al 31 del ciclo minero).
  * **Eje Y (Serie 1 - Real):** `_Medidas[Metraje Acumulado Real (m)]`  
    *(Fórmula probada en VertiPaq: avanza día 1 a 6 y en días 7 a 31 devuelve `BLANK()`, por lo que **la línea se detiene limpiamente en 7,502.91 m y NUNCA se cae a 0**).*
  * **Eje Y (Serie 2 - Meta Acumulada):** `_Medidas[Meta Acumulada (m)]`  
    *(Línea negra discontinua continua que progresa hasta los 52,295.17 m en el día 31).*
* **Regla de Oro para el Eje X (Evitar Desorden):**
  1. En los tres puntos del gráfico (`...`), clic en **Ordenar eje** -> Seleccionar **`fecha_corta_label`** (o `dia_ciclo_operativo`), **NUNCA ordenar por la medida de metraje**.
  2. Clic en **Orden ascendente**.
  3. En panel de Formato -> **Eje X** -> cambiar Tipo de *"Continuo"* a **"Categórico"**. ¡Esto garantiza que el ciclo 26 al 25 se dibuje en orden cronológico estricto sin partirse a la mitad!

---

## 🚜 4. SLIDE 2: FLOTA, MÁQUINAS Y TURNOS DÍA VS NOCHE (MICRO)

### A. Visual 1: Matriz de Control Operativo por Máquina con Drill-Down
* **Objeto Visual:** **Matriz nativa**.
* **Posición:** `X: 20px, Y: 70px, Ancho: 615px, Alto: 310px`.
* **Slots de Filas (Jerarquía Colapsable sin Scroll Infinito):**
  * **Nivel 1 de Filas:** `dim_contrato_minero[nombre_contrato_limpio]`
  * **Nivel 2 de Filas:** `dim_equipo_perforadora[codigo_maquina_limpio]` (Código limpio sin "SAP-": ej. `XRD80USS-010`)
* **Slots de Valores:**
  1. `_Medidas[Nro Guardias Operativas]` (Para cada máquina activa: Días transcurridos × 2 = 12 guardias al día 6).
  2. `_Medidas[Metraje Turno Dia (m)]`
  3. `_Medidas[Metraje Turno Noche (m)]`
  4. `_Medidas[Metraje Perforado Total (m)]`
  5. `_Medidas[Metros por Guardia (m/g)]` (Metraje Total / Guardias Operativas de la máquina).
  6. `_Medidas[Meta por Guardia (m)]`
  7. `_Medidas[% Cumplimiento Meta]` (Con Data Bars / Barras de datos verdes).

---

### B. Visual 2: Comparativa de Producción Turno Día vs Turno Noche (Gráfico de Barras Agrupadas Nativo)
* **Objeto Visual:** **Gráfico de barras agrupadas nativo** *(100% gratuito, sin marcas de agua ni licencias de AppSource)*.
* **Posición:** `X: 655px, Y: 70px, Ancho: 605px, Alto: 310px`.
* **Slots de Campos:**
  * **Eje Y:** `dim_contrato_minero[nombre_contrato_limpio]`
  * **Eje X:** `_Medidas[Metraje Perforado Total (m)]`
  * **Leyenda:** `fact_perforacion_avance[turno_guardia]` (Genera las 2 barras paralelas: 'A' Día y 'B' Noche).
  * **Información sobre herramientas (Tooltips):** `_Medidas[Brecha Turno Dia vs Noche (m)]`, `_Medidas[% Aporte Turno Dia]`
* **Formato Visual y Colores de Turno:**
  * En **Barras -> Colores**:
    * Serie "A" (Turno Día): Celeste cielo `#3B82F6`.
    * Serie "B" (Turno Noche): Azul marino nocturno `#1E1B4B`.
  * En **Etiquetas de datos (*Data labels*)**: Activar con posición *Extremo exterior* en 9 pt negrita.
* **Ventaja Operativa:** Permite al Jefe de Operaciones ver de un solo vistazo la longitud comparativa entre el turno diurno y nocturno en cada contrata, identificando caídas de producción en guardia noche.

---

### C. Visual 3: Top 10 Perforistas por Eficiencia Operativa (Ratio m/Guardia)
* **Objeto Visual:** **Gráfico de barras agrupadas nativo** (o Matriz con Data Bars).
* **Posición:** `X: 20px, Y: 395px, Ancho: 615px, Alto: 305px`.
* **Slots de Campos:**
  * **Eje Y:** `dim_personal[nombre_completo]`
  * **Eje X:** `_Medidas[Perforista Rendimiento (m/g)]` (Ratio real: metros por guardia asignada).
  * **Tooltips:** `_Medidas[Metraje Perforado Total (m)]`, `_Medidas[Nro Guardias Perforadas]`
* **Filtro de Objeto Visual (Panel de Filtros lateral):**
  * Arrastrar `_Medidas[Perforista Es Elegible Top]` y filtrar en **`es igual a 1`** (Asegura un umbral mínimo de >= 3 guardias para no distorsionar el ranking con suplentes de 1 solo turno).
  * Tipo de filtro en `dim_personal[nombre_completo]`: **Top N** -> Superior: **`10`** según `_Medidas[Perforista Rendimiento (m/g)]`.
* **Línea de Referencia:** Línea constante en `12.58 m/guardia` (Meta contractual de guardia).

---

### D. Visual 4: Cuadrantes de Flota y Productividad (Scatter Plot)
* **Objeto Visual:** **Gráfico de dispersión nativo (*Scatter Plot*)**.
* **Posición:** `X: 655px, Y: 395px, Ancho: 605px, Alto: 305px`.
* **Slots de Campos:**
  * **Valores:** `dim_equipo_perforadora[codigo_maquina_limpio]`
  * **Eje X:** `_Medidas[Horas Efectivas Perforacion (h)]`
  * **Eje Y:** `_Medidas[Ratio Perforacion Real (m/h)]`
  * **Tamaño:** `_Medidas[Metraje Perforado Total (m)]`
  * **Leyenda:** `dim_contrato_minero[nombre_contrato_limpio]` (Colores agrupados por Contrato).
* **Línea Dinámica de Promedio:**
  * En el panel **Análisis (*Analytics*)** del visual -> desplegar **Línea promedio (*Average line*)** -> Agregar línea sobre el Eje Y (`Ratio Perforacion Real (m/h)`). Power BI recalcula dinámicamente el promedio según los filtros activos.

---

## ⏱️ 5. SLIDE 3: TIEMPOS, DISPONIBILIDAD Y TAXONOMÍA SIG (MANTENIMIENTO)

### A. Visual 1: Distribución de Horas SIG: Ideal vs Real y por Contrato (Barras 100% Apiladas)
* **Objeto Visual:** **Gráfico de barras 100% apiladas nativo**.
* **Posición:** `X: 20px, Y: 80px, Ancho: 615px, Alto: 300px`.
* **Configuración del Visual (Comparativa: Distribución Meta vs Real Ejecutado):**
  * **Eje Y:** `tbl_escenario_horas[Escenario]` ("Distribución Meta" vs "Real Ejecutado").
  * **Eje X (Valores):** `_Medidas[% Distribucion Horas Escenario]`.
  * **Leyenda:** `dim_taxonomia_actividad[categoria_disponibilidad]` (Las categorías SIG).
* **Porcentajes de Distribución Meta:**
  * **Tiempo Efectivo - Operativo:** **`57.5%`** (0.575).
  * **Mantenimiento:** **`5.0%`** (0.050).
  * **Stand By Inoperativo:** **`37.5%`** (0.375).
  * **Stand By Operativo:** `0.0%`.
  * **Stand By Cliente:** `0.0%`.
  * **TOTAL:** **`100.0%`**.
* **¿Cómo Modificar estos Porcentajes en el Futuro?:**
  * En Power BI Desktop, ve a la tabla `_Medidas` y haz clic en la medida **`[% Distribucion Horas Escenario]`**.
  * En la barra de fórmulas DAX superior, edita los valores dentro del bloque `SWITCH(_Categoria, ...)`:
    * `"Tiempo Efectivo - Operativo", 0.575`
    * `"Mantenimiento", 0.050`
    * `"Stand By Inoperativo", 0.375`
  * Presiona `Enter`. El gráfico se actualizará automáticamente con los nuevos valores.
* **Alternativa para Múltiples CTRs:** Si deseas comparar contratos mineros individuales entre sí en lugar de la meta global, cambia el **Eje Y** a `dim_contrato_minero[nombre_contrato_limpio]` y usa `_Medidas[% Distribucion Horas por CTR]`. Cada contrata tendrá su propia barra sumando 100% sin mezclar datos.

---

### B. Visual 2: Disponibilidad (% DM) vs Utilización (% UT) por Contrato
* **Objeto Visual:** **Gráfico de columnas agrupadas nativo**.
* **Posición:** `X: 655px, Y: 80px, Ancho: 605px, Alto: 300px`.
* **Slots de Campos:**
  * **Eje X:** `dim_contrato_minero[nombre_contrato_limpio]`
  * **Eje Y:** `_Medidas[Disponibilidad Mecanica (% DM)]` (Verde `#0F9D58`) y `_Medidas[Utilizacion Operativa (% UT)]` (Azul `#1E3A8A`).
  * **Línea de Referencia:** Línea constante en `85.0%` (Meta DM).

---

### C. Visual 3: Causa Raíz de Paradas (Decomposition Tree Nativo)
* **Objeto Visual:** **Árbol de descomposición nativo (*Decomposition Tree*)**.  
  *(Ubicación: En el panel de visualizaciones, ícono de bifurcación de 3 ramas `├──`, fila 6, entre influenciadores clave y preguntas y respuestas).*
* **Posición:** `X: 20px, Y: 395px, Ancho: 615px, Alto: 310px`.
* **Slots de Campos:**
  * **Analizar (*Analyze*):** `_Medidas[Total Horas Reportadas (h)]`
  * **Explicar por (*Explain by* en orden jerárquico):**
    1. `dim_taxonomia_actividad[categoria_disponibilidad]`
    2. `dim_taxonomia_actividad[bloque_funcional]`
    3. `dim_taxonomia_actividad[nombre_actividad]`
    4. `dim_equipo_perforadora[codigo_maquina_limpio]`

---

### D. Visual 4: Pareto de Stand By Cliente (Horas Cobrables en Valorizaciones)
* **Objeto Visual:** **Gráfico de columnas agrupadas nativo**.
* **Posición:** `X: 655px, Y: 395px, Ancho: 605px, Alto: 310px`.
* **Slots de Campos:**
  * **Eje X:** `dim_taxonomia_actividad[nombre_actividad]`
  * **Eje Y de Columnas:** `_Medidas[Total Horas Reportadas (h)]` (Orden descendente).
* **Filtro Exclusivo de este Gráfico:**
  * En el panel lateral **Filtros** -> sección **"Filtros en este objeto visual"** -> arrastrar `dim_taxonomia_actividad[categoria_disponibilidad]` y marcar únicamente **"Stand By Cliente"**. Solo afectará a este gráfico sin alterar el resto del slide.

---

## 💰 6. SLIDE 4: COSTO DE OPORTUNIDAD Y METROS PERDIDOS POR PARADAS

### A. Visual 1: Cascada Puente: Del Real a la Meta (Total = Meta Contractual)
* **Objeto Visual:** **Gráfico de cascada nativo (*Waterfall Chart*)**.
* **Posición:** `X: 20px, Y: 65px, Ancho: 790px, Alto: 635px`.
* **Slots de Campos Exactos:**
  * **Categoría (*Category*):** `tbl_cascada_perdidas[Concepto]`
  * **Eje Y (*Y-Axis*):** `_Medidas[Monto Cascada Metros]`
  * **Desglose (*Breakdown*):** Vacío.
* **Cálculo 100% Dinámico de Proporciones (Cero Constantes Hardcodeadas):**
  * La medida `_Medidas[Monto Cascada Metros]` calcula en tiempo real las horas de cada causa según los filtros activos:
    * `_H_Cliente = [Horas Stand By Cliente (h)]`
    * `_H_Mtto = [Horas Mantenimiento Mecanico (h)]`
    * `_H_Cuadrillas = [Horas Stand By Inoperativo (h)]`
  * Las proporciones de la brecha se calculan al vuelo: `DIVIDE(_H_Cliente, _TotalHoras, 0)`, garantizando que si filtras **Cobriza**, **Inmaculada** o **Catalina Huanca**, los metros perdidos reflejen la realidad operativa de esa mina específica.
* **Comportamiento Visual Exacto (La barra de Total es la Meta):**
  * **Paso 1 (Barra Inicial Azul):** `1. Real Perforado` (Avance real alcanzado bajo el filtro activo).
  * **Paso 2 (Escalón Verde de Recuperación):** `2. Demoras de Mina (Cliente)` (Metros perdidos por mina).
  * **Paso 3 (Escalón Verde de Recuperación):** `3. Taller Mecanico` (Metros perdidos por taller mecánico).
  * **Paso 4 (Escalón Verde de Recuperación):** `4. Cuadrillas y Traslados` (Metros perdidos por personal/inoperativo).
  * **Barra Final de TOTAL (Power BI la calcula automáticamente):** Suma exactamente el Real más todas las brechas dinámicas, igualando al centésimo **la Meta Contractual del período**.
* **En el panel de formato del gráfico $\rightarrow$ Total:**
  * Renombra la etiqueta del Total como: **`"Meta al Día 6"`**.
  * Cuadra al 100% de forma dinámica en cualquier nivel de agregación (Flota Global o Contrato Individual).

---

### B. Visual 2: Matriz de Control de Umbrales Operativos de Actividad
* **Objeto Visual:** **Tabla nativa**.
* **Posición:** `X: 830px, Y: 65px, Ancho: 430px, Alto: 330px`.
* **Campos:**
  * `tbl_parametros_umbrales[Actividad]`
  * `tbl_parametros_umbrales[Tipo_Control]`
  * `tbl_parametros_umbrales[Horas_Limite]`
  * `_Medidas[Alerta Exceso Preventivo (> 1h)]`
  * `_Medidas[Alerta Subreporte Falta Camara (< 9h)]`
  * `_Medidas[Alerta Exceso Standby Cliente (> 4%)]`

---

### C. Visual 3: Tarjeta de Desviación Real a la Fecha
* **Posición:** `X: 830px, Y: 410px, Ancho: 430px, Alto: 290px`.
* **Métrica Principal:** `_Medidas[Card Brecha a la Fecha (m)]` (**`-2,618.74 m`**)
* **Texto de Apoyo:** *"Meta al día 6: 10,121.65 m vs Real: 7,502.91 m | Brecha real: -2,618.74 m"*

---

## 📋 7. MATRIZ MAESTRA DE ASIGNACIÓN DE CAMPOS (CHEAT SHEET)

| Slide | Objeto Visual | Tipo de Visual | Eje / Filas / Categoría | Medida Principal | Tooltip / Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | Slicer Año | Tile Slicer | `dim_tiempo_calendario[anio_operativo]` | — | — |
| **01** | Slicer Mes | Dropdown | `dim_tiempo_calendario[mes_nom_operativo]` | — | Orden cronológico 1 a 12 |
| **01** | Slicer Contrato | Dropdown Search | `dim_contrato_minero[nombre_contrato_limpio]`| — | Nombres limpios |
| **01** | Badge Calendario| Card / Badge | — | `[Badge Calendario Operativo]` | Día 6 de 31 (25 restantes) |
| **01** | KPI Metraje Real| Card New | — | `[Metraje Perforado Total (m)]` | Subtexto: `[Subtexto Meta Mes]` |
| **01** | KPI Cierre Proy | Card New | — | `[Proyeccion Cierre Run-Rate (m)]` | Subtexto: `[Subtexto Brecha Proyeccion]` |
| **01** | KPI Ritmo Req   | Card New | — | `[Ritmo Requerido (m/dia)]` | Subtexto: `[Subtexto Aceleracion Requerida]` |
| **01** | KPI DM & UT     | Card New (2 Col)| — | `[% DM]` y `[% UT]` | Callouts grandes en paralelo |
| **01** | Ranking Metas   | **OKViz Bullet** | `nombre_contrato_limpio` | Real: `[Metraje Total]`, Target: `[Meta Mes]` | `[% Cumplimiento Meta]` |
| **01** | Curva S Avance  | Line Chart | `dim_tiempo_calendario[dia_ciclo_operativo]` | `[Metraje Acumulado Real]`, `[Meta Acumulada]` | Sin caídas a 0 en días futuros |
| **02** | Matriz Máquinas | Matriz Nativa | N1: `nombre_contrato_limpio`, N2: `codigo_maquina_limpio` | `[Meta/g]`, `[Turno Día]`, `[Turno Noche]`, `[% Cump]` | Data Bars en `[% Cump]` |
| **02** | Brecha Turnos   | **Nova Silva Dumbbell** | Category: `nombre_contrato_limpio` | Value: `[Metraje Total]`, Legend: `turno_guardia` | `[Brecha Turno Dia vs Noche]` |
| **02** | Top 10 Perforistas| Clustered Bar Chart | `dim_personal[nombre_completo]` | `[Metraje Perforado Total (m)]` (Top 10) | `[Metros por Guardia (m/g)]` |
| **02** | Dispersión Flota| Scatter Plot | `codigo_maquina_limpio` | X: `[Horas Op]`, Y: `[Ratio m/h]`, Legend: `nombre_contrato_limpio` | Línea promedio dinámica |
| **03** | Horas Dual/Real | Barras 100% Apiladas | `tbl_escenario_horas[Escenario]` | `[% Distribucion Horas Escenario]` | Legend: `categoria_disponibilidad` |
| **03** | % DM vs % UT    | Columnas Agrupadas | `nombre_contrato_limpio` | `[% DM]`, `[% UT]` | Línea Ref: 85% DM |
| **03** | Árbol Paradas   | **Decomposition Tree** | — | `[Total Horas]` -> `categoria` -> `bloque` -> `actividad` | — |
| **03** | Pareto Cliente  | Col. Agrupadas | `nombre_actividad` | `[Total Horas]` (Filtro en objeto visual: Standby Cliente) | Orden descendente |
| **04** | Selector Ratio  | Slicer Tile | `tbl_selector_ratio[Tipo_Ratio]` | — | — |
| **04** | Cascada Metros  | **Waterfall Chart** | Category: `tbl_cascada_perdidas[Concepto]` | Y-Axis: `[Monto Cascada Metros]` | Desglose vacío |
| **04** | Umbrales Campo  | Tabla Nativa | `tbl_parametros_umbrales[Actividad]` | `Horas_Limite`, Alerta Preventivo, Alerta Cámara | Semáforos condicionales |

---

## 🔒 8. CHECKLIST FINAL DE CALIDAD EN POWER BI DESKTOP

1. [ ] **Sincronizar Segmentadores:** En *Ver -> Sincronizar segmentadores*, activar el slicer de `anio_operativo`, `mes_nom_operativo` y `nombre_contrato_limpio` para que se propague a las 4 páginas.
2. [ ] **Persistencia Local:** En Power BI Desktop, presiona **`Ctrl + S`** para persistir el archivo `.pbix` en disco con todas las medidas y columnas calculadas inyectadas.
