# 03. Especificación Funcional de Dashboards: Visión de Impacto y Desglose Táctico
**Proyecto**: Sistema Unificado de Business Intelligence y Analítica de Perforación  
**Ubicación**: `C:/Proyectos Python/Detallados/docs/03_ESPECIFICACION_DASHBOARDS_OPERATIVO_Y_GERENCIAL.md`  
**Estándar de Diseño**: Google "The Art of Data Visualization" & IBCS (International Business Communication Standards)  
**Organización**: Rockdrill Group  
**Autores**: `bi_visualization_engineer` & `business_vision_strategist`  

---

## 🎨 1. Principios de Visualización de Alto Impacto (Google Data Viz)

Siguiendo las directrices de diseño de visualización de datos de Google:
1. **Claridad Visual Inmediata («At a Glance»):** La primera pantalla no satura con tablas densas; comunica en menos de 5 segundos el estado de salud de la operación respecto a las metas.
2. **Jerarquía Visual de 3 Niveles:**
   - **Nivel 1 (Slide 1 - Hero Slide):** Impacto ejecutivo macro (Cumplimiento de Metas, Horas de Perforación «La Brújula», Curva S acumulada y DM % global).
   - **Nivel 2 (Slide 2 - Control Táctico):** Rendimiento por perforista, balance de guardias (A vs B) y estructura de horas cobrables vs. no cobrables.
   - **Nivel 3 (Slide 3 - Causa Raíz y Anomalías):** Matriz horaria granular de 24h, registro de paradas imputables y alertas de campo para rectificación.

---

## 🌟 2. Slide 1: Impacto Ejecutivo y Monitoreo Estratégico (Hero Slide)

### 🎯 Propósito:
Proveer a la Gerencia General, Dirección y Jefatura de Operaciones la visión estratégica inmediata de cumplimiento del plan mensual minero (ciclo 26 al 25) y salud mecánica.

```text
========================================================================================================================
SLIDE 1: RESUMEN EJECUTIVO DE ALTO IMPACTO (HERO SLIDE)
========================================================================================================================
[FILTROS GLOBALES]: Mes Operativo [ ENE-25 v ] | CTR [ TODOS v ] | Tipo Operación [ Superficie / Mina ]
------------------------------------------------------------------------------------------------------------------------
[CARD 1 - NORTH STAR]      [CARD 2 - LA BRÚJULA]      [CARD 3 - EFICIENCIA]      [CARD 4 - FACTURABILIDAD] [CARD 5 - SALUD]
% CUMPLIMIENTO META        HORAS PERFORACIÓN EFECTIVA RATIO DE PENETRACIÓN       % HORAS COBRABLES         DISP. MECÁNICA
98.4% de la Meta           1,420.5 hrs                3.18 m/hr                  89.2% Facturable          91.8% (Target: 90%)
(▲ +2.1% vs mes anterior)  (Meta: 1,380 hrs)          (▲ +0.25 m/h vs target)    (▼ -1.5% glosa potencial)(Estado: Óptimo)
------------------------------------------------------------------------------------------------------------------------
[VISUAL 1: CURVA S DE AVANCE ACUMULADO VS PLAN MINERO]               [VISUAL 2: BULLET CHART / VELOCÍMETRO DM %]
Comparativa diaria acumulada del 26 al 25:                           Disponibilidad Mecánica por Contrato Minero:
Metros                                                               CTR Colquijirca  : [████████████████░░] 93.1% (Verde)
30,000 |                              .-* (Real: 28,882m)            CTR Raura        : [██████████████░░░░] 91.5% (Verde)
20,000 |                        .---''   (Meta: 29,350m)             CTR Condestable  : [█████████████░░░░░] 89.0% (Amarillo)
10,000 |                 .---''                                      CTR Toromocho    : [██████████░░░░░░░░] 82.0% (Rojo)
     0 +----------------------------------------------               ---------------------------------------------------
       D26  D30  D05  D10  D15  D20  D25                             ■ Línea de Target Contractual: 90.0%
========================================================================================================================
```

---

## 🛠️ 3. Slide 2: Diagnóstico Táctico y Rendimiento Operativo

### 🎯 Propósito:
Proveer al Jefe de Operaciones y Residentes la capacidad de detectar desvíos entre cuadrillas, desempeño individual de perforistas y riesgo de no cobrabilidad.

