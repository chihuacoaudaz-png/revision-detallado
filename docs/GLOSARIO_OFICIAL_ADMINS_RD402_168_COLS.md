# GLOSARIO DIDÁCTICO OFICIAL DE TÉRMINOS — REPORTE DETALLADO DE AVANCE (168 COLUMNAS)
**Documento Técnico SIG:** Formato `RD.402.P.01.F.01`  
**Empresa:** Rockdrill Group — Sistema Integrado de Gestión (SIG) & Control de Operaciones  
**Versión:** 3.1.0 (Versión Definitiva SIG)  
**Destinatarios:** Administradoras de Contrato, Supervisores de Perforación y Residentes  

---

## 📌 Reglas de Oro para el Llenado Diario del Detallado

1. **Cuadre Obligatorio de 12.0 Horas:**  
   Cada fila de guardia (día o noche) debe totalizar estrictamente **12.0 horas** en la columna `TIEMPO TOTAL` (Col 146). No puede haber guardias con más o menos de 12 horas.
2. **Criterio de Cobrabilidad:**  
   - 🟢 **COBRABLE:** Actividades productivas del taladro o paradas causadas por la mina.  
   - 🔴 **NO COBRABLE:** Fallas mecánicas de la perforadora o demoras internas de Rockdrill.
3. **Repuestos vs Materiales:**  
   - **`Espera de repuestos mecánicos` (Col 108):** Piezas de máquina a cargo del taller de mantenimiento RD.  
   - **`Espera de materiales e insumos` (Col 109):** Brocas, tubos y aditivos a cargo de logística interna RD.
4. **Sostenimiento vs Servicios:**  
   - **`Espera de sostenimiento` (Col 127):** Estallido de roca (*rockburst*), caída de rocas o espera de pernos/shotcrete por geomecánica mina.  
   - **`Falta de servicios` (Col 123):** Corte o caída de presión de aire comprimido suministrado por la mina.

---

## 🎨 Semáforo de Cobrabilidad y Tipos de Stand By

| Categoría de Tiempo | Rango de Columnas | Cobrabilidad | ¿Quién asume la responsabilidad? |
| :--- | :---: | :---: | :--- |
| 🟢 **OPERATIVO** | Cols 53 a 56 (4 cols) | **COBRABLE** | Producción efectiva de perforación y avance en roca. |
| 🔴 **MANTENIMIENTO** | Cols 57 a 58 (2 cols) | **NO COBRABLE** | Taller mecánico y equipo Rockdrill (mantenimiento y averías). |
| 🟢 **STAND BY OPERATIVO** | Cols 59 a 97 (39 cols) | **COBRABLE** | Maniobras necesarias del taladro, geotecnia e instrumentación. |
| 🟡 **STAND BY INOPERATIVO** | Cols 98 a 118 (21 cols) | **NO COBRABLE** | Demoras internas de Rockdrill (cuadrilla, logística interna, seguridad RD). |
| 🔵 **STAND BY CLIENTE** | Cols 119 a 145 (27 cols) | **COBRABLE** | Interrupciones causadas por la mina (servicios, topografía, clima, geomecánica). |

---

## 📖 Glosario Exhaustivo de las 168 Columnas del Detallado

