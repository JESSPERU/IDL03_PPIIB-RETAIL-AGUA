-- ============================================================
-- 06_sp_silver_to_gold.sql
-- Proyecto: IDL03_PPIIB RETAIL AGUA
-- Objetivo: Transformar Silver hacia Gold alineado a Silver real
-- Regla: NO usar SELECT *
-- ============================================================

CREATE OR REPLACE PROCEDURE gold.sp_silver_to_gold()
LANGUAGE plpgsql
AS $$
BEGIN

    TRUNCATE TABLE
        gold.ml_score_output,
        gold.ml_score_input,
        gold.ml_dataset,
        gold.fact_marketing,
        gold.fact_inventario,
        gold.fact_ventas_diarias,
        gold.dim_tiempo,
        gold.dim_producto
    RESTART IDENTITY;

    -- ========================================================
    -- 1. Dim Producto
    -- ========================================================

    INSERT INTO gold.dim_producto (
        id_sku,
        descripcion,
        categoria,
        volumen_litros,
        unidad_medida,
        formato_envase,
        costo_unitario_base,
        precio_lista,
        stock_seguridad,
        lead_time_dias,
        fecha_modificacion
    )
    SELECT
        p.id_sku,
        p.descripcion,
        p.categoria,
        p.volumen_litros,
        p.unidad_medida,
        p.formato_envase,
        p.costo_unitario_base,
        p.precio_lista,
        p.stock_seguridad,
        p.lead_time_dias,
        NOW()
    FROM silver.sap_productos p
    WHERE p.id_sku IS NOT NULL;

    -- ========================================================
    -- 2. Dim Tiempo + Clima
    -- ========================================================

    INSERT INTO gold.dim_tiempo (
        fecha,
        anio,
        mes,
        trimestre,
        numero_dia_semana,
        nombre_dia,
        es_fin_de_semana,
        es_feriado,
        nombre_feriado,
        es_quincena,
        es_fin_mes,
        temporada,
        temperatura_promedio_celsius,
        temperatura_maxima_celsius,
        temperatura_minima_celsius,
        humedad_porcentaje,
        precipitacion_mm,
        alerta_ola_calor,
        fuente_clima,
        fecha_modificacion
    )
    SELECT
        c.fecha,
        EXTRACT(YEAR FROM c.fecha)::INTEGER AS anio,
        c.mes,
        c.trimestre,
        c.numero_dia_semana,
        c.nombre_dia,
        CASE WHEN c.numero_dia_semana IN (6,7) THEN TRUE ELSE FALSE END AS es_fin_de_semana,
        c.es_feriado,
        c.nombre_feriado,
        c.es_quincena,
        c.es_fin_mes,
        c.temporada,
        cl.temperatura_promedio_celsius,
        cl.temperatura_maxima_celsius,
        cl.temperatura_minima_celsius,
        cl.humedad_porcentaje,
        cl.precipitacion_mm,
        cl.alerta_ola_calor,
        cl.fuente_clima,
        NOW()
    FROM silver.calendario_eventos c
    LEFT JOIN silver.clima_diario cl
        ON c.fecha = cl.fecha_medicion
    WHERE c.fecha IS NOT NULL;

    -- ========================================================
    -- 3. Fact Ventas Diarias
    -- ========================================================

    INSERT INTO gold.fact_ventas_diarias (
        fecha,
        id_sku,
        id_canal,
        id_campana,
        cantidad_vendida_total,
        venta_total,
        precio_unitario_promedio,
        descuento_total,
        porcentaje_descuento_promedio,
        numero_transacciones,
        fecha_modificacion
    )
    SELECT
        vc.fecha_venta AS fecha,
        vd.id_sku,
        COALESCE(vc.id_canal, 'SIN_CANAL') AS id_canal,
        COALESCE(vc.id_campana, 'SIN_CAMPANA') AS id_campana,
        SUM(COALESCE(vd.cantidad_vendida, 0)) AS cantidad_vendida_total,
        SUM(
            COALESCE(
                vd.monto_linea,
                COALESCE(vd.cantidad_vendida, 0) * COALESCE(vd.precio_unitario_aplicado, 0)
            )
        ) AS venta_total,
        AVG(vd.precio_unitario_aplicado) AS precio_unitario_promedio,
        SUM(COALESCE(vd.monto_descuento, 0)) AS descuento_total,
        AVG(COALESCE(vd.porcentaje_descuento, 0)) AS porcentaje_descuento_promedio,
        COUNT(DISTINCT vc.id_transaccion) AS numero_transacciones,
        NOW()
    FROM silver.sap_ventas_cabecera vc
    INNER JOIN silver.sap_ventas_detalle vd
        ON vc.id_transaccion = vd.id_transaccion
    WHERE vc.fecha_venta IS NOT NULL
      AND vd.id_sku IS NOT NULL
    GROUP BY
        vc.fecha_venta,
        vd.id_sku,
        COALESCE(vc.id_canal, 'SIN_CANAL'),
        COALESCE(vc.id_campana, 'SIN_CAMPANA');

    -- ========================================================
    -- 4. Fact Inventario
    -- ========================================================

    INSERT INTO gold.fact_inventario (
        fecha,
        id_sku,
        stock_inicial_sistema,
        ingresos_almacen,
        stock_apertura,
        stock_disponible_cierre,
        stock_minimo,
        costo_unitario,
        quiebre_stock_flag,
        flag_stock_bajo,
        fecha_modificacion
    )
    SELECT
        i.fecha_foto AS fecha,
        i.id_sku,
        i.stock_inicial_sistema,
        i.ingresos_almacen,
        i.stock_apertura,
        i.stock_disponible_cierre,
        i.stock_minimo,
        i.costo_unitario,
        COALESCE(i.quiebre_stock_flag, FALSE) AS quiebre_stock_flag,
        CASE
            WHEN COALESCE(i.stock_apertura, 0) <= COALESCE(i.stock_minimo, 0)
            THEN TRUE ELSE FALSE
        END AS flag_stock_bajo,
        NOW()
    FROM silver.sap_inventario_diario i
    WHERE i.fecha_foto IS NOT NULL
      AND i.id_sku IS NOT NULL;

    -- ========================================================
    -- 5. Fact Marketing
    -- ========================================================

    INSERT INTO gold.fact_marketing (
        fecha,
        id_campana,
        plataforma_origen,
        inversion_usd,
        impresiones,
        clics,
        conversiones_atribuidas,
        fecha_modificacion
    )
    SELECT
        a.fecha_metrica AS fecha,
        a.id_campana,
        a.plataforma_origen,
        SUM(COALESCE(a.inversion_usd, 0)) AS inversion_usd,
        SUM(COALESCE(a.impresiones, 0)) AS impresiones,
        SUM(COALESCE(a.clics, 0)) AS clics,
        SUM(COALESCE(a.conversiones_atribuidas, 0)) AS conversiones_atribuidas,
        NOW()
    FROM silver.ads_insights_diario a
    WHERE a.fecha_metrica IS NOT NULL
      AND a.id_campana IS NOT NULL
    GROUP BY
        a.fecha_metrica,
        a.id_campana,
        a.plataforma_origen;

    -- ========================================================
    -- 6. ML Dataset
    -- Granularidad: fecha + SKU
    -- ========================================================

    INSERT INTO gold.ml_dataset (
        fecha,
        id_sku,
        categoria,
        volumen_litros,
        formato_envase,
        cantidad_vendida_total,
        stock_apertura,
        ingresos_almacen,
        stock_disponible_cierre,
        stock_minimo,
        precio_unitario_promedio,
        descuento_total,
        porcentaje_descuento_promedio,
        inversion_ads_total,
        clics_total,
        impresiones_total,
        conversiones_total,
        temperatura_promedio_celsius,
        temperatura_maxima_celsius,
        humedad_porcentaje,
        precipitacion_mm,
        alerta_ola_calor,
        numero_dia_semana,
        mes,
        trimestre,
        es_fin_de_semana,
        es_feriado,
        es_quincena,
        es_fin_mes,
        temporada,
        ventas_lag1,
        ventas_lag7,
        ventas_roll7,
        ads_lag1,
        ads_lag3,
        riesgo_demanda_censurada,
        fecha_modificacion
    )
    WITH ventas_sku AS (
        SELECT
            fecha,
            id_sku,
            SUM(cantidad_vendida_total) AS cantidad_vendida_total,
            SUM(venta_total) AS venta_total,
            AVG(precio_unitario_promedio) AS precio_unitario_promedio,
            SUM(descuento_total) AS descuento_total,
            AVG(porcentaje_descuento_promedio) AS porcentaje_descuento_promedio
        FROM gold.fact_ventas_diarias
        GROUP BY fecha, id_sku
    ),
    marketing_dia AS (
        SELECT
            fecha,
            SUM(inversion_usd) AS inversion_ads_total,
            SUM(clics) AS clics_total,
            SUM(impresiones) AS impresiones_total,
            SUM(conversiones_atribuidas) AS conversiones_total
        FROM gold.fact_marketing
        GROUP BY fecha
    ),
    base AS (
        SELECT
            v.fecha,
            v.id_sku,
            p.categoria,
            p.volumen_litros,
            p.formato_envase,
            v.cantidad_vendida_total,
            i.stock_apertura,
            i.ingresos_almacen,
            i.stock_disponible_cierre,
            i.stock_minimo,
            v.precio_unitario_promedio,
            v.descuento_total,
            v.porcentaje_descuento_promedio,
            COALESCE(m.inversion_ads_total, 0) AS inversion_ads_total,
            COALESCE(m.clics_total, 0) AS clics_total,
            COALESCE(m.impresiones_total, 0) AS impresiones_total,
            COALESCE(m.conversiones_total, 0) AS conversiones_total,
            t.temperatura_promedio_celsius,
            t.temperatura_maxima_celsius,
            t.humedad_porcentaje,
            t.precipitacion_mm,
            t.alerta_ola_calor,
            t.numero_dia_semana,
            t.mes,
            t.trimestre,
            t.es_fin_de_semana,
            t.es_feriado,
            t.es_quincena,
            t.es_fin_mes,
            t.temporada
        FROM ventas_sku v
        LEFT JOIN gold.dim_producto p
            ON v.id_sku = p.id_sku
        LEFT JOIN gold.fact_inventario i
            ON v.fecha = i.fecha
           AND v.id_sku = i.id_sku
        LEFT JOIN marketing_dia m
            ON v.fecha = m.fecha
        LEFT JOIN gold.dim_tiempo t
            ON v.fecha = t.fecha
    ),
    features AS (
        SELECT
            b.*,
            LAG(b.cantidad_vendida_total, 1) OVER (
                PARTITION BY b.id_sku ORDER BY b.fecha
            ) AS ventas_lag1,
            LAG(b.cantidad_vendida_total, 7) OVER (
                PARTITION BY b.id_sku ORDER BY b.fecha
            ) AS ventas_lag7,
            AVG(b.cantidad_vendida_total) OVER (
                PARTITION BY b.id_sku
                ORDER BY b.fecha
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS ventas_roll7,
            LAG(b.inversion_ads_total, 1) OVER (
                PARTITION BY b.id_sku ORDER BY b.fecha
            ) AS ads_lag1,
            LAG(b.inversion_ads_total, 3) OVER (
                PARTITION BY b.id_sku ORDER BY b.fecha
            ) AS ads_lag3
        FROM base b
    )
    SELECT
        fecha,
        id_sku,
        categoria,
        volumen_litros,
        formato_envase,
        cantidad_vendida_total,
        stock_apertura,
        ingresos_almacen,
        stock_disponible_cierre,
        stock_minimo,
        precio_unitario_promedio,
        descuento_total,
        porcentaje_descuento_promedio,
        inversion_ads_total,
        clics_total,
        impresiones_total,
        conversiones_total,
        temperatura_promedio_celsius,
        temperatura_maxima_celsius,
        humedad_porcentaje,
        precipitacion_mm,
        alerta_ola_calor,
        numero_dia_semana,
        mes,
        trimestre,
        es_fin_de_semana,
        es_feriado,
        es_quincena,
        es_fin_mes,
        temporada,
        COALESCE(ventas_lag1, 0),
        COALESCE(ventas_lag7, 0),
        COALESCE(ventas_roll7, cantidad_vendida_total),
        COALESCE(ads_lag1, 0),
        COALESCE(ads_lag3, 0),
        CASE
            WHEN COALESCE(stock_apertura, 0) <= 0 THEN TRUE
            ELSE FALSE
        END AS riesgo_demanda_censurada,
        NOW()
    FROM features
    WHERE fecha IS NOT NULL
      AND id_sku IS NOT NULL;

    -- ========================================================
    -- 7. ML Score Input 2026
    -- Objetivo:
    -- Generar input futuro para todo el año 2026.
    -- Resultado esperado:
    -- 365 días x 3 SKUs = 1095 filas.
    -- ========================================================

    INSERT INTO gold.ml_score_input (
        fecha_objetivo,
        id_sku,
        categoria,
        volumen_litros,
        formato_envase,
        stock_apertura,
        ingresos_almacen,
        precio_unitario_estimado,
        descuento_estimado,
        inversion_ads_planificada,
        clics_estimados,
        impresiones_estimadas,
        temperatura_promedio_estimada,
        temperatura_maxima_estimada,
        humedad_porcentaje_estimada,
        precipitacion_mm_estimada,
        alerta_ola_calor,
        numero_dia_semana,
        mes,
        trimestre,
        es_fin_de_semana,
        es_feriado,
        es_quincena,
        es_fin_mes,
        temporada,
        ventas_lag1,
        ventas_lag7,
        ventas_roll7,
        ads_lag1,
        ads_lag3
    )
    WITH fechas_2026 AS (
        SELECT
            GENERATE_SERIES(
                DATE '2026-01-01',
                DATE '2026-12-31',
                INTERVAL '1 day'
            )::DATE AS fecha_objetivo
    ),

    ultimo_sku AS (
        SELECT
            d.*,
            ROW_NUMBER() OVER (
                PARTITION BY d.id_sku
                ORDER BY d.fecha DESC
            ) AS rn
        FROM gold.ml_dataset d
    ),

    base_sku AS (
        SELECT
            *
        FROM ultimo_sku
        WHERE rn = 1
    ),

    promedios_historicos AS (
        SELECT
            id_sku,
            mes,
            numero_dia_semana,

            AVG(cantidad_vendida_total) AS promedio_ventas,
            AVG(ventas_lag7) AS promedio_ventas_lag7,
            AVG(ventas_roll7) AS promedio_ventas_roll7,

            AVG(precio_unitario_promedio) AS promedio_precio,
            AVG(descuento_total) AS promedio_descuento,

            AVG(inversion_ads_total) AS promedio_ads,
            AVG(clics_total) AS promedio_clics,
            AVG(impresiones_total) AS promedio_impresiones,

            AVG(temperatura_promedio_celsius) AS promedio_temp_prom,
            AVG(temperatura_maxima_celsius) AS promedio_temp_max,
            AVG(humedad_porcentaje) AS promedio_humedad,
            AVG(precipitacion_mm) AS promedio_precipitacion,

            AVG(ads_lag1) AS promedio_ads_lag1,
            AVG(ads_lag3) AS promedio_ads_lag3
        FROM gold.ml_dataset
        GROUP BY
            id_sku,
            mes,
            numero_dia_semana
    )

    SELECT
        f.fecha_objetivo,
        b.id_sku,
        b.categoria,
        b.volumen_litros,
        b.formato_envase,

        -- Stock inicial estimado:
        -- se usa el último stock de cierre conocido como punto de partida.
        b.stock_disponible_cierre AS stock_apertura,

        -- Si no existe plan de reposición futuro, se deja en cero.
        0 AS ingresos_almacen,

        COALESCE(ph.promedio_precio, b.precio_unitario_promedio) AS precio_unitario_estimado,
        COALESCE(ph.promedio_descuento, 0) AS descuento_estimado,

        COALESCE(ph.promedio_ads, 0) AS inversion_ads_planificada,
        COALESCE(ROUND(ph.promedio_clics), 0)::INTEGER AS clics_estimados,
        COALESCE(ROUND(ph.promedio_impresiones), 0)::INTEGER AS impresiones_estimadas,

        COALESCE(ph.promedio_temp_prom, b.temperatura_promedio_celsius) AS temperatura_promedio_estimada,
        COALESCE(ph.promedio_temp_max, b.temperatura_maxima_celsius) AS temperatura_maxima_estimada,
        COALESCE(ph.promedio_humedad, b.humedad_porcentaje) AS humedad_porcentaje_estimada,
        COALESCE(ph.promedio_precipitacion, b.precipitacion_mm) AS precipitacion_mm_estimada,

        CASE
            WHEN COALESCE(ph.promedio_temp_max, b.temperatura_maxima_celsius) >= 28
            THEN TRUE
            ELSE FALSE
        END AS alerta_ola_calor,

        EXTRACT(ISODOW FROM f.fecha_objetivo)::INTEGER AS numero_dia_semana,
        EXTRACT(MONTH FROM f.fecha_objetivo)::INTEGER AS mes,
        EXTRACT(QUARTER FROM f.fecha_objetivo)::INTEGER AS trimestre,

        CASE
            WHEN EXTRACT(ISODOW FROM f.fecha_objetivo)::INTEGER IN (6, 7)
            THEN TRUE
            ELSE FALSE
        END AS es_fin_de_semana,

        CASE
            WHEN TO_CHAR(f.fecha_objetivo, 'MM-DD') IN (
                '01-01',
                '05-01',
                '07-28',
                '07-29',
                '12-25'
            )
            THEN TRUE
            ELSE FALSE
        END AS es_feriado,

        CASE
            WHEN EXTRACT(DAY FROM f.fecha_objetivo)::INTEGER IN (15, 30)
            THEN TRUE
            ELSE FALSE
        END AS es_quincena,

        CASE
            WHEN f.fecha_objetivo =
                 (
                    DATE_TRUNC('month', f.fecha_objetivo)::DATE
                    + INTERVAL '1 month - 1 day'
                 )::DATE
            THEN TRUE
            ELSE FALSE
        END AS es_fin_mes,

        CASE
            WHEN EXTRACT(MONTH FROM f.fecha_objetivo)::INTEGER IN (12, 1, 2, 3)
                THEN 'Verano'
            WHEN EXTRACT(MONTH FROM f.fecha_objetivo)::INTEGER IN (4, 5)
                THEN 'Otoño'
            WHEN EXTRACT(MONTH FROM f.fecha_objetivo)::INTEGER IN (6, 7, 8, 9)
                THEN 'Invierno'
            ELSE 'Primavera'
        END AS temporada,

        COALESCE(ROUND(ph.promedio_ventas), b.cantidad_vendida_total)::INTEGER AS ventas_lag1,
        COALESCE(ROUND(ph.promedio_ventas_lag7), b.ventas_lag7)::INTEGER AS ventas_lag7,
        COALESCE(ph.promedio_ventas_roll7, b.ventas_roll7) AS ventas_roll7,

        COALESCE(ph.promedio_ads_lag1, b.ads_lag1) AS ads_lag1,
        COALESCE(ph.promedio_ads_lag3, b.ads_lag3) AS ads_lag3

    FROM fechas_2026 f
    CROSS JOIN base_sku b
    LEFT JOIN promedios_historicos ph
        ON ph.id_sku = b.id_sku
       AND ph.mes = EXTRACT(MONTH FROM f.fecha_objetivo)::INTEGER
       AND ph.numero_dia_semana = EXTRACT(ISODOW FROM f.fecha_objetivo)::INTEGER;