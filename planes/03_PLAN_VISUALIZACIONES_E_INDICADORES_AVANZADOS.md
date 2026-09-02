# 📊 PLAN MAESTRO DE VISUALIZACIONES, INDICADORES Y ARQUITECTURA DE INFORMACIÓN
## Rockdrill Group — Control de Operaciones de Perforación Diamantina (DDH)
**Documento Técnico:** `planes/03_PLAN_VISUALIZACIONES_E_INDICADORES_AVANZADOS.md`  
**Autor:** Antigravity (Pair Programming con Senior BI Visualization Engineer & Mining Domain Specialist)  
**Fecha:** Setiembre 2026  
**Insumo Base:** `indicadores.txt` (Ideas y Requerimientos Operativos de Gerencia y Residencia)  

---

## 🎯 1. VISIÓN GENERAL Y ENFOQUE ARQUITECTÓNICO

El documento `indicadores.txt` reúne las necesidades reales del negocio: control de desviaciones diarias, exigencia de cumplimiento de metas, separación nítida entre Disponibilidad (% DM) y Utilización (% UT), monitoreo de pérdidas por falta de personal y una visión ejecutiva estructurada de **Macro a Micro**.

Para transformar estas ideas en una herramienta de clase mundial sin saturar al usuario, aplicamos:
1. **Buenas Prácticas de Visualización de Google:**
   * **Máximo Data-to-Ink Ratio:** Eliminar bordes pesados, fondos 3D y cuadrículas redundantes.
   * **Atributos Pre-atencionales:** El color se usa **exclusivamente para comunicar estado** (Gris para real, Negro para meta, Verde para superávit, Rojo/Naranja para déficit crítico).
   * **Reducción de Carga Cognitiva:** Evitar gráficos de torta con más de 3 categorías y barras apiladas de alta densidad.
2. **Estándares IBCS (International Business Communication Standards):**
   * Barras de desviación (*Variance Bars*) en lugar de comparar dos barras adyacentes mentalmente.
   * Gráficos *Bullet* (termómetros de desempeño) para metas diarias y mensuales.
   * *Small Multiples* (múltiplos pequeños) para comparar máquinas y contratos con la misma escala.
3. **Custom Visuals Certificados de Microsoft AppSource:**
   * **Zebra BI Tables & Charts** (o en su defecto visuales nativos optimizados con SVG y barras integradas).
   * **Bullet Chart by OKViz** (el mejor visual para meta vs real con rangos aceptables).
   * **Árbol de Descomposición (Decomposition Tree - Nativo):** Ideal para explorar de raíz por qué se perdieron horas o metros (CTR -> Máquina -> Categoría Standby -> Motivo específico).

---

## 🧭 2. ESTRUCTURA NARRATIVA DE NAVEGACIÓN (MACRO A MICRO)

Organizamos el Dashboard en **4 Páginas Especializadas** que responden a diferentes preguntas de negocio y niveles jerárquicos:

```text
+---------------------------------------------------------------------------------------------------------+
|                                    NIVEL 1: RESUMEN EJECUTIVO & METAS CTR                               |
|                     (Gerencia de Operaciones / Directorio - ¿Vamos a cumplir el mes?)                   |
|  - Metraje Total vs Meta Mensual  - Required Run-Rate (m/día)  - % Cumplimiento por CTR (Macro)        |
+---------------------------------------------------------------------------------------------------------+
                                                     │ (Drill-through / Cross-filtering)
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                    NIVEL 2: FLOTA, MÁQUINAS Y TURNOS                                    |
|                       (Jefes de Operaciones / Residentes - ¿Qué máquina se desvió?)                     |
|  - Meta Diaria por Máquina (Bullet Charts)  - Comparativa Turno A (Día) vs B (Noche)  - Ratios (m/h)   |
+---------------------------------------------------------------------------------------------------------+
                                                     │ (Navegación / Exploración)
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                  NIVEL 3: TIEMPOS, DISPONIBILIDAD & PARADAS                             |
|                 (Mantenimiento Mecánico y Control Operativo - ¿Dónde se fueron las horas?)              |
|  - DM % vs UT % por CTR  - Paretos Standby Cliente  - Distribución Meta (57.5/5/37.5) vs Real           |
+---------------------------------------------------------------------------------------------------------+
                                                     │ (Análisis Causa-Raíz)
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                  NIVEL 4: COSTO DE OPORTUNIDAD & METROS PERDIDOS                        |
|              (Gestión Humana y Contratos - ¿Cuántos metros dejamos de facturar y por qué?)             |
|  - Metros Perdidos por Falta Personal  - Metros Perdidos por Mtto  - Control Umbrales Falta Cámara      |
+---------------------------------------------------------------------------------------------------------+
```

