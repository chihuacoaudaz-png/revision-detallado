---
title: 02. Diccionario de Datos y Tipado Estricto (135 Columnas)
aliases: [Diccionario de Datos, Data Types Schema, Estructura Oficial 135]
tags:
  - etl
  - datatypes
  - schema
  - rockdrill
created: 2026-08-13
updated: 2026-08-13
---

# 📊 02. Diccionario de Datos y Tipado Estricto (135 Columnas Oficiales)

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 1. Estructura Global y Orden Canónico

El dataset consolidado oficial contiene **135 columnas** organizadas estrictamente en dos bloques:
1. **129 Columnas Nativas Oficiales** (Posiciones 1 a 129): Corresponden a los campos del formulario operacional `RD.402.P.01.F.01`.
2. **6 Columnas de Metadatos y Auditoría** (Posiciones 130 a 135): Se ubican **estrictamente al final** del dataset para no alterar la indexación nativa.

---

## 2. Clasificación de Tipos de Datos (Data Types Schema)

| Categoría | Cantidad | Tipo en Pandas (`dtype`) | Formato / Reglas de Negocio |
| :--- | :---: | :--- | :--- |
| **Identificadores Enteros** | 2 | `int64` | `N°` (índice 1..N), `SONDAJE_PARALELO` (default 1) |
| **Fecha Operacional** | 1 | `str` (ISO `YYYY-MM-DD`) | Fecha del turno de perforación (sin componente de hora) |
| **Métricas y Numéricos** | 88 | `float64` | Redondeo a 2 decimales para metrajes, profundidades, horómetros, consumibles y tiempos |
| **Campos de Texto / Descriptivos** | 44 | `str` / `object` | Cadenas limpias, sin espacios diacríticos ni nulos enmascarados (`""`) |
| **TOTAL DATASET** | **135** | - | Esquema validado al 100% mediante aserciones automáticas |

---

## 3. Catálogo Detallado de Columnas

### A. Bloque Operacional y de Identificación (Cols 1 - 10)
* `N°` (`int64`): Identificador secuencial de registro.
* `ZONA` (`str`): `"CENTRO"` (Americana, Chungar, Ticlio, Morococha, Yauliyacu, San Cristóbal, Andaychagua, Cerro) o `"PERIFERICO"`.
* `CTR` (`str`): Nombre del contrato minero normalizado (ej. `"CATALINA HUANCA"`).
* `MAQUINA` (`str`): Código corporativo oficial SAP (ej. `"XRD125UFDR-001"`).
* `TURNO (A=1;B=2)` (`str`): Turno original registrado en la planilla cruda.
* `GRUPO` (`str`): Cuadrilla o grupo asignado (ej. `"1.0"`, `"2.0"`, `"3.0"`).
* `MES` (`str`): Mes operacional calculado (corte al día 26, ej. `"JULIO"`).
* `FECHA` (`str`): Fecha en formato `YYYY-MM-DD`.
* `SONDAJE` (`str`): Código de pozo/taladro diamantino (ej. `"UDH-3753–2026"`).
* `PROFUNDIDAD DE SONDAJE` (`float64`): Profundidad proyectada total del pozo.

### B. Bloque de Perforación y Metrajes (Cols 11 - 23)
* `LINEA` (`str`): Diámetro de línea de perforación (`"HQ"`, `"NQ"`, `"BQ"`, `"HWT"`).
* `INCLINACIÓN` (`str`): Ángulo de inclinación del taladro en grados (ej. `"-45.00"`).
* `DESDE` (`float64`): Profundidad de inicio del avance en el turno (m).
* `HASTA` (`float64`): Profundidad de fin del avance en el turno (m).
* `METRAJE` (`float64`): Metraje perforado en el turno ($HASTA - DESDE$) en metros.
* `HORAS EXTRAS` (`float64`): Horas suplementarias laboradas.
* `PERFORISTA` (`str`): Nombre completo del operador principal.
* `AYUDANTE` (`str`): Nombre del primer asistente.
* `AYUDANTE 2` (`str`): Nombre del segundo asistente.
* `TOTAL` (`float64`): Total acumulado del pozo reportado en la planilla.
* `METROS ACUMULADO` (`float64`): Metros acumulados progresivos.
* `METROS PROYECTADO` (`float64`): Meta proyectada del cliente.
* `METROS META` (`float64`): Meta programada del mes.

### C. Bloque de Brocas y Escariadores (Cols 24 - 30)
* `MARCA BROCA`, `SERIE DE BROCA`, `Nº BROCA`, `ESTADO DE LA BROCA` (`str`).
* `MARCA ESCARIADOR`, `Nº ESCARIADOR`, `ESTADO DEL ESCARIADOR` (`str`).

