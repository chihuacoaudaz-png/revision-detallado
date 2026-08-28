# 📑 Informe Integral de Exploración Técnica: Fuentes de Datos, Control Interno, Motor de Reconciliación y Reportes Ejecutivos PDF

**Proyecto**: Rockdrill Group Detailed Reporting Pipeline  
**Agente**: Survey Explorer 3  
**Fecha de Elaboración**: 2026-08-19  
**Ruta de Trabajo**: `C:\Proyectos Python\Detallados\.agents\survey_explorer_3`  
**Ruta Base del Proyecto**: `C:\Proyectos Python\Detallados`  

---

## Executive Summary

El presente documento constituye la investigación técnica y análisis arquitectural exhaustivo sobre los cuatro pilares fundamentales del sistema de reportería de **Rockdrill Group**:
1. **Mecanismos de Descarga Automatizada desde OWA**: Arquitectura Playwright, gestión de sesiones multiusuario sin credenciales hardcodeadas, selectores bilingües, estrategia de descarga de 4 niveles y auditoría de descargas.
2. **Compilación de Control Interno (`RD.402.P.01.F.04`)**: Estructura de pestañas diarias (`dd.mm`), algoritmo de parada adaptativo, filldown de CTR, estandarización de máquinas SAP y asignación determinística de turnos `A`/`B`.
3. **Motor de Reconciliación y Auditoría Turno a Turno**: Cruce Full Outer Join por `ID_CLAVE_UNICA` (`{FECHA}-{MAQUINA}-{TURNO}`), taxonomía y categorización de causas de discrepancia (inversiones de turno, faltantes de origen, registros históricos en cero y ajustes de campo), y métricas de cuadratura ($\ge 96\%$ global y $100\%$ en contratos con reporte disponible).
4. **Arquitectura de Reportes Ejecutivos en PDF**: Diseño editorial para audiencia no técnica (Gerencia, Operaciones, Administradoras), estructuración de las 156 columnas canónicas en 13 bloques funcionales, y selección tecnológica de ReportLab vs WeasyPrint / matplotlib.

---

## 1. Mecanismos de Descarga Automatizada OWA (`descargar_detallados.py`)

### 1.1. Arquitectura y Autenticación Delegada Local
El descargador automatizado (`descargar_detallados.py`, 603 líneas) implementa una integración sobre **Microsoft Playwright** (`playwright.sync_api`) utilizando el navegador **Microsoft Edge** (`channel="msedge"`) con contexto persistente (`launch_persistent_context`):

```
+-------------------------------------------------------------+
|                     Usuario / Operador                      |
+-------------------------------------------------------------+
                              |
                     --setup (1ra vez)
                              v
+-------------------------------------------------------------+
|              Microsoft Edge Persistent Context              |
|        - Directorio: .sesiones/{nombre_usuario}/            |
|        - Autenticación SSO: @rockdrillgroup.com             |
|        - Cookies y tokens de sesión locales persistidos     |
+-------------------------------------------------------------+
                              |
                 Ejecución Diaria (--fecha)
                              v
+-------------------------------------------------------------+
|                    Navegación OWA Mail                      |
|             https://outlook.office.com/mail/                |
+-------------------------------------------------------------+
```

* **Gestión de Sesiones Multiusuario (`obtener_session_dir`)**:
  - Cada operador registra su perfil mediante `python descargar_detallados.py --setup`.
  - Las cookies de sesión se guardan localmente en `.sesiones/{nombre_usuario}/` y el usuario activo en `.descargador_config.json`.
  - **Seguridad**: No se almacenan contraseñas ni secretos en texto plano; aprovecha las cookies nativas de Edge y el SSO corporativo de Microsoft 365.
  - Compatibilidad: Migra automáticamente perfiles previos de `.edge_session/`.

