-- ============================================================
-- 03_create_silver_tables.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Re-crear tablas Silver limpias, tipadas y alineadas a RAW real
-- ============================================================

CREATE SCHEMA IF NOT EXISTS silver;

DROP TABLE IF EXISTS silver.sap_ventas_detalle CASCADE;
DROP TABLE IF EXISTS silver.sap_ventas_cabecera CASCADE;
DROP TABLE IF EXISTS silver.sap_inventario_diario CASCADE;
DROP TABLE IF EXISTS silver.ads_insights_diario CASCADE;
DROP TABLE IF EXISTS silver.clima_diario CASCADE;
DROP TABLE IF EXISTS silver.calendario_eventos CASCADE;
DROP TABLE IF EXISTS silver.sap_promociones CASCADE;
DROP TABLE IF EXISTS silver.ads_campanas CASCADE;
DROP TABLE IF EXISTS silver.sap_canales CASCADE;
DROP TABLE IF EXISTS silver.sap_clientes CASCADE;
DROP TABLE IF EXISTS silver.sap_productos CASCADE;

CREATE TABLE silver.sap_clientes (
    id_cliente TEXT PRIMARY KEY,
    nombre_empresa TEXT,
    tipo_cliente TEXT,
    distrito TEXT,
    ubicacion TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_productos (
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
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_canales (
    id_canal TEXT PRIMARY KEY,
    nombre_canal TEXT,
    tipo_canal TEXT,
    comision_porcentaje NUMERIC(10,4),
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.ads_campanas (
    id_campana TEXT PRIMARY KEY,
    nombre_campana TEXT,
    plataforma_origen TEXT,
    objetivo_campana TEXT,
    id_sku_objetivo TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    tipo_audiencia TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_ventas_cabecera (
    id_transaccion TEXT PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    fecha_hora_venta TIMESTAMP,
    id_cliente TEXT,
    id_canal TEXT,
    id_campana TEXT,
    estado_venta TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_ventas_detalle (
    id_detalle TEXT PRIMARY KEY,
    id_transaccion TEXT NOT NULL,
    linea_detalle INTEGER,
    id_sku TEXT NOT NULL,
    cantidad_vendida INTEGER,
    precio_unitario_aplicado NUMERIC(12,2),
    porcentaje_descuento NUMERIC(10,2),
    monto_descuento NUMERIC(12,2),
    monto_linea NUMERIC(12,2),
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_inventario_diario (
    fecha_foto DATE NOT NULL,
    id_sku TEXT NOT NULL,
    stock_inicial_sistema INTEGER,
    ingresos_almacen INTEGER,
    stock_apertura INTEGER,
    stock_disponible_cierre INTEGER,
    stock_minimo INTEGER,
    costo_unitario NUMERIC(12,2),
    quiebre_stock_flag BOOLEAN,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,
    PRIMARY KEY (fecha_foto, id_sku)
);

CREATE TABLE silver.ads_insights_diario (
    id_campana TEXT NOT NULL,
    fecha_metrica DATE NOT NULL,
    plataforma_origen TEXT,
    inversion_usd NUMERIC(12,2),
    clics INTEGER,
    impresiones INTEGER,
    conversiones_atribuidas INTEGER,
    moneda TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER,
    PRIMARY KEY (id_campana, fecha_metrica)
);

CREATE TABLE silver.clima_diario (
    fecha_medicion DATE PRIMARY KEY,
    temperatura_promedio_celsius NUMERIC(10,2),
    temperatura_maxima_celsius NUMERIC(10,2),
    temperatura_minima_celsius NUMERIC(10,2),
    humedad_porcentaje NUMERIC(10,2),
    precipitacion_mm NUMERIC(10,2),
    alerta_ola_calor BOOLEAN,
    fuente_clima TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.calendario_eventos (
    fecha DATE PRIMARY KEY,
    nombre_dia TEXT,
    numero_dia_semana INTEGER,
    mes INTEGER,
    trimestre INTEGER,
    es_feriado BOOLEAN,
    nombre_feriado TEXT,
    es_quincena BOOLEAN,
    es_fin_mes BOOLEAN,
    temporada TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE silver.sap_promociones (
    id_promocion TEXT PRIMARY KEY,
    id_sku TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    porcentaje_descuento NUMERIC(10,2),
    tipo_promocion TEXT,
    etl_loaded_at TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    usuario_modificacion TEXT DEFAULT CURRENT_USER
);
