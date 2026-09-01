# 📖 Diccionario de Datos del Modelo Tabular

> [!NOTE]
> Este documento detalla la estructura física, granularidad, columnas, tipos de datos y significado de negocio de las **13 tablas** del modelo de datos de `RESIDENTES.pbix`.

---

## 📊 Resumen de Tablas del Modelo

| Tabla | Tipo | Filas Aprox. | Columnas | Descripción del Negocio |
| :--- | :--- | :---: | :---: | :--- |
| **`Fact_Metraje`** | Hechos | 62,514 | 17 | Registros de avance físico de perforación por guardia. |
| **`Fact_Tiempos`** | Hechos | 384,758 | 21 | Registro transaccional de horas consumidas por actividad y categoría. |
| **`Fact_Abastecimiento`** | Hechos | 122,616 | 15 | Registros de compras, despachos y guías de almacén. |
| **`Consumo Consolidado`**| Hechos | 424,687 | 20 | Salidas de almacén reales de consumibles, brocas y aditivos. |
| **`Fact_Metas`** | Hechos | 988 | 5 | Metas mensuales programadas de metraje por máquina y CTR. |
| **`Fact_Personal_Asignado`**| Puente / Hechos | 176,439 | 3 | Asignación de trabajadores (perforistas/ayudantes) por operación. |
| **`Reporte_Brocas`** | Hechos / Detalle| 5,002 | 17 | Registro de vida útil, desgaste y rendimiento por serie de broca. |
| **`Dim_Calendario`** | Dimensión | 1,096 | 9 | Calendario operativo con cortes del 26 al 25 y semanas operativas. |
| **`Dim_CTR`** | Dimensión | 21 | 5 | Catálogo de Contratos / Centros de Costos, coordinadores y precios. |
| **`Dim_Maquina`** | Dimensión | 78 | 1 | Catálogo maestro de equipos de perforación. |
| **`Dim_Personal`** | Dimensión | 2,187 | 2 | Catálogo maestro de perforistas y ayudantes. |
| **`Dim_Sondaje`** | Dimensión | 4,460 | 8 | Catálogo de sondajes, profundidad programada y fechas reales. |
| **`Dim_Familias`** | Dimensión | 12 | 3 | Catálogo de familias de insumos y sus pesos presupuestales. |

---

