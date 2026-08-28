# 📘 Manual de Usuario: Reporte Detallado de Avance (RD.402.P.01.F.01)
### *La Guía Definitiva y Práctica para la Administradora de Contrato*
**Rockdrill Group — Sistema Integrado de Gestión (SIG) & Control de Operaciones**

---

## 🌟 1. Introducción y Propósito

¡Bienvenida a la versión renovada del **Reporte Detallado de Avance**!

Este formato ha sido rediseñado pensando en hacer tu día a día más ágil, cómodo y seguro. Se han incorporado fórmulas inteligentes que calculan automáticamente los avances, asignan cuadrillas, propagan profundidades y horómetros, y validan que tus horas cuadren siempre a la perfección.

> **El Secreto del Éxito:** La plantilla hace el 80% del trabajo pesado por ti (sumas, acumulados, nombres de cuadrilla, fechas y metros). Tu rol principal es registrar los datos operativos de los reportes diarios de los perforistas y verificar los semáforos visuales.

---

## 🏗️ 2. Estructura General del Libro de Trabajo

Cada archivo de tu contrato (`RD.402.P.01.F.01_[CONTRATO].xlsx`) contiene:

1. **Pestañas de Máquinas (Nombres SAP):**
   * Cada máquina asignada a tu proyecto tiene su propia pestaña (ej. `XRD90USS-004`, `LF90DST-002`, etc.).
   * En ellas se realiza todo el trabajo diario de digitación.
2. **Hojas Ocultas de Soporte (`Aditivos` y `Listas`):**
   * Contienen los catálogos oficiales de aditivos, líneas de perforación y estados de herramientas.
   * Están ocultas para no saturar tu barra de pestañas, pero alimentan los menús desplegables de todas las máquinas.
3. **Libro 100% Desbloqueado:**
   * Tienes total libertad para copiar, pegar, ajustar y revisar tus datos sin restricciones de contraseñas.

---

## 🚀 3. Paso a Paso: Apertura del Mes

Al iniciar cada mes operativo, solo necesitas configurar la cabecera de cada máquina una sola vez:

```
[1. Fechas del Mes] ---> [2. Nombre del Mes] ---> [3. Registrar Cuadrillas] ---> [4. Metas y Proyección]
 (T5 Inicio / T6 Fin)      (Automático en W5)       (Grupos 1 al 5 en Cabecera)      (D8 Meta / D9 Proy.)
```

### Paso 1: Configurar las Fechas del Período
* En la celda **`T5`**, ingresa la fecha de inicio del mes (ej. `01/08/2026` o `26/07/2026`).
* En la celda **`T6`**, ingresa la fecha de fin del mes (ej. `31/08/2026` o `25/08/2026`).
* *Efecto inmediato:* La celda **`W5`** mostrará automáticamente el nombre del mes en **MAYÚSCULAS** (ej. `AGOSTO`).

### Paso 2: Registrar el Personal en las Tarjetas de Grupo (Filas 8 a 15)
En la parte superior encontrarás las casillas para registrar a tu personal según el grupo de trabajo:
* **Grupo 1:** Perforista en **`H8`**, Ayudante 1 en **`H12`**, Ayudante 2 en **`H15`**.
* **Grupo 2:** Perforista en **`R8`**, Ayudante 1 en **`R12`**, Ayudante 2 en **`R15`**.
* **Grupo 3:** Perforista en **`X8`**, Ayudante 1 en **`X12`**, Ayudante 2 en **`X15`**.
* **Grupo 4:** Perforista en **`AG8`**, Ayudante 1 en **`AG12`**, Ayudante 2 en **`AG15`**.
* **Grupo 5:** Perforista en **`AM8`**, Ayudante 1 en **`AM12`**, Ayudante 2 en **`AM15`**.

> Al llenar estos nombres en la cabecera, la plantilla colocará automáticamente los nombres del perforista y ayudantes en las filas de abajo cada vez que selecciones el número de grupo.

---

## 📝 4. Guía de Llenado Diario por Guardia (Filas 25 a 86)

Cada día del mes está compuesto por **dos filas continuas**:
* **Fila Impar (ej. 25, 27, 29...):** Turno Día (**Turno A**).
* **Fila Par (ej. 26, 28, 30...):** Turno Noche (**Turno B**), identificada con un fondo sombreado suave para facilitar la lectura.

