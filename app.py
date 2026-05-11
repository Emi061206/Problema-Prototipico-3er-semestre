# Importación de la librería 'os' para interactuar con el sistema operativo (rutas de archivos, etc.)
import os
# Importación de 'streamlit' con el alias 'st' para crear la interfaz gráfica web interactiva
import streamlit as st
# Importación de 'pandas' con el alias 'pd' para manipulación y análisis de datos en tablas (DataFrames)
import pandas as pd
# Importación de 'numpy' con el alias 'np' para cálculos numéricos y manejo de arreglos
import numpy as np
# Importación de 'plotly.graph_objects' con el alias 'go' para crear gráficos interactivos personalizados (ej. 3D)
import plotly.graph_objects as go
# Importación de 'plotly.express' con el alias 'px' para crear gráficos rápidos y estadísticos
import plotly.express as px
# Importación del módulo 'integrate' de 'scipy' para realizar cálculos matemáticos de integración
from scipy import integrate
# Importación de 'FPDF' de la librería 'fpdf' para la generación de documentos PDF
from fpdf import FPDF
# Importación de 'base64' para codificar datos binarios (usado internamente en streamlit/pdfs a veces)
import base64

# Configuración inicial de la página de Streamlit: título de la pestaña, diseño ancho ('wide') y barra lateral expandida
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide", initial_sidebar_state="expanded")

# Definición de paleta de colores para indicadores visuales: Cyan, Verde, Ámbar (naranja) y Rojo
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"
# Definición de paleta de colores para el tema oscuro de la aplicación (fondos, tarjetas, bordes y texto atenuado)
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"

# Inyección de código CSS personalizado para estilizar la aplicación mediante markdown
st.markdown(f"""
<style>
/* Importación de fuentes de Google Fonts: 'Rajdhani' para texto general y 'Share Tech Mono' para datos técnicos */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
/* Estilos base para el HTML y cuerpo: aplicación de la fuente principal y colores de fondo oscuros */
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {BG_DEEP}; color: #ffffff; }}
/* Estilo para la barra lateral: color de fondo y borde separador */
[data-testid="stSidebar"] {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}
/* Estilo para los contenedores de métricas: fondo de tarjeta, borde, relleno y bordes redondeados */
div[data-testid="metric-container"] {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; }}
/* Estilo para las etiquetas (títulos) de las métricas: color atenuado y fuente monoespaciada pequeña */
div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-family: 'Share Tech Mono', monospace; font-size: 11px; }}
/* Estilo para los valores numéricos de las métricas: color cyan y fuente en negrita (peso 700) */
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {CYAN} !important; font-weight: 700; }}
/* Estilo para una clase personalizada 'card-container': similar al contenedor de métricas, usado para gráficos u otros bloques */
.card-container {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
</style>
""", unsafe_allow_html=True) # El parámetro 'unsafe_allow_html=True' permite a Streamlit renderizar el CSS crudo

# Decorador que indica a Streamlit que guarde en caché el resultado de esta función para mejorar el rendimiento
@st.cache_data
# Función para extraer datos de producción histórica desde un archivo CSV
def extraer_datos_csv():
    # Obtención del directorio donde se encuentra este script ('app.py')
    directorio = os.path.dirname(__file__)
    # Construcción de la ruta absoluta hacia el archivo CSV de datos limpios
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    # Verificación de la existencia del archivo en la ruta especificada
    if not os.path.exists(ruta):
        # Si no existe, retorna un DataFrame vacío con las columnas esperadas para evitar errores
        return pd.DataFrame(columns=['Nommunicipio', 'Anio', 'Nomcultivo', 'Volumenproduccion', 'Preciomediorural'])
    # Si existe, lee el archivo CSV y retorna el DataFrame de pandas con sus datos
    return pd.read_csv(ruta)