### 🗃️ Tabla: `Consumo Consolidado`
* **Registros:** 424,687 filas
* **Columnas:** 20

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 2 | `GS` | Texto | Campo de dimensión/hecho |
| 3 | `Fecha` | Fecha / Datetime | Marca temporal del registro operativo. |
| 4 | `Maquina` | Texto | Código identificador de la máquina perforadora. |
| 5 | `Codigo` | Texto | Campo de dimensión/hecho |
| 6 | `Descripcion` | Texto | Campo de dimensión/hecho |
| 7 | `Serie` | Texto | Número de serie o código de la broca diamantina. |
| 8 | `Cant` | Entero / Decimal | Cantidad de unidades físicas consumidas o despachadas. |
| 9 | `UM` | Texto | Campo de dimensión/hecho |
| 10 | `Familia` | Texto | Campo de dimensión/hecho |
| 11 | `Costo` | Moneda / Decimal | Importe monetario en dólares ($). |
| 12 | `Total` | Moneda / Decimal | Importe monetario en dólares ($). |
| 13 | `ACTIVOS` | Texto | Campo de dimensión/hecho |
| 14 | `Item` | Texto | Campo de dimensión/hecho |
| 15 | `MARCA` | Texto | Campo de dimensión/hecho |
| 16 | `TIPO` | Texto | Campo de dimensión/hecho |
| 17 | `DESCARGA` | Texto | Campo de dimensión/hecho |
| 18 | `ALTURA_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 19 | `MODELO` | Texto | Campo de dimensión/hecho |
| 20 | `LINEA` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Dim_CTR`
* **Registros:** 21 filas
* **Columnas:** 5

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 2 | `COORDINADOR` | Texto | Campo de dimensión/hecho |
| 3 | `Costo por metro` | Decimal (Float) | Metros perforados registrados en la guardia. |
| 4 | `ZONA` | Texto | Campo de dimensión/hecho |
| 5 | `P.U. PROMEDIO` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Dim_Calendario`
* **Registros:** 1,096 filas
* **Columnas:** 9

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `Date` | Fecha / Datetime | Marca temporal del registro operativo. |
| 2 | `Año Operativo` | Texto | Campo de dimensión/hecho |
| 3 | `Mes Num Operativo` | Texto | Campo de dimensión/hecho |
| 4 | `Mes Operativo` | Texto | Campo de dimensión/hecho |
| 5 | `Mes Año` | Texto | Campo de dimensión/hecho |
| 6 | `Periodo Sort` | Texto | Campo de dimensión/hecho |
| 7 | `Semana Num` | Texto | Campo de dimensión/hecho |
| 8 | `Semana` | Texto | Campo de dimensión/hecho |
| 9 | `Semana Operativa` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Dim_Familias`
* **Registros:** 12 filas
* **Columnas:** 3

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `ID_FAMILIA` | Texto | Campo de dimensión/hecho |
| 2 | `FAMILIA` | Texto | Campo de dimensión/hecho |
| 3 | `%` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Dim_Maquina`
* **Registros:** 78 filas
* **Columnas:** 1

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `MAQUINA` | Texto | Código identificador de la máquina perforadora. |

### 🗃️ Tabla: `Dim_Personal`
* **Registros:** 2,187 filas
* **Columnas:** 2

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `PERFORISTA` | Texto | Nombre completo normalizado del personal operativo. |
| 2 | `PUESTO` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Dim_Sondaje`
* **Registros:** 4,460 filas
* **Columnas:** 8

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `SONDAJE` | Texto | Campo de dimensión/hecho |
| 2 | `FECHA_INICIO_REAL` | Fecha / Datetime | Marca temporal del registro operativo. |
| 3 | `FECHA_FIN_REAL` | Fecha / Datetime | Marca temporal del registro operativo. |
| 4 | `AVANCE_ACUMULADO` | Decimal (Float) | Metros perforados registrados en la guardia. |
| 5 | `MAQUINA_PRINCIPAL` | Texto | Código identificador de la máquina perforadora. |
| 6 | `CTR_A_CARGO` | Texto | Centro de trabajo o contrato minero. |
| 7 | `PROFUNDIDAD_PROGRAMADA` | Texto | Campo de dimensión/hecho |
| 8 | `Etiqueta_Gantt` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Fact_Abastecimiento`
* **Registros:** 122,616 filas
* **Columnas:** 15

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `MES` | Texto | Campo de dimensión/hecho |
| 2 | `FECHA` | Fecha / Datetime | Marca temporal del registro operativo. |
| 3 | `CONTRATO` | Texto | Campo de dimensión/hecho |
| 4 | `TRA` | Texto | Campo de dimensión/hecho |
| 5 | `DESCRIPCION` | Texto | Campo de dimensión/hecho |
| 6 | `UND` | Texto | Campo de dimensión/hecho |
| 7 | `CANT` | Entero / Decimal | Cantidad de unidades físicas consumidas o despachadas. |
| 8 | `PRECIO` | Moneda / Decimal | Importe monetario en dólares ($). |
| 9 | `TOTAL` | Moneda / Decimal | Importe monetario en dólares ($). |
| 10 | `FAMILIA` | Texto | Campo de dimensión/hecho |
| 11 | `TIPO` | Texto | Campo de dimensión/hecho |
| 12 | `C.COSTO` | Moneda / Decimal | Importe monetario en dólares ($). |
| 13 | `CODTRA` | Texto | Campo de dimensión/hecho |
| 14 | `GUIA` | Texto | Campo de dimensión/hecho |
| 15 | `cod` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Fact_Metas`
* **Registros:** 988 filas
* **Columnas:** 5

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 2 | `MES OPERATIVO` | Texto | Campo de dimensión/hecho |
| 3 | `META METRAJE` | Decimal (Float) | Metros perforados registrados en la guardia. |
| 4 | `MAQUINA` | Texto | Código identificador de la máquina perforadora. |
| 5 | `TIPO_MAQUINA` | Texto | Código identificador de la máquina perforadora. |

