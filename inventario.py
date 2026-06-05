import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="CONTROL DE INVENTARIO DE RETAIL DE AGUA",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ RUTAS CORREGIDAS PARA SIEMPRE (PC: data / GITHUB: datos)
RUTA_PROYECTO = "."
CARPETA = "data" if os.path.exists("data") else "datos"
RUTA_GOLD = os.path.join(RUTA_PROYECTO, CARPETA, "2.-Tablas Gold")
RUTA_LOGO = os.path.join(RUTA_PROYECTO, "agua premiun.png")

# ---------------- ESTILOS ----------------
st.markdown("""
<style>
* { font-family: 'Segoe UI', Roboto, sans-serif; }
.stApp { background: linear-gradient(120deg, #e0f2fe 0%, #b9e0f9 50%, #7cc6f8 100%); }
h1, h2, h3 { color: #0c4a6e; font-weight: 600; }
.stCard, div[data-testid="stMetricValue"] { background-color: rgba(255,255,255,0.85); border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
[data-testid="stSidebar"] { background-color: rgba(255,255,255,0.9); }
</style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS (SIN ERRORES) ----------------
@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos():
    try:
        # Cargar archivos
        dp = pd.read_csv(os.path.join(RUTA_GOLD, "dim_producto.csv"))
        dv = pd.read_csv(os.path.join(RUTA_GOLD, "fact_ventas_diarias.csv"))
        di = pd.read_csv(os.path.join(RUTA_GOLD, "fact_inventario.csv"))

        # ✅ CORREGIR NOMBRES DE COLUMNAS (SI NO COINCIDEN)
        renombrar = {
            'descripcion': ['producto', 'nombre', 'Descripcion', 'Producto'],
            'Precio Unitario': ['precio', 'precio_unitario', 'Precio', 'VALOR_VENTA'],
            'Costo Unitario': ['costo', 'costo_unitario', 'Costo', 'VALOR_COSTO']
        }
        for columna, alternativas in renombrar.items():
            if columna not in dp.columns:
                for alt in alternativas:
                    if alt in dp.columns:
                        dp = dp.rename(columns={alt: columna})
                        break

        # ✅ CREAR COLUMNA DE RENTABILIDAD SI NO EXISTE
        if 'Rentabilidad %' not in dp.columns:
            if 'Precio Unitario' in dp.columns and 'Costo Unitario' in dp.columns:
                dp['Rentabilidad %'] = round(((dp['Precio Unitario'] - dp['Costo Unitario']) / dp['Precio Unitario']) * 100, 2)
            else:
                dp['Rentabilidad %'] = 0

        return dp, dv, di

    except Exception as e:
        st.error(f"❌ ERROR: {str(e)}")
        st.info(f"📂 Buscando en: {RUTA_GOLD}")
        return None, None, None

# Ejecutar
dim_producto, fact_ventas, fact_inventario = cargar_datos()
if dim_producto is None: st.stop()

# ---------------- MENÚ ----------------
with st.sidebar:
    if os.path.exists(RUTA_LOGO): st.image(RUTA_LOGO, width=150)
    st.title("Panel de Gestión")
    opcion = st.radio("Navegación", ["Inicio", "Análisis de Ventas", "Inventario", "Modelos IA", "Datos"])
    st.markdown("---")
    st.subheader("🔍 Filtros")
    fecha_min = pd.to_datetime(fact_ventas['Fecha']).min() if 'Fecha' in fact_ventas.columns else "2024-01-01"
    fecha_max = pd.to_datetime(fact_ventas['Fecha']).max() if 'Fecha' in fact_ventas.columns else "2024-12-31"
    periodo = st.date_input("Periodo", [fecha_min, fecha_max])
    productos = ["Todos"] + list(dim_producto.get('descripcion', dim_producto.columns[0]).unique())
    producto_sel = st.selectbox("Producto", productos)

# ---------------- PÁGINAS ----------------
if opcion == "Inicio":
    st.header("💧 BIENVENIDO - CONTROL DE INVENTARIO")
    st.success("✅ Sistema conectado correctamente")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Productos", len(dim_producto))
    with c2: st.metric("Ventas", len(fact_ventas))
    with c3: st.metric("Inventario", len(fact_inventario))

elif opcion == "Análisis de Ventas":
    st.header("📈 ANÁLISIS DE VENTAS")
    consulta = st.radio("", ["Precios", "Ganancias", "Rentabilidad", "Devoluciones"], horizontal=True)

    df = dim_producto.copy()
    if producto_sel != "Todos":
        col_nombre = 'descripcion' if 'descripcion' in df.columns else df.columns[0]
        df = df[df[col_nombre] == producto_sel]

    if consulta == "Rentabilidad":
        st.subheader("📊 Rentabilidad (%)")
        col_x = 'descripcion' if 'descripcion' in df.columns else df.columns[0]
        if 'Rentabilidad %' in df.columns:
            fig = px.bar(df, x=col_x, y='Rentabilidad %', color='Rentabilidad %',
                         color_continuous_scale="RdYlGn", template="plotly_white",
                         labels={col_x:"Producto"}, title="Rentabilidad por Producto")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de rentabilidad disponibles")

    elif consulta == "Precios":
        st.subheader("💰 Precio Unitario")
        col_x = 'descripcion' if 'descripcion' in df.columns else df.columns[0]
        col_y = 'Precio Unitario' if 'Precio Unitario' in df.columns else df.columns[1]
        fig = px.bar(df, x=col_x, y=col_y, template="plotly_white", title="Precios Unitarios")
        st.plotly_chart(fig, use_container_width=True)

    elif consulta == "Ganancias":
        st.subheader("💵 Ganancias")
        if 'Precio Unitario' in df.columns and 'Costo Unitario' in df.columns:
            df['Ganancia'] = df['Precio Unitario'] - df['Costo Unitario']
            col_x = 'descripcion' if 'descripcion' in df.columns else df.columns[0]
            fig = px.bar(df, x=col_x, y='Ganancia', color='Ganancia', template="plotly_white", title="Ganancia por Producto")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Faltan datos de precio/costo")

    elif consulta == "Devoluciones":
        st.info("📉 Módulo de devoluciones en construcción")

elif opcion == "Inventario":
    st.header("📦 INVENTARIO")
    st.dataframe(fact_inventario, use_container_width=True)

elif opcion == "Modelos IA":
    st.header("🤖 INTELIGENCIA ARTIFICIAL")
    st.info("🚀 Predicción de demanda lista para integrar")

elif opcion == "Datos":
    st.header("🔎 EXPLORADOR DE DATOS")
    tab1,tab2,tab3 = st.tabs(["Productos","Ventas","Inventario"])
    with tab1: st.dataframe(dim_producto, use_container_width=True)
    with tab2: st.dataframe(fact_ventas, use_container_width=True)
    with tab3: st.dataframe(fact_inventario, use_container_width=True)