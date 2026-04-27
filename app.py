# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA INTELIGENTE DE MONITOREO AGROFORESTAL - MORELOS
# Aplicación web interactiva para análisis financiero de cultivos agrícolas
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Importaciones y Dependencias ─────────────────────────────────────────────
# Librerías necesarias para el funcionamiento de la aplicación
import os                      # Manejo de rutas del sistema de archivos
import streamlit as st         # Framework para crear interfaces web interactivas
import pandas as pd            # Manipulación y análisis de datos tabulares
import numpy as np             # Operaciones numéricas y cálculos matemáticos
import plotly.express as px    # Creación de gráficos interactivos
import importlib               # Carga dinámica de módulos Python
from sqlalchemy import create_engine  # Conexión a bases de datos SQL

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL DE LA INTERFAZ
# Define el título, layout y estado inicial de la página en Streamlit
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Smart Agroforestry Morelos",  # Título que aparece en la pestaña del navegador
    layout="wide",                            # Layout amplio para mejor visualización de gráficos
    initial_sidebar_state="expanded"          # La barra lateral comienza expandida
)

# ═══════════════════════════════════════════════════════════════════════════════
# IDENTIDAD VISUAL (Paleta de Colores Industrial)
# Define los colores del tema visual de la aplicación (estilo industrial/cyberpunk)
# ═══════════════════════════════════════════════════════════════════════════════
# Colores principales del tema
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"  # Colores neon para destacar elementos
# Colores de fondo y bordes
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"  # Fondo oscuro profesional

# Inyección de estilos CSS personalizados para personalizar la apariencia de Streamlit
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

# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO DE CONECTIVIDAD DE DATOS
# Funciones para cargar datos desde diferentes fuentes (CSV y SQL)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data  # Decorador que cachea el resultado para evitar recargas innecesarias
def extraer_datos_csv():
    """
    Carga los datos históricos agrícolas desde un archivo CSV local.
    Utiliza una ruta relativa que funciona en diferentes equipos.
    """
    directorio = os.path.dirname(__file__)  # Obtiene el directorio donde está este script
    # Construye la ruta absoluta al archivo CSV
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    return pd.read_csv(ruta)  # Lee y retorna el CSV como DataFrame

def extraer_datos_sql():
    """
    Intenta conectar a una base de datos SQL para obtener el catálogo de cultivos.
    Si falla, usa datos de respaldo predefinidos como fallback.
    """
    try:
        # Intenta importar la función de conexión desde el módulo database
        from database import obtener_conexion
        engine = obtener_conexion()  # Crea el motor de conexión a la base de datos
        # Query SQL para obtener datos de cultivos: nombre, costos, prima de sostenibilidad y riesgo
        query = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad FROM catalogo_cultivos"
        return pd.read_sql(query, engine)  # Ejecuta la consulta y retorna DataFrame
    except Exception:
        # Si falla la conexión, usa datos de respaldo hardcodeados
        data_respaldo = {
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'],
            'costo_operativo': [41000.0, 65000.0, 55000.0, 38000.0],
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04],
            'riesgo_probabilidad': [0.35, 0.10, 0.20, 0.25]
        }
        return pd.DataFrame(data_respaldo)  # Retorna DataFrame con datos de respaldo

# Carga los datos al iniciar la aplicación
df_historico = extraer_datos_csv()   # DataFrame con datos históricos de cultivos
df_catalogo = extraer_datos_sql()     # DataFrame con catálogo de cultivos (desde SQL o fallback)

# Intenta cargar un módulo adicional de modelo de inversión (opcional)
try:
    modelo_inversion = importlib.import_module("03_modelo_inversion")
except ImportError:
    modelo_inversion = None  # Si no existe el módulo, se asigna None

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL DE CONTROL (Barra Lateral)
# Widgets interactivos que permiten al usuario filtrar y seleccionar datos
# ═══════════════════════════════════════════════════════════════════════════════
st.sidebar.header("Panel de Control")  # Título de la barra lateral

# Selector desplegable para elegir el municipio
municipio = st.sidebar.selectbox("Seleccione Municipio:", df_historico['Nommunicipio'].unique())

# Selector desplegable para elegir el mes de análisis
mes_actual = st.sidebar.selectbox("Mes de Análisis:", 
    ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])

# Slider para seleccionar el rango de años del período de análisis
anio_range = st.sidebar.slider("Periodo:", int(df_historico['Anio'].min()), int(df_historico['Anio'].max()), (2018, 2024))