# Función para extraer datos desde la base de datos SQL (o usar datos simulados por defecto)
def extraer_datos_sql():
    # Bloque 'try' para intentar la conexión real a la base de datos
    try:
        # Intenta importar la función 'obtener_conexion' del módulo local 'database'
        from database import obtener_conexion
        # Establece la conexión (el 'engine' de SQLAlchemy o conector similar)
        engine = obtener_conexion()
        # Consulta SQL para extraer parámetros técnicos y económicos de los cultivos
        q_cultivos = "SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad, inversion_infraestructura FROM catalogo_cultivos"
        # Consulta SQL para extraer los modificadores y datos de los municipios
        q_municipios = "SELECT nombre, tipo_suelo, mod_rendimiento, mod_costo, mod_riesgo FROM municipios"
        # Ejecuta las consultas y devuelve dos DataFrames con los resultados
        return pd.read_sql(q_cultivos, engine), pd.read_sql(q_municipios, engine)
    # Si ocurre algún error (ej. módulo 'database' no existe, o fallo de conexión), se ejecuta el bloque 'except'
    except Exception:
        # Creación de un DataFrame simulado para el catálogo de cultivos como respaldo ('fallback')
        d_cultivos = pd.DataFrame({
            'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'], # Nombres de cultivos soportados
            'costo_operativo': [32057.66, 105100.0, 55000.0, 38000.0], # Costos operativos base
            'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04], # Incremento en precio por prácticas sostenibles
            'riesgo_probabilidad': [0.35, 0.08, 0.20, 0.25], # Probabilidad de pérdida o afectación
            'inversion_infraestructura': [0.0, 147000.0, 0.0, 0.0] # Costo de infraestructura inicial
        })
        # Creación de un DataFrame simulado para los municipios como respaldo
        d_municipios = pd.DataFrame({
            'nombre': ['Temixco', 'Cuautla', 'Jiutepec'], # Lista de municipios
            'tipo_suelo': ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'], # Tipos de suelo
            'mod_rendimiento': [1.15, 1.0, 0.95], # Multiplicador de rendimiento (clima/suelo)
            'mod_costo': [0.95, 1.05, 1.10], # Multiplicador de costos operativos
            'mod_riesgo': [0.85, 1.0, 1.10] # Multiplicador de riesgo climático
        })
        # Retorna los dos DataFrames de respaldo
        return d_cultivos, d_municipios

# Función para generar un documento PDF de reporte para el agricultor
def generar_pdf_agricultor(municipio, utilidad, inversion, prob_exito, suelo):
    # Instancia de un nuevo objeto PDF
    pdf = FPDF()
    # Añade una nueva página al documento
    pdf.add_page()
    # Configura el color de relleno a un verde oscuro para el encabezado
    pdf.set_fill_color(30, 120, 30)
    # Dibuja un rectángulo relleno ('F') en la parte superior que actúa como banner
    pdf.rect(0, 0, 210, 40, 'F')
    # Configura la fuente Arial, negrita ('B'), tamaño 16 para el título principal
    pdf.set_font("Arial", 'B', 16)
    # Configura el color del texto a blanco
    pdf.set_text_color(255, 255, 255)
    # Imprime el título principal centrado ('C')
    pdf.cell(0, 10, "REPORTE DE VIABILIDAD AGROECONOMICA", ln=True, align='C')
    # Cambia la fuente a Arial normal, tamaño 12 para el subtítulo
    pdf.set_font("Arial", '', 12)
    # Imprime el subtítulo del sistema y año
    pdf.cell(0, 10, "Sistema Inteligente Morelos | Proyeccion 2026", ln=True, align='C')
    # Añade un salto de línea (espacio vertical de 25 unidades)
    pdf.ln(25)
    # Restablece el color del texto a negro
    pdf.set_text_color(0, 0, 0)
    # Configura la fuente para el encabezado de resultados
    pdf.set_font("Arial", 'B', 14)
    # Imprime el texto indicando para qué municipio son los resultados
    pdf.cell(0, 10, f"Resultados para el Productor: {municipio}", ln=True)
    # Configura la fuente para el párrafo explicativo
    pdf.set_font("Arial", '', 11)
    # Imprime un párrafo de texto multilinea que describe la recomendación (Higo + Hidroponía) y el suelo
    pdf.multi_cell(0, 7, f"Se presenta el dictamen tecnico para la transicion al modelo combinado Higo (1 ha) + Modulo Hidroponico (100m2). Analisis basado en suelo tipo {suelo}.")
    # Salto de línea pequeño
    pdf.ln(10)
    # Configura color de relleno verde muy claro para los encabezados de la tabla
    pdf.set_fill_color(230, 245, 230)
    # Configura fuente en negrita para encabezados de tabla
    pdf.set_font("Arial", 'B', 12)
    # Dibuja la celda "CONCEPTO" (ancho 90, con borde '1', alineación centro 'C', con fondo 'True')
    pdf.cell(90, 10, "CONCEPTO", 1, 0, 'C', True)
    # Dibuja la celda "VALOR ESTIMADO" a un lado y realiza salto de línea ('1' en ln)
    pdf.cell(90, 10, "VALOR ESTIMADO", 1, 1, 'C', True)
    # Configura fuente normal para los datos de la tabla
    pdf.set_font("Arial", '', 12)
    # Celda para la etiqueta de inversión
    pdf.cell(90, 10, "Inversion Inicial (CAPEX)", 1)
    # Celda para el valor formateado de la inversión, alineado a la derecha ('R')
    pdf.cell(90, 10, f"$ {inversion:,.2f} MXN", 1, 1, 'R')
    # Celda para la etiqueta de utilidad
    pdf.cell(90, 10, "Utilidad Neta Anual", 1)
    # Celda para el valor formateado de la utilidad
    pdf.cell(90, 10, f"$ {utilidad:,.2f} MXN", 1, 1, 'R')
    # Celda para la etiqueta de probabilidad de éxito
    pdf.cell(90, 10, "Confianza del Exito", 1)
    # Celda para el porcentaje de éxito
    pdf.cell(90, 10, f"{prob_exito:.1f} %", 1, 1, 'R')
    # Salto de línea
    pdf.ln(15)
    # Fuente en negrita para el título del dictamen
    pdf.set_font("Arial", 'B', 12)
    # Imprime el título "DICTAMEN FINAL:"
    pdf.cell(0, 10, "DICTAMEN FINAL:", ln=True)
    # Fuente cursiva ('I') para el texto del dictamen
    pdf.set_font("Arial", 'I', 11)
    # Imprime el texto de recomendación de ejecución inmediata
    pdf.multi_cell(0, 7, "Se recomienda la EJECUCION INMEDIATA. El modelo genera flujo de caja constante y cubre la inversion inicial en el primer ciclo operativo pleno.")
    # Salto de línea al final del documento
    pdf.ln(20)
    # Fuente muy pequeña para los créditos
    pdf.set_font("Arial", 'B', 8)
    # Imprime el texto de créditos centrado en la parte inferior
    pdf.cell(0, 5, "Desarrollado por NA. | Ciencia de Datos para Negocios", align='C')
    # Genera el PDF en memoria y retorna su representación en bytes para ser descargable
    return bytes(pdf.output())

