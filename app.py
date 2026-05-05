# Importación de librerías necesarias
import os # Para manejo de rutas y archivos del sistema
import streamlit as st # Framework principal para crear la interfaz web del dashboard
import pandas as pd # Para manipulación y análisis de datos tabulares (DataFrames)
import numpy as np # Para cálculos numéricos y generación de números aleatorios (Monte Carlo)
import plotly.graph_objects as go # Para crear gráficos interactivos avanzados (ej. gráficos 3D)
import plotly.express as px # Para crear gráficos interactivos de forma rápida y sencilla
from scipy import integrate # Para realizar cálculos de integración matemática (cálculo de volumen)

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide", initial_sidebar_state="expanded")

# Definición de paleta de colores para la interfaz
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"

# Inyección de código CSS personalizado para estilizar la aplicación
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

# Función para extraer datos históricos de un archivo CSV local
@st.cache_data # Utiliza caché para no recargar los datos en cada interacción
def extraer_datos_csv():
    directorio = os.path.dirname(__file__)
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    if not os.path.exists(ruta): # Retorna DataFrame vacío si no existe el archivo
        return pd.DataFrame(columns=['Nommunicipio', 'Anio', 'Nomcultivo', 'Volumenproduccion', 'Preciomediorural'])
    return pd.read_csv(ruta)

# Función para simular/extraer datos de catálogos desde una base de datos SQL
def extraer_datos_sql():
    try:
        from database import obtener_conexion
        engine = obtener_conexion()
        # Consultas SQL para obtener información de cultivos y municipios
        q_cultivos = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad, inversion_infraestructura FROM catalogo_cultivos"
        q_municipios = "SELECT nombre, tipo_suelo, mod_rendimiento, mod_costo, mod_riesgo FROM municipios"
        return pd.read_sql(q_cultivos, engine), pd.read_sql(q_municipios, engine)
    except Exception:
        # Datos de respaldo (mock data) en caso de que falle la conexión a la base de datos
        d_cultivos = pd.DataFrame({
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'],
            'costo_operativo': [32057.66, 105100.0, 55000.0, 38000.0],
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04],
            'riesgo_probabilidad': [0.35, 0.08, 0.20, 0.25],
            'inversion_infraestructura': [0.0, 147000.0, 0.0, 0.0]
        })
        d_municipios = pd.DataFrame({
            'nombre': ['Temixco', 'Cuautla', 'Jiutepec'],
            'tipo_suelo': ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'],
            'mod_rendimiento': [1.15, 1.0, 0.95],
            'mod_costo': [0.95, 1.05, 1.10],
            'mod_riesgo': [0.85, 1.0, 1.10]
        })
        return d_cultivos, d_municipios

# Carga de los datos en DataFrames
df_historico = extraer_datos_csv()
df_catalogo, df_municipios = extraer_datos_sql()

# Matriz fenológica: multiplicadores de rendimiento según el mes de siembra para cada cultivo
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

# Diccionario con los meses óptimos de siembra sugeridos por cultivo
mes_siembra_optimo = {
    'Higo': 'Febrero - Marzo',
    'Maíz grano': 'Mayo - Junio (PV)',
    'Caña de azúcar': 'Julio - Agosto',
    'Sorgo grano': 'Mayo - Junio (PV)'
}

# Tasas de volatilidad de mercado por cultivo (usado para simulaciones de Monte Carlo)
volatilidad_mercado = {'Higo': 0.12, 'Maíz grano': 0.25, 'Caña de azúcar': 0.08, 'Sorgo grano': 0.20}
np.random.seed(42) # Fijar semilla para reproducibilidad de las simulaciones

# Configuración del menú lateral (Sidebar) para los filtros del usuario
st.sidebar.header("Panel de Control")
municipio = st.sidebar.selectbox("Seleccione Municipio:", df_municipios['nombre'].unique())
mes_actual = st.sidebar.selectbox("Mes de Análisis:", list(matriz_fenologica['Higo'].keys()))
anio_range = st.sidebar.slider("Periodo:", 2018, 2026, (2018, 2026))

