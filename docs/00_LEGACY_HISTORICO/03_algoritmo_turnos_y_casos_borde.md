---
title: 03. Algoritmo Inteligente de Turnos y Casos Borde
aliases: [Algoritmo de Turnos, Casos Borde, Multi-sondajes]
tags:
  - turnos
  - algoritmos
  - python
  - casos-borde
  - conciliacion
created: 2026-08-13
updated: 2026-08-13
---

# 🧠 03. Algoritmo Inteligente de Turnos y Casos Borde Resueltos

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 1. El Reto Operacional de los Turnos Mineros

En las operaciones de perforación, el día operacional (24 horas) se divide en dos guardias:
* **Turno Día (`'A'`)**: Primera mitad de la jornada.
* **Turno Noche (`'B'`)**: Segunda mitad de la jornada.

Sin embargo, los reportes detallados en Excel presentan las siguientes anomalías:
1. **Multi-Sondajes Intra-Guardia**: Un perforista termina un pozo y arranca otro en el mismo turno, generando 2 o 3 filas bajo una misma guardia.
2. **Typos en la Columna Turno**: El digitador copia `Turno = 1.0` en la fila del nuevo pozo a pesar de que el operador pertenece a la guardia nocturna (`Grupo = 2.0`).
3. **Turnos sin Perforación (Mantenimiento / StandBy)**: Si el Turno Día tiene 0.00 m y su fila se elimina antes de asignar turnos, la fila de la noche quedaba sola y se convertía erróneamente en Turno Día.

---

## 2. Implementación de Producción: `assign_daily_turnos_fast` y Mapeo por Índice

### ⚙️ El Principio de Alineación por Índice (`df.loc[idxs]`):
El DataFrame se agrupa por fecha (`df.groupby("FECHA_NORM", sort=False)`), pero **nunca se asigna una lista plana** de retorno. En su lugar, el resultado se escribe directamente en los índices exactos de fila:
```python
df["TURNO_ESTANDAR"] = ""
for _, idxs in df.groupby("FECHA_NORM", sort=False).groups.items():
    sub = df.loc[idxs]
    g_list = sub["GRUPO"].tolist() if "GRUPO" in sub.columns else [None] * len(sub)
    t_list = sub["TURNO (A=1;B=2)"].tolist() if "TURNO (A=1;B=2)" in sub.columns else [None] * len(sub)
    p_list = sub["PERFORISTA"].tolist() if "PERFORISTA" in sub.columns else [None] * len(sub)
    df.loc[idxs, "TURNO_ESTANDAR"] = assign_daily_turnos_fast(g_list, t_list, p_list)
```
Esto garantiza inmunidad ante filas vacías al final de la hoja o fechas no contiguas en el Excel original.

### 🧠 Jerarquía Operacional en `assign_daily_turnos_fast`:
```python
def assign_daily_turnos_fast(grupos_list: list, turnos_list: list, perfs_list: list) -> list[str]:
    n = len(turnos_list)
    if n == 0: return []

    raw_turnos = [normalize_turno_val(t) for t in turnos_list]
    raw_grupos = [str(g).strip().replace(".0", "") if pd.notna(g) and str(g).strip() not in ("", "nan", "None", "0.0", "0") else "" for g in grupos_list]
    raw_perfs = [str(p or "").strip().upper() for p in perfs_list]
    raw_perfs = [p if p not in ("", "FALSO", "0.0", "NAN", "NONE", "0") else "" for p in raw_perfs]

    # FFILL: Propagar valores por celdas combinadas
    for i in range(1, n):
        if not raw_turnos[i]: raw_turnos[i] = raw_turnos[i-1]
        if not raw_grupos[i]: raw_grupos[i] = raw_grupos[i-1]
        if not raw_perfs[i]: raw_perfs[i] = raw_perfs[i-1]

    # 1. Caso de 1 sola fila en el día
    if n == 1:
        t0 = raw_turnos[0]
        if t0 in ("B", "N", "2", "2.0"): return ["B"]
        return ["A"]

    # 2. Caso de 2 filas en el día: Secuencia estándar (A = Día, B = Noche)
    if n == 2:
        return ["A", "B"]

    # 3. Caso de n >= 3 filas (Multi-sondaje o múltiples tramos en el día)
    # 3.1 Transición por GRUPO de guardia
    if any(g != "" for g in raw_grupos):
        g0 = next((g for g in raw_grupos if g != ""), "")
        if g0 != "":
            for i in range(1, n):
                gi = raw_grupos[i]
                if gi != "" and gi != g0:
                    return ["A" if idx < i else "B" for idx in range(n)]

    # 3.2 Transición por PERFORISTA
    if any(p != "" for p in raw_perfs):
        p0 = next((p for p in raw_perfs if p != ""), "")
        if p0 != "":
            for i in range(1, n):
                pi = raw_perfs[i]
                if pi != "" and pi != p0:
                    return ["A" if idx < i else "B" for idx in range(n)]

    # 3.3 Transición declarada en Turno (ej. A -> B)
    if any(t == "B" for t in raw_turnos):
        for i in range(1, n):
            if raw_turnos[i] == "B" and raw_turnos[i-1] == "A":
                return ["A" if idx < i else "B" for idx in range(n)]

    # 3.4 Reparto secuencial 50/50
    split = max(1, n // 2)
    return ["A" if i < split else "B" for i in range(n)]
```

---

## 3. Casos Borde Críticos Resueltos en Agosto 2026

### 🛠️ 1. Chungar (`LM90U-001`, Filas Residuales al Pie de Hoja)
* **Situación**: La hoja contenía una fila residual con fecha `2026-07-26` al final del libro (fila 52). El `groupby` agrupaba esta fila junto a las filas 0 y 1, provocando que `df_turnos.extend()` desfasara 1 posición a todas las filas del mes e invirtiera los turnos A y B de Agosto.
* **Resolución**: La asignación directa por índice `df.loc[idxs, "TURNO_ESTANDAR"]` erradicó el desfase, pasando de 44 falsos intercambios de turno a 0 en Chungar.

### 🛠️ 2. Condestable (`XRD80ITH-001`, 28.07 y 05.08)
* **Situación**: Días con 3 filas donde el operador de noche finaliza un pozo y arranca otro (ej. 28.07: Fila 1 = De La Cruz / Grupo 2 = 30.0 m; Filas 2 y 3 = Saire / Grupo 1 = 15.6 m + 12.5 m = 28.1 m). El digitador escribió `1.0` en la fila 2 por error.
* **Resolución**: La transición por `GRUPO` rotativo agrupó las filas 2 y 3 en Turno B, cuadrando con Control Interno al **100.00% exacto (30.0 m en A, 28.1 m en B)**.

### 🛠️ 3. Catalina Huanca (`XRD50U-003`, 09.08 y 10.08)
* **Situación**: Fila 1 = Vargas / Grupo 1 (Turno A) y Filas 2 y 3 = Chipana / Grupo 2 (Turno B) con múltiples subtramos.
* **Resolución**: Detección nativa del cambio de guardia asignando Fila 1 = `'A'` y Filas 2, 3 = `'B'`, cuadrando 100% contra Control Interno (**4.2 m vs 12.0 m** el 09.08 y **5.8 m vs 23.6 m** el 10.08).

---

## 🔗 Notas Relacionadas

- [[docs/04_matriz_conciliacion_y_auditoria|04. Matriz Comparativa, Conciliación Diaria y Diagnósticos]]
- [[docs/05_guia_ejecucion_y_mantenimiento|05. Guía de Ejecución, Automatización y Mantenimiento]]