---

## 🧮 3. CATÁLOGO MATEMÁTICO DE INDICADORES (CON DATA REAL AUDITADA)

A partir de la data real auditada de Rockdrill (`7,502.91 m` perforados y `7,687.0 h` reportadas en 22 CTRs), definimos las métricas exactas:

### A. Cumplimiento y Ritmo Diario Requerido (Required Run-rate)

#### 1. Meta Diaria Prorrateada por Máquina y Guardia
* **Concepto:** Las metas en `fact_metas_mensuales` están planteadas para el mes operativo (ej. Setiembre 2026: 31 días, del 26 de agosto al 25 de setiembre).
* **Fórmula DAX:**
  ```text
Meta Diaria (m/día) = Meta Mensual (m) / Días del Ciclo (31)
Meta por Guardia (m/guardia) = Meta Diaria (m/día) / 2 guardias (Día/Noche)
```
* *Ejemplo Real:* Para una máquina con meta mensual de `780.17 m`:
  * Meta Diaria = 780.17 / 31 = **25.17 m/día**.
  * Meta por Guardia = 25.17 / 2 = **12.58 m/guardia**.

#### 2. Ritmo Diario Requerido de Cierre (*Required Run-rate*)
* **Concepto:** Señala a los residentes a qué velocidad diaria deben perforar los días que faltan para no incumplir el contrato.
* **Fórmula DAX:**
  ```text
Ritmo Requerido (m/día) = MAX(0, Meta Mensual - Metraje Real Acumulado) / Días Restantes del Ciclo
```
* *Caso Práctico:* Si un CTR tiene `5,475 m` de meta, lleva perforados `903 m` y restan 18 días de ciclo:
  * Ritmo Requerido = (5,475 - 903) / 18 = **254.0 m/día**.
  * Si el histórico actual del CTR es de `180 m/día`, el semáforo alerta **DÉFICIT PROYECTADO**.

---

### B. Tiempos: Disponibilidad Mecánica (% DM) vs Utilización (% UT)

#### Duración Estándar de Turnos por Operación
* **Regla General:** **12.0 horas por turno** (Guardia A: Día, Guardia B: Noche = 24.0 h/día por máquina).
* **Excepciones Operativas Validadas en Datos:**
  * **CONTRATO CATALINA HUANCA:** **`10.15 horas/guardia`** (Régimen especial de jornada minera efectiva).
  * **CONTRATO YAULIYACU:** **`11.00 horas/guardia`** (Acuerdo operativo de relevo y tránsito).
  * *(El resto de contratos: Cobriza, Chungar, Raura, Americana, etc. operan a 12.00 h/guardia).*

En minería y sondajes diamantinos la disponibilidad y la utilización responden a áreas totalmente distintas:
* **Disponibilidad Mecánica (% DM):** Mide la gestión del **Área de Mantenimiento Mecánico**. ¿La perforadora estaba mecánicamente apta para operar? El mínimo contractual exigido es **85.0%**.
* **Utilización (% UT):** Mide la gestión del **Área de Operaciones y Mina**. De las horas en que la máquina estuvo disponible, ¿cuánto tiempo realmente estuvo cortando roca?

