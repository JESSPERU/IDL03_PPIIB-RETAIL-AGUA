-- ============================================================
-- 00_create_schemas_meta.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Crear esquemas principales de la Arquitectura Medallion
-- ============================================================

CREATE SCHEMA IF NOT EXISTS meta;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Comentarios descriptivos
COMMENT ON SCHEMA meta IS 'Esquema de metadatos, auditoría y control del pipeline ETL/ELT.';
COMMENT ON SCHEMA bronze IS 'Capa Bronze: datos crudos RAW, cargados como TEXT desde archivos fuente.';
COMMENT ON SCHEMA silver IS 'Capa Silver: datos limpios, tipados y validados.';
COMMENT ON SCHEMA gold IS 'Capa Gold: dimensiones, hechos, dataset ML, score input y score output.';
