# 📊 BI Control de Operaciones y Residentes - Rock Drill

Repositorio técnico y base de conocimientos para el sistema de Business Intelligence **`RESIDENTES.pbix`** de Control de Proyectos (Rock Drill).

---

## 🗂️ Estructura del Repositorio (Buenas Prácticas)

```
.
├── docs/
│   └── obsidian/                      # 📚 Knowledge Base completa para Obsidian
│       ├── 00_INDICE_MAESTRO.md        # Mapa de contenidos (MOC)
│       ├── 01_ARQUITECTURA_Y_ETL.md    # Pipeline de datos y script Polars
│       ├── 02_DICCIONARIO_DE_DATOS.md  # Diccionario exhaustivo de 13 tablas
│       ├── 03_MODELO_RELACIONAL.md     # Esquema estrella y 23 relaciones
│       ├── 04_CATALOGO_MEDIDAS_DAX.md  # Catálogo clasificado de 116 medidas DAX
│       ├── 05_SISTEMA_METRAJE_PERDIDO_AJUSTADO.md # Ingeniería ROP y pérdida de metros
│       └── 06_GUIA_RECONSTRUCCION_TOTAL.md        # Manual paso a paso desde cero
├── src/
│   ├── etl/                           # ⚙️ Pipeline ETL en Python (Polars)
│   │   └── procesarv2.py              # Script principal de extracción y normalización
│   └── tools/                         # 🛠️ Utilidades de inspección y diagnóstico
│       ├── inspect_v2.py
│       ├── inspect_deep.py
│       ├── inspect_presupuesto.py
│       ├── inspect_final.py
│       └── diag_modelo.py
├── dax/                               # 📐 Archivos DAX consolidados
│   └── medidas_completas.dax          # Código DAX de todas las medidas del modelo
├── archive/                           # 📦 Scripts de testing y logs históricos
└── README.md                          # Este archivo
```

---

## 🚀 Inicio Rápido

1. **Documentación en Obsidian:**
   Abre la carpeta `docs/obsidian` como un Vault en Obsidian para navegar los enlaces bidireccionales, diagramas Mermaid y fórmulas.
2. **Ejecutar ETL:**
   ```bash
   python src/etl/procesarv2.py
   ```
3. **Catálogo DAX:**
   Consulta `dax/medidas_completas.dax` o `docs/obsidian/04_CATALOGO_MEDIDAS_DAX.md`.
