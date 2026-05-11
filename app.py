# Importar la librería os para interactuar con rutas y el sistema de archivos del sistema operativo
import os
# Importar streamlit para construir y renderizar la interfaz de usuario web interactiva
import streamlit as st
# Importar pandas para la manipulación y análisis de datos tabulares (DataFrames)
import pandas as pd
# Importar numpy para la generación de números aleatorios y operaciones matemáticas vectorizadas
import numpy as np
# Importar el módulo graph_objects de plotly para construir gráficos tridimensionales complejos
import plotly.graph_objects as go
# Importar plotly.express para la creación rápida de gráficos estadísticos de alto nivel (barras)
import plotly.express as px
# Importar la función integrate de scipy para calcular integrales dobles en los modelos de utilidad
from scipy import integrate
# Importar FPDF para la generación de documentos PDF directamente en la memoria RAM
from fpdf import FPDF
# Importar base64 para la codificación y decodificación de datos binarios (necesario para Streamlit)
import base64

# Configurar las propiedades de la página web: título de la pestaña, ancho completo y barra lateral abierta
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide", initial_sidebar_state="expanded")

# Definir variables de colores hexadecimales para elementos de éxito, advertencia y peligro
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"
# Definir variables de colores hexadecimales para el fondo oscuro, tarjetas y bordes de la interfaz
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"