### 1.2. Modos de Destino y Limpieza Preventiva
El descargador soporta dos modos operativos:
1. **Modo Estructura Base (Por Defecto)**:
   - Destino: `Estructura base/Rockdrill_Control_Operaciones/CTR_{CTR}/02_Detallado/`
   - **Regla de Negocio de Limpieza (`limpiar_detallado_previo_ctr`)**: Antes de guardar el nuevo archivo, purga todos los archivos `.xlsx`/`.xlsb` preexistentes en la carpeta `02_Detallado` del CTR. Esto garantiza que exista **exactamente 1 reporte detallado activo por contrato**.
2. **Modo Prueba (`--prueba`)**:
   - Destino: `prueba correos/` (carpeta limpiada al inicio de cada corrida) para inspección manual y benchmarking.

### 1.3. Regla Temporal y Búsqueda Estricta por Fecha
La perforación diaria se envía al día siguiente:
$$\text{Fecha de Correo } (N) \implies \text{Perforación Operativa } (N - 1)$$

* **Búsqueda Estricta (`build_ctrs_config`)**:
  - Query obligatoria: `f"{CTR} received:{fecha}"` (ej. `AMERICANA received:18/08/2026`).
  - **Eliminación de Fallbacks sin Fecha**: Versiones tempranas tenían un fallback `"{CTR}"` sin fecha que provocaba la descarga de reportes de fechas desactualizadas (ej. descarga del 14/08 cuando se solicitaba el 17/08 en Andaychagua). En la versión actual, **no existe fallback sin fecha**; si no hay correo en la fecha exacta, se reporta formalmente como `FALTANTE`.

### 1.4. Selectores DOM Bilingües (Español / Inglés)
Para garantizar portabilidad en máquinas con configuraciones regionales diversas:
- Búsqueda: `#topSearchInput, input[aria-label*='Buscar'], input[aria-label*='Search']`
- Botón Cerrar: `button[aria-label*='Cerrar'], button[aria-label*='Close'], i[data-icon-name='Cancel']`
- Descarga Masiva: `button:has-text('Descargar todo'), button:has-text('Download all'), span:has-text('Descargar todo')`
- Descarga Individual: `button:has-text('Descargar'), button:has-text('Download'), div[role='menuitem']:has-text('Descargar')`
- Detección de Adjuntos: `div[class*='attachment'], div[aria-label*='adjunt'], div[aria-label*='attach']`

### 1.5. Estrategia de Descarga en 4 Niveles
Cuando se abre un correo de un CTR, el descargador ejecuta una cascada de extracción:
1. **Estrategia 1 (Descarga Masiva / ZIP - `descargar_via_zip`)**:
   - Dispara clic en `Descargar todo` / `Download all`.
   - Si OWA entrega un `.zip` (habitual cuando el correo incluye detallado + PDFs firmados como en Catalina Huanca o Americana), lo extrae en memoria temporal, filtra el archivo que cumple `es_detallado_para_ctr(zname, aliases)`, lo guarda en `02_Detallado/` y elimina el ZIP temporal.
2. **Estrategia 2 (Menú Contextual de Adjunto Individual)**:
   - Localiza elementos con extensiones `.xlsx`, `.xlsb`, `.xls` que coincidan con los alias del CTR.
   - Realiza hover y clic en el botón chevron (`ChevronDown`, `Más opciones`) o clic derecho para invocar el menú contextual y hacer clic en `Descargar`.
3. **Estrategia 3 (Clic Directo con `expect_download`)**:
   - Clic directo en la tarjeta del adjunto capturando el evento de descarga con timeout de 3 segundos.
4. **Estrategia 4 (Descarga desde Visor Online)**:
   - Si OWA abre el archivo en el visor de Excel Online integrado, localiza el botón `Descargar` de la barra superior.

### 1.6. Validaciones de Negocio y Filtros de Exclusión
La función `es_detallado_para_ctr(nombre_archivo, aliases)` aplica filtros estrictos:
- Extensiones permitidas: `.xlsx`, `.xlsb`, `.xls`.
- **Exclusiones Mandatorias**: Descarta archivos que contengan `f.03`, `f03`, `f 03`, `f.07`, `f07`, `cda`, `corto` (resúmenes ejecutivos diarios que no son el reporte detallado).
- **Inclusiones Mandatorias**: Debe contener al menos un alias del CTR (ej. `["catalina", "huanca"]`) y las palabras clave `detallado`, `f.01`, `f01` o `f 01`.
- **Conservación de Nombres**: Se guarda el archivo con el nombre original del remitente para total trazabilidad.

