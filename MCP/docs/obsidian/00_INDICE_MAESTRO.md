# 🗺️ Índice Maestro: BI Control de Operaciones y Perforación (Rock Drill)

> [!NOTE]
> **Propósito del Vault:**
> Esta base de conocimientos documenta íntegramente la arquitectura de datos, el pipeline ETL en Polars, el modelo relacional tabular y el catálogo exhaustivo de fórmulas DAX del sistema de Business Intelligence **`RESIDENTES.pbix`** de **Rock Drill**.
>
> Diseñado para consulta rápida en **Obsidian**, auditoría técnica y reconstrucción total del dashboard desde cero.

---

## 🧭 Mapa de Contenidos (MOC)

```mermaid
mindmap
  root((BI Residentes Rock Drill))
    Arquitectura y ETL
      [[01_ARQUITECTURA_Y_ETL]]
      Pipeline Polars procesarv2.py
      Rutas de Archivos y Fuentes
      Esquema Estrella de Salida
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

---

## 📌 Metadatos del Sistema

* **Proyecto:** Dashboard de Residentes / Control de Operaciones de Perforación Diamantina (DDH) e Interior Mina.
* **Organización:** Rock Drill - Control de Proyectos.
* **Ruta de Trabajo Local:** `C:\Mis Archivos Locales\MCP BI`
* **Ruta PBIX Oficial:** `C:\Users\PERDLAP33\OneDrive - ROCK DRILL\Archivos de Pedro Gamarra - CONTROL DE PROYECTOS\12. DASHBOARD\Dashboard Previo\Residentes\BD\DashboardsV2\RESIDENTES.pbix`
* **Tecnologías:** Power BI Desktop / Analysis Services Tabular Engine, Python (Polars, Calamine, PBIXRay), Obsidian Markdown.
* **Última Actualización del Modelo:** Agosto 2026.
