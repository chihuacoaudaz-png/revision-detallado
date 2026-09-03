-- ==============================================================================
-- ROCKDRILL GROUP - ENTERPRISE DATA WAREHOUSE & ANALYTICS PLATFORM
-- ARCHITECTURE: Kimball Dimensional Model (Star / Snowflake Schema)
-- COMPLIANCE: ANSI SQL (PostgreSQL / Snowflake / Microsoft Fabric / Azure SQL)
-- PATH: C:/Proyectos Python/Detallados/sql/01_schema_ddl_enterprise.sql
-- VERSION: 3.1.0 (Refined with Field Resiliency, Reperforations & Anomaly Auditing)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DIMENSION TABLES (WITH UNKNOWN/MISSING MEMBER SUPPORT: SK = -1)
-- ------------------------------------------------------------------------------

-- Dimensión Tiempo / Calendario (Civil & Ciclo Minero 26 al 25)
CREATE TABLE dim_tiempo_calendario (
    calendario_sk           INT NOT NULL PRIMARY KEY,            -- YYYYMMDD (ej. 20260828) o -1 para No Definido
    fecha_dt                DATE NOT NULL UNIQUE,
    anio_civil              SMALLINT NOT NULL,
    mes_num_civil           SMALLINT NOT NULL,
    mes_nom_civil           VARCHAR(20) NOT NULL,
    dia_mes                 SMALLINT NOT NULL,
    dia_semana_num          SMALLINT NOT NULL,                   -- 1=Lunes, 7=Domingo
    dia_semana_nom          VARCHAR(20) NOT NULL,
    es_fin_semana           BOOLEAN NOT NULL,
    trimestre_civil         VARCHAR(5) NOT NULL,
    -- Atributos Operativos Mineros (Regla del Día 26 al 25)
    anio_operativo          SMALLINT NOT NULL,
    mes_num_operativo       SMALLINT NOT NULL,
    mes_nom_operativo       VARCHAR(20) NOT NULL,
    mes_anio_operativo      VARCHAR(10) NOT NULL,                -- 'ENE-26'
    periodo_operativo_sort  INT NOT NULL,                        -- YYYYMM (202601)
    dia_ciclo_operativo     SMALLINT NOT NULL,
    es_cierre_operativo     BOOLEAN NOT NULL,
    -- Atributos de Visualización y Ordenamiento Cronológico Minero (SortByColumn)
    fecha_corta_label       VARCHAR(10) NOT NULL,                -- '26-Ago', '01-Set' (SortBy: calendario_sk)
    dia_ciclo_label         VARCHAR(25) NOT NULL,                -- 'Día 01 (26-Ago)' (SortBy: dia_ciclo_operativo)
    fecha_operativa_dt      DATE NOT NULL,                       -- Tipo DATE nativo para series de tiempo
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Contrato Minero (CTRs)
CREATE TABLE dim_contrato_minero (
    contrato_sk             SMALLINT NOT NULL PRIMARY KEY,       -- -1 para CTR No Asignado
    contrato_cd             VARCHAR(30) NOT NULL UNIQUE,         -- 'COLQUIJIRCA', 'RAURA'
    nombre_contrato         VARCHAR(100) NOT NULL,
    nombre_contrato_corto   VARCHAR(50) NOT NULL,                -- 'Catalina Huanca', 'Cobriza' (limpio sin prefijos)
    cliente_minero          VARCHAR(100) NOT NULL,
    grupo_empresarial       VARCHAR(60),
    zona_geografica         VARCHAR(20) NOT NULL,                -- 'CENTRO', 'SUR', 'NORTE'
    tipo_operacion          VARCHAR(30) NOT NULL,                -- 'SUBTERRANEA', 'SUPERFICIE', 'MIXTA'
    altitud_msnm            INT,
    moneda_contractual      VARCHAR(5) DEFAULT 'USD',
    estado_vigencia         VARCHAR(15) DEFAULT 'ACTIVO',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Equipos y Máquinas Perforadoras
CREATE TABLE dim_equipo_perforadora (
    equipo_sk               SMALLINT NOT NULL PRIMARY KEY,       -- -1 para Equipo No Asignado
    equipo_cd               VARCHAR(40) NOT NULL UNIQUE,
    codigo_sap              VARCHAR(30) NOT NULL,
    modelo_fabricante       VARCHAR(60) NOT NULL,
    fabricante              VARCHAR(60) DEFAULT 'ROCKDRILL',
    tipo_energia            VARCHAR(30) NOT NULL,                -- 'DIESEL', 'ELECTRO-HIDRAULICA'
    tipo_aplicacion         VARCHAR(30) NOT NULL,
    capacidad_prof_hq_m     INT,
    horas_dia_planeadas     SMALLINT DEFAULT 24 NOT NULL,
    contrato_sk_asignado    SMALLINT REFERENCES dim_contrato_minero(contrato_sk),
    estado_operativo        VARCHAR(20) DEFAULT 'OPERATIVO',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Línea y Diámetro de Perforación
CREATE TABLE dim_linea_diametro (
    linea_sk                SMALLINT NOT NULL PRIMARY KEY,       -- -1 para Diámetro Desconocido
    linea_cd                VARCHAR(15) NOT NULL UNIQUE,         -- 'HQ', 'NQ', 'BQ', 'PQ', 'HWT'
    tipo_tuberia            VARCHAR(30) NOT NULL,
    diametro_corona_mm      DECIMAL(6,2),
    diametro_testigo_mm     DECIMAL(6,2),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Personal y Cuadrillas
CREATE TABLE dim_personal (
    personal_sk             INT NOT NULL PRIMARY KEY,            -- -1 para Personal No Asignado / Faltante
    personal_cd             VARCHAR(30) NOT NULL UNIQUE,         -- DNI o Código
    dni_carnet              VARCHAR(20),
    nombre_completo         VARCHAR(120) NOT NULL,
    rol_estandarizado       VARCHAR(40) NOT NULL,                -- 'PERFORISTA', 'AYUDANTE 1', 'AYUDANTE 2'
    contratista_propio      VARCHAR(20) DEFAULT 'ROCKDRILL',
    estado_personal         VARCHAR(15) DEFAULT 'ACTIVO',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Sondajes y Taladros Mineros (Soporte para Reperforaciones y Ramales Paralelos)
CREATE TABLE dim_sondaje_taladro (
    sondaje_sk              INT NOT NULL PRIMARY KEY,            -- -1 para Sondaje No Asignado
    sondaje_cd              VARCHAR(60) NOT NULL,                -- 'CND-24-015', 'CND-24-015A'
    contrato_sk             SMALLINT NOT NULL REFERENCES dim_contrato_minero(contrato_sk),
    sondaje_padre_sk        INT REFERENCES dim_sondaje_taladro(sondaje_sk), -- Autorreferencia para ramales
    tipo_taladro            VARCHAR(30) DEFAULT 'ORIGINAL',      -- 'ORIGINAL', 'REPERFORACION', 'RAMAL_PARALELO', 'PILOTO'
    profundidad_programada_m DECIMAL(8,2) NOT NULL,
    linea_sk_collar         SMALLINT REFERENCES dim_linea_diametro(linea_sk),
    inclinacion_grados      DECIMAL(5,2) NOT NULL,
    azimut_grados           DECIMAL(5,2),
    coordenada_este         DECIMAL(12,3),
    coordenada_norte        DECIMAL(12,3),
    cota_collar_msnm        DECIMAL(8,2),
    estado_sondaje          VARCHAR(20) DEFAULT 'EN EJECUCION',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Taxonomía de Actividades y Disponibilidad (17 Bloques / 5 Categorías)
CREATE TABLE dim_taxonomia_actividad (
    actividad_sk            SMALLINT NOT NULL PRIMARY KEY,       -- -1 para Actividad No Catalogada
    actividad_cd            VARCHAR(30) NOT NULL UNIQUE,
    nombre_actividad        VARCHAR(100) NOT NULL,
    bloque_funcional        VARCHAR(60) NOT NULL,
    categoria_disponibilidad VARCHAR(40) NOT NULL,
    es_cobrable             BOOLEAN NOT NULL,
    impacta_disp_mecanica   BOOLEAN NOT NULL,
    impacta_disp_operativa  BOOLEAN NOT NULL,
    departamento_responsable VARCHAR(60) NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensión Catálogo de Insumos (Preparada para Futura Expansión)
CREATE TABLE dim_catalogo_insumo (
    insumo_sk               INT NOT NULL PRIMARY KEY,            -- -1 para Insumo No Asignado
    insumo_cd               VARCHAR(40) NOT NULL UNIQUE,
    descripcion_insumo      VARCHAR(120) NOT NULL,
    familia_insumo          VARCHAR(50) NOT NULL,
    unidad_medida_estandar  VARCHAR(15) NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------------------------
-- 2. FACT TABLES (CORE DRILLING OPERATIONS WITH REPERFORATION & ANOMALY FLAGS)
-- ------------------------------------------------------------------------------

-- Fact 1: Avance Físico de Perforación
-- Granularidad: 1 fila por evento/pase de perforación por guardia por máquina por taladro
CREATE TABLE fact_perforacion_avance (
    avance_id               BIGSERIAL PRIMARY KEY,
    calendario_sk           INT NOT NULL DEFAULT -1 REFERENCES dim_tiempo_calendario(calendario_sk),
    contrato_sk             SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_contrato_minero(contrato_sk),
    equipo_sk               SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_equipo_perforadora(equipo_sk),
    sondaje_sk              INT NOT NULL DEFAULT -1 REFERENCES dim_sondaje_taladro(sondaje_sk),
    linea_sk                SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_linea_diametro(linea_sk),
    perforista_sk           INT NOT NULL DEFAULT -1 REFERENCES dim_personal(personal_sk),
    turno_guardia           VARCHAR(5) NOT NULL,                 -- 'A', 'B'
    grupo_rotativo          VARCHAR(5) NOT NULL,
    -- Tipo de Pase (Manejo de Reperforaciones y Ramales)
    tipo_pase_perforacion   VARCHAR(30) DEFAULT 'AVANCE_VIRGEN', -- 'AVANCE_VIRGEN', 'REPERFORACION', 'RAMAL_PARALELO'
    es_reperforacion        BOOLEAN DEFAULT FALSE,
    -- Cotas Físicas
    desde_m                 DECIMAL(8,2) NOT NULL,
    hasta_m                 DECIMAL(8,2) NOT NULL,
    metraje_guardia_m       DECIMAL(8,2) NOT NULL,
    horas_extras_guardia    DECIMAL(4,2) DEFAULT 0.00,
    recuperacion_testigo_pct DECIMAL(5,2),
    -- Flags de Auditoría y Resiliencia en Campo
    tiene_anomalia          BOOLEAN DEFAULT FALSE,
    codigo_anomalia_campo   VARCHAR(50),                         -- 'ERR_MONOTONIA', 'ERR_PERFORISTA_VACIO'
    source_batch_id         VARCHAR(50),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact 2: Distribución Horaria de Eventos Operacionales
-- Granularidad: 1 fila por evento/actividad horaria en la guardia por máquina
CREATE TABLE fact_horas_operativas (
    hora_evento_id          BIGSERIAL PRIMARY KEY,
    calendario_sk           INT NOT NULL DEFAULT -1 REFERENCES dim_tiempo_calendario(calendario_sk),
    contrato_sk             SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_contrato_minero(contrato_sk),
    equipo_sk               SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_equipo_perforadora(equipo_sk),
    sondaje_sk              INT DEFAULT -1 REFERENCES dim_sondaje_taladro(sondaje_sk),
    actividad_sk            SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_taxonomia_actividad(actividad_sk),
    turno_guardia           VARCHAR(5) NOT NULL,
    grupo_rotativo          VARCHAR(5) NOT NULL,
    horas_reportadas        DECIMAL(5,2) NOT NULL,
    es_cobrable             BOOLEAN NOT NULL,
    categoria_disponibilidad VARCHAR(40) NOT NULL,
    bitacora_comentario     TEXT,
    -- Auditoría de Balance Horario
    tiene_desbalance_guardia BOOLEAN DEFAULT FALSE,
    codigo_anomalia_campo   VARCHAR(50),                         -- 'ERR_GUARDIA_DESBALANCE_14H'
    source_batch_id         VARCHAR(50),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact 3: Metas Mensuales
CREATE TABLE fact_metas_mensuales (
    meta_id                 SERIAL PRIMARY KEY,
    contrato_sk             SMALLINT NOT NULL REFERENCES dim_contrato_minero(contrato_sk),
    equipo_sk               SMALLINT NOT NULL REFERENCES dim_equipo_perforadora(equipo_sk),
    periodo_operativo_sort  INT NOT NULL,                        -- YYYYMM
    meta_metraje_m          DECIMAL(10,2) NOT NULL,
    horas_programadas_mes   DECIMAL(6,2) DEFAULT 720.00,
    ratio_mh_objetivo       DECIMAL(6,2),
    disp_mecanica_target_pct DECIMAL(5,2) DEFAULT 90.00,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Puente: Cuadrilla por Guardia (M:M)
CREATE TABLE brg_cuadrilla_guardia (
    asignacion_id           BIGSERIAL PRIMARY KEY,
    calendario_sk           INT NOT NULL DEFAULT -1 REFERENCES dim_tiempo_calendario(calendario_sk),
    contrato_sk             SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_contrato_minero(contrato_sk),
    equipo_sk               SMALLINT NOT NULL DEFAULT -1 REFERENCES dim_equipo_perforadora(equipo_sk),
    turno_guardia           VARCHAR(5) NOT NULL,
    personal_sk             INT NOT NULL DEFAULT -1 REFERENCES dim_personal(personal_sk),
    rol_desempenado         VARCHAR(40) NOT NULL,
    horas_laboradas         DECIMAL(4,2) DEFAULT 12.00,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------------------------
-- 3. INSERCIÓN DE MIEMBROS POR DEFECTO (-1) PARA RESILIENCIA A DATOS INCOMPLETOS
-- ------------------------------------------------------------------------------

INSERT INTO dim_tiempo_calendario (calendario_sk, fecha_dt, anio_civil, mes_num_civil, mes_nom_civil, dia_mes, dia_semana_num, dia_semana_nom, es_fin_semana, trimestre_civil, anio_operativo, mes_num_operativo, mes_nom_operativo, mes_anio_operativo, periodo_operativo_sort, dia_ciclo_operativo, es_cierre_operativo)
VALUES (-1, '1900-01-01', 1900, 1, 'SIN FECHA', 1, 1, 'NO DEFINIDO', FALSE, 'N/A', 1900, 1, 'SIN MES', 'S/M', 190001, 1, FALSE)
ON CONFLICT (calendario_sk) DO NOTHING;

INSERT INTO dim_contrato_minero (contrato_sk, contrato_cd, nombre_contrato, nombre_contrato_corto, cliente_minero, zona_geografica, tipo_operacion)
VALUES (-1, 'SIN_CTR', 'CONTRATO NO ESPECIFICADO', 'No Asignado', 'NO ASIGNADO', 'CENTRO', 'DESCONOCIDO')
ON CONFLICT (contrato_sk) DO NOTHING;

INSERT INTO dim_equipo_perforadora (equipo_sk, equipo_cd, codigo_sap, modelo_fabricante, tipo_energia, tipo_aplicacion, contrato_sk_asignado)
VALUES (-1, 'SIN_EQUIPO', 'SAP-PENDIENTE', 'EQUIPO NO DEFINIDO', 'DIESEL', 'SUPERFICIE', -1)
ON CONFLICT (equipo_sk) DO NOTHING;

INSERT INTO dim_linea_diametro (linea_sk, linea_cd, tipo_tuberia)
VALUES (-1, 'S/D', 'DIAMETRO NO ESPECIFICADO')
ON CONFLICT (linea_sk) DO NOTHING;

INSERT INTO dim_personal (personal_sk, personal_cd, nombre_completo, rol_estandarizado)
VALUES (-1, 'SIN_PERSONAL', '[NO ESPECIFICADO / PERSONAL PENDIENTE]', 'PERFORISTA')
ON CONFLICT (personal_sk) DO NOTHING;

INSERT INTO dim_sondaje_taladro (sondaje_sk, sondaje_cd, contrato_sk, profundidad_programada_m, inclinacion_grados)
VALUES (-1, 'SIN_SONDAJE', -1, 100.0, -90.0)
ON CONFLICT (sondaje_sk) DO NOTHING;

INSERT INTO dim_taxonomia_actividad (actividad_sk, actividad_cd, nombre_actividad, bloque_funcional, categoria_disponibilidad, es_cobrable, impacta_disp_mecanica, impacta_disp_operativa, departamento_responsable)
VALUES (-1, 'ACT_NO_CAT', '[ACTIVIDAD NO CATALOGADA EN DETALLADO]', 'OTROS_POR_RECTIFICAR', 'STANDBY_INOPERATIVO_NO_COBRABLE', FALSE, FALSE, TRUE, 'OPERACIONES')
ON CONFLICT (actividad_sk) DO NOTHING;

INSERT INTO dim_catalogo_insumo (insumo_sk, insumo_cd, descripcion_insumo, familia_insumo, unidad_medida_estandar)
VALUES (-1, 'SIN_INSUMO', '[INSUMO NO ESPECIFICADO]', 'PENDIENTE', 'UND')
ON CONFLICT (insumo_sk) DO NOTHING;
