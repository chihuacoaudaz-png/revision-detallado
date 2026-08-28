---
title: 06. Flujo de Descarga de Correos OWA, Reglas por CTR y Reportes Detallados
aliases: [Flujo de Correos Rockdrill, Descarga OWA Playwright, Mapeo CTRs y Reportes]
tags:
  - outlook
  - owa
  - playwright
  - rockdrill
  - reportes-detallados
  - avance-diario
  - automatizacion-correos
  - obsidian-vault
created: 2026-08-17
updated: 2026-08-17
status: active
version: 1.0.0
---

# 📧 06. Flujo de Descarga de Correos OWA, Reglas por CTR y Reportes Detallados (Rockdrill)

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 🎯 1. Principio Operacional y Flujo de Envío Diario

En la operación de perforación diamantina de **Rockdrill Group**, cada contrato minero (**CTR**) reporta diariamente su producción al cierre de jornada.

### 📅 Regla Temporal de Recepción:
$$\text{Fecha de Correo} = \text{Día } N \implies \text{Perforación Operativa} = \text{Día } (N - 1)$$
*Ejemplo:* Los correos recibidos el **14 de agosto de 2026** corresponden a los turnos y metrajes perforados el **13 de agosto de 2026**.

---

## 📑 2. Tipología de Reportes Operacionales

| Tipo de Reporte | Código Oficial Formato | Contenido | Destino / Tratamiento |
| :--- | :--- | :--- | :--- |
| **Reporte Detallado de Avance** | `RD.402.P.01.F.01` | Excel con todas las máquinas del CTR, 135 columnas, desglose por sondaje, turnos A/B y horas operativas. | **OBJETIVO DE DESCARGA** (1 archivo único por CTR). |
| **Avance Diario / Corto** | `RD.402.P.01.F.03` / `RD.402.P.01.F.07` | Resumen ejecutivo diario de avance y metraje del día. | *Descartado del pipeline de Detallados*. |
| **Reporte Escaneado / Turno** | PDFs (`RP-*.pdf`, `RPV *.pdf`) | Hojas de partes diarios físicos firmados por perforistas. | *Descartado del pipeline de Detallados*. |

---

## 🏢 3. Catálogo de los 18 Contratos Mineros (CTRs) y Particularidades

| # | CTR Canónico | Remitente Habitual | Alias / Variaciones de Nombre en Adjunto |
|---|---|---|---|
| 1 | `AMERICANA` | Logística Americana | `RD.402.P.01.F.01 Reporte Detallado de Avance AMERICANA -AGOSTO-.xlsx` |
| 2 | `ANDAYCHAGUA` | Administración Andaychagua | `RD.402.P.01.F.01 Reporte Detallado de Avance ANDAYCHAGUA - AGOSTO.xlsx` |
| 3 | `CATALINA_HUANCA` | Administración Catalina Huanca | `H RD.402.P.01.F.01 Reporte Detallado de Avance CATALINA HUANCA - AGOSTO.xlsx` (envía múltiples PDFs juntos). |
| 4 | `CERRO` | Log CTR Cerro | `RD.402.P.01.F.01 Reporte Detallado de Avance CERRO - AGOSTO.xlsx` |
| 5 | `CHUNGAR` | Administración Chungar | `RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR ojo - AGOSTO.xlsx` |
| 6 | `COBRIZA` | Administración Cobriza | `RD.402.P.01.F.01 Reporte Detallado de Avance COBRIZA - AGOSTO.xlsx` |
| 7 | `COLQUISIRI` | Administración Colquisiri | `H RD.40.P.01.F.01 Reporte Detallado de Avance COLQUIJIRCA - AGOSTO.XLSX` (alias frecuente: *Colquijirca*). |
| 8 | `CONDESTABLE` | Administración Condestable | `RD.402.P.01.F.01 Reporte Detallado de Avance CONDESTABLE -AGOSTO.xlsx` |
| 9 | `CUCULI` | Logística Cuculí | `RD.402.P.01.F.01 Reporte Detallado de Avance CUCULI-Agosto.xlsx` |
| 10 | `INMACULADA` | Administración Inmaculada | `RD 402 P 01 F 01 Reporte Detallado de Avance INMACULADA AGOSTO.xlsx` (sin puntos en código). |
| 11 | `LA_ESTRELLA` | Willian Peláez Arangurí | `RD.402.P.01.F.01 Reporte Detallado de Avance LA ESTRELLA - AGOSTO (003).xlsx` |
| 12 | `MOROCOCHA` | Administración Morococha | `Copia de RD.402.P.01.F.01 Reporte Detallado de Avance MOROCOCHA - AGOSTO.xlsx` |
| 13 | `RAURA` | Administración Raura | `RD.402.P.01.F.01 Reporte Detallado de Avance RAURA - AGOSTO.xlsx` |
| 14 | `SAN_CRISTOBAL` | Administración San Cristóbal | `RD.402.P.01.F.01 Reporte Detallado de Avance SAN CRISTOBAL -AGOSTO.xlsx` |
| 15 | `TAMBOJASA` | Elton Ordóñez Carhuavilca | `RD.402.P.01.F.01 Reporte Detallado de Avance TAMBOJASA - AGOSTO.xlsx` |
| 16 | `TICLIO` | Administración Ticlio | `RD.402.P.01.F.01 Reporte Detallado de Avance TICLIO - JULIO.xlsx` |
| 17 | `YAULIYACU` | Administración Yauliyacu | `RD.402.P.01.F Reporte detallado de Avance Yauliyacu - AGOSTO.xlsx` |
| 18 | `YAURICOCHA` | Logística CTR Yauricocha | `Copia de RD.402.P.01.F.01 Reporte Detallado de Avance YAURICOCHA - AGOSTO.xlsx` |