# Se llama a la función para cargar datos históricos en 'df_historico'
df_historico = extraer_datos_csv()
# Se llama a la función para cargar catálogo de cultivos y municipios en sus respectivos DataFrames
df_catalogo, df_municipios = extraer_datos_sql()

# Diccionario que actúa como matriz fenológica (rendimiento según mes de siembra) para cada cultivo
matriz_fenologica = {
    'Higo': {'Enero': 0.9, 'Febrero': 0.9, 'Marzo': 1.0, 'Abril': 1.1, 'Mayo': 1.2, 'Junio': 1.2, 'Julio': 1.1, 'Agosto': 1.0, 'Septiembre': 0.9, 'Octubre': 0.9, 'Noviembre': 0.8, 'Diciembre': 0.8}, # El Higo tiene mejor rinde si se planta entre Abril-Julio
    'Maíz grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.2, 'Mayo': 1.2, 'Junio': 1.5, 'Julio': 1.0, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.8, 'Noviembre': 0.0, 'Diciembre': 0.0}, # Maíz depende fuertemente de lluvias (Junio)
    'Caña de azúcar': {'Enero': 1.3, 'Febrero': 1.4, 'Marzo': 1.5, 'Abril': 1.4, 'Mayo': 1.2, 'Junio': 0.5, 'Julio': 0.5, 'Agosto': 0.5, 'Septiembre': 0.5, 'Octubre': 0.5, 'Noviembre': 1.0, 'Diciembre': 1.2},
    'Sorgo grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.5, 'Mayo': 1.0, 'Junio': 1.3, 'Julio': 1.2, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.5, 'Noviembre': 0.0, 'Diciembre': 0.0}
}

# Diccionario con la descripción textual de los meses óptimos de siembra por cultivo
mes_siembra_optimo = {'Higo': 'Febrero - Marzo', 'Maíz grano': 'Mayo - Junio (PV)', 'Caña de azúcar': 'Julio - Agosto', 'Sorgo grano': 'Mayo - Junio (PV)'}
# Diccionario con factores de volatilidad de mercado (variación de precios esperada) por cultivo
volatilidad_mercado = {'Higo': 0.12, 'Maíz grano': 0.25, 'Caña de azúcar': 0.08, 'Sorgo grano': 0.20}
# Fijación de la semilla aleatoria de numpy para asegurar la reproducibilidad de las simulaciones de Monte Carlo
np.random.seed(42)

