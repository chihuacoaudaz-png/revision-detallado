# Reporte Definitivo de Auditoría y Análisis de Discrepancias de Metrajes

## 1. Resumen Ejecutivo Comparativo por CTR

El presente análisis evalúa la totalidad de los metrajes perforados reportados en los **Reportes Detallados por Equipo** (`pipeline_limpieza.py`) frente a la planilla consolidada de **Control Interno** (`compilar_control_interno.py`), excluyendo explícitamente al contrato **COLQUIJIRCA** por no llevarse control de metrajes en este sistema.

| Contrato (CTR) | Metraje Detallados (m) | Metraje Control Interno (m) | Diferencia Total (m) | Diagnóstico Definitivo / Causa Raíz |
|---|---|---|---|---|
| **AMERICANA** | 2,511.20 | 2,511.20 | **0.00** | Coincidencia perfecta (100% OK) |
| **ANDAYCHAGUA** | 2,315.85 | 2,315.85 | **0.00** | Coincidencia perfecta (100% OK) |
| **CATALINA HUANCA** | 4,677.20 | 4,677.20 | **0.00** | Coincidencia perfecta (100% OK) |
| **CERRO** | 660.20 | 660.20 | **0.00** | Coincidencia perfecta (100% OK) |
| **CHUNGAR** | 2,347.55 | 2,347.55 | **0.00** | Coincidencia perfecta (100% OK) |
| **COBRIZA** | 4,376.70 | 4,376.70 | **0.00** | Coincidencia perfecta (100% OK) |
| **COLQUISIRI** | 1,165.60 | 1,165.60 | **0.00** | Coincidencia perfecta (100% OK) |
| **CONDESTABLE** | 2,800.40 | 2,800.40 | **0.00** | **Resuelto (0.00 m) al aplicar filtro de Hojas Visibles (`sheet.visible`)** |
| **CUCULI** | 804.10 | 804.10 | **0.00** | **Resuelto (0.00 m) al aplicar filtro de Hojas Visibles (`sheet.visible`)** |
| **INMACULADA** | 3,404.55 | 3,404.55 | **0.00** | Coincidencia perfecta (100% OK) |
| **LA ESTRELLA** | 1,228.70 | 1,228.70 | **0.00** | Coincidencia perfecta (100% OK) |
| **MOROCOCHA** | 1,842.80 | 1,842.80 | **0.00** | Coincidencia perfecta (100% OK) |
| **RAURA** | 2,793.51 | 2,793.51 | **0.00** | Coincidencia perfecta (100% OK) |
| **SAN CRISTOBAL** | 2,325.40 | 2,325.40 | **0.00** | Coincidencia perfecta (100% OK) |
| **TAMBOJASA** | 299.55 | 299.55 | **0.00** | Coincidencia perfecta (100% OK) |
| **TICLIO** | 484.15 | 484.15 | **0.00** | Coincidencia perfecta (100% OK) |
| **YAULIYACU** | 2,553.80 | 2,428.40 | **+125.40** | **Explicado**: Sondaje paralelo operativamente controlado pero no cobrado (columna `SONDAJE_PARALELO`) |
| **YAURICOCHA** | 188.75 | 188.75 | **0.00** | Coincidencia perfecta (100% OK) |
| **TOTAL GENERAL** | **36,780.01** | **36,654.61** | **+125.40** | **17 de 18 CTRs en Coincidencia Perfecta (0.00 m)** |

---

## 2. Explicación Técnica de Ingeniería de Datos y Manejo de Casos Borde

### A. Manejo de Sondajes Vacíos con Metraje (`ffill().bfill()` vs Power Query)

En los partes detallados originales existían casos donde las celdas de `SONDAJE` estaban vacías pero sí contenían metraje perforado:

1. **Caso MOROCOCHA (Filas Intermedias sin Sondaje)**:
   - En hojas como `XRD150USS` y `XRD80USS-011`, en los turnos Noche (B) los operadores no repetían el nombre del pozo.
   - **Resolución**: El algoritmo aplica `ffill()` (Fill Down / Rellenar hacia abajo), por lo que las filas intermedias heredan el sondaje activo de la fila superior dentro de la misma hoja.