# Multiselect para filtrar por diagnóstico ICC (Índice de Competitividad del Cultivo)
filtro_estatus = st.sidebar.multiselect(
    "Filtrar por Diagnóstico ICC:",
    options=["Alta Competitividad", "Optimización Requerida", "Diversificación Urgente"],
    default=["Alta Competitividad", "Optimización Requerida"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR ANALÍTICO E INTEGRACIÓN
# Procesamiento de datos: filtrado, fusión de DataFrames y cálculos financieros
# ═══════════════════════════════════════════════════════════════════════════════

# Filtrado del DataFrame histórico por municipio y rango de años seleccionados
df_f = df_historico[(df_historico['Nommunicipio'] == municipio) & 
                    (df_historico['Anio'] >= anio_range[0]) & 
                    (df_historico['Anio'] <= anio_range[1])].copy()

# Fusión (merge) de los datos históricos con el catálogo de cultivos
# Combina las filas donde el nombre del cultivo coincida
df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')

# Cálculos financieros vectorizados (sin necesidad de bucles)
df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))  # Precio con prima de sostenibilidad
df_merge['ingreso_total'] = df_merge['Volumenproduccion'] * df_merge['precio_ajustado']  # Ingreso = volumen × precio ajustado
df_merge['utilidad_neta'] = df_merge['ingreso_total'] - df_merge['costo_operativo'].fillna(41000)  # Utilidad = ingreso - costo operativo

# Cálculo del ICC (Índice de Competitividad del Cultivo)
# Pondera la utilidad neta contra la probabilidad de riesgo
df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - df_merge['riesgo_probabilidad'].fillna(0.2))

def clasificar_icc(val):
    """
    Clasifica el estado de competitividad del cultivo según el valor del ICC.
    """
    if val < 20000: return "Diversificación Urgente"    # ICC bajo: requiere cambio de cultivo
    if val > 80000: return "Alta Competitividad"        # ICC alto: cultivo rentable y seguro
    return "Optimización Requerida"                     # ICC medio: requiere mejoras

# Aplica la función de clasificación a cada fila del DataFrame
df_merge['Estatus'] = df_merge['ICC'].apply(clasificar_icc)

# Aplica el filtro de multiselección seleccionado en la barra lateral
df_final_filtrado = df_merge[df_merge['Estatus'].isin(filtro_estatus)]

# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE VISUALIZACIÓN SEGURA
# Renderizado condicional de dashboards y métricas con validación de datos
# ═══════════════════════════════════════════════════════════════════════════════

# Título principal de la aplicación
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")

# VALIDACIÓN CRÍTICA: Si el DataFrame resultante está vacío, detiene el renderizado
# Muestra un mensaje de advertencia al usuario indicando que ajuste los filtros
if df_final_filtrado.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados. Por favor, ajuste los criterios en la barra lateral.")
else:
    # Si existe el módulo de modelo de inversión, lo utiliza para obtener proyecciones
    if modelo_inversion:
        df_dictamen, df_proyeccion = modelo_inversion.evaluar_estrategia_inversion(df_final_filtrado)
        # Verificación de existencia de columna antes de indexar (Previene el KeyError: 'Mes')
        if not df_proyeccion.empty and 'Mes' in df_proyeccion.columns:
            # Filtra las proyecciones para el mes seleccionado y ordena por rentabilidad
            df_mes = df_proyeccion[df_proyeccion['Mes'] == mes_actual].sort_values(by='Rentabilidad_Proyectada', ascending=False)
        else:
            df_mes = pd.DataFrame()  # DataFrame vacío si no hay datos de proyección
    else:
        df_dictamen, df_mes = pd.DataFrame(), pd.DataFrame()

    # ═══════════════════════════════════════════════════════════════════════════
    # RENDERIZADO DE DASHBOARDS
    # Muestra las métricas clave en tres columnas
    # ═══════════════════════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Utilidad Neta Acumulada", f"${df_final_filtrado['utilidad_neta'].sum():,.2f}")
    with col2:
        st.metric("ICC Promedio Regional", f"{df_final_filtrado['ICC'].mean():,.0f} pts")
    with col3:
        if not df_mes.empty:
            st.metric(f"Mejor Opción ({mes_actual})", df_mes.iloc[0]['Nomcultivo'])

    st.markdown("---")

    # Gráficos en dos columnas: evolución de precios y competitividad por cultivo
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("#### Evolución de Precios Ajustados")
        # Gráfico de línea que muestra la tendencia del precio ajustado por año
        fig_line = px.line(df_final_filtrado.groupby('Anio')['precio_ajustado'].mean().reset_index(), x='Anio', y='precio_ajustado')
        fig_line.update_traces(line_color=CYAN, line_width=3)
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("#### Análisis de Competitividad por Cultivo")
        # Gráfico de barras horizontales que muestra el ICC promedio por cultivo
        fig_bar = px.bar(df_final_filtrado.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabla detallada con diagnóstico operativo y solvencia
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("#### Diagnóstico Operativo y Solvencia")
    st.dataframe(
        df_final_filtrado[['Anio', 'Nomcultivo', 'ICC', 'costo_operativo', 'Estatus']].style
            .map(lambda x: f'background-color: {RED if "Urgente" in str(x) else (GREEN if "Alta" in str(x) else AMBER)}; color: {"white" if "Urgente" in str(x) else "#000"}; font-weight: bold;', subset=['Estatus'])
            .format({'ICC': '{:,.0f}', 'costo_operativo': '${:,.2f}'}),
        use_container_width=True, hide_index=True
    )
    
    # Botón para exportar los datos filtrados en formato CSV
    csv = df_final_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar Dictamen (CSV)", csv, f"Reporte_{municipio}.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)