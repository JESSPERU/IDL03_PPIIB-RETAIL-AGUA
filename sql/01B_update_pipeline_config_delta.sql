-- ============================================================
-- 01B_update_pipeline_config_delta.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Configurar fuentes del pipeline y cargas FULL/DELTA
-- Nota: Los CSV reales usan etl_loaded_at como campo incremental.
-- ============================================================

INSERT INTO meta.pipeline_config
(
    nombre_tabla,
    esquema_origen,
    esquema_destino,
    ruta_archivo,
    tipo_carga,
    campo_delta,
    procedimiento_sp,
    activo,
    orden_ejecucion,
    descripcion
)
VALUES
(
    'sap_clientes_maestro',
    'raw_file',
    'bronze',
    'data/raw/sap_clientes_maestro.csv',
    'FULL',
    NULL,
    NULL,
    TRUE,
    1,
    'Maestro de clientes. Se carga FULL porque es catálogo.'
),
(
    'sap_productos_maestro',
    'raw_file',
    'bronze',
    'data/raw/sap_productos_maestro.csv',
    'FULL',
    NULL,
    NULL,
    TRUE,
    2,
    'Maestro de productos. Se carga FULL porque es catálogo.'
),
(
    'sap_canales_maestro',
    'raw_file',
    'bronze',
    'data/raw/sap_canales_maestro.csv',
    'FULL',
    NULL,
    NULL,
    TRUE,
    3,
    'Maestro de canales. Se carga FULL porque es catálogo.'
),
(
    'ads_campanas_maestro',
    'raw_file',
    'bronze',
    'data/raw/ads_campanas_maestro.csv',
    'FULL',
    NULL,
    NULL,
    TRUE,
    4,
    'Maestro de campañas publicitarias. Se carga FULL porque es catálogo.'
),
(
    'sap_ventas_cabecera',
    'raw_file',
    'bronze',
    'data/raw/sap_ventas_cabecera.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    5,
    'Cabecera de ventas. Se carga DELTA usando etl_loaded_at.'
),
(
    'sap_ventas_detalle',
    'raw_file',
    'bronze',
    'data/raw/sap_ventas_detalle.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    6,
    'Detalle de ventas por SKU. Se carga DELTA usando etl_loaded_at.'
),
(
    'sap_inventario_diario',
    'raw_file',
    'bronze',
    'data/raw/sap_inventario_diario.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    7,
    'Inventario diario. Se carga DELTA usando etl_loaded_at.'
),
(
    'ads_insights_diario',
    'raw_file',
    'bronze',
    'data/raw/ads_insights_diario.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    8,
    'Métricas diarias de publicidad digital. Se carga DELTA usando etl_loaded_at.'
),
(
    'clima_diario_log',
    'raw_file',
    'bronze',
    'data/raw/clima_diario_log.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    9,
    'Datos climáticos diarios. Se carga DELTA usando etl_loaded_at.'
),
(
    'calendario_eventos',
    'raw_file',
    'bronze',
    'data/raw/calendario_eventos.csv',
    'FULL',
    NULL,
    NULL,
    TRUE,
    10,
    'Calendario de eventos, feriados y estacionalidad. Se carga FULL.'
),
(
    'sap_promociones',
    'raw_file',
    'bronze',
    'data/raw/sap_promociones.csv',
    'DELTA',
    'etl_loaded_at',
    NULL,
    TRUE,
    11,
    'Promociones comerciales. Se carga DELTA usando etl_loaded_at.'
)
ON CONFLICT (nombre_tabla)
DO UPDATE SET
    esquema_origen = EXCLUDED.esquema_origen,
    esquema_destino = EXCLUDED.esquema_destino,
    ruta_archivo = EXCLUDED.ruta_archivo,
    tipo_carga = EXCLUDED.tipo_carga,
    campo_delta = EXCLUDED.campo_delta,
    procedimiento_sp = EXCLUDED.procedimiento_sp,
    activo = EXCLUDED.activo,
    orden_ejecucion = EXCLUDED.orden_ejecucion,
    descripcion = EXCLUDED.descripcion,
    actualizado_en = NOW();

-- Reinicio controlado del watermark para reconstrucción o primera carga
UPDATE meta.pipeline_config
SET ultima_fecha_delta = NULL,
    actualizado_en = NOW();

SELECT
    orden_ejecucion,
    nombre_tabla,
    esquema_destino,
    tipo_carga,
    campo_delta,
    ultima_fecha_delta,
    activo
FROM meta.pipeline_config
ORDER BY orden_ejecucion;