### 1.7. Auditoría y Registro de Rendimiento
Cada ejecución genera dos archivos de auditoría en `output/auditoria_descargas/`:
1. `_MAPEO_DESCARGAS_{fecha}.xlsx`: Contiene `CTR`, `Estado` (`DESCARGADO` / `FALTANTE`), `Archivo`, `Ruta_Destino`, `Bytes`.
2. `_TIEMPOS_{fecha}.xlsx`: Registro de segundos invertidos por cada uno de los 18 CTRs y tiempo total acumulado.

---

## 2. Compilación de Control Interno (`RD.402.P.01.F.04`)

### 2.1. Estructura del Libro Maestro de Control Interno
El archivo `RD.402.P.01.F.04  Consolidado de Avance [Mes].xlsx` es el libro oficial donde la Administración Central consolida diariamente los metros reportados por los 18 contratos.
- **Nomenclatura de Pestañas**: Pestañas diarias con formato `dd.mm` (ej. `26.07`, `27.07`, ..., `17.08`).
- **Filtrado de Hojas (`src/etl_control_interno.py:43`)**: Regex `^\d{1,2}\.\d{1,2}$`. Ignora hojas de gráficos, resúmenes mensuales, parametrizaciones o tablas dinámicas.
- **Inferencia de Año y Cruce de Fin de Año**: Extrae el año del nombre del archivo (ej. `2026`) y maneja la transición diciembre (`12`) a enero (`01`) incrementando el año en 1 si ocurre un reset de mes.

```
Pestaña Diaria (ej. "16.08"):
+-----------------------------------------------------------------------------------------------+
| Fila 1 a 8: Encabezados y Metadatos de Control Interno                                        |
| Fila 9: Títulos de Columna [CONTRATO, ..., EQUIPO, ..., SE PERFORO, ..., METRAJE]             |
+-----------------------------------------------------------------------------------------------+
| Fila 10 en adelante (Datos Operativos):                                                       |
| Col A (0): CTR (con celdas combinadas) -> Filldown                                            |
| Col C (2): MAQUINA (Nombre del equipo)                                                        |
| Col E (4): SE PERFORO ("SI" / "NO")                                                           |
| Col G (6): METRAJE DIARIO (Metros perforados en la guardia)                                   |
+-----------------------------------------------------------------------------------------------+
| Condición de Parada: Fila con texto "TOTAL AVANCE", "TOTAL ACUMULADO" o "TOTAL GENERAL"      |
+-----------------------------------------------------------------------------------------------+
```

### 2.2. Algoritmo de Extracción y Transformación
1. **Lectura Acelerada con Rust Calamine**: Utiliza `python_calamine.CalamineWorkbook` para leer hojas binarias de Excel en milisegundos sin sobrecarga de COM ni openpyxl.
2. **Condición de Parada Adaptativa (`etl_control_interno.py:80`)**:
   La lectura inicia en la Fila 10 (índice 9). Se evalúa cada fila; si el texto concatenado contiene `"TOTAL AVANCE"`, `"TOTAL ACUMULADO"` o `"TOTAL GENERAL"`, se detiene inmediatamente el procesamiento de la pestaña, evitando capturar subtotales, promedios o pies de página.
3. **Propagación de CTR (Filldown en Columna A)**:
   En Excel, los nombres de contrato suelen ocupar celdas combinadas que abarcan múltiples filas de máquinas. El script detecta el valor en Columna A, filtra títulos (`CONTRATO`, `EQUIPO`, `AVANCE`, `SISTEMA`, `TOTAL`) y propaga el CTR actual a las filas subsiguientes.
