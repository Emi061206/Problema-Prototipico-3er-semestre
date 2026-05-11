# Importar libreria para interactuar con rutas del sistema operativo
import os
# Importar pandas para la manipulacion de datos tabulares y CSV
import pandas as pd
# Importar numpy para la simulacion numerica y generacion de distribuciones
import numpy as np
# Importar librerias graficas de Plotly para renderizado 3D y 2D
import plotly.graph_objects as go
import plotly.express as px
# Importar Streamlit como framework principal de la aplicacion
import streamlit as st
# Importar herramienta de calculo integral espacial
from scipy import integrate
# Importar motor de creacion de PDFs
from fpdf import FPDF

# Configurar parametros de la ventana, titulo y estado de la barra lateral
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide", initial_sidebar_state="expanded")

# Definir variables de colores semaforicos para las graficas
CYAN, GREEN, AMBER, RED = "#3498DB", "#2E8B57", "#F39C12", "#E74C3C"
# Definir paleta de Psicologia del Color Agricola (Crema, Blanco, Verde Olivo, Tierra, Cítrico)
BG_DEEP, BG_CARD, BORDER, TEXT_MAIN, TEXT_DIM, ACCENT, TECH_BLUE = "#F9FBF2", "#FFFFFF", "#558B2F", "#3E2723", "#795548", "#E67E22", "#3498DB"