```text
========================================================================================================================
SLIDE 2: CONTROL OPERATIVO, CUADRILLAS Y COBRABILIDAD
========================================================================================================================
[FILTROS]: CTR [ COLQUIJIRCA v ] | Máquina [ XRD80WDTH-001 v ] | Turno [ A / B ]
------------------------------------------------------------------------------------------------------------------------
[VISUAL 1: RANKING DE PERFORISTAS (METROS & RATIO M/H)]              [VISUAL 2: ESTRUCTURA DE COBRABILIDAD HORARIA]
Desempeño individual por guardia:                                    Desglose de las 5 Categorías de Disponibilidad:
1. Juan Perez   : 145.0m (3.42 m/h) | Turno A [Top Performer]        ■ Operativo Cobrable               : 58.2% (14.0h)
2. Carlos Soto  : 122.0m (2.95 m/h) | Turno B                        ■ Stand By Cliente (Cobrable)       : 18.5% ( 4.4h)
3. Marco Ruiz   : 110.0m (2.60 m/h) | Turno A                        ■ Stand By Operativo (Cobrable)     : 12.5% ( 3.0h)
4. Pedro Gomez  :  78.0m (1.85 m/h) | Turno B [Alerta Bajo Rend.]    ■ Mantenimiento RD (No Cobrable)    :  6.4% ( 1.5h)
                                                                     ■ Stand By Inoperativo (No Cobrable):  4.4% ( 1.1h)
------------------------------------------------------------------------------------------------------------------------
[VISUAL 3: COMPARATIVA BALANCE DE GUARDIA (TURNO A VS B)]            [VISUAL 4: TOP ALERTAS DE PARADAS ACCIONABLES]
Metros Perforados por Turno:                                         Causas Raíz de Horas No Cobrables:
• Guardia A (Día)   : 54.5% (15,740 m)                               • Falta de Personal RD : 42.5 hrs -> Alerta RRHH
• Guardia B (Noche) : 45.5% (13,142 m) -> Brecha a corregir          • Espera Scoop Mina    : 38.0 hrs -> Sustento Cobro
========================================================================================================================
```

---

## 🔍 4. Slide 3: Desglose Granular de 24h, Causa Raíz y Auditoría de Campo

### 🎯 Propósito:
Revisión celda a celda de la matriz horaria y **gestión del log de anomalías detectadas en campo** para solicitar su rectificación antes del cierre mensual.

```text
========================================================================================================================
SLIDE 3: MATRIZ HORARIA DETALLADA Y LOG DE ANOMALÍAS DE CAMPO
========================================================================================================================
[TABLA 1: MATRIZ DE 24 HORAS POR MÁQUINA Y ACTIVIDAD]
Fecha      | CTR         | Máquina   | Turno | Perfo (h) | Ensayo(h)| Mtto(h) | SBC(h) | SBI(h) | Total(h)| Estado
2026-08-27 | COLQUIJIRCA | XRD80-001 | A     | 8.5       | 2.0      | 0.5     | 1.0    | 0.0    | 12.0    | Balanceado OK
2026-08-27 | COLQUIJIRCA | XRD80-001 | B     | 6.0       | 0.0      | 4.0     | 2.0    | 0.0    | 12.0    | Balanceado OK
2026-08-27 | COLQUIJIRCA | TL55-001  | A     | 0.0       | 0.0      | 12.0    | 0.0    | 0.0    | 12.0    | Standby Mtto
------------------------------------------------------------------------------------------------------------------------
[TABLA 2: LOG DE ANOMALÍAS Y SOLICITUD DE RECTIFICACIÓN A CAMPO]
Fecha      | CTR         | Máquina   | Guardia | Código Anomalía            | Detalle / Valor Observado | Acción Requerida
2026-08-26 | CONDESTABLE | M4C-01    | B       | ERR_BALANCE_GUARDIA_14H    | Suma reportada: 14.5 hrs  | Rectificar en Mina
2026-08-25 | RAURA       | XRD80-01  | A       | ERR_PERFORISTA_NO_ASIGNADO | Campo Perforista vacío     | Solicitar Fotocheck
2026-08-24 | COLQUIJIRCA | XRD100-01 | A       | ERR_MONOTONIA_COTAS        | HASTA (120m) < DESDE (125m)| Corregir Cota
========================================================================================================================
```
