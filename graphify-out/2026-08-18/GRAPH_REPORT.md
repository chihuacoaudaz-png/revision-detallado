# Graph Report - detallados  (2026-08-18)

## Corpus Check
- 55 files · ~749,076 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 554 nodes · 602 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- __init__.py
- 3. Catálogo Detallado de Columnas
- descargar_detallados.py
- 🚀 08. Guía de Uso del Descargador Portable de Detallados
- ⚡ 07. Análisis de Rendimiento del Descargador Automatizado
- 📚 Master Knowledge Base & Handoff: Pipeline ETL de Detallados y Control Interno (Rockdrill)
- 🔍 Diagnóstico Técnico y Puntos a Corregir Mañana
- 📧 06. Flujo de Descarga de Correos OWA, Reglas por CTR y Reportes Detallados (Rockdrill)
- 3. Casos Borde Críticos Resueltos
- 🚀 05. Guía de Ejecución, Automatización y Mantenimiento
- 🛠️ Rockdrill Group - Pipeline ETL de Detallados y Control Interno
- 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M
- 2. Pseudocódigo Detallado del Algoritmo (Paso a Paso)
- 📜 Historial Completo de Preguntas, Requerimientos y Respuestas
- 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M
- Manual Técnico Extremadamente Detallado para la Replicación del ETL de Control Interno y Matriz Comparativa
- Documento de Handoff y Estado del Proyecto - ETL de Reportes Detallados por Equipo
- 🏛️ Resumen Completo de Conversación, Arquitectura y Estado del Proyecto
- Documento de Handoff y Estado del Proyecto - ETL y Compilación de Control Interno
- matriz_comparativa_metrajes_9b70af81.md
- 🗺️ Guía y Ubicación de Archivos del Proyecto - Rockdrill
- rules/graphify.md
- workflows/graphify.md
- control_interno_compilado_6a61bd72.md
- detallados_consolidados_89de2410.md
- _MAPEO_DESCARGAS_17_08_2026_a4dc9450.md
- _TIEMPOS_17_08_2026_ff251905.md
- 1. Cluster de Rendimiento y ROP (Rate of Penetration)
- HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md
- 3. Cluster de Metas y Cumplimiento de Programa
- 4. Desglose Estructural Hoja por Hoja del Dashboard
- 6. Cluster de Costos y Control Presupuestal
- 4. Cluster de Control de Tiempos y Horas Operativas
- 2. Cluster de Metraje y Avance Físico
- 📊 Resumen de Tablas del Modelo
- 🏗️ Arquitectura de Datos y Pipeline ETL
- 5. Cluster de Metraje Perdido y Disponibilidad Global
- 2. Implementación de Fórmulas DAX
- 🛠️ Guía Maestra de Reconstrucción Total desde Cero
- MCP/procesarv2.py
- etl/procesarv2.py
- 📊 BI Control de Operaciones y Residentes - Rock Drill

