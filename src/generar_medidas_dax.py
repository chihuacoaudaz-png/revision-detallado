"""
Generador de Catálogo de Medidas DAX Oficiales (Rockdrill Group)
Proyecto: Sistema Integral de Business Intelligence y Analítica de Perforación
Genera las medidas DAX en formato estructurado, script Tabular Model / DAX Editor y Markdown.
"""

from pathlib import Path
import json

MEDIDAS_DAX = [
    # -------------------------------------------------------------------------
    # 1. MÉTRICAS DE PRODUCCIÓN Y METRAJE
    # -------------------------------------------------------------------------
    {
        "tabla": "fact_perforacion_avance",
        "nombre": "Metraje Perforado Total (m)",
        "categoria": "Producción",
        "formato": "#,##0.00 \"m\"",
        "dax": "SUM(fact_perforacion_avance[metraje_guardia_m])",
        "descripcion": "Sumatoria total del metraje físico perforado registrado en las guardias operativas."
    },
    {
        "tabla": "fact_perforacion_avance",
        "nombre": "Metraje Promedio por Guardia (m/g)",
        "categoria": "Producción",
        "formato": "#,##0.00 \"m/g\"",
        "dax": "AVERAGE(fact_perforacion_avance[metraje_guardia_m])",
        "descripcion": "Promedio de avance físico alcanzado por guardia operativa."
    },
    {
        "tabla": "fact_perforacion_avance",
        "nombre": "Metraje Turno A (Día)",
        "categoria": "Producción",
        "formato": "#,##0.00 \"m\"",
        "dax": "CALCULATE([Metraje Perforado Total (m)], fact_perforacion_avance[turno_guardia] = \"A\")",
        "descripcion": "Metraje total perforado en el turno diurno (Guardia A)."
    },
    {
        "tabla": "fact_perforacion_avance",
        "nombre": "Metraje Turno B (Noche)",
        "categoria": "Producción",
        "formato": "#,##0.00 \"m\"",
        "dax": "CALCULATE([Metraje Perforado Total (m)], fact_perforacion_avance[turno_guardia] = \"B\")",
        "descripcion": "Metraje total perforado en el turno nocturno (Guardia B)."
    },
    {
        "tabla": "fact_perforacion_avance",
        "nombre": "Balance Turno (% Día)",
        "categoria": "Producción",
        "formato": "0.0%",
        "dax": "DIVIDE([Metraje Turno A (Día)], [Metraje Perforado Total (m)], 0)",
        "descripcion": "Porcentaje de producción aportado por el turno día sobre el total."
    },

    # -------------------------------------------------------------------------
    # 2. MÉTRICAS DE TIEMPOS Y HORAS
    # -------------------------------------------------------------------------
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Totales Reportadas (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "SUM(fact_horas_operativas[horas_reportadas])",
        "descripcion": "Sumatoria total de horas registradas en todas las actividades."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Perforación Efectiva (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), dim_taxonomia_actividad[categoria_disponibilidad] = \"Tiempo Efectivo\")",
        "descripcion": "Horas dedicadas a perforación directa en roca (La Brújula)."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Mantenimiento (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), dim_taxonomia_actividad[categoria_disponibilidad] = \"Mantenimiento\")",
        "descripcion": "Horas de mantenimiento preventivo y correctivo de la perforadora."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Stand By Operativo (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), dim_taxonomia_actividad[categoria_disponibilidad] = \"Stand By Operativo\")",
        "descripcion": "Horas en maniobras operativas y ensayos geotécnicos."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Stand By Inoperativo (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), dim_taxonomia_actividad[categoria_disponibilidad] = \"Stand By Inoperativo\")",
        "descripcion": "Horas no cobrables por paradas internas (traslados, refrigerios, esperas RD)."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Stand By Cliente (h)",
        "categoria": "Tiempos",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), dim_taxonomia_actividad[categoria_disponibilidad] = \"Stand By Cliente\")",
        "descripcion": "Horas imputables al cliente minero (voladuras, falta de ventilación, scoop, agua)."
    },
    {
        "tabla": "fact_horas_operativas",
        "nombre": "Horas Cobrables Totales (h)",
        "categoria": "Facturabilidad",
        "formato": "#,##0.00 \"h\"",
        "dax": "CALCULATE(SUM(fact_horas_operativas[horas_reportadas]), fact_horas_operativas[es_cobrable] = TRUE())",
        "descripcion": "Total de horas valorizables ante el cliente minero."
    },

    # -------------------------------------------------------------------------
    # 3. RATIOS DE EFICIENCIA OPERATIVA (KPIS MINEROS)
    # -------------------------------------------------------------------------
    {
        "tabla": "_Medidas",
        "nombre": "Ratio de Penetración (m/h)",
        "categoria": "Eficiencia",
        "formato": "#,##0.00 \"m/h\"",
        "dax": "DIVIDE([Metraje Perforado Total (m)], [Horas Perforación Efectiva (h)], 0)",
        "descripcion": "Velocidad real de perforación por hora efectiva de broca en fondo."
    },
    {
        "tabla": "_Medidas",
        "nombre": "Disponibilidad Mecánica (DM %)",
        "categoria": "Eficiencia",
        "formato": "0.0%",
        "dax": "DIVIDE([Horas Totales Reportadas (h)] - [Horas Mantenimiento (h)], [Horas Totales Reportadas (h)], 0)",
        "descripcion": "Porcentaje de tiempo en que el equipo estuvo mecánicamente apto para operar."
    },
    {
        "tabla": "_Medidas",
        "nombre": "Utilización Operativa (UT %)",
        "categoria": "Eficiencia",
        "formato": "0.0%",
        "dax": "DIVIDE([Horas Perforación Efectiva (h)], [Horas Totales Reportadas (h)] - [Horas Mantenimiento (h)], 0)",
        "descripcion": "Porcentaje del tiempo disponible que se destinó efectivamente a perforar."
    },
    {
        "tabla": "_Medidas",
        "nombre": "Ratio de Cobrabilidad (% Facturable)",
        "categoria": "Facturabilidad",
        "formato": "0.0%",
        "dax": "DIVIDE([Horas Cobrables Totales (h)], [Horas Totales Reportadas (h)], 0)",
        "descripcion": "Porcentaje de horas facturables sobre el total reportado en mina."
    },

    # -------------------------------------------------------------------------
    # 4. METAS Y CUMPLIMIENTO (CICLO MINERO 26 AL 25)
    # -------------------------------------------------------------------------
    {
        "tabla": "fact_metas_mensuales",
        "nombre": "Meta Metraje Mes (m)",
        "categoria": "Cumplimiento",
        "formato": "#,##0.00 \"m\"",
        "dax": "SUM(fact_metas_mensuales[meta_metraje_m])",
        "descripcion": "Meta acumulada de perforación comprometida contractualmente para el mes operativo."
    },
    {
        "tabla": "_Medidas",
        "nombre": "Cumplimiento de Meta (% Meta)",
        "categoria": "Cumplimiento",
        "formato": "0.0%",
        "dax": "DIVIDE([Metraje Perforado Total (m)], [Meta Metraje Mes (m)], 0)",
        "descripcion": "Porcentaje de avance alcanzado respecto a la meta contractual mensual."
    }
]

