# Catálogo Maestro de Palabras Clave para Clasificación de Tiempos y Motivos
**Código de Formato:** RD.402.P.01.F.01  
**Estándar:** 167 Columnas Canónicas (Rockdrill Group)  
**Versión:** 2.3.0 (Agosto 2026)

---

## 🎯 1. Objetivo y Principio de Mapeo Léxico-Semántico

Este documento establece el **diccionario de términos clave (N-grams)** y las **reglas de coincidencia léxica** para clasificar automáticamente las descripciones escritas en texto libre por las administradoras de contrato (columna *"SI ES OTROS \* INDICAR EL MOTIVO"*).

El objetivo es clasificar los motivos directamente hacia una de las **167 columnas oficiales** del formato maestro, agrupadas en las **5 categorías inamovibles de la convención interempresarial**.

---

## ⚙️ 2. Algoritmo de Preprocesamiento de Texto

Antes de evaluar las palabras clave, cada cadena de texto debe someterse a la siguiente pipeline de normalización:
1. **Normalización Unicode (NFKD):** Descomposición de caracteres acentuados (`Á` $\to$ `A`, `É` $\to$ `E`, `Í` $\to$ `I`, `Ó` $\to$ `O`, `Ú` $\to$ `U`, `Ñ` $\to$ `N`).
2. **Conversión a Mayúsculas:** `str.upper()`.
3. **Limpieza de Puntuación:** Reemplazar signos especiales por espacios (`re.sub(r'[^A-Z0-9\s]', ' ', texto)`).
4. **Colapso de Espacios Múltiples:** Espacio simple entre palabras.

---

## 📚 3. Diccionario Canónico de Palabras Clave por Categoría

### 🟢 Categoría 1: OPERATIVO [COBRABLE] (Cols 55 a 59)
Actividades de avance productivo y entubado/revestimiento cobradas por metro o tarifa operativa.

| Destino Propuesto | Palabras Clave Primarias | Palabras Clave Secundarias / Variaciones de Campo |
| :--- | :--- | :--- |
| **`Perforación`** | `PERFORACION`, `PERFORANDO`, `AVANCE`, `PERFORAR` | `PERFORANDO EN`, `PERFORACION HQ`, `PERFORACION NQ`, `TALADRO` |
| **`Rimado`** | `RIMADO`, `REAMING`, `RIMAR`, `ESCARIADO` | `RIMADO CON BROCA`, `RIMADO HQ`, `AMPLIACION DE DIAMETRO` |
| **`Asentado / Retiro de revestimiento (Casing)`** | `CASING`, `REVESTIMIENTO`, `ASENTADO CASING`, `HWT`, `HW` | `ASENTADO DE TUBERIA HWT`, `RETIRO DE CASING`, `ENTUBADO CASING` |
| **`Instalación PVC`** | `PVC`, `TUBERIA PVC`, `TUBO PVC` | `INSTALACION DE PVC`, `ENTUBADO PVC`, `RANURADO PVC` |
| **`Reperforación`** | `REPERFORACION`, `RE PERFORACION`, `REPERFORAR` | `REPASADO DE SONDAJE`, `REPERFORANDO TRAMO` |

---

### 🔴 Categoría 2: MANTENIMIENTO [NO COBRABLE] (Cols 60 a 61)
Interrupciones por intervención mecánica o eléctrica sobre el equipo de perforación o sus componentes.

| Destino Propuesto | Palabras Clave Primarias | Palabras Clave Secundarias / Variaciones de Campo |
| :--- | :--- | :--- |
| **`Mantenimiento Preventivo`** | `PREVENTIVO`, `MANTENIMIENTO PROGRAMADO`, `CHECK LIST` | `PM 250`, `PM 500`, `PM 1000`, `CAMBIO DE ACEITE PROGRAMADO` |
| **`Mantenimiento Correctivo`** | `FALLA MECANICA`, `FALLA ELECTRICA`, `REPARACION`, `MANTTO`, `MANTENIMIENTO`, `MECANICO`, `ELECTRICO`, `INOPERATIVO`, `INOPERATIVA` | `CABEZAL`, `BOMBA DE AGUA`, `FMC`, `BEAN`, `MOTOR`, `MANGUERA HIDRAULICA`, `WINCHE`, `CABLE DE WINCHE`, `FUGA DE ACEITE`, `SOLDADURA`, `CAMBIO DE SELLO`, `VALVULA`, `PRESOSTATO`, `ENGRASE`, `PISTON`, `SENSOR`, `MORDAZAS`, `CAMBIO DE MORDAZA`, `MAQUINANDO BROCA`, `ARRANQUE DEL EQUIPO`, `SE ENGRASA`, `SE ACONDICIONA ACCESORIOS Y SE ENGRASA`, `BAJO PRESION DE MARTILLO` |

