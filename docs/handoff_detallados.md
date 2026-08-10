# Documento de Handoff y Estado del Proyecto - ETL de Reportes Detallados por Equipo

## 1. Contexto y En Qué Se Está Trabajando
El proyecto consiste en el desarrollo, optimización y consolidación del pipeline ETL en Python para la limpieza automatizada de los **Reportes Detallados por Equipo** de perforación de Rockdrill (`RD.402.P.01.F.01`). 

Estos reportes son archivos Excel complejos emitidos individualmente por cada contrato (CTR) y contienen múltiples pestañas/hojas dedicadas a cada máquina operativa (ej. `XRD50U-002`, `XRD90U-004`, `LM75U-011`). El objetivo central del pipeline es consolidar estos archivos descentralizados en una única tabla estructurada de 133 columnas oficiales, garantizando la integridad de datos, limpieza numérica profunda y trazabilidad por turno.

---

## 2. Lo Que Está Hecho y Funcionalidades Validadas
Se ha completado el 100% de la arquitectura ETL del script [`pipeline_limpieza.py`](file:///c:/Proyectos%20Python/Detallados/pipeline_limpieza.py). Las capacidades implementadas y verificadas incluyen:

1. **Lectura Ultra-Rápida de Excel**: Migración completa de `openpyxl` a `python-calamine` (`CalamineWorkbook`), reduciendo tiempos de lectura de minutos a milisegundos.
2. **Truncamiento de Hojas Corruptas (`[:200]`)**: Slicing de seguridad que limita la lectura a las primeras 200 filas por hoja, evitando cuelgues o consumo excesivo de RAM causados por celdas con formato fantasma que extendían el rango hasta 1,048,576 filas (ej. hoja `XRD90U-010` en San Cristóbal).
3. **Mapeo Dual-Row de Encabezados (Equivalente M)**: Replicación exacta del comportamiento de Power Query M `Table.Skip([Data], 22)`, donde la Fila 23 (index 22) actua como categoría con *forward-fill* horizontal y la Fila 24 (index 23) actua como sub-encabezado.
4. **Limpieza Numérica Profunda (`clean_number_value`)**: Eliminación automatizada de apostrofes (`'`), tildes (`´`), comillas (`"`), espacios no rompibles (`\xa0`) y conversión de comas decimales (`,`) a puntos (`.`).
5. **Corrección de FECHA (ffill) y MES Operacional**: Aplicación de `ffill()` a nivel de hoja individual antes del filtrado de filas vacías. Esto corrige el error donde las filas del Turno 2 (que en Excel venían con la fecha vacía) heredan la fecha del Turno 1, permitiendo calcular correctamente el `MES` operacional (corte al día 26).
6. **Estandarización de Turnos ('A' y 'B')**: Conversión sistemática de cualquier nomenclatura (`1`/`2`, `A`/`B`/`C`, `D`/`N`, `G1`/`G2`) a `A` (Turno Día / Guardia 1) y `B` (Turno Noche / Guardia 2).
7. **Generación de `ID_CLAVE_UNICA`**: Construcción automatizada de la clave `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}` en cada fila para trazabilidad unívoca.
8. **Estandarización de Máquinas SAP**: Integración de la matriz de `Excepciones` de `Maestros_Maquinas.xlsx` para mapear nombres heterogéneos de hojas a códigos oficiales SAP.
9. **Exclusión Explícita de COLQUIJIRCA**: Exclusión de negocio configurada mediante `CTRS_EXCLUIDOS = {"COLQUIJIRCA"}`.
10. **Exportación Consolidada**: Generación limpia de `detallados_consolidados.xlsx` y `detallados_consolidados.csv` (2,716 filas x 134 columnas).

---

## 3. Dónde Estamos / Etapa del Proyecto
- **Fase Actual**: **ETL Finalizado y Validado (Ready for Production / BI Integration)**.
- El pipeline se ejecuta de forma autónoma en < 3 segundos, procesando 18 archivos Excel de CTR y 57 hojas operativas de máquinas, generando los consolidados sin errores.

---

## 4. Decisiones Técnicas Tomadas y Razón de Ser (Justificación)

| Decisión Técnica | Razón de Ser / Justificación Técnica |
|---|---|
| **Uso de `python-calamine` sobre `openpyxl`** | `openpyxl` parsea el DOM XML completo creando millones de objetos Python por celda vacía cuando `dimension ref` indica 1,048,576 filas. `python-calamine` utiliza Rust en segundo plano y lee en binario C, reduciendo el tiempo de 45 segundos por archivo a 0.05 segundos. |
| **Slicing de filas `raw_rows[:200]`** | Se determinó que ningún parte diario por máquina contiene más de 120 filas (31 días x 2 turnos + cabeceras = ~75 filas). Acotar a las primeras 200 filas previene fugas de memoria sin perder un solo dato operativo. |
| **`ffill()` de FECHA antes del filtro de vacíos** | En Excel, los supervisores colocaban la fecha solo en el Turno 1 (celda combinada visual). Si se filtraban primero las filas vacías, las filas del Turno 2 perdían su fecha y el cálculo de `MES` por defecto asignaba `ENERO`. |
| **Estandarización de Turnos a 'A' y 'B'** | Cada contrato utiliza códigos distintos (`1`/`2`, `A`/`B`/`C`, `D`/`N`). Unificar en `A` (Día) y `B` (Noche) permite cruzar los partes de máquina contra Control Interno sin desalineaciones de turno. |
| **Generación de `ID_CLAVE_UNICA`** | Permite auditorías y cruzados automáticos de metrajes turno a turno entre la vista de supervisores (`Detallados`) y la vista administrativa (`Control Interno`). |
| **Exclusión explícita de `COLQUIJIRCA`** | Por definición de negocio, Colquijirca no maneja control de metrajes en este esquema de detallados. Su inclusión distorsionaba la matriz comparativa. |

---

## 5. Siguientes Pasos Concretos (Próximas Acciones)

1. **Automatización de Ejecución Programada**:
   - Configurar una tarea programada (Windows Task Scheduler o Cron) para ejecutar `pipeline_limpieza.py` al cierre de cada guardia o de forma diaria.
2. **Carga en Modelo Semántico BI / Power BI**:
   - Importar `detallados_consolidados.csv` en el modelo de datos de Power BI o SQL Server como la tabla de hechos de avance diario (`Fact_AvanceDetallado`).
3. **Monitoreo de Alertas de Auditoría**:
   - Consumir la columna `Alerta_Comentarios` (`FALTA COMENTARIO` / `OK`) para enviar reportes automáticos a los supervisores cuando registren metrajes en `Otros*` sin justificación explicativa.

---

## 6. Stack y Framework de Python Utilizado

- **Python**: 3.12+ (64-bit)
- **Librería de Lectura de Excel**: `python-calamine` v0.2.0+ (Parser C/Rust ultra rápido)
- **Librería de Manipulación de Datos**: `pandas` v2.2+ (Transformación, `ffill`, `groupby`, `merge`)
- **Librería de Cálculo Matemático / Numérico**: `numpy` v1.26+ (Manejo de `NaN` y conversiones flotantes)
- **Librería de Exportación Excel**: `openpyxl` v3.1+ (Escritura de `.xlsx` consolidado)
- **Módulos Nativos de Python**: `pathlib.Path`, `unicodedata`, `re`, `datetime`, `dateutil.relativedelta`.