# Obtención de los parámetros específicos del municipio seleccionado
datos_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
mod_rend = datos_mun['mod_rendimiento']
mod_costo = datos_mun['mod_costo']
mod_riesgo = datos_mun['mod_riesgo']

# Mostrar información edafológica y modificadores en el menú lateral
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Edafología:** {datos_mun['tipo_suelo']}")
st.sidebar.markdown(f"**Rendimiento:** x{mod_rend} | **Costo:** x{mod_costo}")

# Filtrado de los datos históricos según los parámetros del usuario (municipio y años)
df_f = df_historico[(df_historico['Nommunicipio'] == municipio) & (df_historico['Anio'] >= anio_range[0]) & (df_historico['Anio'] <= min(2024, anio_range[1]))].copy()

# Cálculo de indicadores financieros para los datos históricos
if not df_f.empty:
    df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')
    # Ajustar precio sumando la prima de sostenibilidad
    df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
    # Ajustar costo operativo con el modificador del municipio
    df_merge['costo_ajustado'] = df_merge['costo_operativo'].fillna(32057.66) * mod_costo
    # Calcular utilidad neta: (Ingresos) - (Costos)
    df_merge['utilidad_neta'] = ((df_merge['Volumenproduccion'] * mod_rend) * df_merge['precio_ajustado']) - df_merge['costo_ajustado']
    # Calcular ICC (Índice de Competitividad Comercial) penalizado por riesgo
    df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - (df_merge['riesgo_probabilidad'].fillna(0.2) * mod_riesgo))
    df_merge['Tipo_Dato'] = 'Histórico'