---

## 🤖 4. Arquitectura de Descarga Automatizada (Playwright SSO)

### 🔐 1. Autenticación Delegada Local (Edge Persistent Context):
* **Directorio de Sesión**: `.sesiones/{nombre_usuario}/` (un perfil por persona)
* **Mecanismo**: Cada usuario ejecuta `--setup` la primera vez para crear su perfil Edge con SSO corporativo `@rockdrillgroup.com`. No requiere admin de tenant ni credenciales en scripts.
* **Migración**: Los perfiles legacy en `.edge_session` se migran automáticamente.

### 🌐 2. Compatibilidad de Idioma (ES/EN):
Todos los selectores DOM soportan OWA en Español e Inglés:
- `Buscar` / `Search`
- `Descargar todo` / `Download all`
- `Descargar` / `Download`
- `Cerrar` / `Close`

### 🔍 3. Algoritmo de Búsqueda y Selección Estricta:
1. **Query Estricta**: `"{CTR} received:{fecha}"` — **SIEMPRE con filtro de fecha**.
2. **Sin Fallback Sin Fecha**: ~~v1.0 usaba fallback `"{CTR}"` sin fecha~~ → Eliminado en v2.0 porque causaba descargas de fechas incorrectas (bug Andaychagua 14/08 vs 17/08).
3. **Filtro de Adjunto**:
   - Extensión obligatoria: `.xlsx`, `.xlsb`, `.xls`.
   - Patrón de inclusión: `detallado`, `f.01`, `f01`, `f 01`.
   - Patrón de exclusión: `f.03`, `f.07`, `avance diario`, `.pdf`, `.png`.
4. **Restricción de Cardinalidad**: Exactamente **1 archivo por CTR**.
5. **Conservación de Nombres**: Nombre original sin renombrar.

> [!CAUTION]
> **Bug corregido en v2.0**: El fallback sin `received:` de v1.0 descargó el detallado de
> Andaychagua del 14/08 cuando se pedía el del 17/08, porque OWA devolvió el correo más
> reciente de cualquier fecha. La v2.0 elimina todos los fallbacks sin fecha.

---

## 📊 5. Historial de Ejecuciones y Resultados

### 🗓️ 17/08/2026 (Perforación del 16/08/2026)

**Resultado**: 16/18 CTRs descargados exitosamente | 2 faltantes

