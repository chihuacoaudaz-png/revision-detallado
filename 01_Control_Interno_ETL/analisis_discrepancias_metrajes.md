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
| **YAULIYACU** | 2,553.80 | 2,428.40 | **+125.40** | Registros de máquina `XRD125USS-001` (17 al 25 de julio) omitidos en CI |
| **YAURICOCHA** | 188.75 | 188.75 | **0.00** | Coincidencia perfecta (100% OK) |
| **TOTAL GENERAL** | **36,780.01** | **36,654.61** | **+125.40** | **17 de 18 CTRs en Coincidencia Perfecta (0.00 m)** |

---

## 2. Explicación Técnica de Ingeniería de Datos

### A. Filtro de Hojas Visibles (`sheet.visible` / `Hidden = false`)
- **Causa Raíz:** En versiones previas del pipeline, el filtrado de hojas se realizaba comparando únicamente el nombre del tab contra la lista `HOJAS_EXCLUIDAS = {"ADITIVOS", "GENERAL", "LISTAS", "Tiempos"}`.
- **Observación de Ingeniería:** Los archivos Excel de los CTRs contenían pestañas **ocultas** (`hidden` o `veryHidden`) con borradores de máquinas o pestañas inactivas de meses anteriores (p. ej. `LM75U-011`, `XRD40U-006` en Condestable; `XRD100ST-001 (2)` en Cuculí).
- **Solución Replicada de Power Query M:** En Power Query M, el pipeline utiliza `Table.SelectRows(Source, each [Hidden] = false)`. Al incorporar la lectura XML de `xl/workbook.xml` en Python para omitir hojas ocultas (`state="hidden"`), los metrajes de **CONDESTABLE** y **CUCULI** pasaron a coincidir al **100.00% (0.00 m de error)** con Control Interno, eliminando las falsas discrepancias de +196.10m y +117.65m.

### B. Artefactos de Precisión de Coma Flotante IEEE 754 (`1e-12` en Excel)
- **Causa Raíz:** La aritmética de coma flotante estándar IEEE 754 genera imprecisiones microscópicas al sustraer o sumar decimales (p. ej. `49.5 - 35.0 = 14.500000000000004` o `34.99999999999999`). Al construir tablas dinámicas en Excel sin redondeo previo, Excel muestra diferencias como `-4E-12` o `-8.18E-12` (es decir, `0.000000000004 m`).
- **Solución Replicada:** Se aplica redondeo explícito `.round(2)` en todas las métricas numéricas (`METRAJE`, `DESDE`, `HASTA`, `PROFUNDIDAD DE SONDAJE`), eliminando el ruido numérico a nivel de 12 decimales sin alterar ningún valor real de perforación.

---

## 3. Auditoría Detallada de la Única Discrepancia Restante: YAULIYACU (+125.40 m)

- **Resultado Auditoría**: **Desfase Justificado por Omisión en Planilla de Control Interno**.
- **Máquinas coincidentes en Yauliyacu**:
  - `XDR50USS-00T`: 947.30 m vs 947.30 m (Diferencia: **0.00 m**) 🟢
  - `XRD50USS-003`: 1,359.30 m vs 1,359.30 m (Diferencia: **0.00 m**) 🟢
- **Máquina discrepante**:
  - `XRD125USS-001`: **247.20 m (Detallado) vs 121.80 m (Control Interno)** → Diferencia: **+125.40 m** 🔴
- **Detalle de las fechas omitidas en Control Interno:**
  - 17 de Julio: 16.10 m (Turno A: 5.25m, Turno B: 10.85m)
  - 18 de Julio: 44.00 m (Turno A: 21.30m, Turno B: 22.70m)
  - 19 de Julio: 6.10 m (Turno B: 6.10m)
  - 20 de Julio: 17.90 m (Turno A: 4.85m, Turno B: 13.05m)
  - 21 de Julio: 31.10 m (Turno A: 13.30m, Turno B: 17.80m)
  - 25 de Julio: 10.20 m (Turno A: 8.50m, Turno B: 1.70m)
  - **Total Omisión en Control Interno:** **125.40 m**.

---

## 4. Conclusión de Calidad del Dato
- 17 de los 18 CTRs cuadran en **Coincidencia Exacta de 0.00 m**.
- No se ha forzado ni descartado ningún dato de manera arbitraria; todo se basa en la replicación exacta de las reglas de visibilidad y formato de Power Query M.