4. **Filtro de Filas de Máquina (Columna C)**:
   Descarta filas vacías o con textos de cabecera como `EQUIPO`, `SUB`, `SUP`, `MAQUINA`, `NONE`, `-`.
5. **Limpieza Numérica de Metraje (Columna G)**:
   Maneja comas decimales (`3,55` $\rightarrow$ `3.55`), espacios, guiones y celdas nulas mediante `clean_number_value()`.

### 2.3. Asignación de Turnos `A` / `B` en Control Interno
En las plantillas de Control Interno, cada equipo perforador activo presenta dos filas correlativas por cada día operativo:
- **1ra aparición de la máquina en el día**: Turno **`A`** (Guardia Día / Guardia 1).
- **2da aparición de la máquina en el día**: Turno **`B`** (Guardia Noche / Guardia 2).

El contador `machine_turn_counter[(fecha_iso, ctr_clean, official_maq)]` secuencia exactamente estas apariciones, asegurando paridad biunívoca con los turnos operativos.

### 2.4. Estandarización de Nombres de Máquina contra Maestro SAP
Tanto en Control Interno como en los reportes detallados, existen discrepancias tipográficas en los nombres de los equipos. El sistema normaliza los nombres contra la hoja `Exepciones` de `Maestros_Maquinas.xlsx` y el diccionario canónico `KNOWN_FALLBACK_EXCEPTIONS`:

| CTR | Nombre en Planilla Local | Nombre Normalizado SAP Oficial | Razón de Estandarización |
| :--- | :--- | :--- | :--- |
| `TICLIO` | `XRD150USS-001` | `XRD150U-007` | Reasignación de código SAP en contrato |
| `TAMBOJASA` | `DE710ST-002` | `DE710T-002` | Supresión de letra 'S' errónea en campo |
| `YAULIYACU` | `XRD50USS-001` / `00T` | `XDR50USS-00T` | Corrección de acrónimo XDR |
| `MOROCOCHA` | `XRD90USS-002` | `XRD90USS-005` | Cambio de equipo asignado |
| `CHUNGAR` | `XRD90U-003` | `XRD90U-021` | Actualización de flota interna |
| `ANDAYCHAGUA`| `XRD90U-017` | `XRD150U-001` | Reemplazo de máquina por capacidad |
| `COBRIZA` | `XRD90U-008` | `XRD150U-008` | Código SAP unificado |
| `INMACULADA` | `XRD250-001` | `XRD250U-001` | Estandarización de sufijo 'U' (Underground) |
| `INMACULADA` | `XRD80U-008` | `XRD80USS-008` | Estandarización de sufijo 'USS' |
| `INMACULADA` | `XRD90U-012 (XRD150)`| `XRD90U-012` | Eliminación de texto auxiliar entre paréntesis |

---

## 3. Motor de Reconciliación y Auditoría Turno a Turno

### 3.1. Clave Primaria y Full Outer Join
El cruce se fundamenta en la generación determinística de una clave primaria universal `ID_CLAVE_UNICA`:

$$\text{ID\_CLAVE\_UNICA} = \text{AAAAMMDD} - \text{CODIGO\_MAQUINA\_SAP} - \text{TURNO}$$
*Ejemplo:* `20260816-XRD80ITH-001-A`

El motor (`src/reconciliacion.py`) ejecuta un **Full Outer Join** agrupado por clave entre Detallados y Control Interno:
```python
comp = pd.merge(
    det_sum, ci_sum,
    on=["ID_CLAVE_UNICA", "FECHA", "CTR", "MAQUINA", "TURNO_ESTANDAR"],
    how="outer"
).fillna(0.0)

comp["DIFERENCIA"] = (comp["METRAJE_DETALLADO"] - comp["METRAJE_CI"]).round(2)
discrepancias = comp[comp["DIFERENCIA"].abs() > 0.01].copy()
```

### 3.2. Ventana de Fechas Operacionales y Truncamiento de Corte
Un hallazgo crítico documentado en `contexto/DIAGNOSTICO_Y_PUNTOS_A_CORREGIR_MANANA.md` reveló que los reportes detallados en campo suelen contener registros proyectados o días posteriores (ej. hasta el 25 de agosto), mientras que Control Interno solo compila hasta la fecha de corte evaluada (ej. 16 o 17 de agosto).

