-- ============================================================
-- 05_sp_bronze_to_silver.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Transformar Bronze RAW hacia Silver tipado
-- Reglas:
-- 1. No usar SELECT *
-- 2. Limpiar monedas como 'S/ 1.20'
-- 3. Aceptar fechas YYYY-MM-DD y timestamps YYYY-MM-DD HH24:MI:SS
-- 4. Auditar registros inválidos en meta.pipeline_error_log
-- ============================================================

CREATE SCHEMA IF NOT EXISTS silver;

CREATE OR REPLACE FUNCTION silver.fn_to_numeric_clean(v TEXT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    cleaned TEXT;
BEGIN
    IF v IS NULL OR TRIM(v) = '' THEN
        RETURN NULL;
    END IF;

    cleaned := regexp_replace(TRIM(v), '[^0-9\.\-]', '', 'g');

    IF cleaned IS NULL OR cleaned = '' OR cleaned = '-' OR cleaned = '.' THEN
        RETURN NULL;
    END IF;

    IF cleaned ~ '^-?[0-9]+(\.[0-9]+)?$' THEN
        RETURN cleaned::NUMERIC;
    END IF;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION silver.fn_to_int_clean(v TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    cleaned TEXT;
BEGIN
    IF v IS NULL OR TRIM(v) = '' THEN
        RETURN NULL;
    END IF;

    cleaned := regexp_replace(TRIM(v), '[^0-9\-]', '', 'g');

    IF cleaned ~ '^-?[0-9]+$' THEN
        RETURN cleaned::INTEGER;
    END IF;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION silver.fn_to_bool_clean(v TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF v IS NULL THEN
        RETURN FALSE;
    END IF;

    IF LOWER(TRIM(v)) IN ('true', '1', 'si', 'sí', 'yes', 'y') THEN
        RETURN TRUE;
    END IF;

    RETURN FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION silver.fn_to_date_clean(v TEXT)
RETURNS DATE
LANGUAGE plpgsql
AS $$
BEGIN
    IF v IS NULL OR TRIM(v) = '' THEN
        RETURN NULL;
    END IF;

    IF TRIM(v) ~ '^\d{4}-\d{2}-\d{2}$' THEN
        RETURN TO_DATE(TRIM(v), 'YYYY-MM-DD');
    END IF;

    IF TRIM(v) ~ '^\d{4}-\d{2}-\d{2} ' THEN
        RETURN LEFT(TRIM(v), 10)::DATE;
    END IF;

    IF TRIM(v) ~ '^\d{2}/\d{2}/\d{4}$' THEN
        RETURN TO_DATE(TRIM(v), 'DD/MM/YYYY');
    END IF;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION silver.fn_to_timestamp_clean(v TEXT)
RETURNS TIMESTAMP
LANGUAGE plpgsql
AS $$
BEGIN
    IF v IS NULL OR TRIM(v) = '' THEN
        RETURN NULL;
    END IF;

    IF TRIM(v) ~ '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$' THEN
        RETURN TRIM(v)::TIMESTAMP;
    END IF;

    IF TRIM(v) ~ '^\d{4}-\d{2}-\d{2}$' THEN
        RETURN TRIM(v)::DATE::TIMESTAMP;
    END IF;

    IF TRIM(v) ~ '^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$' THEN
        RETURN TO_TIMESTAMP(TRIM(v), 'DD/MM/YYYY HH24:MI:SS');
    END IF;

    IF TRIM(v) ~ '^\d{2}/\d{2}/\d{4}$' THEN
        RETURN TO_DATE(TRIM(v), 'DD/MM/YYYY')::TIMESTAMP;
    END IF;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE PROCEDURE silver.sp_bronze_to_silver()
LANGUAGE plpgsql
AS $$
BEGIN

    -- Clientes
    INSERT INTO silver.sap_clientes (
        id_cliente, nombre_empresa, tipo_cliente, distrito, ubicacion,
        etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_cliente),
        TRIM(nombre_empresa),
        TRIM(tipo_cliente),
        TRIM(distrito),
        TRIM(ubicacion),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_clientes_maestro
    WHERE id_cliente IS NOT NULL AND TRIM(id_cliente) <> ''
    ON CONFLICT (id_cliente)
    DO UPDATE SET
        nombre_empresa = EXCLUDED.nombre_empresa,
        tipo_cliente = EXCLUDED.tipo_cliente,
        distrito = EXCLUDED.distrito,
        ubicacion = EXCLUDED.ubicacion,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Productos
    INSERT INTO silver.sap_productos (
        id_sku, descripcion, categoria, volumen_litros, unidad_medida,
        formato_envase, costo_unitario_base, precio_lista, stock_seguridad,
        lead_time_dias, etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_sku),
        TRIM(descripcion),
        TRIM(categoria),
        silver.fn_to_numeric_clean(volumen_litros),
        TRIM(unidad_medida),
        TRIM(formato_envase),
        silver.fn_to_numeric_clean(costo_unitario_base),
        silver.fn_to_numeric_clean(precio_lista),
        silver.fn_to_int_clean(stock_seguridad),
        silver.fn_to_int_clean(lead_time_dias),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_productos_maestro
    WHERE id_sku IS NOT NULL AND TRIM(id_sku) <> ''
    ON CONFLICT (id_sku)
    DO UPDATE SET
        descripcion = EXCLUDED.descripcion,
        categoria = EXCLUDED.categoria,
        volumen_litros = EXCLUDED.volumen_litros,
        unidad_medida = EXCLUDED.unidad_medida,
        formato_envase = EXCLUDED.formato_envase,
        costo_unitario_base = EXCLUDED.costo_unitario_base,
        precio_lista = EXCLUDED.precio_lista,
        stock_seguridad = EXCLUDED.stock_seguridad,
        lead_time_dias = EXCLUDED.lead_time_dias,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Canales
    INSERT INTO silver.sap_canales (
        id_canal, nombre_canal, tipo_canal, comision_porcentaje,
        etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_canal),
        TRIM(nombre_canal),
        TRIM(tipo_canal),
        silver.fn_to_numeric_clean(comision_porcentaje),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_canales_maestro
    WHERE id_canal IS NOT NULL AND TRIM(id_canal) <> ''
    ON CONFLICT (id_canal)
    DO UPDATE SET
        nombre_canal = EXCLUDED.nombre_canal,
        tipo_canal = EXCLUDED.tipo_canal,
        comision_porcentaje = EXCLUDED.comision_porcentaje,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Campañas
    INSERT INTO silver.ads_campanas (
        id_campana, nombre_campana, plataforma_origen, objetivo_campana,
        id_sku_objetivo, fecha_inicio, fecha_fin, tipo_audiencia,
        etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_campana),
        TRIM(nombre_campana),
        TRIM(plataforma_origen),
        TRIM(objetivo_campana),
        TRIM(id_sku_objetivo),
        silver.fn_to_date_clean(fecha_inicio),
        silver.fn_to_date_clean(fecha_fin),
        TRIM(tipo_audiencia),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.ads_campanas_maestro
    WHERE id_campana IS NOT NULL AND TRIM(id_campana) <> ''
    ON CONFLICT (id_campana)
    DO UPDATE SET
        nombre_campana = EXCLUDED.nombre_campana,
        plataforma_origen = EXCLUDED.plataforma_origen,
        objetivo_campana = EXCLUDED.objetivo_campana,
        id_sku_objetivo = EXCLUDED.id_sku_objetivo,
        fecha_inicio = EXCLUDED.fecha_inicio,
        fecha_fin = EXCLUDED.fecha_fin,
        tipo_audiencia = EXCLUDED.tipo_audiencia,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Auditar ventas cabecera con fecha inválida
    INSERT INTO meta.pipeline_error_log (
        nombre_tabla, capa, registro_json, mensaje_error, fecha_error
    )
    SELECT
        'sap_ventas_cabecera',
        'silver',
        to_jsonb(b),
        'Registro omitido por fecha_venta inválida: ' || COALESCE(b.fecha_venta, 'NULL'),
        NOW()
    FROM bronze.sap_ventas_cabecera b
    WHERE b.id_transaccion IS NOT NULL
      AND TRIM(b.id_transaccion) <> ''
      AND silver.fn_to_date_clean(b.fecha_venta) IS NULL
      AND NOT EXISTS (
          SELECT 1
          FROM meta.pipeline_error_log e
          WHERE e.nombre_tabla = 'sap_ventas_cabecera'
            AND e.capa = 'silver'
            AND e.registro_json ->> 'id_transaccion' = b.id_transaccion
      );

    -- Ventas cabecera
    INSERT INTO silver.sap_ventas_cabecera (
        id_transaccion, fecha_venta, fecha_hora_venta, id_cliente, id_canal,
        id_campana, estado_venta, etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_transaccion),
        silver.fn_to_date_clean(fecha_venta),
        silver.fn_to_timestamp_clean(fecha_venta),
        TRIM(id_cliente),
        TRIM(id_canal),
        NULLIF(TRIM(id_campana), ''),
        TRIM(estado_venta),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_ventas_cabecera
    WHERE id_transaccion IS NOT NULL
      AND TRIM(id_transaccion) <> ''
      AND silver.fn_to_date_clean(fecha_venta) IS NOT NULL
    ON CONFLICT (id_transaccion)
    DO UPDATE SET
        fecha_venta = EXCLUDED.fecha_venta,
        fecha_hora_venta = EXCLUDED.fecha_hora_venta,
        id_cliente = EXCLUDED.id_cliente,
        id_canal = EXCLUDED.id_canal,
        id_campana = EXCLUDED.id_campana,
        estado_venta = EXCLUDED.estado_venta,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Auditar ventas detalle con numéricos inválidos relevantes
    INSERT INTO meta.pipeline_error_log (
        nombre_tabla, capa, registro_json, mensaje_error, fecha_error
    )
    SELECT
        'sap_ventas_detalle',
        'silver',
        to_jsonb(b),
        'Registro omitido por cantidad inválida: ' || COALESCE(b.cantidad_vendida, 'NULL'),
        NOW()
    FROM bronze.sap_ventas_detalle b
    WHERE b.id_transaccion IS NOT NULL
      AND TRIM(b.id_transaccion) <> ''
      AND silver.fn_to_int_clean(b.cantidad_vendida) IS NULL
      AND NOT EXISTS (
          SELECT 1
          FROM meta.pipeline_error_log e
          WHERE e.nombre_tabla = 'sap_ventas_detalle'
            AND e.capa = 'silver'
            AND e.registro_json ->> 'id_transaccion' = b.id_transaccion
            AND e.registro_json ->> 'linea_detalle' = b.linea_detalle
      );

    -- Ventas detalle
    INSERT INTO silver.sap_ventas_detalle (
        id_detalle, id_transaccion, linea_detalle, id_sku, cantidad_vendida,
        precio_unitario_aplicado, porcentaje_descuento, monto_descuento,
        monto_linea, etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_transaccion) || '_' || COALESCE(NULLIF(TRIM(linea_detalle), ''), '1') AS id_detalle,
        TRIM(id_transaccion),
        COALESCE(silver.fn_to_int_clean(linea_detalle), 1),
        TRIM(id_sku),
        silver.fn_to_int_clean(cantidad_vendida),
        COALESCE(silver.fn_to_numeric_clean(precio_unitario_aplicado), 0),
        COALESCE(silver.fn_to_numeric_clean(porcentaje_descuento), 0),
        COALESCE(silver.fn_to_numeric_clean(monto_descuento), 0),
        COALESCE(
            silver.fn_to_numeric_clean(monto_linea),
            silver.fn_to_int_clean(cantidad_vendida) * silver.fn_to_numeric_clean(precio_unitario_aplicado)
        ),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_ventas_detalle
    WHERE id_transaccion IS NOT NULL
      AND TRIM(id_transaccion) <> ''
      AND id_sku IS NOT NULL
      AND TRIM(id_sku) <> ''
      AND silver.fn_to_int_clean(cantidad_vendida) IS NOT NULL
    ON CONFLICT (id_detalle)
    DO UPDATE SET
        id_transaccion = EXCLUDED.id_transaccion,
        linea_detalle = EXCLUDED.linea_detalle,
        id_sku = EXCLUDED.id_sku,
        cantidad_vendida = EXCLUDED.cantidad_vendida,
        precio_unitario_aplicado = EXCLUDED.precio_unitario_aplicado,
        porcentaje_descuento = EXCLUDED.porcentaje_descuento,
        monto_descuento = EXCLUDED.monto_descuento,
        monto_linea = EXCLUDED.monto_linea,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Inventario
    INSERT INTO silver.sap_inventario_diario (
        fecha_foto, id_sku, stock_inicial_sistema, ingresos_almacen,
        stock_apertura, stock_disponible_cierre, stock_minimo, costo_unitario,
        quiebre_stock_flag, etl_loaded_at, fecha_modificacion
    )
    SELECT
        silver.fn_to_date_clean(fecha_foto),
        TRIM(id_sku),
        silver.fn_to_int_clean(stock_inicial_sistema),
        silver.fn_to_int_clean(ingresos_almacen),
        silver.fn_to_int_clean(stock_apertura),
        silver.fn_to_int_clean(stock_disponible_cierre),
        silver.fn_to_int_clean(stock_minimo),
        silver.fn_to_numeric_clean(costo_unitario),
        silver.fn_to_bool_clean(quiebre_stock_flag),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_inventario_diario
    WHERE silver.fn_to_date_clean(fecha_foto) IS NOT NULL
      AND id_sku IS NOT NULL
      AND TRIM(id_sku) <> ''
    ON CONFLICT (fecha_foto, id_sku)
    DO UPDATE SET
        stock_inicial_sistema = EXCLUDED.stock_inicial_sistema,
        ingresos_almacen = EXCLUDED.ingresos_almacen,
        stock_apertura = EXCLUDED.stock_apertura,
        stock_disponible_cierre = EXCLUDED.stock_disponible_cierre,
        stock_minimo = EXCLUDED.stock_minimo,
        costo_unitario = EXCLUDED.costo_unitario,
        quiebre_stock_flag = EXCLUDED.quiebre_stock_flag,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Ads insights
    INSERT INTO silver.ads_insights_diario (
        id_campana, fecha_metrica, plataforma_origen, inversion_usd,
        clics, impresiones, conversiones_atribuidas, moneda,
        etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_campana),
        silver.fn_to_date_clean(fecha_metrica),
        TRIM(plataforma_origen),
        silver.fn_to_numeric_clean(inversion_usd),
        silver.fn_to_int_clean(clics),
        silver.fn_to_int_clean(impresiones),
        silver.fn_to_int_clean(conversiones_atribuidas),
        TRIM(moneda),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.ads_insights_diario
    WHERE id_campana IS NOT NULL
      AND TRIM(id_campana) <> ''
      AND silver.fn_to_date_clean(fecha_metrica) IS NOT NULL
    ON CONFLICT (id_campana, fecha_metrica)
    DO UPDATE SET
        plataforma_origen = EXCLUDED.plataforma_origen,
        inversion_usd = EXCLUDED.inversion_usd,
        clics = EXCLUDED.clics,
        impresiones = EXCLUDED.impresiones,
        conversiones_atribuidas = EXCLUDED.conversiones_atribuidas,
        moneda = EXCLUDED.moneda,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Clima
    INSERT INTO silver.clima_diario (
        fecha_medicion, temperatura_promedio_celsius, temperatura_maxima_celsius,
        temperatura_minima_celsius, humedad_porcentaje, precipitacion_mm,
        alerta_ola_calor, fuente_clima, etl_loaded_at, fecha_modificacion
    )
    SELECT
        silver.fn_to_date_clean(fecha_medicion),
        silver.fn_to_numeric_clean(temperatura_promedio_celsius),
        silver.fn_to_numeric_clean(temperatura_maxima_celsius),
        silver.fn_to_numeric_clean(temperatura_minima_celsius),
        silver.fn_to_numeric_clean(humedad_porcentaje),
        silver.fn_to_numeric_clean(precipitacion_mm),
        silver.fn_to_bool_clean(alerta_ola_calor),
        TRIM(fuente_clima),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.clima_diario_log
    WHERE silver.fn_to_date_clean(fecha_medicion) IS NOT NULL
    ON CONFLICT (fecha_medicion)
    DO UPDATE SET
        temperatura_promedio_celsius = EXCLUDED.temperatura_promedio_celsius,
        temperatura_maxima_celsius = EXCLUDED.temperatura_maxima_celsius,
        temperatura_minima_celsius = EXCLUDED.temperatura_minima_celsius,
        humedad_porcentaje = EXCLUDED.humedad_porcentaje,
        precipitacion_mm = EXCLUDED.precipitacion_mm,
        alerta_ola_calor = EXCLUDED.alerta_ola_calor,
        fuente_clima = EXCLUDED.fuente_clima,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Calendario
    INSERT INTO silver.calendario_eventos (
        fecha, nombre_dia, numero_dia_semana, mes, trimestre,
        es_feriado, nombre_feriado, es_quincena, es_fin_mes,
        temporada, etl_loaded_at, fecha_modificacion
    )
    SELECT
        silver.fn_to_date_clean(fecha),
        TRIM(nombre_dia),
        silver.fn_to_int_clean(numero_dia_semana),
        silver.fn_to_int_clean(mes),
        silver.fn_to_int_clean(trimestre),
        silver.fn_to_bool_clean(es_feriado),
        TRIM(nombre_feriado),
        silver.fn_to_bool_clean(es_quincena),
        silver.fn_to_bool_clean(es_fin_mes),
        TRIM(temporada),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.calendario_eventos
    WHERE silver.fn_to_date_clean(fecha) IS NOT NULL
    ON CONFLICT (fecha)
    DO UPDATE SET
        nombre_dia = EXCLUDED.nombre_dia,
        numero_dia_semana = EXCLUDED.numero_dia_semana,
        mes = EXCLUDED.mes,
        trimestre = EXCLUDED.trimestre,
        es_feriado = EXCLUDED.es_feriado,
        nombre_feriado = EXCLUDED.nombre_feriado,
        es_quincena = EXCLUDED.es_quincena,
        es_fin_mes = EXCLUDED.es_fin_mes,
        temporada = EXCLUDED.temporada,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

    -- Promociones
    INSERT INTO silver.sap_promociones (
        id_promocion, id_sku, fecha_inicio, fecha_fin,
        porcentaje_descuento, tipo_promocion, etl_loaded_at, fecha_modificacion
    )
    SELECT
        TRIM(id_promocion),
        TRIM(id_sku),
        silver.fn_to_date_clean(fecha_inicio),
        silver.fn_to_date_clean(fecha_fin),
        silver.fn_to_numeric_clean(porcentaje_descuento),
        TRIM(tipo_promocion),
        silver.fn_to_timestamp_clean(etl_loaded_at),
        NOW()
    FROM bronze.sap_promociones
    WHERE id_promocion IS NOT NULL AND TRIM(id_promocion) <> ''
    ON CONFLICT (id_promocion)
    DO UPDATE SET
        id_sku = EXCLUDED.id_sku,
        fecha_inicio = EXCLUDED.fecha_inicio,
        fecha_fin = EXCLUDED.fecha_fin,
        porcentaje_descuento = EXCLUDED.porcentaje_descuento,
        tipo_promocion = EXCLUDED.tipo_promocion,
        etl_loaded_at = EXCLUDED.etl_loaded_at,
        fecha_modificacion = NOW();

END;
$$;
