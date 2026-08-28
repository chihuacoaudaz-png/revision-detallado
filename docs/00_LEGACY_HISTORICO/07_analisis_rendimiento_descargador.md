---
title: 07. Análisis de Rendimiento del Descargador Automatizado
aliases: [Performance Descargador, Optimización Playwright OWA]
tags:
  - rendimiento
  - playwright
  - owa
  - optimizacion
  - rockdrill
  - automatizacion
  - obsidian-vault
created: 2026-08-17
updated: 2026-08-17
status: active
version: 1.0.0
---

# ⚡ 07. Análisis de Rendimiento del Descargador Automatizado

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 🎯 1. Contexto y Problema

El script `descargar_todos_los_detallados_exactos.py` descarga automáticamente los 18 Reportes Detallados de Avance (`RD.402.P.01.F.01`) desde OWA (Outlook Web App) usando Playwright con la sesión SSO de Edge.

### ⏱️ Tiempo Observado (v1.0):
- **Ejecución del 17/08/2026**: ~2 horas para procesar 18 CTRs
- **Promedio por CTR**: ~6-7 minutos incluyendo fallbacks

---

## 🔍 2. Perfil de Tiempos por Operación (v1.0 Original)

| Operación | Tiempo Fijo | Frecuencia por CTR | Subtotal Estimado |
|:---|:---|:---|:---|
| `time.sleep(3)` después de búsqueda | 3.0s | 1-3 queries | 3-9s |
| `time.sleep(2.5)` al abrir correo | 2.5s | 1-5 correos | 2.5-12.5s |
| `time.sleep(1.5)` al clickear adjunto | 1.5s | 1-3 intentos | 1.5-4.5s |
| `time.sleep(2)` carga inicial OWA | 2.0s | 1 vez global | 2.0s |
| Timeout `expect_download` (fallido) | 8-10s | 0-2 veces | 0-20s |
| Re-query locators (`div[role='option']`) | ~0.5s | cada iteración | ~2.5s |

### 📊 Resumen de Overhead por CTR:
```
Caso óptimo  (1 query, 1 correo, ZIP directo):  ~8s
Caso promedio (1 query, 2 correos, adjunto ind): ~15-20s
Caso peor    (3 queries × 5 correos × fallback): ~60-90s
```

> [!WARNING]
> El caso peor se multiplica por los CTRs que no tienen correo en la fecha
> (como INMACULADA y LA_ESTRELLA), donde se agotan TODAS las queries y
> TODOS los correos con timeouts completos.

---

## 🐌 3. Cuellos de Botella Identificados

### 3.1 Sleeps Fijos Innecesarios
- `time.sleep(3)` después de buscar: OWA renderiza resultados en ~0.5-1s en la mayoría de casos.
- `time.sleep(2.5)` después de abrir correo: El panel de lectura carga en ~0.5-1.5s.
- **Desperdicio estimado**: 1.5-2s por cada operación × ~80 operaciones = **~2-3 minutos**.

### 3.2 Fallback Queries Exhaustivas
Cuando un CTR no existe para la fecha (INMACULADA, LA_ESTRELLA), el script:
1. Busca con `received:fecha` → 5 correos × 2.5s = 12.5s + timeouts
2. Busca sin fecha → 5 correos × 2.5s = 12.5s + timeouts
3. Total por CTR faltante: **~60-90 segundos desperdiciados**

### 3.3 Locator Broad para Adjuntos
```python
# Selector original: demasiado amplio
elements = page.locator("button, div[role='button'], div, span, a")
    .filter(has_text=re.compile(r'\.(xlsx|xlsb|xls)', re.IGNORECASE)).all()
```
Este selector captura **todos los elementos del DOM** y luego filtra por texto. En correos con muchos elementos, puede tardar ~1-2s.

### 3.4 Sin Instrumentación
Sin logging de tiempos es imposible saber qué CTR está atascado o qué operación domina el tiempo total.

---

## ✅ 4. Optimizaciones Implementadas (v2.0 - `descargar_detallados_optimizado.py`)

| # | Optimización | Antes | Después | Ahorro Est. |
|:---|:---|:---|:---|:---|
| 1 | Wait de búsqueda | `time.sleep(3)` | `wait_for_selector(DOM signal, 5s)` + 0.5s | ~2s/query |
| 2 | Wait de apertura de correo | `time.sleep(2.5)` | `wait_for_selector(attachments, 4s)` + 0.3s | ~1.5s/correo |
| 3 | Wait de click adjunto | `time.sleep(1.5)` | `time.sleep(0.8)` | ~0.7s/click |
| 4 | Wait inicial | `time.sleep(2)` | `time.sleep(1)` | 1s global |
| 5 | Instrumentación | Ninguna | Timing por CTR + total + export Excel | Diagnóstico |
| 6 | CLI configurable | Hardcoded `FECHA_OBJETIVO` | `--fecha dd/mm/yyyy` | Flexibilidad |

### 📈 Estimación de Mejora:
```
v1.0: ~120 min (18 CTRs)  → ~6.7 min/CTR promedio
v2.0: ~20-30 min estimado → ~1.1-1.7 min/CTR promedio
Mejora esperada: 4x-6x más rápido
```

---

## 🚀 5. Uso del Script Optimizado

```bash
# Descargar reportes del día actual
python descargar_detallados_optimizado.py

# Descargar para una fecha específica
python descargar_detallados_optimizado.py --fecha 17/08/2026

# Descargar para fecha anterior
python descargar_detallados_optimizado.py --fecha 14/08/2026
```

### 📂 Salidas:
- `prueba correos/` → Reportes detallados descargados
- `prueba correos/_MAPEO_EXACTO_{fecha}.xlsx` → Auditoría de descargas
- `prueba correos/_TIEMPOS_EJECUCION_{fecha}.xlsx` → Profiling por CTR

---

## 🔮 6. Oportunidades Futuras de Optimización

1. **Detección temprana de "sin resultados"**: Si OWA muestra "No se encontraron resultados", saltar al siguiente query sin iterar correos.
2. **Caché de sesión OWA**: Reutilizar la misma pestaña en lugar de navegar desde 0.
3. **Paralelismo con múltiples pestañas**: Abrir N pestañas y procesar N CTRs en paralelo (riesgo: throttling de OWA).
4. **Microsoft Graph API**: Acceso directo a correos y adjuntos sin UI, ~100x más rápido pero requiere permisos admin del tenant.

---

## 🔗 Notas Relacionadas

- [[docs/06_flujo_descarga_correos_outlook_y_ctrs|06. Flujo de Descarga de Correos OWA]]
- [[docs/05_guia_ejecucion_y_mantenimiento|05. Guía de Ejecución y Mantenimiento]]
