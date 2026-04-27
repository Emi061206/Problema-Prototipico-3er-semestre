# ─── Importaciones y Dependencias ─────────────────────────────────────────────
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import importlib
from sqlalchemy import create_engine

# ─── Configuración Global de la Interfaz ──────────────────────────────────────
st.set_page_config(
    page_title="Smart Agroforestry Morelos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Identidad Visual (Paleta de Colores Industrial) ──────────────────────────
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {BG_DEEP}; color: #ffffff; }}
[data-testid="stSidebar"] {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}
div[data-testid="metric-container"] {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; }}
div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-family: 'Share Tech Mono', monospace; font-size: 11px; }}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {CYAN} !important; font-weight: 700; }}
.card-container {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
</style>
""", unsafe_allow_html=True)

# ─── Módulo de Conectividad de Datos ──────────────────────────────────────────
@st.cache_data
def extraer_datos_csv():
    directorio = os.path.dirname(__file__)
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    return pd.read_csv(ruta)

def extraer_datos_sql():
    try:
        from database import obtener_conexion
        engine = obtener_conexion()
        query = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad FROM catalogo_cultivos"
        return pd.read_sql(query, engine)
    except Exception:
        data_respaldo = {
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'],
            'costo_operativo': [41000.0, 65000.0, 55000.0, 38000.0],
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04],
            'riesgo_probabilidad': [0.35, 0.10, 0.20, 0.25]
        }
        return pd.DataFrame(data_respaldo)

df_historico = extraer_datos_csv()
df_catalogo = extraer_datos_sql()

try:
    modelo_inversion = importlib.import_module("03_modelo_inversion")
except ImportError:
    modelo_inversion = None

# ─── Panel de Control (Barra Lateral) ─────────────────────────────────────────
st.sidebar.header("Panel de Control")
municipio = st.sidebar.selectbox("Seleccione Municipio:", df_historico['Nommunicipio'].unique())
mes_actual = st.sidebar.selectbox("Mes de Análisis:", 
    ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])
anio_range = st.sidebar.slider("Periodo:", int(df_historico['Anio'].min()), int(df_historico['Anio'].max()), (2018, 2024))

filtro_estatus = st.sidebar.multiselect(
    "Filtrar por Diagnóstico ICC:",
    options=["Alta Competitividad", "Optimización Requerida", "Diversificación Urgente"],
    default=["Alta Competitividad", "Optimización Requerida"]
)

# ─── Motor Analítico e Integración ────────────────────────────────────────────
df_f = df_historico[(df_historico['Nommunicipio'] == municipio) & 
                    (df_historico['Anio'] >= anio_range[0]) & 
                    (df_historico['Anio'] <= anio_range[1])].copy()

df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')
df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
df_merge['ingreso_total'] = df_merge['Volumenproduccion'] * df_merge['precio_ajustado']
df_merge['utilidad_neta'] = df_merge['ingreso_total'] - df_merge['costo_operativo'].fillna(41000)
df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - df_merge['riesgo_probabilidad'].fillna(0.2))

def clasificar_icc(val):
    if val < 20000: return "Diversificación Urgente"
    if val > 80000: return "Alta Competitividad"
    return "Optimización Requerida"

df_merge['Estatus'] = df_merge['ICC'].apply(clasificar_icc)

# Aplicación del filtro de multiselección
df_final_filtrado = df_merge[df_merge['Estatus'].isin(filtro_estatus)]

# ─── Lógica de Visualización Segura ───────────────────────────────────────────
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")

# VALIDACIÓN CRÍTICA: Si el DataFrame resultante está vacío, detiene el renderizado
if df_final_filtrado.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados. Por favor, ajuste los criterios en la barra lateral.")
else:
    if modelo_inversion:
        df_dictamen, df_proyeccion = modelo_inversion.evaluar_estrategia_inversion(df_final_filtrado)
        # Verificación de existencia de columna antes de indexar (Previene el KeyError: 'Mes')
        if not df_proyeccion.empty and 'Mes' in df_proyeccion.columns:
            df_mes = df_proyeccion[df_proyeccion['Mes'] == mes_actual].sort_values(by='Rentabilidad_Proyectada', ascending=False)
        else:
            df_mes = pd.DataFrame()
    else:
        df_dictamen, df_mes = pd.DataFrame(), pd.DataFrame()

    # ─── Renderizado de Dashboards ───
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Utilidad Neta Acumulada", f"${df_final_filtrado['utilidad_neta'].sum():,.2f}")
    with col2:
        st.metric("ICC Promedio Regional", f"{df_final_filtrado['ICC'].mean():,.0f} pts")
    with col3:
        if not df_mes.empty:
            st.metric(f"Mejor Opción ({mes_actual})", df_mes.iloc[0]['Nomcultivo'])

    st.markdown("---")

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("#### Evolución de Precios Ajustados")
        fig_line = px.line(df_final_filtrado.groupby('Anio')['precio_ajustado'].mean().reset_index(), x='Anio', y='precio_ajustado')
        fig_line.update_traces(line_color=CYAN, line_width=3)
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("#### Análisis de Competitividad por Cultivo")
        fig_bar = px.bar(df_final_filtrado.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("#### Diagnóstico Operativo y Solvencia")
    st.dataframe(
        df_final_filtrado[['Anio', 'Nomcultivo', 'ICC', 'costo_operativo', 'Estatus']].style
            .map(lambda x: f'background-color: {RED if "Urgente" in str(x) else (GREEN if "Alta" in str(x) else AMBER)}; color: {"white" if "Urgente" in str(x) else "#000"}; font-weight: bold;', subset=['Estatus'])
            .format({'ICC': '{:,.0f}', 'costo_operativo': '${:,.2f}'}),
        use_container_width=True, hide_index=True
    )
    
    csv = df_final_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar Dictamen (CSV)", csv, f"Reporte_{municipio}.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)