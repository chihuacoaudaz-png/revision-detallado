===============================================================================
  ROCKDRILL GROUP - GENERADOR DE BASE DE DATOS DIMENSIONAL (KIMBALL)
  DOCUMENTO DE INSTRUCCIONES Y MANUAL DE USO (FORMATO TEXTO PLANO)
===============================================================================

Ubicacion de esta carpeta: BBDD/
Script principal: generar_base_datos_dimensional.py
Lanzador de un solo clic: EJECUTAR_BBDD.bat
Archivo base oficial: CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx (176 columnas)

-------------------------------------------------------------------------------
1. QUE HACE ESTE PROGRAMA?
-------------------------------------------------------------------------------
Este programa toma la informacion directamente del archivo oficial consolidado
por Power Query: 'CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx' ubicado en la
carpeta 'Rockdrill_Control_Operaciones\Base de datos' y separa sus 176 columnas
en un Modelo Dimensional Estrella (Kimball) listo para Power BI, Excel o SQL.

Procesa las 3,505 filas operativas del periodo mensual completo (del 26 de
agosto al 25 de septiembre de 2026), generando 11 tablas en total:
- 7 Tablas de Dimensiones (Filtros): Fechas, Contratos, Maquinas, Diametros,
  Personal, Sondajes con diseno geologico y Taxonomia de 5 Categorias.
- 3 Tablas de Hechos (Metricas): Metrajes perforados (7,502.91 m), Horas
  operativas desglosadas (4,747 eventos) y Metas mensuales.
- 1 Tabla Puente: Asignacion de cuadrillas por guardia (4,820 registros).

Todo se exporta a formatos CSV, Parquet (alta velocidad) y un libro Excel
maestro llamado 'ESQUEMA_ESTRELLA_COMPLETO.xlsx'.


-------------------------------------------------------------------------------
2. COMO CONFIGURAR LAS RUTAS (EN LOCAL O EN ONEDRIVE / NUBE)?
-------------------------------------------------------------------------------
Abra el archivo 'generar_base_datos_dimensional.py' con el Bloc de Notas
(Notepad) o cualquier editor. En la parte superior vera las variables:

A) RUTA_CONSOLIDADOR_POWERQUERY:
   Ruta del archivo Excel maestro generado por Power Query.

   -> Si trabaja en su computadora local (Ruta por defecto):
     r"C:\Proyectos Python\Detallados\Estructura base\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"

   -> Si trabaja en la nube o sincroniza con OneDrive del trabajo:
     r"C:\Users\SU_USUARIO\OneDrive - Rockdrill Group\Rockdrill_Control_Operaciones\Base de datos\CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx"

B) RUTA_CARPETA_OPERACIONES:
   Ruta a la carpeta principal 'Rockdrill_Control_Operaciones'. Si traslada
   toda la carpeta, el algoritmo buscara automaticamente el archivo
   'CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx' en la subcarpeta 'Base de datos'.

C) RUTA_DESTINO_BBDD:
   Carpeta donde se guardaran las 11 tablas generadas.
   Por defecto se guarda en: 'BBDD\output_star_schema'.

D) FORMATOS A GENERAR:
   GENERAR_ARCHIVOS_CSV = True
   GENERAR_ARCHIVOS_PARQUET = True
   GENERAR_EXCEL_MAESTRO = True


-------------------------------------------------------------------------------
3. COMO EJECUTAR EL PROGRAMA?
-------------------------------------------------------------------------------
OPCION 1 (RECOMENDADA - UN SOLO CLIC):
  Haga doble clic sobre el archivo 'EJECUTAR_BBDD.bat'.
  - Si tiene Python instalado, ejecutara el codigo al instante.
  - Si la computadora NO tiene Python, iniciara automaticamente el ejecutable
    independiente 'EJECUTAR_BBDD.exe' incluido en la subcarpeta.

OPCION 2 (LINEA DE COMANDOS):
  Abra PowerShell o CMD en esta carpeta y escriba:
  python generar_base_datos_dimensional.py


-------------------------------------------------------------------------------
4. TABLAS GENERADAS EN 'output_star_schema/'
-------------------------------------------------------------------------------
1.  dim_tiempo_calendario     : Fechas, semanas civiles y semanas operativas (26 al 25).
2.  dim_contrato_minero       : 18 contratos mineros (tipo_operacion = SUBTERRANEA).
3.  dim_equipo_perforadora    : Maquinas con tipo_servicio (SUPERFICIE / INTERIOR MINA).
4.  dim_linea_diametro        : Diametros PQ, HQ, NQ, BQ, HWT.
5.  dim_personal              : Perforistas y ayudantes con roles estandarizados.
6.  dim_sondaje_taladro       : Sondajes con profundidad meta, linea e inclinacion.
7.  dim_taxonomia_actividad   : 116 actividades en 5 categorias de disponibilidad.
8.  fact_perforacion_avance   : Metraje diario (7,502.91 m), brocas (n_broca), escariadores, casing y motor.
9.  fact_horas_operativas     : Horas de perforacion, mantenimiento y standbys (> 0).
10. brg_cuadrilla_guardia     : Personal asignado y horas extras por guardia.
11. fact_metas_mensuales      : Metas de avance mensual por equipo.
12. ESQUEMA_ESTRELLA_COMPLETO.xlsx : Libro maestro de Excel con todas las hojas.


-------------------------------------------------------------------------------
5. CONTROL DE CALIDAD Y AUDITORIA
-------------------------------------------------------------------------------
El programa valida automaticamente:
- Que la suma total de metraje sea exactamente 7,502.91 m (cero perdidas respecto a Power Query).
- Que no existan claves huerfanas ni relaciones rotas entre tablas.
- Que las dimensiones cuenten con el comodin desconocido (sk = -1).

Fin del documento.
===============================================================================
