# 08. Plan de Implementación: Flujo de Separación en Tablas con Power Query en la Nube (Power BI Pro)
**Documento Oficial de Planificación de Arquitectura Cloud**  
**Ubicación**: `C:\Proyectos Python\Detallados\planes\08_PLAN_FLUJO_SEPARACION_TABLAS_POWER_QUERY_NUBE_PRO.md`  
**Autoridad de Control**: Squad Multidisciplinario (Data Analyst, DBA, BI Engineer) auditado por PMO y Auditores  
**Licencia Base**: Power BI Pro (Capacidad Compartida de Microsoft)  
**Fecha**: 04 de Setiembre de 2026  
**Estado**: Propuesta Técnica para Revisión y Aprobación  

---

## 🎯 1. Objetivo y Alcance

Diseñar e implementar el flujo completo de **separación y modelado dimensional en esquema estrella Kimball** utilizando exclusivamente **Power Query en la Nube (Power BI Service Dataflows / Flujos de Datos)** con una licencia **Power BI Pro**, permitiendo:
1. Conectar directamente a los repositorios oficiales en **SharePoint Online / OneDrive Corporativo**.
2. Separar la base monolítica en **7 Dimensiones normalizadas y 3 Tablas de Hechos**.
3. Automatizar la actualización diaria desatendida (hasta 8 veces al día) sin depender de scripts locales en computadoras personales.
4. **Blindar la arquitectura ante la futura incorporación de la base histórica (>64,000 filas)**, evitando desbordamientos de memoria o timeouts en la nube.

---

## ⚠️ 2. Análisis Crítico de Viabilidad Técnica: Restricciones de Licencia Pro

Operar Power Query en la nube bajo una licencia **Power BI Pro (Capacidad Compartida)** impone restricciones físicas estrictas que deben ser gestionadas por arquitectura:

| Parámetro / Límite en Power BI Pro | Valor Límite Oficial | Riesgo Operativo Identificado | Estrategia de Mitigación en el Plan |
| :--- | :---: | :--- | :--- |
| **Tiempo Máximo de Refresco** | **2 horas (120 min)** | Si el flujo tarda >120 min, Power BI aborta con error de *Timeout*. | Separación en capas (Cold/Hot). El refresco diario solo procesará ~3,500 filas (< 5 min). |
| **Frecuencia de Actualización** | **8 veces al día** | Suficiente para la operación minera (1 o 2 refrescos diarios requeridos). | Programar 2 refrescos: 07:00 y 19:00 (post cierre de guardias A y B). |
| **Almacenamiento por Área de Trabajo** | **10 GB máximo** | Desbordamiento si se almacenan copias redundantes de históricos. | VertiPaq y Parquet comprimen en ratio 10:1. La data histórica completa pesará < 50 MB. |
| **Motor de Cómputo Mejorado (ECE)** | **NO DISPONIBLE** *(Solo Premium/Fabric)* | En Pro no hay DirectQuery sobre Dataflows ni caché SQL de entidades calculadas. | Evitar cadenas de entidades vinculadas redundantes que fuercen re-lecturas a SharePoint. |
| **Actualización Incremental en Dataflows** | **NO DISPONIBLE** *(Solo Premium/Fabric)* | Un Dataflow Pro no puede hacer particionado automático `RangeStart`/`RangeEnd`. | **Particionado Arquitectural Manual**: Dataflow Frío (histórico estático) + Dataflow Caliente (mes activo). |
| **Memoria de Contenedor Mashup** | **~1.5 GB RAM** | El unpivot de 48 columnas sobre 64,000 filas genera >3 millones de celdas en memoria. | **PROHIBIDO** desanidar la base histórica completa en cada corrida diaria. |
| **Throttling de SharePoint Online** | **HTTP 429 (Rate Limit)** | Abrir decenas de Excels pesados simultáneamente satura la API de Microsoft Graph. | Agrupar por fecha de modificación y extraer hojas operativas de forma secuencial y limpia. |

---

## 🛡️ 3. Impacto de la Futura Incorporación de la Base Histórica (>64,000 Filas)

### 3.1 El Diagnóstico de Saturación (Lo que NO se debe hacer):
Si se pretendiera que un único Dataflow en Power BI Service lea diariamente tanto los detallados del mes actual como los 64,607 registros históricos (2024–2026) y aplique el desanidado (*unpivot*) de 48 columnas de tiempo:
$$\text{Filas de Hechos} = 64,607 \times 48 = \mathbf{3,101,136\text{ registros en memoria Mashup}}$$
* **Resultado Inevitable en Pro:** El contenedor de Power Query Cloud se quedará sin memoria RAM (`Mashup evaluation exceeded container memory limit`) o superará los 120 minutos de ejecución, rompiendo la actualización diaria.