| # | CTR | Estado | Archivo | Tamaño |
|:---|:---|:---|:---|:---|
| 1 | AMERICANA | ✅ OK | `RD.402.P.01.F.01  Reporte Detallado de Avance AMERICANA -AGOSTO-.xlsx` | 687,537 B |
| 2 | ANDAYCHAGUA | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance ANDAYCHAGUA - AGOSTOokaoka.xlsx` | 732,367 B |
| 3 | CATALINA_HUANCA | ✅ OK | `H RD.402.P.01.F.01 Reporte Detallado de Avance CATALINA HUANCA - AGOSTO.xlsx` | 834,460 B |
| 4 | CERRO | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance CERRO - AGOSTO.xlsx` | 578,405 B |
| 5 | CHUNGAR | ✅ OK | `RRRD.402.P.01.F.01 Reporte Detallado de Avance - CHUNGAR ojo - AGOSTO.xlsx` | 1,147,868 B |
| 6 | COBRIZA | ✅ OK | `RD.402.P.01.F.01  Reporte Detallado de Avance COBRIZA - AGOSTO.xlsx` | 967,683 B |
| 7 | COLQUISIRI | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance COLQUISIRI - AGOSTO.xlsx` | 591,214 B |
| 8 | CONDESTABLE | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance  CONDESTABLE -AGOSTO.xlsx` | 1,019,425 B |
| 9 | CUCULI | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance  CUCULI-Agosto.xlsx` | 660,058 B |
| 10 | **INMACULADA** | ❌ FALTANTE | *Detectado pero no descargado* | — |
| 11 | **LA_ESTRELLA** | ❌ FALTANTE | *Sin correo con detallado en la fecha* | — |
| 12 | MOROCOCHA | ✅ OK | `Copia de RD.402.P.01.F.01  Reporte Detallado de Avance MOROCOCHA - AGOSTO.xlsx` | 691,048 B |
| 13 | RAURA | ✅ OK | `RD.402.P.01.F.01  Reporte Detallado de Avance RAURA - AGOSTO.xlsx` | 890,640 B |
| 14 | SAN_CRISTOBAL | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance SAN CRISTOBAL -AGOSTO.xlsx` | 854,493 B |
| 15 | TAMBOJASA | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance TAMBOJASA  - AGOSTO.xlsx` | 652,416 B |
| 16 | TICLIO | ✅ OK | `RD.402.P.01.F.01 Reporte Detallado de Avance TICLIO - AGOSTO.xlsx` | 584,516 B |
| 17 | YAULIYACU | ✅ OK | `RD.402.P.01.F Reporte detallado de Avance Yauliyacu - AGOSTO.xlsx` | 708,718 B |
| 18 | YAURICOCHA | ✅ OK | `Copia de RD.402.P.01.F.01 Reporte Detallado de Avance YAURICOCHA  - AGOSTO.xlsx` | 162,430 B |

> [!NOTE]
> **INMACULADA**: El script detectó el correo `"AVANCE DIARIO DETALLADO AL 16/08..."` y el archivo
> `RD 402 P 01 F 01 Reporte Detallado de Avance INMACULADA AGOSTO.xlsx`, pero falló al descargarlo
> por un problema de interacción con el DOM de OWA (el adjunto no se expuso como tarjeta clickeable).
> Inmaculada usa formato sin puntos en el código (`RD 402` vs `RD.402`), lo cual podría afectar
> la detección en la estructura de adjuntos de OWA.

> [!NOTE]
> **LA_ESTRELLA**: No se encontró ningún correo con un Reporte Detallado para esta fecha.
> Las búsquedas con `ESTRELLA received:17/08/2026` y `LA ESTRELLA received:17/08/2026`
> devolvieron correos de otros CTRs (Raura, Yauricocha) pero ninguno con adjunto de La Estrella.
> Posible envío tardío o por canal diferente.

---

## 🔗 Notas Relacionadas

- [[docs/01_arquitectura_y_pipeline_etl|01. Arquitectura del Pipeline y Sustitución de Power Query]]
- [[docs/05_guia_ejecucion_y_mantenimiento|05. Guía de Ejecución, Automatización y Mantenimiento]]
- [[docs/07_analisis_rendimiento_descargador|07. Análisis de Rendimiento del Descargador]]