# --- CONFIGURACIÓN DE LA BARRA LATERAL (SIDEBAR) ---
# Título en la barra lateral
st.sidebar.header("Panel de Control")
# Menú desplegable para seleccionar un municipio (obtiene valores únicos del DataFrame de municipios)
municipio = st.sidebar.selectbox("Seleccione Municipio:", df_municipios['nombre'].unique())
# Menú desplegable para seleccionar el mes de análisis (toma las llaves del mes del diccionario de fenología del Higo)
mes_actual = st.sidebar.selectbox("Mes de Análisis:", list(matriz_fenologica['Higo'].keys()))
# Slider de rango para seleccionar el periodo de años de análisis (entre 2018 y 2026)
anio_range = st.sidebar.slider("Periodo:", 2018, 2026, (2018, 2026))

# Filtra la fila correspondiente al municipio seleccionado en el DataFrame de municipios
datos_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
# Extrae los modificadores (clima/suelo/riesgo) específicos de ese municipio a variables individuales
mod_rend, mod_costo, mod_riesgo = datos_mun['mod_rendimiento'], datos_mun['mod_costo'], datos_mun['mod_riesgo']

# Filtra los datos históricos: coincidencias con el municipio seleccionado, y dentro del rango de años (hasta 2024 máximo para datos reales)
df_f = df_historico[(df_historico['Nommunicipio'] == municipio) & (df_historico['Anio'] >= anio_range[0]) & (df_historico['Anio'] <= min(2024, anio_range[1]))].copy()

# Si hay datos históricos después de aplicar los filtros...
if not df_f.empty:
    # Cruza (hace un 'merge' o JOIN) los datos históricos con los datos del catálogo de cultivos usando el nombre del cultivo
    df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')
    # Calcula precio ajustado aplicando la prima por sostenibilidad (llena nulos con 0 por si acaso)
    df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
    # Calcula el costo ajustado usando el costo operativo base multiplicado por el modificador del municipio
    df_merge['costo_ajustado'] = df_merge['costo_operativo'].fillna(32057.66) * mod_costo
    # Calcula la utilidad neta base: Ingresos (Volumen * Mod Rendimiento * Precio Aj) menos los costos ajustados
    df_merge['utilidad_neta'] = ((df_merge['Volumenproduccion'] * mod_rend) * df_merge['precio_ajustado']) - df_merge['costo_ajustado']
    # Calcula el ICC (Índice de Competitividad de Cultivos): Utilidad ajustada por la probabilidad de riesgo climático modificado
    df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - (df_merge['riesgo_probabilidad'].fillna(0.2) * mod_riesgo))
    # Etiqueta estas filas como datos históricos
    df_merge['Tipo_Dato'] = 'Histórico'
