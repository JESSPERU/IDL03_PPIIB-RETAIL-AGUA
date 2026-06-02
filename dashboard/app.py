# ============================================================
# AQUA INTEL — Dashboard Predictivo Retail Agua
# Proyecto Productivo II  ·  Capa Gold · Supabase / PostgreSQL
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import datetime

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title="AquaIntel · Dashboard",
    page_icon=":droplet:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PALETA & TEMA GLOBAL  (dark industrial / aqua)
# ============================================================

COLORS = {
    "bg_dark":   "#080E1A",
    "bg_panel":  "#0D1628",
    "bg_card":   "#111E33",
    "aqua":      "#00D4E8",
    "aqua_dim":  "#007B89",
    "teal":      "#00B4A2",
    "cyan_soft": "#7EEAEA",
    "amber":     "#FFB703",
    "red":       "#FF3B5C",
    "green":     "#00E599",
    "blue_soft": "#4FC3F7",
    "text_pri":  "#E8F4FD",
    "text_sec":  "#7BA7C2",
    "border":    "#1E3050",
    # semáforo
    "ROJO":      "#FF3B5C",
    "AMARILLO":  "#FFB703",
    "VERDE":     "#00E599",
    "AZUL":      "#4FC3F7",
}

C_BG_DARK   = COLORS["bg_dark"]
C_BG_PANEL  = COLORS["bg_panel"]
C_BG_CARD   = COLORS["bg_card"]
C_AQUA      = COLORS["aqua"]
C_AQUA_DIM  = COLORS["aqua_dim"]
C_TEAL      = COLORS["teal"]
C_AMBER     = COLORS["amber"]
C_RED       = COLORS["red"]
C_GREEN     = COLORS["green"]
C_BLUE      = COLORS["blue_soft"]
C_TEXT_PRI  = COLORS["text_pri"]
C_TEXT_SEC  = COLORS["text_sec"]
C_BORDER    = COLORS["border"]

PLOTLY_TEMPLATE = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)"
}

def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Mono", color=C_TEXT_SEC, size=11)
    )
    return fig

# ============================================================
# ICONOS SVG PREMIUM  (stroke-based, estilo Lucide)
# ============================================================

# Wrapper para inyectar color y tamaño sin alterar el SVG base
def icon(name, size=16, color="currentColor"):
    svgs = {
        # ── Brand ──────────────────────────────────────────────
        "wave": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2'
            ' 1.3 0 1.9.5 2.5 1"/>'
            '<path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2'
            ' 5-2 1.3 0 1.9.5 2.5 1"/>'
            '<path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2'
            ' 5-2 1.3 0 1.9.5 2.5 1"/>'
            '</svg>'
        ),
        # ── KPIs ───────────────────────────────────────────────
        "sparkles": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2'
            ' 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937'
            'l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582'
            ' 6.135a.5.5 0 0 1-.963 0z"/>'
            '<path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>'
            '</svg>'
        ),
        "box": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0'
            ' 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>'
            '<path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>'
            '</svg>'
        ),
        "triangle_alert": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>'
            '<path d="M12 9v4"/><path d="M12 17h.01"/>'
            '</svg>'
        ),
        "calendar": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<rect width="18" height="18" x="3" y="4" rx="2"/>'
            '<line x1="16" x2="16" y1="2" y2="6"/>'
            '<line x1="8" x2="8" y1="2" y2="6"/>'
            '<line x1="3" x2="21" y1="10" y2="10"/>'
            '</svg>'
        ),
        "shopping_cart": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/>'
            '<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57'
            'l1.65-7.43H5.12"/>'
            '</svg>'
        ),
        # ── Sidebar ────────────────────────────────────────────
        "sliders": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<line x1="4" x2="4" y1="21" y2="14"/>'
            '<line x1="4" x2="4" y1="10" y2="3"/>'
            '<line x1="12" x2="12" y1="21" y2="12"/>'
            '<line x1="12" x2="12" y1="8" y2="3"/>'
            '<line x1="20" x2="20" y1="21" y2="16"/>'
            '<line x1="20" x2="20" y1="12" y2="3"/>'
            '<line x1="1" x2="7" y1="14" y2="14"/>'
            '<line x1="9" x2="15" y1="8" y2="8"/>'
            '<line x1="17" x2="23" y1="16" y2="16"/>'
            '</svg>'
        ),
        "package": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2'
            ' 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/>'
            '<path d="M12 22V12"/>'
            '<path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"/>'
            '<path d="m7.5 4.27 9 5.15"/>'
            '</svg>'
        ),
        "activity": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'
            '</svg>'
        ),
        # ── Tabs ───────────────────────────────────────────────
        "trending_up": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
            '<polyline points="16 7 22 7 22 13"/>'
            '</svg>'
        ),
        "layers": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0'
            ' 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/>'
            '<path d="m6.08 9.5-3.5 1.6a1 1 0 0 0 0 1.81l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9a1'
            ' 1 0 0 0 0-1.83l-3.5-1.59"/>'
            '<path d="m6.08 14.5-3.5 1.6a1 1 0 0 0 0 1.81l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9a1'
            ' 1 0 0 0 0-1.83l-3.5-1.59"/>'
            '</svg>'
        ),
        "target": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/>'
            '<circle cx="12" cy="12" r="6"/>'
            '<circle cx="12" cy="12" r="2"/>'
            '</svg>'
        ),
        "traffic_cone": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M9.3 6.2a4.55 4.55 0 0 0 5.4 0"/>'
            '<path d="M7.9 10.7c.9.8 2.4 1.3 4.1 1.3s3.2-.5 4.1-1.3"/>'
            '<path d="M13.9 3.5a1.93 1.93 0 0 0-3.8-.1l-3 10c-.1.2-.1.4-.1.6 0 1.7 3.4 3'
            ' 5 3s5-1.3 5-3c0-.2 0-.4-.1-.5Z"/>'
            '<path d="M7 21h10"/><path d="M5.3 18.1c-.5.3-.8.7-.8 1.1 0 1.1 3.4 2 7.5 2'
            ' 4.1 0 7.5-.9 7.5-2 0-.4-.3-.8-.8-1.1"/>'
            '</svg>'
        ),
        "database": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
            '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
            '<path d="M3 12A9 3 0 0 0 21 12"/>'
            '</svg>'
        ),
        # ── Semáforo ───────────────────────────────────────────
        "circle_x": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/>'
            '<path d="m15 9-6 6"/><path d="m9 9 6 6"/>'
            '</svg>'
        ),
        "clock": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/>'
            '<polyline points="12 6 12 12 16 14"/>'
            '</svg>'
        ),
        "circle_check": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/>'
            '<path d="m9 12 2 2 4-4"/>'
            '</svg>'
        ),
        "archive": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<rect width="20" height="5" x="2" y="3" rx="1"/>'
            '<path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/>'
            '<path d="M10 12h4"/>'
            '</svg>'
        ),
        # ── Acciones ───────────────────────────────────────────
        "search": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="11" cy="11" r="8"/>'
            '<path d="m21 21-4.3-4.3"/>'
            '</svg>'
        ),
        "download": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
            '<polyline points="7 10 12 15 17 10"/>'
            '<line x1="12" x2="12" y1="15" y2="3"/>'
            '</svg>'
        ),
        "check_circle": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="{c}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
            '<polyline points="22 4 12 14.01 9 11.01"/>'
            '</svg>'
        ),
        # ── Data source dots ───────────────────────────────────
        "dot": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="8" fill="{c}"/>'
            '</svg>'
        ),
    }

    svg = svgs.get(name, svgs["dot"])
    svg = svg.replace("{c}", color)
    return (
        f'<span style="display:inline-flex; align-items:center; vertical-align:middle;'
        f' width:{size}px; height:{size}px; flex-shrink:0;">'
        f'{svg}'
        f'</span>'
    )


