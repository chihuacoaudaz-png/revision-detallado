# 🗺️ Guía y Ubicación de Archivos del Proyecto - Rockdrill

Este documento detalla la función exacta de cada archivo y carpeta en el repositorio tras la reestructuración limpia.

---

## 📌 Archivos Principales en la Raíz

| Archivo | Tipo | Propósito |
| :--- | :--- | :--- |
| [`config.py`](file:///C:/proyectos%20python/detallados/config.py) | **Configuración** | Centraliza rutas, resolución dinámica (OneDrive / Local) y parámetros operativos. |
| [`descargar_detallados.py`](file:///C:/proyectos%20python/detallados/descargar_detallados.py) | **Descargador OWA** | Descarga los 18 reportes detallados desde Outlook y los ubica en sus carpetas oficiales. |
| [`ejecutar_pipeline.py`](file:///C:/proyectos%20python/detallados/ejecutar_pipeline.py) | **ETL Principal** | Orquesta la limpieza de 135 columnas, compilación de Control Interno y reconciliación. |
| [`requirements.txt`](file:///C:/proyectos%20python/detallados/requirements.txt) | **Dependencias** | Lista de paquetes Python necesarios (`pandas`, `python-calamine`, `playwright`, etc.). |
| [`README.md`](file:///C:/proyectos%20python/detallados/README.md) | **Manual de Usuario** | Guía de operación paso a paso en lenguaje claro para cualquier usuario o administrador. |
| [`HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md`](file:///C:/proyectos%20python/detallados/HANDOFF_KNOWLEDGE_BASE_OBSIDIAN.md) | **Knowledge Base** | Base de conocimiento maestra para Obsidian con el índice general de arquitectura. |

---

## 📂 Carpetas del Repositorio

| Carpeta | Contenido |
| :--- | :--- |
| [`src/`](file:///C:/proyectos%20python/detallados/src) | **Código Fuente Modular**: `etl_detallados.py`, `etl_control_interno.py`, `reconciliacion.py`, `utils.py`, `pipeline.py`. |
| [`Estructura base/`](file:///C:/proyectos%20python/detallados/Estructura%20base) | **Almacén de Datos Operativos**: Las 18 carpetas `CTR_{NOMBRE}` con `01_Avance_Diario` y `02_Detallado`, más `00_Control_Interno` y `Maestro_Maquinas`. |
| [`output/`](file:///C:/proyectos%20python/detallados/output) | **Entregables Oficiales**: `detallados_consolidados.xlsx/csv`, `matriz_comparativa_metrajes.xlsx` y reportes de auditoría de descargas. |
| [`notebooks/`](file:///C:/proyectos%20python/detallados/notebooks) | **Cuadernos Jupyter**: `ETL_Limpieza_Detallados_y_Control_Interno.ipynb` con explicación celda por celda. |
| [`docs/`](file:///C:/proyectos%20python/detallados/docs) | **Notas Obsidian**: Documentación modular del 01 al 08 (Algoritmo de turnos, Diccionario 135 cols, Conciliación, Descargador, etc.). |
| [`tests/`](file:///C:/proyectos%20python/detallados/tests) | **Pruebas Automatizadas**: Tests unitarios de lógica de negocio, turnos y encabezados. |
| [`tools/`](file:///C:/proyectos%20python/detallados/tools) | **Herramientas de Desarrollo**: Scripts históricos de investigación, profiling y códigos legacy archivados. |
| [`.sesiones/`](file:///C:/proyectos%20python/detallados/.sesiones) | **Perfiles de Autenticación**: Sesiones locales de Microsoft Edge (1 carpeta por usuario). |