# Si no hay datos históricos (ej. por el filtro)...
else:
    # Crea un DataFrame vacío con las columnas necesarias para no romper el código posterior
    df_merge = pd.DataFrame(columns=['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'utilidad_neta'])

# Si el usuario seleccionó un rango que incluye años futuros (mayor a 2024), se calculan proyecciones
if anio_range[1] > 2024:
    # Lista de años futuros a proyectar (desde 2025 o inicio del rango si es mayor, hasta el fin del rango)
    anios_futuros = [a for a in range(max(2025, anio_range[0]), anio_range[1] + 1)]
    filas_proyectadas = [] # Lista temporal para guardar los registros calculados
    # Itera sobre cada año futuro
    for anio in anios_futuros:
        # Itera sobre cada cultivo disponible en el catálogo
        for _, row in df_catalogo.iterrows():
            # Extrae propiedades base del cultivo de la iteración actual
            cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
            # Obtiene el modificador biológico/fenológico para el cultivo en el mes seleccionado (1.0 por defecto si no existe)
            m_bio = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
            # Define un precio base arbitrario: mayor para el Higo, menor para otros
            p_base = 34994.18 if cultivo == 'Higo' else 5516.0
            # Simulación de Monte Carlo (1000 muestras) de distribución normal para estimar el precio futuro ('p_esp' será la media de la simulación)
            # El centro (loc) se ve influido por el modificador biológico, la dispersión (scale) por la volatilidad del mercado
            p_esp = np.mean(np.random.normal(loc=p_base * m_bio, scale=(p_base * m_bio * volatilidad_mercado.get(cultivo, 0.15)), size=1000))
            # Volumen de producción esperado base (Higo produce más valor que otros en volumen nominal del ejemplo)
            v_esp = 6.82 if cultivo == 'Higo' else 3.5
            # Cálculo de la utilidad neta esperada aplicando todos los modificadores (rendimiento, mes, prima y costo)
            utilidad = ((v_esp * mod_rend * m_bio) * (p_esp * (1 + prima))) - (costo * mod_costo)
            # Al cultivo de Higo se le suma un margen adicional arbitrario en la proyección (probablemente representando el módulo hidropónico anexo)
            if cultivo == 'Higo': utilidad += (117600.00 - 58100.00)
            # Cálculo del ICC proyectado (Utilidad descontando factor de riesgo)
            icc = utilidad * (1 - (riesgo * mod_riesgo))
            # Añade el registro calculado a la lista de proyecciones
            filas_proyectadas.append({'Nommunicipio': municipio, 'Anio': anio, 'Nomcultivo': cultivo, 'Volumenproduccion': v_esp * mod_rend * m_bio, 'Preciomediorural': p_esp, 'costo_ajustado': costo * mod_costo, 'utilidad_neta': utilidad, 'ICC': icc, 'Tipo_Dato': 'Proyección Monte Carlo', 'Estatus': "Alta Competitividad" if icc > 200000 else "Optimización Requerida"})
    # Si se generaron filas, las concatena (agrega) al DataFrame principal que tenía los datos históricos
    if filas_proyectadas:
        df_merge = pd.concat([df_merge, pd.DataFrame(filas_proyectadas)], ignore_index=True)

# Añade separador en la barra lateral
st.sidebar.markdown("---")
# Subtítulo para la sección de reportes en la barra lateral
st.sidebar.subheader("Reportes Ejecutivos")
# Botón para generar y descargar el PDF de agricultor
if st.sidebar.button("Generar Reporte para Agricultor"):
    # Llama a la función generadora de PDF con valores estáticos de demostración y el tipo de suelo dinámico
    pdf_bytes = generar_pdf_agricultor(municipio, 251159.31, 147000.00, 95.4, datos_mun['tipo_suelo'])
    # Botón de descarga nativo de Streamlit que proporciona el archivo generado al usuario
    st.sidebar.download_button(label="Descargar Reporte (PDF)", data=pdf_bytes, file_name=f"Reporte_Agricola_{municipio}.pdf", mime="application/pdf")

# --- CONSTRUCCIÓN DEL ÁREA PRINCIPAL (TABS) ---
# Título principal de la aplicación
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")
# Creación de 3 pestañas principales para dividir la información
tab_dash, tab_math, tab_pred = st.tabs(["Dashboard Operativo", "Evaluación Regional (Integrales)", "Motor Predictivo (Monte Carlo)"])

# Contenido de la primera pestaña: Dashboard principal
with tab_dash:
    # Divide el espacio en dos columnas iguales
    c1, c2 = st.columns(2)
    # Columna 1 muestra una métrica clave principal con valor estático para demostración
    c1.metric("Utilidad Neta Proyectada (Higo+NFT)", "$ 251,159.31 MXN")
    # Columna 2 muestra el valor de la inversión inicial
    c2.metric("Inversión Inicial (CAPEX)", "$ 147,000.00 MXN")
    # Usa markdown para renderizar un 'div' con el estilo personalizado 'card-container'
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    # Verifica si existen datos calculados
    if not df_merge.empty:
        # Agrupa los datos por cultivo y calcula el ICC promedio, creando un gráfico de barras horizontales de comparación
        fig_bar = px.bar(df_merge.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        # Limpia el estilo del gráfico (fondos transparentes y oculta leyenda de color)
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        # Despliega el gráfico en la interfaz ocupando el ancho disponible
        st.plotly_chart(fig_bar, use_container_width=True)
    # Cierra el 'div' personalizado
    st.markdown('</div>', unsafe_allow_html=True)

# Contenido de la segunda pestaña: Evaluación Regional usando gráficos 3D basados en funciones matemáticas
with tab_math:
    # Definición de función lambda que modela matemáticamente la rentabilidad del Maíz (dependiente de 2 variables 'x' e 'y')
    func_maiz = lambda y, x: ((16.548 * x * mod_rend) - ((19.8 + 12.257 * x) * mod_costo) - (0.2 * y * mod_costo))
    # Definición de función lambda que modela matemáticamente la rentabilidad del Higo (función cuadrática en 'y')
    func_higo = lambda y, x: ((356.259 * x * mod_rend) - (105.1 * mod_costo) - (0.1 * (y**2) * mod_costo))
    # Generación de mallas (grid) bidimensionales de valores (50x50 puntos) para evaluar las funciones en espacio 3D
    x_g, y_g = np.meshgrid(np.linspace(0, 5, 50), np.linspace(0, 3, 50))
    # Creación del gráfico 3D con Plotly insertando 2 superficies (una para Higo y otra para Maíz)
    # np.vectorize permite aplicar la función lambda a todos los puntos de la matriz a la vez
    fig_3d = go.Figure(data=[
        go.Surface(z=np.vectorize(lambda x, y: func_higo(y, x))(x_g, y_g), x=x_g, y=y_g, colorscale='Tealgrn', showscale=False, opacity=0.9),
        go.Surface(z=np.vectorize(lambda x, y: func_maiz(y, x))(x_g, y_g), x=x_g, y=y_g, colorscale='OrRd', showscale=False, opacity=0.8)
    ])
    # Ajustes del layout del modelo 3D (rango del eje Z para enfocarse en la zona útil, fondo transparente, alto ajustado)
    fig_3d.update_layout(scene=dict(zaxis=dict(range=[-50, 1500])), paper_bgcolor="rgba(0,0,0,0)", height=600)
    # Despliega el gráfico 3D en la interfaz
    st.plotly_chart(fig_3d, use_container_width=True)

# Contenido de la tercera pestaña: Simulaciones Predictivas (Método Monte Carlo)
with tab_pred:
    # Función local que ejecuta una simulación para calcular el riesgo/probabilidad de éxito por cada cultivo
    def simular_cultivo(row):
        # Desempaqueta parámetros del cultivo analizado
        cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
        # Obtiene modificador fenológico del mes seleccionado
        m_bio = matriz_fenologica.get(cultivo, {}).get(mes_actual, 1.0)
        # Base de precio referencial
        p_base = 34994.18 if cultivo == 'Higo' else 5516.0
        # Simula 1000 escenarios posibles de precios bajo una distribución normal con desviación del 12%
        p_sim = np.random.normal(loc=p_base * m_bio, scale=(p_base * 0.12), size=1000)
        # Calcula el vector de las 1000 utilidades resultantes en base a los 1000 precios simulados
        util = ((6.82 if cultivo == 'Higo' else 3.5) * mod_rend * m_bio * p_sim * (1 + prima)) - (costo * mod_costo)
        # Modificador específico que incrementa ganancia para modelo "Higo" (asociado a la mejora hidropónica)
        if cultivo == 'Higo': util += 59500.00
        # Calcula los 1000 resultados ICC ajustando la utilidad por el riesgo en el área
        icc_sim = util * (1 - (riesgo * mod_riesgo))
        # Retorna una fila ('Serie') con el nombre del cultivo, el % de escenarios que resultaron en ICC positivo, y el promedio final del ICC
        return pd.Series([cultivo, (np.sum(icc_sim > 0) / 1000) * 100, np.mean(icc_sim), mes_siembra_optimo.get(cultivo, 'N/D')])
    
    # Aplica la función 'simular_cultivo' a cada fila ('axis=1') del catálogo de cultivos original y guarda en un nuevo DataFrame
    df_p = df_catalogo.apply(simular_cultivo, axis=1)
    # Nombra las columnas del DataFrame de resultados
    df_p.columns = ['Cultivo', 'Probabilidad de Éxito (%)', 'ICC Esperado', 'Época de Siembra']
    
    # Divide la vista en dos columnas asimétricas (1 parte para métrica de sugerencia, 2 partes para gráfica)
    col_a, col_b = st.columns([1, 2])
    # Busca en los resultados cuál cultivo tuvo la mayor "Probabilidad de Éxito" y lo muestra como Métrica/Sugerencia
    col_a.metric("Sugerencia Técnica", df_p.sort_values(by='Probabilidad de Éxito (%)', ascending=False).iloc[0]['Cultivo'])
    # Construye una gráfica de barras horizontales con la probabilidad de éxito de todos los cultivos (rango X de 0 a 100%)
    fig_p = px.bar(df_p, x='Probabilidad de Éxito (%)', y='Cultivo', orientation='h', color_continuous_scale='Tealgrn', range_x=[0, 100])
    # Despliega la gráfica en la segunda columna ocupando su ancho
    col_b.plotly_chart(fig_p, use_container_width=True)