#### Fórmulas Estándar Oficiales:
```text
Horas Mecánicamente Disponibles = Total Horas Reportadas - Horas Mantenimiento Mecánico

% DM = (Horas Mecánicamente Disponibles / Total Horas Reportadas) × 100   [Meta Contractual: >= 85.0%]

% UT = (Horas Efectivas de Perforación / Horas Mecánicamente Disponibles) × 100
```

#### Benchmarks Reales Auditados en la Data de Rockdrill:
| Contrato Minero | Horas Reportadas | Mtto Mecánico | Horas Disponibles | Horas Efectivas Perforación | **% DM (Mecánica)** | **% UT (Operación)** | Diagnóstico Operativo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **CONTRATO CHUNGAR** | 864.0 h | 28.5 h | 835.5 h | 168.5 h | **96.7%** | **20.2%** | Excelente mecánica, pero subutilizada por mina/standbys |
| **CONTRATO AMERICANA** | 288.0 h | 10.5 h | 277.5 h | 73.5 h | **96.4%** | **26.5%** | Alta disponibilidad, utilización moderada |
| **CONTRATO CATALINA HUANCA**| 609.0 h (10.15h/g)| 24.0 h | 585.0 h | 189.5 h | **96.1%** | **32.4%** | Muy equilibrada; la mejor utilización del grupo |
| **CONTRATO ANDAYCHAGUA**| 432.0 h | 19.0 h | 413.0 h | 127.0 h | **95.6%** | **30.8%** | 210 h en Standby Inop (charlas, traslados, personal) |
| **CONTRATO COBRIZA** | 720.0 h | 42.5 h | 677.5 h | 239.0 h | **94.1%** | **35.3%** | Mayor desgaste mecánico pero alto aprovechamiento |
| **CONTRATO RAURA** | 576.0 h | 36.0 h | 540.0 h | 181.5 h | **93.8%** | **33.6%** | Mantenimiento demandante en terreno difícil |

> [!IMPORTANT]
> **Hallazgo Crítico:** La Disponibilidad Mecánica promedio supera holgadamente el 85% contractual (**> 94%** en todos los contratos), lo que demuestra que los mecánicos tienen las máquinas listas. **El cuello de botella está en la Utilización (20% a 35%)**, consumida principalmente por **Stand By Inoperativo (51.9%)** y demoras operativas.

---

### C. Ratios de Perforación (m/h)

* **Fórmula:**
  ```text
Ratio de Perforación (m/h) = Metraje Perforado Total (m) / Horas Efectivas de Perforación (h)
```
* **Exclusión de Máquinas Siniestradas:** Se añade un filtro en el cálculo DAX para omitir equipos en estado `SINIESTRADA` o `INOPERATIVA_PROLONGADA` (ej. en Cobriza) para no distorsionar el promedio de la flota activa.
* **Valores Reales por Contrato:**
  * Americana: **5.74 m/h** *(Alta velocidad / Terreno favorable)*
  * Chungar: **4.35 m/h**
  * Raura: **4.08 m/h**
  * Cobriza: **3.78 m/h**
  * Andaychagua: **3.62 m/h**
  * Catalina Huanca: **3.57 m/h** *(Formación dura / Fracturada)*

---

### D. Metros Perdidos por Standby (Costo de Oportunidad)

* **Concepto:** Cuantificar el metraje que Rockdrill dejó de perforar y facturar debido a causas específicas (Falta de Personal, Mantenimiento, Traslados, Esperas de Cámara).
* **Fórmula General:**
  ```text
Metros Perdidos = Horas de Standby × Ratio de Perforación (m/h)
```
* **Los 2 Modelos de Ratio Implementados (Conmutables por Selector DAX):**
  * **Opción A (Ratio Real del Mes en Curso):**  
    ```text
Ratio Real Mes = Metros Perforados Mes Actual / Horas Efectivas Perforación Mes Actual
```  
    *Ventaja:* Refleja la pérdida tangible y concreta al ritmo exacto que la cuadrilla viene perforando hoy.
  * **Opción B (Ratio Promedio Ponderado de los Últimos 3 Meses — Rolling 3M):**  
    ```text
Ratio Rolling 3M = Suma(Metros Perforados últimos 3 meses) / Suma(Horas Efectivas últimos 3 meses)
```  
    *Ventaja:* Elimina la distorsión del sesgo de meta inalcanzable y suaviza anomalías mensuales puntuales, midiendo la pérdida frente a la verdadera capacidad media probada de la operación.
