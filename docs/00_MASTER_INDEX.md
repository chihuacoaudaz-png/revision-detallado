# 📋 Índice Maestro de Documentación Técnica y Arquitectura
**Proyecto**: Sistema Unificado de Business Intelligence y Analítica de Perforación  
**Ubicación Principal**: `C:\Proyectos Python\Detallados\`  
**Organización**: Rockdrill Group  

---

## 🏛️ 1. Módulo de Arquitectura Actual y Estándar SIG 168 Columnas

1. [**`01_ARQUITECTURA_EMPRESARIAL_ERD_Y_SQL.md`**](file:///C:/Proyectos%20Python/Detallados/docs/01_ARQUITECTURA_EMPRESARIAL_ERD_Y_SQL.md)
   - Diagrama de Entidad-Relación (ERD) en Mermaid, modelado dimensional Kimball desde cero, llaves subrogadas enteras, tabla puente $M:M$ (`brg_cuadrilla_guardia`) y acoplamiento pasivo de costos/insumos.
2. [**`02_ESTANDAR_SIG_168_COLUMNAS_Y_TAXONOMIA.md`**](file:///C:/Proyectos%20Python/Detallados/docs/11_nuevo_estandar_sig_f01_168_columnas.md)
   - Los 17 bloques funcionales, taxonomía canónica de 5 categorías de disponibilidad y eliminación de la ambigüedad de "Otros".
3. [**`03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md`**](file:///C:/Proyectos%20Python/Detallados/docs/03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md)
   - Lógica económica de perforación diamantina (DDH: Metrajes vs Horas Cobrables), wireframes visuales para Jefe de Operaciones y Gerencia General, y catálogo de medidas DAX.
4. [**`04_PLAN_GOBERNANZA_WBS_Y_QUALITY_GATES.md`**](file:///C:/Proyectos%20Python/Detallados/docs/04_PLAN_GOBERNANZA_WBS_Y_QUALITY_GATES.md)
   - Marco de gobernanza con 5 Quality Gates obligatorias, WBS jerárquico y protocolo de auditoría de `project_governance_auditor`.
5. [**`GUIA_TECNICA_CONSTRUCCION_ENCABEZADOS_Y_PIPELINE_ETL.md`**](file:///C:/Proyectos%20Python/Detallados/docs/GUIA_TECNICA_CONSTRUCCION_ENCABEZADOS_Y_PIPELINE_ETL.md)
   - Guía técnica maestra para LLMs e Ingenieros de Datos: filtrado de hojas no operativas, motor dual-row de encabezados, filldown/fillup, turnos multi-sondaje y homologación SAP.
6. [**`GUIA_PASO_A_PASO_POWERQUERY_RECOPILADOR.md`**](file:///C:/Proyectos%20Python/Detallados/docs/GUIA_PASO_A_PASO_POWERQUERY_RECOPILADOR.md)
   - Guía paso a paso de implementación en Excel Power Query, prevención de Formula Firewall y catálogo de consultas M.
7. [**`07_RESUMEN_EJECUTIVO_Y_DECISIONES_ARQUITECTURA.md`**](file:///C:/Proyectos%20Python/Detallados/docs/07_RESUMEN_EJECUTIVO_Y_DECISIONES_ARQUITECTURA.md)
   - Resumen ejecutivo, axioma de conciliación 1-a-1 y mapa de entregables oficiales.

---

## 🏛️ 2. Módulo Legacy e Histórico (Preservado en `docs/00_LEGACY_HISTORICO/`)

Toda la documentación técnica del flujo de recopilación y limpieza anterior ha sido aislada en:  
👉 [**`C:\Proyectos Python\Detallados\docs\00_LEGACY_HISTORICO\`**](file:///C:/Proyectos%20Python/Detallados/docs/00_LEGACY_HISTORICO)

- `01_arquitectura_y_pipeline_etl.md` (Pipeline previo Calamine 135 columnas)
- `01_especificacion_tecnica_156_columnas.md` (Propuesta de transición 156 cols)
- `02_catalogo_68_actividades_y_tiempos.md` (Catálogo histórico de 68 actividades)
- `02_diccionario_de_datos_135_columnas.md` (Diccionario previo)
- `03_algoritmo_turnos_y_casos_borde.md` (Lógica de turnos anterior)
- `03_estrategia_powerbi_esquema_estrella.md` (Primer boceto estrella)
- `04_matriz_conciliacion_y_auditoria.md` (Conciliación histórica)
- `05_comparativa_legacy_135_vs_propuesta_156.md` (Análisis comparativo)
- `06_flujo_descarga_correos_outlook_y_ctrs.md` (Descargador de correos)
- `07_analisis_rendimiento_descargador.md` (Rendimiento)
- `08_guia_descargador_portable.md` (Descargador portable)
- `09_mapeo_actividades_y_estrategia_powerbi.md` (Mapeo previo)
- `10_propuesta_estandarizacion_detallado_f01.md` (Génesis de la propuesta)

---

## 📍 3. Mapa de Rutas de Todos los Outputs y Entregables

| Entregable / Componente | Ruta Relativa | Ruta Absoluta | Formato / Contenido |
| :--- | :--- | :--- | :--- |
| **Script DDL ANSI SQL** | `sql/01_schema_ddl_enterprise.sql` | [`C:\Proyectos Python\Detallados\sql\01_schema_ddl_enterprise.sql`](file:///C:/Proyectos%20Python/Detallados/sql/01_schema_ddl_enterprise.sql) | DDL SQL ejecutable para PostgreSQL, Snowflake, Microsoft Fabric y Azure SQL |
| **Diagrama ERD y Arquitectura** | `docs/01_ARQUITECTURA_EMPRESARIAL_ERD_Y_SQL.md` | [`C:\Proyectos Python\Detallados\docs\01_ARQUITECTURA_EMPRESARIAL_ERD_Y_SQL.md`](file:///C:/Proyectos%20Python/Detallados/docs/01_ARQUITECTURA_EMPRESARIAL_ERD_Y_SQL.md) | Diagrama ERD visual Kimball, diccionario de datos, granos atómicos y llaves subrogadas |
| **Especificación de Dashboards** | `docs/03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md` | [`C:\Proyectos Python\Detallados\docs\03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md`](file:///C:/Proyectos%20Python/Detallados/docs/03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md) | Wireframes, lógica económica de perforación (DDH) y catálogo de medidas DAX |
| **Gobernanza y Quality Gates** | `docs/04_PLAN_GOBERNANZA_WBS_Y_QUALITY_GATES.md` | [`C:\Proyectos Python\Detallados\docs\04_PLAN_GOBERNANZA_WBS_Y_QUALITY_GATES.md`](file:///C:/Proyectos%20Python/Detallados/docs/04_PLAN_GOBERNANZA_WBS_Y_QUALITY_GATES.md) | WBS en 5 fases y protocolo de auditoría de `project_governance_auditor` |
| **Documentación Legacy** | `docs/00_LEGACY_HISTORICO/` | [`C:\Proyectos Python\Detallados\docs\00_LEGACY_HISTORICO\`](file:///C:/Proyectos%20Python/Detallados/docs/00_LEGACY_HISTORICO) | 25 documentos del flujo histórico previo aislados |
| **Plantillas y Esquema SIG** | `NUEVO FORMATO DETALLADO/` | [`C:\Proyectos Python\Detallados\NUEVO FORMATO DETALLADO\`](file:///C:/Proyectos%20Python/Detallados/NUEVO%20FORMATO%20DETALLADO) | Plantilla Excel oficial `RD.402.P.01.F.01` y manuales de administradoras |
| **Base de Conocimientos Obsidian** | `MCP/docs/obsidian/` | [`C:\Proyectos Python\Detallados\MCP\docs\obsidian\`](file:///C:/Proyectos%20Python/Detallados/MCP/docs/obsidian) | Vault modular técnico en Markdown (Módulos 00 a 09 con wikilinks) |
