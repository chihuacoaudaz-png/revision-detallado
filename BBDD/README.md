# 🗄️ MÓDULO BBDD: GENERADOR DE BASE DE DATOS DIMENSIONAL (KIMBALL STAR SCHEMA)
## Rockdrill Group — Sistema Integral de Analítica y Business Intelligence

**Ubicación:** [`BBDD/`](file:///c:/Proyectos%20Python/Detallados/BBDD)  
**Script Principal:** [`generar_base_datos_dimensional.py`](file:///c:/Proyectos%20Python/Detallados/BBDD/generar_base_datos_dimensional.py)  
**Lanzador Rápido:** [`EJECUTAR_BBDD.bat`](file:///c:/Proyectos%20Python/Detallados/BBDD/EJECUTAR_BBDD.bat)  
**Base Oficial de Entrada:** [`CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx`](file:///c:/Proyectos%20Python/Detallados/Estructura%20base/Rockdrill_Control_Operaciones/Base%20de%20datos/CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx) (176 columnas)

---

## 📖 1. ¿QUÉ HACE ESTE MÓDULO?

Este módulo transforma directamente el archivo maestro generado por Power Query:  
**`CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx`** (ubicado en `Rockdrill_Control_Operaciones\Base de datos`)  
en un **Esquema Estrella Dimensional (Kimball)** de alto desempeño optimizado para Power BI, SQL Server, PostgreSQL, Snowflake y Microsoft Fabric.

El algoritmo procesa las 176 columnas y 3,505 filas operativas del periodo mensual completo (del 26 de agosto al 25 de septiembre de 2026), separándolas limpiamente en:
* **7 Tablas de Dimensiones (Filtros):** Fechas, Contratos, Máquinas, Diámetros, Personal, Sondajes con parámetros de diseño y Taxonomía de Actividades.
* **3 Tablas de Hechos (Métricas):** Metrajes de perforación, Horas operativas unpivoteadas en 5 categorías y Metas mensuales.
* **1 Tabla Puente:** Cuadrillas y asignaciones de personal por guardia.

---

## ⚙️ 2. CÓMO CONFIGURAR LAS VARIABLES (EN LOCAL O EN ONEDRIVE / NUBE)

Abra el archivo [`generar_base_datos_dimensional.py`](file:///c:/Proyectos%20Python/Detallados/BBDD/generar_base_datos_dimensional.py) con cualquier editor de texto o código (Notepad, VS Code, etc.). En las primeras líneas encontrará las variables configurables:

```python
# =============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES DEL SISTEMA (MODIFICAR SEGÚN EL ENTORNO)
# =============================================================================
# 1. RUTA OFICIAL DEL ARCHIVO CONSOLIDADOR POWERQUERY:
#    Este es el archivo consolidado oficial generado por Power Query con las 176 columnas.
#
#    -> RUTA EN DISCO LOCAL:
#    RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
#
#    -> RUTA EN LA NUBE / ONEDRIVE (Para ejecutar sincronizado en OneDrive del trabajo):
#    Reemplace 'TU_USUARIO' por su usuario de Windows o la ruta exacta donde sincroniza su OneDrive:
#    RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Users\TU_USUARIO\OneDrive - Rockdrill Group\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
#
#    -> RUTA DE LA CARPETA GENERAL 'Rockdrill_Control_Operaciones' (Opcional):
#    Si traslada la carpeta completa, el script buscará automáticamente 'Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx':
RUTA_CONSOLIDADOR_POWERQUERY = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"
RUTA_CARPETA_OPERACIONES    = r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones"

# 2. RUTA DE DESTINO PARA LA BASE DE DATOS DIMENSIONAL (Esquema Estrella):
#    Carpeta donde se guardarán las 11 tablas generadas en formatos CSV, Parquet y Excel.
RUTA_DESTINO_BBDD           = r"C:\Proyectos Python\Detallados\BBDD\output_star_schema"

# 3. FORMATOS DE EXPORTACIÓN (Activar con True o desactivar con False):
GENERAR_ARCHIVOS_CSV        = True
GENERAR_ARCHIVOS_PARQUET    = True
GENERAR_EXCEL_MAESTRO      = True

# 4. HOJA DE LECTURA DENTRO DEL CONSOLIDADOR:
HOJA_CONSOLIDADA_EXCEL      = "Consolidado_Operaciones"
# =============================================================================
```

> [!TIP]
> **Para copiarlo y ejecutarlo en la nube / OneDrive:**  
> 1. Copie la carpeta `BBDD` a la máquina o carpeta donde tenga sincronizado OneDrive.
> 2. Abra `generar_base_datos_dimensional.py` y modifique la línea de `RUTA_CONSOLIDADOR_POWERQUERY` colocando la ruta a su carpeta OneDrive:  
>    `r"C:\Users\<SU_USUARIO>\OneDrive - Rockdrill Group\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"`
> 3. ¡Listo! Ejecute `EJECUTAR_BBDD.bat` o el script de Python.

---

## 🚀 3. CÓMO EJECUTAR EL ALGORITMO

Tiene 2 formas sencillas de ejecutar el proceso:

### Opción A: Doble Clic (Recomendado para Usuarios y Administradores)
Haga doble clic en el archivo:  
👉 **`EJECUTAR_BBDD.bat`**  
Se abrirá una ventana de comandos que ejecutará la separación automáticamente y mostrará el resumen de filas generadas. Si la máquina no tiene Python configurado en el PATH, el archivo `.bat` ejecutará automáticamente el binario independiente compilado [`EJECUTAR_BBDD/EJECUTAR_BBDD.exe`](file:///c:/Proyectos%20Python/Detallados/BBDD/EJECUTAR_BBDD/EJECUTAR_BBDD.exe).

### Opción B: Desde la Terminal (PowerShell o CMD)
```bash
cd "C:\Proyectos Python\Detallados\BBDD"
python generar_base_datos_dimensional.py
```

---

## 📊 4. TABLAS GENERADAS EN `output_star_schema/`

Al finalizar la ejecución, se generarán en la subcarpeta `output_star_schema/` los siguientes archivos:

| Nombre de la Tabla | Tipo | Filas | Descripción de Contenido |
| :--- | :---: | :---: | :--- |
| **`dim_tiempo_calendario`** | Dimensión | 62 | Calendario con semanas ISO civiles y semanas operativas del ciclo 26 al 25. |
| **`dim_contrato_minero`** | Dimensión | 19 | 18 contratos mineros con `tipo_operacion = 'SUBTERRANEA'`. |
| **`dim_equipo_perforadora`** | Dimensión | 59 | Máquinas con `tipo_servicio = 'SUPERFICIE' / 'INTERIOR MINA'`. |
| **`dim_linea_diametro`** | Dimensión | 5 | Líneas de corte (PQ, HQ, NQ, BQ, HWT) y especificaciones en mm. |
| **`dim_personal`** | Dimensión | 412 | Catálogo unificado de perforistas y ayudantes. |
| **`dim_sondaje_taladro`** | Dimensión | 121 | Sondajes con metas geológicas: profundidad programada, línea e inclinación. |
| **`dim_taxonomia_actividad`**| Dimensión | 94 | 116 actividades agrupadas en las 5 categorías oficiales de disponibilidad. |
| **`fact_perforacion_avance`**| Hechos | 3,505 | Metraje perforado (**7,502.91 m**), cotas, brocas (`n_broca`), casing, horómetros y bitácora. |
| **`fact_horas_operativas`** | Hechos | 4,747 | Tiempos operativos unpivoteados filtrados a horas $> 0$. |
| **`brg_cuadrilla_guardia`** | Puente | 4,820 | Asignaciones de personal y horas extras por guardia. |
| **`fact_metas_mensuales`**  | Hechos | 58 | Metas operativas y proyecciones por máquina. |
| **`ESQUEMA_ESTRELLA_COMPLETO.xlsx`** | Consolidado | 11 hojas | Libro maestro de Excel con todas las tablas dimensionales. |

---

## 🛡️ 5. AUDITORÍA Y CONTROL DE CALIDAD

El script verifica automáticamente que:
1. El **Metraje Total** sea exactamente **7,502.91 m** (coincidencia exacta al 100.00% con la base de Power Query).
2. Todas las llaves foráneas coincidan al 100% con sus dimensiones (cero llaves huérfanas).
3. Todas las dimensiones incluyan el registro comodín desconocido (`sk = -1`) para evitar caídas en Power BI si faltan datos en campo.