* **Regla de Alineación**:
  $$\text{Rango Evaluado: } \text{min\_date}(CI) \le \text{FECHA} \le \text{fecha\_corte}$$
  Al acotar ambos datasets a la ventana operativa común, se eliminan falsos positivos por desfase de días futuros.

### 3.3. Taxonomía Exhaustiva de Causas de Discrepancia

Las discrepancias detectadas entre Detallados y Control Interno se clasifican en **4 causas raíz bien documentadas**:

```
+---------------------------------------------------------------------------------------------------+
|                            TAXONOMÍA DE DISCREPANCIAS DE METRAJE                                  |
+---------------------------------------------------------------------------------------------------+
| 1. Intercambio de Turno (Shift Swap)     | Suma diaria exacta (0.00 m). Desfase A vs B por        |
|                                          | imputación manual del supervisor.                       |
+------------------------------------------+--------------------------------------------------------+
| 2. Faltante de Reporte en Origen         | CTR no envió correo en la fecha exacta o reporte sin   |
|                                          | procesar (ej. Americana, Colquijirca no medido).       |
+------------------------------------------+--------------------------------------------------------+
| 3. Registros en Cero / Sondaje Paralelo  | Perforación real en parte diario omitida en Control    |
|                                          | Interno (ej. Yauliyacu XRD125USS-001 +125.40 m).       |
+------------------------------------------+--------------------------------------------------------+
| 4. Redondeos y Ajustes Decimales         | Variaciones milimétricas por profundidad acumulada     |
|                                          | en campo (ej. San Cristóbal +/- 0.04 m).               |
+---------------------------------------------------------------------------------------------------+
```

#### Caso 1: Intercambio de Turno con Suma Diaria Idéntica
* **Comportamiento**: En contratos como **Chungar**, **Morococha**, **Catalina Huanca** y **Condestable**, el metraje diario total de la máquina es $100\%$ idéntico entre el Detallado y Control Interno, pero la distribución entre Guardia 1 (Turno A) y Guardia 2 (Turno B) difiere.
* **Ejemplo Real (Chungar `XRD90U-021`, 08/07/2026)**:
  - Detallado: Turno A = $8.55\text{ m}$, Turno B = $21.25\text{ m}$ (Total = $29.80\text{ m}$)
  - Control Interno: Turno A = $10.35\text{ m}$, Turno B = $19.45\text{ m}$ (Total = $29.80\text{ m}$)
  - Diferencia Diaria Neta: $\mathbf{0.00\text{ m}}$.

#### Caso 2: Faltante de Reporte en Origen
* **Comportamiento**: Cuando una unidad minera no remite su correo diario a OWA (ej. **Americana** en fechas no enviadas, o **Andaychagua** cuando no hubo envío al 17/08), el sistema lo identifica explícitamente sin inventar datos ni replicar archivos obsoletos.
* **Manejo**: Se lista en el reporte de auditoría como `FALTANTE` con aviso explícito para gestión administrativa.

#### Caso 3: Registros en Cero Históricos / Sondajes Paralelos
* **Comportamiento**: Máquinas que perforaron sondajes adicionales que constan en los partes diarios pero que no fueron cargados a la planilla de Control Interno por razones de facturación o acuerdos con el cliente minero.
* **Ejemplo Real (Yauliyacu `XRD125USS-001`, 17 al 25 de Julio)**:
  - Se ejecutó un **taladro paralelo** acumulando $+125.40\text{ m}$ en los reportes detallados.
  - En Control Interno los registros figuran con $0.00\text{ m}$.
  - Diagnóstico validado: Desfase 100% justificado por naturaleza de sondaje paralelo.

