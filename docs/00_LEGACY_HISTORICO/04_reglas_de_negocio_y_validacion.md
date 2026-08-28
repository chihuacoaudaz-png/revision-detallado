# 🛡️ 04. Reglas de Negocio, Fórmulas y Validación de Datos

Este documento define las reglas de integridad matemática y validaciones que debe cumplir el nuevo reporte detallado **RD.402.P.01.F.01**.

---

## 1. Reglas de Integridad de Metrajes y Sondajes

1. **Monotonía de Profundidad:**
   $$\text{HASTA} \ge \text{DESDE} \ge 0$$
2. **Cálculo de Metraje por Tramo:**
   $$\text{METRAJE X GUARDIA} = \text{HASTA} - \text{DESDE}$$
3. **Control de Turno:**
   - La suma de horas de actividades por fila/guardia debe ser coherente con la jornada ($12.0\text{ hrs}$ por turno completo o $8.0\text{ hrs}$ según régimen).
4. **Validación de Brocas y Escariadores:**
   - Si se reporta metraje de perforación $> 0.00\text{ m}$, debe existir obligatoriamente el número de serie o correlativo de broca (`Nº BROCA`).
5. **Justificación Obligatoria de Tiempos `Otros*`:**
   - Si se registra tiempo en `OTROS RD` u `OTROS CLIENTE`, la columna `COMENTARIOS` es obligatoria con un mínimo de 10 caracteres explicativos.

---

## 2. Fórmulas Integradas en la Plantilla Excel

| Celda / Campo | Fórmula Excel Estándar | Comportamiento |
| :--- | :--- | :--- |
| `METRAJE X GUARDIA` | `=IF(AND(ISNUMBER(N25),ISNUMBER(M25)), N25-M25, 0)` | Calcula automáticamente el metraje restando Desde de Hasta |
| `TOTAL HORAS` | `=SUM(BE25:EJ25)` | Suma horizontal de todas las columnas de tiempo de la fila |
| `METRAJE X DÍA` | `=SUMIFS(Q:Q, H:H, H25, D:D, D25)` | Suma diaria automática por máquina y fecha |
| `METROS ACUMULADOS` | `=SUMIFS(Q:Q, I:I, I25, H:H, "<="&H25)` | Acumulado progresivo del pozo |
