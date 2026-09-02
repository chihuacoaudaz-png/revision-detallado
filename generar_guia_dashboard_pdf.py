"""
Generador de la Guía Técnica y Operativa del Modelo Power BI en PDF (Rockdrill Group)
=====================================================================================
Compila un documento ejecutivo, técnico y operativo con ReportLab que describe
la arquitectura del Esquema Estrella, diccionario de tablas, flujo de datos,
métricas operativas (metros, horas, CTRs, metas) y gobernanza del Dashboard.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# --- CANVAS CON NUMERACIÓN DE PÁGINAS Y ENCABEZADOS EDITORIALES ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (A partir de página 2)
        if self._pageNumber > 1:
            self.drawString(40, 760, "ROCKDRILL GROUP — CONTROL DE OPERACIONES")
            self.drawRightString(572, 760, "GUÍA TÉCNICA Y OPERATIVA: MODELO TABULAR POWER BI")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 752, 572, 752)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawString(40, 30, "Documento Técnico Oficial — Control Operacional y Arquitectura de Datos")
        self.drawRightString(572, 30, page_text)
        self.restoreState()


def generar_pdf_guia():
    # Rutas de salida: tanto en la raíz como en docs/
    root_dir = Path(r"C:\Proyectos Python\Detallados")
    docs_dir = root_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path_root = root_dir / "GUIA_TECNICA_OPERATIVA_DASHBOARD_BI.pdf"
    pdf_path_docs = docs_dir / "GUIA_TECNICA_OPERATIVA_DASHBOARD_BI.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path_root),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )
    
    # --- ESTILOS DE TEXTO ---
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1E3A8A")    # Azul Corporativo Oscuro Rockdrill
    c_secondary = colors.HexColor("#0284C7")  # Azul Cielo
    c_dark = colors.HexColor("#0F172A")       # Texto oscuro
    c_muted = colors.HexColor("#475569")      # Texto secundario / gris
    c_bg_box = colors.HexColor("#F8FAFC")     # Fondo de cajas
    c_border = colors.HexColor("#CBD5E1")     # Bordes suaves
    c_accent = colors.HexColor("#D97706")     # Ámbar de advertencia / KPI
    c_green = colors.HexColor("#059669")      # Verde de éxito
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_muted,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Header1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=5
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )
    kpi_num_style = ParagraphStyle(
        'KpiNum',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=c_primary,
        alignment=1
    )
    kpi_label_style = ParagraphStyle(
        'KpiLabel',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_muted,
        alignment=1
    )
    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )
    table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    box_p = ParagraphStyle(
        'BoxText',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    story = []

    # =========================================================================
    # PORTADA / ENCABEZADO EJECUTIVO
    # =========================================================================
    story.append(Paragraph("ROCKDRILL GROUP — CONTROL DE OPERACIONES", ParagraphStyle(
        'PreHeader', fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=c_secondary, spaceAfter=4
    )))
    story.append(Paragraph("GUÍA TÉCNICA Y OPERATIVA DEL MODELO BI", title_style))
    story.append(Paragraph(
        "<b>Arquitectura Dimensional Kimball (Star Schema) en Power BI</b> | Diccionario de Tablas, Origen de Almacenamiento, Métricas de Perforación (Metros, Horas, CTRs, Metas) y Manual de Mantenimiento.",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Tarjetas KPI de Estado del Modelo
    kpi_data = [
        [
            Paragraph("7,502.91 m", kpi_num_style),
            Paragraph("7,687.0 h", kpi_num_style),
            Paragraph("22 CTRs / 96 Eq.", kpi_num_style),
            Paragraph("52,295.17 m", kpi_num_style),
            Paragraph("16 Relaciones", kpi_num_style)
        ],
        [
            Paragraph("Metraje Real Perforado", kpi_label_style),
            Paragraph("Horas Reportadas", kpi_label_style),
            Paragraph("Flota y Contratos", kpi_label_style),
            Paragraph("Meta Mes Activo (Set)", kpi_label_style),
            Paragraph("Esquema Estrella Activo", kpi_label_style)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[106]*5)
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_box),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 1: MAPA DE ALMACENAMIENTO (¿DÓNDE SE GUARDA CADA DATO?)
    # =========================================================================
    story.append(Paragraph("1. Arquitectura de Datos y Repositorio de Almacenamiento", h1_style))
    story.append(Paragraph(
        "Para que cualquier miembro del equipo pueda auditar, mantener y enriquecer el Dashboard, "
        "el flujo de datos está estructurado en 3 capas desacopladas con trazabilidad total:",
        body_style
    ))

    storage_table_data = [
        [Paragraph("Capa / Archivo", table_header), Paragraph("Ubicación en Disco / Nube", table_header), Paragraph("Contenido y Función Operativa", table_header), Paragraph("Actualización", table_header)],
        [
            Paragraph("<b>Base Operativa F-01</b><br/><code>CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx</code>", table_cell),
            Paragraph("<code>Estructura base/Rockdrill_Control_Operaciones/Base de datos/</code>", table_cell),
            Paragraph("Contiene el reporte diario detallado consolidado de campo (176 columnas). Registra cada turno de perforación, metros desde/hasta, horómetros, cuadrillas, brocas y eventos de parada.", table_cell),
            Paragraph("Diario / Semanal", table_cell)
        ],
        [
            Paragraph("<b>Maestro de Metas</b><br/><code>METAS.xlsx</code>", table_cell),
            Paragraph("Raíz del proyecto / OneDrive compartido", table_cell),
            Paragraph("Contiene 1,052 registros históricos de metas planificadas por Contrato (CTR), Máquina y Mes Operativo (2025 al 2026). Desacoplado de los reportes diarios para evitar errores de llenado.", table_cell),
            Paragraph("Mensual", table_cell)
        ],
        [
            Paragraph("<b>Capa Dimensional Procesada</b><br/><code>BBDD/output_star_schema/</code>", table_cell),
            Paragraph("Carpeta local y sincronizada en OneDrive", table_cell),
            Paragraph("Almacena las <b>11 tablas del Esquema Estrella</b> en formato <code>.csv</code> (UTF-8) y <code>.parquet</code> (compresión columnar). Incluye el libro consolidado <code>ESQUEMA_ESTRELLA_COMPLETO.xlsx</code>.", table_cell),
            Paragraph("Automático (24 s)", table_cell)
        ],
        [
            Paragraph("<b>Visualización Semántica</b><br/><code>DASH.pbix</code>", table_cell),
            Paragraph("Raíz del proyecto / OneDrive", table_cell),
            Paragraph("Modelo Tabular de Power BI con las 16 relaciones físicas activas, medidas analíticas DAX (utilización, disponibilidad mecánica, ritmo diario) y vistas visuales IBCS.", table_cell),
            Paragraph("Bajo demanda", table_cell)
        ],
    ]
    t_storage = Table(storage_table_data, colWidths=[120, 140, 200, 72])
    t_storage.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_storage)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 2: DICCIONARIO DE LAS 11 TABLAS (7 DIMENSIONES + 4 HECHOS/PUENTE)
    # =========================================================================
    story.append(Paragraph("2. Diccionario de Datos: Las 11 Tablas del Esquema Estrella", h1_style))
    story.append(Paragraph(
        "El modelo sigue estrictamente la metodología Kimball: tablas de dimensiones que contienen atributos de contexto "
        "y tablas de hechos con métricas cuantitativas aditivas y semi-aditivas.",
        body_style
    ))

    dict_table_data = [
        [Paragraph("Tabla", table_header), Paragraph("Tipo", table_header), Paragraph("Filas", table_header), Paragraph("Llave Primaria / Unión", table_header), Paragraph("Descripción y Atributos de Negocio", table_header)],
        # Dimensiones
        [
            Paragraph("<b>dim_tiempo_calendario</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("731", table_cell),
            Paragraph("<code>calendario_sk</code> (YYYYMMDD)", table_cell),
            Paragraph("Abarca del 01/01/2025 al 31/12/2026. Maneja semanas calendario (lun-dom) y semanas del ciclo operativo minero (del 26 al 25). Clave para análisis temporal.", table_cell)
        ],
        [
            Paragraph("<b>dim_contrato_minero</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("22", table_cell),
            Paragraph("<code>contrato_sk</code>", table_cell),
            Paragraph("Maestro de contratos mineros (Cobriza, Chungar, Inmaculada, Raura, Catalina Huanca, etc.). Tipificados como operación subterránea con clientes mineros asociados.", table_cell)
        ],
        [
            Paragraph("<b>dim_equipo_perforadora</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("96", table_cell),
            Paragraph("<code>equipo_sk</code>", table_cell),
            Paragraph("Flota integral de perforadoras (XRD, Boart Longyear, Sandvik). Contiene código SAP, modelo, fabricante, tipo de servicio (Mina/Superficie) y horas día planeadas (24h).", table_cell)
        ],
        [
            Paragraph("<b>dim_linea_diametro</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("4", table_cell),
            Paragraph("<code>linea_sk</code>", table_cell),
            Paragraph("Líneas de perforación diamantina: HQ (63.5 mm), NQ (47.6 mm), BQ (36.5 mm), PQ (85.0 mm). Define diámetros de broca y testigo geológico.", table_cell)
        ],
        [
            Paragraph("<b>dim_personal</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("412", table_cell),
            Paragraph("<code>personal_sk</code>", table_cell),
            Paragraph("Personal operativo y técnico (perforistas, ayudantes, mecánicos). Contiene DNI/Carnet, nombres completos normalizados y rol estandarizado.", table_cell)
        ],
        [
            Paragraph("<b>dim_sondaje_taladro</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("121", table_cell),
            Paragraph("<code>sondaje_sk</code>", table_cell),
            Paragraph("Taladros o pozos perforados. Contiene profundidad programada, inclinación en grados, cota y tipo de taladro. Relacionado directamente al avance.", table_cell)
        ],
        [
            Paragraph("<b>dim_taxonomia_actividad</b>", table_cell),
            Paragraph("Dimensión", table_cell),
            Paragraph("94", table_cell),
            Paragraph("<code>actividad_sk</code>", table_cell),
            Paragraph("Taxonomía oficial SIG Rockdrill (17 bloques funcionales). Clasifica cada evento en <b>5 Categorías de Disponibilidad</b> (Operativo, Stand By Op, Stand By Cliente, Mtto Mecánico, Inoperativo) y flag de cobrabilidad.", table_cell)
        ],
        # Hechos
        [
            Paragraph("<b>fact_perforacion_avance</b>", table_cell_bold),
            Paragraph("Hechos", table_cell_bold),
            Paragraph("3,505", table_cell_bold),
            Paragraph("<code>avance_id</code><br/>FK: <code>perforista_sk</code>", table_cell),
            Paragraph("<b>Tabla central de producción.</b> Contiene el metraje perforado (7,502.91 m), tramos desde/hasta, nro de broca, escariador, casing, reperforación, horómetros y petróleo.", table_cell)
        ],
        [
            Paragraph("<b>fact_horas_operativas</b>", table_cell_bold),
            Paragraph("Hechos", table_cell_bold),
            Paragraph("4,747", table_cell_bold),
            Paragraph("<code>hora_evento_id</code>", table_cell),
            Paragraph("<b>Tabla central de tiempos.</b> Eventos de duración horaria de cada actividad (> 0 h). Suma 7,687 h reportadas. Base para calcular DM %, UT % y horas cobrables.", table_cell)
        ],
        [
            Paragraph("<b>brg_cuadrilla_guardia</b>", table_cell),
            Paragraph("Puente", table_cell),
            Paragraph("4,820", table_cell),
            Paragraph("<code>asignacion_id</code>", table_cell),
            Paragraph("Tabla puente que conecta cada turno con su dotación de personal (perforista titular y ayudantes 1, 2 y 3) junto con sus horas laboradas y extras.", table_cell)
        ],
        [
            Paragraph("<b>fact_metas_mensuales</b>", table_cell_bold),
            Paragraph("Hechos", table_cell_bold),
            Paragraph("1,052", table_cell_bold),
            Paragraph("<code>meta_id</code>", table_cell),
            Paragraph("<b>Tabla de planeamiento mensual.</b> Metas de metraje por CTR y Máquina desde 2025 hasta 2026. Meta activa de setiembre 2026: <b>52,295.17 m</b>.", table_cell)
        ],
    ]
    t_dict = Table(dict_table_data, colWidths=[110, 48, 32, 102, 240])
    t_dict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_dict)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 3: LAS 4 MÉTRICAS OPERATIVAS CLAVE (DRIVERS DEL NEGOCIO)
    # =========================================================================
    story.append(Paragraph("3. Métricas Operativas Clave y Drivers de Rentabilidad", h1_style))
    story.append(Paragraph(
        "En la perforación diamantina (DDH) la rentabilidad se rige por un <b>modelo dual</b>: "
        "Facturación por Metros Perforados (PU) y Facturación por Horas Operativas / Stand By Cliente. "
        "A continuación se detallan los 4 pilares analíticos del Dashboard:",
        body_style
    ))

    kpi_details = [
        [
            Paragraph("<b>1. Metros Perforados (Avance Físico)</b>", h2_style),
            Paragraph("<b>2. Horas Operativas y Taxonomía SIG</b>", h2_style)
        ],
        [
            Paragraph(
                "• <b>Columna de Origen:</b> <code>fact_perforacion_avance[metraje_guardia_m]</code>.<br/>"
                "• <b>Volumen Validado:</b> <b>7,502.91 metros</b> en 3,505 guardias analizadas.<br/>"
                "• <b>Metrajes Especiales:</b> Casing (revestimiento de tubería) y Reperforación, auditados para no inflar el avance geológico neto.<br/>"
                "• <b>Productividad Perforista:</b> Calculada vinculando la dimensión <code>dim_personal</code> mediante <code>perforista_sk</code>.",
                body_style
            ),
            Paragraph(
                "• <b>Columna de Origen:</b> <code>fact_horas_operativas[horas_reportadas]</code>.<br/>"
                "• <b>Volumen Validado:</b> <b>7,687.0 horas</b> en 4,747 eventos operativos.<br/>"
                "• <b>Las 5 Categorías de Disponibilidad:</b><br/>"
                "  1. <i>Operativo Efectivo:</i> Perforación rotativa real.<br/>"
                "  2. <i>Stand By Operativo:</i> Maniobras de cuadrilla Rockdrill.<br/>"
                "  3. <i>Stand By Cliente:</i> Paradas imputables a la mina (cobrables).<br/>"
                "  4. <i>Mantenimiento:</i> Reparaciones mecánicas/eléctricas.<br/>"
                "  5. <i>Inoperatividad:</i> Averías mayores o falta de frente.",
                body_style
            )
        ],
        [
            Paragraph("<b>3. Contratos (CTR) y Flota de Perforadoras</b>", h2_style),
            Paragraph("<b>4. Metas de Planeamiento y Proyección Run-Rate</b>", h2_style)
        ],
        [
            Paragraph(
                "• <b>Segmentación por CTR:</b> Análisis independiente para los 22 contratos (ej. Cobriza: 903.1 m, Chungar: 733.15 m, Catalina Huanca: 676.8 m, Raura: 740.76 m, Americana: 421.7 m).<br/>"
                "• <b>Rendimiento Horario:</b> Ratio <i>m/h</i> (Metros Perforados / Horas Efectivas de Perforación).<br/>"
                "• <b>Control de Consumibles:</b> Galones de petróleo por metro perforado (<code>petroleo_gln / metraje_guardia_m</code>).",
                body_style
            ),
            Paragraph(
                "• <b>Meta Oficial:</b> Alimentada desde <code>METAS.xlsx</code> (52,295.17 m en Set-2026 para 64 máquinas activas).<br/>"
                "• <b>Cumplimiento:</b> <code>DIVIDE([Metraje Real], [Meta Metraje], 0)</code>.<br/>"
                "• <b>Proyección Dinámica de Cierre:</b> No utiliza campos manuales de admin. Se calcula dinámicamente en DAX según el ritmo diario promedio y los días restantes del ciclo minero (del 26 al 25):<br/>"
                "  <i>Proyección = Metraje Real + (Ritmo Diario × Días Restantes)</i>",
                body_style
            )
        ]
    ]
    t_kpi_det = Table(kpi_details, colWidths=[266, 266])
    t_kpi_det.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_box),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_kpi_det)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 4: MAPA RELACIONAL Y REGLAS TÉCNICAS CRÍTICAS
    # =========================================================================
    story.append(Paragraph("4. Reglas Técnicas y Relacionales en Power BI", h1_style))
    story.append(Paragraph(
        "Para garantizar que el modelo funcione sin ambigüedad y con máxima velocidad de cálculo VertiPaq, "
        "se aplican 3 reglas obligatorias en Power BI Desktop:",
        body_style
    ))

    rules_data = [
        [
            Paragraph("<b>Regla 1: Cultura Regional en Power Query (en-US)</b>", table_cell_bold),
            Paragraph(
                "Los archivos CSV generados por el pipeline usan el punto (<code>.</code>) como separador decimal estándar. "
                "Al importar en Power BI bajo Windows en español, el código M <b>debe incluir el parámetro <code>'en-US'</code></b> "
                "en <code>Table.TransformColumnTypes</code>. De omitirse, Windows interpretará el punto como separador de miles "
                "(convirtiendo 28.3 m en 283 m).",
                table_cell
            )
        ],
        [
            Paragraph("<b>Regla 2: Llave de Perforista (perforista_sk)</b>", table_cell_bold),
            Paragraph(
                "En <code>dim_personal</code> la llave primaria es <code>personal_sk</code> (engloba a todo el personal de la empresa). "
                "En <code>fact_perforacion_avance</code> la llave foránea se llama <code>perforista_sk</code> para indicar el rol específico "
                "del perforista titular. En Power BI ambas se enlazan sin problema en cardinalidad <b>Varios a Uno (*:1)</b> con 0 registros huérfanos.",
                table_cell
            )
        ],
        [
            Paragraph("<b>Regla 3: Esquema Estrella Puro (Sin Lazos Snowflake)</b>", table_cell_bold),
            Paragraph(
                "<b>No debe relacionarse <code>dim_sondaje_taladro</code> con <code>dim_contrato_minero</code></b>. Ambas dimensiones ya se relacionan "
                "directamente con las tablas de hechos. Si se conectan entre sí, Power BI detecta rutas circulares ambiguas y desactiva la relación "
                "de los sondajes con el metraje de perforación.",
                table_cell
            )
        ]
    ]
    t_rules = Table(rules_data, colWidths=[170, 362])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 5: MANUAL DE OPERACIÓN Y ACTUALIZACIÓN (CÓMO ACTUALIZAR EL BI)
    # =========================================================================
    story.append(Paragraph("5. Procedimiento de Actualización Periódica (Manual de Mantenimiento)", h1_style))
    story.append(Paragraph(
        "Cualquier persona del equipo puede actualizar el Dashboard siguiendo este procedimiento estándar de 3 pasos (tiempo estimado: 1 minuto):",
        body_style
    ))

    steps_data = [
        [
            Paragraph("Paso 1: Pegar Datos Nuevos", table_cell_bold),
            Paragraph("Paso 2: Ejecutar el Pipeline", table_cell_bold),
            Paragraph("Paso 3: Refrescar Power BI", table_cell_bold)
        ],
        [
            Paragraph(
                "Reemplazar o guardar el archivo actualizado <code>CONSOLIDADOR_DETALLADOS_POWERQUERY.xlsx</code> en la carpeta de base de datos "
                "y/o el archivo <code>METAS.xlsx</code> en la raíz/OneDrive si hubo cambios de planeamiento mensual.",
                table_cell
            ),
            Paragraph(
                "Hacer doble clic sobre el ejecutable <b><code>EJECUTAR_BBDD.bat</code></b> (o correr <code>python generar_base_datos_dimensional.py</code>). "
                "El proceso demora ~24 segundos y regenera automáticamente todas las tablas del esquema estrella.",
                table_cell
            ),
            Paragraph(
                "Abrir <b><code>DASH.pbix</code></b> y hacer clic en el botón <b>Actualizar (Refresh)</b> de la cinta superior. "
                "Los visuales, tarjetas y métricas de avance se actualizarán inmediatamente con los nuevos metros y horas.",
                table_cell
            )
        ]
    ]
    t_steps = Table(steps_data, colWidths=[177, 177, 178])
    t_steps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,1), (-1,1), c_bg_box),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_steps)
    story.append(Spacer(1, 14))

    # Pie institucional de cierre
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Rockdrill Group — Gerencia de Operaciones y Control de Gestión</b><br/>"
        "Documento emitido para estandarización y transferencia de conocimiento técnico sobre el Modelo Tabular Power BI.",
        ParagraphStyle('FooterNotice', fontName='Helvetica', fontSize=7.5, leading=10, textColor=c_muted, alignment=1)
    ))

    # Construir el documento
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Copiar también a docs/
    import shutil
    shutil.copyfile(str(pdf_path_root), str(pdf_path_docs))
    
    print(f"PDF generado exitosamente en:")
    print(f" - {pdf_path_root} ({pdf_path_root.stat().st_size / 1024:.1f} KB)")
    print(f" - {pdf_path_docs} ({pdf_path_docs.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    generar_pdf_guia()