---

### 🟢 Categoría 3: STAND BY OPERATIVO [COBRABLE] (Cols 62 a 93)
Maniobras operacionales necesarias, estabilización del pozo, ensayos geotécnicos/hidrogeológicos y desmovilización.

| Destino Propuesto | Palabras Clave Primarias | Palabras Clave Secundarias / Variaciones de Campo |
| :--- | :--- | :--- |
| **`Lavado de sondaje`** | `LAVADO DE POZO`, `LAVADO DE SONDAJE`, `LAVADO` | `LAVANDO POZO`, `LIMPIEZA DE POZO CON AGUA`, `CIRCULACION DE AGUA` |
| **`Mezclado de lodos`** | `MEZCLADO DE LODOS`, `PREPARACION DE LODOS`, `MEZCLA DE ADITIVOS` | `PREPARANDO LODO`, `BENTONITA MEZCLA`, `POLIMERO MEZCLA` |
| **`Manipulación de tuberías`** | `MANIPULACION DE TUBERIA`, `MANIPULACION DE TUBERIAS`, `ARMADO DE LINEA`, `DESARMADO DE LINEA` | `ACOPLE DE BARRAS`, `DESACOPLE`, `MANIPULEO DE BARRAS` |
| **`Maniobras por descarga y carga de tuberías`** | `DESCARGA DE TUBERIA`, `CARGA Y DESCARGA`, `DESCARGUE DE TUBERIA`, `DESCARGA DE BARRAS`, `MANIOBRAS DE CARGA` | `DESCARGA DEL CAMION`, `BAJADA DE BARRAS`, `SACADA DE BARRAS`, `DESEMBONADA`, `CORTE DE TUBERIA`, `CHAVETA`, `CAMBIO DE BROCA`, `CAMBIO DE CORONA`, `CAMBIO DE ZAPATA`, `CAMBIO DE REAMER` |
| **`Acondicionamiento de sondaje`** | `ACONDICIONAMIENTO`, `ACONDICIONAR`, `ACONDICIONADO`, `ACONDICIONAMIENO`, `ACONDICONAMIENTO`, `ACONDICIONAMINETO`, `ACONDICIONMIENTO` | `ESTABILIZANDO SONDAJE`, `ESTABILIZADO DE SONDAJE`, `RETORNO DE AGUA`, `PERDIDA DE AGUA`, `NIVEL DE AGUA`, `LODOS`, `BENTONITA`, `POLIMERO`, `TORQUE`, `SELLADO DE SONDAJE`, `ALINEACION DE SONDAJE`, `BOMBEO DE AGUA`, `BOMBEO`, `RECUPERACION DE RETORNO`, `RECUPERAR RETORNO`, `RECUPERANDO RETORNO` |
| **`Cambio de línea`** | `CAMBIO DE LINEA`, `REDUCCION DE LINEA`, `CAMBIO A BQ`, `CAMBIO A NQ`, `CAMBIO A HQ` | `REDUCCION DE DIAMETRO`, `CAMBIO DE DIAMETRO` |
| **`Recuperación de sondaje`** | `RECUPERACION DE SONDAJE`, `RECUPERAR SONDAJE` | `REACONDICIONAMIENTO DE POZO PERDIDO` |
| **`Recuperación de materiales / atrapamiento (pesca)`** | `PESCA`, `ATRAPAMIENTO`, `ATRAPADA`, `ATRAPADO`, `BARRAS ATRAPADAS`, `RECUPERACION DE TUBERIA` | `RECUPERACION DE BAREL`, `RECUPERACION DE TUBO`, `RECUPERACION DE HERRAMIENTA`, `TRABAJOS DE RECUPERACION`, `QUENA HQ`, `RECUPERAR TUBERIA`, `LIBERAR TUBERIA`, `RECUPERACION HQ`, `RESCATE DE TUBERIA`, `PESCA DE TESTIGO`, `TUBO INTERIOR ATRAPADO` |
| **`Traslado entre cámaras de perforación`** | `TRASLADO ENTRE CAMARAS`, `CAMBIO DE CAMARA`, `TRASLADO DE EQUIPO`, `TRASLADO DE MAQUINA`, `MOVIMIENTO DE MAQUINA` | `MOVIMIENTO DE EQUIPO`, `TRASLADO ENTRE CABINAS`, `TRASLADO DE TALADRO A TALADRO` |
| **`Desmovilización`** | `DESMOVILIZACION`, `DESMOVILIZAR`, `RETIRO DE EQUIPOS`, `DESMONTAJE DE EQUIPO` | `DESARME DE PLATAFORMA`, `DESARME INTEGRAL`, `MAQUINA A SUPERFICIE` |
| **`Maniobras de problemas geológicos`** | `PROBLEMAS GEOLOGICOS`, `PROBLEMA GEOLOGICO` | `MANIOBRAS POR TERRENO`, `DIFICULTADES LITOLOGICAS` |
| **`Perforación en fallas y/o terrenos altamente fracturados`** | `FALLA`, `FRACTURADA`, `FRACTURADO`, `ZONA DE FALLA`, `ZONA FRACTURADA`, `TERRENO FRACTURADO` | `TERRENO INESTABLE`, `CAIDA DE TESTIGO`, `DERRUMBE`, `TERRENO DURO`, `CAVACIONES`, `TALADRO DESVIADO` |
| **`Medición de Desviación`** | `DESVIACION`, `GYRO`, `REFLEX`, `MEDICION`, `ORIENTACION` | `LANZADO DE PITAS`, `PITAJE`, `MEDICION DE TRAYECTORIA` |
| **`Orientación de Testigos`** | `ORIENTACION DE TESTIGOS`, `ORIENTACION DE TESTIGO`, `TESTIGO ORIENTADO` | `REFLEX ACT`, `MARCADO DE ORIENTACION` |
| **`Anclado de máquina de perforación`** | `ANCLAJE`, `ANCLADO`, `ACLAJE`, `PERNO DE ANCLAJE` | `PERNOS DE MAQUINA`, `FIJACION DE MAQUINA` |
| **`Perforación de perno de anclaje`** | `PERFORACION DE PERNO`, `PERFORACION DE PERNO DE ANCLAJE` | `PERFORANDO ANCLAJE`, `PERNO ANCLAJE` |
| **`Cementación`** | `CEMENTACION`, `CEMENTO`, `FRAGUADO`, `LECHADA`, `TAPON DE CEMENTO` | `INYECTANDO CEMENTO`, `PREPARACION DE LECHADA`, `ESPERA DE FRAGUADO` |
| **`Obturación de sondaje con packer`** | `PAKER`, `PACKER`, `PARCKER`, `OBTURADOR`, `OBTURACION`, `TAPON` | `SELLADO CON PACKER`, `INFLADO DE PACKER`, `ENSAYO CON PACKER` |
| **`Ensayo Lefranc`** | `LEFRAN`, `LEFRANC`, `PRUEBA LEFRANC` | `ENSAYO DE PERMEABILIDAD LEFRANC`, `CARGA CONSTANTE/VARIABLE` |
| **`Ensayo Lugeon`** | `LUGEON`, `PRUEBA LUGEON` | `ENSAYO DE PERMEABILIDAD LUGEON`, `PRESION ESCALONADA` |
| **`Prueba SPT`** | `SPT`, `PRUEBA SPT`, `PENETRACION ESTANDAR` | `ENSAYO SPT`, `GOLPES SPT` |
| **`Prueba Shelby`** | `SHELBY`, `SHELLBY`, `TUBO SHELBY` | `MUESTREO SHELBY`, `MUESTRA INALTERADA` |
| **`Pruebas Geotécnicas`** | `PRUEBAS GEOTECNICAS`, `PRUEBA GEOTECNICA`, `PRUEBAS DE SUELO` | `CARACTERIZACION GEOTECNICA`, `ENSAYO GEOTECNICO` |
| **`Prueba de nivel freático`** | `NIVEL FRIATICO`, `NIVEL FREATICO`, `NIVEL DE AGUA` | `MEDICION DE NIVEL FREATO`, `NIVEL ESTATICO` |
| **`Ensayo Air Lift`** | `AIR LIFT`, `AIRLIFT`, `ENSAYO AIR LIFT` | `BOMBEO AIR LIFT`, `PURGA CON AIRE` |
| **`Ensayo Slug Test`** | `SLUG TEST`, `SLUGTEST`, `ENSAYO SLUG` | `SLUG TEST DE PERMEABILIDAD` |
| **`Instalación de piezómetro Casagrande`** | `PIEZOMETRO CASAGRANDE`, `CASAGRANDE`, `CASA GRANDE` | `INSTALACION CASAGRANDE`, `TUBO CASAGRANDE` |
| **`Instalación de piezómetro de cuerda vibrante`** | `CUERDA VIBRANTE`, `PIEZOMETRO CUERDA VIBRANTE`, `VW PIEZOMETER` | `SENSOR CUERDA VIBRANTE`, `CELDA DE PRESION` |
| **`Instalación de inclinómetro`** | `INCLINOMETRO`, `INSTALACION DE INCLINOMETRO` | `TUBERIA DE INCLINOMETRIA`, `CASING INCLINOMETRICO` |
| **`Instalación de piezómetro multinivel`** | `PIEZOMETRO MULTINIVEL`, `MULTINIVEL`, `MULTILEVEL` | `SISTEMA MULTINIVEL`, `PUERTOS MULTINIVEL` |
| **`Prueba de lectura de inclinómetro`** | `LECTURA DE INCLINOMETRO`, `SONDA INCLINOMETRICA` | `PERFIL INCLINOMETRICO`, `MEDICION CON SONDA` |
| **`Toma de lecturas cuerda vibrante`** | `LECTURA CUERDA VIBRANTE`, `TOMA DE LECTURAS`, `DATALOGGER` | `READOUT CUERDA VIBRANTE`, `MONITOREO CUERDA VIBRANTE` |

