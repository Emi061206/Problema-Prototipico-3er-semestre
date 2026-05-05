import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import integrate

# Configura la página de Streamlit con título, ancho de diseño y estado inicial de la barra lateral.
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide", initial_sidebar_state="expanded")

# Definición de la paleta de colores usada en el dashboard.
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"

# Inyección de estilos CSS personalizados para mejorar la apariencia visual de la app.
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

@st.cache_data
# Carga el archivo CSV desde disco y lo almacena en caché para evitar recarga constante.
def extraer_datos_csv():
    directorio = os.path.dirname(__file__)
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    return pd.read_csv(ruta)

# Intenta obtener datos de una base de datos SQL; si falla, devuelve un conjunto de datos de respaldo.
def extraer_datos_sql():
    try:
        from database import obtener_conexion
        engine = obtener_conexion()
        q_cultivos = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad FROM catalogo_cultivos"
        q_municipios = "SELECT nombre, tipo_suelo, mod_rendimiento, mod_costo, mod_riesgo FROM municipios"
        return pd.read_sql(q_cultivos, engine), pd.read_sql(q_municipios, engine)
    except Exception:
        # Datos estáticos para poder mostrar la aplicación sin requerir conexión a la base de datos.
        d_cultivos = pd.DataFrame({
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'],
            'costo_operativo': [41000.0, 65000.0, 55000.0, 38000.0],
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04],
            'riesgo_probabilidad': [0.35, 0.10, 0.20, 0.25]
        })
        d_municipios = pd.DataFrame({
            'nombre': ['Temixco', 'Cuautla', 'Jiutepec'],
            'tipo_suelo': ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'],
            'mod_rendimiento': [1.15, 1.0, 0.95],
            'mod_costo': [0.95, 1.05, 1.10],
            'mod_riesgo': [0.85, 1.0, 1.10]
        })
        return d_cultivos, d_municipios

# Carga los datos históricos y de catálogo para todo el análisis.
df_historico = extraer_datos_csv()
df_catalogo, df_municipios = extraer_datos_sql()

# Definición de factores fenológicos por cultivo y mes para simular variación estacional.
matriz_fenologica = {
    'Higo': {
        'Enero': 0.9, 'Febrero': 0.9, 'Marzo': 1.0, 'Abril': 1.1,
        'Mayo': 1.2, 'Junio': 1.2, 'Julio': 1.1, 'Agosto': 1.0,
        'Septiembre': 0.9, 'Octubre': 0.9, 'Noviembre': 0.8, 'Diciembre': 0.8
    },
    'Maíz grano': {
        'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.2,
        'Mayo': 1.2, 'Junio': 1.5, 'Julio': 1.0, 'Agosto': 1.0,
        'Septiembre': 0.8, 'Octubre': 0.8, 'Noviembre': 0.0, 'Diciembre': 0.0
    },
    'Caña de azúcar': {
        'Enero': 1.3, 'Febrero': 1.4, 'Marzo': 1.5, 'Abril': 1.4,
        'Mayo': 1.2, 'Junio': 0.5, 'Julio': 0.5, 'Agosto': 0.5,
        'Septiembre': 0.5, 'Octubre': 0.5, 'Noviembre': 1.0, 'Diciembre': 1.2
    },
    'Sorgo grano': {
        'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.5,
        'Mayo': 1.0, 'Junio': 1.3, 'Julio': 1.2, 'Agosto': 1.0,
        'Septiembre': 0.8, 'Octubre': 0.5, 'Noviembre': 0.0, 'Diciembre': 0.0
    }
}

# Reglas de siembra recomendada por cultivo para referencias de planeación.
mes_siembra_optimo = {
    'Higo': 'Febrero - Marzo',
    'Maíz grano': 'Mayo - Junio (PV)',
    'Caña de azúcar': 'Julio - Agosto',
    'Sorgo grano': 'Mayo - Junio (PV)'
}

# Volatilidad de mercado usada para simular precios futuros.
volatilidad_mercado = {'Higo': 0.12, 'Maíz grano': 0.25, 'Caña de azúcar': 0.08, 'Sorgo grano': 0.20}
np.random.seed(42)

# Interfaz de usuario para seleccionar municipio, mes y rango anual.
st.sidebar.header("Panel de Control")
municipio = st.sidebar.selectbox("Seleccione Municipio:", df_municipios['nombre'].unique())
mes_actual = st.sidebar.selectbox("Mes de Análisis:", list(matriz_fenologica['Higo'].keys()))
anio_range = st.sidebar.slider("Periodo:", 2018, 2026, (2018, 2026))

# Obtiene los modificadores físicos y de riesgo del municipio seleccionado.
datos_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
mod_rend = datos_mun['mod_rendimiento']
mod_costo = datos_mun['mod_costo']
mod_riesgo = datos_mun['mod_riesgo']

# Muestra la información geográfica y de rendimiento del municipio seleccionado.
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Edafología:** {datos_mun['tipo_suelo']}")
st.sidebar.markdown(f"**Rendimiento:** x{mod_rend} | **Costo:** x{mod_costo}")