def exportar_catalogo_dax(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Exportar Markdown
    md_lines = [
        "# 📐 Catálogo Oficial de Medidas DAX - Rockdrill Group",
        "## Sistema Unificado de Business Intelligence y Analítica de Perforación\n",
        "| # | Tabla Destino | Nombre de Medida | Categoría | Formato | Fórmula DAX | Descripción |",
        "| :---: | :--- | :--- | :---: | :---: | :--- | :--- |"
    ]
    for idx, m in enumerate(MEDIDAS_DAX, start=1):
        md_lines.append(f"| {idx} | `{m['tabla']}` | **{m['nombre']}** | {m['categoria']} | `{m['formato']}` | `{m['dax']}` | {m['descripcion']} |")
        
    md_path = output_dir / "03_CATALOGO_MEDIDAS_DAX_OFICIALES.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    
    # 2. Exportar Script DAX para Editor Power BI / Tabular Model
    dax_script = ["// SCRIPT DAX OFICIAL ROCKDRILL GROUP - VERTIPAQ TABULAR MODEL", ""]
    for m in MEDIDAS_DAX:
        dax_script.append(f"// {m['nombre']} ({m['categoria']})")
        dax_script.append(f"// {m['descripcion']}")
        dax_script.append(f"{m['nombre']} = ")
        dax_script.append(f"    {m['dax']}")
        dax_script.append("")
        
    script_path = output_dir / "medidas_dax_powerbi.dax"
    script_path.write_text("\n".join(dax_script), encoding="utf-8")
    
    print(f"[OK] Catálogo DAX generado: {md_path}")
    print(f"[OK] Script DAX generado: {script_path}")

if __name__ == "__main__":
    exportar_catalogo_dax(Path(__file__).parent.parent / "docs")