---

### 🟡 Categoría 4: STAND BY INOPERATIVO [NO COBRABLE] (Cols 94 a 115)
Demoras internas imputables a la gestión de Rockdrill (cuadrilla, logística interna, mantenimiento, orden y seguridad interna).

| Destino Propuesto | Palabras Clave Primarias | Palabras Clave Secundarias / Variaciones de Campo |
| :--- | :--- | :--- |
| **`Desate de rocas`** | `DESATE`, `DESATE DE ROCAS`, `PLASTEO` | `DESATANDO LABOR`, `BANQUEO`, `PEINADO DE ROCA` |
| **`Orden y limpieza`** | `5S`, `LIMPIEZA`, `ORDEN Y LIMPIEZA` | `LAVADO DE PLATAFORMA`, `ACOMODO DE MATERIALES` |
| **`Recojo de lama`** | `LAMA`, `RECOJO DE LAMA` | `LIMPIEZA DE LAMA`, `EVACUACION DE LODO` |
| **`Poza de sedimentación`** | `POZA`, `POZA DE SEDIMENTACION`, `SEDIMENTACION` | `LIMPIEZA DE POZAS`, `DRAGADO DE POZA` |
| **`Estandarización`** | `ESTANDARIZACION`, `ENTABLADO`, `GEOMEMBRANA`, `MONTAJE` | `ALINEADO DE EQUIPO`, `NIVELADO`, `NIVELACION` |
| **`Desestandarización`** | `DESESTANDARIZACION`, `DESMONTAJE` | `RETIRO DE ENTABLADO`, `DESMONTAJE DE BASE` |
| **`Instalación de red de agua o drenaje`** | `DRENAJE`, `RED DE AGUA`, `INSTALACION DE AGUA` | `MANGUERA DE AGUA INTERNA`, `LINEA DE DRENAJE RD` |
| **`Instalación / Desinstalación de equipos`** | `INSTALACION DE EQUIPOS`, `DESINSTALACION DE EQUIPOS` | `ARMADO DE SISTEMA RD`, `CONEXION DE EQUIPOS` |
| **`Traslado de accesorios`** | `TRASLADO DE ACCESORIOS`, `CARGADO DE MATERIALES`, `ABASTECIMIENTO`, `ACARREO` | `APOYO A ALMACEN`, `APOYO AL AREA DE LOGISTICA`, `TRASLADO DE CAJAS`, `PEDIDOS MATERIALES` |
| **`Auditoría Interna`** | `AUDITORIA INTERNA`, `INSPECCION INTERNA RD` | `CONTROL DE CALIDAD RD`, `AUDITORIA HSEQ RD` |
| **`Capacitación (Interna)`** | `CHARLA`, `CAPACITACION`, `IPERC`, `REPARTO`, `GCOM`, `TRASLAPE`, `INDUCCION`, `PAUSAS ACTIVAS` | `HERRAMIENTAS DE GESTION`, `HERAMIENTAS DE GESTION`, `LLENADO DE REPORTE`, `REPORTE Y RELEVO`, `REVISION DE PETS`, `PETS`, `SE PASA VEO`, `VEO`, `OPT` |
| **`Cambio de punto`** | `CAMBIO DE PUNTO`, `MINI CAMBIO`, `REUBICACION` | `CORRIMIENTO DE TALADRO`, `REUBICACION EN CAMARA` |
| **`Espera de repuestos mecánicos`** | `ESPERA DE REPUESTO`, `REPUESTO`, `REPUESTOS MECANICOS`, `FALTA DE REPUESTO` | `REPUESTO EN TALLER`, `ENVIO DE PIEZA MECANICA`, `VALVULA TALLER` |
| **`Espera de materiales e insumos de perforación`** | `ESPERA DE MATERIALES`, `FALTA DE BROCA`, `FALTA DE MATERIAL`, `SISTEMA DE PERFORACION`, `CORE BAREL` | `ESPERA DE ACCESORIOS`, `FALTA DE HERRAMIENTA`, `FALTA DE MATERIALES`, `ESPERA DE CORE BARREL` |
| **`Traslado de personal`** | `TRASLADO DE PERSONAL`, `CAMBIO DE GUARDIA INTERNO` | `MOVILIZACION DE CUADRILLA RD` |
| **`Refrigerio`** | `REFRIGERIO`, `ALMUERZO`, `CENA`, `ALIMENTACION`, `ALIMENTOS` | `HORA DE COMIDA`, `CAMBIO DE GUARDIA` |
| **`Traslado de máquina (Interno RD)`** | `TRASLADO DE MAQUINA INTERNO`, `MOVILIZACION INTERNA RD` | `TRASLADO POR REUBICACION RD` |
| **`Falta de personal`** | `FALTA DE PERSONAL`, `FALTA DE PEROSNAL`, `SIN PERSONAL`, `PERFORISTA`, `AYUDANTE`, `SIN CUADRILLA` | `DESCANSO MEDICO`, `INASISTENCIA`, `VACACIONES`, `FALTA PERSONAL`, `FALTA DE OPERADOR`, `SIN OPERADOR`, `INCOMPLETA`, `FALTA DE CUADRILLA`, `PERSONAL INCOMPLETO` |
| **`Falta / Problemas herramientas RD`** | `HERRAMIENTAS RD`, `FALTA HERRAMIENTAS RD` | `LLAVES STILLSON`, `PRENSA DE MANO` |
| **`Paralización por fiestas`** | `FIESTAS PATRIAS`, `FIESTAS`, `DESFILE`, `FERIADO`, `ANO NUEVO`, `NAVIDAD`, `DIA DEL MINERO` | `DIA DEL TRABAJADOR`, `CELEBRACION DIA`, `DIA DEL PADRE`, `CUMPLEANOS`, `COMPARTIR` |
| **`Pare RD`** | `PARE RD`, `PARADA RD` | `PARALIZACION POR DECISION RD` |
| **`Otros*`** | `OTROS RD`, `DEMORA RD NO ESPECIFICADA` | `MOTIVOS DIVERSOS RD` |

