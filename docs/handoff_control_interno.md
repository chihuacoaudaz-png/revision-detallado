# Documento de Handoff y Estado del Proyecto - ETL y Compilación de Control Interno

## 1. Contexto y En Qué Se Está Trabajando
Esta vertiente del proyecto abarca el desarrollo de la herramienta de compilación y auditoría de **Control Interno** (`RD.402.P.01.F.04 Consolidado de Avance Julio.xlsx`). 

El archivo de Control Interno es un libro maestro utilizado por la administración central para consolidar los metrajes reportados diariamente. Contiene 30 pestañas asociadas a cada día del mes operacional (`26.06` a `25.07`). El objetivo fue construir un procedimiento automatizado que extraiga y unifique esta información en una estructura estándar de turnos (`A`/`B`) y la cruce mediante una `ID_CLAVE_UNICA` contra los **Reportes Detallados por Equipo**, aislando las diferencias exactas de metraje.

---

## 2. Lo Que Está Hecho y Funcionalidades Validadas
Se ha completado la implementación de los módulos [`compilar_control_interno.py`](file:///c:/Proyectos%20Python/Detallados/01_Control_Interno_ETL/compilar_control_interno.py) y [`matriz_comparativa_metrajes.py`](file:///c:/Proyectos%20Python/Detallados/01_Control_Interno_ETL/matriz_comparativa_metrajes.py):

1. **Extracción Adaptativa desde Fila 10 hasta 'TOTAL AVANCE'**:
   - Escaneo automático de las 30 pestañas diarias (`26.06` a `25.07`).
   - Identificación dinámica de la celda de parada `TOTAL AVANCE` o `TOTAL ACUMULADO` en la Columna C, omitiendo filas de totales e informativos de pie de página.
2. **Filldown Estandarizado de CTR (Columna A)**:
   - Recuperación del nombre del CTR de celdas combinadas horizontales/verticales mediante propadación hacia abajo (*filldown*).
3. **Estandarización de Máquinas SAP**:
   - Mapeo de nombres de equipos utilizando la matriz de `Excepciones` de `Maestros_Maquinas.xlsx` y aliases específicos (ej. `TICLIO / XRD150USS-001` $\rightarrow$ `XRD150U-007`).
4. **Estandarización de Turnos A/B y Clave Única**:
   - Asignación de Turno 1 como **`A`** (Día) y Turno 2 como **`B`** (Noche) basado en la secuencia de aparición de cada equipo en la hoja diaria.
   - Generación de `ID_CLAVE_UNICA` = `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}` para 3,204 registros de Control Interno.
5. **Exclusión Explícita de COLQUIJIRCA**:
   - Filtrado de registros de Colquijirca para mantener la homogeneidad con el pipeline de Detallados.
6. **Matriz Comparativa Automática**:
   - Ejecución de `outer join` por `ID_CLAVE_UNICA` evaluando $\text{DIFERENCIA} = \text{DETALLADOS} - \text{CONTROL\_INTERNO}$.
   - Aislamiento e identificación exacta de las **5 discrepancias principales**:
     - **CHUNGAR**: -1.50 m (Diferencia el 05-Jul en `LM110U-001`).
     - **CONDESTABLE**: +196.10 m (Registros de sept/oct 2025 en `LM75UFDR-001` presentes en Detallados pero omitidos en Control Interno).
     - **CUCULI**: +117.65 m (Registros de nov 2025 en `XRD100ST-001 (2)` omitidos en Control Interno).
     - **MOROCOCHA**: -46.40 m (4 fechas específicas con mayor avance reportado en Control Interno).
     - **YAULIYACU**: +125.40 m (Registros de `XRD125USS-001` del 17 al 25 de julio no reportados en Control Interno).
   - Coincidencia perfecta (0.00 m de diferencia) en los **14 CTRs restantes**.

---

## 3. Dónde Estamos / Etapa del Proyecto
- **Fase Actual**: **Auditoría Comparativa Completada y Documentada (Entregable Intermedio Finalizado)**.
- Se han generado todos los reportes compilados en Excel y CSV dentro de `01_Control_Interno_ETL/output/`.

---

## 4. Decisiones Técnicas Tomadas y Razón de Ser (Justificación)

| Decisión Técnica | Razón de Ser / Justificación Técnica |
|---|---|
| **Lectura con Detección Dinámica de 'TOTAL AVANCE'** | En Control Interno las tablas diarias varían en cantidad de máquinas (filas 10 a 125 aprox.). Detener la lectura al encontrar `TOTAL AVANCE` evita procesar resúmenes acumulados que duplicarían los números. |
| **Generación de `TURNO_ESTANDAR` por Secuencia (1->A, 2->B)** | En las hojas de Control Interno las máquinas se repiten exactamente 2 veces consecutivas (Turno Día y Turno Noche) sin tener una columna explícita de turno. Mapear la 1ra aparición a `A` y 2da a `B` empareja 1:1 con los turnos de los partes detallados. |
| **Comparación por `ID_CLAVE_UNICA` ({FECHA}\|{CTR}\|{MAQUINA}\|{TURNO})** | Comparar por totales acumulados oculta errores cruzados (ej. un día con +10m y otro con -10m daría 0m). La clave única por turno expone la discrepancia a nivel de guardia. |
| **Resguardo de Permisos en Salida CSV (`try/except PermissionError`)** | Si el usuario tiene abierto el archivo CSV en Excel durante la ejecución, Python fallaba con `PermissionError`. El script captura el error y emite un warning sin abortar el flujo. |

---

## 5. Siguientes Pasos Concretos (Próximas Acciones)

1. **Retroalimentación a Supervisores y Administración**:
   - Compartir el archivo [`analisis_discrepancias_metrajes.md`](file:///c:/Proyectos%20Python/Detallados/01_Control_Interno_ETL/analisis_discrepancias_metrajes.md) con el área de operaciones para que regularicen los partes de Morococha y Yauliyacu.
2. **Implementación de Reglas de Conciliación Automática**:
   - Incorporar un flag de estado `DIFERENCIA_AUDITORIA` en el dashboard de Power BI para alertar en tiempo real cuando el avance del día difiera entre el parte de guardia y la planilla de Control Interno.

---

## 6. Stack y Framework de Python Utilizado

- **Python**: 3.12+
- **Librería de Lectura Excel**: `python-calamine` (Detección limpia de hojas `26.06` a `25.07`)
- **Librería de Análisis**: `pandas` (`merge(how='outer')`, `groupby`, `agg`)
- **Librería de Exportación**: `openpyxl` (Generación del libro comparativo `matriz_comparativa_metrajes.xlsx`)
- **Estructura de Carpetas**: `01_Control_Interno_ETL/output/`
