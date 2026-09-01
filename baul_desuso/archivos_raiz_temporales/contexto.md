# 🏛️ DOCUMENTO DE CONTEXTO TÉCNICO Y ARQUITECTURA INTEGRAL
## Sistema de Recopilación y Consolidación de Reportes Detallados de Perforación (Rockdrill Group)

Este documento contiene **toda la información de negocio, técnica, estructural y operacional** necesaria para que cualquier Inteligencia Artificial (LLM) o Ingeniero de Datos comprenda el ecosistema completo y explique **paso a paso cómo construir desde cero un consolidador de datos en Microsoft Excel (mediante Power Query M nativo o Python)** que unifique todos los reportes operativos en una única base de datos estructurada.

---

## 📁 1. Organización del Directorio y Fuentes de Datos

La estructura de carpetas física en disco (o en SharePoint / OneDrive) sigue una jerarquía estandarizada:

```
Rockdrill_Control_Operaciones/
├── 00_Control_Interno/
│   └── RD.402.P.01.F.04  Consolidado de Avance Setiembre.xlsx  <- Maestro de Control Interno (hojas diarias "26.08", "27.08", etc.)
├── Maestro_Maquinas/
│   └── Maestros_Maquinas.xlsx                                  <- Catálogo SAP y hoja 'Exepciones' de nombres de máquinas
├── CTR_AMERICANA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_AMERICANA.xlsx                    <- Libro con una pestaña por máquina de perforación
├── CTR_ANDAYCHAGUA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_Avance Detallado ANDAYCHAGUA SEPTIEMBRE.xlsx
├── CTR_CATALINA_HUANCA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01 Reporte Detallado de Avance CATALINA HUANCA - SETIEMBRE.xlsx
├── CTR_CERRO/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_CERRO.xlsx
├── CTR_CHUNGAR/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_CHUNGAR.xlsx
├── CTR_COBRIZA/
│   └── 02_Detallado/
│       └── Copia de RD.402.P.01.F.01_COBRIZA.xlsx
├── CTR_COLQUISIRI/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01 Reporte Detallado de Avance COLQUISIRI - SETIEMBRE.xlsx
├── CTR_CONDESTABLE/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_CONDESTABLE.xlsx
├── CTR_CUCULI/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_CUCULI.xlsx
├── CTR_INMACULADA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_Reporte Detallado de Avance INMACULADA SETIEMBRE.xlsx
├── CTR_LA_ESTRELLA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_Reporte detallado_Setiembre_LA ESTRELLA.xlsx
├── CTR_MOROCOCHA/
│   └── 02_Detallado/
│       └── Copia de RD.402.P.01.F.01_DETALLADO MOROCOCHA.xlsx
├── CTR_RAURA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_REPORTE DETALLADO RAURA.xlsx
├── CTR_SAN_CRISTOBAL/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01REPORTE DETALLADO SETIEMBRE_SAN_CRISTOBAL .xlsx
├── CTR_TAMBOJASA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01 Avance Detallado - TAMBOJASA.xlsx
├── CTR_TICLIO/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_TICLIO - SETIEMBRE.xlsx
├── CTR_YAULIYACU/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_YAULIYACU.xlsx
├── CTR_YAURICOCHA/
│   └── 02_Detallado/
│       └── RD.402.P.01.F.01_YAURICOCHA.xlsx
├── CTR_CAPITANA/   <- EXCLUIDO POR REGLA DE NEGOCIO (Contrato no operativo estándar)
└── CTR_COLQUIJIRCA/ <- EXCLUIDO POR REGLA DE NEGOCIO (Formato no homologado)
```

### Reglas de Exclusión de Carpetas y Hojas:
1. **Contratos Excluidos:** Se omiten carpetas con nombres `CTR_CAPITANA` y `CTR_COLQUIJIRCA`.
2. **Hojas No Operativas a Ignorar:** Dentro de cada libro Excel existen pestañas administrativas que **NO** corresponden a máquinas y deben descartarse obligatoriamente:
   - `ADITIVOS`, `GENERAL`, `LISTAS`, `Tiempos`, `TIEMPOS`, `RESUMEN`, `GRAFICOS`, `MAESTRO`, `PARAMETROS`, `GLOSARIO`.
3. **Hojas Ocultas:** Se deben ignorar las pestañas ocultas (`Hidden` o `VeryHidden`).
4. **Hojas Válidas:** Cada pestaña restante corresponde al nombre de una máquina de perforación (ej. `XRD50U-002`, `LM90U-001`, `XRD150USS-004`).

---

## 📐 2. Anatomía de la Plantilla Excel del Reporte Detallado (`RD.402.P.01.F.01`)

