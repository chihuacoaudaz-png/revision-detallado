# Pipeline ETL de Reportes Detallados y Auditoría de Control Interno (Rockdrill)

Este repositorio contiene la arquitectura completa del pipeline de Extracción, Transformación y Carga (ETL), la implementación en **Power Query M** para Power BI, las copias de respaldo de seguridad y la conciliación de metrajes por `ID_CLAVE_UNICA` contra la base de datos oficial (`bbdd.xlsx`).

---

## 📂 Consultas Power Query M Listas para Usar (`codigo_m/`)

El repositorio contiene las consultas M listas para copiar y pegar directamente en el Editor de Power Query de Power BI o Excel:

1. **`codigo_m/codigo_m_detallados.txt`** ➔ Consulta **`Detallados_BD`**:
   - Extrae los 18 proyectos CTR (excluye Colquijirca).
   - Lee cabeceras duales (filas 22 y 23 de Excel).
   - Propaga fechas y sondajes (`FillDown` + `FillUp`).
   - Mapea `TURNO_ESTANDAR` a `"A"` (Día) y `"B"` (Noche).
   - **Resultado**: 6,428 filas procesadas con las 135 columnas oficiales.

2. **`codigo_m/codigo_m_control_interno.txt`** ➔ Consulta **`Consolidado_BD`**:
   - Motor dual: lee archivo plano (`BASE DE DATOS`) o las 30 pestañas diarias (`26.06` a `25.07`).
   - Selecciona estrictamente las **9 columnas oficiales**: `FECHA`, `CTR`, `APLICACION`, `MAQUINA_RAW`, `MAQUINA`, `SE_PERFORO`, `TURNO_ESTANDAR`, `METRAJE_CI`, `ID_CLAVE_UNICA`.
   - Asigna `TURNO_ESTANDAR` basándose en la posición/celda `DIAS_TRABAJADOS` (`1` = `"A"`, `null` = `"B"`).
   - **Resultado**: 3,204 filas consolidadas.

3. **`codigo_m/codigo_m_matriz_discrepancias.txt`** ➔ Consulta **`Discrepancias_BD`**:
   - Cruce Full Outer Join por `ID_CLAVE_UNICA` (`YYYY-MM-DD|CTR|MAQUINA|TURNO_ESTANDAR`).
   - Calcula `DIFERENCIA = METRAJE_DETALLADO - METRAJE_CONTROL_INTERNO`.
   - Filtra registros con `ABS(DIFERENCIA) >= 0.01`.
   - Ordenamiento multinivel corregido: `{{"FECHA", Order.Ascending}, {"CTR", Order.Ascending}, {"MAQUINA", Order.Ascending}}`.
   - **Resultado**: Exactamente **935 filas de discrepancias** (100.00% coincidencia con `bbdd.xlsx`).

### 🛡️ Copias de Respaldo Incluidas:
- `codigo_m/codigo_m_detallados_backup.txt`
- `codigo_m/codigo_m_control_interno_backup.txt`

---

## 📊 Comparativo Definitivo de Metrajes por Contrato (`bbdd.xlsx`)

| CTR | Metraje Detallados | Metraje Control Interno | Diferencia | Estado |
| :--- | :---: | :---: | :---: | :---: |
| **AMERICANA** | 2,511.20 | 2,511.20 | **0.00** | ✅ Coincidencia Exacta |
| **ANDAYCHAGUA** | 2,315.85 | 2,315.85 | **0.00** | ✅ Coincidencia Exacta |
| **CATALINA HUANCA** | 4,677.20 | 4,677.20 | **0.00** | ✅ Coincidencia Exacta |
| **CERRO** | 660.20 | 660.20 | **0.00** | ✅ Coincidencia Exacta |
| **CHUNGAR** | 2,346.05 | 2,347.55 | **-1.50** | ⚠️ Diferencia Real Origen |
| **COBRIZA** | 4,376.70 | 4,376.70 | **0.00** | ✅ Coincidencia Exacta |
| **COLQUISIRI** | 1,165.60 | 1,165.60 | **0.00** | ✅ Coincidencia Exacta |
| **CONDESTABLE** | 2,800.40 | 2,800.40 | **0.00** | ✅ Coincidencia Exacta |
| **CUCULI** | 804.10 | 804.10 | **0.00** | ✅ Coincidencia Exacta |
| **INMACULADA** | 3,404.55 | 3,404.55 | **0.00** | ✅ Coincidencia Exacta |
| **LA ESTRELLA** | 1,228.70 | 1,228.70 | **0.00** | ✅ Coincidencia Exacta |
| **MOROCOCHA** | 1,796.40 | 1,842.80 | **-46.40** | ⚠️ Diferencia Real Origen |
| **RAURA** | 2,793.51 | 2,793.51 | **0.00** | ✅ Coincidencia Exacta |
| **SAN CRISTOBAL** | 2,325.40 | 2,325.40 | **0.00** | ✅ Coincidencia Exacta |
| **TAMBOJASA** | 299.55 | 299.55 | **0.00** | ✅ Coincidencia Exacta |
| **TICLIO** | 484.15 | 484.15 | **0.00** | ✅ Coincidencia Exacta |
| **YAULIYACU** | 2,553.80 | 2,428.40 | **+125.40** | ⚠️ Diferencia Real Origen |
| **YAURICOCHA** | 188.75 | 188.75 | **0.00** | ✅ Coincidencia Exacta |
| **TOTAL** | **36,732.11** | **36,654.61** | **+77.50** | 🎯 **100% Validado en BBDD** |

---

## 🚀 Guía para Ejecutar el Entorno Python

```bash
git clone https://github.com/chihuacoaudaz-png/revision-detallado.git
cd revision-detallado

# Crear entorno virtual e instalar librerías
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install python-calamine pandas openpyxl numpy

# Validar sintaxis M y reglas de negocio
python validate_all_m_syntax.py
```