```
+----+------------+---------+-------+-------+-------+-------+-------+-------------------+
| Fila |   Fecha    | Sondaje | Línea | Desde | Hasta | Turno | Grupo |    Perforista     |
+----+------------+---------+-------+-------+-------+-------+-------+-------------------+
| 25 | 01/08/2026 | U-105   | HQ    |   0.0 |  18.5 | A     |     1 | JUAN PEREZ        |
| 26 |            | U-105   | HQ    |  18.5 |  36.0 | B     |     2 | CARLOS RODRIGUEZ  |
+----+------------+---------+-------+-------+-------+-------+-------+-------------------+
```

---

### 🔹 Sección 1: Datos Generales de la Guardia (Columnas A a N)

1. **Fecha (Columna A):**
   * Viene formulada automáticamente desde la celda de inicio `$T$5`. No necesitas digitarla.
2. **Sondaje (Columna B):**
   * Escribe el código del pozo (ej. `DDH-001`, `S-105`).
   * En el turno noche (fila par), el nombre del sondaje se copia automáticamente del turno día.
3. **Línea / Diámetro (Columna D):**
   * Selecciona del desplegable: `HQ`, `NQ`, `BQ`, `PQ`, `W80` o `W100`.
4. **Profundidad Desde (Columna F) y Hasta (Columna G):**
   * **`DESDE` (F):** Se autocompleta con el valor `HASTA` de la guardia anterior si es el mismo pozo. Si cambias de pozo, se reinicia en `0.0`.
   * **`HASTA` (G):** Digita la profundidad alcanzada al final de la guardia.
   * ⚠️ **Alerta de Inversión:** Si por error digitas un `Hasta` menor que el `Desde`, la celda se pintará de **ROJO** para avisarte.
5. **Turno (Columna H):**
   * Viene predeterminado como **`A`** (Día) y **`B`** (Noche). Desplegable con opciones estrictas.
6. **Grupo (Columna I):**
   * Selecciona el grupo que trabajó (**`1`, `2`, `3`, `4`, `5`**).
7. **Metraje de Guardia (Columna J):**
   * Se calcula automáticamente: `Hasta - Desde`. Si no hubo perforación, muestra 0.
8. **Horas Extras (Columna K):**
   * Desplegable con opciones `0`, `1`, `2`, `3`, `4` si el personal realizó sobretiempo autorizado.
9. **Personal de Cuadrilla (Columnas L, M, N):**
   * Se llenan **automáticamente** según el Grupo seleccionado en la columna `I`.
   * *¿Hubo un suplente o apoyo externo?* Puedes sobreescribir cualquier celda a mano directamente.

---

### 🔹 Sección 2: Acumulados y Metas (Columnas O a R)

* **Total Metraje Día (Columna O):** Suma automáticamente el avance del Turno A + Turno B del día.
* **Comparativo Acumulado (Columna P):** Suma progresivamente el avance acumulado del mes día a día.
* **Proyectado (Columna Q):**
  * Inicia en `Q25 = $D$9 / Días del Mes` y acumula la cuota diaria proyectada.
* **Meta (Columna R):**
  * Inicia en `R25 = $D$8 / Días del Mes` y acumula la meta diaria del contrato.

---

### 🔹 Sección 3: Control de Brocas y Escariadores (Columnas T a Y)

| Columna | Nombre | Tipo de Campo | Instrucción de Llenado |
| :---: | :--- | :---: | :--- |
| **T** | Serie Broca | Texto / Código | Digita el número de serie de la broca. |
| **U** | N° Broca | Número / Texto | Digita el correlativo interno de la broca. |
| **V** | **Estado Broca** | **Desplegable** | Selecciona: `NUEVO`, `USADO`, `DESCARTADO`, `PULIDO`. |
| **W** | Marca Escariador | Texto | Digita la marca del escariador (ej. Rockdrill, Boart, Fordia). |
| **X** | N° Escariador | Número / Texto | Digita el correlativo interno del escariador. |
| **Y** | **Estado Escariador**| **Desplegable** | Selecciona: `NUEVO`, `USADO`, `DESCARTADO`. |

---

### 🔹 Sección 4: Consumo de Aditivos (Columnas Z a AW)

El reporte contiene 8 familias de aditivos (`Bentonita`, `PAC`, `Polímero`, `Lubricantes`, `Controlador PH`, `Inhibidores`, `Estabilizador`, `Otros`):
1. **Columna Producto (Z, AC, AF, AI, AL, AO, AR, AU):**
   * Menú desplegable con los nombres comerciales oficiales (ej. `MAX BENTONITE`, `SUPER GEL`, `MAX LUBE`).
2. **Columna Cantidad (AA, AD, AG, AJ, AM, AP, AS, AV):**
   * Digita la cantidad física consumida en la guardia.