# ============================================================
# CSS GLOBAL
# ============================================================

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700;800&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background: {C_BG_DARK} !important;
    color: {C_TEXT_PRI};
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] {{
    background: {C_BG_PANEL} !important;
    border-right: 1px solid {C_BORDER};
}}
[data-testid="stSidebar"] * {{
    color: {C_TEXT_PRI} !important;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stDateInput label {{
    color: {C_AQUA} !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.brand-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px 0 24px 0;
    border-bottom: 1px solid {C_BORDER};
    margin-bottom: 24px;
}}
.brand-icon {{
    width: 48px; height: 48px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, {C_AQUA_DIM}40, {C_AQUA}20);
    border: 1px solid {C_AQUA}40;
    border-radius: 10px;
    color: {C_AQUA};
    flex-shrink: 0;
}}
.brand-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: {C_TEXT_PRI};
    line-height: 1;
}}
.brand-title span {{ color: {C_AQUA}; }}
.brand-sub {{
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: {C_TEXT_SEC};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}}
.section-label {{
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: {C_AQUA};
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding-left: 2px;
}}
.section-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: {C_TEXT_PRI};
    margin-bottom: 4px;
}}
.kpi-card {{
    background: {C_BG_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 18px 20px 14px;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {C_AQUA}, transparent);
}}
.alert-row {{
    background: rgba(255,59,92,0.06);
    border: 1px solid rgba(255,59,92,0.3);
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
}}
.divider {{
    border: none;
    border-top: 1px solid {C_BORDER};
    margin: 28px 0;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: {C_BG_PANEL};
    border-bottom: 1px solid {C_BORDER};
    gap: 2px;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {C_TEXT_SEC};
    padding: 10px 20px;
    border-radius: 0;
}}
.stTabs [aria-selected="true"] {{
    background: {C_BG_CARD} !important;
    color: {C_AQUA} !important;
    border-bottom: 2px solid {C_AQUA} !important;
}}
div[data-testid="stMetric"] {{
    background: {C_BG_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 14px;
}}
div[data-testid="stMetricLabel"] {{
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem !important;
    color: {C_TEXT_SEC} !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2rem !important;
    color: {C_AQUA} !important;
}}
div[data-testid="stMetricDelta"] {{
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
}}
.stDataFrame {{
    background: {C_BG_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
}}
.stSelectbox > div > div {{
    background: {C_BG_PANEL} !important;
    border-color: {C_BORDER} !important;
    color: {C_TEXT_PRI} !important;
}}
.stDateInput input {{
    background: {C_BG_PANEL} !important;
    border-color: {C_BORDER} !important;
    color: {C_TEXT_PRI} !important;
}}
.stMultiSelect > div {{
    background: {C_BG_PANEL} !important;
    border-color: {C_BORDER} !important;
}}
h1, h2, h3 {{
    font-family: 'Barlow Condensed', sans-serif !important;
    color: {C_TEXT_PRI} !important;
}}
p, li, span {{ color: {C_TEXT_SEC}; }}

/* Icon badge on metric labels */
.metric-icon-label {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: {C_TEXT_SEC};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# CONEXIÓN SUPABASE
# ============================================================

@st.cache_resource
def get_engine():
    DATABASE_URL = st.secrets["DATABASE_URL"]
    return create_engine(DATABASE_URL)

# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    ventas     = pd.read_sql("SELECT * FROM gold.fact_ventas_diarias", engine)
    score      = pd.read_sql("SELECT * FROM gold.ml_score_output", engine)
    inventario = pd.read_sql("SELECT * FROM gold.fact_inventario", engine)
    marketing  = pd.read_sql("SELECT * FROM gold.fact_marketing", engine)
    productos  = pd.read_sql("SELECT * FROM gold.dim_producto", engine)
    tiempo     = pd.read_sql("SELECT * FROM gold.dim_tiempo", engine)
    return ventas, score, inventario, marketing, productos, tiempo

@st.cache_data(ttl=300)
def load_data_csv():
    ventas     = pd.read_csv("fact_ventas_diarias.csv")
    score      = pd.read_csv("ml_score_output.csv")
    inventario = pd.read_csv("fact_inventario.csv")
    marketing  = pd.read_csv("fact_marketing.csv")
    productos  = pd.read_csv("dim_producto.csv")
    tiempo     = pd.read_csv("dim_tiempo.csv")
    return ventas, score, inventario, marketing, productos, tiempo

try:
    ventas, score, inventario, marketing, productos, tiempo = load_data()
    DATA_SOURCE = "Supabase (Gold)"
    DATA_DOT_COLOR = C_GREEN
except Exception:
    ventas, score, inventario, marketing, productos, tiempo = load_data_csv()
    DATA_SOURCE = "CSV local (demo)"
    DATA_DOT_COLOR = C_AMBER

for _df, _col in [
    (ventas,     "fecha"),
    (score,      "fecha_objetivo"),
    (inventario, "fecha"),
    (marketing,  "fecha"),
    (tiempo,     "fecha"),
]:
    if _col in _df.columns:
        _df[_col] = pd.to_datetime(_df[_col])

sku_map = (
    dict(zip(productos["id_sku"], productos["descripcion"]))
    if not productos.empty else {}
)

# ============================================================
# SIDEBAR  —  Filtros globales
# ============================================================

with st.sidebar:
    # ── Logo sidebar ──────────────────────────────────────────
    st.markdown(
        f"<div style='text-align:center; padding:12px 0 20px 0;'>"
        f"<div style='display:inline-flex; align-items:center; justify-content:center;"
        f" width:52px; height:52px; background:linear-gradient(135deg,{C_AQUA_DIM}50,{C_AQUA}20);"
        f" border:1px solid {C_AQUA}50; border-radius:14px; color:{C_AQUA}; margin-bottom:10px;'>"
        f"{icon('wave', size=28, color=C_AQUA)}"
        f"</div>"
        f"<div style='font-family:Barlow Condensed,sans-serif; font-size:1.6rem;"
        f" font-weight:800; color:{C_TEXT_PRI};'>AQUA"
        f"<span style='color:{C_AQUA};'>INTEL</span></div>"
        f"<div style='font-family:Space Mono,monospace; font-size:0.55rem;"
        f" color:{C_TEXT_SEC}; letter-spacing:0.15em; text-transform:uppercase;"
        f" margin-top:4px;'>Retail Agua · Capa Gold</div>"
        f"</div>"
        f"<hr style='border:none; border-top:1px solid {C_BORDER}; margin-bottom:20px;'/>",
        unsafe_allow_html=True,
    )

    # ── Label filtros ─────────────────────────────────────────
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:6px;"
        f" font-family:Space Mono,monospace; font-size:0.6rem;"
        f" color:{C_AQUA}; letter-spacing:0.15em; text-transform:uppercase;"
        f" margin-bottom:10px;'>"
        f"{icon('sliders', size=12, color=C_AQUA)}"
        f" Filtros</div>",
        unsafe_allow_html=True,
    )

    # SKU label con ícono
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:5px;"
        f" font-family:Space Mono,monospace; font-size:0.65rem;"
        f" color:{C_AQUA}; letter-spacing:0.08em; text-transform:uppercase;"
        f" margin-bottom:4px;'>"
        f"{icon('package', size=12, color=C_AQUA)} SKU / Producto</div>",
        unsafe_allow_html=True,
    )
    all_skus = sorted(score["id_sku"].dropna().unique().tolist())
    sku_opts = ["Todos"] + all_skus
    sel_sku  = st.selectbox("", sku_opts, label_visibility="collapsed")

    score_date_min = score["fecha_objetivo"].min().date()
    score_date_max = score["fecha_objetivo"].max().date()

    st.markdown(
        f"<div style='display:flex; align-items:center; gap:5px;"
        f" font-family:Space Mono,monospace; font-size:0.65rem;"
        f" color:{C_AQUA}; letter-spacing:0.08em; text-transform:uppercase;"
        f" margin-top:8px; margin-bottom:4px;'>"
        f"{icon('calendar', size=12, color=C_AQUA)} Fecha inicio</div>",
        unsafe_allow_html=True,
    )
    flt_fecha_ini = st.date_input(
        "", score_date_min,
        min_value=score_date_min, max_value=score_date_max,
        label_visibility="collapsed",
    )

    st.markdown(
        f"<div style='display:flex; align-items:center; gap:5px;"
        f" font-family:Space Mono,monospace; font-size:0.65rem;"
        f" color:{C_AQUA}; letter-spacing:0.08em; text-transform:uppercase;"
        f" margin-top:8px; margin-bottom:4px;'>"
        f"{icon('calendar', size=12, color=C_AQUA)} Fecha fin</div>",
        unsafe_allow_html=True,
    )
    flt_fecha_fin = st.date_input(
        "", score_date_max,
        min_value=score_date_min, max_value=score_date_max,
        label_visibility="collapsed",
    )

    st.markdown(
        f"<hr style='border:none; border-top:1px solid {C_BORDER}; margin:16px 0;'/>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='display:flex; align-items:center; gap:5px;"
        f" font-family:Space Mono,monospace; font-size:0.65rem;"
        f" color:{C_AQUA}; letter-spacing:0.08em; text-transform:uppercase;"
        f" margin-bottom:4px;'>"
        f"{icon('activity', size=12, color=C_AQUA)} Ventana histórica</div>",
        unsafe_allow_html=True,
    )
    ventanas_hist = {"3 meses": 90, "6 meses": 180, "1 año": 365, "Todo": 9999}
    v_label  = st.selectbox("", list(ventanas_hist.keys()), index=3, label_visibility="collapsed")
    dias_hist = ventanas_hist[v_label]

    st.markdown(
        f"<hr style='border:none; border-top:1px solid {C_BORDER}; margin:16px 0;'/>",
        unsafe_allow_html=True,
    )
    # Fuente de datos con dot de color
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:6px;"
        f" font-family:Space Mono,monospace; font-size:0.55rem; color:{C_TEXT_SEC};'>"
        f"{icon('dot', size=8, color=DATA_DOT_COLOR)}"
        f" {DATA_SOURCE}</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# FILTRADO
# ============================================================

def filtrar_score(df):
    d = df.copy()
    d = d[
        (d["fecha_objetivo"] >= pd.to_datetime(flt_fecha_ini)) &
        (d["fecha_objetivo"] <= pd.to_datetime(flt_fecha_fin))
    ]
    if sel_sku != "Todos":
        d = d[d["id_sku"] == sel_sku]
    return d


def filtrar_ventas(df):
    d = df.copy()
    if d.empty:
        return d
    fecha_ref = d["fecha"].max()
    d = d[d["fecha"] >= fecha_ref - pd.Timedelta(days=dias_hist)]
    if sel_sku != "Todos":
        d = d[d["id_sku"] == sel_sku]
    return d


score_f  = filtrar_score(score)
ventas_f = filtrar_ventas(ventas)
inv_f    = inventario.copy()
if sel_sku != "Todos":
    inv_f = inv_f[inv_f["id_sku"] == sel_sku]

ventas_agg = (
    ventas_f
    .groupby(["fecha", "id_sku"])
    .agg(
        cantidad_vendida=("cantidad_vendida_total", "sum"),
        venta_total=("venta_total", "sum"),
    )
    .reset_index()
)

mkt_agg = (
    marketing
    .groupby("fecha")
    .agg(
        inversion_usd=("inversion_usd", "sum"),
        conversiones=("conversiones_atribuidas", "sum"),
    )
    .reset_index()
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"<div class='brand-header'>"
    f"<div class='brand-icon'>{icon('wave', size=30, color=C_AQUA)}</div>"
    f"<div>"
    f"<div class='brand-title'>AQUA<span>INTEL</span></div>"
    f"<div class='brand-sub'>Dashboard Predictivo Retail Agua · Proyecto Productivo II</div>"
    f"</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ============================================================
# KPIs GLOBALES
# ============================================================

total_pred     = score_f["cantidad_predicha"].sum() if not score_f.empty else 0
total_stock    = score_f["stock_fin"].mean()         if not score_f.empty else 0
alertas_compra = int((score_f["alerta_compra"] == "COMPRAR").sum()) if not score_f.empty else 0
dias_cob_prom  = score_f["dias_cobertura"].mean()    if not score_f.empty else 0
total_vendido  = ventas_agg["cantidad_vendida"].sum() if not ventas_agg.empty else 0

try:
    fecha_ref  = ventas_f["fecha"].max()
    sem_act    = ventas_f[ventas_f["fecha"] >  fecha_ref - pd.Timedelta(days=7)]["cantidad_vendida_total"].sum()
    sem_ant    = ventas_f[
        (ventas_f["fecha"] <= fecha_ref - pd.Timedelta(days=7)) &
        (ventas_f["fecha"] >  fecha_ref - pd.Timedelta(days=14))
    ]["cantidad_vendida_total"].sum()
    delta_ventas = ((sem_act - sem_ant) / sem_ant * 100) if sem_ant > 0 else 0.0
except Exception:
    delta_ventas = 0.0

col1, col2, col3, col4, col5 = st.columns(5)

# Función helper para label de métrica con ícono SVG
def metric_label(icon_name, label_text, icon_color=C_AQUA):
    return (
        f"<div class='metric-icon-label'>"
        f"{icon(icon_name, size=13, color=icon_color)}"
        f"<span>{label_text}</span>"
        f"</div>"
    )

with col1:
    st.markdown(metric_label("sparkles", "Demanda Predicha"), unsafe_allow_html=True)
    st.metric("", f"{total_pred:,.0f} u", delta="período seleccionado", label_visibility="collapsed")
with col2:
    st.markdown(metric_label("box", "Stock Promedio"), unsafe_allow_html=True)
    st.metric("", f"{total_stock:,.0f} u", label_visibility="collapsed")
with col3:
    st.markdown(metric_label("triangle_alert", "Alertas Compra", icon_color=C_RED if alertas_compra > 10 else C_AMBER), unsafe_allow_html=True)
    st.metric(
        "", alertas_compra,
        delta="Revisar" if alertas_compra > 10 else "Bajo control",
        delta_color="inverse" if alertas_compra > 10 else "normal",
        label_visibility="collapsed",
    )
with col4:
    st.markdown(metric_label("calendar", "Días Cobertura Prom."), unsafe_allow_html=True)
    st.metric("", f"{dias_cob_prom:.1f} d", label_visibility="collapsed")
with col5:
    st.markdown(metric_label("shopping_cart", "Ventas Históricas"), unsafe_allow_html=True)
    st.metric("", f"{total_vendido:,.0f} u",
              delta=f"{delta_ventas:+.1f}% vs sem ant.",
              label_visibility="collapsed")

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# ============================================================
# TABS PRINCIPALES
# ============================================================

# Labels de tabs con SVG icons embebidos en HTML
# Nota: Streamlit no renderiza HTML en st.tabs(), así que usamos
# texto unicode minimalista + el ícono se inyecta en la sección
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "↗  HISTÓRICO & PREDICCIÓN",
    "▣  INVENTARIO & ALERTAS",
    "◎  ADS & CORRELACIÓN",
    "◈  SEMÁFORO DE STOCK",
    "≡  DETALLE COMPLETO",
])

