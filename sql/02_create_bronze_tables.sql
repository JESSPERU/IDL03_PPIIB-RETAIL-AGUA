-- ============================================================
-- 02_create_bronze_tables.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Re-crear tablas RAW/Bronze alineadas a los CSV reales
-- Nota: En Bronze se conserva el dato crudo como TEXT + auditoría ETL.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS bronze;

DROP TABLE IF EXISTS bronze.sap_ventas_detalle CASCADE;
DROP TABLE IF EXISTS bronze.sap_ventas_cabecera CASCADE;
DROP TABLE IF EXISTS bronze.sap_inventario_diario CASCADE;
DROP TABLE IF EXISTS bronze.ads_insights_diario CASCADE;
DROP TABLE IF EXISTS bronze.clima_diario_log CASCADE;
DROP TABLE IF EXISTS bronze.calendario_eventos CASCADE;
DROP TABLE IF EXISTS bronze.sap_promociones CASCADE;
DROP TABLE IF EXISTS bronze.ads_campanas_maestro CASCADE;
DROP TABLE IF EXISTS bronze.sap_canales_maestro CASCADE;
DROP TABLE IF EXISTS bronze.sap_clientes_maestro CASCADE;
DROP TABLE IF EXISTS bronze.sap_productos_maestro CASCADE;

CREATE TABLE bronze.sap_clientes_maestro (
    id_cliente TEXT,
    nombre_empresa TEXT,
    tipo_cliente TEXT,
    distrito TEXT,
    ubicacion TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_productos_maestro (
    id_sku TEXT,
    descripcion TEXT,
    categoria TEXT,
    volumen_litros TEXT,
    unidad_medida TEXT,
    formato_envase TEXT,
    costo_unitario_base TEXT,
    precio_lista TEXT,
    stock_seguridad TEXT,
    lead_time_dias TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_canales_maestro (
    id_canal TEXT,
    nombre_canal TEXT,
    tipo_canal TEXT,
    comision_porcentaje TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.ads_campanas_maestro (
    id_campana TEXT,
    nombre_campana TEXT,
    plataforma_origen TEXT,
    objetivo_campana TEXT,
    id_sku_objetivo TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    tipo_audiencia TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_ventas_cabecera (
    id_transaccion TEXT,
    fecha_venta TEXT,
    id_cliente TEXT,
    id_canal TEXT,
    id_campana TEXT,
    estado_venta TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_ventas_detalle (
    id_transaccion TEXT,
    linea_detalle TEXT,
    id_sku TEXT,
    cantidad_vendida TEXT,
    precio_unitario_aplicado TEXT,
    porcentaje_descuento TEXT,
    monto_descuento TEXT,
    monto_linea TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_inventario_diario (
    fecha_foto TEXT,
    id_sku TEXT,
    stock_inicial_sistema TEXT,
    ingresos_almacen TEXT,
    stock_apertura TEXT,
    stock_disponible_cierre TEXT,
    stock_minimo TEXT,
    costo_unitario TEXT,
    quiebre_stock_flag TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.ads_insights_diario (
    id_campana TEXT,
    fecha_metrica TEXT,
    plataforma_origen TEXT,
    inversion_usd TEXT,
    clics TEXT,
    impresiones TEXT,
    conversiones_atribuidas TEXT,
    moneda TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.clima_diario_log (
    fecha_medicion TEXT,
    temperatura_promedio_celsius TEXT,
    temperatura_maxima_celsius TEXT,
    temperatura_minima_celsius TEXT,
    humedad_porcentaje TEXT,
    precipitacion_mm TEXT,
    alerta_ola_calor TEXT,
    fuente_clima TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.calendario_eventos (
    fecha TEXT,
    nombre_dia TEXT,
    numero_dia_semana TEXT,
    mes TEXT,
    trimestre TEXT,
    es_feriado TEXT,
    nombre_feriado TEXT,
    es_quincena TEXT,
    es_fin_mes TEXT,
    temporada TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

CREATE TABLE bronze.sap_promociones (
    id_promocion TEXT,
    id_sku TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    porcentaje_descuento TEXT,
    tipo_promocion TEXT,
    etl_source_file TEXT,
    etl_loaded_at TEXT,
    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);
