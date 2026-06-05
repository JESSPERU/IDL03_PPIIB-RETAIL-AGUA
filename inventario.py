import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- CONFIGURACIÓN DE LA PÁGINA ----------------
st.set_page_config(
    page_title="CONTROL DE INVENTARIO DE RETAIL DE AGUA",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ SOLUCIÓN DEL PROBLEMA: DETECTA SI ES "data" O "datos"
RUTA_PROYECTO = "."

# Busca automáticamente cuál nombre de carpeta existe
if os.path.exists(os.path.join(RUTA_PROYECTO, "data")):
    CARPETA_DATOS = "data"
else:
    CARPETA_DATOS = "datos"

# Ruta final, ahora sí correcta en ambos lados
RUTA_GOLD = os.path.join(RUTA_PROYECTO, CARPETA_DATOS, "2.-Tablas Gold")
RUTA_LOGO = os.path.join(RUTA_PROYECTO, "agua premiun.png")

# ---------------- ESTILOS Y FONDO ----------------
st.markdown("""
<style>
* { font-family: 'Segoe UI', Roboto, sans-serif; }

/* FONDO PRINCIPAL LLAMATIVO (ACORDE A AGUA) */
.stApp {
    background: linear-gradient(120deg, #e0f2fe 0%, #b9e0f9 50%, #7cc6f8 100%);
}

/* TÍTULOS */
h1, h2, h3 {
    color: #0c4a6e;
    font-weight: 600;
}

/* TARJETAS DE CONTENIDO */
.stCard, div[data-testid="stMetricValue"] {
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.9);
}
</style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    try:
        # Rutas ahora 100% correctas
        dim_producto = pd.read_csv(os.path.join(RUTA_GOLD, "dim_producto.csv"))
        fact_ventas = pd.read_csv(os.path.join(RUTA_GOLD, "fact_ventas_diarias.csv"))
        fact_inventario = pd.read_csv(os.path.join(RUTA_GOLD, "fact_inventario.csv"))

        # ✅ CALCULA LA COLUMNA SI NO EXISTE
        if 'Rentabilidad %' not in dim_producto.columns:
            dim_producto['Rentabilidad %'] = round(
                ((dim_producto['Precio Unitario'] - dim_producto['Costo Unitario']) / dim_producto['Precio Unitario']) * 100,
                2
            )

        return dim_producto, fact_ventas, fact_inventario

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        st.info(f"🔎 Buscando en carpeta: {RUTA_GOLD}")
        return None, None, None

# Ejecutar carga
dim_producto, fact_ventas, fact_inventario = cargar_datos()

# Verificar que los datos se cargaron
if dim_producto is None:
    st.stop()

# ---------------- MENÚ LATERAL ----------------
with st.sidebar:
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=150)
    else:
        st.warning("⚠️ Logo no encontrado")

    st.title("Panel de Gestión")
    opcion = st.radio(
        "Navegación",
        ["Inicio", "Análisis de Ventas", "Inventario y Recursos", "Modelos IA / Predicción", "Datos Interactivos"]
    )

    st.markdown("---")
    st.subheader("🔍 Filtros Generales")

    # Filtro de fecha
    fecha_min = pd.to_datetime(fact_ventas['Fecha']).min()
    fecha_max = pd.to_datetime(fact_ventas['Fecha']).max()
    periodo = st.date_input("Periodo de análisis", [fecha_min, fecha_max])

    # Filtro de producto
    lista_productos = ["Todos"] + dim_producto['descripcion'].unique().tolist()
    producto_sel = st.selectbox("Producto / Tipo", lista_productos)

# ---------------- PÁGINA: ANÁLISIS DE VENTAS ----------------
if opcion == "Análisis de Ventas":
    st.header("📈 Análisis de Ventas")

    tipo_consulta = st.radio(
        "Tipo de Consulta:",
        ["Precios Unitarios", "Ganancias por Producto", "Pérdidas / Devoluciones", "Rentabilidad"],
        horizontal=True
    )

    # Filtrar datos
    df_filtrado = dim_producto.copy()
    if producto_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['descripcion'] == producto_sel]

    # ✅ GRÁFICO CORREGIDO
    if tipo_consulta == "Rentabilidad":
        st.subheader("📊 Rentabilidad por Producto (%)")
        columnas_nec = ['descripcion', 'Rentabilidad %']
        if all(col in df_filtrado.columns for col in columnas_nec):
            fig = px.bar(
                df_filtrado,
                x="descripcion",
                y="Rentabilidad %",
                color="Rentabilidad %",
                color_continuous_scale="RdYlGn",
                title="Rentabilidad (%) por Producto",
                labels={"descripcion": "Producto", "Rentabilidad %": "Porcentaje (%)"},
                template="plotly_white"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Faltan columnas necesarias")

    elif tipo_consulta == "Precios Unitarios":
        st.subheader("💰 Precio Unitario de Productos")
        fig = px.bar(
            df_filtrado,
            x="descripcion",
            y="Precio Unitario",
            color="Categoría",
            title="Precios Unitarios",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_consulta == "Ganancias por Producto":
        st.subheader("💵 Ganancias Totales")
        df_filtrado['Ganancia Total'] = (df_filtrado['Precio Unitario'] - df_filtrado['Costo Unitario']) * 100
        fig = px.bar(
            df_filtrado,
            x="descripcion",
            y="Ganancia Total",
            color="Ganancia Total",
            color_continuous_scale="Blues",
            title="Ganancias Estimadas",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_consulta == "Pérdidas / Devoluciones":
        st.subheader("📉 Pérdidas y Devoluciones")
        st.info("📌 Módulo en desarrollo")

# ---------------- OTRAS PÁGINAS ----------------
elif opcion == "Inicio":
    st.header("💧 Bienvenido al Sistema de Gestión")
    st.success("✅ Conexión exitosa con todos los datos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Productos", len(dim_producto))
    with col2:
        st.metric("Registros Ventas", len(fact_ventas))
    with col3:
        st.metric("Ítems Inventario", len(fact_inventario))

elif opcion == "Inventario y Recursos":
    st.header("📦 Control de Inventario")
    st.dataframe(fact_inventario.head(20), use_container_width=True)

elif opcion == "Modelos IA / Predicción":
    st.header("🤖 Predicción de Demanda")
    st.info("🚀 Módulo de inteligencia artificial listo para integrar")

elif opcion == "Datos Interactivos":
    st.header("🔎 Explorador de Datos")
    tab1, tab2, tab3 = st.tabs(["Productos", "Ventas", "Inventario"])
    with tab1:
        st.dataframe(dim_producto, use_container_width=True)
    with tab2:
        st.dataframe(fact_ventas, use_container_width=True)
    with tab3:
        st.dataframe(fact_inventario, use_container_width=True)