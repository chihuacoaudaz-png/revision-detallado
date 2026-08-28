# Especificación Técnica del Nuevo Estándar SIG (RD.402.P.01.F.01)

## 1. Resumen Ejecutivo
El formato **RD.402.P.01.F.01 (Reporte Detallado de Avance)** ha sido estandarizado a nivel corporativo para Rockdrill Group, alcanzando una estructura canónica fija de **168 columnas** y **507 celdas combinadas preservadas**, compatible con el Sistema Integrado de Gestión (SIG) y el pipeline ETL de Control de Gestión.

---

## 2. Arquitectura Canónica de 168 Columnas

| Bloque / Sección | Columnas | Letras Excel | Descripción Operativa |
| :--- | :---: | :---: | :--- |
| **Identificación y Sondaje** | 1 – 5 | `A:E` | Fecha, Nombre del Sondaje, Profundidad Total, Línea (HQ/NQ/BQ/PQ/W80/W100) e Inclinación/Azimut. |
| **Avance Diario y Cuadrilla** | 6 – 15 | `F:O` | Profundidades (Desde, Hasta), Turno (A/B), Grupo (1..5), Metraje Guardia, Horas Extras, Perforista, Ayudante 1, Ayudante 2 y Total Metraje Día. |
| **Comparativo y Metas** | 16 – 18 | `P:R` | Metraje Acumulado Pozo, Proyectado Cierre Acumulado y Meta Contractual Acumulada. |
| **Herramientas de Corte** | 19 – 25 | `S:Y` | Brocas (Marca, Serie, N°, Estado en V) y Escariadores (Marca, N°, Estado en Y). |
| **Consumo de Aditivos** | 26 – 50 | `Z:AX` | 8 familias de productos con menú desplegable dinámico (`Aditivos!$A$2:$H$17`) y unidades estrictas (`KG, LITRO`). |
| **Combustible Diésel** | 51 – 52 | `AY:AZ` | Cantidad de Petróleo Diésel D2 consumido en galones (GLN). |
| **Tiempos Operativos Directos** | 53 – 56 | `BA:BD` | Perforación efectiva, Rimado, Asentado/Retiro de Casing y Re-perforación. |
| **Tiempos de Mantenimiento** | 57 – 58 | `BE:BF` | Mantenimiento Preventivo (alerta amarilla > 1.0h) y Mantenimiento Correctivo. |
| **Actividades Operativas (Maniobras)** | 59 – 77 | `BG:BY` | 19 maniobras operativas (Lavado, Mezclado, Tuberías, Acondicionamiento, Desviación, Traslados, Anclajes, Cementación, etc.). |
| **Ensayos Geotécnicos e Hidrogeológicos** | 78 – 97 | `BZ:CS` | **Sección Especial**: Lefranc, Lugeon, SPT, Shelby, Freático, Air Lift, Slug Test, Casagrande, Cuerda Vibrante, Inclinómetros, Caudales y reservas SBO1-5. |
| **Actividades de Soporte y Seguridad** | 98 – 118 | `CT:DN` | 21 actividades internas (Desate, Limpieza 5S, Lama, Pozas, Estandarización, Charlas IPERC, Refrigerio, Traslado personal, etc.). |
| **Condiciones Cliente y Entorno Minero** | 119 – 145 | `DO:EO` | 27 eventos de cliente (Voladura, Falta agua, Energía, Ventilación, Scoop, Topografía, Clima, Inundación, etc.). |
| **Resumen y Consolidación de Horas** | 146 – 152 | `EP:EV` | Tiempo Total (EP = 12.0h), Tiempo Efectivo (EQ), Lost Time (ER), Mantenimiento (ES), SB Operativo (ET), SB Inoperativo (EU) y SB Cliente (EV). |
| **Metrajes Especiales** | 153 – 160 | `EW:FD` | Rimado Casing HWT/HQ (Desde, Hasta, Metraje, Acumulado) y Reperforación (Desde, Hasta, Metraje, Acumulado). |
| **Control de Horómetros** | 161 – 164 | `FE:FH` | Horómetro Inicial (FE), Horómetro Final (FF), Total Horas Guardia (FG) y Total Horas Acumulado Mes (FH). |
| **Bitácora y Observaciones** | 165 – 168 | `FI:FL` | Trabajos realizados mecánica, repuestos utilizados, descripción litológica y comentarios de campo. |

---

## 3. Lógica Matemática y Fórmulas Clave

1. **Propagación Inteligente de Profundidad (DESDE en Col F):**
   ```excel
   =IF(B26="","", IF(B26=B25, IF(ISNUMBER(G25), G25, 0), 0))
   ```
   *Al cambiar el nombre del sondaje en la Columna B, el DESDE reinicia automáticamente en 0.0 m.*

2. **Cálculo Seguro de Metraje (Col J):**
   ```excel
   =IF(G25="","", IF(AND(ISNUMBER(G25),ISNUMBER(F25)), IF(G25>=F25, G25-F25, 0), IF(ISNUMBER(G25), G25, 0)))
   ```

3. **Asignación de Personal por Grupo (Cols L, M, N):**
   ```excel
   =IF(I25=1,$H$8,IF(I25=2,$R$8,IF(I25=3,$X$8,IF(I25=4,$AG$8,IF(I25=5,$AM$8,"")))))
   ```

4. **Proyectado y Meta Acumulativos (Cols Q y R):**
   * Fila 25: `Q25 = $D$9/(($T$6-$T$5)+1)` y `R25 = $D$8/(($T$6-$T$5)+1)`.
   * Filas siguientes: `Q27 = Q25 + $Q$25` y `R27 = R25 + $R$25`.

5. **Balance Horario (Col EP):**
   ```excel
   =SUM(BA25:EO25)
   ```
   *Formato condicional verde si es exactamente 12.0h, rojo si difiere.*

6. **Fila 87 de Totales Generales:**
   * `J87`: `=SUM(J25:J86)` (Metros Totales).
   * `EP87..EV87`: Sumas de cada subtotal horario.
   * `AA87, AD87, AG87, AJ87, AM87, AP87, AS87, AV87, AY87`: Sumas de insumos y diésel.
   * `BA87..EO87`: Sumas individuales de cada una de las actividades del reporte.
