# PROTOCOLO ESTÁNDAR Y REGLAS INQUEBRANTABLES DE REASIGNACIÓN DE 'OTROS' (ROCKDRILL)

Este documento define las normas operativas, de ingeniería de software y de control de calidad para cualquier proceso de limpieza, clasificación semántica y actualización de bases de datos históricas (`BD_DETALLADO`).

---

## 1. REGLAS INQUEBRANTABLES (NON-NEGOTIABLE CORE RULES)

### Regla 1: Aislamiento Intra-Fila Absoluto (Prohibido Salir de la Fila)
* **Principio:** Toda reasignación de horas registradas en `OTROS RD` u `OTROS CLIENTE` en la fila $i$ debe ejecutarse **exclusivamente dentro de la misma fila $i$** (`Fila i -> Fila i`).
* **Prohibición:** Queda terminantemente prohibido transferir horas a otras filas, otros turnos, otras fechas u otras máquinas para "completar guardias".

### Regla 2: Segregación Estricta de Casos Sin Motivo (Grupo B - Casos Observados)
* **Principio:** Si una fila tiene `OTROS > 0` pero el campo de motivo o comentarios está vacío, contiene solo números (`"0"`, `"0.0"`, `"1.0"`), o texto no clasificable:
  * **Acción:** NO copiar ni inyectar horas en ninguna columna de actividad.
  * **Destino:** Aislar obligatoriamente en el **Grupo B (`Casos_Observados`)** con estado `PENDIENTE_REVISION_MANUAL`.
* **Prohibición:** Prohibido asumir o adivinar motivos en celdas numéricas o en blanco.

### Regla 3: Copiado Puro y Preservación Histórica de Origen (Cero Borrados)
* **Principio:** El proceso es de **copiado aditivo** hacia la columna de actividad destino (`VALOR_FINAL = VALOR_ACTUAL + HORAS_REASIGNADAS`).
* **Preservación:** Los valores de `OTROS RD` y `OTROS CLIENTE` deben **permanecer intactos** en la base modificada.
* **Prohibición:** Prohibido borrar, sobreescribir con 0 o restar de las columnas de origen `OTROS`. Prohibido alterar columnas de subtotales, totales o fórmulas.

### Regla 4: Inserción Ordenada en OpenXML para Celdas Sparse
* **Principio:** En archivos `.xlsx` grandes, las celdas vacías no existen como nodos XML. Al inyectar una celda que no existe en la fila:
  * Se debe calcular el índice numérico de la columna (`A=1, ... BP=68, ...`).
  * Se debe insertar el nodo `<c r="BP{fila}"><v>{valor}</v></c>` en la **posición alfabética exacta** antes de la siguiente columna existente.
* **Prohibición:** Prohibido asumir que todas las celdas existen en el XML o insertar nodos desordenados (provoca corrupción o silenciamiento de datos).

---

## 2. ARQUITECTURA DEL DOBLE FILTRO SEMÁNTICO

1. **Filtro 1 (Python NLP Determinístico):**
   * Normalización ASCII/NFKD.
   * Catálogo de expresiones regulares con terminología de perforación diamantina (DDH).
   * Extracción de tiempos explícitos multicausa (ej. `"2h acondicionamiento 1h nivelado"` $\to$ descomposición proporcional ponderada).
   * Detección de divisores multicausa (`/`, `;`, `+`, `Y`) con equipartición 50%/50% o $1/N$.
   * Protección de frases compuestas (ej. *"Carga y descarga de tuberías"*, *"Orden y limpieza"*).

2. **Filtro 2 (Evaluación Semántica LLM):**
   * Validación del contexto y jerga operativa para motivos no estándar (ej. *"Desfile"* $\to$ `PARALIZACIÓN POR FIESTAS`, *"Ripeo de cámara"* $\to$ `F. DE HABILITACIÓN DE CÁMARA O PLATAFORMA`).
   * Generación de la matriz de auditoría semántica (`auditoria_llm_motivos.json`).

---

## 3. PROTOCOLO DE AUDITORÍA Y CONTROL DE CALIDAD (QA)

Antes de dar por concluida cualquier corrida, es obligatorio ejecutar dos frentes de auditoría:

1. **Auditoría Física Automatizada Post-Inyección:**
   * Relectura directa de la base `.xlsx` generada mediante `python_calamine` / `openpyxl`.
   * Extracción del 100% de las celdas copiadas y comparación estricta contra `VALOR_FINAL_CELDA`.
   * Verificación de cero alteraciones en las filas observadas del Grupo B.

2. **Auditoría Independiente por Subagente:**
   * Invocación de un subagente auditor (`research` o `self`) que inspecciona los archivos generados, valida el 100% de coincidencia y emite el **Dictamen Formal de Control de Calidad**.

---

## 4. ESTÁNDAR DE ENTREGABLES EXCLUSIVOS

Los reportes de salida deben contener **únicamente** los registros evaluados con `OTROS > 0`:
* **Hoja 1 (`Casos_Copiados`):** Filas con motivo válido, indicando `FILA_EXCEL`, `CTR`, `ACTIVIDAD_DESTINO`, `LETRA_COLUMNA` (ej. `BM`, `BP`, `EA`), `CELDA_EXCEL` (ej. `BP60520`), `VALOR_ANTERIOR_CELDA`, `HORAS_COPIADAS` y `VALOR_FINAL_CELDA`.
* **Hoja 2 (`Casos_Observados`):** Filas con `OTROS > 0` sin motivo para revisión manual.
* **Hoja 3 (`Resumen_Por_CTR`):** Consolidado gerencial de efectividad por contrato minero.