else:
    # DataFrame vacío si no hay datos en el rango histórico
    df_merge = pd.DataFrame(columns=['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'utilidad_neta'])

# Generación de proyecciones futuras (Monte Carlo) si el usuario seleccionó años mayores a 2024
if anio_range[1] > 2024:
    anios_futuros = [a for a in range(max(2025, anio_range[0]), anio_range[1] + 1)]
    filas_proyectadas = []
    
    for anio in anios_futuros:
        for _, row in df_catalogo.iterrows():
            # Extraer características del cultivo
            cultivo = row['nombre_cultivo']
            costo = row['costo_operativo']
            prima = row['prima_sostenibilidad']
            riesgo = row['riesgo_probabilidad']
            
            # Obtener multiplicadores y establecer variables de simulación
            multiplicador_biologico = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
            precio_base = 34994.18 if cultivo == 'Higo' else 5516.0
            precio_estacional = precio_base * multiplicador_biologico
            desviacion = precio_estacional * volatilidad_mercado.get(cultivo, 0.15)
            
            # Simulación de Monte Carlo (1000 iteraciones) para predecir precios
            precios_simulados = np.random.normal(loc=precio_estacional, scale=desviacion, size=1000)
            precio_esperado = np.mean(precios_simulados) # Promedio de los precios simulados
            precio_ajustado_esp = precio_esperado * (1 + prima)
            costo_aj = costo * mod_costo
            
            # Definir volúmenes esperados e iniciar cálculo de utilidad
            vol_esp = 6.82 if cultivo == 'Higo' else 3.5
            utilidad_esperada = ((vol_esp * mod_rend * multiplicador_biologico) * precio_ajustado_esp) - costo_aj
            
            # Ajustes financieros específicos para el cultivo de Higo (ej. hidroponía)
            if cultivo == 'Higo':
                utilidad_esperada += 117600.00 # Ingreso bruto hidropónico constante
                utilidad_esperada -= 35536.00 # Amortización CAPEX anual opcional o ajuste OPEX
                
            # Calcular ICC esperado para la proyección
            icc_esperado = utilidad_esperada * (1 - (riesgo * mod_riesgo))
            
            # Agregar la fila proyectada a la lista
            filas_proyectadas.append({
                'Nommunicipio': municipio, 'Anio': anio, 'Nomcultivo': cultivo,
                'Volumenproduccion': vol_esp * mod_rend * multiplicador_biologico,
                'Preciomediorural': precio_esperado, 'costo_operativo': costo,
                'costo_ajustado': costo_aj, 'prima_sostenibilidad': prima,
                'riesgo_probabilidad': riesgo, 'precio_ajustado': precio_ajustado_esp,
                'utilidad_neta': utilidad_esperada, 'ICC': icc_esperado, 'Tipo_Dato': 'Proyección Monte Carlo'
            })
            
    # Concatenar los datos históricos con los datos proyectados
    if filas_proyectadas:
        df_proyectado = pd.DataFrame(filas_proyectadas)
        df_merge = pd.concat([df_merge, df_proyectado], ignore_index=True)

# Función anónima para clasificar el estado de competitividad basado en el ICC
clasificar_icc = lambda val: "Diversificación Urgente" if val < 20000 else ("Alta Competitividad" if val > 200000 else "Optimización Requerida")
df_merge['Estatus'] = df_merge['ICC'].apply(clasificar_icc)

# Título principal de la aplicación web
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")

# Creación de pestañas para organizar la información
tab_dash, tab_math, tab_pred = st.tabs(["Dashboard Operativo", "Evaluación Regional (Integrales)", "Motor Predictivo (Monte Carlo)"])

# ----- PESTAÑA 1: Dashboard Operativo -----
with tab_dash:
    # Mostrar métricas principales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Utilidad Neta Acumulada", f"${df_merge['utilidad_neta'].sum():,.2f}")
    with col2:
        st.metric("ICC Promedio Regional", f"{df_merge['ICC'].mean():,.0f} pts")

    # Gráfico de barras horizontales mostrando el ICC por cultivo
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("#### Análisis de Competitividad Histórica y Proyectada")
    if not df_merge.empty:
        fig_bar = px.bar(df_merge.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla con el dictamen operativo de cada registro (histórico y proyectado)
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown(f"#### Dictamen Operativo (Periodo: {anio_range[0]} - {anio_range[1]})")
    if not df_merge.empty:
        # Aplicar estilos a la tabla dependiendo del estatus (semáforo de colores)
        st.dataframe(
            df_merge[['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'Estatus']].style
                .map(lambda x: f'background-color: {RED if "Urgente" in str(x) else (GREEN if "Alta" in str(x) else AMBER)}; color: {"white" if "Urgente" in str(x) else "#000"}; font-weight: bold;', subset=['Estatus'])
                .format({'ICC': '{:,.0f}', 'costo_ajustado': '${:,.2f}'}),
            use_container_width=True, hide_index=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ----- PESTAÑA 2: Evaluación Regional (Integrales) -----
with tab_math:
    st.markdown("### Superficie de Rentabilidad y Volumen de Utilidad Acumulada")
    # Funciones de rentabilidad para el maíz y el higo (superficies paramétricas)
    func_maiz = lambda y, x: ((16.548 * x * mod_rend) - ((19.8 + 12.257 * x) * mod_costo) - (0.2 * y * mod_costo))
    func_higo = lambda y, x: ((356.259 * x * mod_rend) - (105.1 * mod_costo) - (0.1 * (y**2) * mod_costo))

    # Cálculo del volumen bajo las superficies mediante integrales dobles
    lim_x_inf, lim_x_sup = 0, 5
    lim_y_inf, lim_y_sup = lambda x: 0, lambda x: 3
    vol_maiz, _ = integrate.dblquad(func_maiz, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)
    vol_higo, _ = integrate.dblquad(func_higo, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)

    # Mostrar métricas comparativas derivadas de las integrales
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Volumen de Utilidad (Higo)", f"${vol_higo * 1000:,.2f} MXN", delta="Alta Competitividad")
    with c2:
        st.metric("Volumen de Utilidad (Maíz)", f"${vol_maiz * 1000:,.2f} MXN", delta="Diversificación Urgente", delta_color="inverse")
    with c3:
        st.metric("Brecha de Capitalización", f"${(vol_higo - vol_maiz) * 1000:,.2f} MXN")

    # Generar la visualización 3D de las superficies de rentabilidad
    x_vals = np.linspace(lim_x_inf, lim_x_sup, 50)
    y_vals = np.linspace(0, 3, 50)
    x_grid, y_grid = np.meshgrid(x_vals, y_vals)
    z_maiz = np.vectorize(lambda x, y: func_maiz(y, x))(x_grid, y_grid)
    z_higo = np.vectorize(lambda x, y: func_higo(y, x))(x_grid, y_grid)

    fig_3d = go.Figure()
    fig_3d.add_trace(go.Surface(z=z_higo, x=x_grid, y=y_grid, colorscale='Tealgrn', name='Plano Higo', showscale=False, opacity=0.9))
    fig_3d.add_trace(go.Surface(z=z_maiz, x=x_grid, y=y_grid, colorscale='OrRd', name='Plano Maíz', showscale=False, opacity=0.8))
    fig_3d.update_layout(scene=dict(zaxis=dict(range=[-50, 1500])), paper_bgcolor="rgba(0,0,0,0)", height=600)
    st.plotly_chart(fig_3d, use_container_width=True)

# ----- PESTAÑA 3: Motor Predictivo (Monte Carlo) -----
with tab_pred:
    st.markdown("### Motor de Predicción Estacional (Simulación Probabilística)")
    
    # Función que simula escenarios para calcular probabilidades de éxito (utilidad > 0)
    def simular_cultivo(row):
        cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
        multiplicador_biologico = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
        precio_base = 34994.18 if cultivo == 'Higo' else 5516.0
        
        # Generar 1000 escenarios de precio usando distribución normal
        precios_simulados = np.random.normal(loc=precio_base * multiplicador_biologico, scale=(precio_base * 0.12), size=1000)
        vol_esp = 6.82 if cultivo == 'Higo' else 3.5
        
        # Calcular el arreglo de utilidades para cada simulación
        utilidades = ((vol_esp * mod_rend * multiplicador_biologico) * (precios_simulados * (1 + prima))) - (costo * mod_costo)
        if cultivo == 'Higo': utilidades += 59500.00 # Flujo neto 100m2 (Ajuste específico del Higo)
        
        # Calcular ICC para las simulaciones y la probabilidad de éxito (fracción > 0)
        icc_sim = utilidades * (1 - (riesgo * mod_riesgo))
        return pd.Series([cultivo, (np.sum(icc_sim > 0) / 1000) * 100, np.mean(icc_sim), mes_siembra_optimo.get(cultivo, 'N/D')])

    # Ejecutar la simulación sobre el catálogo y ordenar por probabilidad de éxito
    df_prediccion = df_catalogo.apply(simular_cultivo, axis=1)
    df_prediccion.columns = ['Cultivo', 'Probabilidad de Éxito (%)', 'ICC Esperado', 'Época de Siembra']
    df_prediccion = df_prediccion.sort_values(by='Probabilidad de Éxito (%)', ascending=False)
    
    # Mostrar resultados en métricas y gráfico de barras
    col_a, col_b = st.columns([1, 2])
    with col_a:
        # Recomendar el cultivo con mayor probabilidad de éxito
        st.metric("Cultivo Sugerido", df_prediccion.iloc[0]['Cultivo'])
        st.metric("Confianza Estadística", f"{df_prediccion.iloc[0]['Probabilidad de Éxito (%)']:.1f}%")
        st.dataframe(df_prediccion[['Cultivo', 'Época de Siembra']], hide_index=True)
    with col_b:
        # Gráfico con la probabilidad de éxito por cultivo
        fig_prob = px.bar(df_prediccion, x='Probabilidad de Éxito (%)', y='Cultivo', orientation='h', color_continuous_scale='Tealgrn', range_x=[0, 100])
        st.plotly_chart(fig_prob, use_container_width=True)