#### Caso 4: Ajustes de Campo y Redondeos Decimales
* **Comportamiento**: Diferencias decimales menores generadas por la resta de cotas de profundidad acumulada en campo frente a la planilla central.
* **Ejemplo Real (San Cristóbal `XRD90U-023`)**:
  - Turno B (30/06): Detallado $38.21\text{ m}$ vs CI $38.25\text{ m}$ ($-0.04\text{ m}$)
  - Turno A (01/07): Detallado $33.39\text{ m}$ vs CI $33.35\text{ m}$ ($+0.04\text{ m}$)
  - Causa: Redondeo decimal en cota de profundidad acumulada ($121.71\text{ m}$ vs $121.75\text{ m}$).

### 3.4. Métricas de Cuadratura y Validación Operativa
En las pruebas integrales ejecutadas sobre los 18 CTRs:
- **Tasa de Coincidencia Exacta Global**: **$95.17\% - 96.5\%$** de todas las claves primarias evaluadas presentan exactamente $0.00\text{ m}$ de diferencia.
- **Cuadratura Acumulada del 100.00%**: Coincidencia perfecta ($0.00\text{ m}$ de diferencia acumulada) en los contratos con reporte disponible:
  1. `TICLIO` ($0.00\text{ m}$)
  2. `CERRO` ($0.00\text{ m}$)
  3. `COBRIZA` ($0.00\text{ m}$)
  4. `COLQUISIRI` ($0.00\text{ m}$)
  5. `CUCULI` ($0.00\text{ m}$)
  6. `LA ESTRELLA` ($0.00\text{ m}$)
  7. `SAN CRISTOBAL` ($0.00\text{ m}$)
  8. `YAURICOCHA` ($0.00\text{ m}$)
  9. `CATALINA HUANCA` ($0.00\text{ m}$)
  10. `CONDESTABLE` ($0.00\text{ m}$)
  11. `TAMBOJASA` ($0.00\text{ m}$)
  12. `RAURA` ($0.00\text{ m}$)
  13. `CHUNGAR` ($0.00\text{ m}$)
  14. `MOROCOCHA` ($0.00\text{ m}$)
  15. `INMACULADA` ($0.00\text{ m}$)

---

## 4. Generación de Informes Ejecutivos en PDF (`generar_pdf_propuesta.py`)

### 4.1. Requerimientos de Diseño Editorial para Audiencia No Técnica
El informe técnico ejecutivo está concebido para ser presentado a **Gerencia General, Gerencia de Operaciones, Administradoras de Contrato y Jefaturas de TI**. Por ello, debe cumplir estrictos estándares visuales:
1. **Claridad Tipográfica y Jerarquía Visual**:
   - Títulos en Azul Corporativo (`#1E3A8A`) y subtítulos en Verde Azulado / Teal (`#0D9488`).
   - Texto base en tono carbón oscuro (`#0F172A`) de alta legibilidad (Helvetica 9pt / interlineado 13pt).
   - Fondos suaves (`#F1F5F9`, `#EFF6FF`) para tarjetas de metadatos y cuadros de llamada (*callouts*).
2. **Numeración Dinámica de Páginas y Encabezados Corridos**:
   - Implementación de la clase `NumberedCanvas(canvas.Canvas)` en ReportLab: realiza dos pasadas para calcular el número total de páginas y estampar `"Página X de Y"`.
   - Encabezado corporativo superior a partir de la página 2 con línea divisoria y marca de confidencialidad en el pie de página.
3. **Tablas Estructuradas con Repetición de Cabecera**:
   - Todas las tablas extensas emplean `repeatRows=1` para que los encabezados se repitan automáticamente al saltar de página.
   - Alternancia de color en filas (`#FFFFFF` y `#F8FAFC`) con bordes sutiles (`#CBD5E1`).

### 4.2. Estructura de las 156 Columnas en 13 Bloques Canónicos
El documento formaliza la transición desde las plantillas heterogéneas actuales hacia un **Catálogo Maestro de 156 Columnas** agrupadas en 13 bloques correlativos que reflejan el flujo de trabajo en mina:

| Bloque | Denominación del Bloque | Rango de Columnas | N° Cols | Contenido Principal |
| :---: | :--- | :---: | :---: | :--- |
| **01** | Identificación y Generales | Cols 1 a 10 | 10 | N°, Zona, CTR, Máquina SAP, Turno (A/B), Grupo, Mes, Fecha, Año, Guardia. |
| **02** | Sondaje y Metraje | Cols 11 a 22 | 12 | Sondaje, Profundidad, Línea (NQ/HQ/PQ), Inclinación, Desde, Hasta, Metraje guardia, Metas. |
| **03** | Personal Asignado | Cols 23 a 25 | 3 | Perforista, Ayudante 1, Ayudante 2 (Nombres estandarizados). |
| **04** | Brocas y Escariadores | Cols 26 a 33 | 8 | Marca, Serie, N° y Estado de broca/escariador, Cambio de broca. |
| **05** | Aditivos y Combustible | Cols 34 a 57 | 24 | Bentonita, PAC, Polímeros, Lubricantes, Inhibidores, Petróleo (Cantidades y Unidades). |
| **06** | Operación Efectiva | Cols 58 a 76 | 19 | Perforación neta, Rimado, Casing, PVC, Reperforación, Lavado, Desviación Gyro, SPT, Piezómetro. |
| **07** | Preparación y Maniobras | Cols 77 a 101 | 25 | Maniobra de barras, Traslados (máquina, cámaras, personal), 5S, Pozas, Charlas, IPERC, Refrigerio. |
| **08** | Mantenimiento | Cols 102 a 106 | 5 | Mantenimiento Preventivo, Correctivo, Check List Pre Uso, Espera de Repuestos, Total Mantto. |
| **09** | Stand By Inoperativo (Rockdrill) | Cols 107 a 115 | 9 | Falta de personal, insumos, camioneta/cisterna, esperas inoperativas, Pare RD. |
| **10** | Stand By Cliente (Mina) | Cols 116 a 136 | 21 | Falta de agua/energía/ventilación, espera de scoop/frente/geología, voladura, clima, Pare Cía. |
| **11** | Totales y Disponibilidad | Cols 137 a 143 | 7 | Total Horas, Horas Efectivas, Horas Operativas, Lost Time, Disponibilidad Mecánica (%), UT (%). |
| **12** | Detalle de Tramos | Cols 144 a 151 | 8 | Tramos Desde/Hasta y Metrajes de Rimado HWT/HQ, Reperforación y Horómetros. |
| **13** | Bitácoras y Observaciones | Cols 152 a 156 | 5 | Trabajos realizados, repuestos usados, descripción litológica y comentarios de guardia. |

### 4.3. Mecanismo de Vistas Ocultables por Contrato
Para evitar el rechazo de los administradores de contrato en campo:
- **Familiaridad**: Se mantiene exactamente el doble encabezado en **Filas 23 y 24** con llenado desde la **Fila 25**.
- **Ocultación Dinámica (`Hide Columns`)**: Si una mina es subterránea y no usa columnas de superficie (ej. `Condiciones Climáticas` o `Pruebas Lugeon`), la administradora simplemente las **oculta visualmente en Excel**. Las columnas **no se borran ni se mueven de posición**, garantizando que el pipeline de ingesta automatizada nunca sufra desfasamiento de índices.

### 4.4. Selección Tecnológica: ReportLab vs WeasyPrint / matplotlib
Se evaluaron tres opciones tecnológicas para la generación de reportes PDF:

| Criterio | ReportLab (Seleccionado) | WeasyPrint | matplotlib / LaTeX |
| :--- | :--- | :--- | :--- |
| **Dependencias del Sistema** | **Cero dependencias binarias** (Pure Python / C-extension ligera). | Requiere bibliotecas GTK+, Pango, Cairo (problemático en Windows Server). | Requiere distribución TeX instalada (varios GB) o salida estática de imagen. |
| **Velocidad de Compilación** | **Sub-segundo (< 0.5s para 6 páginas)**. | ~3-6s por documento debido al motor WebKit/CSS. | ~5-15s (LaTeX) / Renders pesados. |
| **Control Tipográfico y Tablas** | **Total**: `Paragraph`, `TableStyle`, `KeepTogether`, `NumberedCanvas`. | Bueno mediante CSS Paged Media. | Rígido en tablas extensas de múltiples páginas. |
| **Portabilidad Multiplataforma** | **100% portable** en Windows, Linux y macOS sin configuración. | Frecuentes fallos de DLLs en Windows. | Difícil de empaquetar en entornos portables. |

