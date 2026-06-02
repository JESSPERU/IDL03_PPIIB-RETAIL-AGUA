# ==========================================
# DASHBOARD RETAIL AGUA
# Proyecto Productivo II
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Retail Agua",
    page_icon="💧",
    layout="wide"
)

# ==========================================
# CONEXIÓN SUPABASE
# ==========================================

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL
)

# ==========================================
# CARGA DE DATOS
# ==========================================

@st.cache_data
def load_data():

    ventas = pd.read_sql(
        """
        SELECT *
        FROM gold.fact_ventas_diarias
        """,
        engine
    )

    score = pd.read_sql(
        """
        SELECT *
        FROM gold.ml_score_output
        """,
        engine
    )

    importancia = pd.read_sql(
        """
        SELECT *
        FROM gold.ml_feature_importance
        """,
        engine
    )

    productos = pd.read_sql(
        """
        SELECT *
        FROM gold.dim_producto
        """,
        engine
    )

    return ventas, score, importancia, productos


ventas, score, importancia, productos = load_data()

# ==========================================
# CONVERSIONES
# ==========================================

if "fecha_objetivo" in score.columns:
    score["fecha_objetivo"] = pd.to_datetime(
        score["fecha_objetivo"]
    )

# ==========================================
# TÍTULO
# ==========================================

st.title(
    "💧 Dashboard Predictivo Retail Agua"
)

st.markdown(
    """
    Sistema de monitoreo de demanda,
    inventarios y alertas de reposición
    basado en la Capa Gold de Supabase.
    """
)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Filtros")

sku = st.sidebar.selectbox(
    "📦 SKU",
    ["Todos"] +
    sorted(
        score["id_sku"].unique()
    ).tolist()
)

fecha_inicio = st.sidebar.date_input(
    "📅 Fecha inicio",
    score["fecha_objetivo"].min()
)

fecha_fin = st.sidebar.date_input(
    "📅 Fecha fin",
    score["fecha_objetivo"].max()
)

# ==========================================
# FILTROS
# ==========================================

score_filtrado = score.copy()

score_filtrado = score_filtrado[
    (
        score_filtrado["fecha_objetivo"]
        >= pd.to_datetime(fecha_inicio)
    )
    &
    (
        score_filtrado["fecha_objetivo"]
        <= pd.to_datetime(fecha_fin)
    )
]

if sku != "Todos":

    score_filtrado = score_filtrado[
        score_filtrado["id_sku"] == sku
    ]

# ==========================================
# KPIs
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📈 Demanda Pronosticada",
        f"{score_filtrado['cantidad_predicha'].sum():,.0f}"
    )

with col2:

    st.metric(
        "🚚 Reposición Total",
        f"{score_filtrado['cantidad_reponer'].sum():,.0f}"
    )

with col3:

    st.metric(
        "⚠ Alertas Compra",
        score_filtrado[
            score_filtrado[
                "alerta_compra"
            ] == "COMPRAR"
        ].shape[0]
    )

with col4:

    st.metric(
        "📦 Stock Promedio",
        f"{score_filtrado['stock_fin'].mean():,.0f}"
    )

# ==========================================
# DEMANDA PROYECTADA
# ==========================================

st.subheader(
    "📈 Demanda Pronosticada"
)

fig_demanda = px.line(
    score_filtrado,
    x="fecha_objetivo",
    y="cantidad_predicha",
    color="id_sku",
    markers=True,
    title="Proyección de Demanda"
)

st.plotly_chart(
    fig_demanda,
    use_container_width=True
)

# ==========================================
# INVENTARIO
# ==========================================

st.subheader(
    "📦 Inventario Proyectado"
)

fig_stock = px.line(
    score_filtrado,
    x="fecha_objetivo",
    y=[
        "stock_fin",
        "stock_seguridad"
    ],
    title="Stock Fin vs Stock Seguridad"
)

st.plotly_chart(
    fig_stock,
    use_container_width=True
)

# ==========================================
# FEATURE IMPORTANCE
# ==========================================

st.subheader(
    "🧠 Variables más importantes"
)

top_features = importancia.head(10)

fig_importancia = px.bar(
    top_features,
    x="importance_value",
    y="feature_name",
    orientation="h",
    title="Top 10 Variables del Modelo"
)

st.plotly_chart(
    fig_importancia,
    use_container_width=True
)

# ==========================================
# SEMÁFORO
# ==========================================

st.subheader(
    "🚦 Semáforo de Stock"
)

st.dataframe(
    score_filtrado[
        [
            "fecha_objetivo",
            "id_sku",
            "dias_cobertura",
            "semaforo_stock",
            "alerta_compra",
            "comentario_negocio"
        ]
    ],
    use_container_width=True
)

# ==========================================
# ALERTAS
# ==========================================

st.subheader(
    "⚠ Productos con Alerta"
)

alertas = score_filtrado[
    score_filtrado[
        "alerta_compra"
    ] == "COMPRAR"
]

st.dataframe(
    alertas[
        [
            "fecha_objetivo",
            "id_sku",
            "cantidad_reponer",
            "fecha_llegada",
            "comentario_negocio"
        ]
    ],
    use_container_width=True
)

# ==========================================
# TABLA DETALLE
# ==========================================

st.subheader(
    "📋 Detalle Completo"
)

st.dataframe(
    score_filtrado,
    use_container_width=True
)