| N° | Col | Nombre en el Detallado | Tipo de Stand By / Bloque | Cobrabilidad | Explicación Didáctica para la Administradora |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **1** | A | DÍAS | DÍAS | DATO | Fecha calendario de la guardia de perforación (día/mes/año). |
| **2** | B | NOMBRE | SONDAJE | DATO | Código oficial del taladro asignado por Geología mina (ej. DDH-045). |
| **3** | C | PROFUNDIDAD | SONDAJE | DATO | Profundidad total programada del pozo en metros lineales. |
| **4** | D | LINEA | SONDAJE | DATO | Diámetro de perforación: PQ (122.6mm), HQ (96mm), NQ (75.7mm) o BQ (60mm). |
| **5** | E | INCLINACIÓN | SONDAJE | DATO | Ángulo del pozo respecto a la horizontal (+ hacia arriba, - hacia abajo). |
| **6** | F | DESDE | AVANCE DIARIO | METRAJE | Profundidad inicial del taladro al comenzar el turno. |
| **7** | G | HASTA | AVANCE DIARIO | METRAJE | Profundidad final alcanzada por la broca al terminar el turno. |
| **8** | H | TURNO (A=1;B=2) | AVANCE DIARIO | DATO | Turno de trabajo: A = Guardia Día (1), B = Guardia Noche (2). |
| **9** | I | GRUPO | AVANCE DIARIO | DATO | Grupo o cuadrilla de trabajo asignada a la máquina (G1, G2, G3). |
| **10** | J | METRAJE | AVANCE DIARIO | METRAJE | Avance lineal perforado en la guardia (Fórmula: HASTA - DESDE). |
| **11** | K | HORAS EXTRAS | AVANCE DIARIO | DATO | Horas extraordinarias laboradas por la cuadrilla fuera de la jornada regular. |
| **12** | L | PERFORISTA | AVANCE DIARIO | DATO | Nombre y apellido del operador titular de la máquina de perforación. |
| **13** | M | AYUDANTE | AVANCE DIARIO | DATO | Nombre del primer asistente de perforación. |
| **14** | N | AYUDANTE | AVANCE DIARIO | DATO | Nombre del segundo asistente de perforación (si aplica cuadrilla triple). |
| **15** | O | TOTAL metraje del dia | AVANCE DIARIO | METRAJE | Suma total de metros avanzados en las 24 horas del día (Turno A + Turno B). |
| **16** | P | ACUMULADO | COMPARATIVO | DATO | Metraje total acumulado perforado en el pozo hasta la fecha. |
| **17** | Q | PROYECTADO | COMPARATIVO | DATO | Metros programados a avanzar según el plan mensual del contrato. |
| **18** | R | META | COMPARATIVO | DATO | Meta contractual diaria o mensual fijada para la máquina. |
| **19** | S | MARCA | BROCA | DATO | Fabricante de la broca diamantina (ej. Boart Longyear, Fordia, Di-Corp). |
| **20** | T | SERIE | BROCA | DATO | Número de serie de fábrica grabado en el cuerpo de la corona. |
| **21** | U | Nº BROCA | BROCA | DATO | Correlativo interno asignado a la broca en el proyecto. |
| **22** | V | ESTADO DE LA BROCA | BROCA | DATO | Condición: Nueva (N), Usada (U), Descartada (D) o Pulida (P). |
| **23** | W | MARCA | ESCARIADOR | DATO | Fabricante del escariador / reaming shell. |
| **24** | X | Nº ESCARIADOR | ESCARIADOR | DATO | Correlativo interno del escariador en la operación. |
| **25** | Y | ESTADO DEL ESCARIADOR | ESCARIADOR | DATO | Condición física del escariador (Nuevo, Usado, Descartado). |
| **26** | Z | BENTONITA - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Nombre comercial de la arcilla viscosificadora (ej. Max Gel, Bentopol). |
| **27** | AA | BENTONITA - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad física consumida en la guardia. |
| **28** | AB | BENTONITA - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida (Bolsa x 25 kg, Saco x 50 lb). |
| **29** | AC | PAC - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Polímero celulósico reductor de filtrado (ej. PAC R, PAC L). |
| **30** | AD | PAC - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad de PAC dosificada en la tina. |
| **31** | AE | PAC - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida del PAC (Saco / Balde). |
| **32** | AF | POLIMERO - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Polímero sintético estabilizador de lutitas y lubricante (ej. Poly Drill, CR 650). |
| **33** | AG | POLIMERO - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad consumida en el turno. |
| **34** | AH | POLIMERO - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de despacho (Galón, Balde x 20 L, Saco). |
| **35** | AI | LUBRICANTES - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Grasa para barras o aditivo reductor de torque (ej. Torqueless, Rod Grease). |
| **36** | AJ | LUBRICANTES - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad utilizada para engrase de sarta de perforación. |
| **37** | AK | LUBRICANTES - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida (Balde x 5 Gal, Pote x 16 kg). |
| **38** | AL | CONTROLADOR DE PH Y DUREZA - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Químico acondicionador de agua de lodos (ej. Ceniza de soda, Bicarbonato). |
| **39** | AM | CONTROLADOR DE PH Y DUREZA - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad dosificada en las tinas de agua. |
| **40** | AN | CONTROLADOR DE PH Y DUREZA - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida (Bolsa x 25 kg, Saco). |
| **41** | AO | INHIBIDORES - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Químico anti-hinchamiento de arcillas expansivas (ej. Cloruro de Potasio KCl). |
| **42** | AP | INHIBIDORES - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad consumida en la guardia. |
| **43** | AQ | INHIBIDORES - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida (Saco / Galón). |
| **44** | AR | ESTABILIZADOR - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Producto sellador de microfracturas en pared del taladro (ej. Star-Seal). |
| **45** | AS | ESTABILIZADOR - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad dosificada en la preparación de fluidos. |
| **46** | AT | ESTABILIZADOR - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida (Bolsa / Balde). |
| **47** | AU | OTROS - CLASIFICACIÓN | ADITIVOS (X UNIDADES) | CONSUMO | Tipo o familia del producto especial utilizado. |
| **48** | AV | OTROS - PRODUCTO | ADITIVOS (X UNIDADES) | CONSUMO | Nombre comercial del aditivo especial no catalogado en bloques anteriores. |
| **49** | AW | OTROS - CANT. | ADITIVOS (X UNIDADES) | CONSUMO | Cantidad consumida en el turno. |
| **50** | AX | OTROS - UND. | ADITIVOS (X UNIDADES) | DATO | Unidad de medida del producto. |
| **51** | AY | PETROLEO - CANT. | COMBUSTIBLE | CONSUMO | Volumen de combustible diésel suministrado a la perforadora o grupo. |
| **52** | AZ | PETROLEO - GLN | COMBUSTIBLE | DATO | Unidad de medida estándar (Galones americanos). |
| **53** | BA | Perforación | OPERATIVO | COBRABLE | Broca rotando y cortando roca en fondo con extracción continua de testigo. |
| **54** | BB | Rimado | OPERATIVO | COBRABLE | Ensanchamiento o calibración del taladro con corona escariadora. |
| **55** | BC | Asentado / Retiro de revestimiento (Casing) | OPERATIVO | COBRABLE | Instalación o extracción de tubería metálica de revestimiento (HWT/HW/NW). |
| **56** | BD | RePerforación | OPERATIVO | COBRABLE | Corte y repaso de tramos colapsados que se derrumbaron dentro del pozo. |
| **57** | BE | Preventivo | MANTENIMIENTO | NO COBRABLE | Mantenimiento planificado por horómetro (PM 250, 500, 1000 hrs, cambio aceite/filtros). |
| **58** | BF | Correctivo | MANTENIMIENTO | NO COBRABLE | Parada por avería mecánica o eléctrica de la máquina, bombas de lodos o winche. |
| **59** | BG | Lavado de sondaje | STAND BY OPERATIVO | COBRABLE | Circulación de agua limpia para evacuar detritos antes de ingresar barras o cambiar broca. |
| **60** | BH | Mezclado de lodos | STAND BY OPERATIVO | COBRABLE | Tiempo dedicado a la preparación y batido de aditivos químicos en las tinas. |
| **61** | BI | Manipulación de tuberías | STAND BY OPERATIVO | COBRABLE | Acople, desacople y verificación de roscas de barras de perforación en la plataforma. |
| **62** | BJ | Acondicionamiento de sondaje | STAND BY OPERATIVO | COBRABLE | Inyección de mezclas densas para sellar fracturas y recuperar retorno de agua. |
| **63** | BK | Cambio de línea | STAND BY OPERATIVO | COBRABLE | Reducción de diámetro de perforación (ej. de HQ a NQ o de NQ a BQ). |
| **64** | BL | Recuperación de sondaje por problemas geologicos | STAND BY OPERATIVO | COBRABLE | Maniobras para salvar el pozo ante colapsos severos del macizo o cavernas. |
| **65** | BM | Recuperación de materiales y o maniobras por atrapamiento | STAND BY OPERATIVO | COBRABLE | Pesca y rescate de barras o tubos interiores atascados en el taladro. |
| **66** | BN | Maniobras por descarga y carga de tuberías (por problemas geologicos) | STAND BY OPERATIVO | COBRABLE | Sacada y bajada completa de tuberías forzada por condiciones del terreno. |
| **67** | BO | Perforación en fallas y/o terrenos altamente fracturados | STAND BY OPERATIVO | COBRABLE | Avance a parámetros lentos y controlados en zonas de falla o cizalla. |
| **68** | BP | Medición de Desviación | STAND BY OPERATIVO | COBRABLE | Toma de trayectoria espacial del pozo con instrumentos Gyro o Reflex. |
| **69** | BQ | Traslado entre cámaras de perforación | STAND BY OPERATIVO | COBRABLE | Movilización de la perforadora de una cámara a otra según programa geológico mina. |
| **70** | BR | Cambio de punto de perforacion | STAND BY OPERATIVO | COBRABLE | Reubicación de la máquina dentro de la misma cámara para iniciar nuevo taladro. |
| **71** | BS | Anclado de máquina de perforación | STAND BY OPERATIVO | COBRABLE | Fijación y nivelación de la base de la perforadora al piso de la labor. |
| **72** | BT | Perforación de perno de anclaje | STAND BY OPERATIVO | COBRABLE | Perforación de taladros cortos para colocar los pernos de fijación de la máquina. |
| **73** | BU | Cementación de perno de anclaje y fraguado | STAND BY OPERATIVO | COBRABLE | Inyección de resina o lechada en pernos de anclaje y tiempo de endurecimiento. |
| **74** | BV | Cementado y fraguado de sondaje | STAND BY OPERATIVO | COBRABLE | Inyección de cemento dentro del pozo para taponar agua o consolidar paredes. |
| **75** | BW | Obturación/Sellado de sondaje con packer | STAND BY OPERATIVO | COBRABLE | Instalación de obturadores mecánicos/inflables para aislar tramos del pozo. |
| **76** | BX | Sellado de Sondaje | STAND BY OPERATIVO | COBRABLE | Sellado final del collar o boca de pozo según especificación ambiental/geológica. |
| **77** | BY | Inyección de lechada de cemento | STAND BY OPERATIVO | COBRABLE | Bombeo de pasta de cemento para impermeabilizar horizontes acuíferos. |
| **78** | BZ | Ensayo Lefranc | STAND BY OPERATIVO | COBRABLE | Prueba de permeabilidad in situ a nivel constante o variable en suelos/roca blanda. |
| **79** | CA | Ensayo Lugeon | STAND BY OPERATIVO | COBRABLE | Prueba de permeabilidad en roca bajo presiones de agua escalonadas. |
| **80** | CB | Prueba SPT | STAND BY OPERATIVO | COBRABLE | Ensayo de penetración dinámica estándar por conteo de golpes en suelos. |
| **81** | CC | Prueba Shelby | STAND BY OPERATIVO | COBRABLE | Muestreo inalterado de suelos cohesivos con tubo de pared delgada. |
| **82** | CD | Pruebas Geotécnicas | STAND BY OPERATIVO | COBRABLE | Conjunto de ensayos geomecánicos de caracterización de terreno. |
| **83** | CE | Prueba de nivel freático | STAND BY OPERATIVO | COBRABLE | Medición de la profundidad del agua subterránea con sonda piezométrica. |
| **84** | CF | Ensayo Air Lift | STAND BY OPERATIVO | COBRABLE | Desarrollo y bombeo del pozo inyectando aire comprimido para generar surgencia. |
| **85** | CG | Ensayo Slug Test | STAND BY OPERATIVO | COBRABLE | Prueba hidrogeológica por variación súbita de nivel de agua en el pozo. |
| **86** | CH | Instalación de piezómetro Casagrande | STAND BY OPERATIVO | COBRABLE | Instalación de tubo de PVC ranurado con celda de filtro para monitoreo de agua. |
| **87** | CI | Instalación de piezómetro de cuerda vibrante | STAND BY OPERATIVO | COBRABLE | Colocación de sensor electrónico de presión de poros (Vibrating Wire). |
| **88** | CJ | Instalación de inclinómetro | STAND BY OPERATIVO | COBRABLE | Instalación de tubería ranurada especial para medir deformaciones y desplazamientos. |
| **89** | CK | Instalación de piezómetro multinivel | STAND BY OPERATIVO | COBRABLE | Instalación de múltiples sensores a distintas profundidades en el mismo taladro. |
| **90** | CL | Instrumentación, toma de presión de agua y caudal | STAND BY OPERATIVO | COBRABLE | Medición de presión hidrostática con manómetros y caudal de agua surgente. |
| **91** | CM | Prueba de lectura de inclinómetro | STAND BY OPERATIVO | COBRABLE | Toma de perfiles de inclinometría con sonda digital en la tubería ranurada. |
| **92** | CN | Toma de lecturas cuerda vibrante | STAND BY OPERATIVO | COBRABLE | Adquisición de datos con lector digital conectado a los sensores de cuerda vibrante. |
| **93** | CO | SBO1 | STAND BY OPERATIVO | COBRABLE | Espacio reservado para actividad operativa cobrable específica de contrato. |
| **94** | CP | SBO2 | STAND BY OPERATIVO | COBRABLE | Espacio reservado para actividad operativa cobrable específica de contrato. |
| **95** | CQ | SBO3 | STAND BY OPERATIVO | COBRABLE | Espacio reservado para actividad operativa cobrable específica de contrato. |
| **96** | CR | SBO4 | STAND BY OPERATIVO | COBRABLE | Espacio reservado para actividad operativa cobrable específica de contrato. |
| **97** | CS | SBO5 | STAND BY OPERATIVO | COBRABLE | Espacio reservado para actividad operativa cobrable específica de contrato. |
| **98** | CT | Desate de rocas | STAND BY INOPERATIVO | NO COBRABLE | Purga manual de rocas sueltas en corona y paredes de la labor con barretillas. |
| **99** | CU | Orden y limpieza | STAND BY INOPERATIVO | NO COBRABLE | Acondicionamiento, limpieza y aplicación de 5S en la plataforma de trabajo. |
| **100** | CV | Recojo de lama | STAND BY INOPERATIVO | NO COBRABLE | Extracción y limpieza de detritos y lodos acumulados en piso o canaletas. |
| **101** | CW | Poza de sedimentación | STAND BY INOPERATIVO | NO COBRABLE | Limpieza, dragado y adecuación de las pozas de decantación de lodos. |
| **102** | CX | Estandarización y Desestandarización | STAND BY INOPERATIVO | NO COBRABLE | Montaje y desmontaje de entablados, bandejas ambientales y geomembranas. |
| **103** | CY | Instalación de red de agua o drenaje | STAND BY INOPERATIVO | NO COBRABLE | Tendido de mangueras y bombas sumergibles internas de Rockdrill. |
| **104** | CZ | Instalación / Desinstalación de maquina | STAND BY INOPERATIVO | NO COBRABLE | Armado del mástil, tableros eléctricos y conexiones de la perforadora. |
| **105** | DA | Traslado de accesorios | STAND BY INOPERATIVO | NO COBRABLE | Acarreo interno de cajas de testigos, tuberías y materiales hacia la plataforma. |
| **106** | DB | Auditoría Interna | STAND BY INOPERATIVO | NO COBRABLE | Inspección de seguridad o control operacional del equipo HSEQ / Residencia RD. |
| **107** | DC | Charla, reparto de guardia, llenado de herramientas y reportes | STAND BY INOPERATIVO | NO COBRABLE | Charla de seguridad de 5 min, llenado de IPERC Continuo, PETS y relevo. |
| **108** | DD | Espera de repuestos mecánicos | STAND BY INOPERATIVO | NO COBRABLE | Demora por piezas mecánicas/eléctricas a cargo del taller de mantenimiento RD. |
| **109** | DE | Espera de materiales e insumos de perforación | STAND BY INOPERATIVO | NO COBRABLE | Demora por entrega de brocas, tubos o aditivos a cargo de logística interna RD. |
| **110** | DF | Traslado de personal | STAND BY INOPERATIVO | NO COBRABLE | Tiempo de viaje de la cuadrilla desde campamento o bocamina hasta la labor. |
| **111** | DG | Refrigerio | STAND BY INOPERATIVO | NO COBRABLE | Tiempo reglamentario de alimentación de la cuadrilla (almuerzo / cena). |
| **112** | DH | Falta de personal | STAND BY INOPERATIVO | NO COBRABLE | Cuadrilla incompleta por ausentismo, descansos médicos o falta de relevo. |
| **113** | DI | Paralización por fiestas | STAND BY INOPERATIVO | NO COBRABLE | Parada acordada por festividades oficiales (Fiestas Patrias, Navidad, Año Nuevo). |
| **114** | DJ | Pare RD/ seguridad | STAND BY INOPERATIVO | NO COBRABLE | Detención preventiva ordenada por supervisión Rockdrill ante condición de riesgo. |
| **115** | DK | SBI1 | STAND BY INOPERATIVO | NO COBRABLE | Espacio reservado para parada interna no cobrable específica del contrato. |
| **116** | DL | SBI2 | STAND BY INOPERATIVO | NO COBRABLE | Espacio reservado para parada interna no cobrable específica del contrato. |
| **117** | DM | SBI3 | STAND BY INOPERATIVO | NO COBRABLE | Espacio reservado para parada interna no cobrable específica del contrato. |
| **118** | DN | SBI4 | STAND BY INOPERATIVO | NO COBRABLE | Espacio reservado para parada interna no cobrable específica del contrato. |
| **119** | DO | Voladura | STAND BY CLIENTE | COBRABLE | Horario de chispeo/disparo en mina y tiempo obligatorio de evacuación. |
| **120** | DP | Falta de agua | STAND BY CLIENTE | COBRABLE | Corte o baja presión en la red de agua industrial suministrada por la mina. |
| **121** | DQ | Falta de energía | STAND BY CLIENTE | COBRABLE | Corte de fluido eléctrico en subestación mina o mantenimiento de líneas del cliente. |
| **122** | DR | Falta de ventilación | STAND BY CLIENTE | COBRABLE | Ventilador apagado, manga rota o gases tóxicos (CO, CO2) por encima de LMP. |
| **123** | DS | Falta de servicios | STAND BY CLIENTE | COBRABLE | Corte de aire comprimido industrial de mina para bombas Wilden y winches. |
| **124** | DT | Espera Orden Cliente | STAND BY CLIENTE | COBRABLE | Máquina lista parada esperando instrucción geológica o autorización del cliente. |
| **125** | DU | Espera de programa | STAND BY CLIENTE | COBRABLE | Demora en la entrega o modificación del plan de perforación por Geología mina. |
| **126** | DV | Espera de cámara | STAND BY CLIENTE | COBRABLE | Retraso en la entrega física de la labor por labores de minado del cliente. |
| **127** | DW | Espera de sostenimiento | STAND BY CLIENTE | COBRABLE | Parada por estallido de roca o espera de pernos/shotcrete por geomecánica mina. |
| **128** | DX | Espera de scoop | STAND BY CLIENTE | COBRABLE | Demora por limpieza de marina o tránsito de equipo pesado en la cámara. |
| **129** | DY | Espera de marcado de punto | STAND BY CLIENTE | COBRABLE | Demora en la entrega formal de coordenadas y collar del taladro en terreno. |
| **130** | DZ | Espera de Topografía | STAND BY CLIENTE | COBRABLE | Espera del topógrafo de mina para alineación láser de la máquina y azimut. |
| **131** | EA | Espera de grúa | STAND BY CLIENTE | COBRABLE | Falta de disponibilidad del camión grúa o equipo de izaje provisto por la mina. |
| **132** | EB | Espera por puebas de permeabilidad y/o ensayos | STAND BY CLIENTE | COBRABLE | Máquina en espera del especialista o geólogo del cliente para iniciar pruebas. |
| **133** | EC | Auditoría externa/ Osinergmin | STAND BY CLIENTE | COBRABLE | Inspección de fiscalizadores del Estado (Osinergmin, Sunafil) o gerencia cliente. |
| **134** | ED | Capacitación (Externa Cliente) | STAND BY CLIENTE | COBRABLE | Cursos o talleres de inducción y seguridad obligatorios dictados por la mina. |
| **135** | EE | Falta de habilitación de cámara o plataforma | STAND BY CLIENTE | COBRABLE | Rampa bloqueada por desmonte, deslizamientos o accesos sin pase hacia la labor. |
| **136** | EF | Espera de orden cliente | STAND BY CLIENTE | COBRABLE | Parada a la espera de confirmación de fin de pozo o cambio de objetivo. |
| **137** | EG | Condiciones climáticas | STAND BY CLIENTE | COBRABLE | Paralización por tormenta eléctrica (Alerta Roja), nevada, granizo o lluvia torrencial. |
| **138** | EH | Inundación | STAND BY CLIENTE | COBRABLE | Aniego de la cámara por colapso o falla en el sistema de bombeo principal de la mina. |
| **139** | EI | Paralización por estrés térmico o alta temperatura | STAND BY CLIENTE | COBRABLE | Exceso de calor/humedad en labor subterránea sobre los límites permitidos. |
| **140** | EJ | Parada por sismo/microsismo | STAND BY CLIENTE | COBRABLE | Evacuación de emergencia ordenada por el Centro de Control de Operaciones (OCP). |
| **141** | EK | Conflicto social | STAND BY CLIENTE | COBRABLE | Bloqueo de accesos, paro comunal o huelga de terceros externa a Rockdrill. |
| **142** | EL | SBC1 | STAND BY CLIENTE | COBRABLE | Espacio reservado para parada imputable al cliente específica de contrato. |
| **143** | EM | SBC2 | STAND BY CLIENTE | COBRABLE | Espacio reservado para parada imputable al cliente específica de contrato. |
| **144** | EN | SBC3 | STAND BY CLIENTE | COBRABLE | Espacio reservado para parada imputable al cliente específica de contrato. |
| **145** | EO | SBC4 | STAND BY CLIENTE | COBRABLE | Espacio reservado para parada imputable al cliente específica de contrato. |
| **146** | EP | TIEMPO TOTAL | RESUMEN DE HORAS | TOTAL HORAS | Suma total de horas de la guardia (debe sumar exactamente 12.0 horas). |
| **147** | EQ | TIEMPO EFECTIVO - OPERATIVO | RESUMEN DE HORAS | TOTAL HORAS | Horas netas dedicadas a perforación, rimado, casing y reperforación. |
| **148** | ER | LOST TIME | RESUMEN DE HORAS | TOTAL HORAS | Suma de horas no productivas (Mantenimiento + Stand Bys). |
| **149** | ES | Mantenimiento | RESUMEN DE HORAS | TOTAL HORAS | Subtotal de horas de mantenimiento (Preventivo + Correctivo). |
| **150** | ET | Stand By Operativo | RESUMEN DE HORAS | TOTAL HORAS | Subtotal de horas de Stand By Operativo cobrables. |
| **151** | EU | Stand By Inoperativo | RESUMEN DE HORAS | TOTAL HORAS | Subtotal de horas de Stand By Inoperativo no cobrables. |
| **152** | EV | Stand By Cliente | RESUMEN DE HORAS | TOTAL HORAS | Subtotal de horas de Stand By Cliente cobrables. |
| **153** | EW | DESDE | RIMADO CON CASING HWT/HQ | METRAJE | Profundidad inicial del tramo revestido con tubería pesada HWT/HQ. |
| **154** | EX | HASTA | RIMADO CON CASING HWT/HQ | METRAJE | Profundidad final del tramo revestido. |
| **155** | EY | METRAJE | RIMADO CON CASING HWT/HQ | METRAJE | Metros lineales de tubería casing instalados en la guardia. |
| **156** | EZ | TOTAL | RIMADO CON CASING HWT/HQ | METRAJE | Total acumulado de entubado casing en el sondaje. |
| **157** | FA | DESDE | RE-PERFORACIÓN | METRAJE | Profundidad inicial del tramo reperforado por colapso. |
| **158** | FB | HASTA | RE-PERFORACIÓN | METRAJE | Profundidad final del tramo reperforado. |
| **159** | FC | METRAJE | RE-PERFORACIÓN | METRAJE | Metros lineales reperforados en la guardia. |
| **160** | FD | TOTAL | RE-PERFORACIÓN | METRAJE | Total acumulado de metros reperforados en el sondaje. |
| **161** | FE | DESDE | HOROMETRO | HORAS MOTOR | Lectura del horómetro del motor al iniciar el turno. |
| **162** | FF | HASTA | HOROMETRO | HORAS MOTOR | Lectura del horómetro del motor al culminar el turno. |
| **163** | FG | ACUMULADO | HOROMETRO | HORAS MOTOR | Horas de motor acumuladas en el mes. |
| **164** | FH | TOTAL | HOROMETRO | HORAS MOTOR | Horas de motor trabajadas en la guardia (Hasta - Desde). |
| **165** | FI | TRABAJOS REALIZADOS | BITACORA DE MANTENIMIENTO | DATO | Descripción detallada de tareas mecánicas ejecutadas en el equipo. |
| **166** | FJ | REPUESTOS UTILIZADOS | BITACORA DE MANTENIMIENTO | DATO | Lista de repuestos, filtros o mangueras cambiadas durante el turno. |
| **167** | FK | DESCRIPCIÓN LITOLÓGICA | OBSERVACIONES | DATO | Resumen de las características de la roca cortada (tipo de roca, vetillas). |
| **168** | FL | COMENTARIOS | OBSERVACIONES | DATO | Observaciones generales de la guardia, coordinaciones e incidencias de campo. |
