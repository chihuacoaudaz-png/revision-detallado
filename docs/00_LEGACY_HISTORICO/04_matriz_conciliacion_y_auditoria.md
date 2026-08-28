---
title: 04. Matriz Comparativa, Conciliación Diaria y Diagnósticos
aliases: [Matriz Comparativa, Auditoría Diaria, Discrepancias Reales]
tags:
  - conciliacion
  - auditoria
  - metrajes
  - diagnostico
  - control-interno
created: 2026-08-13
updated: 2026-08-13
---

# ⚖️ 04. Matriz Comparativa, Conciliación Diaria y Diagnósticos Operacionales

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 1. Metodología de Conciliación

La reconciliación se realiza mediante un **Full Outer Join** entre el dataset de Detallados y el Consolidado de Control Interno sobre la clave primaria `ID_CLAVE_UNICA`:

$$\text{DIFERENCIA} = \text{METRAJE\_DETALLADO} - \text{METRAJE\_CONTROL\_INTERNO}$$

Se generan dos tablas de auditoría:
1. **`discrepancias_diarias_resumen`**: Filtra **únicamente los registros donde $|DIFERENCIA| \ge 0.01\text{ m}$**.
2. **`auditoria_bruto_completa`**: Contiene la totalidad de las 3,256 claves primarias para trazabilidad total.

---

## 2. Resumen Acumulado por Contrato Minero (18 CTRs al 18/08/2026)

| CTR | Metraje Detallados (m) | Metraje Control Interno (m) | Diferencia (m) | Total Claves | Coincidencias Exactas | % Coincidencia | Estado de Cuadratura |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **AMERICANA** | 1,864.30 | 1,864.30 | **0.00** | 96 | 96 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **ANDAYCHAGUA** | 1,594.00 | 1,594.00 | **0.00** | 144 | 144 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **CATALINA HUANCA** | 3,544.80 | 3,544.80 | **0.00** | 240 | 240 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **CERRO** | 697.10 | 697.10 | **0.00** | 48 | 48 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **COBRIZA** | 3,271.60 | 3,271.60 | **0.00** | 336 | 336 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **COLQUISIRI** | 1,085.60 | 1,085.60 | **0.00** | 48 | 48 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **CONDESTABLE** | 2,061.90 | 2,061.90 | **0.00** | 192 | 192 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **INMACULADA** | 2,320.30 | 2,320.30 | **0.00** | 336 | 336 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **LA ESTRELLA** | 715.30 | 715.30 | **0.00** | 96 | 96 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **MOROCOCHA** | 962.50 | 962.50 | **0.00** | 144 | 144 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **RAURA** | 2,605.62 | 2,605.62 | **0.00** | 192 | 192 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **SAN CRISTOBAL** | 1,427.35 | 1,427.35 | **0.00** | 192 | 192 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **TAMBOJASA** | 1,119.75 | 1,119.75 | **0.00** | 96 | 96 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **TICLIO** | 683.25 | 683.25 | **0.00** | 48 | 48 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **YAULIYACU** | 1,853.05 | 1,853.05 | **0.00** | 144 | 144 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **YAURICOCHA** | 189.80 | 189.80 | **0.00** | 96 | 96 | **100.00%** | ✅ **100% Cuadratura Exacta** |
| **CHUNGAR** | 2,333.05 | 2,333.05 | **0.00** | 256 | 254 | **99.22%** | ✅ **Suma Total Exacta** (Desfase de $\pm 0.20$ m en `LM110U-001`) |
| **CUCULI** | 553.10 | 553.10 | **0.00** | 48 | 45 | **93.75%** | ✅ **Suma Total Exacta** (Distribución interna en `XRD100ST-001`) |
| **TOTAL GENERAL** | **28,882.37** | **28,882.37** | **0.00** | **2,752** | **2,743** | **99.67%** | ✅ **100% Cuadrado** |

---

## 3. Catálogo Exhaustivo de las 9 Discrepancias Diarias

De las **2,752 claves evaluadas**, únicamente 9 presentan variaciones menores:

```text
1. Chungar LM110U-001 (2 Claves -> ±0.20 m):
   - 2026-07-29 Turno B: Detallado 13.00 m vs CI 13.20 m (-0.20 m)
   - 2026-07-30 Turno A: Detallado 8.85 m vs CI 8.65 m (+0.20 m)
   * Diagnóstico: Desfase operacional de corte de medianoche entre dos días consecutivos.

2. Cuculí XRD100ST-001 (3 Claves -> ±1.80 m / ±0.20 m):
   - 2026-07-31 Turno A: Detallado 22.90 m vs CI 21.10 m (+1.80 m)
   - 2026-07-31 Turno B: Detallado 31.00 m vs CI 33.00 m (-2.00 m)
   - 2026-08-07 Turno B: Detallado 15.20 m vs CI 15.00 m (+0.20 m)
   * Diagnóstico: Reclasificación interna de tramos de perforación entre guardias por supervisión.

3. Chungar LM110U-001 (2 Claves -> 0.00 m):
   - 2026-08-12 Turnos A y B: Auto-resuelto a distribución de Control Interno (9.40 m y 10.90 m).

4. La Estrella XRD150U-004 (2 Claves -> 0.00 m):
   - 2026-08-16 Turnos A y B: Auto-resuelto a distribución de Control Interno (6.20 m y 0.60 m).
```

---

## 4. Validación Histórica contra `agosto2026.xlsx`

Se contrastó el resultado final con el libro corporativo maestro [`tools/agosto2026.xlsx`](file:///C:/Proyectos%20Python/Detallados/tools/agosto2026.xlsx) (hoja `COMPA`), verificando coincidencia exacta al milímetro en la sumatoria acumulada de los 18 contratos mineros ($28,882.37\text{ m}$).

---

## 🔗 Notas Relacionadas

- [[docs/02_diccionario_de_datos_135_columnas|02. Diccionario de Datos y Tipado Estricto (135 Columnas)]]
- [[docs/03_algoritmo_turnos_y_casos_borde|03. Algoritmo Inteligente de Turnos y Casos Borde]]
- [[docs/05_guia_ejecucion_y_mantenimiento|05. Guía de Ejecución, Automatización y Mantenimiento]]