* **Impacto Real en la Data Actual (a Ratio Promedio de ~4.0 m/h):**
  * **Falta de Personal (Gestión Humana):** 655.0 horas × 4.0 m/h = **`2,620 metros perdidos`**.
  * **Traslado de Personal:** 1,130.0 horas × 4.0 m/h = **`4,520 metros perdidos`**.
  * **Mantenimiento Correctivo:** 334.0 horas × 4.0 m/h = **`1,336 metros perdidos`**.
  * **Stand By Cliente:** 290.0 horas × 4.0 m/h = **`1,160 metros perdidos`** *(Horas facturables al cliente según contrato)*.

---

### E. Distribución de Horas Meta vs Real (Estructura Dual de 2 Pilares)

Para superar el modelo antiguo estático (57.5 / 5.0 / 37.5) y dotar al Dashboard de flexibilidad operativa ante la realidad de cada contrato, la estructura de horas meta se organiza en **Dos Pilares Complementarios**:

```text
+-------------------------------------------------------------------------------------------------------------------------+
|                                    ESTRUCTURA DUAL DE DISTRIBUCIÓN DE HORAS META (100%)                                 |
+-------------------------------------------------------------+-----------------------------------------------------------+
|             PILAR I: REGLAS DETERMINÍSTICAS (GOBERNANZA)     |         PILAR II: COMPONENTES VARIABLES (PARAMÉTRICOS)    |
|   1. Mantenimiento Mecánico Meta (15.0% Fijo - DM >= 85%)   |   Actividades Recurrentes Inevitables (Traslados,        |
|   2. Perforación Efectiva Meta (Ratio Mes Mayor Cumplimiento)|   Refrigerio, Orden y Limpieza) y Acuerdos de Gestión:    |
|                                                             |   3. Stand By Operativo Meta (Pauta Técnica Maniobras)    |
|                                                             |   4. Stand By Cliente Meta   (Tope Tolerancia Mina)       |
|                                                             |   5. Stand By Inoperativo    (Remanente Calibrable)       |
|                                                             |   *Calibración: Estudios Históricos o Convención Gerencia |
+-------------------------------------------------------------+-----------------------------------------------------------+
```

#### Pilar I: Componentes Determinísticos y Contractuales (Fijos)

1. **Mantenimiento Mecánico Meta (`15.0% Fijo`):**  
   Basado en la cláusula contractual estándar de Disponibilidad Mecánica mínima del **85.0%**.  
   ```text
Presupuesto Máximo Taller Mecánico = 15.0% × Total Horas Reportadas
```
2. **Perforación Efectiva Meta (% PEP_Meta — Dinámico por CTR):**  
   Calculado a partir de la Meta de Metros del mes actual y el **Ratio de Perforación (m/h) del Mes Récord de Mayor Cumplimiento**:
   ```text
Horas Perforación Meta = Meta de Metros del Mes Actual (m) / Ratio Histórico Óptimo de Mayor Cumplimiento (m/h)
```
   ```text
Horas Perforación Meta = Meta de Metros del Mes Actual (m) / Ratio Histórico Óptimo de Mayor Cumplimiento (m/h)
```
   *(Garantiza una meta exigente pero 100% alcanzable, libre de sesgos de metas de metros infladas o desfasadas).*

---

#### Pilar II: Componentes Variables y Paramétricos (Estudios Históricos y Convenciones de Gerencia)

