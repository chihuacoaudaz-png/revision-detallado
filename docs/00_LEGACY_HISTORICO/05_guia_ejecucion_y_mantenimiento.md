---
title: 05. Guía de Ejecución, Automatización y Mantenimiento
aliases: [Guía de Ejecución, Manual de Operaciones, Pipeline CLI, Flujo Punta a Punta]
tags:
  - ejecucion
  - etl
  - jupyter
  - python
  - graphify
  - obsidian
  - automatizacion
created: 2026-08-13
updated: 2026-08-17
version: 2.2.0
---

# 🚀 05. Guía de Ejecución, Automatización y Mantenimiento

[[HANDOFF_KNOWLEDGE_BASE_OBSIDIAN|⬅️ Volver a la Base de Conocimiento Principal]]

---

## 🧭 1. Flujo Operativo Punta a Punta

El flujo completo del proyecto consta de 3 etapas secuenciales:

```mermaid
flowchart LR
    A["1. OWA Outlook (Correos Diarios)"] -->|"descargar_detallados.py"| B["2. Estructura Base (CTR_*/02_Detallado)"]
    B -->|"ejecutar_pipeline_completo.py"| C["3. Output (Consolidados y Conciliación)"]
    
    style A fill:#0078d4,stroke:#333,stroke-width:1px,color:#fff
    style B fill:#107c41,stroke:#333,stroke-width:1px,color:#fff
    style C fill:#d83b01,stroke:#333,stroke-width:1px,color:#fff
```

---

## 📦 2. Requisitos y Entorno de Ejecución

El proyecto opera con Python 3.11+ y requiere las siguientes librerías instaladas:

```bash
pip install pandas numpy python-calamine openpyxl python-dateutil playwright
python -m playwright install chromium
```

---

## ⚡ 3. Guía de Ejecución Diaria

### Paso 1: Configuración Inicial de Sesión (Solo la 1ra vez por usuario)
```bash
python descargar_detallados.py --setup
```
*Abre Edge, permite iniciar sesión con SSO de `@rockdrillgroup.com` y guarda el perfil localmente en `.sesiones/`.*

---

### Paso 2: Descargar Reportes Detallados del Día hacia `Estructura base`
```bash
# Para descargar los reportes recibidos hoy (perforación de ayer):
python descargar_detallados.py

# Para una fecha específica:
python descargar_detallados.py --fecha 17/08/2026

# Modo prueba (guarda en 'prueba correos/' sin sobreescribir Estructura base):
python descargar_detallados.py --fecha 17/08/2026 --prueba
```
*Cada reporte `.xlsx` descargado se ubica automáticamente en `Estructura base/Rockdrill_Control_Operaciones/CTR_{CTR}/02_Detallado/` limpiando el archivo anterior de esa carpeta.*

---

### Paso 3: Ejecutar el Pipeline ETL de Limpieza y Conciliación
```bash
# Ejecución completa (Detallados + Control Interno + Conciliación):
python ejecutar_pipeline_completo.py

# Solo limpiar Reportes Detallados:
python ejecutar_pipeline_completo.py --solo-detallados

# Solo compilar Control Interno:
python ejecutar_pipeline_completo.py --solo-ci

# Solo regenerar matriz de conciliación:
python ejecutar_pipeline_completo.py --solo-conciliacion
```

---

### Paso 4 (Opcional): Reconstruir y Ejecutar el Jupyter Notebook Explicativo
```bash
# Reconstruir el notebook con documentación celda por celda:
python build_notebook.py

# Ejecutar todas las celdas y validar aserciones al 100%:
python execute_notebook.py
```

---

## 📁 4. Estructura Limpia del Proyecto (Lista para OneDrive)

```text
C:\proyectos python\detallados\  (o carpeta compartida en OneDrive)
├── config.py                           # Resolución dinámica de rutas (Auto / Portable / Custom)
├── descargar_detallados.py             # Descargador automatizado OWA -> Estructura base
├── ejecutar_pipeline_completo.py       # Script principal de ejecución ETL
├── pipeline_limpieza.py                # Módulo central de limpieza de detallados
├── build_notebook.py                   # Generador del notebook explicativo
├── execute_notebook.py                 # Validador de aserciones en notebook
├── README.md                           # Documentación técnica principal
├── HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md  # Master Knowledge Base
├── GUIA_Y_UBICACION_DE_ARCHIVOS.md     # Catálogo de archivos
│
├── Estructura base\                    # Almacén maestro de datos (18 CTRs)
│   └── Rockdrill_Control_Operaciones\
│       ├── 00_Control_Interno\         # RD.402.P.01.F.04 Consolidado de Avance
│       ├── Maestro_Maquinas\           # Maestros_Maquinas.xlsx (Excepciones SAP)
│       └── CTR_{NOMBRE}\               # 18 carpetas CTR
│           ├── 01_Avance_Diario\       # Resúmenes ejecutivos F.03/F.07
│           └── 02_Detallado\           # Reporte Detallado F.01 (1 por CTR)
│
├── output\                             # Entregables consolidados generados
│   ├── detallados_consolidados.xlsx    # 135 columnas tipadas
│   ├── detallados_consolidados.csv     # Exportación CSV UTF-8 con BOM
│   ├── matriz_comparativa_metrajes.xlsx# Conciliación con Control Interno
│   └── auditoria_descargas\            # Reportes de auditoría de descarga OWA
│
├── 01_Control_Interno_ETL\             # Módulos especializados de Control Interno
├── notebook\                           # Notebook explicativo con 29 celdas
├── docs\                               # Documentación modular Obsidian (01 a 08)
├── tools\                              # Scripts de investigación y legacy organizados
│   ├── scripts_investigacion\          # Herramientas de análisis, dom y profiling
│   ├── powerquery_m_legacy\            # Códigos M y scripts de Power Query reemplazados
│   └── descargas_experimentos\         # Descargadores experimentales previos
└── .sesiones\                          # Perfiles de autenticación local por usuario
```

---

## 🔒 5. Variables de Configuración en `ejecutar_pipeline_completo.py`

En la cabecera de `ejecutar_pipeline_completo.py` se encuentran las variables configurables:

```python
# 1. Rutas (resueltas automáticamente vía config.py)
BASE_PATH = resolve_base_data_path()
OUTPUT_PATH = REPO_ROOT / "output"
CONTROL_INTERNO_PATH = resolve_control_interno_path(BASE_PATH)

# 2. Exclusiones de hojas no operativas
HOJAS_EXCLUIDAS = {"ADITIVOS", "GENERAL", "LISTAS", "Tiempos", "RESUMEN", "GRAFICOS"}
CTRS_EXCLUIDOS = {"COLQUIJIRCA"}

# 3. Parámetros de lectura Excel
MIN_ROWS = 24
SKIP_ROWS = 22  # Fila 23 del Excel (cabecera dual en 23 y 24)
```

---

## 🔗 Notas Relacionadas

- [[docs/06_flujo_descarga_correos_outlook_y_ctrs|06. Flujo de Descarga de Correos OWA]]
- [[docs/08_guia_descargador_portable|08. Guía de Uso del Descargador Portable]]
- [[docs/01_arquitectura_y_pipeline_etl|01. Arquitectura del Pipeline y Sustitución de Power Query]]
- [[docs/04_matriz_conciliacion_y_auditoria|04. Matriz Comparativa, Conciliación Diaria y Diagnósticos]]
