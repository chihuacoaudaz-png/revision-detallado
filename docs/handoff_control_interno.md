# Documento de Handoff y Estado del Proyecto - ETL y Compilación de Control Interno

## 1. Contexto y En Qué Se Está Trabajando
Esta vertiente del proyecto abarca el desarrollo de la herramienta de compilación y auditoría de **Control Interno** (`RD.402.P.01.F.04 Consolidado de Avance Julio.xlsx`). 

El archivo de Control Interno es un libro maestro utilizado por la administración central para consolidar los metrajes reportados diariamente. Contiene 30 pestañas asociadas a cada día del mes operacional (`26.06` a `25.07`). El objetivo fue construir un procedimiento automatizado en Power Query M y Python que extraiga y unifique esta información en una estructura estándar de turnos (`A`/`B`) y la cruce mediante una `ID_CLAVE_UNICA` contra los **Reportes Detallados por Equipo**, aislando las diferencias exactas de metraje.

---

## 2. Lo Que Está Hecho y Funcionalidades Validadas

1. **Extracción Dual en Power Query M (`Consolidado_BD`)**:
   - Soporta formato de hoja plana (`BASE DE DATOS`, `BD`, `00_CONTROL_INTERNO`) y formato multi-hoja diario (`26.06` a `25.07`).
   - Selección estricta de las **9 columnas oficiales**: `FECHA`, `CTR`, `APLICACION`, `MAQUINA_RAW`, `MAQUINA`, `SE_PERFORO`, `TURNO_ESTANDAR`, `METRAJE_CI`, `ID_CLAVE_UNICA`.
   - Asignación de Turno basada en `DIAS_TRABAJADOS` (`1` = `"A"`, `null` = `"B"`).
2. **Matriz de Discrepancias (`Discrepancias_BD`)**:
   - Cruce `Full Outer Join` por `ID_CLAVE_UNICA` entre `Detallados_BD` y `Consolidado_BD`.
   - Ordenamiento multinivel corregido: `{{"FECHA", Order.Ascending}, {"CTR", Order.Ascending}, {"MAQUINA", Order.Ascending}}`.
   - **Coincidencia Exacta**: Exactamente **935/935 discrepancias diarias de guardia** validadas 1-a-1 contra `bbdd.xlsx`.

---

## 3. Estado del Modelo M en GitHub

- **`codigo_m/codigo_m_control_interno.txt`** ➔ Código oficial de Control Interno en M.
- **`codigo_m/codigo_m_control_interno_backup.txt`** ➔ Copia de respaldo de seguridad.
- **`codigo_m/codigo_m_matriz_discrepancias.txt`** ➔ Código de la matriz de discrepancias en M.