El modelo reconoce que en la operación minera existen **actividades recurrentes indispensables** que ocurren *sí o sí* en cada guardia de campo:
* **Traslado de personal:** Ingreso y salida de bocamina a cámara.
* **Refrigerio de cuadrilla:** Tiempo legal de alimentación.
* **Orden, limpieza y recojo de lama:** Mantenimiento del área de trabajo.
* **Charlas de seguridad y reparto de guardia:** Cumplimiento legal diario.

Para no atar al Dashboard a porcentajes rígidos, las metas de las 3 categorías restantes serán **variables y calibrables** mediante dos vías:
* **Vía A — Estudios Históricos de Tiempos y Movimientos:** Análisis empírico de cuánto tardan los traslados y refrigerios en cada mina específica (ej. un traslado en Cobriza o Catalina Huanca difiere enormemente de una labor superficial o de acceso rápido).
* **Vía B — Convenciones de Gerencia de Operaciones:** Metas fijadas por directiva gerencial (ej. metas de reducción de tiempos muertos o acuerdos de tolerancia con el cliente minero).

#### Implementación Técnica de la Parametrización en Power BI:
Se creará una **Tabla de Parámetros de Horas (`tbl_parametros_horas`)** en el modelo de datos para que Gerencia pueda calibrar los valores sin tocar fórmulas DAX:
1. **Stand By Cliente Meta (Tope de Tolerancia Contractual):**  
   Parametrizado por defecto en **`4.0%`** (o el valor estipulado en la convención de cada CTR). Todo exceso sobre este umbral se cataloga como hora cobrable en valorizaciones.
2. **Stand By Operativo Meta (Pauta Técnica de Maniobras Wireline):**  
   Parametrizado inicialmente en función de la perforación efectiva (≈ 0.35 × % PEP_Meta, rango típico **10% - 14%**), calibrable según el estudio de maniobras por tipo de terreno.
3. **Stand By Inoperativo Meta (Tiempo Muerto Admisible Mínimo):**  
   Calculado como el remanente admisible para las actividades recurrentes indispensables (traslado + refrigerio + charla ≈ 2h a 2.5h por guardia de 12h, rango **16% - 20%**). Cualquier hora adicional no justificada por la convención se visibiliza como ineficiencia operativa (ej. Falta de Personal o Falta de Cámara).

#### Comparativa Referencial en la Data Actual:
| Categoría de Horas | Meta Antigua | **Nuevo Modelo Dual (Pilar I + Pilar II)** | Real Ejecutado | Diagnóstico de Brecha |
| :--- | :---: | :---: | :---: | :--- |
| **Tiempo Operativo Efectivo** | 57.5% | **Dinámica según Ratio Récord (~45% - 60%)** | **26.3%** | Brecha crítica por baja utilización |
| **Mantenimiento Mecánico** | 5.0% | **15.0% Fijo (Tope Contractual DM >= 85%)** | **4.3%** | Desempeño sobresaliente de mantenimiento |
| **Stand By Operativo** | *(No existía)* | **Paramétrico: Maniobra Wireline (~10% - 14%)** | **13.7%** | Alineado al estándar técnico de maniobra |
| **Stand By Cliente** | *(No existía)* | **Paramétrico: Tope Contractual Tolerable (4.0%)**| **3.8%** | Dentro del margen normal de mina |
| **Stand By Inoperativo** | 37.5% | **Paramétrico: Remanente Actividades Recurrentes (~16% - 20%)** | **51.9%** | <span style="color:red">**Exceso severo (+32%) por traslados y personal**</span> |

---

## 🖥️ 4. PROPUESTA DE DISEÑO DE PÁGINAS Y VISUALES (GOOGLE DATA VIZ / IBCS)

### Página 1: Torre de Control Operativa & Cumplimiento de Metas (Nivel Macro)
* **Público Objetivo:** Gerencia General, Gerencia de Operaciones.
* **Filtros Superiores (Slicers compactos):** Mes Operativo, Zona Geográfica, Contrato (CTR).
* **Fila 1 (Tarjetas KPI con Micro-sparklines):**
  * `Metraje Total Perforado` (con % vs Meta).
  * `Proyección Cierre Run-Rate` (Metros estimados a fin de mes).
  * `Ritmo Requerido (m/día)` (con indicador de advertencia si supera la capacidad real).
  * `Horas Efectivas de Perforación` (% sobre el total).