SKU_COLORS = {
    "SKU_500ML": C_AQUA,
    "SKU_1L":    C_TEAL,
    "SKU_20L":   C_BLUE,
}

# ────────────────────────────────────────────────────────────
# TAB 1 — HISTÓRICO & PREDICCIÓN
# ────────────────────────────────────────────────────────────

with tab1:
    st.markdown(
        f"<div class='section-label'>Análisis temporal</div>"
        f"<div class='section-title'>Ventas Históricas vs. Demanda Predicha</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:0.8rem; color:{C_TEXT_SEC}; margin-bottom:20px;'>"
        "Comparación entre ventas reales registradas (Capa Gold) y las proyecciones "
        "generadas por el modelo de Machine Learning.</p>",
        unsafe_allow_html=True,
    )

    skus_plot = all_skus if sel_sku == "Todos" else [sel_sku]

    fig_hist = go.Figure()
    for sku in skus_plot:
        df_s   = ventas_agg[ventas_agg["id_sku"] == sku].sort_values("fecha")
        nombre = sku_map.get(sku, sku)
        color  = SKU_COLORS.get(sku, C_AQUA)
        fig_hist.add_trace(go.Scatter(
            x=df_s["fecha"], y=df_s["cantidad_vendida"],
            name=f"▸ {nombre} (Real)",
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{nombre}</b><br>%{{x|%d %b %Y}}<br>Vendido: %{{y:,.0f}} u<extra></extra>",
        ))

    for sku in skus_plot:
        df_p   = score_f[score_f["id_sku"] == sku].sort_values("fecha_objetivo")
        nombre = sku_map.get(sku, sku)
        color  = SKU_COLORS.get(sku, C_AQUA)
        fig_hist.add_trace(go.Scatter(
            x=df_p["fecha_objetivo"], y=df_p["cantidad_predicha"],
            name=f"◈ {nombre} (Predicción)",
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
            opacity=0.75,
            hovertemplate=f"<b>{nombre} — Predicción</b><br>%{{x|%d %b %Y}}<br>Predicho: %{{y:,.0f}} u<extra></extra>",
        ))

    hoy_ts  = ventas["fecha"].max() if not ventas.empty else pd.Timestamp.now()
    hoy_str = hoy_ts.strftime("%Y-%m-%d")

    fig_hist.add_shape(
        type="line",
        x0=hoy_str, x1=hoy_str,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color=C_AMBER, width=1, dash="dash"),
    )
    fig_hist.add_annotation(
        x=hoy_str, y=1,
        xref="x", yref="paper",
        text="HOY",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color=C_AMBER, family="Space Mono", size=10),
    )
    if not score_f.empty:
        x1_str = score_f["fecha_objetivo"].max().strftime("%Y-%m-%d")
        fig_hist.add_shape(
            type="rect",
            x0=hoy_str, x1=x1_str,
            y0=0, y1=1,
            xref="x", yref="paper",
            fillcolor=C_AQUA,
            opacity=0.03,
            layer="below",
            line_width=0,
        )

    fig_hist.update_layout(
        **PLOTLY_TEMPLATE,
        height=390,
        xaxis_title="Fecha", yaxis_title="Unidades",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        "<div class='section-label' style='margin-top:24px;'>Desglose mensual</div>"
        "<div class='section-title'>Volumen de Ventas por Mes y SKU</div>",
        unsafe_allow_html=True,
    )

    ventas_mes = ventas_agg.copy()
    ventas_mes["mes"] = ventas_mes["fecha"].dt.to_period("M").astype(str)
    ventas_mes_agg = (
        ventas_mes.groupby(["mes", "id_sku"])["cantidad_vendida"]
        .sum().reset_index()
    )
    fig_barras = px.bar(
        ventas_mes_agg, x="mes", y="cantidad_vendida", color="id_sku",
        barmode="group",
        color_discrete_map=SKU_COLORS,
        labels={"cantidad_vendida": "Unidades", "mes": "Mes", "id_sku": "SKU"},
    )
    fig_barras.update_layout(
        **PLOTLY_TEMPLATE,
        height=310,
        xaxis=dict(
            tickangle=-45,
            gridcolor=C_BORDER,
            linecolor=C_BORDER,
            tickcolor=C_TEXT_SEC
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig_barras.update_traces(marker_line_color="rgba(0,0,0,0)", opacity=0.88)
    st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown(
        "<div class='section-label' style='margin-top:24px;'>Horizonte predictivo</div>"
        "<div class='section-title'>Proyección de Demanda — Período Seleccionado</div>",
        unsafe_allow_html=True,
    )
    fig_pred = go.Figure()
    for sku in skus_plot:
        df_p   = score_f[score_f["id_sku"] == sku].sort_values("fecha_objetivo")
        nombre = sku_map.get(sku, sku)
        color  = SKU_COLORS.get(sku, C_AQUA)
        fig_pred.add_trace(go.Scatter(
            x=df_p["fecha_objetivo"], y=df_p["cantidad_predicha"],
            name=nombre, fill="tozeroy", mode="lines",
            line=dict(color=color, width=2),
            fillcolor="rgba(0,212,232,0.15)",
            hovertemplate=f"<b>{nombre}</b><br>%{{x|%d %b %Y}}<br>Predicción: %{{y:,.0f}} u<extra></extra>",
        ))
    fig_pred.update_layout(
        **PLOTLY_TEMPLATE,
        height=320,
        xaxis_title="Fecha", yaxis_title="Unidades Predichas",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_pred, use_container_width=True)


# ────────────────────────────────────────────────────────────
# TAB 2 — INVENTARIO & ALERTAS
# ────────────────────────────────────────────────────────────

with tab2:
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown(
            "<div class='section-label'>Inventario proyectado</div>"
            "<div class='section-title'>Stock Fin vs. Stock de Seguridad</div>",
            unsafe_allow_html=True,
        )
        fig_inv = go.Figure()
        for sku in skus_plot:
            df_s   = score_f[score_f["id_sku"] == sku].sort_values("fecha_objetivo")
            color  = SKU_COLORS.get(sku, C_AQUA)
            nombre = sku_map.get(sku, sku)
            fig_inv.add_trace(go.Scatter(
                x=df_s["fecha_objetivo"], y=df_s["stock_fin"],
                name=f"{nombre} — Stock",
                line=dict(color=color, width=2.5), mode="lines",
            ))
            fig_inv.add_trace(go.Scatter(
                x=df_s["fecha_objetivo"], y=df_s["stock_seguridad"],
                name=f"{nombre} — Seg.",
                line=dict(color=color, width=1, dash="dot"),
                mode="lines", opacity=0.55,
            ))
        fig_inv.update_layout(
            **PLOTLY_TEMPLATE,
            height=360,
            xaxis_title="Fecha", yaxis_title="Unidades",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_inv, use_container_width=True)

        st.markdown(
            "<div class='section-label' style='margin-top:20px;'>Cobertura temporal</div>"
            "<div class='section-title'>Días de Cobertura Disponibles</div>",
            unsafe_allow_html=True,
        )
        fig_cob = go.Figure()
        for sku in skus_plot:
            df_s   = score_f[score_f["id_sku"] == sku].sort_values("fecha_objetivo")
            color  = SKU_COLORS.get(sku, C_AQUA)
            nombre = sku_map.get(sku, sku)
            fig_cob.add_trace(go.Scatter(
                x=df_s["fecha_objetivo"], y=df_s["dias_cobertura"],
                name=nombre, fill="tozeroy", mode="lines",
                line=dict(color=color, width=2),
                fillcolor="rgba(0,212,232,0.18)"
            ))
        for nivel, color_sem, label in [
            (2,  C_RED,   "— Quiebre"),
            (5,  C_AMBER, "— Mínimo"),
            (10, C_GREEN, "— Sobre-stock"),
        ]:
            fig_cob.add_hline(
                y=nivel, line_dash="dot", line_color=color_sem, line_width=1,
                annotation_text=label,
                annotation_font=dict(color=color_sem, size=9, family="Space Mono"),
                annotation_position="right",
            )
        fig_cob.update_layout(
            **PLOTLY_TEMPLATE,
            height=300,
            xaxis_title="Fecha", yaxis_title="Días",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=10, b=40),
        )
        st.plotly_chart(fig_cob, use_container_width=True)

    with right_col:
        st.markdown(
            "<div class='section-label'>Órdenes de reposición</div>"
            "<div class='section-title'>Productos con ALERTA</div>",
            unsafe_allow_html=True,
        )
        alertas_df = (
            score_f[score_f["alerta_compra"] == "COMPRAR"]
            .sort_values("dias_cobertura")
        )
        if alertas_df.empty:
            st.markdown(
                f"<div style='display:flex; align-items:center; gap:8px;"
                f" background:rgba(0,229,153,0.08); border:1px solid rgba(0,229,153,0.3);"
                f" border-radius:6px; padding:12px 14px;"
                f" font-family:Space Mono,monospace; font-size:0.7rem; color:{C_GREEN};'>"
                f"{icon('check_circle', size=14, color=C_GREEN)}"
                f" Sin alertas activas en el período seleccionado."
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            for _, row in alertas_df.head(20).iterrows():
                sem_color = COLORS.get(row["semaforo_stock"], C_AMBER)
                st.markdown(
                    f"<div class='alert-row'>"
                    f"<div style='display:flex; align-items:center; gap:6px;'>"
                    f"{icon('triangle_alert', size=11, color=sem_color)}"
                    f"<span style='color:{C_AQUA}; font-weight:700;'>{row['id_sku']}</span>"
                    f"<span style='color:{C_TEXT_SEC}; margin-left:4px;'>{str(row['fecha_objetivo'])[:10]}</span>"
                    f"</div>"
                    f"<div style='text-align:right;'>"
                    f"<div style='color:{sem_color}; font-weight:700;'>{row['dias_cobertura']:.1f} días</div>"
                    f"<div style='color:{C_TEXT_SEC}; font-size:0.6rem;'>Reponer: {row['cantidad_reponer']:,.0f} u</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            "<div class='section-label' style='margin-top:24px;'>Distribución</div>"
            "<div class='section-title'>Semáforo por Días</div>",
            unsafe_allow_html=True,
        )
        sem_counts = score_f["semaforo_stock"].value_counts().reset_index()
        sem_counts.columns = ["semaforo", "count"]
        sem_colors_list = [COLORS.get(s, "#888") for s in sem_counts["semaforo"]]
        fig_dona = go.Figure(go.Pie(
            labels=sem_counts["semaforo"], values=sem_counts["count"],
            hole=0.62,
            marker=dict(colors=sem_colors_list, line=dict(color=C_BG_DARK, width=3)),
            textfont=dict(family="Space Mono", size=10, color=C_TEXT_PRI),
        ))
        fig_dona.update_layout(
            **PLOTLY_TEMPLATE,
            height=260, showlegend=True,
            legend=dict(font=dict(size=9)),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_dona, use_container_width=True)

        rep_df = (
            score_f.groupby("id_sku")["cantidad_reponer"]
            .sum().reset_index()
            .rename(columns={"cantidad_reponer": "Total Reponer", "id_sku": "SKU"})
        )
        rep_df["Producto"] = rep_df["SKU"].map(sku_map)
        fig_rep = px.bar(
            rep_df, y="Producto", x="Total Reponer", orientation="h",
            color="Total Reponer",
            color_continuous_scale=[[0, C_AQUA_DIM], [1, C_AQUA]],
        )
        fig_rep.update_layout(
            **PLOTLY_TEMPLATE,
            height=190, showlegend=False, coloraxis_showscale=False,
            xaxis_title="Unidades", yaxis_title="",
            margin=dict(l=0, r=0, t=6, b=0),
        )
        st.plotly_chart(fig_rep, use_container_width=True)


# ────────────────────────────────────────────────────────────
# TAB 3 — ADS & CORRELACIÓN
# ────────────────────────────────────────────────────────────

with tab3:
    st.markdown(
        "<div class='section-label'>Marketing digital</div>"
        "<div class='section-title'>Inversión en Ads vs. Volumen de Ventas</div>",
        unsafe_allow_html=True,
    )

    ventas_global = (
        ventas.groupby("fecha")["cantidad_vendida_total"]
        .sum().reset_index()
        .rename(columns={"cantidad_vendida_total": "ventas"})
    )
    df_ads = pd.merge(ventas_global, mkt_agg, on="fecha", how="left").fillna(0)
    df_ads = df_ads.sort_values("fecha")
    df_ads["ventas_7d"] = df_ads["ventas"].rolling(7, min_periods=1).mean()
    df_ads["inv_7d"]    = df_ads["inversion_usd"].rolling(7, min_periods=1).mean()

    fig_ads = make_subplots(specs=[[{"secondary_y": True}]])
    fig_ads.add_trace(
        go.Scatter(
            x=df_ads["fecha"], y=df_ads["ventas_7d"],
            name="Ventas (MA 7d)",
            line=dict(color=C_AQUA, width=2.5), mode="lines",
        ),
        secondary_y=False,
    )
    fig_ads.add_trace(
        go.Bar(
            x=df_ads["fecha"], y=df_ads["inv_7d"],
            name="Inversión Ads (MA 7d)",
            marker_color=C_AMBER, opacity=0.45,
        ),
        secondary_y=True,
    )
    fig_ads.update_layout(
        **PLOTLY_TEMPLATE,
        height=370,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig_ads.update_yaxes(
        title_text="Unidades vendidas", secondary_y=False,
        gridcolor=C_BORDER, color=C_TEXT_SEC,
    )
    fig_ads.update_yaxes(
        title_text="Inversión USD", secondary_y=True,
        gridcolor="rgba(0,0,0,0)", color=C_AMBER,
    )
    st.plotly_chart(fig_ads, use_container_width=True)

    st.markdown(
        "<div class='section-label' style='margin-top:24px;'>Correlación</div>"
        "<div class='section-title'>Dispersión: Ads Invertidos vs. Ventas del Día</div>",
        unsafe_allow_html=True,
    )

    col_sc1, col_sc2 = st.columns([2, 1])
    with col_sc1:
        fig_scatter = px.scatter(
            df_ads,
            x="inversion_usd",
            y="ventas",
            labels={"inversion_usd": "Inversión Ads (USD)", "ventas": "Ventas (u)"},
            color_discrete_sequence=[C_AQUA],
        )
        fig_scatter.update_traces(
            marker=dict(size=5, opacity=0.65, color=C_AQUA),
            selector=dict(mode="markers"),
        )
        fig_scatter.for_each_trace(
            lambda t: t.update(line_color=C_AMBER, line_width=2)
            if t.mode == "lines" else None
        )
        fig_scatter.update_layout(
            **PLOTLY_TEMPLATE,
            height=340, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_sc2:
        df_corr  = df_ads[df_ads["inversion_usd"] > 0]
        corr_val = df_corr["inversion_usd"].corr(df_corr["ventas"])
        corr_str = f"{corr_val:.2f}" if not pd.isna(corr_val) else "N/A"
        corr_label = "Correlación fuerte" if (not pd.isna(corr_val) and corr_val > 0.6) else "Correlación moderada"

        st.markdown(
            f"<div style='background:{C_BG_CARD}; border:1px solid {C_BORDER};"
            f" border-radius:8px; padding:24px; margin-top:8px; text-align:center;'>"
            f"<div style='font-family:Space Mono,monospace; font-size:0.6rem;"
            f" color:{C_TEXT_SEC}; letter-spacing:0.15em; text-transform:uppercase;"
            f" margin-bottom:12px;'>Correlación de Pearson<br>Ads ↔ Ventas</div>"
            f"<div style='font-family:Barlow Condensed,sans-serif; font-size:4rem;"
            f" font-weight:800; color:{C_AQUA}; line-height:1;'>{corr_str}</div>"
            f"<div style='display:flex; align-items:center; justify-content:center; gap:6px;"
            f" font-family:Space Mono,monospace; font-size:0.65rem;"
            f" color:{C_AMBER}; margin-top:10px;'>"
            f"{icon('trending_up', size=13, color=C_AMBER)}"
            f" {corr_label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='section-label' style='margin-top:20px;'>Por plataforma</div>",
            unsafe_allow_html=True,
        )
        plat_df = (
            marketing.groupby("plataforma_origen")["inversion_usd"]
            .sum().reset_index()
            .sort_values("inversion_usd", ascending=False)
        )
        fig_plat = px.bar(
            plat_df, x="plataforma_origen", y="inversion_usd",
            color="plataforma_origen",
            color_discrete_sequence=[C_AQUA, C_TEAL, C_BLUE, C_AMBER],
            labels={"plataforma_origen": "", "inversion_usd": "USD"},
        )
        fig_plat.update_layout(
            **PLOTLY_TEMPLATE,
            showlegend=False, height=220,
            margin=dict(l=0, r=0, t=6, b=0),
        )
        st.plotly_chart(fig_plat, use_container_width=True)


# ────────────────────────────────────────────────────────────
# TAB 4 — SEMÁFORO DE STOCK
# ────────────────────────────────────────────────────────────

with tab4:
    st.markdown(
        "<div class='section-label'>Gobernanza operativa</div>"
        "<div class='section-title'>Sistema de Semáforo — Niveles de Stock</div>",
        unsafe_allow_html=True,
    )

    # Íconos SVG premium para semáforo — círculos con símbolo interno
    SEMAFORO_ICONS = {
        "ROJO": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24">'
            f'<circle cx="12" cy="12" r="10" fill="{C_RED}" opacity="0.15"/>'
            f'<circle cx="12" cy="12" r="10" fill="none" stroke="{C_RED}" stroke-width="1.5"/>'
            f'<line x1="12" y1="8" x2="12" y2="12" stroke="{C_RED}" stroke-width="2" stroke-linecap="round"/>'
            f'<circle cx="12" cy="15.5" r="1" fill="{C_RED}"/>'
            f'</svg>'
        ),
        "AMARILLO": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24">'
            f'<circle cx="12" cy="12" r="10" fill="{C_AMBER}" opacity="0.15"/>'
            f'<circle cx="12" cy="12" r="10" fill="none" stroke="{C_AMBER}" stroke-width="1.5"/>'
            f'<polyline points="12 7 12 12 15 14" stroke="{C_AMBER}" stroke-width="2"'
            f' stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
            f'</svg>'
        ),
        "VERDE": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24">'
            f'<circle cx="12" cy="12" r="10" fill="{C_GREEN}" opacity="0.15"/>'
            f'<circle cx="12" cy="12" r="10" fill="none" stroke="{C_GREEN}" stroke-width="1.5"/>'
            f'<polyline points="8 12 11 15 16 9" stroke="{C_GREEN}" stroke-width="2"'
            f' stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
            f'</svg>'
        ),
        "AZUL": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24">'
            f'<circle cx="12" cy="12" r="10" fill="{C_BLUE}" opacity="0.15"/>'
            f'<circle cx="12" cy="12" r="10" fill="none" stroke="{C_BLUE}" stroke-width="1.5"/>'
            f'<line x1="12" y1="8" x2="12" y2="13" stroke="{C_BLUE}" stroke-width="2" stroke-linecap="round"/>'
            f'<line x1="9" y1="16" x2="15" y2="16" stroke="{C_BLUE}" stroke-width="2" stroke-linecap="round"/>'
            f'<polyline points="9 13 12 16 15 13" stroke="{C_BLUE}" stroke-width="2"'
            f' stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
            f'</svg>'
        ),
    }

    leyenda_cols = st.columns(4)
    leyenda_items = [
        ("ROJO",     "Quiebre inminente", "≤ 2 días cobertura",   C_RED),
        ("AMARILLO", "Stock mínimo",      "2 – 5 días cobertura", C_AMBER),
        ("VERDE",    "Stock óptimo",      "5 – 10 días cob.",     C_GREEN),
        ("AZUL",     "Sobre-stock",       "> 10 días cobertura",  C_BLUE),
    ]
    for col, (nombre, desc, rango, color) in zip(leyenda_cols, leyenda_items):
        with col:
            st.markdown(
                f"<div style='background:{C_BG_CARD}; border:1px solid {color}40;"
                f" border-radius:8px; padding:14px; text-align:center;'>"
                f"<div style='display:flex; justify-content:center; margin-bottom:6px;'>"
                f"{SEMAFORO_ICONS[nombre]}"
                f"</div>"
                f"<div style='font-family:Barlow Condensed,sans-serif; font-size:1.2rem;"
                f" font-weight:700; color:{color}; margin:4px 0;'>{nombre}</div>"
                f"<div style='font-family:Space Mono,monospace; font-size:0.58rem;"
                f" color:{C_TEXT_SEC};'>{desc}</div>"
                f"<div style='font-family:Space Mono,monospace; font-size:0.55rem;"
                f" color:{color}; margin-top:4px;'>{rango}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    if not score_f.empty:
        score_heat = score_f.copy()
        score_heat["semana"]  = score_heat["fecha_objetivo"].dt.to_period("W").astype(str)
        score_heat["sem_num"] = score_heat["semaforo_stock"].map(
            {"ROJO": 1, "AMARILLO": 2, "VERDE": 3, "AZUL": 4}
        )
        heat_pivot = (
            score_heat.groupby(["id_sku", "semana"])["sem_num"]
            .mean().unstack(fill_value=0)
        )
        fig_heat = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns.tolist(),
            y=[sku_map.get(s, s) for s in heat_pivot.index.tolist()],
            colorscale=[
                [0.00, C_BG_PANEL],
                [0.25, C_RED],
                [0.50, C_AMBER],
                [0.75, C_GREEN],
                [1.00, C_BLUE],
            ],
            showscale=False,
            hovertemplate="SKU: %{y}<br>Semana: %{x}<br>Nivel: %{z:.2f}<extra></extra>",
        ))
        fig_heat.update_layout(
            **PLOTLY_TEMPLATE,
            height=220,
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=8),
                gridcolor=C_BORDER,
                linecolor=C_BORDER,
                tickcolor=C_TEXT_SEC
            ),
            margin=dict(l=0, r=0, t=10, b=60),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown(
        "<div class='section-label' style='margin-top:20px;'>Tabla operativa</div>"
        "<div class='section-title'>Detalle de Semáforo por Fecha y SKU</div>",
        unsafe_allow_html=True,
    )
    cols_sem = ["fecha_objetivo", "id_sku", "dias_cobertura",
                "semaforo_stock", "alerta_compra", "comentario_negocio"]
    tabla_sem = score_f[cols_sem].rename(columns={
        "fecha_objetivo":     "Fecha",
        "id_sku":             "SKU",
        "dias_cobertura":     "Días Cob.",
        "semaforo_stock":     "Semáforo",
        "alerta_compra":      "Alerta",
        "comentario_negocio": "Comentario",
    }).sort_values("Días Cob.")
    st.dataframe(tabla_sem, use_container_width=True, height=420, hide_index=True)