## God Nodes (most connected - your core abstractions)
1. `3. Cluster de Metas y Cumplimiento de Programa` - 26 edges
2. `6. Cluster de Costos y Control Presupuestal` - 23 edges
3. `4. Cluster de Control de Tiempos y Horas Operativas` - 22 edges
4. `2. Cluster de Metraje y Avance Físico` - 18 edges
5. `1. Cluster de Rendimiento y ROP (Rate of Penetration)` - 16 edges
6. `📊 Resumen de Tablas del Modelo` - 14 edges
7. `7. Cluster de Brocas y Consumo de Insumos` - 13 edges
8. `4. Desglose Estructural Hoja por Hoja del Dashboard` - 13 edges
9. `run_etl_detallados()` - 12 edges
10. `run_full_pipeline()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `run_full_pipeline()`  [EXTRACTED]
  ejecutar_pipeline.py → src/pipeline.py
- `run_etl_control_interno()` --calls--> `clean_number_value()`  [EXTRACTED]
  src/etl_control_interno.py → src/utils.py
- `run_etl_control_interno()` --calls--> `load_machine_exceptions()`  [EXTRACTED]
  src/etl_control_interno.py → src/utils.py
- `run_etl_control_interno()` --calls--> `normalize_ctr()`  [EXTRACTED]
  src/etl_control_interno.py → src/utils.py
- `run_full_pipeline()` --calls--> `run_etl_control_interno()`  [EXTRACTED]
  src/pipeline.py → src/etl_control_interno.py

## Import Cycles
- None detected.

## Communities (42 total, 6 thin omitted)

### Community 0 - "__init__.py"
Cohesion: 0.07
Nodes (44): main(), ===============================================================================…, DataFrame, Path, ETL de Compilación de Control Interno (RD.402.P.01.F.04)…, Extrae y compila las pestañas diarias del libro maestro de Control Interno., run_etl_control_interno(), assign_daily_turnos_fast() (+36 more)

### Community 2 - "3. Catálogo Detallado de Columnas"
Cohesion: 0.14
Nodes (13): 📊 02. Diccionario de Datos y Tipado Estricto (135 Columnas Oficiales), 1. Estructura Global y Orden Canónico, 2. Clasificación de Tipos de Datos (Data Types Schema), 3. Catálogo Detallado de Columnas, A. Bloque Operacional y de Identificación (Cols 1 - 10), B. Bloque de Perforación y Metrajes (Cols 11 - 23), C. Bloque de Brocas y Escariadores (Cols 24 - 30), D. Bloque de Consumibles, Aditivos y Combustible (Cols 31 - 54) (+5 more)

### Community 3 - "descargar_detallados.py"
Cohesion: 0.13
Nodes (25): Path, ===============================================================================…, Resuelve la carpeta 'Rockdrill_Control_Operaciones' según el modo configurado., Busca dinámicamente el libro maestro de Control Interno dentro de…, resolve_base_data_path(), resolve_control_interno_path(), build_ctrs_config(), buscar_en_owa() (+17 more)

### Community 4 - "🚀 08. Guía de Uso del Descargador Portable de Detallados"
Cohesion: 0.10
Nodes (19): 🚀 08. Guía de Uso del Descargador Portable de Detallados, 🎯 1. ¿Qué es?, 📋 2. Requisitos Previos, ⚙️ 3. Configuración Inicial (Primera vez), 🔧 4. Uso Diario, 📅 5. Regla de Fecha, 🔒 6. Seguridad: Solo Fecha Exacta, 📂 7. Estructura de Archivos Generados (+11 more)

### Community 5 - "⚡ 07. Análisis de Rendimiento del Descargador Automatizado"
Cohesion: 0.12
Nodes (16): ⚡ 07. Análisis de Rendimiento del Descargador Automatizado, 🎯 1. Contexto y Problema, 🔍 2. Perfil de Tiempos por Operación (v1.0 Original), 3.1 Sleeps Fijos Innecesarios, 3.2 Fallback Queries Exhaustivas, 3.3 Locator Broad para Adjuntos, 3.4 Sin Instrumentación, 🐌 3. Cuellos de Botella Identificados (+8 more)

### Community 6 - "📚 Master Knowledge Base & Handoff: Pipeline ETL de Detallados y Control Interno (Rockdrill)"
Cohesion: 0.11
Nodes (19): 🎯 1. Resumen Ejecutivo y Objetivo del Proyecto, 🏗️ 2. ¿Por Qué Python (Pandas + Calamine) vs. Power Query (M)?, 🧩 3. Arquitectura del Flujo ETL, 🔑 4. Estructura Canónica de 135 Columnas y Clave Primaria, ⚙️ 5. El Algoritmo Inteligente de Turnos (`assign_daily_turnos_grid_smart`), 📊 6. Resultados de Conciliación y Matriz de Discrepancias, 📋 8.1. Reglas Operativas y de Negocio Extraídas del BI:, ⚠️ 8.2. Observaciones Críticas del Modelo Heredado: (+11 more)

### Community 7 - "🔍 Diagnóstico Técnico y Puntos a Corregir Mañana"
Cohesion: 0.14
Nodes (13): 🔍 Diagnóstico Técnico y Puntos a Corregir Mañana, ✅ ESTADO DE RESOLUCIÓN COMPLETA, 📋 Plan de Acción Inmediato para Mañana, ⚠️ Punto 1: Falta de Filtro por Ventana de Fechas de Control Interno (Truncamiento), ⚠️ Punto 2: Descarga de los 3 CTRs Faltantes (AMERICANA, ANDAYCHAGUA, INMACULADA), ⚠️ Punto 3: Pequeñas Variaciones en RAURA (-7.33 m) y TAMBOJASA (+2.95 m), ¿Qué ocurrió?, ¿Qué ocurrió? (+5 more)

### Community 8 - "📧 06. Flujo de Descarga de Correos OWA, Reglas por CTR y Reportes Detallados (Rockdrill)"
Cohesion: 0.15
Nodes (12): 📧 06. Flujo de Descarga de Correos OWA, Reglas por CTR y Reportes Detallados (Rockdrill), 🗓️ 17/08/2026 (Perforación del 16/08/2026), 🔐 1. Autenticación Delegada Local (Edge Persistent Context):, 🎯 1. Principio Operacional y Flujo de Envío Diario, 🌐 2. Compatibilidad de Idioma (ES/EN):, 📑 2. Tipología de Reportes Operacionales, 🔍 3. Algoritmo de Búsqueda y Selección Estricta:, 🏢 3. Catálogo de los 18 Contratos Mineros (CTRs) y Particularidades (+4 more)

### Community 9 - "3. Casos Borde Críticos Resueltos"
Cohesion: 0.18
Nodes (10): 🧠 03. Algoritmo Inteligente de Turnos y Casos Borde Resueltos, 🛠️ 1. Catalina Huanca (`XRD125UFDR-001`, 29.06), 1. El Reto Operacional de los Turnos Mineros, 🛠️ 2. Condestable (`XRD80ITH-001`, 01.07 y 05.07), 2. Implementación Canónica: `assign_daily_turnos_grid_smart`, 3. Casos Borde Críticos Resueltos, 🛠️ 3. Morococha (`XRD80USS-011`) - Filas Intermedias sin Sondaje, 🛠️ 4. Chungar (`LM110U-001`, 06 de Julio Turno B) (+2 more)

### Community 10 - "🚀 05. Guía de Ejecución, Automatización y Mantenimiento"
Cohesion: 0.17
Nodes (11): 🚀 05. Guía de Ejecución, Automatización y Mantenimiento, 🧭 1. Flujo Operativo Punta a Punta, 📦 2. Requisitos y Entorno de Ejecución, ⚡ 3. Guía de Ejecución Diaria, 📁 4. Estructura Limpia del Proyecto (Lista para OneDrive), 🔒 5. Variables de Configuración en `ejecutar_pipeline_completo.py`, 🔗 Notas Relacionadas, Paso 1: Configuración Inicial de Sesión (Solo la 1ra vez por usuario) (+3 more)

### Community 11 - "🛠️ Rockdrill Group - Pipeline ETL de Detallados y Control Interno"
Cohesion: 0.18
Nodes (10): 1️⃣ Paso 1: Configuración Inicial (Solo la primera vez), 2️⃣ Paso 2: Descargar los Reportes del Día, 3️⃣ Paso 3: Ejecutar el Procesamiento y Conciliación, ⚙️ ¿Cómo cambiar parámetros y rutas? (`config.py`), 🚀 ¿Cómo usar el sistema en 3 simples pasos?, 📚 Documentación Técnica Detallada, 📁 Estructura del Proyecto, 🛠️ Instalación para Desarrolladores (+2 more)

### Community 12 - "1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M"
Cohesion: 0.20
Nodes (9): 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M, 2. Especificación de Campos y Tipos de Datos para Power Query (Control Interno), 3. Consideraciones Críticas para Flujos de Power Query (Control Interno), Especificación Técnica de Lógica ETL, Traducción Power Query M y Diccionario de Campos - Control Interno, Paso 1: Selección de Hojas Diarias (`26.06` a `25.07`), Paso 2: Lectura Adaptativa desde Fila 10 hasta 'TOTAL AVANCE', Paso 3: Propagación de CTR (Columna A Filldown) y Estandarización, Paso 4: Estandarización de Turno A/B por Secuencia de Máquina (+1 more)

### Community 13 - "2. Pseudocódigo Detallado del Algoritmo (Paso a Paso)"
Cohesion: 0.20
Nodes (9): 1. Diagrama de Flujo del Proceso, 2. Pseudocódigo Detallado del Algoritmo (Paso a Paso), 3. Matriz de Mapeo de Máquinas Excepcionales (SAP Master), 4. Validaciones Post-Procesamiento (Criterios de Calidad), Manual Técnico Extremadamente Detallado para la Replicación del ETL de Reportes Detallados, Paso 2.1. Escaneo de Archivos e Inspección de Estructura, Paso 2.2. Algoritmo de Extracción Dual-Row de Encabezados, Paso 2.3. Algoritmo de Limpieza Numérica Profunda (`clean_number_value`) (+1 more)

### Community 14 - "📜 Historial Completo de Preguntas, Requerimientos y Respuestas"
Cohesion: 0.18
Nodes (10): 10. Implementación de Directivas de Negocio (`repuesta.txt`) y Esquema Estrella Power BI, 1. Sesión Inicial y Diagnóstico del Descargador, 2. Flujo de Limpieza Previa y Fecha Objetivo, 3. Revisión de Eficiencia, Documentación Obsidian y Graphify, 4. Control de Fallos en Descarga (Caso Andaychagua) y No-Hardcoding, 5. Reordenamiento y Limpieza Estructural del Proyecto, 6. Prueba con Consolidado de Avance de Agosto (Fecha 16/08), 8. Corrección de Casos Específicos (Condestable, Inmaculada, Americana y Andaychagua) (+2 more)

### Community 15 - "1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M"
Cohesion: 0.22
Nodes (8): 1. Mapeo de Pasos ETL: Lógica Agnóstica vs Traducción Power Query M, 2. Validación Cuantitativa y Coincidencia en BBDD, Especificación Técnica de Lógica ETL, Traducción Power Query M y Diccionario de Campos - Reportes Detallados y Control Interno, Paso 1: Filtro de Archivos y Exclusión de CTRs (Excluido COLQUIJIRCA), Paso 2: Lectura de Hojas Operativas y Omisión de Encabezados (Skip 22 en Detallados), Paso 3: Propagación de FECHA y SONDAJE (`FillDown` + `FillUp`) y Filtrado de Filas Operativas Reales, Paso 4: Extracción de Control Interno (Motor Dual Multi-Hoja Diario y Plano), Paso 5: Cruce y Matriz de Discrepancias (`Discrepancias_BD`)

### Community 16 - "Manual Técnico Extremadamente Detallado para la Replicación del ETL de Control Interno y Matriz Comparativa"
Cohesion: 0.25
Nodes (7): 1. Diagrama de Flujo del Proceso, 2. Pseudocódigo Detallado del Algoritmo, 3. Guía de Interpretación del Reporte de Auditoría y Conciliación, 4. Validaciones Post-Procesamiento (Control Interno), Manual Técnico Extremadamente Detallado para la Replicación del ETL de Control Interno y Matriz Comparativa, Paso 2.1. Algoritmo de Compilación de Hojas Diarias, Paso 2.2. Algoritmo de Cruce y Matriz Comparativa por Clave Única

### Community 17 - "Documento de Handoff y Estado del Proyecto - ETL de Reportes Detallados por Equipo"
Cohesion: 0.33
Nodes (5): 1. Contexto y En Qué Se Está Trabajando, 2. Lo Que Está Hecho y Funcionalidades Validadas, 3. Estado de Conciliación en BBDD, 4. Archivos Entregados en GitHub, Documento de Handoff y Estado del Proyecto - ETL de Reportes Detallados por Equipo

### Community 18 - "🏛️ Resumen Completo de Conversación, Arquitectura y Estado del Proyecto"
Cohesion: 0.29
Nodes (6): 📁 1. Estructura de Directorios Actual, ⚙️ 2. Variables de Inicialización y Configuración (`config.py`), 🚀 3. Comandos de Ejecución, 📊 4. Métricas de Rendimiento y Resultados de Conciliación al 16/08/2026, 🏛️ Resumen Completo de Conversación, Arquitectura y Estado del Proyecto, Tabla de Conciliación por Contrato Minero (CTR):

### Community 19 - "Documento de Handoff y Estado del Proyecto - ETL y Compilación de Control Interno"
Cohesion: 0.40
Nodes (4): 1. Contexto y En Qué Se Está Trabajando, 2. Lo Que Está Hecho y Funcionalidades Validadas, 3. Estado del Modelo M en GitHub, Documento de Handoff y Estado del Proyecto - ETL y Compilación de Control Interno

### Community 20 - "matriz_comparativa_metrajes_9b70af81.md"
Cohesion: 0.50
Nodes (3): Sheet: AUDITORIA COMPLETA, Sheet: DISCREPANCIAS, Sheet: RESUMEN POR CTR

### Community 21 - "🗺️ Guía y Ubicación de Archivos del Proyecto - Rockdrill"
Cohesion: 0.50
Nodes (3): 📌 Archivos Principales en la Raíz, 📂 Carpetas del Repositorio, 🗺️ Guía y Ubicación de Archivos del Proyecto - Rockdrill

### Community 28 - "1. Cluster de Rendimiento y ROP (Rate of Penetration)"
Cohesion: 0.06
Nodes (31): 1. Cluster de Rendimiento y ROP (Rate of Penetration), 7. Cluster de Brocas y Consumo de Insumos, 📐 Catálogo Exhaustivo de Medidas DAX, 🔹 `[Consumo Consolidado].[Cantidad Brocas consumidas]`, 🔹 `[Medidas].[Abastecimiento Cantidad]`, 🔹 `[Medidas].[Cantidad Brocas]`, 🔹 `[Medidas].[Cantidad Brocas (Con Metraje)]`, 🔹 `[Medidas].[Cantidad Brocas CONSUMO]` (+23 more)

### Community 29 - "HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md"
Cohesion: 0.07
Nodes (25): 🏗️ 01. Arquitectura del Pipeline ETL y Sustitución de Power Query, 1. Justificación de la Migración Técnica, 2. Diagrama de Flujo Modular del Pipeline, 3. Componentes y Módulos de Código, 🔗 Notas Relacionadas, ⚖️ 04. Matriz Comparativa, Conciliación Diaria y Diagnósticos Operacionales, 1. Metodología de Conciliación, 2. Resumen Acumulado por Contrato Minero (18 CTRs) (+17 more)

### Community 30 - "3. Cluster de Metas y Cumplimiento de Programa"
Cohesion: 0.08
Nodes (26): 3. Cluster de Metas y Cumplimiento de Programa, 🔹 `[Medidas].[Desviación %]`, 🔹 `[Medidas].[Desviación al fin de mes %]`, 🔹 `[Medidas].[Desviación % dinamica]`, 🔹 `[Medidas].[Desviación Proyectado %]`, 🔹 `[Medidas].[Meta Acumulada]`, 🔹 `[Medidas].[Meta Acumulada Periodo]`, 🔹 `[Medidas].[Meta al Día]` (+18 more)

### Community 31 - "4. Desglose Estructural Hoja por Hoja del Dashboard"
Cohesion: 0.08
Nodes (24): 🏷️ 1. Nombres de Tablas, 1. Resumen de Arquitectura y Conexión de Datos, 2. Flujo de Datos y ETL (Script de Python: `procesarv2.py`), 🗂️ 2. Nombres de Columnas, 📊 3. Nombres de Medidas DAX, 3. Protocolo de Estandarización de Datos (Buenas Prácticas Google Data Analytics), 4. Desglose Estructural Hoja por Hoja del Dashboard, 5. Recomendaciones de Mejores Prácticas para el Rediseño (+16 more)

### Community 32 - "6. Cluster de Costos y Control Presupuestal"
Cohesion: 0.09
Nodes (23): 6. Cluster de Costos y Control Presupuestal, 🔹 `[Consumo Consolidado].[Presupuesto PDD]`, 🔹 `[Medidas].[Abastecimiento Cantidad]`, 🔹 `[Medidas].[Costo Abastecimiento ($)]`, 🔹 `[Medidas].[Costo Abastecimiento MTD Operativo ($)]`, 🔹 `[Medidas].[Costo Abastecimiento x Metro ($/m)]`, 🔹 `[Medidas].[Costo Cantidad]`, 🔹 `[Medidas].[Costo Consumo  ($)]` (+15 more)

### Community 33 - "4. Cluster de Control de Tiempos y Horas Operativas"
Cohesion: 0.09
Nodes (22): 4. Cluster de Control de Tiempos y Horas Operativas, 🔹 `[Disponibilidad global].[Dias Sin Perforar]`, 🔹 `[Disponibilidad global].[Metros_por_guardia_ideales]`, 🔹 `[Disponibilidad global].[Turnos Sin Perforar]`, 🔹 `[Disponibilidad global].[VAR Horas_disminuyen_dg]`, 🔹 `[Medidas].[Dias Mes Operativo]`, 🔹 `[Medidas].[Dias Operativos Restantes]`, 🔹 `[Medidas].[Dias Operativos Transcurridos]` (+14 more)

### Community 34 - "2. Cluster de Metraje y Avance Físico"
Cohesion: 0.11
Nodes (18): 2. Cluster de Metraje y Avance Físico, 🔹 `[Disponibilidad global].[Metros DG]`, 🔹 `[Disponibilidad global].[Metros NO PERFORADOS]`, 🔹 `[Disponibilidad global].[Metros_por_guardia_ideales]`, 🔹 `[Medidas].[% Avance Gantt]`, 🔹 `[Medidas].[Cantidad Brocas (Con Metraje)]`, 🔹 `[Medidas].[Cantidad Consumo x Metro ($/m)]`, 🔹 `[Medidas].[Ejecutado Acumulado]` (+10 more)

### Community 35 - "📊 Resumen de Tablas del Modelo"
Cohesion: 0.12
Nodes (15): 📖 Diccionario de Datos del Modelo Tabular, 📊 Resumen de Tablas del Modelo, 🗃️ Tabla: `Consumo Consolidado`, 🗃️ Tabla: `Dim_Calendario`, 🗃️ Tabla: `Dim_CTR`, 🗃️ Tabla: `Dim_Familias`, 🗃️ Tabla: `Dim_Maquina`, 🗃️ Tabla: `Dim_Personal` (+7 more)

### Community 36 - "🏗️ Arquitectura de Datos y Pipeline ETL"
Cohesion: 0.17
Nodes (11): 1. Diagrama de Flujo de Datos (Data Lineage), 2. Configuración de Rutas del Entorno, 3. Lógica de Transformación en Python (`procesarv2.py`), 4. Frecuencia y Procedimiento de Actualización, A. Normalización de Nombres y Llaves, 📊 Archivo Power BI, 🏗️ Arquitectura de Datos y Pipeline ETL, B. Generación de Llave Primaria Operativa (`KEY_OPERACION`) (+3 more)

### Community 37 - "5. Cluster de Metraje Perdido y Disponibilidad Global"
Cohesion: 0.18
Nodes (11): 5. Cluster de Metraje Perdido y Disponibilidad Global, 🔹 `[Disponibilidad global].[Dias Sin Perforar]`, 🔹 `[Disponibilidad global].[Metros DG]`, 🔹 `[Disponibilidad global].[Metros Perdidos DG]`, 🔹 `[Disponibilidad global].[Turnos Sin Perforar]`, 🔹 `[Disponibilidad global].[Valor no ganado]`, 🔹 `[Disponibilidad global].[Valor Perdido]`, 🔹 `[Disponibilidad global].[VAR Horas_disminuyen_dg]` (+3 more)

### Community 38 - "2. Implementación de Fórmulas DAX"
Cohesion: 0.18
Nodes (11): 1. Fundamento Matemático, 1️⃣ `[Medidas].[ROP_Efectivo]`, 2. Implementación de Fórmulas DAX, 2️⃣ `[Medidas].[f_efectivo]`, 3. Matriz Visual en Power BI, 3️⃣ `[Medidas].[m_perdido_ajustado]` *(Con Corrección de Totales para Múltiples CTRs)*, A. $\text{ROP}_{\text{Efectivo}}$ (Velocidad Neta de Penetración en Roca), B. $f_{\text{efectivo}}$ (Factor de Corrección por Eficiencia de Guardia) (+3 more)

### Community 39 - "🛠️ Guía Maestra de Reconstrucción Total desde Cero"
Cohesion: 0.22
Nodes (9): Fase 1: Pipeline ETL y Generación de Datos, Fase 2: Configuración en Power BI Desktop, Fase 3: Creación de Relaciones del Modelo, Fase 4: Creación de la Tabla de Medidas, Fase 5: Estructura de Páginas Visuales, 🛠️ Guía Maestra de Reconstrucción Total desde Cero, 📄 Página 1: Principal / Dashboard Ejecutivo, 📄 Página 2: Desglose de Horas y Pérdida de Metraje (+1 more)

### Community 40 - "MCP/procesarv2.py"
Cohesion: 0.39
Nodes (7): limpiar_key(), normalizar_cols_excel(), normalizar_nombre(), procesar_data(), Normaliza nombres: mayúsculas, sin acentos, sin puntos, espacios limpios, Estandariza texto para evitar duplicados en actividades o llaves, Normaliza nombres de columnas del Excel

### Community 41 - "etl/procesarv2.py"
Cohesion: 0.39
Nodes (7): limpiar_key(), normalizar_cols_excel(), normalizar_nombre(), procesar_data(), Normaliza nombres: mayúsculas, sin acentos, sin puntos, espacios limpios, Estandariza texto para evitar duplicados en actividades o llaves, Normaliza nombres de columnas del Excel

### Community 42 - "📊 BI Control de Operaciones y Residentes - Rock Drill"
Cohesion: 0.50
Nodes (3): 📊 BI Control de Operaciones y Residentes - Rock Drill, 🗂️ Estructura del Repositorio (Buenas Prácticas), 🚀 Inicio Rápido

## Knowledge Gaps
- **343 isolated node(s):** `graphify`, `Workflow: graphify`, `📌 Archivos Principales en la Raíz`, `📂 Carpetas del Repositorio`, `🧭 Índice del Knowledge Graph` (+338 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `📐 Catálogo Exhaustivo de Medidas DAX` connect `1. Cluster de Rendimiento y ROP (Rate of Penetration)` to `6. Cluster de Costos y Control Presupuestal`, `4. Cluster de Control de Tiempos y Horas Operativas`, `2. Cluster de Metraje y Avance Físico`, `5. Cluster de Metraje Perdido y Disponibilidad Global`, `HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md`, `3. Cluster de Metas y Cumplimiento de Programa`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `3. Cluster de Metas y Cumplimiento de Programa` connect `3. Cluster de Metas y Cumplimiento de Programa` to `1. Cluster de Rendimiento y ROP (Rate of Penetration)`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `6. Cluster de Costos y Control Presupuestal` connect `6. Cluster de Costos y Control Presupuestal` to `1. Cluster de Rendimiento y ROP (Rate of Penetration)`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **What connects `graphify`, `Workflow: graphify`, `📌 Archivos Principales en la Raíz` to the rest of the system?**
  _343 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07013574660633484 - nodes in this community are weakly interconnected._
- **Should `3. Catálogo Detallado de Columnas` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `descargar_detallados.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12535612535612536 - nodes in this community are weakly interconnected._