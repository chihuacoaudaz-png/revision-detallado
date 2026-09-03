# 🗺️ Índice Maestro: BI Control de Operaciones y Perforación (Rock Drill)

> [!NOTE]
> **Propósito del Vault:**
> Esta base de conocimientos documenta íntegramente la arquitectura de datos, el pipeline ETL en Python/Polars, el recopilador en Power Query M (168 columnas), el modelo relacional tabular y el catálogo exhaustivo de fórmulas DAX del sistema de Business Intelligence **`RESIDENTES.pbix`** de **Rock Drill**.
>
> Diseñado para consulta rápida en **Obsidian**, auditoría técnica y reconstrucción total del dashboard desde cero.

---

## 🧭 Mapa de Contenidos (MOC)

```mermaid
mindmap
  root((BI Residentes Rock Drill))
    Arquitectura y ETL
      [[01_ARQUITECTURA_Y_ETL]]
      Pipeline Polars y Python
      Rutas de Archivos y Fuentes
      Esquema Estrella de Salida
    Recopilador Power Query M
      [[07_RECOPILADOR_POWERQUERY_Y_168_COLUMNAS]]
      Ecosistema 168 Columnas A:FL
      Corrección Duplicado 2X
      Auditoría vs Control Interno
    Motor Encabezados y Casos Borde
      [[08_MOTOR_DE_ENCABEZADOS_Y_CASOS_BORDE_ETL]]
      Cabeceras Dual-Row Fills
      Aislamiento FillDown
      Homologación SAP
    Diccionario de Datos
      [[02_DICCIONARIO_DE_DATOS]]
      Tablas de Hechos (Facts)
      Tablas de Dimensiones (Dims)
      Tipos y Llaves Primarias
    Modelo Relacional
      [[03_MODELO_RELACIONAL]]
      Diagrama Estrella ERD
      Relaciones 1:N y Puentes M:M
      Direcciones de Filtro Cruzado
    Catálogo de Medidas DAX
      [[04_CATALOGO_MEDIDAS_DAX]]
      Cluster ROP y Rendimiento
      Cluster Metraje y Avance
      Cluster Metas y Proyecciones
      Cluster Costos y Presupuestos
    Metraje Perdido Ajustado
      [[05_SISTEMA_METRAJE_PERDIDO_AJUSTADO]]
      ROP_Efectivo y f_efectivo
      Reglas por CTR (11h, 10.15h, 12h)
      Matriz de Desglose de Horas
    Guía de Reconstrucción Total
      [[06_GUIA_RECONSTRUCCION_TOTAL]]
      Paso a Paso desde Cero
      Power Query M Scripts
      Estructura de Visuales y Filtros
    Habilitación CAPITANA
      [[09_ACTUALIZACION_Y_HABILITACION_CAPITANA]]
      Desbloqueo Filtros M
      Cuadratura 1-a-1 Metrajes
      Modelo Dimensional XRD150U-010
```

---

## 📑 Módulos de Documentación

| Módulo | Documento | Descripción Clave |
| :--- | :--- | :--- |
| **01** | [[01_ARQUITECTURA_Y_ETL\|Arquitectura y ETL]] | Origen de datos Excel, pipeline `procesarv2.py` (Polars), normalización y exportación de CSVs. |
| **02** | [[02_DICCIONARIO_DE_DATOS\|Diccionario de Datos]] | Definición detallada de las 13 tablas, 140+ columnas, tipos de datos y dominios de negocio. |
| **03** | [[03_MODELO_RELACIONAL\|Modelo Relacional Tabular]] | Arquitectura estrella/copo de nieve, llaves (`KEY_OPERACION`), cardinalidades y diagramas Mermaid. |
| **04** | [[04_CATALOGO_MEDIDAS_DAX\|Catálogo de Medidas DAX]] | Diccionario de más de 116 medidas DAX clasificadas por área funcional y fórmulas completas. |
| **05** | [[05_SISTEMA_METRAJE_PERDIDO_AJUSTADO\|Sistema de Metraje Perdido]] | Formulación matemática de ROP Efectivo, factor $f_{\text{efectivo}}$ por CTR y matriz de stand-by. |
| **06** | [[06_GUIA_RECONSTRUCCION_TOTAL\|Guía de Reconstrucción Total]] | Manual paso a paso para levantar el proyecto desde cero en un `.pbix` en blanco. |
| **07** | [[07_RECOPILADOR_POWERQUERY_Y_168_COLUMNAS\|Recopilador Power Query M y 168 Cols]] | Arquitectura Power Query M de 168 columnas, corrección del duplicado 2X y conciliación diaria. |
| **08** | [[08_MOTOR_DE_ENCABEZADOS_Y_CASOS_BORDE_ETL\|Motor de Encabezados y Casos Borde]] | Construcción dual-row de cabeceras, forward-fill horizontal, `FillDown`/`FillUp` y homologación SAP. |
| **09** | [[09_ACTUALIZACION_Y_HABILITACION_CAPITANA\|Habilitación Contrato CAPITANA]] | Diagnóstico, desbloqueo en Power Query M (F01/F04), cuadratura 1-a-1 y modelo dimensional. |

---

## 📌 Metadatos del Sistema

* **Proyecto:** Dashboard de Residentes / Control de Operaciones de Perforación Diamantina (DDH) e Interior Mina.
* **Organización:** Rock Drill - Control de Proyectos.
* **Ruta de Trabajo Local:** `C:\Proyectos Python\Detallados`
* **Ruta PBIX Oficial:** `C:\Users\PERDLAP33\OneDrive - ROCK DRILL\Archivos de Pedro Gamarra - CONTROL DE PROYECTOS\12. DASHBOARD\Dashboard Previo\Residentes\BD\DashboardsV2\RESIDENTES.pbix`
* **Tecnologías:** Power BI Desktop / Analysis Services Tabular Engine, Python (Polars, Calamine, OpenPyXL), Power Query M, Obsidian Markdown.
* **Última Actualización del Modelo:** Setiembre 2026.
