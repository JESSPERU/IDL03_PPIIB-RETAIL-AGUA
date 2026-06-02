# ==========================================
# SCORE MODEL
# Proyecto Retail Agua
# ==========================================

import pandas as pd
import numpy as np
import joblib

# ==========================================
# 1. CARGAR ARCHIVOS
# ==========================================

modelo = joblib.load(
    "models/modelo_demanda.pkl"
)

score_df = pd.read_csv(
    "data/2.-Tablas Gold/ml_score_input.csv"
)

dim_producto = pd.read_csv(
    "data/2.-Tablas Gold/dim_producto.csv"
)

print("Score input:", score_df.shape)
print("Dim producto:", dim_producto.shape)

# ==========================================
# 2. PREPARAR VARIABLES
# ==========================================

score_model = score_df.copy()

score_model = score_model.rename(
    columns={
        "precio_unitario_estimado":
            "precio_unitario_promedio",

        "descuento_estimado":
            "descuento_total",

        "inversion_ads_planificada":
            "inversion_ads_total",

        "clics_estimados":
            "clics_total",

        "impresiones_estimadas":
            "impresiones_total",

        "temperatura_promedio_estimada":
            "temperatura_promedio_celsius",

        "temperatura_maxima_estimada":
            "temperatura_maxima_celsius",

        "humedad_porcentaje_estimada":
            "humedad_porcentaje",

        "precipitacion_mm_estimada":
            "precipitacion_mm"
    }
)

score_model["conversiones_total"] = 0
score_model["porcentaje_descuento_promedio"] = 0
score_model["stock_minimo"] = 0
score_model["riesgo_demanda_censurada"] = False

# ==========================================
# 3. ORDENAR COLUMNAS
# ==========================================

columnas_modelo = list(
    modelo.feature_names_in_
)

score_model = score_model[
    columnas_modelo
]

# ==========================================
# 4. PREDICCIÓN
# ==========================================

predicciones = modelo.predict(
    score_model
)

score_df[
    "cantidad_predicha"
] = predicciones

# ==========================================
# 5. DATOS LOGÍSTICOS
# ==========================================

score_df = score_df.merge(
    dim_producto[
        [
            "id_sku",
            "stock_seguridad",
            "lead_time_dias"
        ]
    ],
    on="id_sku",
    how="left"
)

score_df["fecha_objetivo"] = pd.to_datetime(
    score_df["fecha_objetivo"]
)

score_df = score_df.sort_values(
    [
        "id_sku",
        "fecha_objetivo"
    ]
)

# ==========================================
# 6. SIMULACIÓN INVENTARIO
# ==========================================

resultado = []

for sku in score_df["id_sku"].unique():

    sku_df = (
        score_df[
            score_df["id_sku"] == sku
        ]
        .copy()
        .sort_values(
            "fecha_objetivo"
        )
    )

    stock_seguridad = (
        sku_df[
            "stock_seguridad"
        ]
        .iloc[0]
    )

    lead_time = (
        sku_df[
            "lead_time_dias"
        ]
        .iloc[0]
    )

    # Inventario inicial
    stock_actual = (
        stock_seguridad * 2
    )

    ordenes_pendientes = []

    for _, row in sku_df.iterrows():

        fecha = row["fecha_objetivo"]

        llegadas = [
            x
            for x in ordenes_pendientes
            if x["fecha"] <= fecha
        ]

        for llegada in llegadas:

            stock_actual += (
                llegada["cantidad"]
            )

        ordenes_pendientes = [
            x
            for x in ordenes_pendientes
            if x["fecha"] > fecha
        ]

        demanda = (
            row["cantidad_predicha"]
        )

        stock_inicio = stock_actual

        stock_fin = max(
            stock_actual - demanda,
            0
        )

        punto_reorden = (
            stock_seguridad
            +
            (
                demanda
                * lead_time
            )
        )

        stock_objetivo = (
            stock_seguridad
            +
            (
                demanda * lead_time
            )
            +
            demanda
        )

        cantidad_reponer = 0

        fecha_llegada = None

        alerta = "OK"

        if stock_fin < (
            punto_reorden * 0.90
        ):

            cantidad_reponer = (
                stock_objetivo
                - stock_fin
            )

            fecha_llegada = (
                fecha
                +
                pd.Timedelta(
                    days=lead_time
                )
            )

            ordenes_pendientes.append(
                {
                    "fecha":
                        fecha_llegada,

                    "cantidad":
                        cantidad_reponer
                }
            )

            alerta = "COMPRAR"

        dias_cobertura = (
            max(stock_fin, 0)
            / demanda
            if demanda > 0
            else 0
        )

        resultado.append({

            "fecha_objetivo":
                fecha,

            "id_sku":
                sku,

            "cantidad_predicha":
                round(demanda, 2),

            "stock_inicio":
                round(stock_inicio, 2),

            "stock_fin":
                round(stock_fin, 2),

            "riesgo_quiebre_stock":
                stock_fin == 0,

            "stock_seguridad":
                stock_seguridad,

            "stock_objetivo":
                round(stock_objetivo, 2),

            "lead_time_dias":
                lead_time,

            "punto_reorden":
                round(punto_reorden, 2),

            "cantidad_reponer":
                round(cantidad_reponer, 2),

            "fecha_llegada":
                fecha_llegada,

            "dias_cobertura":
                round(dias_cobertura, 2),

            "alerta_compra":
                alerta,

            "comentario_negocio":
                (
                    "Generar orden de compra"
                    if alerta == "COMPRAR"
                    else "Inventario suficiente"
                )
        })

        stock_actual = stock_fin

# ==========================================
# 7. OUTPUT FINAL
# ==========================================

output_v2 = pd.DataFrame(
    resultado
)

output_v2["semaforo_stock"] = np.select(

    [
        output_v2["dias_cobertura"] <= 2,

        (
            (output_v2["dias_cobertura"] > 2)
            &
            (output_v2["dias_cobertura"] <= 4)
        ),

        (
            (output_v2["dias_cobertura"] > 4)
            &
            (output_v2["dias_cobertura"] <= 10)
        ),

        output_v2["dias_cobertura"] > 10
    ],

    [
        "ROJO",
        "AMARILLO",
        "VERDE",
        "AZUL"
    ],

    default="VERDE"
)

# ==========================================
# 8. EXPORTAR
# ==========================================

output_v2.to_csv(
    "data/2.-Tablas Gold/ml_score_output.csv",
    index=False
)

print(
    "ml_score_output.csv generado correctamente."
)