**Conclusión**: **ReportLab** es la herramienta idónea para la generación de informes ejecutivos en el ecosistema de Rockdrill, garantizando ejecución inmediata, portabilidad en cualquier máquina de la empresa y diseño visual de calidad de imprenta.

---

## 5. Matriz de Componentes del Repositorio y Arquitectura de Código

```
C:\Proyectos Python\Detallados\
├── .sesiones/                        # Perfiles de sesión OWA persistentes por usuario
├── config.py                         # Configuración central (rutas dinámicas OneDrive / Local)
├── descargar_detallados.py           # Descargador OWA con Playwright y Edge SSO
├── ejecutar_pipeline.py              # CLI principal de ejecución del pipeline integral
├── generar_pdf_propuesta.py          # Generador de informes ejecutivos en PDF (ReportLab)
├── docs_propuesta_data.py            # Catálogo maestro de 156 columnas para reportes
├── src/
│   ├── utils.py                      # XML visibility, limpieza numérica, carga de excepciones
│   ├── etl_detallados.py             # Parser Calamine, slicing 200 filas, asignación de turnos
│   ├── etl_control_interno.py        # Compilador multi-hoja de Control Interno (dd.mm)
│   ├── reconciliacion.py             # Motor Full Outer Join y matriz comparativa
│   └── pipeline.py                   # Orquestador modular del flujo de datos
├── Estructura base/
│   └── Rockdrill_Control_Operaciones/
│       ├── 00_Control_Interno/       # RD.402.P.01.F.04 Consolidado de Avance mensual
│       ├── Maestro_Maquinas/         # Maestros_Maquinas.xlsx (Matriz de Exepciones SAP)
│       └── CTR_{CONTRATO}/
│           ├── 01_Avance_Diario/     # Reportes ejecutivos cortos (descartados de detallados)
│           └── 02_Detallado/         # Reporte Detallado RD.402.P.01.F.01 activo
└── output/
    ├── detallados_consolidados.xlsx/csv # Consolidado de los 18 contratos
    ├── control_interno/                 # control_interno_compilado.xlsx/csv
    ├── matriz_comparativa_metrajes.xlsx # Matriz de reconciliación y discrepancias
    ├── auditoria_descargas/             # Mapeos de descarga y profiling de tiempos
    └── PROPUESTA_ESTANDARIZACION_DETALLADO_F01.pdf # Informe ejecutivo PDF
```

---

## 6. Síntesis y Recomendaciones Técnicas para la Siguiente Fase

1. **Fecha de Corte y Ventana Operativa**:
   - Consolidar como regla estándar del pipeline la alineación dinámica de la ventana de fechas: $\text{min\_date}(CI) \le \text{FECHA} \le \text{max\_date}(CI)$, evitando que metrajes de días posteriores generen falsas discrepancias.
2. **Normalización Temprana de Excepciones**:
   - Mantener actualizada la hoja `Exepciones` en `Maestros_Maquinas.xlsx` para absorber nuevos cambios de flota o variaciones de nombres locales sin alterar el código fuente.
3. **Despliegue de la Plantilla Universal de 156 Columnas**:
   - Publicar la plantilla unificada basada en la propuesta aprobada en el PDF ejecutivo, permitiendo a las administradoras ocultar columnas no aplicables mediante vistas estándar de Excel.
4. **Mantenimiento del Descargador OWA**:
   - Conservar la política de **búsqueda estricta por fecha** (`received:dd/mm/yyyy`) y la detección explícita de contratos faltantes, previniendo la contaminación de bases de datos con archivos de fechas no coincidentes.
