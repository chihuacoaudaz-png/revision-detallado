"""
Generador del Informe Técnico en PDF: Propuesta de Estandarización del Reporte Detallado F.01
=============================================================================================
Utiliza ReportLab para compilar un documento ejecutivo, profesional y altamente legible
con diseño editorial corporativo (Rockdrill Group).
"""

import os
from pathlib import Path
from config import OUTPUT_PATH
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# --- CANVAS CON NUMERACIÓN DE PÁGINAS DINÁMICA ---
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (A partir de página 2)
        if self._pageNumber > 1:
            self.drawString(40, 760, "ROCKDRILL GROUP — CONTROL DE OPERACIONES")
            self.drawRightString(572, 760, "INFORME TÉCNICO: ESTANDARIZACIÓN RD.402.P.01.F.01")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 752, 572, 752)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawString(40, 30, "Documento Confidencial de Gestión Interna — Versión 1.0 (Agosto 2026)")
        self.drawRightString(572, 30, page_text)
        self.restoreState()


def generar_pdf(output_dir: Path = OUTPUT_PATH):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "PROPUESTA_ESTANDARIZACION_DETALLADO_F01.pdf"
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )
    
    # --- ESTILOS DE TEXTO ---
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1E3A8A")    # Azul Corporativo Oscuro
    c_secondary = colors.HexColor("#0D9488")  # Teal / Turquesa
    c_dark = colors.HexColor("#0F172A")       # Texto principal
    c_muted = colors.HexColor("#475569")      # Texto secundario
    c_bg_box = colors.HexColor("#F1F5F9")     # Fondo de cajas
    c_border = colors.HexColor("#CBD5E1")     # Bordes
    
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
        fontSize=11,
        leading=15,
        textColor=c_muted,
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        'BodyDarkBold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B")
    )
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=c_dark
    )
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_dark,
        alignment=1
    )

    story = []

    # =========================================================================
    # PORTADA / ENCABEZADO EJECUTIVO
    # =========================================================================
    story.append(Paragraph("ROCKDRILL GROUP — CONTROL DE PROYECTOS Y OPERACIONES", ParagraphStyle('TopTag', fontName='Helvetica-Bold', fontSize=9, textColor=c_secondary, leading=11, spaceAfter=4)))
    story.append(Paragraph("Propuesta Técnica de Estandarización de Plantilla:<br/>Reporte Detallado de Avance (RD.402.P.01.F.01)", title_style))
    story.append(Paragraph("Catálogo Maestro de 156 Columnas, Arquitectura en 13 Bloques Operativos y Mecanismo de Vistas Ocultables por Contrato Minero.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Tarjeta de Metadatos
    meta_data = [
        [
            Paragraph("<b>Fecha de Emisión:</b> 19 de Agosto de 2026", body_style),
            Paragraph("<b>Área Responsable:</b> Control de Proyectos / Operaciones", body_style)
        ],
        [
            Paragraph("<b>Objetivo:</b> Unificar los 18 contratos en una plantilla única", body_style),
            Paragraph("<b>Destinatarios:</b> Gerencia de Operaciones, Admins de Contrato, TI", body_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[260, 272])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_box),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 1. RESUMEN EJECUTIVO Y DIAGNÓSTICO
    # =========================================================================
    story.append(Paragraph("1. Diagnóstico de Situación y Justificación", h1_style))
    p_diag = (
        "Actualmente, la operación de Rockdrill en sus 18 contratos mineros (CTRs) utiliza versiones "
        "heterogéneas del formato <b>RD.402.P.01.F.01</b>. A lo largo del tiempo, la base histórica consolidó "
        "<b>156 columnas</b> que incluían actividades específicas de superficie, mina subterránea y demoras particulares. "
        "Sin embargo, al no existir una plantilla maestra universal, algunas unidades mineras comprimieron actividades "
        "en campos genéricos (como 'Tiempos Muertos' o 'Esperas Operativas') o insertaron columnas en posiciones distintas, "
        "generando fricción operativa y requiriendo parches manuales para la consolidación mensual y reportería en Power BI."
    )
    story.append(Paragraph(p_diag, body_style))

    # Cuadro de Ventajas
    p_ventajas = (
        "<b>💡 Principios Clave de la Solución Propuesta:</b><br/>"
        "• <b>100% Familiar para las Administradoras (Admins):</b> Mantiene exactamente la estructura visual de doble encabezado (Filas 23 y 24) y llenado a partir de la fila 25.<br/>"
        "• <b>Plantilla Única Maestra Universal:</b> Contiene las 156 columnas canónicas de todas las actividades posibles.<br/>"
        "• <b>Vistas Personalizadas por Contrato:</b> Cada administradora simplemente <i>oculta</i> (Hide) las columnas que no aplican a su mina (ej. 'Condiciones Climáticas' en interior mina o 'Scoop' en superficie) <u>sin mover de posición las demás columnas</u>.<br/>"
        "• <b>Automatización Directa:</b> El sistema de ingesta lee siempre las columnas en su ubicación exacta, eliminando errores de desfase."
    )
    t_callout = Table([[Paragraph(p_ventajas, callout_style)]], colWidths=[532])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 2. ESTRUCTURA EN 13 BLOQUES OPERATIVOS
    # =========================================================================
    story.append(Paragraph("2. Estructura y Distribución de los 13 Bloques Canónicos", h1_style))
    story.append(Paragraph("Las 156 columnas se organizan en 13 bloques funcionales correlativos que siguen el flujo natural de reporte en campo:", body_style))

    bloques_data = [
        [
            Paragraph("Bloque", table_hdr_style),
            Paragraph("Sección Operativa", table_hdr_style),
            Paragraph("Columnas", table_hdr_style),
            Paragraph("Cant.", table_hdr_style),
            Paragraph("Descripción y Propósito Operativo", table_hdr_style)
        ],
        [
            Paragraph("<b>01</b>", table_cell_center),
            Paragraph("Identificación y Generales", table_cell_bold),
            Paragraph("Cols 1 a 10", table_cell_center),
            Paragraph("10", table_cell_center),
            Paragraph("N°, Zona, CTR, Máquina SAP, Turno (A/B), Grupo, Mes, Fecha, Año, Guardia.", table_cell_style)
        ],
        [
            Paragraph("<b>02</b>", table_cell_center),
            Paragraph("Sondaje y Metraje", table_cell_bold),
            Paragraph("Cols 11 a 22", table_cell_center),
            Paragraph("12", table_cell_center),
            Paragraph("Sondaje, Profundidad, Diámetro (Línea), Inclinación, Desde, Hasta, Metraje guardia, Metas.", table_cell_style)
        ],
        [
            Paragraph("<b>03</b>", table_cell_center),
            Paragraph("Personal Asignado", table_cell_bold),
            Paragraph("Cols 23 a 25", table_cell_center),
            Paragraph("3", table_cell_center),
            Paragraph("Perforista oficial, Ayudante 1 y Ayudante 2 (Nombres estandarizados).", table_cell_style)
        ],
        [
            Paragraph("<b>04</b>", table_cell_center),
            Paragraph("Brocas y Escariadores", table_cell_bold),
            Paragraph("Cols 26 a 33", table_cell_center),
            Paragraph("8", table_cell_center),
            Paragraph("Marca, Serie, N° correlativo y Estado de brocas/escariadores, Cambio de broca.", table_cell_style)
        ],
        [
            Paragraph("<b>05</b>", table_cell_center),
            Paragraph("Aditivos y Combustible", table_cell_bold),
            Paragraph("Cols 34 a 57", table_cell_center),
            Paragraph("24", table_cell_center),
            Paragraph("Consumo de Bentonita, PAC, Polímeros, Lubricantes, Inhibidores, Petróleo (Cant. y Und).", table_cell_style)
        ],
        [
            Paragraph("<b>06</b>", table_cell_center),
            Paragraph("Operación Efectiva", table_cell_bold),
            Paragraph("Cols 58 a 76", table_cell_center),
            Paragraph("19", table_cell_center),
            Paragraph("Perforación neta, Rimado, Casing, PVC, Reperforación, Lavado, Desviación, Piezómetro, etc.", table_cell_style)
        ],
        [
            Paragraph("<b>07</b>", table_cell_center),
            Paragraph("Preparación y Maniobras", table_cell_bold),
            Paragraph("Cols 77 a 101", table_cell_center),
            Paragraph("25", table_cell_center),
            Paragraph("Maniobra barras, Traslados (máquina, cámaras, personal), 5S, Pozas, Charlas, IPERC, Refrigerio.", table_cell_style)
        ],
        [
            Paragraph("<b>08</b>", table_cell_center),
            Paragraph("Mantenimiento", table_cell_bold),
            Paragraph("Cols 102 a 106", table_cell_center),
            Paragraph("5", table_cell_center),
            Paragraph("Mantenimiento Preventivo, Correctivo, Check List Pre Uso, Espera de Repuestos y Total Mantto.", table_cell_style)
        ],
        [
            Paragraph("<b>09</b>", table_cell_center),
            Paragraph("Stand By Inoperativo (RD)", table_cell_bold),
            Paragraph("Cols 107 a 115", table_cell_center),
            Paragraph("9", table_cell_center),
            Paragraph("Falta personal, insumos, camioneta/cisterna, esperas inoperativas, Pare RD.", table_cell_style)
        ],
        [
            Paragraph("<b>10</b>", table_cell_center),
            Paragraph("Stand By Cliente (Mina)", table_cell_bold),
            Paragraph("Cols 116 a 136", table_cell_center),
            Paragraph("21", table_cell_center),
            Paragraph("Falta agua/energía/ventilación, espera scoop/frente/geología, voladura, clima, Pare Cía.", table_cell_style)
        ],
        [
            Paragraph("<b>11</b>", table_cell_center),
            Paragraph("Totales y Disponibilidad", table_cell_bold),
            Paragraph("Cols 137 a 143", table_cell_center),
            Paragraph("7", table_cell_center),
            Paragraph("Tiempo Total, Horas Efectivas, Horas Operativas, Lost Time, Disponibilidad Mecánica (%), UT (%).", table_cell_style)
        ],
        [
            Paragraph("<b>12</b>", table_cell_center),
            Paragraph("Detalle de Tramos", table_cell_bold),
            Paragraph("Cols 144 a 151", table_cell_center),
            Paragraph("8", table_cell_center),
            Paragraph("Tramos Desde/Hasta y Metrajes de Rimado HWT/HQ, Reperforación y Horómetro.", table_cell_style)
        ],
        [
            Paragraph("<b>13</b>", table_cell_center),
            Paragraph("Bitácoras y Observaciones", table_cell_bold),
            Paragraph("Cols 152 a 156", table_cell_center),
            Paragraph("5", table_cell_center),
            Paragraph("Trabajos realizados, repuestos usados, descripción litológica y comentarios de guardia.", table_cell_style)
        ],
    ]

    t_bloques = Table(bloques_data, colWidths=[36, 115, 68, 30, 283])
    t_bloques.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_bloques)

    story.append(PageBreak())

    # =========================================================================
    # 3. CATÁLOGO MAESTRO COMPLETO DE LAS 156 COLUMNAS
    # =========================================================================
    story.append(Paragraph("3. Catálogo Maestro de las 156 Columnas Canónicas", h1_style))
    story.append(Paragraph("A continuación se presenta el detalle exhaustivo columna por columna con su clasificación oficial:", body_style))

    # Cargar datos de las 156 columnas
    from docs_propuesta_data import COLS_DATA_156

    cols_table_data = [
        [
            Paragraph("N°", table_hdr_style),
            Paragraph("Encabezado Fila 23 (Grupo)", table_hdr_style),
            Paragraph("Encabezado Fila 24 (Columna)", table_hdr_style),
            Paragraph("Tipo", table_hdr_style),
            Paragraph("Categoría BI", table_hdr_style),
            Paragraph("Responsable", table_hdr_style)
        ]
    ]

    for item in COLS_DATA_156:
        cols_table_data.append([
            Paragraph(str(item[0]), table_cell_center),
            Paragraph(item[1], table_cell_bold),
            Paragraph(item[2], table_cell_style),
            Paragraph(item[3], table_cell_center),
            Paragraph(item[4], table_cell_style),
            Paragraph(item[5], table_cell_style)
        ])

    t_cols = Table(cols_table_data, colWidths=[24, 115, 175, 48, 85, 85], repeatRows=1)
    t_cols.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_cols)

    story.append(Spacer(1, 12))

    # =========================================================================
    # 4. PLAN DE TRANSICIÓN Y RECOMENDACIONES
    # =========================================================================
    story.append(Paragraph("4. Plan de Transición y Recomendaciones para Operaciones", h1_style))
    p_plan = (
        "<b>1. Distribución de la Plantilla Maestra:</b> Se entregará un archivo Excel con las 156 columnas y fórmulas bloqueadas en filas de subtotales.<br/>"
        "<b>2. Ajuste Visual por Unidad Minera:</b> La administradora de cada contrato abrirá la plantilla y ocultará las columnas no aplicables a su proyecto, guardando una copia de trabajo local.<br/>"
        "<b>3. Cero Ruptura en Consolidación:</b> Toda extracción automatizada en Python o Power BI leerá las 156 columnas sin requerir mantenimiento ni adaptaciones específicas por CTR.<br/>"
        "<b>4. Auditoría de Nombres de Personal:</b> Se recomienda implementar listas desplegables (Data Validation) en las columnas de Perforista y Ayudantes para evitar discrepancias ortográficas."
    )
    story.append(Paragraph(p_plan, body_style))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"  [OK] PDF GENERADO EXITOSAMENTE EN: {pdf_path}")


if __name__ == "__main__":
    generar_pdf()
