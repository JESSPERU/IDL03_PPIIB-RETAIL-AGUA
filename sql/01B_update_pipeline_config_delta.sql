-- ============================================================
-- 01B_update_pipeline_config_delta.sql
-- Ajuste: los CSV reales no tienen fecha_actualizacion; usan etl_loaded_at.
-- ============================================================

UPDATE meta.pipeline_config
SET campo_delta = 'etl_loaded_at',
    ultima_fecha_delta = NULL,
    actualizado_en = NOW()
WHERE nombre_tabla IN (
    'sap_ventas_cabecera',
    'sap_ventas_detalle',
    'sap_inventario_diario',
    'ads_insights_diario',
    'clima_diario_log',
    'sap_promociones'
);

UPDATE meta.pipeline_config
SET campo_delta = NULL,
    ultima_fecha_delta = NULL,
    actualizado_en = NOW()
WHERE tipo_carga = 'FULL';
