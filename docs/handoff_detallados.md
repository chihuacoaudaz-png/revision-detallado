# Documento de Handoff y Estado del Proyecto - ETL de Reportes Detallados por Equipo

## 1. Contexto y En Qué Se Está Trabajando
El proyecto consiste en el desarrollo, optimización y consolidación del pipeline ETL en Python y **Power Query M** para la limpieza automatizada de los **Reportes Detallados por Equipo** de perforación de Rockdrill (`RD.402.P.01.F.01`).

Estos reportes son archivos Excel complejos emitidos individualmente por cada contrato (CTR) y contienen múltiples pestañas/hojas dedicadas a cada máquina operativa (ej. `XRD50U-002`, `XRD90U-004`, `LM75U-011`). El objetivo central del pipeline es consolidar estos archivos descentralizados en una única tabla estructurada de 135 columnas oficiales y conectar mediante `ID_CLAVE_UNICA` con **Control Interno** para conciliación diaria.

---

## 2. Lo Que Está Hecho y Funcionalidades Validadas

1. **Lectura y Procesamiento de 18 CTRs**: Extracción de **6,428 registros de Detallados** across all operational contracts.
2. **Propagación de Sondajes Vacíos (`FillDown` + `FillUp`)**: Resueltos los casos especiales de Chungar (Máquina `LM110U-001`, 06-jul Turno B 1.50m) y Morococha.
3. **Fórmula de Turno Estandarizado (`TURNO_ESTANDAR`)**: Estandarización directa a `"A"` (Día) y `"B"` (Noche) sobre cada registro de fila.
4. **Cálculo de `ID_CLAVE_UNICA`**: Formato unívoco `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}` para conciliación.
5. **Cruce de Conciliación en `Discrepancias_BD`**: Reconciliación 1-a-1 verificada empíricamente contra `bbdd.xlsx`, alcanzando **935/935 coincidencia exacta de discrepancias**.

---

## 3. Estado de Conciliación en BBDD

- **15 de los 18 CTRs** registran **0.00 m de diferencia acumulada** (coincidencia exacta al centímetro).
- **CHUNGAR**: `2,346.05 m` vs `2,347.55 m` (Diferencia real origen: **-1.50 m**).
- **MOROCOCHA**: `1,796.40 m` vs `1,842.80 m` (Diferencia real origen: **-46.40 m**).
- **YAULIYACU**: `2,553.80 m` vs `2,428.40 m` (Diferencia real origen: **+125.40 m**). Explicado por perforación paralela no cobrable.

---

## 4. Archivos Entregados en GitHub

- `codigo_m/codigo_m_detallados.txt` (Consulta `Detallados_BD` en M)
- `codigo_m/codigo_m_control_interno.txt` (Consulta `Consolidado_BD` en M)
- `codigo_m/codigo_m_matriz_discrepancias.txt` (Consulta `Discrepancias_BD` en M)
- `codigo_m/codigo_m_detallados_backup.txt` (Copia de respaldo)
- `codigo_m/codigo_m_control_interno_backup.txt` (Copia de respaldo)
