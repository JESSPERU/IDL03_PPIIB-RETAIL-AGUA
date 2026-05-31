-- ============================================================
-- 02_create_bronze_tables.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Crear tablas RAW/Bronze con columnas TEXT + auditoría
-- ============================================================

CREATE SCHEMA IF NOT EXISTS bronze;

-- ============================================================
-- 1. Maestro de Clientes
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_clientes_maestro (
    id_cliente TEXT,
    nombre_empresa TEXT,
    tipo_cliente TEXT,
    ubicacion TEXT,
    distrito TEXT,
    provincia TEXT,
    departamento TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 2. Maestro de Productos
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_productos_maestro (
    id_sku TEXT,
    descripcion TEXT,
    categoria TEXT,
    volumen_litros TEXT,
    unidad_medida TEXT,
    lead_time_dias TEXT,
    stock_seguridad TEXT,
    estado_producto TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 3. Maestro de Canales
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_canales_maestro (
    id_canal TEXT,
    nombre_canal TEXT,
    tipo_canal TEXT,
    comision_porcentaje TEXT,
    estado_canal TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 4. Maestro de Campañas Ads
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.ads_campanas_maestro (
    id_campana TEXT,
    nombre_campana TEXT,
    plataforma_origen TEXT,
    objetivo_campana TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    estado_campana TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 5. Ventas Cabecera
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_ventas_cabecera (
    id_transaccion TEXT,
    fecha_venta TEXT,
    fecha_hora_venta TEXT,
    id_cliente TEXT,
    id_canal TEXT,
    estado_transaccion TEXT,
    metodo_pago TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 6. Ventas Detalle
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_ventas_detalle (
    id_detalle TEXT,
    id_transaccion TEXT,
    id_sku TEXT,
    cantidad_vendida TEXT,
    precio_unitario_aplicado TEXT,
    monto_descuento TEXT,
    porcentaje_descuento TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 7. Inventario Diario
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_inventario_diario (
    fecha_foto TEXT,
    id_sku TEXT,
    stock_apertura TEXT,
    ingresos_almacen TEXT,
    salidas_ajuste TEXT,
    stock_disponible_cierre TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 8. Insights diarios de Ads
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.ads_insights_diario (
    id_campana TEXT,
    fecha_metrica TEXT,
    plataforma_origen TEXT,
    inversion_usd TEXT,
    impresiones TEXT,
    clics TEXT,
    conversiones TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 9. Clima Diario
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.clima_diario_log (
    fecha_medicion TEXT,
    ciudad TEXT,
    temperatura_promedio_celsius TEXT,
    temperatura_maxima_celsius TEXT,
    temperatura_minima_celsius TEXT,
    humedad_porcentaje TEXT,
    alerta_ola_calor TEXT,
    fuente_clima TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 10. Calendario y eventos
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.calendario_eventos (
    fecha TEXT,
    anio TEXT,
    mes TEXT,
    dia TEXT,
    dia_semana TEXT,
    nombre_dia TEXT,
    es_fin_de_semana TEXT,
    es_feriado TEXT,
    nombre_feriado TEXT,
    es_quincena TEXT,
    es_fin_de_mes TEXT,
    temporada TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- 11. Promociones
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.sap_promociones (
    id_promocion TEXT,
    id_sku TEXT,
    nombre_promocion TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    tipo_promocion TEXT,
    porcentaje_descuento TEXT,
    monto_descuento TEXT,
    estado_promocion TEXT,
    fecha_actualizacion TEXT,

    etl_batch_id TEXT,
    etl_fecha_carga TIMESTAMP DEFAULT NOW(),
    etl_archivo_origen TEXT,
    etl_hash_registro TEXT,
    etl_usuario TEXT DEFAULT CURRENT_USER
);

-- ============================================================
-- Comentarios de documentación
-- ============================================================

COMMENT ON TABLE bronze.sap_clientes_maestro IS 'Tabla RAW de clientes provenientes del sistema SAP/ERP.';
COMMENT ON TABLE bronze.sap_productos_maestro IS 'Tabla RAW de productos/SKUs.';
COMMENT ON TABLE bronze.sap_canales_maestro IS 'Tabla RAW de canales de venta.';
COMMENT ON TABLE bronze.ads_campanas_maestro IS 'Tabla RAW de campañas publicitarias.';
COMMENT ON TABLE bronze.sap_ventas_cabecera IS 'Tabla RAW de cabecera de ventas.';
COMMENT ON TABLE bronze.sap_ventas_detalle IS 'Tabla RAW de detalle de ventas por SKU.';
COMMENT ON TABLE bronze.sap_inventario_diario IS 'Tabla RAW de inventario diario con stock apertura y cierre.';
COMMENT ON TABLE bronze.ads_insights_diario IS 'Tabla RAW de métricas diarias de marketing digital.';
COMMENT ON TABLE bronze.clima_diario_log IS 'Tabla RAW de clima diario.';
COMMENT ON TABLE bronze.calendario_eventos IS 'Tabla RAW de calendario, feriados y estacionalidad.';
COMMENT ON TABLE bronze.sap_promociones IS 'Tabla RAW de promociones comerciales.';
