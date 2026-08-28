# Original User Request

## 2026-08-19T16:19:00Z

Pipeline integral, portable y de alta precisión para la descarga automatizada desde OWA, normalización de esquemas (135 y 156 columnas), asignación de turnos por cuadrilla/perforista, compilación de Control Interno y auditoría de metrajes día a día y turno a turno para los 18 contratos mineros de Rockdrill Group.

Working directory: C:\Proyectos Python\Detallados
Integrity mode: development

## Requirements

### R1. Descargador OWA Robusto y Bilingüe
- Descarga automatizada de los 18 contratos mineros para cualquier fecha calendario especificada (received:dd/mm/yyyy).
- Soporte para adjuntos en tarjetas directas, menús desplegables contextuales, visores online y archivos ZIP (ej. Andaychagua, Inmaculada, Cuculí).
- Detección precisa de ausencias con aviso explícito cuando un CTR no cuente con correo en la fecha pedida (ej. Americana).

### R2. Extracción y Normalización de Reportes Detallados
- Extracción de los 18 contratos mineros mapeando las 135 columnas canónicas.
- Asignación infalible de turnos operativos (A = Día / B = Noche) basada en:
  1. Transición de cuadrillas / perforistas distintos en el mismo día.
  2. Identificadores explícitos de turno (N, 2, B -> Turno B).
  3. Separación multi-taladro.
- Normalización automática de nombres de máquina contra el Maestro SAP corporativo y matriz de excepciones.

### R3. Compilación de Control Interno
- Compilación de todas las pestañas diarias del libro maestro RD.402.P.01.F.04 hasta la fecha de corte evaluada sin pérdida de registros ni desalineación de CTRs.

### R4. Conciliación y Auditoría Turno a Turno
- Cruce Full Outer Join por clave única {FECHA}-{MAQUINA}-{TURNO}.
- Clasificación automática de causas de discrepancia:
  - Intercambio de turno con suma diaria idéntica (ej. Catalina Huanca, Condestable).
  - Faltante de reporte detallado en origen (ej. Americana).
  - Registros en cero históricos en Control Interno (ej. Yauliyacu XRD125USS-001).
  - Ajustes de campo y redondeos decimales.

### R5. Generación de Informes Ejecutivos en PDF
- Generación de informes en PDF con diseño corporativo editorial para personas no técnicas (gerencia, operaciones y administradoras).

## Acceptance Criteria

### Precisión y Validación Operativa
- [ ] Conciliación día a día y turno a turno con >= 96% de coincidencia exacta (0.00 m de diferencia) sobre todas las claves evaluadas a la fecha de corte.
- [ ] Cero falsos positivos por diferencias en nombres de máquina o asignación errónea de turnos.
- [ ] Cuadratura del 100.00% en los contratos con reporte disponible (Ticlio, Cerro, Cobriza, Colquisiri, Cuculí, La Estrella, San Cristóbal, Yauricocha, Catalina Huanca, Condestable, Tambojasa, Raura).

### Rendimiento y Portabilidad
- [ ] Ejecución del pipeline integral en menos de 45 segundos.
- [ ] Código modular, desacoplado de usuarios o rutas hardcodeadas.
