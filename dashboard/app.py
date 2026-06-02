import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine

DATABASE_URL = st.secrets[postgresql://postgres.qccjpigpazraorfjymzc:5u&9VA*#UtA6FYz@aws-1-us-east-1.pooler.supabase.com:5432/postgres]

engine = create_engine(
    DATABASE_URL
)
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

    return (
        ventas,
        score,
        importancia,
        productos
    )

    st.set_page_config(
    page_title="Retail Agua",
    page_icon="💧",
    layout="wide"
)

st.title(
    "💧 Dashboard Predictivo Retail Agua"
)

sku = st.sidebar.selectbox(
    "📦 SKU",
    sorted(
        score["id_sku"].unique()
    )
)
fecha_inicio = st.sidebar.date_input(
    "Fecha Inicio"
)

fecha_fin = st.sidebar.date_input(
    "Fecha Fin"
)

st.metric(
    "📈 Demanda Pronosticada",
    round(
        score["cantidad_predicha"].sum()
    )
)


st.metric(
    "🚚 Reposición Total",
    round(
        score["cantidad_reponer"].sum()
    )
)

st.metric(
    "⚠ Alertas",
    (
        score[
            score[
                "alerta_compra"
            ] == "COMPRAR"
        ]
        .shape[0]
    )
)

st.metric(
    "📦 Stock Promedio",
    round(
        score[
            "stock_fin"
        ].mean()
    )
)

fig = px.line(
    ...
)

st.dataframe(
    score[
        [
            "id_sku",
            "dias_cobertura",
            "semaforo_stock"
        ]
    ]
)

fig = px.bar(
    importancia.head(10),
    x="importance_value",
    y="feature_name"
)