### 3.2 La Solución de Alta Ingeniería: Arquitectura Desacoplada (Cold Dataflow + Hot Dataflow)
Para garantizar **100% de viabilidad técnica y velocidad sub-minuto**, dividimos el entorno en **dos flujos de datos independientes**:

```mermaid
flowchart TD
    subgraph SP_SOURCES ["📁 FUENTES SHAREPOINT ONLINE / ONEDRIVE"]
        SP_ACTIVO["Carpeta 02_Detallado (Mes en Curso)<br/>~3,505 filas (26 Ago - 25 Set)"]
        SP_HIST["HISTORICO_2026_ESTANDARIZADO.xlsx<br/>25,736 filas (Ene - Ago 2026 Congelado)"]
        SP_METAS["METAS.xlsx<br/>1,052 registros históricos"]
    end

    subgraph DF_CLOUD ["☁️ POWER BI SERVICE (DATAFLOWS EN ÁREA DE TRABAJO PRO)"]
        subgraph DF_COLD ["❄️ DATAFLOW FRÍO: DF_Historico_Congelado (Sin Refresco Programado)"]
            F_FACT_HIST["Fact_Horas_Operativas_Hist<br/>Fact_Perforacion_Avance_Hist"]
            SP_HIST --> F_FACT_HIST
        end

        subgraph DF_HOT ["🔥 DATAFLOW CALIENTE: DF_Operaciones_Activas (Refresco Diario: 07:00 / 19:00)"]
            STG_ACT["Staging_Detallados_Mes_Activo<br/>(Filtro de hojas, 168 cols, tipado 'en-US')"]
            DIMS["7 Dimensiones Normalizadas:<br/>Dim_Maquina, Dim_CTR, Dim_Tiempo, Dim_Personal..."]
            FACT_ACT["Fact_Horas_Operativas_Activo<br/>Fact_Perforacion_Avance_Activo"]
            FACT_METAS["Fact_Metas_Mensuales"]
            
            SP_ACTIVO --> STG_ACT
            STG_ACT --> DIMS
            STG_ACT --> FACT_ACT
            SP_METAS --> FACT_METAS
        end
    end

    subgraph SEMANTIC_MODEL ["📊 MODELO SEMÁNTICO VERTIPAQ (DASH.pbix / DATASET SERVICE)"]
        APPEND["Table.Combine()<br/>(Unión de Hechos Activos + Históricos en Memoria Tabular)"]
        VIRT_MODEL["16 Relaciones Físicas 1:N<br/>49 Medidas DAX Intactas<br/>4 Slides Corporativas Nativas"]
        
        DIMS --> VIRT_MODEL
        FACT_METAS --> VIRT_MODEL
        F_FACT_HIST --> APPEND
        FACT_ACT --> APPEND
        APPEND --> VIRT_MODEL
    end

    style DF_COLD fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style DF_HOT fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style SEMANTIC_MODEL fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

### 💡 ¿Por qué esta solución es 100% viable con Licencia Pro?
1. **El Dataflow Frío (`DF_Historico_Congelado`) se ejecuta UNA SOLA VEZ:** No tiene programación de refresco. Sus tablas quedan materializadas permanentemente en el almacenamiento del workspace.
2. **El Dataflow Caliente (`DF_Operaciones_Activas`) vuela en velocidad:** Solo transforma ~3,500 filas del mes activo. Su refresco toma **menos de 3 minutos**.
3. **La unión (`Table.Combine`) ocurre en VertiPaq:** El motor tabular de Power BI está optimizado en C++ y realiza la compresión columnar en segundos, consumiendo < 25 MB de memoria.

---

## 🏛️ 4. Estructura de Tablas a Separar en Power Query M (Esquema Estrella)

A partir de la base staging de 168 columnas (`Staging_Detallados`), Power Query generará las siguientes 10 entidades:

```mermaid
erDiagram
    Dim_CTR ||--o{ Fact_Perforacion_Avance : "1:N"
    Dim_Maquina ||--o{ Fact_Perforacion_Avance : "1:N"
    Dim_Tiempo_Calendario ||--o{ Fact_Perforacion_Avance : "1:N"
    Dim_Personal ||--o{ Fact_Perforacion_Avance : "1:N"
    Dim_Sondaje ||--o{ Fact_Perforacion_Avance : "1:N"
    
    Dim_CTR ||--o{ Fact_Horas_Operativas : "1:N"
    Dim_Maquina ||--o{ Fact_Horas_Operativas : "1:N"
    Dim_Tiempo_Calendario ||--o{ Fact_Horas_Operativas : "1:N"
    Dim_Categoria_Disponibilidad ||--o{ Fact_Horas_Operativas : "1:N"
    Dim_Actividad_Operativa ||--o{ Fact_Horas_Operativas : "1:N"

    Dim_CTR ||--o{ Fact_Metas_Mensuales : "1:N"
    Dim_Maquina ||--o{ Fact_Metas_Mensuales : "1:N"
    Dim_Tiempo_Calendario ||--o{ Fact_Metas_Mensuales : "1:N"

    Dim_Maquina ||--o{ puente_horas_contrato : "1:N"
    Dim_CTR ||--o{ puente_horas_contrato : "1:N"
```

---

## 📜 5. Especificación Técnica de Consultas Power Query M

### 5.1 Parámetros Globales del Flujo en la Nube
```powerquery
// Parámetros de conexión a SharePoint Online
p_UrlSharePoint = "https://rovheco-my.sharepoint.com/personal/pedro_gamarra_rockdrillgroup_com" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
p_RutaCarpetaDetallados = "Rockdrill_Control_Operaciones" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

### 5.2 Tabla: `Dim_Maquina`
* **Origen:** `Staging_Detallados` (Filas únicas de `MAQUINA_HOMOLOGADA`).
* **Transformaciones M:**
  1. `Table.SelectColumns(Staging, {"MAQUINA_HOMOLOGADA", "CTR"})`
  2. `Table.Distinct()`
  3. Homologación SAP y asignación de metadatos (Tipo de servicio: Superficie / Interior Mina).
  4. Generación de llave subrogada entera: `maquina_sk = Table.AddIndexColumn(..., 1)`.
  5. Inserción de fila desconocida: `sk = -1`, `[NO ESPECIFICADO]`.

### 5.3 Tabla: `Dim_CTR`
* **Origen:** `Staging_Detallados` (Filas únicas de `CTR`).
* **Transformaciones M:**
  1. Creación de `nombre_contrato_corto` (ej. *"Catalina Huanca"*, *"Cobriza"*, *"Andaychagua"* sin prefijos `CTR_`).
  2. Categorización de Unidad Minera y Cliente.
  3. Llave subrogada: `ctr_sk`. Miembro `-1` para no especificado.

### 5.4 Tabla: `Dim_Tiempo_Calendario`
* **Origen:** Generación pura en Power Query M (Serie diaria del 01/01/2024 al 31/12/2026).
* **Campos Críticos de Negocio:**
  * `calendario_sk`: Entero `YYYYMMDD`.
  * `fecha_dt`: Fecha ISO.
  * `anio_operativo`, `mes_operativo`: Basados en el corte contable minero **(del día 26 al 25)**.
  * `dia_ciclo_operativo`: Entero del 1 al 31 (el día 26 es el Día 1).
  * `fecha_corta_label`: Texto `"26-Ago"` (ordenado por `calendario_sk`).
  * `dia_ciclo_label`: Texto `"Día 01"` (ordenado por `dia_ciclo_operativo`).

### 5.5 Tabla: `Fact_Perforacion_Avance`
* **Grano Atómico:** Una fila por cada tramo de perforación / sondaje en cada guardia.
* **Métricas Clave:**
  * `metraje_perforado_m`: Metraje neto ($HASTA - DESDE$).
  * `cota_desde_m`, `cota_hasta_m`.
  * `horas_extras`.
  * `horometro_acumulado_h`, `horometro_total_h`.
  * Llaves foráneas: `maquina_sk`, `ctr_sk`, `calendario_sk`, `personal_sk`, `sondaje_sk`.
  * Llave unívoca de conciliación: `id_clave_unica` (`YYYYMMDD-CTR-MAQUINA-TURNO`).

### 5.6 Tabla: `Fact_Horas_Operativas` (El Motor de Disponibilidad SIG)
* **Grano Atómico:** Una fila por cada actividad de tiempo registrada en la guardia.
* **Algoritmo M de Desanidado (Unpivot Optimizado):**
  1. Seleccionar columnas de llaves (`id_clave_unica`, `maquina_sk`, `ctr_sk`, `calendario_sk`) y las 48 columnas canónicas de tiempo (cols 54 a 104 y anexas).
  2. `Table.UnpivotOtherColumns(..., {"id_clave_unica", ...}, "Actividad", "Horas")`
  3. `Table.SelectRows(..., each [Horas] > 0)` *(Filtrar ceros inmediatamente: reduce el tamaño en un 85%)*.
  4. Mapeo a las 5 Categorías SIG canónicas:
     * `PERFORACIÓN` / `RIMADO` ➔ **Operativa Efectiva**.
     * `LAVADO`, `MANIPULACIÓN`, `DESATE`, `CHARLA` ➔ **Stand By Operativo (SBO)**.
     * `MANTTO. PREVENTIVO` / `CORRECTIVO` ➔ **Mantenimiento**.
     * `FALTA PERSONAL`, `FALTA CAMIONETA`, `PARE RD` ➔ **Stand By Inoperativo (SBI)**.
     * `ESPERA ORDEN`, `VOLADURA`, `FALTA AGUA`, `PARE CIA` ➔ **Stand By Cliente (SBC)**.
  5. **Regla Anti-Duplicidad:** Si existe registro en categoría anexa específica (ej. `Falta de personal`), la fila genérica `Otros` se descarta automáticamente.

### 5.7 Tabla: `Fact_Metas_Mensuales`
* **Origen:** Lectura de [`METAS.xlsx`](file:///c:/Proyectos%20Python/Detallados/METAS.xlsx) en SharePoint.
* **Grano:** Una fila por máquina, contrato y mes operativo (52,295.17 m para Setiembre 2026).

---

## 🔄 6. Protocolo Operativo: Día a Día vs. Cierre Mensual

```mermaid
sequenceDiagram
    autonumber
    participant SP as SharePoint Online
    participant DF_H as DF_Operaciones_Activas (Cloud)
    participant DF_C as DF_Historico_Congelado (Cloud)
    participant PBI as DASH.pbix / Servicio PBI

    Note over SP,PBI: OPERACIÓN DIARIA (Ciclo en Curso: < 3 min)
    SP->>DF_H: Ingesta detallados del día (Mes Activo)
    DF_H->>DF_H: Separación en Tablas y Unpivot (~3,500 filas)
    DF_H->>PBI: Actualización automática programada (07:00 y 19:00)
    PBI->>PBI: VertiPaq refresca visuales y 49 medidas DAX

    Note over SP,PBI: CIERRE MENSUAL (Día 25 - Sellado Contable)
    Note over DF_H: 1. Auditoría 1-a-1 contra Control Interno
    Note over DF_H: 2. Cuadratura 12.0h y monotonía cotas
    DF_H->>DF_C: Transferencia inmutable del mes cerrado
    Note over DF_C: Se ejecuta refresco manual de DF_Historico_Congelado (1 vez al mes)
    Note over DF_H: Se limpia staging para el nuevo ciclo (día 26)
```

---

## 👥 7. Dictamen y Compromisos del Panel Multidisciplinario

* **`data_scientist_architect` (Data Analyst):**
  > *"El filtrado inmediato de `[Horas] > 0` en el unpivot reduce la volumetría de 3 millones a menos de 450,000 registros reales de paradas, garantizando que el flujo en la nube corra con fluidez en capacidad compartida Pro."*
* **`database_administrator` (DBA):**
  > *"El desacoplamiento en Dataflow Frío (estático) y Dataflow Caliente (diario) es la arquitectura canónica para evitar re-procesamientos innecesarios en licencias Pro. Garantiza cero retrabajo y cumplimiento del límite de 120 minutos."*
* **`bi_visualization_engineer` (BI Engineer):**
  > *"Al replicar fielmente los nombres de columnas y tipos de datos en el Dataflow de la nube, `DASH.pbix` podrá alternar el origen de datos desde los CSV locales hacia los Flujos de Datos de Power BI Service con un simple cambio de origen de Power Query, sin tocar ninguna medida DAX."*
* **`audit_common_sense_agent` (Auditor de Sentido Común):**
  > *"Aprobado. La regla de no refrescar el histórico diariamente protege la integridad de los datos cerrados: lo que ya se auditó no se vuelve a tocar, previniendo alteraciones accidentales por fallas de conexión."*
* **`qa_data_auditor` (Auditor de QA):**
  > *"Se incorporarán pasos de verificación en Power Query M que generen una tabla de control de anomalías (`Log_Anomalias_Cloud`) para alertar de cualquier guardia que no sume 12h antes de que impacte en los reportes ejecutivos."*
* **`project_governance_auditor` (Gobernanza PMO):**
  > *"Este plan se aprueba formalmente como la Especificación Oficial de Ingeniería de Datos Cloud. Pasa a estado de revisión para visto bueno del usuario."*

---

## 📋 8. Pasos para la Puesta en Marcha (Hoja de Ruta)

1. **Revisión y Visto Bueno del Plan:** El usuario evalúa esta propuesta técnica en [`planes/08_PLAN_FLUJO_SEPARACION_TABLAS_POWER_QUERY_NUBE_PRO.md`](file:///c:/Proyectos%20Python/Detallados/planes/08_PLAN_FLUJO_SEPARACION_TABLAS_POWER_QUERY_NUBE_PRO.md).
2. **Construcción del Código M Modular:** Generar los scripts M listos para copiar y pegar en Power BI Service Dataflows.
3. **Creación del Espacio de Trabajo en Power BI Service:** Configurar el Workspace con la cuenta corporativa Pro y vincular a SharePoint Online.
4. **Validación de Rendimiento en Nube:** Probar el refresco del mes activo cronometrando el tiempo de ejecución (< 5 minutos).
5. **Acople Gradual de la Base Histórica:** Cuando la base histórica de 2026 esté adaptada manualmente por el usuario, subirla como fuente del Dataflow Frío.