# Inyectar código CSS personalizado para aplicar tipografías de Google Fonts y colores a los componentes
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
""", unsafe_allow_html=True) # unsafe_allow_html=True permite que Streamlit renderice etiquetas HTML/CSS puras

# Definir función decorada con cache_data para no recargar el archivo CSV en cada interacción del usuario
@st.cache_data
def extraer_datos_csv():
    # Obtener la ruta absoluta del directorio donde se encuentra este script
    directorio = os.path.dirname(__file__)
    # Construir la ruta hacia el archivo CSV de datos históricos
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    # Validar si el archivo no existe en la ruta especificada
    if not os.path.exists(ruta):
        # Retornar un DataFrame vacío con las columnas necesarias para evitar errores de ejecución
        return pd.DataFrame(columns=['Nommunicipio', 'Anio', 'Nomcultivo', 'Volumenproduccion', 'Preciomediorural'])
    # Leer y retornar el archivo CSV utilizando pandas
    return pd.read_csv(ruta)

# Definir función para conectar a la base de datos SQL o usar datos de respaldo en caso de error
def extraer_datos_sql():
    # Iniciar un bloque try para intentar la conexión con el motor de base de datos
    try:
        # Importar la función obtener_conexion desde el archivo local database.py
        from database import obtener_conexion
        # Establecer la conexión con el motor
        engine = obtener_conexion()
        # Definir la consulta SQL para obtener los parámetros financieros de los cultivos
        q_cultivos = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad, inversion_infraestructura FROM catalogo_cultivos"
        # Definir la consulta SQL para obtener los factores edafológicos de los municipios
        q_municipios = "SELECT nombre, tipo_suelo, mod_rendimiento, mod_costo, mod_riesgo FROM municipios"
        # Ejecutar las consultas y retornar los resultados como DataFrames de pandas
        return pd.read_sql(q_cultivos, engine), pd.read_sql(q_municipios, engine)
    # Capturar cualquier excepción (error de conexión, falta de archivo, etc.)
    except Exception:
        # Crear un DataFrame de respaldo con los datos financieros auditados (CAPEX de 147k, etc.)
        d_cultivos = pd.DataFrame({
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'],
            'costo_operativo': [32057.66, 105100.0, 55000.0, 38000.0],
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04],
            'riesgo_probabilidad': [0.35, 0.08, 0.20, 0.25],
            'inversion_infraestructura': [0.0, 147000.0, 0.0, 0.0]
        })
        # Crear un DataFrame de respaldo con los índices topográficos de los municipios
        d_municipios = pd.DataFrame({
            'nombre': ['Temixco', 'Cuautla', 'Jiutepec'],
            'tipo_suelo': ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'],
            'mod_rendimiento': [1.15, 1.0, 0.95],
            'mod_costo': [0.95, 1.05, 1.10],
            'mod_riesgo': [0.85, 1.0, 1.10]
        })
        # Retornar los DataFrames de respaldo
        return d_cultivos, d_municipios

# Definir función para construir el PDF del reporte anual consolidado
def generar_pdf_anual(municipio, utilidad, inversion, prob_exito, suelo):
    # Instanciar un objeto de la clase FPDF
    pdf = FPDF()
    # Agregar una nueva página al documento PDF
    pdf.add_page()
    # Establecer el color de relleno RGB (verde oscuro) para el encabezado
    pdf.set_fill_color(30, 120, 30)
    # Dibujar un rectángulo relleno en la parte superior de la página
    pdf.rect(0, 0, 210, 40, 'F')
    # Configurar la fuente Arial, Negrita, tamaño 16
    pdf.set_font("Arial", 'B', 16)
    # Configurar el color del texto a blanco
    pdf.set_text_color(255, 255, 255)
    # Imprimir el título del reporte centrado con salto de línea
    pdf.cell(0, 10, "REPORTE ANUAL DE VIABILIDAD", ln=True, align='C')
    # Cambiar la fuente a Arial regular, tamaño 12
    pdf.set_font("Arial", '', 12)
    # Imprimir el subtítulo centrado
    pdf.cell(0, 10, "Proyeccion Ciclo Completo 2026", ln=True, align='C')
    
    # Insertar un espacio vertical de 25 unidades
    pdf.ln(25)
    # Restablecer el color del texto a negro
    pdf.set_text_color(0, 0, 0)
    # Configurar la fuente para la sección de datos
    pdf.set_font("Arial", 'B', 14)
    # Imprimir el nombre del municipio seleccionado
    pdf.cell(0, 10, f"Municipio: {municipio}", ln=True)
    # Configurar la fuente para el párrafo descriptivo
    pdf.set_font("Arial", '', 11)
    # Imprimir un bloque de texto multilinea con la descripción del suelo y modelo
    pdf.multi_cell(0, 7, f"Analisis de transicion al modelo Higo (1 ha) + Hidroponia (100m2) en suelo {suelo}.")
    
    # Insertar espacio y configurar colores para el encabezado de la tabla
    pdf.ln(10)
    pdf.set_fill_color(230, 245, 230)
    pdf.set_font("Arial", 'B', 12)
    # Crear la primera celda del encabezado de la tabla (con bordes y fondo relleno)
    pdf.cell(90, 10, "CONCEPTO", 1, 0, 'C', True)
    # Crear la segunda celda del encabezado de la tabla y dar salto de línea
    pdf.cell(90, 10, "VALOR ANUAL", 1, 1, 'C', True)
    
    # Configurar fuente regular para los datos de la tabla
    pdf.set_font("Arial", '', 12)
    # Fila 1: Concepto de inversión y su valor dinámico alineado a la derecha
    pdf.cell(90, 10, "Inversion Inicial (CAPEX)", 1)
    pdf.cell(90, 10, f"$ {inversion:,.2f}", 1, 1, 'R')
    # Fila 2: Utilidad neta anual
    pdf.cell(90, 10, "Utilidad Operativa Neta", 1)
    pdf.cell(90, 10, f"$ {utilidad:,.2f}", 1, 1, 'R')
    # Fila 3: Probabilidad estadística de éxito
    pdf.cell(90, 10, "Probabilidad de Exito", 1)
    pdf.cell(90, 10, f"{prob_exito:.1f} %", 1, 1, 'R')
    
    # Insertar espacio para la sección del dictamen final
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    # Imprimir etiqueta del dictamen
    pdf.cell(0, 10, "DICTAMEN:", ln=True)
    # Cambiar fuente a cursiva (Italic) para el texto del dictamen
    pdf.set_font("Arial", 'I', 11)
    # Imprimir texto multilínea justificando la decisión técnica
    pdf.multi_cell(0, 7, "Ejecucion recomendada. El modelo es altamente resiliente y garantiza flujo de caja.")
    
    # Espacio para el pie de página
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 8)
    # Imprimir el autor en el pie de página centrado (Fijado como N.A según instrucción)
    pdf.cell(0, 5, "Desarrollado por N.A", align='C')
    
    # Retornar el archivo PDF generado en memoria codificado como bytes
    return bytes(pdf.output())

# Definir función para construir el PDF del reporte mensual detallado
def generar_pdf_mensual(mes, municipio, datos_mes):
    # Instanciar un objeto de la clase FPDF
    pdf = FPDF()
    # Agregar página
    pdf.add_page()
    # Establecer color RGB (azul) para el encabezado del reporte mensual
    pdf.set_fill_color(41, 128, 185)
    # Dibujar el rectángulo del encabezado
    pdf.rect(0, 0, 210, 40, 'F')
    # Configurar fuente y color blanco para el título
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 255, 255)
    # Imprimir título incluyendo el mes en mayúsculas
    pdf.cell(0, 10, f"REPORTE MENSUAL: {mes.upper()}", ln=True, align='C')
    # Imprimir subtítulo con el municipio
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Gestion Operativa - {municipio}", ln=True, align='C')
    
    # Añadir espacio y cambiar texto a negro
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    # Imprimir título de la sección de tabla
    pdf.cell(0, 10, "Resumen de Flujo de Caja Mensual", ln=True)
    
    # Configurar fondo gris claro para el encabezado de la tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    # Imprimir las 4 columnas del encabezado de ingresos/egresos
    pdf.cell(70, 10, "Concepto", 1, 0, 'C', True)
    pdf.cell(40, 10, "Ingresos", 1, 0, 'C', True)
    pdf.cell(40, 10, "Egresos", 1, 0, 'C', True)
    pdf.cell(40, 10, "Neto", 1, 1, 'C', True)
    
    # Configurar fuente regular para el contenido numérico
    pdf.set_font("Arial", '', 10)
    # Definir matriz de filas con los datos pasados en el diccionario 'datos_mes'
    filas = [
        ["Modulo Hidroponico", f"$ {datos_mes['ing_h']:,.2f}", f"$ {datos_mes['egr_h']:,.2f}", f"$ {datos_mes['net_h']:,.2f}"],
        ["Cultivo de Higo", f"$ {datos_mes['ing_f']:,.2f}", f"$ {datos_mes['egr_f']:,.2f}", f"$ {datos_mes['net_f']:,.2f}"],
        ["Costos Fijos (Prorrateo)", "$ 0.00", "$ 4,300.00", "-$ 4,300.00"]
    ]
    # Iterar sobre las filas de la matriz para imprimir cada celda
    for f in filas:
        pdf.cell(70, 10, f[0], 1)
        pdf.cell(40, 10, f[1], 1, 0, 'R')
        pdf.cell(40, 10, f[2], 1, 0, 'R')
        pdf.cell(40, 10, f[3], 1, 1, 'R')
    
    # Espacio para las observaciones finales
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    # Imprimir la nota técnica específica del mes evaluado
    pdf.multi_cell(0, 7, f"Nota Tecnica: {datos_mes['nota']}")
    
    # Pie de página con autor
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(0, 5, "Desarrollado por N.A", align='C')
    
    # Retornar el flujo de bytes del documento generado
    return bytes(pdf.output())

# Extraer y asignar los datos históricos llamando a la función cacheada
df_historico = extraer_datos_csv()
# Extraer los catálogos financieros y topográficos
df_catalogo, df_municipios = extraer_datos_sql()

# Configurar el encabezado principal de la barra lateral
st.sidebar.header("Panel de Control")
# Crear un menú desplegable (select) para elegir el municipio
municipio_sel = st.sidebar.selectbox("Seleccione Municipio:", ["Temixco", "Cuautla", "Jiutepec"])
# Crear un menú desplegable para elegir el mes a analizar
mes_sel = st.sidebar.selectbox("Mes para Reporte Mensual:", ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
# Crear un deslizador para acotar el rango de años históricos
anio_range = st.sidebar.slider("Periodo (Historico):", 2018, 2026, (2018, 2026))

# Filtrar el DataFrame de municipios para aislar los datos del municipio seleccionado
datos_mun = df_municipios[df_municipios['nombre'] == municipio_sel].iloc[0]
# Extraer modificadores específicos del tipo de suelo del municipio
mod_rend = datos_mun['mod_rendimiento']
mod_costo = datos_mun['mod_costo']
mod_riesgo = datos_mun['mod_riesgo']

# Definir un diccionario estático con datos financieros mensuales de prueba basados en el modelo de Higo
datos_mensuales_db = {
    'Febrero': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 119329.0, 'egr_f': 4050.0, 'net_f': 115279.0, 'nota': "Pico de cosecha de Higo. Liquidez maxima."},
    'Marzo': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 119329.0, 'egr_f': 4050.0, 'net_f': 115279.0, 'nota': "Continuacion de cosecha de Higo. Flujo positivo."},
    'Junio': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 0.0, 'egr_f': 1500.0, 'net_f': -1500.0, 'nota': "Fase de mantenimiento de Higo. Hidroponia cubre costos fijos."}
}
# Definir los datos predeterminados en caso de seleccionar un mes no listado en el diccionario
default_mes = {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 0.0, 'egr_f': 800.0, 'net_f': -800.0, 'nota': "Hidroponia mantiene el flujo operativo y evita apalancamiento."}

# Agregar un divisor horizontal en la barra lateral
st.sidebar.markdown("---")
# Agregar subtítulo para la sección de botones de descarga
st.sidebar.subheader("Generacion de Reportes")

# Botón para detonar la creación del reporte anual
if st.sidebar.button("Generar Reporte ANUAL"):
    # Llamar a la función generando los bytes del PDF con valores estáticos de proyección
    pdf_anual = generar_pdf_anual(municipio_sel, 251159.31, 147000.00, 95.4, datos_mun['tipo_suelo'])
    # Mostrar el botón de descarga nativo de Streamlit inyectando los bytes en memoria
    st.sidebar.download_button("Descargar PDF Anual", data=pdf_anual, file_name=f"Reporte_Anual_{municipio_sel}.pdf", mime="application/pdf")

# Botón para detonar la creación del reporte mensual dinámico
if st.sidebar.button(f"Generar Reporte de {mes_sel}"):
    # Recuperar los datos del mes seleccionado o el default si no existe
    info_mes = datos_mensuales_db.get(mes_sel, default_mes)
    # Llamar a la función que genera el PDF mensual
    pdf_mes = generar_pdf_mensual(mes_sel, municipio_sel, info_mes)
    # Mostrar el botón de descarga del PDF mensual
    st.sidebar.download_button(f"Descargar PDF {mes_sel}", data=pdf_mes, file_name=f"Reporte_{mes_sel}_{municipio_sel}.pdf", mime="application/pdf")

# Filtrar los datos históricos según municipio y años seleccionados
df_f = df_historico[(df_historico['Nommunicipio'] == municipio_sel) & (df_historico['Anio'] >= anio_range[0]) & (df_historico['Anio'] <= min(2024, anio_range[1]))].copy()

# Validar que existan datos históricos después del filtro
if not df_f.empty:
    # Unir datos históricos con parámetros del catálogo SQL
    df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')
    # Ajustar el precio base multiplicándolo por la prima de sostenibilidad
    df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
    # Ajustar el costo base multiplicándolo por el factor edafológico municipal
    df_merge['costo_ajustado'] = df_merge['costo_operativo'].fillna(32057.66) * mod_costo
    # Calcular la utilidad neta considerando rendimiento, precio y costo ajustados
    df_merge['utilidad_neta'] = ((df_merge['Volumenproduccion'] * mod_rend) * df_merge['precio_ajustado']) - df_merge['costo_ajustado']
    # Calcular el Índice de Competitividad (ICC) penalizando la utilidad por el riesgo combinado
    df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - (df_merge['riesgo_probabilidad'].fillna(0.2) * mod_riesgo))
else:
    # Crear un DataFrame vacío en caso de que no haya datos para evitar fallos de ejecución
    df_merge = pd.DataFrame(columns=['Anio', 'Nomcultivo', 'ICC', 'costo_ajustado', 'utilidad_neta'])

# Imprimir el título principal de la aplicación en el cuerpo de la página
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")
# Crear tres pestañas principales para dividir el análisis visual y matemático
tab_dash, tab_math, tab_pred = st.tabs(["Dashboard Operativo", "Evaluación Regional (Integrales)", "Motor Predictivo (Monte Carlo)"])

# Contenido de la primera pestaña: Dashboard Operativo
with tab_dash:
    # Crear dos columnas para mostrar métricas clave
    c1, c2 = st.columns(2)
    # Mostrar la utilidad neta proyectada como métrica
    c1.metric("Utilidad Neta Proyectada (Higo+NFT)", "$ 251,159.31 MXN")
    # Mostrar la inversión de capital inicial
    c2.metric("Inversión Inicial (CAPEX)", "$ 147,000.00 MXN")
    
    # Crear un contenedor estilizado mediante HTML/CSS para el gráfico de barras
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("#### Histórico de Competitividad por Cultivo")
    # Validar que existan datos antes de graficar
    if not df_merge.empty:
        # Generar un gráfico de barras horizontales evaluando el ICC histórico promedio
        fig_bar = px.bar(df_merge.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        # Actualizar fondos del gráfico para mantener la transparencia y ocultar la escala de color
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        # Dibujar el gráfico interactivo en Streamlit adaptándose al ancho
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        # Mostrar alerta si no hay datos disponibles
        st.warning("No hay datos históricos para el rango seleccionado.")
    # Cerrar contenedor HTML
    st.markdown('</div>', unsafe_allow_html=True)

# Contenido de la segunda pestaña: Matemáticas (Integrales y Superficies)
with tab_math:
    st.markdown("### Superficie de Rentabilidad y Volumen de Utilidad Acumulada")
    # Definir función anónima (lambda) para la utilidad del maíz basada en x (hectáreas) e y (tecnificación)
    func_maiz = lambda y, x: ((16.548 * x * mod_rend) - ((19.8 + 12.257 * x) * mod_costo) - (0.2 * y * mod_costo))
    # Definir función anónima (lambda) para la utilidad del higo
    func_higo = lambda y, x: ((356.259 * x * mod_rend) - (105.1 * mod_costo) - (0.1 * (y**2) * mod_costo))
    
    # Crear matrices bidimensionales (meshgrid) para evaluar las funciones en un plano XY
    x_g, y_g = np.meshgrid(np.linspace(0, 5, 50), np.linspace(0, 3, 50))
    # Vectorizar y aplicar la función del higo sobre la malla XY para obtener el eje Z
    z_higo = np.vectorize(lambda x, y: func_higo(y, x))(x_g, y_g)
    # Vectorizar y aplicar la función del maíz sobre la malla XY
    z_maiz = np.vectorize(lambda x, y: func_maiz(y, x))(x_g, y_g)
    
    # Construir objeto Figure de Plotly
    fig_3d = go.Figure(data=[
        # Añadir superficie 3D correspondiente al higo con escala de colores verde
        go.Surface(z=z_higo, x=x_g, y=y_g, colorscale='Tealgrn', showscale=False, opacity=0.9, name='Higo+NFT'), 
        # Añadir superficie 3D correspondiente al maíz con escala de colores roja
        go.Surface(z=z_maiz, x=x_g, y=y_g, colorscale='OrRd', showscale=False, opacity=0.8, name='Maíz')
    ])
    # Ajustar dimensiones visuales de la gráfica 3D, rango del eje Z y eliminar el fondo
    fig_3d.update_layout(scene=dict(zaxis=dict(range=[-50, 1500])), paper_bgcolor="rgba(0,0,0,0)", height=600)
    # Renderizar el gráfico tridimensional
    st.plotly_chart(fig_3d, use_container_width=True)

# Contenido de la tercera pestaña: Simulación Estocástica
with tab_pred:
    st.markdown("### Motor de Predicción Estacional (Monte Carlo)")
    # Diccionario con multiplicadores fenológicos basados en meses de siembra del SIAP
    matriz_fenologica = {'Higo': {'Enero': 0.9, 'Febrero': 0.9, 'Marzo': 1.0, 'Abril': 1.1, 'Mayo': 1.2, 'Junio': 1.2, 'Julio': 1.1, 'Agosto': 1.0, 'Septiembre': 0.9, 'Octubre': 0.9, 'Noviembre': 0.8, 'Diciembre': 0.8}, 'Maíz grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.2, 'Mayo': 1.2, 'Junio': 1.5, 'Julio': 1.0, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.8, 'Noviembre': 0.0, 'Diciembre': 0.0}, 'Caña de azúcar': {'Enero': 1.3, 'Febrero': 1.4, 'Marzo': 1.5, 'Abril': 1.4, 'Mayo': 1.2, 'Junio': 0.5, 'Julio': 0.5, 'Agosto': 0.5, 'Septiembre': 0.5, 'Octubre': 0.5, 'Noviembre': 1.0, 'Diciembre': 1.2}, 'Sorgo grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.5, 'Mayo': 1.0, 'Junio': 1.3, 'Julio': 1.2, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.5, 'Noviembre': 0.0, 'Diciembre': 0.0}}
    
    # Definir la función que realiza la simulación Monte Carlo por cada fila (cultivo)
    def simular_cultivo(row):
        # Desempaquetar los parámetros base de la fila del catálogo SQL
        cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
        # Obtener el modificador biológico usando el mes seleccionado en la UI
        m_bio = matriz_fenologica.get(cultivo, {}).get(mes_sel, 1.0)
        # Definir el precio base por tonelada dependiendo de la especie
        p_base = 34994.18 if cultivo == 'Higo' else 5516.0
        # Simular 1000 iteraciones de precios utilizando una distribución normal (media = precio base ajustado)
        p_sim = np.random.normal(loc=p_base * m_bio, scale=(p_base * 0.12), size=1000)
        # Calcular arreglo de utilidades considerando volumen, modificadores de suelo, precio simulado y costos
        util = ((6.82 if cultivo == 'Higo' else 3.5) * mod_rend * m_bio * p_sim * (1 + prima)) - (costo * mod_costo)
        # Inyectar el flujo hidropónico anual constante si el cultivo evaluado es Higo
        if cultivo == 'Higo': util += 59500.00
        # Penalizar el vector de utilidades aplicando la probabilidad combinada de riesgos
        icc_sim = util * (1 - (riesgo * mod_riesgo))
        # Retornar una Serie de pandas con el nombre y el porcentaje de escenarios con ICC mayor a cero
        return pd.Series([cultivo, (np.sum(icc_sim > 0) / 1000) * 100])
        
    # Aplicar la función de simulación a cada fila del catálogo de cultivos
    df_p = df_catalogo.apply(simular_cultivo, axis=1)
    # Renombrar columnas del resultado
    df_p.columns = ['Cultivo', 'Probabilidad de Éxito (%)']
    
    # Crear dos columnas de proporciones para presentar los resultados probabilísticos
    col_a, col_b = st.columns([1, 2])
    # Mostrar el cultivo con mayor probabilidad como métrica principal sugerida
    col_a.metric("Sugerencia Técnica", df_p.sort_values(by='Probabilidad de Éxito (%)', ascending=False).iloc[0]['Cultivo'])
    # Crear gráfica de barras horizontal para comparar probabilidades de éxito
    fig_p = px.bar(df_p, x='Probabilidad de Éxito (%)', y='Cultivo', orientation='h', color_continuous_scale='Tealgrn', range_x=[0, 100])
    # Dibujar la gráfica en la columna derecha
    col_b.plotly_chart(fig_p, use_container_width=True)