### 🗃️ Tabla: `Fact_Metraje`
* **Registros:** 62,514 filas
* **Columnas:** 17

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `KEY_OPERACION` | Texto (Clave) | Llave primaria / foránea de correlación relacional. |
| 2 | `FECHA` | Fecha / Datetime | Marca temporal del registro operativo. |
| 3 | `MAQUINA` | Texto | Código identificador de la máquina perforadora. |
| 4 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 5 | `TURNO` | Texto | Turno de trabajo (Día / Noche). |
| 6 | `SONDAJE` | Texto | Campo de dimensión/hecho |
| 7 | `PERFORISTA` | Texto | Nombre completo normalizado del personal operativo. |
| 8 | `LINEA` | Texto | Campo de dimensión/hecho |
| 9 | `AÑO` | Texto | Campo de dimensión/hecho |
| 10 | `GUARDIAS` | Texto | Campo de dimensión/hecho |
| 11 | `METRAJE_X_GUARDIA` | Decimal (Float) | Metros perforados registrados en la guardia. |
| 12 | `Nº_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 13 | `SERIE_DE_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 14 | `AYUDANTE_1` | Texto | Nombre completo normalizado del personal operativo. |
| 15 | `AYUDANTE_2` | Texto | Nombre completo normalizado del personal operativo. |
| 16 | `MARCA_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 17 | `COMENTARIOS` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Fact_Personal_Asignado`
* **Registros:** 176,439 filas
* **Columnas:** 3

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `KEY_OPERACION` | Texto (Clave) | Llave primaria / foránea de correlación relacional. |
| 2 | `ROL_EN_REPORTE` | Texto | Campo de dimensión/hecho |
| 3 | `NOMBRE_TRABAJADOR` | Texto | Nombre completo normalizado del personal operativo. |

### 🗃️ Tabla: `Fact_Tiempos`
* **Registros:** 384,758 filas
* **Columnas:** 21

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `KEY_OPERACION` | Texto (Clave) | Llave primaria / foránea de correlación relacional. |
| 2 | `FECHA` | Fecha / Datetime | Marca temporal del registro operativo. |
| 3 | `MAQUINA` | Texto | Código identificador de la máquina perforadora. |
| 4 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 5 | `TURNO` | Texto | Turno de trabajo (Día / Noche). |
| 6 | `SONDAJE` | Texto | Campo de dimensión/hecho |
| 7 | `PERFORISTA` | Texto | Nombre completo normalizado del personal operativo. |
| 8 | `LINEA` | Texto | Campo de dimensión/hecho |
| 9 | `AÑO` | Texto | Campo de dimensión/hecho |
| 10 | `GUARDIAS` | Texto | Campo de dimensión/hecho |
| 11 | `Actividad` | Texto | Campo de dimensión/hecho |
| 12 | `Horas` | Decimal (Float) | Cantidad de horas dedicadas a la actividad. |
| 13 | `Categoria` | Texto | Campo de dimensión/hecho |
| 14 | `Afecta_Disp` | Texto | Campo de dimensión/hecho |
| 15 | `Responsable` | Texto | Campo de dimensión/hecho |
| 16 | `Tipo_Movimiento` | Texto | Campo de dimensión/hecho |
| 17 | `JOIN_KEY_EXCEL` | Texto (Clave) | Llave primaria / foránea de correlación relacional. |
| 18 | `AYUDANTE_1` | Texto | Nombre completo normalizado del personal operativo. |
| 19 | `AYUDANTE_2` | Texto | Nombre completo normalizado del personal operativo. |
| 20 | `MARCA_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 21 | `COMENTARIOS` | Texto | Campo de dimensión/hecho |

### 🗃️ Tabla: `Reporte_Brocas`
* **Registros:** 5,002 filas
* **Columnas:** 17

| # | Nombre de Columna | Tipo Inferido | Descripción y Uso de Negocio |
| :-: | :--- | :---: | :--- |
| 1 | `KEY_OPERACION` | Texto (Clave) | Llave primaria / foránea de correlación relacional. |
| 2 | `FECHA` | Fecha / Datetime | Marca temporal del registro operativo. |
| 3 | `MAQUINA` | Texto | Código identificador de la máquina perforadora. |
| 4 | `CTR` | Texto | Centro de trabajo o contrato minero. |
| 5 | `TURNO` | Texto | Turno de trabajo (Día / Noche). |
| 6 | `SONDAJE` | Texto | Campo de dimensión/hecho |
| 7 | `PERFORISTA` | Texto | Nombre completo normalizado del personal operativo. |
| 8 | `LINEA` | Texto | Campo de dimensión/hecho |
| 9 | `AÑO` | Texto | Campo de dimensión/hecho |
| 10 | `GUARDIAS` | Texto | Campo de dimensión/hecho |
| 11 | `MARCA_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 12 | `SERIE_DE_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 13 | `Nº_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 14 | `ESTADO_DE_LA_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 15 | `CAMBIO_BROCA` | Texto | Número de serie o código de la broca diamantina. |
| 16 | `AYUDANTE` | Texto | Nombre completo normalizado del personal operativo. |
| 17 | `DESCRIPCION_LITOLOGICA` | Texto | Campo de dimensión/hecho |