* **Fila 2 (Cuerpo Principal - Visual Recomendado):**
  * **Lado Izquierdo:** **Gráfico de Barras Horizontales con Marcador de Meta (IBCS Variance Bar / Bullet Chart)**:
    * Muestra cada CTR.
    * Barra gris: Metraje Real.
    * Línea vertical negra: Meta prorrateada al día de hoy.
    * Permite ver de un vistazo qué contratos están en verde y cuáles en rojo.
  * **Lado Derecho:** **Curva de Avance Acumulado vs Trayectoria Planificada (Line Chart)**:
    * Eje X: Días del ciclo minero (del 26 al 25).
    * Línea 1 (Continua): Metraje Acumulado Real.
    * Línea 2 (Punteada): Meta acumulada ideal.
    * Línea 3 (Segmentada proyectada): Proyección Run-rate hasta el día 25.
* **Interactividad:** Al hacer clic en una barra de un CTR (ej. Cobriza), todo el reporte se filtra a ese contrato y habilita el botón de *Drill-through* hacia el Nivel 2.

---

### Página 2: Desempeño de Perforadoras & Eficiencia Horaria (Nivel Micro)
* **Público Objetivo:** Residentes de Obra, Jefes de Perforación.
* **Visual 1 (Cumplimiento de Meta Diaria por Máquina):**
  * *Recomendación sobre la idea de barras apiladas día/noche:* Como acertadamente previste, barras apiladas para 76 máquinas saturaría la vista (efecto "código de barras").
  * *Solución Google Data Viz:* **Matriz con Barras de Datos Integradas (Data Bars) o Small Multiples**:
    * Columnas: Máquina | Meta Diaria (m) | Turno Día (m) | Turno Noche (m) | Total Real (m) | % Cumplimiento | Semáforo.
    * Permite ordenar de mayor a menor desviación en 1 segundo.
* **Visual 2 (Comparativa Turno A Día vs Turno B Noche):**
  * **Gráfico Dumbbell (Gráfico de Mancuerna) o Barras Agrupadas Claras**:
    * Muestra para cada máquina dos puntos unidos por una línea: punto azul (Turno Día) y punto oscuro (Turno Noche).
    * Si la línea es muy larga, evidencia una brecha severa de productividad entre turnos (ej. el turno noche perfora 40% menos).
* **Visual 3 (Dispersión Cuadrante: Ratios m/h vs Horas Efectivas):**
  * **Scatter Plot (Gráfico de Dispersión)**:
    * Eje X: Horas Efectivas de Perforación.
    * Eje Y: Ratio de Avance (m/h).
    * Tamaño de burbuja: Metraje Total.
    * Divide el gráfico en 4 cuadrantes:
      * *Cuadrante Estrella (Superior Derecho):* Altas horas y alta velocidad.
      * *Cuadrante Cuello de Botella (Superior Izquierdo):* Rápida pero perfora pocas horas (revisar paradas).
      * *Cuadrante Mecánico (Inferior Derecho):* Perfora muchas horas pero avanza lento (terreno difícil o broca desgastada).
      * *Cuadrante Crítico (Inferior Izquierdo):* Pocas horas y lento.

---

### Página 3: Tiempos, Disponibilidad (% DM / % UT) y Taxonomía SIG
* **Público Objetivo:** Jefes de Mantenimiento Mecánico, Planificadores, Operaciones.
* **Visual 1 (Distribución Meta vs Real de Horas):**
  * *Recomendación sobre gráficos de torta:* Las tortas dificultan comparar ángulos pequeños (ej. 4.3% vs 5%).
  * *Solución Google Data Viz:* **Gráfico de Barras 100% Apiladas Comparativas (Meta vs Real)**:
    * Barra 1: Meta Histórica (57.5% Op | 5% Mtto | 37.5% Inoperativo).
    * Barra 2: Real Ejecutado (26.3% Op | 4.3% Mtto | 51.9% Inoperativo | 13.7% Standby Op | 3.8% Standby Cliente).
    * La brecha visual entre el 57.5% y el 26.3% salta a la vista al instante.