3. **Columna Unidad (AB, AE, AH, AK, AN, AQ, AT, AW):**
   * Menú desplegable restringido estrictamente a **`KG`** o **`LITRO`**.

---

### 🔹 Sección 5: Distribución de Horas y Tiempos (Columnas BA a EO)

Esta es la sección de tiempos de la guardia (12.0 horas por turno):

> **La Regla de Oro de las 12.0 Horas (Columna EP):**
> La suma total de horas distribuidas en la fila debe ser **exactamente 12.0 horas**.
> * 🟢 **Verde Suave:** Cuando la celda `EP` suma exactamente `12.0`. ¡Todo cuadra perfecto!
> * 🔴 **Rojo Claro:** Si la celda `EP` suma un valor distinto (ej. `11.5` o `12.5`). Te avisa inmediatamente para que corrijas el tiempo faltante o sobrante.

#### ⚠️ Alerta de Mantenimiento Preventivo (Columna BE / Col 57):
* Si registras más de **1.0 hora** en `Mantenimiento Preventivo`, la celda se resaltará automáticamente en **AMARILLO SUAVE**.
* *Propósito:* Recordarte que un mantenimiento preventivo mayor a 1 hora debe contar con el sustento del mecánico de turno.

---

### 🔹 Sección 6: Control de Horómetros (Columnas FE a FG)

* **Horómetro Desde (Columna FE):** Se autopropaga desde el `Horómetro Hasta` del turno anterior.
* **Horómetro Hasta (Columna FF):** Digitas el horómetro final del motor de la máquina.
* **Total Horómetro (Columna FG):** Se calcula automáticamente (`FF - FE`).
* ⚠️ **Alerta:** Si ingresas un horómetro final menor al inicial, la celda se pintará de **ROJO**.

---

## 🎯 5. Casos Prácticos y Situaciones Cotidianas

### 📌 Caso 1: Guardia Normal de Perforación sin Inconvenientes
* **Escenario:** Turno Día, se perforó de 0.0m a 24.5m en línea HQ.
* **Acción:**
  1. Digita el Sondaje `DDH-01` en `B25`.
  2. Selecciona Línea `HQ` en `D25`.
  3. `Desde` (`F25`) inicia en `0.0`. Digita `24.5` en `Hasta` (`G25`).
  4. Selecciona Grupo `1` en `I25` $\to$ Se completan perforista y ayudantes automáticamente.
  5. En `V25`, selecciona Estado Broca `NUEVO`.
  6. Distribuye las 12.0 horas: `10.5` en Perforación (`BA25`), `1.0` en Charla de Seguridad (`BI25`), `0.5` en Engrase (`BF25`).
  7. Revisa que `EP25` se pinte de **VERDE (12.0)**.
  8. Ingresa Horómetro Hasta en `FF25`.

---

### 📌 Caso 2: Se Termina un Sondaje y Empieza Otro en la Misma Guardia
* **Escenario:** En la misma guardia de día, se perforaron los últimos 5 metros del pozo `S-101` (de 95.0 a 100.0m) y luego se movió la máquina al nuevo pozo `S-102` (de 0.0 a 8.0m).
* **Solución:**
  1. Registra en la fila principal del día el sondaje `S-102` con su metraje respectivo.
  2. En la distribución de tiempos, asigna las horas de perforación correspondientes a cada labor y las horas de traslado/instalación en `Traslado de Equipo` (`BL`) e `Instalación` (`BM`).
  3. Si requieres detallar ambos pozos por separado, puedes insertar una fila adicional y copiar las fórmulas de la fila superior (las fórmulas están preparadas con referencias relativas seguras).

---

### 📌 Caso 3: Guardia de Standby o Paralización (0.0 Metros)
* **Escenario:** No se pudo perforar por falta de agua del cliente durante toda la noche (12.0 horas).
* **Acción:**
  1. `Sondaje` y `Línea` se mantienen igual.
  2. `Hasta` se deja igual al `Desde` o vacío $\to$ `Metraje Guardia (J)` mostrará `0.0`.
  3. Selecciona el Grupo que estuvo de guardia.
  4. En la sección de tiempos, registra `12.0` en **Standby Cliente: Falta de Agua** (`DO` / Col 119).
  5. Verifica que `EP26` muestre **VERDE (12.0)**.
  6. Como el motor estuvo apagado, el Horómetro Hasta es igual al Desde $\to$ Horas motor = `0.0`.

---

### 📌 Caso 4: Reemplazo o Rotación de Personal en Guardia
* **Escenario:** El perforista habitual del Grupo 1 tuvo descanso médico y fue cubierto por otro perforista.
* **Acción:**
  1. Selecciona Grupo `1` en `I25` para que traiga los ayudantes del grupo.
  2. Haz clic en la celda del Perforista (`L25`) y escribe directamente el nombre del nuevo perforista.
  3. La plantilla aceptará tu edición sin alterar las fórmulas de las demás filas ni romper las tarjetas de resumen.