Cada pestaña de máquina tiene una estructura física fija y estandarizada en formato de **168 columnas** (desde la Columna `A` hasta la Columna `FL`):

```
+-------------------------------------------------------------------------------------------------------------------------------+
| Filas 1 a 22: ENCABEZADO ADMINISTRATIVO (Logos corporativos, datos del contrato, cliente, cuadrilla del mes, metas)         |
+-------------------------------------------------------------------------------------------------------------------------------+
| Fila 23 (Índice 22): NIVEL 1 DE CABECERAS (Celdas Combinadas por Bloques: "ADITIVOS", "MANTENIMIENTO", "HOROMETRO", etc.)   |
+-------------------------------------------------------------------------------------------------------------------------------+
| Fila 24 (Índice 23): NIVEL 2 DE CABECERAS (Subtítulos: "PRODUCTO", "CANT.", "UND.", "DESDE", "HASTA", "METRAJE", "TOTAL")  |
+-------------------------------------------------------------------------------------------------------------------------------+
| Fila 25 (Índice 24): PRIMERA FILA DE DATOS OPERATIVOS (Guardia 1 / Turno Día del 26 de mes anterior)                         |
| Fila 26 en adelante: Registros de guardias diarias (Día / Noche) y tramos de perforación                                      |
+-------------------------------------------------------------------------------------------------------------------------------+
| Filas Finales: PIE DE PÁGINA Y TOTALES (Celdas con texto "TOTAL", "TOTAL GENERAL", "RESUMEN", etc. -> DEBEN FILTRARSE)       |
+-------------------------------------------------------------------------------------------------------------------------------+
```

---

## 📋 3. Catálogo Exhaustivo de las 168 Columnas Canónicas (Cols A a FL)

La plantilla posee exactamente **168 columnas divididas en 17 bloques funcionales**:

| N° | Col Excel | Nombre Canónico Unificado | Bloque Funcional | Tipo de Dato |
| :---: | :---: | :--- | :--- | :---: |
| **1** | `A` | `FECHA` (DÍAS) | 1. Identificación y Sondaje | Fecha (`YYYY-MM-DD`) |
| **2** | `B` | `SONDAJE` (NOMBRE) | 1. Identificación y Sondaje | Texto |
| **3** | `C` | `PROFUNDIDAD` | 1. Identificación y Sondaje | Decimal |
| **4** | `D` | `LINEA` | 1. Identificación y Sondaje | Texto (HQ, NQ, BQ, etc.) |
| **5** | `E` | `INCLINACIÓN` | 1. Identificación y Sondaje | Decimal (grados) |
| **6** | `F` | `DESDE` | 2. Avance Diario y Cuadrilla | Decimal (metros) |
| **7** | `G` | `HASTA` | 2. Avance Diario y Cuadrilla | Decimal (metros) |
| **8** | `H` | `TURNO (A=1;B=2)` | 2. Avance Diario y Cuadrilla | Texto (A / B / 1 / 2) |
| **9** | `I` | `GRUPO` | 2. Avance Diario y Cuadrilla | Texto (1..5) |
| **10** | `J` | `METRAJE` | 2. Avance Diario y Cuadrilla | Decimal ($HASTA - DESDE$) |
| **11** | `K` | `HORAS EXTRAS` | 2. Avance Diario y Cuadrilla | Decimal |
| **12** | `L` | `PERFORISTA` | 2. Avance Diario y Cuadrilla | Texto |
| **13** | `M` | `AYUDANTE 1` | 2. Avance Diario y Cuadrilla | Texto |
| **14** | `N` | `AYUDANTE 2` | 2. Avance Diario y Cuadrilla | Texto |
| **15** | `O` | `TOTAL metraje del dia` | 2. Avance Diario y Cuadrilla | Decimal |
| **16** | `P` | `ACUMULADO` | 3. Comparativo y Metas | Decimal |
| **17** | `Q` | `PROYECTADO` | 3. Comparativo y Metas | Decimal |
| **18** | `R` | `META` | 3. Comparativo y Metas | Decimal |
| **19** | `S` | `MARCA BROCA` | 4. Herramientas de Corte | Texto |
| **20** | `T` | `SERIE BROCA` | 4. Herramientas de Corte | Texto |
| **21** | `U` | `Nº BROCA` | 4. Herramientas de Corte | Texto |
| **22** | `V` | `ESTADO DE LA BROCA` | 4. Herramientas de Corte | Texto (N/U/D/P) |
| **23** | `W` | `MARCA ESCARIADOR` | 4. Herramientas de Corte | Texto |
| **24** | `X` | `Nº ESCARIADOR` | 4. Herramientas de Corte | Texto |
| **25** | `Y` | `ESTADO DEL ESCARIADOR`| 4. Herramientas de Corte | Texto |
| **26-28** | `Z:AB` | `BENTONITA - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **29-31** | `AC:AE` | `PAC - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **32-34** | `AF:AH` | `POLIMERO - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **35-37** | `AI:AK` | `LUBRICANTES - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **38-40** | `AL:AN` | `CONTROLADOR DE PH Y DUREZA - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **41-43** | `AO:AQ` | `INHIBIDORES - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **44-46** | `AR:AT` | `ESTABILIZADOR - PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **47-50** | `AU:AX` | `OTROS - CLASIFICACIÓN`, `PRODUCTO`, `CANT.`, `UND.` | 5. Consumo de Aditivos | Texto / Decimal / Texto |
| **51-52** | `AY:AZ` | `PETROLEO - CANT.`, `PETROLEO - GLN` | 6. Combustible Diésel | Decimal / Texto |
| **53-56** | `BA:BD` | `Perforación`, `Rimado`, `Asentado / Retiro de revestimiento (Casing)`, `RePerforación` | 7. Tiempos Operativos Directos | Decimal (Horas) |
| **57-58** | `BE:BF` | `Preventivo`, `Correctivo` | 8. Tiempos Mantenimiento | Decimal (Horas) |
| **59-77** | `BG:BY` | 19 Maniobras: `Lavado de sondaje`, `Mezclado de lodos`, `Manipulación de tuberías`, `Acondicionamiento`, `Cambio de línea`, `Recuperación sondaje`, `Atrapamiento`, `Descarga/carga tuberías`, `Fallas/fracturados`, `Medición Desviación`, `Traslado cámaras`, `Cambio punto`, `Anclado`, `Perno anclaje`, `Cementación perno`, `Cementado sondaje`, `Packer`, `Sellado`, `Lechada cemento` | 9. Maniobras Operativas (Stand By Operativo) | Decimal (Horas) |
| **78-97** | `BZ:CS` | 20 Ensayos e Instrumentación: `Ensayo Lefranc`, `Ensayo Lugeon`, `Prueba SPT`, `Prueba Shelby`, `Pruebas Geotécnicas`, `Nivel freático`, `Air Lift`, `Slug Test`, `Piezómetro Casagrande`, `Cuerda vibrante`, `Inclinómetro`, `Multinivel`, `Presión/Caudal`, `Lectura inclinómetro`, `Lecturas cuerda vibrante`, `SBO1`, `SBO2`, `SBO3`, `SBO4`, `SBO5` | 10. Ensayos Geotécnicos (Stand By Operativo) | Decimal (Horas) |
| **98-118**| `CT:DN` | 21 Soporte/Seguridad: `Desate`, `Orden y limpieza (5S)`, `Lama`, `Pozas`, `Estandarización`, `Red agua`, `Instalación máquina`, `Traslado accesorios`, `Auditoría interna`, `Charla IPERC`, `Espera repuestos`, `Espera materiales`, `Traslado personal`, `Refrigerio`, `Falta personal`, `Fiestas`, `Pare RD`, `SBI1`, `SBI2`, `SBI3`, `SBI4` | 11. Soporte y Seguridad (Stand By Inoperativo) | Decimal (Horas) |
| **119-145**|`DO:EO` | 27 Eventos Cliente: `Voladura`, `Falta agua`, `Falta energía`, `Falta ventilación`, `Falta servicios`, `Espera Orden`, `Espera programa`, `Espera cámara`, `Espera sostenimiento`, `Espera scoop`, `Marcado punto`, `Topografía`, `Grúa`, `Ensayos cliente`, `Auditoría externa`, `Capacitación`, `Habilitación`, `Orden cliente`, `Clima`, `Inundación`, `Estrés térmico`, `Sismo`, `Conflicto social`, `SBC1`, `SBC2`, `SBC3`, `SBC4` | 12. Entorno Cliente (Stand By Cliente) | Decimal (Horas) |
| **146-152**|`EP:EV` | `TIEMPO TOTAL` (12.0h), `TIEMPO EFECTIVO - OPERATIVO`, `LOST TIME`, `Mantenimiento`, `Stand By Operativo`, `Stand By Inoperativo`, `Stand By Cliente` | 13. Resumen y Consolidación de Horas | Decimal (Horas) |
| **153-156**|`EW:EZ` | `RIMADO CASING HWT/HQ - DESDE`, `HASTA`, `METRAJE`, `TOTAL` | 14. Rimado Casing | Decimal (Metros) |
| **157-160**|`FA:FD` | `RE-PERFORACIÓN - DESDE`, `HASTA`, `METRAJE`, `TOTAL` | 15. Re-Perforación | Decimal (Metros) |
| **161-164**|`FE:FH` | `HOROMETRO - DESDE`, `HASTA`, `ACUMULADO`, `TOTAL` | 16. Control Horómetros | Decimal (Horas Motor) |
| **165-168**|`FI:FL` | `BITACORA - TRABAJOS REALIZADOS`, `BITACORA - REPUESTOS UTILIZADOS`, `DESCRIPCIÓN LITOLÓGICA`, `COMENTARIOS` | 17. Bitácora y Observaciones | Texto Descriptivo |

---

## ⚙️ 4. Reglas de Transformación y Desafíos Técnicos

1. **Tratamiento de Celdas Combinadas en Fecha y Sondaje:**
   - La fecha en la Columna A (`FECHA`) usualmente se escribe en la primera fila del día y las filas subsiguientes del mismo día quedan en blanco por combinación visual. **Se debe aplicar `FillDown` por hoja**.
   - El código del sondaje en la Columna B (`SONDAJE`) puede estar combinado a lo largo de múltiples filas. **Se debe aplicar `FillDown` y `FillUp`**.
2. **Filtrado Riguroso de Filas No Operativas:**
   - Se deben descartar filas vacías o que contengan en Fecha o Sondaje textos de resumen/pie de página como `TOTAL`, `TOTAL GENERAL`, `RESUMEN`, `PROMEDIO`, `SUMA`, `TOTAL AVANCE` o que comiencen con `>`.
3. **Ciclo Operativo Minero (Ciclo del 26 al 25):**
   - El mes operativo minero comprende desde el día **26 del mes anterior** hasta el día **25 del mes en curso**.
   - Si la plantilla base trajo mes 7 para los días 26..31 al iniciar el ciclo de Setiembre, se normaliza al mes correspondiente (Agosto).
4. **Asignación Determinista de Turnos Operativos (A = Día / B = Noche):**
   - Cada día de operación posee 2 guardias de 12 horas.
   - En días de 2 filas: Fila 1 = Turno `A` (Día), Fila 2 = Turno `B` (Noche).
   - En días de $\ge 3$ filas (multi-sondaje): Se detecta la transición por cambio de `GRUPO` rotativo, cambio de `PERFORISTA` o reparto secuencial.
5. **Clave Única de Conciliación 1-a-1:**
   $$\text{ID\_CLAVE\_UNICA} = \text{YYYYMMDD} - \text{MAQUINA} - \text{TURNO}$$
   Esta clave permite conciliar exactamente contra **Control Interno (`RD.402.P.01.F.04`)**.
6. **Mapeo de Nombres de Máquina (Excepciones SAP):**
   - Algunas pestañas tienen nombres locales que difieren del código oficial de Control Interno (ej. en Chungar, la hoja `XRD90U-03` corresponde a la máquina oficial `XRD90U-021`). Se debe aplicar la matriz de homologación del archivo `Maestro_Maquinas.xlsx`.

---

## 🚫 5. Por qué las Implementaciones Comunes de Power Query Fallan y Cómo Evitarlo

| Error Típico en Power Query | Causa Raíz | Solución Definitiva |
| :--- | :--- | :--- |
| **`Formula.Firewall` / Error de Privacidad** | Invocar `Excel.Workbook([Content])` dentro de una función de fila sobre una tabla obtenida por `Folder.Files`. | Abrir `Excel.Workbook([Content])` una sola vez en la consulta principal y pasar la tabla `[Data]` ya abierta a la función. |
| **Columnas Dispersas con Nulos (`Table.Combine` roto)** | Intentar combinar dinámicamente cabeceras de Fila 23 y 24 cuando distintas hojas tienen diferencias de espacios o celdas vacías. | Tomar las primeras 168 columnas (`Column1` a `Column168`) y renombrarlas con el array fijo de 168 nombres oficiales. **Todas las hojas producen el mismo esquema exacto**. |
| **Error en `TablasValidas` / `Table.Combine`** | Una hoja vacía o corrupta retorna un valor `[Error]` que hace explotar `Table.Combine`. | Envolver la función en un bloque `try ... otherwise #table({}, {})` para ignorar hojas corruptas sin frenar el flujo. |

---

## 🎯 6. Salida Requerida: Base de Datos Unificada

El resultado debe ser una **Tabla de Excel Oficial (ListObject)** con:
- **174 columnas en total:** Las **168 columnas canónicas de la A a la FL** + **6 metadatos** (`CTR`, `MAQUINA`, `TURNO_ESTANDAR`, `ID_CLAVE_UNICA`, `ARCHIVO ORIGEN`, `HOJA DE TRABAJO ORIGEN`).
- Lista para ser consumida directamente por **Power BI**, tablas dinámicas o scripts analíticos.