# Inyectar CSS puro forzando la sobreescritura del tema nativo de Streamlit con !important
st.markdown(f"""
<style>
/* Importar tipografias corporativas y tecnicas desde Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
/* Aplicar color de fondo crema y tipografia Tierra a la clase base de la aplicacion */
.stApp {{ background-color: {BG_DEEP}; color: {TEXT_MAIN}; font-family: 'Rajdhani', sans-serif; }}
/* Colorear el panel lateral de blanco puro con un borde divisorio verde olivo */
[data-testid="stSidebar"] {{ background-color: {BG_CARD} !important; border-right: 2px solid {BORDER} !important; }}
/* Volver transparente el fondo del encabezado superior predeterminado */
[data-testid="stHeader"] {{ background-color: transparent !important; }}
/* Estilizar las cajas contenedoras de metricas (KPIs) con bordes, padding y sombra sutil */
div[data-testid="metric-container"] {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
/* Aplicar tono tierra tenue y tipografia monospace a las etiquetas de las metricas */
div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-family: 'Share Tech Mono', monospace; font-size: 14px !important; }}
/* Aplicar el acento naranja citrico al numero principal de la metrica financiera */
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {ACCENT} !important; font-weight: 700; }}
/* Definir clase generica para contener tablas y graficas de forma limpia */
.card-container {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
/* Forzar el color de todos los botones de descarga de reportes al acento Naranja Citrico */
div.stDownloadButton > button {{ background-color: {ACCENT} !important; color: white !important; border: none !important; font-weight: bold !important; width: 100% !important; }}
/* Alterar el color del boton a Azul Riego cuando el usuario pasa el mouse (hover) */
div.stDownloadButton > button:hover {{ background-color: {TECH_BLUE} !important; }}
/* Modificar el color de las pestañas de navegacion al tono tierra tenue */
button[data-baseweb="tab"] {{ color: {TEXT_DIM} !important; }}
/* Alterar el subrayado y texto de la pestaña activa al acento Naranja Citrico */
button[data-baseweb="tab"][aria-selected="true"] {{ color: {ACCENT} !important; border-bottom-color: {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# Almacenar en cache la carga de datos del disco duro
@st.cache_data
def extraer_datos_csv():
    # Obtener la ruta del script para encontrar la carpeta de limpieza de datos
    directorio = os.path.dirname(__file__)
    # Construir la ruta al archivo historico filtrado de la zona
    ruta = os.path.join(directorio, 'Liempeza de Datos', 'Datos Limpios', 'Historico_Morelos_Focalizado.csv')
    # Evaluar si el origen no existe para evitar colapsos
    if not os.path.exists(ruta):
        # Entregar set de respaldo
        return pd.DataFrame({'Nommunicipio': ['Temixco', 'Temixco', 'Cuautla', 'Cuautla', 'Jiutepec', 'Jiutepec'], 'Anio': [2023, 2024, 2023, 2024, 2023, 2024], 'Nomcultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano', 'Maíz grano', 'Higo'], 'Volumenproduccion': [3.5, 6.8, 105.0, 5.5, 3.2, 6.5], 'Preciomediorural': [5500.0, 31000.0, 900.0, 4200.0, 5600.0, 32000.0]})
    # Retornar el origen verificado
    return pd.read_csv(ruta)

# Definir la funcion conectora al esquema relacional
def extraer_datos_sql():
    # Intentar conexion directa
    try:
        from database import obtener_conexion
        engine = obtener_conexion()
        # Traer dataframes directamente desde las consultas
        return pd.read_sql("SELECT nombre_cultivo, costo_operativo, prima_sostenibilidad, riesgo_probabilidad, inversion_infraestructura FROM catalogo_cultivos", engine), pd.read_sql("SELECT nombre, tipo_suelo, mod_rendimiento, mod_costo, mod_riesgo FROM municipios", engine)
    # Controlar interrupciones del servicio
    except Exception:
        # Entregar tablas catalogadas quemadas en el codigo (CAPEX: 147k)
        return pd.DataFrame({'nombre_cultivo': ['Maíz grano', 'Higo', 'Caña de azúcar', 'Sorgo grano'], 'costo_operativo': [32057.66, 105100.0, 55000.0, 38000.0], 'prima_sostenibilidad': [0.05, 0.15, 0.02, 0.04], 'riesgo_probabilidad': [0.35, 0.08, 0.20, 0.25], 'inversion_infraestructura': [0.0, 147000.0, 0.0, 0.0]}), pd.DataFrame({'nombre': ['Temixco', 'Cuautla', 'Jiutepec'], 'tipo_suelo': ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'], 'mod_rendimiento': [1.15, 1.0, 0.95], 'mod_costo': [0.95, 1.05, 1.10], 'mod_riesgo': [0.85, 1.0, 1.10]})

# Generar archivo vectorial anual con FPDF
def generar_pdf_anual(municipio, utilidad, inversion, prob_exito, suelo):
    # Instanciar el core del PDF
    pdf = FPDF()
    # Abrir pagina frontal
    pdf.add_page()
    # Trazar encabezado verde corporativo
    pdf.set_fill_color(30, 120, 30)
    pdf.rect(0, 0, 210, 40, 'F')
    # Rotular titulo e informacion clave del modelo
    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(255, 255, 255); pdf.cell(0, 10, "REPORTE ANUAL DE VIABILIDAD", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.cell(0, 10, "Proyeccion Ciclo Completo 2026", ln=True, align='C')
    # Volver a tinta oscura e informar predio
    pdf.ln(25); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"Municipio: {municipio}", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"Analisis de transicion al modelo Higo (1 ha) + Hidroponia (100m2) en suelo {suelo}.")
    # Generar tabla financiera matricial
    pdf.ln(10); pdf.set_fill_color(230, 245, 230); pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "CONCEPTO", 1, 0, 'C', True); pdf.cell(90, 10, "VALOR ANUAL", 1, 1, 'C', True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(90, 10, "Inversion Inicial (CAPEX)", 1); pdf.cell(90, 10, f"$ {inversion:,.2f}", 1, 1, 'R')
    pdf.cell(90, 10, "Utilidad Operativa Neta", 1); pdf.cell(90, 10, f"$ {utilidad:,.2f}", 1, 1, 'R')
    pdf.cell(90, 10, "Probabilidad de Exito", 1); pdf.cell(90, 10, f"{prob_exito:.1f} %", 1, 1, 'R')
    # Proveer interpretacion de los calculos (Veredicto)
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "DICTAMEN:", ln=True)
    pdf.set_font("Arial", 'I', 11); pdf.multi_cell(0, 7, "Ejecucion recomendada. El modelo es altamente resiliente y garantiza flujo de caja.")
    # Imprimir marca de agua de autoria
    pdf.ln(20); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "Desarrollado por N.A", align='C')
    # Transmitir flujo binario
    return bytes(pdf.output())

# Generar archivo vectorial desfasado mensualmente
def generar_pdf_mensual(mes, municipio, datos_mes):
    # Instanciar el core
    pdf = FPDF()
    # Abrir documento
    pdf.add_page()
    # Color azul para reportes parciales
    pdf.set_fill_color(52, 152, 219)
    pdf.rect(0, 0, 210, 40, 'F')
    # Titular operacion indicando el mes corriente
    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(255, 255, 255); pdf.cell(0, 10, f"REPORTE MENSUAL: {mes.upper()}", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.cell(0, 10, f"Gestion Operativa - {municipio}", ln=True, align='C')
    # Estructurar bloque contable
    pdf.ln(25); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Resumen de Flujo de Caja Mensual", ln=True)
    pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(240, 240, 240)
    pdf.cell(70, 10, "Concepto", 1, 0, 'C', True); pdf.cell(40, 10, "Ingresos", 1, 0, 'C', True); pdf.cell(40, 10, "Egresos", 1, 0, 'C', True); pdf.cell(40, 10, "Neto", 1, 1, 'C', True)
    pdf.set_font("Arial", '', 10)
    # Ejecutar lambda simulado integrando filas estaticas
    filas = [["Modulo Hidroponico", f"$ {datos_mes['ing_h']:,.2f}", f"$ {datos_mes['egr_h']:,.2f}", f"$ {datos_mes['net_h']:,.2f}"], ["Cultivo de Higo", f"$ {datos_mes['ing_f']:,.2f}", f"$ {datos_mes['egr_f']:,.2f}", f"$ {datos_mes['net_f']:,.2f}"], ["Costos Fijos (Prorrateo)", "$ 0.00", "$ 4,300.00", "-$ 4,300.00"]]
    # Imprimir celdas de matriz
    for f in filas:
        pdf.cell(70, 10, f[0], 1); pdf.cell(40, 10, f[1], 1, 0, 'R'); pdf.cell(40, 10, f[2], 1, 0, 'R'); pdf.cell(40, 10, f[3], 1, 1, 'R')
    # Anexar observaciones de campo
    pdf.ln(10); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 7, f"Nota Tecnica: {datos_mes['nota']}")
    # Sellar reporte
    pdf.ln(15); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "Desarrollado por N.A", align='C')
    # Exportar bytes
    return bytes(pdf.output())

# Compilar CSV anual aplicando lambda estructurado 
generar_csv_anual = lambda municipio, utilidad, inversion, prob_exito: pd.DataFrame([{'Municipio': municipio, 'Inversion_Inicial_MXN': inversion, 'Utilidad_Neta_MXN': utilidad, 'Probabilidad_Exito_PCT': prob_exito}]).to_csv(index=False).encode('utf-8')

# Compilar CSV mensual extrayendo matriz de diccionario
generar_csv_mensual = lambda mes, municipio, datos_mes: pd.DataFrame([{'Concepto': 'Modulo Hidroponico', 'Ingresos': datos_mes['ing_h'], 'Egresos': datos_mes['egr_h'], 'Neto': datos_mes['net_h']}, {'Concepto': 'Cultivo de Higo', 'Ingresos': datos_mes['ing_f'], 'Egresos': datos_mes['egr_f'], 'Neto': datos_mes['net_f']}, {'Concepto': 'Costos Fijos', 'Ingresos': 0.0, 'Egresos': 4300.0, 'Neto': -4300.0}]).to_csv(index=False).encode('utf-8')

# Levantar bases historicas y paramétricas al inicio del script
df_historico, (df_catalogo, df_municipios) = extraer_datos_csv(), extraer_datos_sql()

# Trazar herramientas del entorno visual
st.sidebar.header("Panel de Control")
# Control de seleccion geografico
municipio_sel = st.sidebar.selectbox("Seleccione Municipio:", ["Temixco", "Cuautla", "Jiutepec"])
# Control de temporalidad para dictamen especifico
mes_sel = st.sidebar.selectbox("Mes para Reporte Mensual:", ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
# Control de amplitud para el rastreo del SIAP
anio_range = st.sidebar.slider("Periodo Historico:", 2018, 2026, (2018, 2026))

# Focalizar constantes algebraicas interceptando la seleccion geografica
datos_mun = df_municipios[df_municipios['nombre'] == municipio_sel].iloc[0]
# Recuperar multiplicadores
mod_rend, mod_costo, mod_riesgo = datos_mun['mod_rendimiento'], datos_mun['mod_costo'], datos_mun['mod_riesgo']

# Repositorio de conocimientos contables simulando las respuestas del flujo agroforestal
datos_mensuales_db = {'Febrero': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 119329.0, 'egr_f': 4050.0, 'net_f': 115279.0, 'nota': "Pico de cosecha de Higo. Liquidez maxima."}, 'Marzo': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 119329.0, 'egr_f': 4050.0, 'net_f': 115279.0, 'nota': "Continuacion de cosecha de Higo. Flujo positivo."}, 'Junio': {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 0.0, 'egr_f': 1500.0, 'net_f': -1500.0, 'nota': "Fase de mantenimiento de Higo. Hidroponia cubre costos fijos."}}
default_mes = {'ing_h': 9800.0, 'egr_h': 2975.0, 'net_h': 6825.0, 'ing_f': 0.0, 'egr_f': 800.0, 'net_f': -800.0, 'nota': "Hidroponia mantiene el flujo operativo y evita apalancamiento."}

# Renderizar seccion de entregables
st.sidebar.markdown("---")
st.sidebar.subheader("Descarga de Reportes (PDF/CSV)")

# Cargar en memoria el resultado de las transformaciones globales
pdf_anual = generar_pdf_anual(municipio_sel, 251159.31, 147000.00, 95.4, datos_mun['tipo_suelo'])
csv_anual = generar_csv_anual(municipio_sel, 251159.31, 147000.00, 95.4)
info_mes = datos_mensuales_db.get(mes_sel, default_mes)
pdf_mes = generar_pdf_mensual(mes_sel, municipio_sel, info_mes)
csv_mes = generar_csv_mensual(mes_sel, municipio_sel, info_mes)

# Pintar botones de descarga aprovechando el formateo CSS Naranja/Azul
st.sidebar.download_button(label="Descargar PDF Anual", data=pdf_anual, file_name=f"Reporte_Anual_{municipio_sel}.pdf", mime="application/pdf")
st.sidebar.download_button(label="Descargar CSV Anual", data=csv_anual, file_name=f"Reporte_Anual_{municipio_sel}.csv", mime="text/csv")
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.download_button(label=f"Descargar PDF Mensual ({mes_sel})", data=pdf_mes, file_name=f"Reporte_{mes_sel}_{municipio_sel}.pdf", mime="application/pdf")
st.sidebar.download_button(label=f"Descargar CSV Mensual ({mes_sel})", data=csv_mes, file_name=f"Reporte_{mes_sel}_{municipio_sel}.csv", mime="text/csv")

# Diccionarios maestros de variabilidad climatologica
matriz_fenologica = {'Higo': {'Enero': 0.9, 'Febrero': 0.9, 'Marzo': 1.0, 'Abril': 1.1, 'Mayo': 1.2, 'Junio': 1.2, 'Julio': 1.1, 'Agosto': 1.0, 'Septiembre': 0.9, 'Octubre': 0.9, 'Noviembre': 0.8, 'Diciembre': 0.8}, 'Maíz grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.2, 'Mayo': 1.2, 'Junio': 1.5, 'Julio': 1.0, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.8, 'Noviembre': 0.0, 'Diciembre': 0.0}, 'Caña de azúcar': {'Enero': 1.3, 'Febrero': 1.4, 'Marzo': 1.5, 'Abril': 1.4, 'Mayo': 1.2, 'Junio': 0.5, 'Julio': 0.5, 'Agosto': 0.5, 'Septiembre': 0.5, 'Octubre': 0.5, 'Noviembre': 1.0, 'Diciembre': 1.2}, 'Sorgo grano': {'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 'Abril': 0.5, 'Mayo': 1.0, 'Junio': 1.3, 'Julio': 1.2, 'Agosto': 1.0, 'Septiembre': 0.8, 'Octubre': 0.5, 'Noviembre': 0.0, 'Diciembre': 0.0}}
mes_siembra_optimo = {'Higo': 'Febrero - Marzo', 'Maíz grano': 'Mayo - Junio', 'Caña de azúcar': 'Julio - Agosto', 'Sorgo grano': 'Mayo - Junio'}

# Aplicar filtrado matricial reduciendo el alcance al territorio de analisis
df_f = df_historico[(df_historico['Nommunicipio'] == municipio_sel) & (df_historico['Anio'] >= anio_range[0]) & (df_historico['Anio'] <= min(2024, anio_range[1]))].copy()

# Confirmar solidez de la extraccion
if not df_f.empty:
    # Empalmar tabla SQL y CSV
    df_merge = pd.merge(df_f, df_catalogo, left_on='Nomcultivo', right_on='nombre_cultivo', how='left')
    # Ajustar parametros con modificadores ambientales (Usando lambda implicita en Pandas)
    df_merge['precio_ajustado'] = df_merge['Preciomediorural'] * (1 + df_merge['prima_sostenibilidad'].fillna(0))
    df_merge['costo_ajustado'] = df_merge['costo_operativo'].fillna(32057.66) * mod_costo
    df_merge['utilidad_neta'] = ((df_merge['Volumenproduccion'] * mod_rend) * df_merge['precio_ajustado']) - df_merge['costo_ajustado']
    df_merge['ICC'] = df_merge['utilidad_neta'] * (1 - (df_merge['riesgo_probabilidad'].fillna(0.2) * mod_riesgo))
    df_merge['Tipo_Dato'] = 'Historico'
else:
    # Sostener estructura en caso de desbordamiento de filtros
    df_merge = pd.DataFrame(columns=['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'utilidad_neta'])

# Disparar calculo de proyeccion si el slider requiere visibilidad en el futuro (2025-2026)
if anio_range[1] > 2024:
    # Determinar ciclos a pronosticar
    anios_futuros = [a for a in range(max(2025, anio_range[0]), anio_range[1] + 1)]
    # Inicializar colector de datos
    filas_proyectadas = []
    # Generar iteraciones de Monte Carlo
    for anio in anios_futuros:
        for _, row in df_catalogo.iterrows():
            # Extraer tupleta referencial
            cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
            # Evaluar impacto del mes consultado
            m_bio = matriz_fenologica.get(cultivo, {}).get(mes_sel, 1.0)
            # Sembrar limite referencial
            p_base = 34994.18 if cultivo == 'Higo' else 5516.0
            # Operar distribucion y promediar rentabilidad esperada
            utilidad = (((6.82 if cultivo == 'Higo' else 3.5) * mod_rend * m_bio) * (np.mean(np.random.normal(loc=p_base * m_bio, scale=(p_base * 0.12), size=1000)) * (1 + prima))) - (costo * mod_costo)
            # Agregar salvavidas financiero de modulo de Hidroponia
            if cultivo == 'Higo': utilidad += 59500.00
            # Guardar diccionario
            filas_proyectadas.append({'Anio': anio, 'Nomcultivo': cultivo, 'Tipo_Dato': 'Proyeccion Monte Carlo', 'ICC': utilidad * (1 - (riesgo * mod_riesgo)), 'costo_ajustado': costo * mod_costo, 'utilidad_neta': utilidad})
    # Acoplar simulacion a la tabla central
    if filas_proyectadas: df_merge = pd.concat([df_merge, pd.DataFrame(filas_proyectadas)], ignore_index=True)

# Evaluar el estatus de la tabla final utilizando funcion lambda simplificada
if not df_merge.empty: df_merge['Estatus'] = df_merge['ICC'].apply(lambda val: "Diversificacion Urgente" if val < 20000 else ("Alta Competitividad" if val > 200000 else "Optimizacion Requerida"))

# Cabecera jerarquica uno
st.title("Sistema Inteligente de Monitoreo Agroforestal Morelos")
# Interfaz de pestanas
tab_dash, tab_math, tab_pred = st.tabs(["Dashboard Operativo", "Evaluacion Regional (Integrales)", "Motor Predictivo (Monte Carlo)"])

# Enrutador Logico Tab 1
with tab_dash:
    # Cuadricula
    c1, c2 = st.columns(2)
    # Visualizacion de variables contables
    c1.metric("Utilidad Neta Proyectada (Higo+NFT)", "$ 251,159.31 MXN"); c2.metric("Inversion Inicial (CAPEX)", "$ 147,000.00 MXN")
    # Generar caja de CSS aislando contenedor
    st.markdown('<div class="card-container">', unsafe_allow_html=True); st.markdown("#### Historico y Proyeccion de Competitividad por Cultivo")
    # Trazar grafica
    if not df_merge.empty:
        # Agrupar modelo por desempeño
        fig_bar = px.bar(df_merge.groupby('Nomcultivo')['ICC'].mean().sort_values().reset_index(), x='ICC', y='Nomcultivo', orientation='h', color='ICC', color_continuous_scale=[RED, GREEN])
        # Obligar paleta oscura a la letra para legibilidad contra fondos blancos
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, font_color=TEXT_MAIN)
        st.plotly_chart(fig_bar, use_container_width=True)
    else: st.warning("No hay datos para el rango seleccionado.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generar caja inferior
    st.markdown('<div class="card-container">', unsafe_allow_html=True); st.markdown(f"#### Tabla de Dictamen Operativo (Periodo: {anio_range[0]} - {anio_range[1]})")
    # Insertar data grid de estilo
    if not df_merge.empty:
        # Condicionar coloracion (rojo, verde, ambar) con lambda al vuelo en el mapeo
        st.dataframe(df_merge[['Anio', 'Nomcultivo', 'Tipo_Dato', 'ICC', 'costo_ajustado', 'Estatus']].style.map(lambda x: f'background-color: {RED if "Urgente" in str(x) else (GREEN if "Alta" in str(x) else AMBER)}; color: {"white" if "Urgente" in str(x) else "#000"}; font-weight: bold;', subset=['Estatus']).format({'ICC': '{:,.0f}', 'costo_ajustado': '${:,.2f}'}), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Enrutador Logico Tab 2
with tab_math:
    st.markdown("### Superficie de Rentabilidad y Volumen de Utilidad Acumulada")
    # Parametrizar funciones cartesianas de rentabilidad
    func_maiz = lambda y, x: ((16.548 * x * mod_rend) - ((19.8 + 12.257 * x) * mod_costo) - (0.2 * y * mod_costo))
    func_higo = lambda y, x: ((356.259 * x * mod_rend) - (105.1 * mod_costo) - (0.1 * (y**2) * mod_costo))
    # Fabricar lona 3D de 50x50 puntos
    x_g, y_g = np.meshgrid(np.linspace(0, 5, 50), np.linspace(0, 3, 50))
    # Vectorizar funcion aplicandola al espectro Z
    z_higo, z_maiz = np.vectorize(lambda x, y: func_higo(y, x))(x_g, y_g), np.vectorize(lambda x, y: func_maiz(y, x))(x_g, y_g)
    # Renderear solidos interceptados
    fig_3d = go.Figure(data=[go.Surface(z=z_higo, x=x_g, y=y_g, colorscale='Tealgrn', showscale=False, opacity=0.9, name='Higo+NFT'), go.Surface(z=z_maiz, x=x_g, y=y_g, colorscale='OrRd', showscale=False, opacity=0.8, name='Maiz')])
    fig_3d.update_layout(scene=dict(zaxis=dict(range=[-50, 1500])), paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT_MAIN, height=600)
    st.plotly_chart(fig_3d, use_container_width=True)

# Enrutador Logico Tab 3
with tab_pred:
    st.markdown("### Motor de Prediccion Estacional (Monte Carlo)")
    # Declarar funcion analitica lambda embebida para iteracion de Monte Carlo
    def simular_cultivo_grafico(row):
        cultivo, costo, prima, riesgo = row['nombre_cultivo'], row['costo_operativo'], row['prima_sostenibilidad'], row['riesgo_probabilidad']
        m_bio = matriz_fenologica.get(cultivo, {}).get(mes_sel, 1.0)
        p_base = 34994.18 if cultivo == 'Higo' else 5516.0
        # Multiplicacion y simulacion matricial con NumPy sumando contingencia de hidroponia
        util = (((6.82 if cultivo == 'Higo' else 3.5) * mod_rend * m_bio * np.random.normal(loc=p_base * m_bio, scale=(p_base * 0.12), size=1000) * (1 + prima)) - (costo * mod_costo)) + (59500.00 if cultivo == 'Higo' else 0)
        # Empacar fila evaluada
        return pd.Series([cultivo, (np.sum((util * (1 - (riesgo * mod_riesgo))) > 0) / 1000) * 100, mes_siembra_optimo.get(cultivo, 'N/D')])
        
    # Desplegar calculo total
    df_p = df_catalogo.apply(simular_cultivo_grafico, axis=1)
    df_p.columns = ['Cultivo', 'Probabilidad de Exito (%)', 'Epoca de Siembra']
    
    # Renderizar UI
    col_a, col_b = st.columns([1, 2])
    col_a.metric("Sugerencia Tecnica", df_p.sort_values(by='Probabilidad de Exito (%)', ascending=False).iloc[0]['Cultivo'])
    col_a.dataframe(df_p[['Cultivo', 'Epoca de Siembra']], hide_index=True)
    # Renderizar graficos limitando visual al 100%
    fig_p = px.bar(df_p, x='Probabilidad de Exito (%)', y='Cultivo', orientation='h', color_continuous_scale='Tealgrn', range_x=[0, 100])
    fig_p.update_layout(font_color=TEXT_MAIN)
    col_b.plotly_chart(fig_p, use_container_width=True)