# Filtra los datos históricos para el municipio y rango anual elegidos.
df_f = df_historico[(df_historico['Nommunicipio'] == municipio) & (df_historico['Anio'] >= anio_range[0]) & (df_historico['Anio'] <= min(2024, anio_range[1]))].copy()
# Une la información histórica con el catálogo de cultivos para obtener parámetros económicos.
df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')

# Calcula precios ajustados y costos con primas de sostenibilidad y factores del municipio.
df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
df_merge['costo_ajustado'] = df_merge['costo_operativo'].fillna(41000) * mod_costo
# Calcula la utilidad neta en base al volumen producido y al precio ajustado.
df_merge['utilidad_neta'] = ((df_merge['Volumenproduccion'] * mod_rend) * df_merge['precio_ajustado']) - df_merge['costo_ajustado']
# El ICC es una medida de competitividad que penaliza por riesgo.
df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - (df_merge['riesgo_probabilidad'].fillna(0.2) * mod_riesgo))
df_merge['Tipo_Dato'] = 'Histórico'

# Genera proyecciones si el rango anual seleccionado incluye años futuros.
if anio_range[1] > 2024:
    anios_futuros = [a for a in range(max(2025, anio_range[0]), anio_range[1] + 1)]
    filas_proyectadas = []
    
    for anio in anios_futuros:
        for _, row in df_catalogo.iterrows():
            cultivo = row['nombre_cultivo']
            costo = row['costo_operativo']
            prima = row['prima_sostenibilidad']
            riesgo = row['riesgo_probabilidad']
            
            multiplicador_biologico = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
            precio_base = 31496 if cultivo == 'Higo' else 5516
            precio_estacional = precio_base * multiplicador_biologico
            desviacion = precio_estacional * volatilidad_mercado.get(cultivo, 0.15)
            
            precios_simulados = np.random.normal(loc=precio_estacional, scale=desviacion, size=1000)
            precio_esperado = np.mean(precios_simulados)
            precio_ajustado_esp = precio_esperado * (1 + prima)
            costo_aj = costo * mod_costo
            utilidad_esperada = ((10 * mod_rend * multiplicador_biologico) * precio_ajustado_esp) - costo_aj
            icc_esperado = utilidad_esperada * (1 - (riesgo * mod_riesgo))
            
            filas_proyectadas.append({
                'Nommunicipio': municipio,
                'Anio': anio,
                'Nomcultivo': cultivo,
                'Volumenproduccion': 10 * mod_rend * multiplicador_biologico,
                'Preciomediorural': precio_esperado,
                'costo_operativo': costo,
                'costo_ajustado': costo_aj,
                'prima_sostenibilidad': prima,
                'riesgo_probabilidad': riesgo,
                'precio_ajustado': precio_ajustado_esp,
                'utilidad_neta': utilidad_esperada,
                'ICC': icc_esperado,
                'Tipo_Dato': 'Proyección Monte Carlo'
            })
            
    if filas_proyectadas:
        df_proyectado = pd.DataFrame(filas_proyectadas)
        df_merge = pd.concat([df_merge, df_proyectado], ignore_index=True)

# Clasifica la competitividad de cada cultivo según su ICC.
clasificar_icc = lambda val: "Diversificación Urgente" if val < 20000 else ("Alta Competitividad" if val > 80000 else "Optimización Requerida")
df_merge['Estatus'] = df_merge['ICC'].apply(clasificar_icc)

# Título principal de la aplicación.
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")

# Genera pestañas para separar las vistas de análisis.
tab_dash, tab_math, tab_pred = st.tabs(["Dashboard Operativo", "Evaluación Regional (Integrales)", "Motor Predictivo (Monte Carlo)"])