### D. Bloque de Consumibles, Aditivos y Combustible (Cols 31 - 54)
* Productos y cantidades para: `BENTONITA`, `PAC`, `POLIMERO`, `LUBRICANTES`, `INHIBIDORES`, `ESTABILIZADOR`, `OTROS PRODUCTOS`, `GLN DE PETROLEO` (`float64` para cantidades y `str` para nombres/unidades).

### E. Bloque de Tiempos Operativos y Mantenimiento (Cols 55 - 89)
* Tiempos en horas (`float64`): `Perforación`, `Rimado`, `Asentado / Retiro DE REVESTIMIENTO (CASING)`, `Instalación PVC`, `RePerforación`, `MANTTO. PREVENTIVO`, `MANTTO. CORRECTIVO`, `LAVADO DE SONDAJE`, `MEZCLADO DE LODOS`, `MANIPULACIÓN DE TUBERÍAS`, `ACONDICIONAMIENTO DE SONDAJE`, `CAMBIO DE LINEA`, `RECUPERACIÓN DE SONDAJE`, `TRASLADO ENTRE CÁMARAS`, `MANIOBRAS GEOLÓGICAS`, `MEDICIÓN DE DESVIACIÓN`, `PRUEBAS DE SUELO`, `PERNOS DE ANCLAJE`, `CEMENTACIÓN`, `DESATE DE ROCAS`, `ORDEN Y LIMPIEZA`, `RECOJO DE LAMA`, `POZAS DE SEDIMENTACIÓN`, `ESTANDARIZACIÓN`, `RED DE AGUA`, `INSTALACIÓN EQUIPOS`, `TRASLADO ACCESORIOS`, `AUDITORÍA INTERNA`, `CAPACITACIÓN`, `CAMBIO DE PUNTO`, `TRASLADO MÁQUINA`, `ESPERA REPUESTOS`, `TRASLADO PERSONAL`, `REFRIGERIO`, `Otros*`.

### F. Bloque de Stand By y Tiempos Perdidos (Cols 90 - 104)
* Tiempos en horas (`float64`): `VOLADURA`, `FALTA DE AGUA`, `FALTA DE ENERGÍA`, `FALTA DE VENTILACIÓN`, `FALTA DE SERVICIOS`, `ESPERA DE PROGRAMA`, `ESPERA DE CÁMARA`, `ESPERA DE SOSTENIMIENTO`, `ESPERA DE SCOOP`, `ESPERA MARCADO`, `APOYO A GEOLOGÍA`, `AUDITORÍA EXTERNA`, `FALTA PLATAFORMA`, `ESPERA ORDEN CLIENTE`, `CONDICIONES CLIMATICAS`, `OTROS*`.

### G. Bloque de Tiempos Consolidados, Rimado, Reperforación y Horómetros (Cols 105 - 129)
* Justificaciones y subtotales: `SI ES OTROS * INDICAR EL MOTIVO`, `TIEMPO TOTAL`, `TIEMPO EFECTIVO - OPERATIVO`, `LOST TIME`, `TOTAL MANTTO.`, `STAND BY OPERATIVO`, `STAND BY INOPERATIVO`, `STAND BY CLIENTE`.
* Rimado y Reperforación: `RIMADO HWT/HQ DESDE`, `HASTA`, `METRAJE`, `TOTAL`, `REPERFORACIÓN DESDE`, `HASTA`, `METRAJE`, `TOTAL`.
* Horómetros: `HOROMETRO DESDE`, `HASTA`, `ACUMULADO`, `TOTAL`.
* Bitácora: `TRABAJOS REALIZADOS BITACORA DE MANTTO.`, `REPUESTOS UTILIZADOS BITACORA DE MANTTO.`.
* Geología: `DESCRIPCIÓN LITOLÓGICA`, `COMENTARIOS`.

### H. Bloque de Metadatos y Enriquecimiento (Cols 130 - 135 al final)
* `HOJA DE TRABAJO ORIGEN` (`str`): Nombre de la pestaña cruda en el libro Excel.
* `ARCHIVO ORIGEN` (`str`): Nombre del archivo `.xlsx` de origen.
* `TURNO_ESTANDAR` (`str`): `"A"` (Día) o `"B"` (Noche).
* `ID_CLAVE_UNICA` (`str`): Clave primaria compuesta `aaaammdd-codigomaquina-turno`.
* `SONDAJE_PARALELO` (`int64`): Número correlativo del sondaje en el turno (default `1`).
* `Alerta_Comentarios` (`str`): `"OK"` o `"FALTA COMENTARIO"` (si `Otros* > 0` y no hay texto en observaciones).

---

## 🔗 Notas Relacionadas

- [[docs/01_arquitectura_y_pipeline_etl|01. Arquitectura del Pipeline y Sustitución de Power Query]]
- [[docs/04_matriz_conciliacion_y_auditoria|04. Matriz Comparativa, Conciliación Diaria y Diagnósticos]]