# ────────────────────────────────────────────────────────────
# TAB 5 — DETALLE COMPLETO
# ────────────────────────────────────────────────────────────

with tab5:
    st.markdown(
        "<div class='section-label'>Exploración libre</div>"
        "<div class='section-title'>Tabla Completa — ml_score_output (Gold)</div>",
        unsafe_allow_html=True,
    )
    col_busq, col_dl = st.columns([3, 1])
    with col_busq:
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:6px;"
            f" font-family:Space Mono,monospace; font-size:0.65rem;"
            f" color:{C_TEXT_SEC}; letter-spacing:0.08em; margin-bottom:4px;'>"
            f"{icon('search', size=12, color=C_TEXT_SEC)} Buscar en la tabla</div>",
            unsafe_allow_html=True,
        )
        busqueda = st.text_input("", placeholder="SKU, alerta, semáforo…", label_visibility="collapsed")
    with col_dl:
        csv_export = score_f.to_csv(index=False).encode("utf-8")
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:6px;"
            f" font-family:Space Mono,monospace; font-size:0.65rem;"
            f" color:{C_TEXT_SEC}; letter-spacing:0.08em; margin-bottom:4px;'>"
            f"{icon('download', size=12, color=C_TEXT_SEC)} Exportar</div>",
            unsafe_allow_html=True,
        )
        st.download_button(
            "Exportar CSV", csv_export,
            "score_output_filtrado.csv", "text/csv",
            use_container_width=True,
        )

    df_show = score_f.copy()
    if busqueda:
        mask = (
            df_show.astype(str)
            .apply(lambda c: c.str.contains(busqueda, case=False))
            .any(axis=1)
        )
        df_show = df_show[mask]

    st.dataframe(
        df_show.sort_values("fecha_objetivo"),
        use_container_width=True, height=520, hide_index=True,
    )

    st.markdown(
        "<div class='section-label' style='margin-top:24px;'>Histórico</div>"
        "<div class='section-title'>Tabla Ventas Diarias (Gold)</div>",
        unsafe_allow_html=True,
    )
    cols_v = ["fecha", "id_sku", "id_canal", "cantidad_vendida_total",
              "venta_total", "precio_unitario_promedio", "numero_transacciones"]
    st.dataframe(
        ventas_f[cols_v].sort_values("fecha", ascending=False),
        use_container_width=True, height=380, hide_index=True,
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"<hr class='divider'/>"
    f"<div style='display:flex; align-items:center; justify-content:center; gap:8px;"
    f" padding:16px 0 24px;"
    f" font-family:Space Mono,monospace; font-size:0.55rem;"
    f" color:{C_TEXT_SEC}; letter-spacing:0.1em;'>"
    f"{icon('dot', size=7, color=DATA_DOT_COLOR)}"
    f"<span>AQUA<span style='color:{C_AQUA};'>INTEL</span>"
    f" &nbsp;·&nbsp; Proyecto Productivo II &nbsp;·&nbsp;"
    f" Capa Gold · Supabase (PostgreSQL) &nbsp;·&nbsp;"
    f" {DATA_SOURCE}</span>"
    f"</div>",
    unsafe_allow_html=True,
)