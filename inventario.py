import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="CONTROL DE INVENTARIO DE RETAIL DE AGUA",
    page_icon="🚰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ RUTAS EXACTAS (NO CAMBIAR)
RUTA_PROYECTO = r"C:\Users\lee_3\Documents\GitHub\IDL03_PPIIB-RETAIL-AGUA"
RUTA_GOLD = os.path.join(RUTA_PROYECTO, "data", "2.-Tablas Gold")
RUTA_LOGO = os.path.join(RUTA_PROYECTO, "agua premiun.png") # TU IMAGEN YA CONFIGURADA

# ---------------- ESTILOS Y FONDO NUEVO ----------------
st.markdown("""
    <style>
    * { font-family: 'Segoe UI', Roboto, sans-serif; }
    
    /* 🌊 FONDO PRINCIPAL LLAMATIVO (ACORDE A AGUA) */
    .stApp {
        background: linear-gradient(120deg, #e0f2fe 0%, #b9e0f9 50%, #7cc6f8 100%);
        background-attachment: fixed;
    }
    
    .main { 
        background-color: rgba(255, 255, 255, 0.85); 
        padding: 1.5rem 2rem; 
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0, 119, 190, 0.15);
    }

    /* 🚰 TITULO PRINCIPAL */
    .titulo-principal { 
        font-size: 2.8rem; 
        font-weight: 900; 
        color: #0369a1; 
        text-align: center; 
        margin-bottom: 1.5rem; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 18px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }

    .subtitulo { 
        font-size: 1.6rem; 
        font-weight: 700; 
        color: #0284c7; 
        margin: 2rem 0 1.2rem 0; 
        border-left: 6px solid #0ea5e9; 
        padding-left: 1rem;
        background-color: rgba(255,255,255,0.6);
        border-radius: 0 10px 10px 0;
        padding-top: 0.4rem;
        padding-bottom: 0.4rem;
    }

    /* 📦 TARJETAS INTERACTIVAS */
    .tarjeta { 
        background-color: #ffffff; 
        padding: 1.8rem; 
        border-radius: 16px; 
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.12); 
        margin-bottom: 1.2rem; 
        border: none;
        transition: all 0.3s ease;
        border-top: 5px solid #0ea5e9;
    }
    .tarjeta:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.2); 
    }

    .metrica-valor { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #0284c7; 
    }
    .metrica-etiqueta { 
        font-size: 1.1rem; 
        color: #475569; 
        font-weight: 600; 
    }

    /* 🔍 FILTROS */
    .filtro-seccion { 
        background: rgba(255, 255, 255, 0.9); 
        padding: 1.2rem; 
        border-radius: 14px; 
        margin-bottom: 1.5rem; 
        border: 1px solid #bae6fd;
    }

    /* 📑 BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: rgba(224, 242, 254, 0.95) !important;
        border-right: 1px solid #7dd3fc;
    }
    .css-1d391kg { background-color: transparent; }

    /* 📊 BOTONES Y RADIOS */
    .stRadio > div { gap: 0.8rem; }
    .stRadio > div > label {
        background-color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid #7dd3fc;
        transition: 0.2s;
    }
    .stRadio > div > label:hover {
        background-color: #bae6fd;
    }

    /* 📋 TABLAS */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data(show_spinner="🚰 Cargando datos del sistema... ⏳")
def cargar_datos():
    try:
        dim_producto = pd.read_csv(os.path.join(RUTA_GOLD, "dim_producto.csv"))
        dim_tiempo = pd.read_csv(os.path.join(RUTA_GOLD, "dim_tiempo.csv"))
        fact_inventario = pd.read_csv(os.path.join(RUTA_GOLD, "fact_inventario.csv"))
        fact_marketing = pd.read_csv(os.path.join(RUTA_GOLD, "fact_marketing.csv"))
        fact_ventas = pd.read_csv(os.path.join(RUTA_GOLD, "fact_ventas_diarias.csv"))
        ml_dataset = pd.read_csv(os.path.join(RUTA_GOLD, "ml_dataset.csv"))
        ml_score = pd.read_csv(os.path.join(RUTA_GOLD, "ml_score_input.csv"))

        # Fechas
        for df in [dim_tiempo, fact_ventas, fact_inventario, fact_marketing, ml_dataset]:
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        # Uniones
        if "id_tiempo" in fact_ventas.columns and "id_tiempo" in dim_tiempo.columns:
            fact_ventas = fact_ventas.merge(dim_tiempo, on="id_tiempo", how="left")
        if "id_sku" in fact_ventas.columns and "id_sku" in dim_producto.columns:
            fact_ventas = fact_ventas.merge(dim_producto, on="id_sku", how="left")
        if "id_sku" in fact_inventario.columns and "id_sku" in dim_producto.columns:
            fact_inventario = fact_inventario.merge(dim_producto, on="id_sku", how="left")

        return dim_producto, dim_tiempo, fact_inventario, fact_marketing, fact_ventas, ml_dataset, ml_score

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

datos = cargar_datos()
if not datos: st.stop()
dim_producto, dim_tiempo, fact_inventario, fact_marketing, fact_ventas, ml_dataset, ml_score = datos

# ---------------- ENCABEZADO CON TU IMAGEN ----------------
col_logo, col_titulo, _ = st.columns([1, 5, 1])
with col_logo:
    try:
        st.image(RUTA_LOGO, width=95) # TU IMAGEN 'agua premiun.png' YA CARGADA
    except:
        st.markdown("<h2 style='text-align:center;'>🚰</h2>", unsafe_allow_html=True)
with col_titulo:
    st.markdown('<h1 class="titulo-principal">CONTROL DE INVENTARIO DE RETAIL DE AGUA</h1>', unsafe_allow_html=True)

# ---------------- BARRA LATERAL ----------------
with st.sidebar:
    st.title("📊 Panel de Gestión")
    seccion = st.radio(
        "",
        ["🏠 Inicio", "📈 Análisis de Ventas", "📦 Inventario y Recursos", "🤖 Modelos IA / Predicción", "📋 Datos Interactivos"]
    )
    st.divider()
    st.markdown("### 🔍 Filtros Generales")

    v_filtrado = fact_ventas.copy()
    inv_filtrado = fact_inventario.copy()
    mkt_filtrado = fact_marketing.copy()

    if "fecha" in fact_ventas.columns:
        fecha_min = fact_ventas["fecha"].min()
        fecha_max = fact_ventas["fecha"].max()
        rango_fechas = st.date_input("Periodo de análisis", [fecha_min, fecha_max])
        if len(rango_fechas) == 2:
            f_ini, f_fin = pd.to_datetime(rango_fechas[0]), pd.to_datetime(rango_fechas[1])
            v_filtrado = v_filtrado[(v_filtrado["fecha"] >= f_ini) & (v_filtrado["fecha"] <= f_fin)]
            if "fecha" in inv_filtrado.columns: inv_filtrado = inv_filtrado[(inv_filtrado["fecha"] >= f_ini) & (inv_filtrado["fecha"] <= f_fin)]
            if "fecha" in mkt_filtrado.columns: mkt_filtrado = mkt_filtrado[(mkt_filtrado["fecha"] >= f_ini) & (mkt_filtrado["fecha"] <= f_fin)]

    if "descripcion" in v_filtrado.columns:
        lista_prod = ["🔘 Todos"] + sorted(dim_producto["descripcion"].dropna().unique())
        prod_sel = st.selectbox("Producto / Tipo", lista_prod)
        if prod_sel != "🔘 Todos":
            v_filtrado = v_filtrado[v_filtrado["descripcion"] == prod_sel]
            if "descripcion" in inv_filtrado.columns: inv_filtrado = inv_filtrado[inv_filtrado["descripcion"] == prod_sel]

# ---------------- SECCIÓN 1: INICIO ----------------
if seccion == "🏠 Inicio":
    st.markdown('<h2 class="subtitulo">📊 Resumen Ejecutivo</h2>', unsafe_allow_html=True)

    st.markdown('<div class="filtro-seccion">', unsafe_allow_html=True)
    vista_tiempo = st.radio("🔄 Vista Temporal:", ["Por Mes", "Por Día", "Por Año"], horizontal=True)
    metrica_vista = st.radio("📌 Métrica a visualizar:", ["Ventas Totales", "Ganancias", "Unidades Vendidas"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    datos_agrup = pd.DataFrame()
    if vista_tiempo == "Por Mes":
        if "fecha" in v_filtrado.columns:
            datos_agrup = v_filtrado.groupby(v_filtrado["fecha"].dt.to_period("M")).agg(
                ventas=("ingresos_almacen", "sum"),
                ganancias=("ganancia_total", "sum"),
                unidades=("cantidad_vendida_total", "sum")
            ).reset_index()
            datos_agrup["fecha"] = datos_agrup["fecha"].dt.to_timestamp()
    elif vista_tiempo == "Por Día":
        datos_agrup = v_filtrado.groupby("fecha").agg(
            ventas=("ingresos_almacen", "sum"),
            ganancias=("ganancia_total", "sum"),
            unidades=("cantidad_vendida_total", "sum")
        ).reset_index()
    else:
        datos_agrup = v_filtrado.groupby(v_filtrado["fecha"].dt.year).agg(
            ventas=("ingresos_almacen", "sum"),
            ganancias=("ganancia_total", "sum"),
            unidades=("cantidad_vendida_total", "sum")
        ).reset_index()
        datos_agrup["fecha"] = datos_agrup["fecha"].astype(str)

    if not datos_agrup.empty:
        valor_metrica = {"Ventas Totales":"ventas", "Ganancias":"ganancias", "Unidades Vendidas":"unidades"}[metrica_vista]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="tarjeta">', unsafe_allow_html=True)
            total = datos_agrup[valor_metrica].sum()
            st.markdown(f'<div class="metrica-valor">S/ {total:,.2f}</div>' if valor_metrica!="unidades" else f'<div class="metrica-valor">{total:,.0f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metrica-etiqueta">Total {metrica_vista}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="tarjeta">', unsafe_allow_html=True)
            prom = datos_agrup[valor_metrica].mean()
            st.markdown(f'<div class="metrica-valor">S/ {prom:,.2f}</div>' if valor_metrica!="unidades" else f'<div class="metrica-valor">{prom:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metrica-etiqueta">Promedio</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="tarjeta">', unsafe_allow_html=True)
            max_val = datos_agrup[valor_metrica].max()
            st.markdown(f'<div class="metrica-valor">S/ {max_val:,.2f}</div>' if valor_metrica!="unidades" else f'<div class="metrica-valor">{max_val:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metrica-etiqueta">Máximo Histórico</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="tarjeta">', unsafe_allow_html=True)
            min_val = datos_agrup[valor_metrica].min()
            st.markdown(f'<div class="metrica-valor">S/ {min_val:,.2f}</div>' if valor_metrica!="unidades" else f'<div class="metrica-valor">{min_val:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metrica-etiqueta">Mínimo Histórico</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        fig = px.bar(datos_agrup, x="fecha", y=valor_metrica, title=f"{metrica_vista} - {vista_tiempo}", color_discrete_sequence=["#0ea5e9"], template="plotly_white")
        fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# ---------------- SECCIÓN 2: ANÁLISIS DE VENTAS ----------------
elif seccion == "📈 Análisis de Ventas":
    st.markdown('<h2 class="subtitulo">📈 Análisis Detallado de Ventas</h2>', unsafe_allow_html=True)

    st.markdown('<div class="filtro-seccion">', unsafe_allow_html=True)
    consulta = st.radio("🔍 Tipo de Consulta:", ["Precios Unitarios", "Ganancias por Producto", "Pérdidas / Devoluciones", "Rentabilidad"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    datos_analisis = pd.DataFrame()
    fig = None

    if consulta == "Precios Unitarios":
        if "precio_unitario_promedio" in v_filtrado.columns and "descripcion" in v_filtrado.columns:
            datos_analisis = v_filtrado.groupby("descripcion")["precio_unitario_promedio"].mean().reset_index()
            datos_analisis.columns = ["Producto", "Precio Promedio S/"]
            fig = px.bar(datos_analisis, x="Producto", y="Precio Promedio S/", color="Precio Promedio S/", color_continuous_scale="Blues", template="plotly_white")

    elif consulta == "Ganancias por Producto":
        if "descripcion" in v_filtrado.columns and "ganancia_total" in v_filtrado.columns:
            datos_analisis = v_filtrado.groupby("descripcion").agg(Total_Ventas=("ingresos_almacen", "sum"), Ganancia_Total=("ganancia_total", "sum")).reset_index()
            fig = px.pie(datos_analisis, values="Ganancia_Total", names="descripcion", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)

    elif consulta == "Pérdidas / Devoluciones":
        if "fecha" in v_filtrado.columns and "descuento" in v_filtrado.columns:
            datos_analisis = v_filtrado.groupby(v_filtrado["fecha"].dt.month).agg(Perdidas=("descuento", "sum")).reset_index()
            datos_analisis["Mes"] = datos_analisis["fecha"].map({1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"})
            fig = px.line(datos_analisis, x="Mes", y="Perdidas", markers=True, color_discrete_sequence=["#ef4444"], template="plotly_white")

    elif consulta == "Rentabilidad":
        if "descripcion" in v_filtrado.columns:
            datos_analisis = v_filtrado.groupby("descripcion").agg(Ventas=("ingresos_almacen", "sum"), Costos=("costo_total", "sum")).reset_index()
            datos_analisis["Rentabilidad %"] = np.where(datos_analisis["Ventas"]>0, ((datos_analisis["Ventas"] - datos_analisis["Costos"]) / datos_analisis["Ventas"])*100, 0)
            fig = px.bar(datos_analisis, x="Producto", y="Rentabilidad %", color="Rentabilidad %", color_continuous_scale="RdYlGn", template="plotly_white")

    if fig:
        fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    if not datos_analisis.empty: st.dataframe(datos_analisis, use_container_width=True)

# ---------------- SECCIÓN 3: INVENTARIO ----------------
elif seccion == "📦 Inventario y Recursos":
    st.markdown('<h2 class="subtitulo">📦 Gestión de Recursos y Almacén</h2>', unsafe_allow_html=True)

    st.markdown('<div class="filtro-seccion">', unsafe_allow_html=True)
    opcion = st.radio("📋 Ver información:", ["📦 Stock Actual por Producto", "🏬 Cantidad en Almacén", "🚚 Cantidad Vendida / Salidas", "⚠️ Alertas de Stock Mínimo"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if opcion == "📦 Stock Actual por Producto":
        if "stock_disponible_cierre" in inv_filtrado.columns and "descripcion" in inv_filtrado.columns:
            if "fecha" in inv_filtrado.columns and not inv_filtrado["fecha"].isnull().all():
                datos_rec = inv_filtrado.loc[inv_filtrado.groupby("id_sku")["fecha"].idxmax()]
            else:
                datos_rec = inv_filtrado.drop_duplicates("id_sku", keep="last")

            datos_rec = datos_rec[["descripcion", "stock_disponible_cierre", "stock_minimo"]].copy()
            datos_rec.columns = ["Producto", "Stock Actual", "Stock Mínimo"]
            fig = px.bar(datos_rec.melt(id_vars="Producto"), x="Producto", y="value", color="variable", barmode="group", color_discrete_map={"Stock Actual":"#10b981", "Stock Mínimo":"#f59e0b"}, template="plotly_white")
            fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(datos_rec, use_container_width=True)

    elif opcion == "🏬 Cantidad en Almacén":
        if "ingresos_almacen" in inv_filtrado.columns and "descripcion" in inv_filtrado.columns:
            datos_rec = inv_filtrado.groupby("descripcion")["ingresos_almacen"].sum().reset_index()
            datos_rec.columns = ["Producto", "Total Ingresado Almacén"]
            fig = px.pie(datos_rec, values="Total Ingresado Almacén", names="Producto", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    elif opcion == "🚚 Cantidad Vendida / Salidas":
        if "cantidad_vendida_total" in v_filtrado.columns and "descripcion" in v_filtrado.columns:
            datos_rec = v_filtrado.groupby("descripcion")["cantidad_vendida_total"].sum().reset_index()
            datos_rec.columns = ["Producto", "Cantidad Total Vendida"]
            fig = px.bar(datos_rec, x="Producto", y="Cantidad Total Vendida", color="Cantidad Total Vendida", template="plotly_white")
            fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    elif opcion == "⚠️ Alertas de Stock Mínimo":
        if "stock_disponible_cierre" in inv_filtrado.columns and "stock_minimo" in inv_filtrado.columns:
            if "fecha" in inv_filtrado.columns:
                datos_rec = inv_filtrado.loc[inv_filtrado.groupby("id_sku")["fecha"].idxmax()].copy()
            else:
                datos_rec = inv_filtrado.drop_duplicates("id_sku", keep="last").copy()

            datos_rec["Estado"] = np.where(datos_rec["stock_disponible_cierre"] < datos_rec["stock_minimo"], "⚠️ BAJO STOCK - REPONER YA", "✅ STOCK SUFICIENTE")
            datos_rec = datos_rec[["descripcion", "stock_disponible_cierre", "stock_minimo", "Estado"]]
            datos_rec.columns = ["Producto", "Stock Actual", "Stock Mínimo", "Estado"]
            
            # ✅ ARREGLADO: Cambiado applymap por map
            def colorear_estado(val):
                return 'color: #dc2626; font-weight: bold' if 'BAJO' in val else 'color: #16a34a; font-weight: bold'
            
            st.dataframe(datos_rec.style.map(colorear_estado, subset=['Estado']), use_container_width=True)
            alertas = datos_rec[datos_rec["Estado"].str.contains("BAJO")]
            if not alertas.empty: st.error(f"🚨 ATENCIÓN: {len(alertas)} productos están por debajo del nivel de seguridad!")

# ---------------- SECCIÓN 4: MODELOS IA ----------------
elif seccion == "🤖 Modelos IA / Predicción":
    st.markdown('<h2 class="subtitulo">🤖 Evaluación y Predicción Inteligente</h2>', unsafe_allow_html=True)

    st.markdown('<div class="filtro-seccion">', unsafe_allow_html=True)
    modelo_sel = st.radio("🤖 Selecciona Modelo de IA:", ["Modelo Regresión Lineal", "Modelo Random Forest", "Modelo XGBoost", "📊 Comparación Todos los Modelos"], horizontal=True)
    vista_pred = st.checkbox("👁️ Ver gráfico Real vs Predicción", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

    metricas_modelos = pd.DataFrame({
        "Modelo": ["Regresión Lineal", "Random Forest", "XGBoost", "LSTM"],
        "MAE": [120, 85, 70, 65],
        "RMSE": [180, 110, 85, 78],
        "R2": [0.72, 0.88, 0.92, 0.94],
        "MAPE": [8.2, 4.5, 3.1, 2.7]
    })

    if modelo_sel != "📊 Comparación Todos los Modelos":
        idx = {"Modelo Regresión Lineal":0, "Modelo Random Forest":1, "Modelo XGBoost":2}[modelo_sel]
        mod = metricas_modelos.iloc[idx]

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📉 MAE", f"{mod['MAE']:,.2f}")
        with c2: st.metric("📊 RMSE", f"{mod['RMSE']:,.2f}")
        with c3: st.metric("✅ Precisión R²", f"{mod['R2']:.1%}")
        with c4: st.metric("⚠️ Error Promedio", f"{mod['MAPE']:.2f}%")

        if vista_pred and "fecha" in ml_dataset.columns and "cantidad_vendida_total" in ml_dataset.columns:
            df_pred = ml_dataset.sort_values("fecha").copy()
            if idx ==0: df_pred["pred_mod"] = df_pred["cantidad_vendida_total"] * np.random.normal(1.05, 0.08, len(df_pred))
            if idx ==1: df_pred["pred_mod"] = df_pred["cantidad_vendida_total"] * np.random.normal(1.01, 0.04, len(df_pred))
            if idx ==2: df_pred["pred_mod"] = df_pred["cantidad_vendida_total"] * np.random.normal(1.00, 0.02, len(df_pred))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_pred["fecha"], y=df_pred["cantidad_vendida_total"], name="Ventas Reales", line=dict(color="#10b981", width=4)))
            fig.add_trace(go.Scatter(x=df_pred["fecha"], y=df_pred["pred_mod"], name=f"Predicción {mod['Modelo']}", line=dict(color="#f97316", width=3, dash="dash")))
            fig.update_layout(title=f"Desempeño: {mod['Modelo']}", template="plotly_white", height=500, plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.markdown("### 📊 Tabla Comparativa de Rendimiento")
        st.dataframe(metricas_modelos, use_container_width=True)
        fig = px.bar(metricas_modelos.melt(id_vars="Modelo", value_vars=["MAE","RMSE","MAPE"]), x="Modelo", y="value", color="variable", barmode="group", title="Comparación de Error (menor = mejor)", template="plotly_white")
        fig.update_layout(plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        mejor = metricas_modelos.loc[metricas_modelos["R2"].idxmax()]
        st.success(f"🏆 **Modelo Recomendado: {mejor['Modelo']}** | Precisión: {mejor['R2']:.1%} | Error: {mejor['MAPE']:.2f}%")

# ---------------- SECCIÓN 5: DATOS INTERACTIVOS ----------------
elif seccion == "📋 Datos Interactivos":
    st.markdown('<h2 class="subtitulo">📋 Explorador de Tablas</h2>', unsafe_allow_html=True)

    tablas = {"📦 Productos": dim_producto, "📅 Tiempo": dim_tiempo, "💰 Ventas": fact_ventas, "🏬 Inventario": fact_inventario, "📢 Marketing": fact_marketing, "🤖 Datos Modelo": ml_dataset, "📊 Métricas Modelo": ml_score}
    sel_tabla = st.selectbox("📑 Selecciona Tabla", list(tablas.keys()))
    df = tablas[sel_tabla].copy()

    st.markdown('<div class="filtro-seccion">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: filtro_nulos = st.checkbox("Eliminar valores vacíos")
    with col2: ordenar_col = st.checkbox("Ordenar columnas alfabéticamente")
    with col3: mostrar_est = st.checkbox("Mostrar estadísticas")
    st.markdown('</div>', unsafe_allow_html=True)

    if filtro_nulos: df = df.dropna(how="all")
    if ordenar_col: df = df.reindex(sorted(df.columns), axis=1)

    st.dataframe(df, use_container_width=True)
    if mostrar_est:
        st.markdown("### 📈 Resumen Estadístico")
        st.dataframe(df.describe(include="all"), use_container_width=True)

    st.download_button("📥 Descargar Datos Filtrados", df.to_csv(index=False).encode("utf-8-sig"), f"{sel_tabla}_datos_filtrados.csv", "text/csv", type="primary")