---

## 📖 6. Glosario Simple de Columnas y Términos

Para facilitar la consulta rápida de cada sección de la plantilla:

### 1. Cabecera y Resumen General
* **Meta (D8):** Metraje total programado para la máquina en el mes.
* **Proyectado (D9):** Estimación de cierre de mes basada en el ritmo diario actual.
* **Días Transcurridos (D10):** Cantidad de días trabajados con registro de grupo.
* **Metraje Acumulado (D11):** Suma total de metros perforados en el mes.
* **Promedio m/h (D12):** Metros perforados por cada hora efectiva de perforación.
* **Tiempo Efectivo (D15):** Suma total de horas donde la broca estuvo cortando roca.
* **Lost Time (D16):** Suma de horas no operativas (mantenimientos, averías, esperas).
* **Total Horómetro (D20):** Horas totales de funcionamiento del motor de la máquina.

### 2. Guardia y Producción
* **Sondaje:** Código único que identifica el pozo o taladro en perforación.
* **Línea:** Diámetro de las barras y corona de perforación (`HQ`, `NQ`, etc.).
* **Desde / Hasta:** Profundidad inicial y final alcanzada en la guardia (en metros).
* **Metraje Guardia:** Metros lineales perforados en el turno (`Hasta - Desde`).
* **Turno:** `A` para turno de día (7:00 a 19:00) y `B` para turno de noche (19:00 a 7:00).
* **Grupo:** Número del 1 al 5 asignado a la cuadrilla de trabajo.
* **Horas Extras (HE):** Cantidad de horas trabajadas adicionales a las 12h de turno.

### 3. Herramientas y Consumibles
* **Estado de Broca / Escariador:**
  * `NUEVO`: Herramienta sin uso previo que ingresa al pozo por primera vez.
  * `USADO`: Herramienta con desgaste operativo pero aún apta para seguir perforando.
  * `DESCARTADO`: Herramienta que cumplió su vida útil o sufrió rotura irreparable.
  * `PULIDO`: Broca que fue afilada para recuperar su matriz de diamante.
* **Familias de Aditivos:** Productos químicos y lodos utilizados para estabilizar las paredes del pozo, lubricar la sarta y evacuar los detritos (bentonitas, polímeros, lubricantes de barra, etc.).

### 4. Categorías de Tiempos (Horas)
* **Tiempo Operativo (BA a BD):** Horas directas de perforación, rimado, maniobra de barras y recuperación de testigos.
* **Mantenimiento (BE a BF):** Tiempo dedicado a revisiones preventivas del equipo y lubricación.
* **Standby Operativo (BG a CS):** Actividades de soporte normales de la operación (charla de seguridad, inspección de labor, mediciones de pozo, traslados, armados).
* **Standby Inoperativo (CT a DN):** Paralizaciones internas atribuibles a fallas de equipo, reparaciones mecánicas o espera de repuestos.
* **Standby Cliente (DO a EO):** Paralizaciones causadas por el cliente minero (falta de agua, falta de energía, vía bloqueada, falta de frente, esperas geológicas).

---

## ❓ 7. Preguntas Frecuentes (FAQ)

**1. ¿Por qué una celda de tiempo me aparece en rojo?**  
R: Porque la suma de las horas de esa fila (Columna `EP`) es diferente de 12.0 horas. Revisa las horas ingresadas en esa fila hasta que sumen exactamente 12.0.

**2. ¿Por qué el Desde se puso en 0.0 automáticamente?**  
R: Porque cambiaste el nombre del Sondaje respecto a la fila anterior. La plantilla detecta que es un pozo nuevo y reinicia la profundidad a 0.0m.

**3. ¿Cómo puedo ver las hojas de Aditivos o Listas?**  
R: Las hojas están ocultas para simplificar la vista. Si requieres verlas, puedes hacer clic derecho sobre cualquier pestaña de máquina y seleccionar *Mostrar / Unhide*.

**4. ¿Qué pasa si una guardia no perfora nada de metros?**  
R: Dejas la celda `Hasta` en blanco o igual al `Desde`. El metraje de guardia será `0.0` y no generará ningún error `#VALOR!`. Solo asegúrate de registrar las 12.0 horas en los tiempos de standby correspondientes.

---
*Manual elaborado por el equipo de Control de Operaciones & Business Intelligence para el SIG de Rockdrill Group.*
