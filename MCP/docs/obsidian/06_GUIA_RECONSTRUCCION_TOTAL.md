# 🛠️ Guía Maestra de Reconstrucción Total desde Cero

> [!TIP]
> Esta guía permite a cualquier ingeniero de datos o analista de BI reconstruir el archivo **`RESIDENTES.pbix`** desde un documento de Power BI en blanco paso a paso.

---

## Fase 1: Pipeline ETL y Generación de Datos

1. Asegurarse de tener instalado Python 3.10+ con las librerías requeridas:
   ```bash
   pip install polars calamine unidecode
   ```
2. Ejecutar el script maestro de transformación:
   ```bash
   python "src/etl/procesarv2.py"
   ```
3. Verificar que se hayan generado los archivos CSV en la carpeta de destino:
   * `Fact_Tiempos.csv`
   * `Fact_Metraje.csv`
   * `Dim_Maquina.csv`
   * `Dim_Personal.csv`
   * `Dim_Sondaje.csv`
   * `Dim_CTR.csv`
   * `Fact_Personal_Asignado.csv`

---

## Fase 2: Configuración en Power BI Desktop

1. Abrir Power BI Desktop y crear un archivo nuevo en blanco.
2. **Obtener Datos (Get Data):**
   * Importar los 7 archivos CSV generados por el ETL.
   * Importar las hojas de Excel complementarias:
     * `Fact_Abastecimiento`
     * `Consumo Consolidado`
     * `Fact_Metas`
     * `Reporte_Brocas`
     * `Dim_Familias`
3. **Crear la Tabla de Calendario Operativo (`Dim_Calendario`):**
   Crear una tabla calculada con DAX:
   ```dax
   Dim_Calendario = 
   VAR BaseCalendar = CALENDAR(DATE(2024, 1, 1), DATE(2027, 12, 31))
   RETURN
   ADDCOLUMNS(
       BaseCalendar,
       "Año Operativo", IF(DAY([Date]) >= 26, YEAR([Date]) + IF(MONTH([Date])=12, 1, 0), YEAR([Date])),
       "Mes Num Operativo", IF(DAY([Date]) >= 26, IF(MONTH([Date])=12, 1, MONTH([Date])+1), MONTH([Date])),
       "Mes Operativo", FORMAT(DATE(YEAR([Date]), IF(DAY([Date]) >= 26, IF(MONTH([Date])=12, 1, MONTH([Date])+1), MONTH([Date])), 1), "MMMM"),
       "Periodo Sort", (IF(DAY([Date]) >= 26, YEAR([Date]) + IF(MONTH([Date])=12, 1, 0), YEAR([Date])) * 100) + IF(DAY([Date]) >= 26, IF(MONTH([Date])=12, 1, MONTH([Date])+1), MONTH([Date])),
       "Semana Num", WEEKNUM([Date], 2),
       "Semana Operativa", "SEM " & FORMAT(INT((DAY([Date]) + 5) / 7), "00")
   )
   ```

---

## Fase 3: Creación de Relaciones del Modelo

Configurar las 23 relaciones exactamente como se detalla en [[03_MODELO_RELACIONAL]]:
* Establecer `Dim_Calendario[Date]` como eje central temporal (1:N hacia todas las tablas de hechos).
* Establecer `Dim_CTR[CTR]` como eje central de proyectos (1:N hacia todas las tablas de hechos).
* Establecer `Dim_Maquina[MAQUINA]` como dimensión de equipos (1:N Both hacia `Fact_Metraje`).

---

## Fase 4: Creación de la Tabla de Medidas

1. En la pestaña **Inicio** $ightarrow$ **Especificar Datos** $ightarrow$ Crear tabla vacía llamada **`Medidas`**.
2. Copiar y pegar las medidas DAX del catálogo [[04_CATALOGO_MEDIDAS_DAX]] y [[05_SISTEMA_METRAJE_PERDIDO_AJUSTADO]]:
   * `Total Metros`
   * `Total Horas`
   * `Horas Operativas`
   * `ROP_Efectivo`
   * `f_efectivo`
   * `m_perdido_ajustado`
   * `Meta Diaria Lineal`
   * `Ejecutado Acumulado`
   * `Meta Acumulada Periodo`
   * `Costo Consumo x Metro ($/m)`
   * `Presupuesto` y proyecciones.

---

## Fase 5: Estructura de Páginas Visuales

### 📄 Página 1: Principal / Dashboard Ejecutivo
* **KPIs Superiores:** `[Total Metros]`, `[Meta Acumulada Periodo]`, `[Cumplimiento % Operativo]`, `[ROP (m/hr)]`, `[Costo Consumo x Metro ($/m)]`.
* **Gráfico Central:** Ejecutado acumulado vs Meta acumulada a lo largo del periodo operativo (`Dim_Calendario[Date]`).
* **Slicers:** Periodo Operativo, CTR, Máquina.

### 📄 Página 2: Desglose de Horas y Pérdida de Metraje
* **Matriz de Pérdidas:** `CTR` $ightarrow$ `Categoria` $ightarrow$ `Actividad` con `[Total Horas]` y `[m_perdido_ajustado]`.
* **Gráfico de Barras:** Horas de Standby Cliente y Mantenimiento por Máquina.

### 📄 Página 3: Control de Sondajes (Gantt)
* **Visual de Sondajes:** `Dim_Sondaje[SONDAJE]`, `FECHA_INICIO_REAL`, `FECHA_FIN_REAL`, `[% Avance Gantt]`, `[Etiqueta Avance]`.
