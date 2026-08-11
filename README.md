# Pipeline ETL de Reportes Detallados y Auditoría de Control Interno (Rockdrill)

Este repositorio contiene la arquitectura completa del pipeline de Extracción, Transformación y Carga (ETL), conciliación de metrajes por `ID_CLAVE_UNICA` y la documentación técnica para la limpieza automatizada de los **Reportes Detallados por Equipo** (`RD.402.P.01.F.01`) y el libro maestro de **Control Interno** (`RD.402.P.01.F.04`).

---

## 🚀 Guía de Inicio Rápido (Restaurar y Ejecutar en Cualquier PC)

Para clonar este repositorio y retomar el proyecto en cualquier computadora (Windows, Linux, macOS), ejecuta la siguiente secuencia de comandos en tu terminal **Bash / PowerShell**:

### 1. Clonar el Repositorio de GitHub
```bash
git clone https://github.com/chihuacoaudaz-png/revision-detallado.git
cd revision-detallado
```

### 2. Crear el Entorno Virtual de Python e Instalar Dependencias
```bash
python -m venv venv

# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# En Linux / macOS / Git Bash:
source venv/bin/activate

# Instalar librerías requeridas:
pip install python-calamine pandas openpyxl numpy python-dateutil
```

### 3. Ejecutar el Pipeline ETL y la Matriz Comparativa
```bash
# 1. Procesar y consolidar los Reportes Detallados (18 CTRs):
python pipeline_limpieza.py

# 2. Compilar la planilla de Control Interno (30 reportes diarios):
python 01_Control_Interno_ETL/compilar_control_interno.py

# 3. Generar la Matriz Comparativa por Clave Única (Conciliación Guardia a Guardia):
python 01_Control_Interno_ETL/matriz_comparativa_metrajes.py
```

---

## 📂 Estructura del Proyecto

```text
revision-detallado/
│
├── pipeline_limpieza.py                      # Pipeline ETL principal de Reportes Detallados
├── output/                                   # Resultados consolidados
│   ├── detallados_consolidados.csv           # 134 columnas oficiales
│   └── detallados_consolidados.xlsx          # Consolidado en Excel
│
├── 01_Control_Interno_ETL/                   # Módulo de Control Interno y Auditoría
│   ├── compilar_control_interno.py           # ETL de Control Interno
│   ├── matriz_comparativa_metrajes.py        # Algoritmo de Outer Join y Conciliación
│   ├── analisis_discrepancias_metrajes.md    # Reporte definitivo de auditoría (100% verificado)
│   └── output/
│       ├── matriz_comparativa_metrajes.xlsx  # Matriz comparativa por clave única
│       ├── discrepancias_diarias_detalladas.csv
│       └── resumen_discrepancias_ctr.csv
│
├── docs/                                     # Documentación Técnica Completa (Handoff & M)
│   ├── handoff_detallados.md                 # Grupo 1: Estado del proyecto y stack Python
│   ├── handoff_control_interno.md            # Grupo 1: Estado de Control Interno
│   ├── logica_m_campos_detallados.md         # Grupo 2: Traducción M y tipos para Power BI
│   ├── logica_m_campos_control_interno.md    # Grupo 2: Traducción M de Control Interno
│   ├── replicacion_detallada_detallados.md   # Grupo 3: Manual de replicación desde cero
│   └── replicacion_detallada_control_interno.md # Grupo 3: Manual de replicación Control Interno
│
├── .gitignore
└── README.md
```

---

## 📊 Resultados de Conciliación de Metrajes (Auditoría Empírica)

- **17 de los 18 CTRs** registran **0.00 m de diferencia acumulada** (coincidencia exacta al centímetro).
- **CHUNGAR**: `2,347.55 m` vs `2,347.55 m` (Diferencia: **0.00 m**). Resuelto caso de metraje inicial (06-jul Turno B 1.50m) mediante regla secuencial `.ffill().bfill()` de asignación de sondaje.
- **MOROCOCHA**: `1,842.80 m` vs `1,842.80 m` (Diferencia: **0.00 m**).
- **YAULIYACU**: `2,553.80 m` vs `2,428.40 m` (Diferencia: **+125.40 m**). Explicado por la perforación de un **sondaje paralelo no cobrable** en la máquina `XRD125USS-001`. Se incorporó el campo `SONDAJE_PARALELO` (default = `1`) al final del dataset para su gestión en Power Query.
- **CONDESTABLE (0.00 m)** y **CUCULÍ (0.00 m)**: Resueltos al aplicar filtro de hojas visibles (`sheet.visible`).
- **COLQUIJIRCA**: Excluido de negocio por no llevarse control de metrajes.

---

## 🛠️ Estructura de Columnas Exportadas (135 Columnas)

1. **Matriz Nativa Original (Columnas 1 - 129)**: Preserva los 129 campos del reporte diario `RD.402.P.01.F.01`, incluyendo `TURNO (A=1;B=2)` en su ubicación original de la matriz.
2. **Campos Calculados / Metadatos (al final del dataset)**:
   - `HOJA DE TRABAJO ORIGEN`: Nombre de la pestaña de origen.
   - `ARCHIVO ORIGEN`: Nombre del libro Excel de origen.
   - `TURNO_ESTANDAR`: Turno estandarizado en `'A'` (Día) o `'B'` (Noche).
   - `ID_CLAVE_UNICA`: Clave de trazabilidad `{FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}`.
   - `SONDAJE_PARALELO`: Indicador entero/booleano para marcar sondajes paralelos (default `1`).
   - `Alerta_Comentarios`: 'OK' o 'FALTA COMENTARIO'.
