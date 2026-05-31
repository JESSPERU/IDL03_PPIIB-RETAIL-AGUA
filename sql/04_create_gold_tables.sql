-- ============================================================
-- 04_create_gold_tables.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Crear capa Gold alineada a Silver real
-- ============================================================

CREATE SCHEMA IF NOT EXISTS gold;

DROP TABLE IF EXISTS gold.ml_feature_importance CASCADE;
DROP TABLE IF EXISTS gold.ml_score_output CASCADE;
DROP TABLE IF EXISTS gold.ml_score_input CASCADE;
DROP TABLE IF EXISTS gold.ml_dataset CASCADE;
DROP TABLE IF EXISTS gold.fact_marketing CASCADE;
DROP TABLE IF EXISTS gold.fact_inventario CASCADE;
DROP TABLE IF EXISTS gold.fact_ventas_diarias CASCADE;
DROP TABLE IF EXISTS gold.dim_tiempo CASCADE;
DROP TABLE IF EXISTS gold.dim_producto CASCADE;

CREATE TABLE gold.dim_producto (
    id_sku TEXT PRIMARY KEY,
    descripcion TEXT,
    categoria TEXT,
    volumen_litros NUMERIC(10,2),
    unidad_medida TEXT,
    formato_envase TEXT,
    costo_unitario_base NUMERIC(12,2),
    precio_lista NUMERIC(12,2),
    stock_seguridad INTEGER,
    lead_time_dias INTEGER,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE gold.dim_tiempo (
    fecha DATE PRIMARY KEY,
    anio INTEGER,
    mes INTEGER,
    trimestre INTEGER,
    numero_dia_semana INTEGER,
    nombre_dia TEXT,
    es_fin_de_semana BOOLEAN,
    es_feriado BOOLEAN,
    nombre_feriado TEXT,
    es_quincena BOOLEAN,
    es_fin_mes BOOLEAN,
    temporada TEXT,
    temperatura_promedio_celsius NUMERIC(10,2),
    temperatura_maxima_celsius NUMERIC(10,2),
    temperatura_minima_celsius NUMERIC(10,2),
    humedad_porcentaje NUMERIC(10,2),
    precipitacion_mm NUMERIC(10,2),
    alerta_ola_calor BOOLEAN,
    fuente_clima TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE gold.fact_ventas_diarias (
    fecha DATE NOT NULL,
    id_sku TEXT NOT NULL,
    id_canal TEXT NOT NULL,
    id_campana TEXT NOT NULL,
    cantidad_vendida_total INTEGER,
    venta_total NUMERIC(14,2),
    precio_unitario_promedio NUMERIC(12,2),
    descuento_total NUMERIC(14,2),
    porcentaje_descuento_promedio NUMERIC(10,2),
    numero_transacciones INTEGER,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,
    PRIMARY KEY (fecha, id_sku, id_canal, id_campana)
);

CREATE TABLE gold.fact_inventario (
    fecha DATE NOT NULL,
    id_sku TEXT NOT NULL,
    stock_inicial_sistema INTEGER,
    ingresos_almacen INTEGER,
    stock_apertura INTEGER,
    stock_disponible_cierre INTEGER,
    stock_minimo INTEGER,
    costo_unitario NUMERIC(12,2),
    quiebre_stock_flag BOOLEAN,
    flag_stock_bajo BOOLEAN,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,
    PRIMARY KEY (fecha, id_sku)
);

CREATE TABLE gold.fact_marketing (
    fecha DATE NOT NULL,
    id_campana TEXT NOT NULL,
    plataforma_origen TEXT,
    inversion_usd NUMERIC(14,2),
    impresiones INTEGER,
    clics INTEGER,
    conversiones_atribuidas INTEGER,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,
    PRIMARY KEY (fecha, id_campana)
);

CREATE TABLE gold.ml_dataset (
    fecha DATE NOT NULL,
    id_sku TEXT NOT NULL,
    categoria TEXT,
    volumen_litros NUMERIC(10,2),
    formato_envase TEXT,

    cantidad_vendida_total INTEGER,

    stock_apertura INTEGER,
    ingresos_almacen INTEGER,
    stock_disponible_cierre INTEGER,
    stock_minimo INTEGER,

    precio_unitario_promedio NUMERIC(12,2),
    descuento_total NUMERIC(14,2),
    porcentaje_descuento_promedio NUMERIC(10,2),

    inversion_ads_total NUMERIC(14,2),
    clics_total INTEGER,
    impresiones_total INTEGER,
    conversiones_total INTEGER,

    temperatura_promedio_celsius NUMERIC(10,2),
    temperatura_maxima_celsius NUMERIC(10,2),
    humedad_porcentaje NUMERIC(10,2),
    precipitacion_mm NUMERIC(10,2),
    alerta_ola_calor BOOLEAN,

    numero_dia_semana INTEGER,
    mes INTEGER,
    trimestre INTEGER,
    es_fin_de_semana BOOLEAN,
    es_feriado BOOLEAN,
    es_quincena BOOLEAN,
    es_fin_mes BOOLEAN,
    temporada TEXT,

    ventas_lag1 INTEGER,
    ventas_lag7 INTEGER,
    ventas_roll7 NUMERIC(14,2),
    ads_lag1 NUMERIC(14,2),
    ads_lag3 NUMERIC(14,2),

    riesgo_demanda_censurada BOOLEAN,

    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,

    PRIMARY KEY (fecha, id_sku)
);

CREATE TABLE gold.ml_score_input (
    id_score_input BIGSERIAL PRIMARY KEY,
    fecha_objetivo DATE NOT NULL,
    id_sku TEXT NOT NULL,
    categoria TEXT,
    volumen_litros NUMERIC(10,2),
    formato_envase TEXT,

    stock_apertura INTEGER,
    ingresos_almacen INTEGER,

    precio_unitario_estimado NUMERIC(12,2),
    descuento_estimado NUMERIC(14,2),

    inversion_ads_planificada NUMERIC(14,2),
    clics_estimados INTEGER,
    impresiones_estimadas INTEGER,

    temperatura_promedio_estimada NUMERIC(10,2),
    temperatura_maxima_estimada NUMERIC(10,2),
    humedad_porcentaje_estimada NUMERIC(10,2),
    precipitacion_mm_estimada NUMERIC(10,2),
    alerta_ola_calor BOOLEAN,

    numero_dia_semana INTEGER,
    mes INTEGER,
    trimestre INTEGER,
    es_fin_de_semana BOOLEAN,
    es_feriado BOOLEAN,
    es_quincena BOOLEAN,
    es_fin_mes BOOLEAN,
    temporada TEXT,

    ventas_lag1 INTEGER,
    ventas_lag7 INTEGER,
    ventas_roll7 NUMERIC(14,2),
    ads_lag1 NUMERIC(14,2),
    ads_lag3 NUMERIC(14,2),

    fecha_creacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE gold.ml_score_output (
    id_score_output BIGSERIAL PRIMARY KEY,
    fecha_prediccion TIMESTAMP DEFAULT NOW(),
    fecha_objetivo DATE NOT NULL,
    id_sku TEXT NOT NULL,
    cantidad_predicha NUMERIC(14,2),
    intervalo_bajo NUMERIC(14,2),
    intervalo_alto NUMERIC(14,2),
    stock_apertura INTEGER,
    stock_recomendado NUMERIC(14,2),
    riesgo_quiebre_stock BOOLEAN,
    riesgo_sobrestock BOOLEAN,
    modelo_version TEXT,
    comentario_negocio TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE gold.ml_feature_importance (
    id_importance BIGSERIAL PRIMARY KEY,
    modelo_version TEXT,
    feature_name TEXT,
    importance_value NUMERIC(14,6),
    ranking INTEGER,
    fecha_entrenamiento TIMESTAMP DEFAULT NOW(),
    usuario_ejecucion TEXT DEFAULT CURRENT_USER
);