2. **Caso CHUNGAR (LM110U-001, Fila 46 - 06 de Julio Turno B)**:
   - **Situación**: El 06-jul Turno B registró `DESDE = 0.00m`, `HASTA = 1.50m`, `METRAJE = 1.50m`, pero la celda `SONDAJE` estaba en blanco. El nombre del sondaje (`DDHUCH26001`) recién se escribió en la fila del 07-jul Turno A.
   - **Por qué fallaba en Power Query**: La función estándar `Table.FillDown` de Power Query M busca valores hacia arriba. Como las filas anteriores del 26-jun al 06-jul Turno A eran días sin operación con sondaje en blanco, `FillDown` dejaba `null` en el 06-jul Turno B, obligando a revisar a mano el Excel.
   - **Solución Automatizada en el Pipeline**: El pipeline ejecuta la secuencia combinada `.ffill().bfill()` (Rellenar hacia abajo + Rellenar hacia arriba) sobre la columna `SONDAJE`. De esta manera, el 06-jul Turno B absorbe automáticamente `DDHUCH26001` de la fila del 07-jul, logrando asignación 100% automatizada sin celdas `null` ni registros huérfanos.

### B. Filtro de Hojas Visibles (`sheet.visible` / `Hidden = false`)
- **Causa Raíz:** Los archivos Excel de los CTRs contenían pestañas **ocultas** (`hidden` o `veryHidden`) con borradores de máquinas o pestañas inactivas de meses anteriores (p. ej. `LM75U-011` en Condestable; `XRD100ST-001 (2)` en Cuculí).
- **Solución Replicada de Power Query M:** Al incorporar el filtro para omitir hojas ocultas (`sheet.visible`), los metrajes de **CONDESTABLE** y **CUCULI** pasaron a coincidir al **100.00% (0.00 m de error)** con Control Interno.

### C. Artefactos de Precisión de Coma Flotante IEEE 754 (`1e-12` en Excel)
- Se aplica redondeo explícito `.round(2)` en todas las métricas numéricas (`METRAJE`, `DESDE`, `HASTA`, `PROFUNDIDAD DE SONDAJE`), eliminando el ruido numérico a nivel de 12 decimales.

---

## 3. Discrepancia YAULIYACU (+125.40 m) y Campo `SONDAJE_PARALELO`

- **Diagnóstico Operativo de Negocio**:
  - En Yauliyacu, la máquina `XRD125USS-001` registra **247.20 m (Detallado)** vs **121.80 m (Control Interno)** (Diferencia de **+125.40 m** entre los días 17 y 25 de julio).
  - Esta diferencia corresponde a la perforación de un **sondaje paralelo / secundario** que se ejecutó de forma simultánea.
  - El equipo registraba este metraje en el parte detallado diario para control de avance físico y consumo de aditivos del equipo, pero **no se sumaba en la planilla de Control Interno porque era un sondaje que NO SE COBRABA al cliente**.

- **Implementación del Campo `SONDAJE_PARALELO`**:
  - Se agregó la columna `SONDAJE_PARALELO` al final del archivo consolidado con el valor por defecto `1` (booleano/entero) para todas las filas.
  - En la capa posterior (Power Query / Power BI), se puede cambiar `SONDAJE_PARALELO = 0` para los pozos paralelos no facturables de Yauliyacu, permitiendo conciliar al 100.00% el metraje facturable.

---

## 4. Estructura y Orden Oficial de Columnas (135 Columnas)

1. **Matriz Oficial (Columnas 1 a 129)**: Mantiene la estructura exacta original de la planilla, conservando `TURNO (A=1;B=2)` en su posición nativa.
2. **Campos de Metadatos y Calculados (Al Final del Dataset)**:
   - `HOJA DE TRABAJO ORIGEN`: Nombre de la pestaña del Excel.
   - `ARCHIVO ORIGEN`: Nombre del archivo Excel.
   - `TURNO_ESTANDAR`: Turno normalizado ('A' o 'B').
   - `ID_CLAVE_UNICA`: Clave de trazabilidad `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}`.
   - `SONDAJE_PARALELO`: Indicador de sondaje paralelo (default `1`).
   - `Alerta_Comentarios`: Auditoría de observaciones ('OK' o 'FALTA COMENTARIO').

---

## 5. Conclusión de Calidad del Dato
- 17 de los 18 CTRs cuadran en **Coincidencia Exacta de 0.00 m**.
- YAULIYACU está 100% justificado por la regla de negocio de sondajes paralelos no facturables.
- El 100% de los registros de metraje cuentan con asignación válida de `SONDAJE` mediante la regla `.ffill().bfill()`.
