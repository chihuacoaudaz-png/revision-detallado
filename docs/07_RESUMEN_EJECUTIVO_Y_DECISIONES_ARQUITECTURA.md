# 07. Resumen Ejecutivo, Bitácora de Decisiones y Contexto del Proyecto
**Proyecto**: Sistema Unificado de Business Intelligence y Analítica de Perforación  
**Ubicación**: `C:/Proyectos Python/Detallados/docs/07_RESUMEN_EJECUTIVO_Y_DECISIONES_ARQUITECTURA.md`  
**Organización**: Rockdrill Group  
**Fecha de Compilación**: 2026-08-28  

---

## 🎯 1. Resumen Ejecutivo del Proyecto

Este repositorio contiene la arquitectura completa de **Ingesta, Limpieza, Conciliación Diaria 1-a-1 y Modelado Dimensional (Star Schema)** para los Reportes Detallados de Perforación (`RD.402.P.01.F.01`) y el Consolidado de Control Interno (`RD.402.P.01.F.04`) de Rockdrill Group.

### 🏛️ Principios Clave Establecidos:
1. **Foco Estratégico Exclusivo en Horas y Metros**: El core del modelo de datos y las consultas se centra en las variables que mueven la rentabilidad: metros perforados ($HASTA - DESDE$) y distribución de las 12.0 hrs por guardia (efectivas, mantenimiento, standby operativo, inoperativo y cliente).
2. **Axioma Inviolable de Conciliación 1-a-1**: La cuadratura debe cumplirse para el **mismo día, misma máquina y mismo turno (`ID_CLAVE_UNICA = YYYYMMDD-MAQUINA-TURNO`)**. La coincidencia en sumas totales mensuales con diferencias diarias dispersas es calificada como rechazada.
3. **Cero Auto-Reparación**: Las discrepancias u omisiones reales de campo (ej. los 35m de Americana `XRD50USS-001`) se aíslan en el log de anomalías para su rectificación formal.
4. **Arquitectura en Dos Bloques Desacoplados ("Docker-Style")**:
   - **Bloque 1 (Python)**: Motor ultrarrápido con Calamine (Rust) para extracción, limpieza, conciliación y exportación de datos.
   - **Bloque 2 (Power Query M en Excel)**: Consultas y parámetros M nativos inyectados en el modelo de datos de Excel para actualización interactiva con 1 clic.

---

## 📁 2. Estructura de Directorios del Repositorio

```text
📁 Detallados/
   ├── 📁 Estructura base/
   │    └── 📁 Rockdrill_Control_Operaciones/
   │         ├── 📁 00_Control_Interno/   --> RD.402.P.01.F.04 Consolidado de Avance Setiembre.xlsx
   │         ├── 📁 Maestro_Maquinas/     --> Excepciones y mapeos SAP
   │         └── 📁 CTR_{NOMBRE_CTR}/     --> (18 Contratos Mineros)
   │              ├── 📁 01_Avance_Diario/
   │              └── 📁 02_Detallado/    --> RD.402.P.01.F.01 Reporte Detallado.xlsx
   ├── 📁 src/                           --> Código fuente Python y scripts de automatización
   │    ├── etl_detallados.py             --> Motor de extracción Calamine Rust (Skip 22, dual headers)
   │    ├── etl_control_interno.py        --> Extractor de Control Interno diario
   │    ├── reconciliacion.py             --> Motor de cruce 1-a-1 por ID_CLAVE_UNICA
   │    ├── auditor_sentido_comun.py      --> Agente Auditor de Sentido Común
   │    ├── pipeline.py                   --> Orquestador de producción
   │    └── crear_excel_powerquery_nativo.ps1 --> Inyector COM de Power Query M en Excel
   ├── 📁 power_query_m/                 --> Consultas Power Query M puras y parametrizadas (.txt)
   ├── 📁 output/                        --> Entregables oficiales generados (Excel, CSV, Star Schema)
   ├── 📁 docs/                          --> Documentación técnica canónica y contexto histórico
   ├── ejecutar_pipeline.py              --> Script principal de ejecución por terminal
   ├── config.py                         --> Archivo central de rutas y parámetros configurables
   └── PARAMETROS_EJECUCION_CASA.txt     --> Guía de parámetros para ejecución remota/casa
```

---

## 🧪 3. Banco de Pruebas Canónico (Benchmark Validado)

| Prueba de Verificación | Resultado de Auditoría | Estado |
| :--- | :--- | :---: |
| **AMERICANA / `XRD50U-002`** | 100.00% de coincidencia exacta turno a turno (26.08: 35.0m A + 15.5m B; 27.08: 30.4m A + 12.0m B) | ✅ **APROBADO (0.00m)** |
| **AMERICANA / `XRD50USS-001`**| Omisión real de -35.00m en 2026-08-27 Turno B detectada y aislada | ✅ **APROBADO (Detectado)** |
| **CATALINA HUANCA** | Extracción directa en Columna J (índice 9) | ✅ **APROBADO** |
| **Veredicto Auditor Sentido Común**| `APROBADO_CON_CUADRATURA_COMPROBADA` | ✅ **OFICIAL** |