with tab_dash:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Utilidad Neta Acumulada", f"${df_merge['utilidad_neta'].sum():,.2f}")
    with col2:
        st.metric("ICC Promedio Regional", f"{df_merge['ICC'].mean():,.0f} pts")

    # Sección de visualización de barras para comparar la competitividad promedio por cultivo.
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("#### Análisis de Competitividad Histórica y Proyectada")
    fig_bar = px.bar(df_merge.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
    fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla de dictamen operativo con formato condicional para exponer el estado de riesgo.
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown(f"#### Dictamen Operativo (Periodo: {anio_range[0]} - {anio_range[1]})")
    st.dataframe(
        df_merge[['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'Estatus']].style
            .map(lambda x: f'background-color: {RED if "Urgente" in str(x) else (GREEN if "Alta" in str(x) else AMBER)}; color: {"white" if "Urgente" in str(x) else "#000"}; font-weight: bold;', subset=['Estatus'])
            .format({'ICC': '{:,.0f}', 'costo_ajustado': '${:,.2f}'}),
        use_container_width=True, hide_index=True
    )
    csv = df_merge.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar Dictamen (CSV)", csv, f"Reporte_{municipio}_{anio_range[0]}_{anio_range[1]}.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_math:
    st.markdown("### Superficie de Rentabilidad y Volumen de Utilidad Acumulada")

    # Define las funciones de utilidad para cada cultivo con su respectivo módulo de costo.
    func_maiz = lambda y, x: (16.5 * mod_rend) - (0.5 * x * mod_costo) - (0.2 * y * mod_costo)
    func_higo = lambda y, x: (120 * mod_rend) - (0.8 * x * mod_costo) - (0.1 * y * mod_costo)

    lim_x_inf, lim_x_sup = 0, 5
    lim_y_inf, lim_y_sup = lambda x: 0, lambda x: 3

    # Integra el volumen de utilidad en un dominio continuo de superficie y tecnificación hídrica.
    vol_maiz, _ = integrate.dblquad(func_maiz, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)
    vol_higo, _ = integrate.dblquad(func_higo, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Volumen de Utilidad (Higo)", f"${vol_higo * 1000:,.2f} MXN", delta="Alta Competitividad")
    with c2:
        st.metric("Volumen de Utilidad (Maíz)", f"${vol_maiz * 1000:,.2f} MXN", delta="Diversificación Urgente", delta_color="inverse")
    with c3:
        diferencial = (vol_higo - vol_maiz) * 1000
        st.metric("Brecha de Capitalización", f"${diferencial:,.2f} MXN", delta="Ganancia Maximizada")

    x_vals = np.linspace(lim_x_inf, lim_x_sup, 50)
    y_vals = np.linspace(0, 3, 50)
    x_grid, y_grid = np.meshgrid(x_vals, y_vals)

    z_maiz = np.vectorize(lambda x, y: func_maiz(y, x))(x_grid, y_grid)
    z_higo = np.vectorize(lambda x, y: func_higo(y, x))(x_grid, y_grid)

    fig_3d = go.Figure()

    fig_3d.add_trace(go.Surface(z=z_higo, x=x_grid, y=y_grid, colorscale='Tealgrn', name='Plano Higo', showscale=False, opacity=0.9))
    fig_3d.add_trace(go.Surface(z=z_maiz, x=x_grid, y=y_grid, colorscale='OrRd', name='Plano Maíz', showscale=False, opacity=0.8))

    fig_3d.update_layout(
        title=f"Proyección Tridimensional Topográfica - {municipio}",
        scene=dict(xaxis_title='Hectáreas (x)', yaxis_title='Intensidad de Riego (y)', zaxis_title='Utilidad Unitaria', bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=True, gridcolor=BORDER), yaxis=dict(showgrid=True, gridcolor=BORDER), zaxis=dict(showgrid=True, gridcolor=BORDER)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, b=0, t=50), height=600
    )

    st.plotly_chart(fig_3d, use_container_width=True)

with tab_pred:
    st.markdown("### Motor de Predicción Estacional (Simulación Probabilística)")
    st.info(f"Proyección calculada para: **{mes_actual} del Año en curso** - Suelo: **{datos_mun['tipo_suelo']}**")
    
    def simular_cultivo(row):
        cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
        
        multiplicador_biologico = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
        
        precio_base = 31496 if cultivo == 'Higo' else 5516
        precio_estacional = precio_base * multiplicador_biologico
        desviacion = precio_estacional * volatilidad_mercado.get(cultivo, 0.15)
        
        precios_simulados = np.random.normal(loc=precio_estacional, scale=desviacion, size=1000)
        
        utilidades_simuladas = ((10 * mod_rend * multiplicador_biologico) * (precios_simulados * (1 + prima))) - (costo * mod_costo)
        icc_simulados = utilidades_simuladas * (1 - (riesgo * mod_riesgo))
        
        prob_exito = (np.sum(icc_simulados > 0) / 1000) * 100
        recomendacion_siembra = mes_siembra_optimo.get(cultivo, 'No definido')
        
        return pd.Series([cultivo, prob_exito, np.mean(icc_simulados), recomendacion_siembra])

    df_prediccion = df_catalogo.apply(simular_cultivo, axis=1)
    df_prediccion.columns = ['Cultivo', 'Probabilidad de Éxito (%)', 'ICC Esperado', 'Época de Siembra']
    df_prediccion = df_prediccion.sort_values(by='Probabilidad de Éxito (%)', ascending=False)
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown(f"#### Recomendación del Algoritmo")
        st.metric("Cultivo Óptimo Sugerido", df_prediccion.iloc[0]['Cultivo'])
        st.metric("Confianza Estadística", f"{df_prediccion.iloc[0]['Probabilidad de Éxito (%)']:.1f}%")
        
        st.markdown("#### Ventanas de Cultivo Oficiales (SIAP)")
        st.dataframe(df_prediccion[['Cultivo', 'Época de Siembra']], hide_index=True)
    
    with c2:
        st.markdown("#### Matriz de Probabilidad de Éxito (Monte Carlo)")
        fig_prob = px.bar(df_prediccion, x='Probabilidad de Éxito (%)', y='Cultivo', orientation='h', color='Probabilidad de Éxito (%)', color_continuous_scale='Tealgrn', range_x=[0, 100])
        fig_prob.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        st.plotly_chart(fig_prob, use_container_width=True)