---

### 🔵 Categoría 5: STAND BY CLIENTE [COBRABLE] (Cols 116 a 144)
Paradas operacionales imputables a la empresa minera/cliente (servicios mina, interferencias, reguladores, fenómenos naturales, eventos sociales y autorizaciones).

| Destino Propuesto | Palabras Clave Primarias | Palabras Clave Secundarias / Variaciones de Campo |
| :--- | :--- | :--- |
| **`Voladura`** | `VOLADURA`, `DISPARO`, `TIRO`, `EXPLOSIVOS`, `CHISPEO` | `HORA DE DISPARO`, `VOLADURA EN LABOR CONTIGUA` |
| **`Falta de agua`** | `FALTA DE AGUA`, `CORTE DE AGUA`, `BAJA PRESION DE AGUA`, `SIN AGUA` | `AGUA MINA`, `PRESION DE AGUA`, `EXCESO PRESION DE AGUA`, `LINEA DE AGUA MINA` |
| **`Falta de energía`** | `FALTA DE ENERGIA`, `CORTE DE ENERGIA`, `CORTE DE LUZ`, `SIN ENERGIA`, `SIN LUZ` | `FLUIDO ELECTRICO`, `SUBESTACION`, `CAIDA DE TENSION`, `CORTE ELECTRICO` |
| **`Falta de ventilación`** | `VENTILACION`, `GASES`, `MANGA DE VENTILACION`, `HUMO`, `VENTILADOR` | `MONOXIDO`, `CO2`, `FALTA DE AIRE`, `PRESION DE AIRE` |
| **`Falta de servicios`** | `FALTA DE SERVICIOS`, `SERVICIOS MINA`, `LINEA DE AIRE MINA` | `CORTE DE SERVICIOS`, `SUMINISTRO MINA INTERRUMPIDO` |
| **`Espera de programa`** | `ESPERA DE PROGRAMA`, `PROGRAMA GEOLOGIA`, `NUEVO PROGRAMA` | `MODIFICACION DE PROGRAMA`, `CONFIRMACION DE PROGRAMA` |
| **`Espera de cámara`** | `ESPERA DE CAMARA`, `CAMARA MINA`, `ENTREGA DE CAMARA` | `LABOR NO DISPONIBLE`, `CAMARA EN AVANCE` |
| **`Espera de sostenimiento`** | `SOSTENIMIENTO`, `CUADROS`, `MALLA`, `SHOTCRETE`, `PERNOS MINA` | `GEOMECANICA`, `LIBERACION GEOMECANICA`, `INSPECCION GEOMECANICA` |
| **`Espera de scoop`** | `SCOOP`, `LIMPIEZA DE CARGA`, `CARGUIO`, `DUMPER`, `VOLQUETE` | `TRANSITO`, `DESMONTE EN CAMARA`, `TRANSITO DE EQUIPO` |
| **`Espera de marcado de punto`** | `MARCADO DE PUNTO`, `PUNTO DE PERFORACION`, `MARCADO`, `AZIMUT` | `COORDINADAS`, `DEFINICION DE SONDAJE`, `PRELOGUEO` |
| **`Espera de Topografía`** | `TOPOGRAFIA`, `TOPOGRAFICO`, `TOPOGAFICO`, `TOPOGRAFO` | `ALINEAMIENTO TOPOGRAFICO`, `LEVANTAMIENTO TOPOGRAFICO`, `ESPERANDO TOPOGRAFO` |
| **`Espera de grúa`** | `GRUA`, `CAMION GRUA`, `GRUA CLIENTE`, `EQUIPO DE IZAJE` | `ESPERA DE GRUA DE MINA`, `MANIOBRA CON GRUA` |
| **`Traslado de máquina (Cliente)`** | `TRASLADO DE MAQUINA CLIENTE`, `REMOLQUE CLIENTE` | `TRASLADO CON EQUIPO MINA` |
| **`Apoyo a geología`** | `APOYO A GEOLOGIA`, `LOGUEO`, `MUESTREO GEOLOGIA` | `REVISION POR GEOLOGO`, `INSPECCION GEOLOGICA EN CAMARA` |
| **`Auditoría externa`** | `OSINERGMIN`, `OSINERMING`, `SUNAFIL`, `MINEM`, `AUDITORIA EXTERNA`, `AUDITORIA` | `VISITA DE OSINERGMIN`, `VISITA DEL ING`, `VISITA CORPORATIVO`, `VISITA SEGURIDAD`, `REUNION DE COMITE`, `INSPECCION`, `VISITA DE SEGURIDAD HOC`, `VISITA DE HIGIENE`, `VISITA DEL BROCAL`, `VISITA HOC`, `VISITA POR SEGURIDAD` |
| **`Capacitación (Externa Cliente)`** | `CAPACITACION CLIENTE`, `INDUCCION MINA`, `PARADA GENERAL MINA` | `CURSO MINA`, `CAPACITACION OBLIGATORIA CLIENTE` |
| **`Falta de habilitación de cámara o plataforma`** | `RIPEO DE CAMARA`, `DESESTABILIZACION DE CAMARA`, `BLOQUEO DE ACCESO`, `ACCESO BLOQUEADO`, `HABILITACION DE CAMARA`, `PLATAFORMA` | `LIBERACION DE CAMARA`, `FALTA LABOR`, `NO SE INGRESA A CAMARA`, `FALTA DE ACCESO`, `SIN PASE`, `DESLIZAMIENTO`, `SE BLOQUEO LA CAMARA`, `DESMONTE`, `RAMPA BLOQUEADA` |
| **`Espera de orden cliente`** | `ORDEN CLIENTE`, `ORDEN DEL CLIENTE`, `ORDEN DE GEOLOGIA`, `ORDEN DE MINA` | `PARADA POR GEOLOGIA`, `ESPERA DE CONFIRMACION`, `ESPERA DE LA GESTION`, `ESPERANDO COORDINACIONES`, `TRABAJOS PAUSADOS`, `FALTA ING DE SEGURIDAD` |
| **`Condiciones climáticas`** | `LLUVIA`, `CLIMA`, `TORMENTA`, `NIEVE`, `NEBLINA`, `CLIMATICAS`, `TEMPORAL` | `ALERTA ROJA`, `ALERTA AMARILLA`, `DESCARGAS ELECTRICAS` |
| **`Inundación`** | `INUNDACION`, `INUNDADA`, `AGUA EMPOZADA`, `ANIEGO`, `CAMARA INUNDADA` | `BOMBEO MINA REBASADO`, `AGUA EN LABOR` |
| **`Paralización por estrés térmico o alta temperatura`** | `ESTRES TERMICO`, `ESTRESS TERMICO`, `TEMPERATURA`, `CALOR`, `ACLIMATACION` | `GOLPE DE CALOR`, `EXCESO DE CALOR EN CAMARA` |
| **`Parada por sismo/microsismo`** | `SISMO`, `MICROSISMO`, `EVENTO MICROSISMICO`, `REPLICAS DE SISMO` | `EVACUACION POR SISMO`, `PARADA POR REPLICAS`, `SIMULACRO DE SISMO` |
| **`Conflicto social`** | `CONFLICTO SOCIAL`, `PARO COMUNAL`, `BLOQUEO DE GARITA`, `HUELGA` | `BLOQUEO DE CARRETERA`, `PARO DE COMUNIDAD`, `PROBLEMAS SOCIALES` |
| **`Paralización cliente`** | `PARALIZACION POR EL CLIENTE`, `PARALIZACION CLIENTE`, `PARALIZACION MINA` | `PARADA GENERAL DE MINA`, `PARADA DE SEGURIDAD MINA` |
| **`Pare Cía`** | `PARE CIA`, `PARE CLIENTE` | `PARADA COMPAÑIA`, `DETENCION POR COMPAÑIA` |
| **`Prueba PZ`** | `PRUEBA PZ`, `PIEZOMETRO`, `PIEZOMETRICO` | `PRUEBA PIEZOMETRICA CLIENTE` |
| **`Trabajos paralelos mina`** | `TRABAJOS PARALELOS MINA`, `INTERFERENCIA MINA`, `LABOR COMPARTIDA` | `TRABAJO DE TERCEROS EN CAMARA` |
| **`Otros*`** | `OTROS CLIENTE`, `STAND BY CLIENTE NO ESPECIFICADO` | `PARADAS CLIENTE DIVERSAS` |

---

## 🛑 4. Criterios de Derivación a `OBSERVACIONES`

Un registro de texto libre debe clasificarse como `OBSERVACIONES` (sin asignación a una columna tarifaria específica) **únicamente** cuando cumpla con los siguientes criterios:
1. **Ambigüedad Extrema:** Frases genéricas como *"problemas operativos"*, *"revisión de turno"*, *"horas varias"*, *"en espera"*.
2. **Descripciones Meramente Informativas:** Textos como *"taladro finalizado en 150m con retorno normal"*, *"se deja testigo en cajas de cartón"*, *"guardia sin novedad"*.
3. **Múltiples Motivos Contradictorios:** Registros con 3 o más razones dispares sin indicar horas por motivo (*"1h mecanico 2h geologia 3h falta agua"*).
