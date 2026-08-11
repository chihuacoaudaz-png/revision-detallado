# 🗺️ Guía Completa de Ubicación de Archivos y Documentación (Revisión a Mano)

Este documento detalla la estructura exacta del repositorio **`revision-detallado`** para facilitar la revisión a mano desde cualquier equipo (Casa / Oficina).

---

## 📌 1. Archivo de Configuración Central (Portabilidad Casa / Oficina)

- 📄 **[config.py](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/config.py)**
  - **Propósito:** Controla todas las rutas del proyecto en un solo lugar.
  - **Modo por defecto:** `"AUTO"` (autodetecta la carpeta dentro del repositorio clonado).
  - **Para cambiar de PC:** Si deseas usar rutas personalizadas en tu PC de casa o de oficina, solo edita la variable `MODO_ENTORNO = "CUSTOM"` y pon tu ruta en `RUTA_CUSTOM`.

---

## ⚙️ 2. Scripts Principales del Pipeline ETL y Reglas de Limpieza

| Script | Descripción | Documentación Asociada |
|---|---|---|
| 📄 **[pipeline_limpieza.py](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/pipeline_limpieza.py)** | Pipeline principal de limpieza por CTR. Aplica el filtro de **hojas visibles (`sheet.visible`)**, dual-row headers, FillDown horizontal, turnos A/B, clave única y redondeo `.round(2)` para eliminar imprecisiones IEEE 754 (`1e-12`). | 📘 **[handoff_detallados.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/handoff_detallados.md)**<br>📘 **[logica_m_campos_detallados.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/logica_m_campos_detallados.md)**<br>📘 **[replicacion_detallada_detallados.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/replicacion_detallada_detallados.md)** |
| 📄 **[01_Control_Interno_ETL/compilar_control_interno.py](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/compilar_control_interno.py)** | Extrae y compila las 30 hojas diarias de avance de Control Interno (`RD.402.P.01.F.04`). Genera clave única de turno `FECHA\|CTR\|MAQUINA\|TURNO`. | 📘 **[handoff_control_interno.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/handoff_control_interno.md)**<br>📘 **[logica_m_campos_control_interno.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/logica_m_campos_control_interno.md)**<br>📘 **[replicacion_detallada_control_interno.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/docs/replicacion_detallada_control_interno.md)** |
| 📄 **[01_Control_Interno_ETL/matriz_comparativa_metrajes.py](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/matriz_comparativa_metrajes.py)** | Cruza Detallados vs Control Interno por clave única de turno y genera el informe de discrepancias con `.round(2)`. | 📘 **[analisis_discrepancias_metrajes.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/analisis_discrepancias_metrajes.md)** |
| 📄 **[drilldown_discrepancies.py](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/drilldown_discrepancies.py)** | Script de auditoría fina día a día y máquina a máquina para rastreo de diferencias de metraje. | 📘 **[analisis_discrepancias_metrajes.md](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/analisis_discrepancias_metrajes.md)** |

---

## 📊 3. Archivos de Resultados y Salidas (Outputs Generados)

### Salidas de Reporte Detallado (`output/`):
- 📊 **[output/detallados_consolidados.csv](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/output/detallados_consolidados.csv)** — Dataset consolidado plano (3,158 filas, 134 columnas oficiales).
- 📊 **[output/detallados_consolidados.xlsx](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/output/detallados_consolidados.xlsx)** — Libro Excel consolidado oficial de detallados.

### Salidas de Control Interno y Matriz Comparativa (`01_Control_Interno_ETL/output/`):
- 📊 **[01_Control_Interno_ETL/output/control_interno_compilado.csv](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/output/control_interno_compilado.csv)** — Compilación diaria de Control Interno (3,204 turnos).
- 📊 **[01_Control_Interno_ETL/output/control_interno_compilado.xlsx](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/output/control_interno_compilado.xlsx)** — Excel compilado de Control Interno.
- 📊 **[01_Control_Interno_ETL/output/matriz_comparativa_metrajes.xlsx](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/output/matriz_comparativa_metrajes.xlsx)** — Excel comparativo con hojas por turno, resumen por CTR y discrepancias.
- 📊 **[01_Control_Interno_ETL/output/discrepancias_diarias_detalladas.csv](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/output/discrepancias_diarias_detalladas.csv)** — Detalle plano de turnos con diferencias.
- 📊 **[01_Control_Interno_ETL/output/resumen_discrepancias_ctr.csv](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/01_Control_Interno_ETL/output/resumen_discrepancias_ctr.csv)** — Resumen acumulado de metrajes por CTR.

---

## 📁 4. Archivos Excel Fuente (`Estructura base/` y `archivos/`)

- 📂 **[Estructura base/Rockdrill_Control_Operaciones/](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/Estructura%20base/Rockdrill_Control_Operaciones)**
  - Contiene las 18 carpetas `CTR_*` con sus archivos Excel de partes diarios y reportes detallados.
  - Subcarpeta `00_Control_Interno/`: Excel de Consolidado de Avance Julio.
  - Subcarpeta `Maestro_Maquinas/`: Excel `Maestros_Maquinas.xlsx` con la matriz de excepciones SAP.
- 📂 **[archivos/](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/archivos)** — Colección de archivos Excel originales de los reportes de avance por CTR.
- 📂 **[base de comparacion/](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/base%20de%20comparacion)** — Archivo `julio2026.xlsx` de referencia comparativa.

---

## 🧪 5. Scripts de Pruebas y Utilidades (`tests/` y `tools/`)

- 📂 **[tests/](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/tests)** (10 scripts de pruebas de unidad e integración):
  - `test_standardize_turnos.py`, `test_unique_key_matching.py`, `test_extract_control_interno.py`, `test_cleaning_fixes.py`, etc.
- 📂 **[tools/](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/tools)** (19 scripts de inspección y auditoría):
  - `inspect_headers.py`, `inspect_morococha_diffs.py`, `audit_chungar.py`, `compare_totals.py`, etc.
- 📓 **[auditoria.ipynb](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/auditoria.ipynb)** — Jupyter Notebook para análisis interactivo de discrepancias.
- 📊 **[Auditoria_Visual_Discrepancias.xlsx](file:///c:/Proyectos%20Pyhton/detallados/revision-detallado/Auditoria_Visual_Discrepancias.xlsx)** — Libro de trabajo de auditoría visual.

---

## 🚀 6. Guía Rápida para Ejecutar Todo el Proceso

En cualquier computadora (Casa u Oficina):

```powershell
# 1. Clonar o hacer pull en el directorio
git pull origin main

# 2. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Ejecutar pipeline completo en orden
python pipeline_limpieza.py
python 01_Control_Interno_ETL/compilar_control_interno.py
python 01_Control_Interno_ETL/matriz_comparativa_metrajes.py
```
