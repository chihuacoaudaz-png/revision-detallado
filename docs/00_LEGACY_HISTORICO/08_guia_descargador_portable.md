---
title: 08. Guía de Uso del Descargador Portable de Detallados
aliases: [Descargador Portable, Setup Descargador, Guía de Instalación]
tags:
  - guia
  - setup
  - portable
  - playwright
  - owa
  - rockdrill
  - obsidian-vault
created: 2026-08-17
updated: 2026-08-17
status: active
version: 1.0.0
---

# 🚀 08. Guía de Uso del Descargador Portable de Detallados

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 🎯 1. ¿Qué es?

`descargar_detallados.py` es el script **definitivo y portable** para descargar automáticamente los 18 Reportes Detallados de Avance (`RD.402.P.01.F.01`) desde OWA (Outlook Web App).

### Características:
- ✅ **Portable**: Cualquier usuario de Rockdrill puede ejecutarlo
- ✅ **Bilingüe**: Compatible con OWA en Español e Inglés
- ✅ **Seguro**: Solo descarga archivos de la fecha exacta indicada
- ✅ **Auditable**: Genera Excel de mapeo y tiempos de ejecución
- ✅ **Perfiles por usuario**: Cada persona tiene su propia sesión

---

## 📋 2. Requisitos Previos

| Requisito | Detalle |
|:---|:---|
| **Microsoft Edge** | Instalado en el equipo |
| **Sesión de correo** | Correo `@rockdrillgroup.com` con sesión activa en Edge |
| **Python 3.9+** | Con pip instalado |
| **Paquetes Python** | `playwright`, `pandas`, `openpyxl` |

### Instalación de paquetes:

```bash
pip install playwright pandas openpyxl
python -m playwright install chromium
```

---

## ⚙️ 3. Configuración Inicial (Primera vez)

Cada usuario debe ejecutar el setup **una sola vez** por equipo:

```bash
python descargar_detallados.py --setup
```

Este comando:
1. Te pide tu nombre (ej: `cesar.contreras`)
2. Abre Edge con un perfil limpio
3. Te redirige a OWA para que inicies sesión
4. Guarda las cookies de tu sesión localmente en `.sesiones/{tu_nombre}/`
5. Crea `.descargador_config.json` con tu perfil activo

> [!IMPORTANT]
> **La sesión se guarda localmente.** Tus credenciales NO se almacenan en texto plano.
> Solo se persisten las cookies del navegador, igual que cuando usas Edge normalmente.

---

## 🔧 4. Uso Diario

### Descargar reportes de una fecha específica:
```bash
python descargar_detallados.py --fecha 17/08/2026
```

### Descargar reportes de hoy:
```bash
python descargar_detallados.py
```

### Usar un perfil de usuario diferente:
```bash
python descargar_detallados.py --fecha 17/08/2026 --usuario juan.perez
```

---

## 📅 5. Regla de Fecha

$$\text{Fecha del correo} = \text{Día } N \implies \text{Perforación} = \text{Día } (N - 1)$$

| Si quieres los reportes de perforación del... | Usa `--fecha` con... |
|:---|:---|
| 16 de agosto | `17/08/2026` |
| 13 de agosto | `14/08/2026` |
| Ayer | *(fecha de hoy, que es el default)* |

---

## 🔒 6. Seguridad: Solo Fecha Exacta

> [!WARNING]
> El script **SOLO descarga correos de la fecha exacta indicada**.
> No hay fallback a fechas anteriores. Esto previene errores como
> descargar el archivo del día 14 cuando se pide el del 17.

Si un CTR no envió su reporte en la fecha indicada, aparecerá como `FALTANTE` en el mapeo. Esto es **intencional**: es mejor un faltante que un archivo incorrecto.

---

## 📂 7. Estructura de Archivos Generados

```text
C:\proyectos python\detallados\
├── .sesiones\                          # Perfiles de sesión por usuario
│   ├── cesar.contreras\                # Perfil de César
│   └── juan.perez\                     # Perfil de Juan
├── .descargador_config.json            # Config del último usuario activo
├── prueba correos\                     # Reportes descargados (se limpia cada ejecución)
│   ├── RD.402.P.01.F.01 ... AMERICANA.xlsx
│   ├── RD.402.P.01.F.01 ... CERRO.xlsx
│   ├── ... (16-18 archivos .xlsx)
│   ├── _MAPEO_EXACTO_17_08_2026.xlsx   # Auditoría: qué se descargó y qué faltó
│   └── _TIEMPOS_EJECUCION_17_08_2026.xlsx  # Profiling de tiempos por CTR
└── descargar_detallados.py             # Este script
```

---

## ❓ 8. Troubleshooting

### "No hay perfil de sesión configurado"
→ Ejecutar `python descargar_detallados.py --setup`

### "OWA no carga / timeout al buscar"
→ Verificar que tu sesión de correo siga activa. Puede que la cookie haya expirado.
→ Ejecutar `--setup` de nuevo para refrescar la sesión.

### "CTR aparece como FALTANTE"
→ Verificar manualmente en OWA si el correo existe para esa fecha.
→ Si el CTR envió tarde (al día siguiente), usar la fecha de recepción correcta.

### "Edge no abre / error de Playwright"
→ Verificar que no haya otra instancia de Edge usando el mismo perfil.
→ Cerrar todos los procesos de Edge y reintentar.

---

## 🔗 Notas Relacionadas

- [[docs/06_flujo_descarga_correos_outlook_y_ctrs|06. Flujo de Descarga y Catálogo de CTRs]]
- [[docs/07_analisis_rendimiento_descargador|07. Análisis de Rendimiento]]
- [[docs/05_guia_ejecucion_y_mantenimiento|05. Guía de Ejecución y Mantenimiento]]