* **Visual 2 (Disponibilidad Mecánica % DM vs Utilización % UT por CTR):**
  * Gráfico de Columnas Agrupadas con línea de meta corporativa (Línea de 95% DM y 45% UT).
* **Visual 3 (Pareto de Standby Cliente - Causas Cobrables):**
  * Gráfico de Pareto (Barras ordenadas descendentes por horas de parada imputables a mina + línea de % acumulado).
  * Ideal para adjuntar en las actas de valorización y cobrar las horas de parada al cliente minero.
* **Visual 4 (Árbol de Descomposición - Root Cause Analysis):**
  * Permite al usuario desglosar libremente: Total Horas -> Categoría SIG -> Bloque Funcional -> Actividad Específica -> Máquina causante.

---

### Página 4: Costo de Oportunidad y Metros Perdidos por Paradas
* **Público Objetivo:** Gerencia de Operaciones, Gestión Humana, Mantenimiento.
* **Tarjetas de Impacto Financiero y Operativo:**
  * `Metros Perdidos por Falta de Personal` (`2,620 m`).
  * `Metros Perdidos por Mantenimiento Correctivo` (`1,336 m`).
  * `Metros Perdidos por Traslados y Logística` (`4,520 m`).
  * `Metros Recuperables por Standby Cliente` (`1,160 m`).
* **Visual 1 (Cascada de Metraje - Waterfall Chart):**
  * Inicio: **Meta Teórica Planificada (100%)**.
  * Caídas: (-) Pérdida por Falta Personal, (-) Pérdida por Mtto, (-) Pérdida por Espera Cámara, (-) Pérdida por Paradas Cliente.
  * Final: **Metraje Real Alcanzado**.
  * Este visual es el más potente en reuniones de directorio porque explica con precisión matemática a qué área corresponde cada metro que faltó.
* **Visual 2 (Monitoreo de Sub-reporte de Horas y Umbrales Mínimos):**
  * Tabla con formato condicional basada en los umbrales mínimos (ej. Parada por Falta de Cámara en guardia completa con < 9h registradas).
  * Alerta con ícono rojo las guardias donde el reporte de campo fue mal llenado por el administrador.

---

## 🚀 5. PLAN DE REVISIÓN, CONSULTA Y PRÓXIMOS PASOS

Para validar este plan antes de implementar visual por visual en Power BI Desktop, propongo seguir esta ruta estructurada:

### Paso 1: Consultas Clave para Decisión del Usuario
1. **Ratios para Metros Perdidos:** ¿Prefieres que por defecto se use el **Ratio Real del Mes** (m/h ejecutado) o el **Ratio Teórico de Meta**? (Recomiendo implementar un selector dinámico para alternar ambos).
2. **Custom Visuals de la Tienda:** ¿Tu organización permite el uso de visuales certificados de Microsoft AppSource como **Zebra BI** o **Bullet Chart by OKViz**, o nos ceñimos estrictamente a los visuales **100% nativos** de Power BI? (Ambas opciones son completamente viables; los nativos no requieren licencias adicionales).
3. **Tabla de Parámetros de Horas Mínimas:** Para el control de sub-reportes (como la falta de cámara con mínimo 9h), ¿definimos una tabla estática en DAX/Power Query con las 3 o 4 actividades críticas más frecuentes?

### Paso 2: Ejecución Técnica
Una vez que me des el visto bueno sobre este plan:
1. Crearemos las medidas DAX faltantes (Required Run-rate, % DM, % UT, Metros Perdidos, Meta Diaria Prorrateada) dentro de la tabla `_Medidas`.
2. Configuraremos las páginas y visuales paso a paso en tu Power BI Desktop.
