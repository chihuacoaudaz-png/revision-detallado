# 06. Regla de Negocio Inviolable: Conciliación 1-a-1 y Auditoría de Sentido Común
**Proyecto**: Sistema Unificado de Business Intelligence y Analítica de Perforación  
**Ubicación**: `C:/Proyectos Python/Detallados/docs/06_REGLA_DE_NEGOCIO_CONCILIACION_Y_AUDITORIA_SENTIDO_COMUN.md`  
**Organización**: Rockdrill Group  

---

## 🏛️ 1. Axioma Fundamental de Conciliación de Metrajes

> [!IMPORTANT]
> **REGLA DE NEGOCIO INVIOLABLE (AXIOMA DE CONCILIACIÓN DIARIA)**:
> Los metrajes de perforación **DEBEN COINCIDIR EXACTAMENTE (0.00 m)** entre el **Reporte Detallado (`RD.402.P.01.F.01`)** y el **Consolidado de Control Interno (`RD.402.P.01.F.04`)** para el **MISMO DÍA, MISMA MÁQUINA y MISMO TURNO**:
>
> $$\text{ID\_CLAVE\_UNICA} = \text{YYYYMMDD} - \text{MAQUINA} - \text{TURNO}$$
> $$\text{DIFERENCIA} = \text{METRAJE\_DETALLADO} - \text{METRAJE\_CONTROL\_INTERNO} = 0.00\text{ m}$$

### ❌ Lo que es Inaceptable (Falsa Cuadratura):
* **Falsa Cuadratura Mensual**: Si la sumatoria total del mes coincide pero existen discrepancias dispersas en los días y turnos individuales, **el flujo está mal construido o desfasado**.
* No se admiten compensaciones artificiales entre turnos A y B o entre días contiguos sin diagnóstico fundado.
* Si no coincide la clave primaria, **se detecta un error operacional o una omisión de campo inmediata**.

---

## 🎯 2. Banco de Pruebas Canónico (Benchmark de Verificación)

Cualquier cambio en el pipeline (Python o Power Query M) debe validarse obligatoriamente contra este banco de pruebas conocido:

| Contrato / Máquina | Prueba de Verificación | Resultado Esperado | Diagnóstico de Negocio |
| :--- | :--- | :---: | :--- |
| **AMERICANA / `XRD50U-002`** | Conciliación diaria completa (26.08 y 27.08) | **100.00% Coincidencia Exacta (0.00 m)** | 26.08: 35.0m (A) + 15.5m (B)<br/>27.08: 30.4m (A) + 12.0m (B) |
| **AMERICANA / `XRD50USS-001`** | Auditoría de omisión de reporte en campo | **Discrepancia Exacta de -35.00 m** | 27.08 Turno B: Control Interno reporta 35.0m; en el Detallado no fue digitado (omisión real de campo). |
| **CATALINA HUANCA** | Extracción estándar en plantilla unificada | **100.00% Coincidencia Exacta** | El metraje reside estrictamente en la **Columna J** (índice 9). |

---

## 🛡️ 3. Agente Auditor de Sentido Común (`audit_common_sense_agent`)

Se establece un subagente y módulo de auditoría autónomo encargado de:
1. **Cuestionar Sistemáticamente los Resultados**: Ninguna salida se da por aprobada si el porcentaje de coincidencia exacta por clave primaria cae por debajo del 95% sin justificación física.
2. **Inspección de Monotonía y Cotas**: Validar $HASTA \ge DESDE$ y $METRAJE = HASTA - DESDE$.
3. **Validación de Balance de Jornada**: Auditar que la suma de horas operativas e inoperativas no exceda las $12.0\text{ h}$ estándar por guardia.
4. **Log de Rectificación**: Toda diferencia real se aísla en `output/reporte_anomalias_campo.xlsx` para tramitar su rectificación con la administradora de contrato y jefatura de operaciones.
