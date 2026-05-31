-- ============================================================
-- 01_create_meta_tables.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Crear tablas de control, auditoría y errores del pipeline
-- ============================================================

CREATE TABLE IF NOT EXISTS meta.pipeline_config (
    id_config BIGSERIAL PRIMARY KEY,
    nombre_tabla TEXT NOT NULL UNIQUE,
    esquema_origen TEXT NOT NULL,
    esquema_destino TEXT NOT NULL,
    ruta_archivo TEXT,
    tipo_carga TEXT NOT NULL CHECK (tipo_carga IN ('FULL', 'DELTA')),
    campo_delta TEXT,
    ultima_fecha_delta TIMESTAMP,
    procedimiento_sp TEXT,
    activo BOOLEAN DEFAULT TRUE,
    orden_ejecucion INTEGER,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    usuario_ejecucion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE IF NOT EXISTS meta.pipeline_run_log (
    id_run BIGSERIAL PRIMARY KEY,
    nombre_tabla TEXT,
    capa TEXT,
    tipo_carga TEXT,
    estado TEXT CHECK (estado IN ('INICIADO', 'EXITOSO', 'ERROR')),
    fecha_inicio TIMESTAMP DEFAULT NOW(),
    fecha_fin TIMESTAMP,
    registros_leidos INTEGER DEFAULT 0,
    registros_insertados INTEGER DEFAULT 0,
    registros_actualizados INTEGER DEFAULT 0,
    registros_duplicados INTEGER DEFAULT 0,
    mensaje_error TEXT,
    usuario_ejecucion TEXT DEFAULT CURRENT_USER
);

CREATE TABLE IF NOT EXISTS meta.pipeline_error_log (
    id_error BIGSERIAL PRIMARY KEY,
    nombre_tabla TEXT,
    capa TEXT,
    registro_json JSONB,
    mensaje_error TEXT,
    fecha_error TIMESTAMP DEFAULT NOW(),
    usuario_ejecucion TEXT DEFAULT CURRENT_USER
);

COMMENT ON TABLE meta.pipeline_config IS 'Tabla maestra de configuración del pipeline. Controla origen, destino, tipo de carga FULL/DELTA y orden de ejecución.';
COMMENT ON TABLE meta.pipeline_run_log IS 'Tabla de auditoría de cada ejecución del pipeline.';
COMMENT ON TABLE meta.pipeline_error_log IS 'Tabla para registrar errores a nivel de registro o proceso.';
