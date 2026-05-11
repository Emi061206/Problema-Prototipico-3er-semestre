# =============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# Cada librería cumple un rol específico dentro del sistema.
# =============================================================================

# Módulo del sistema operativo: permite construir rutas de archivos de forma
# independiente al sistema operativo (Windows, Linux, Mac).
import os

# Streamlit: framework para construir aplicaciones web interactivas con Python.
# Se importa con el alias 'st' para escribir menos código.
import streamlit as st

# Pandas: librería para manipulación de datos en forma de tablas (DataFrames).
# Se importa con el alias 'pd'.
import pandas as pd

# NumPy: librería de cálculo numérico. Permite operaciones sobre arreglos y
# generación de números aleatorios para las simulaciones de Monte Carlo.
import numpy as np

# Plotly Graph Objects: crea gráficos interactivos de nivel avanzado,
# como la superficie 3D de evaluación regional.
import plotly.graph_objects as go

# Plotly Express: crea gráficos estadísticos de forma rápida y sencilla
# (ej. barras horizontales de competitividad y probabilidad).
import plotly.express as px

# SciPy Integrate: módulo de integración matemática. Se importa aunque en
# la versión actual los cálculos se modelan con funciones lambda y Plotly 3D.
from scipy import integrate

# FPDF: librería para generar documentos PDF desde Python.
# Se usa para crear los reportes descargables (anual y mensual).
from fpdf import FPDF

# Base64: permite codificar datos binarios en texto. Puede usarse para
# incrustar archivos dentro de HTML (uso potencial en descargas).
import base64


# =============================================================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA STREAMLIT
# =============================================================================

# Configura la pestaña del navegador, el diseño ancho y la barra lateral abierta.
# Debe ser la PRIMERA instrucción de Streamlit en el script.
st.set_page_config(
    page_title="Smart Agroforestry Morelos",  # Título de la pestaña del navegador
    layout="wide",                            # Diseño ancho: aprovecha todo el ancho de pantalla
    initial_sidebar_state="expanded"          # La barra lateral aparece abierta al iniciar
)


# =============================================================================
# PALETA DE COLORES DEL TEMA OSCURO
# =============================================================================

# Colores para indicadores y estados visuales:
# CYAN  = azul eléctrico  (valores positivos / métricas principales)
# GREEN = verde neón       (alta rentabilidad)
# AMBER = ámbar / naranja  (alertas o rendimiento medio)
# RED   = rojo             (baja rentabilidad o pérdida)
CYAN, GREEN, AMBER, RED = "#00e5ff", "#00ff88", "#ffb300", "#ff4444"

# Colores del fondo y la interfaz:
# BG_DEEP  = azul muy oscuro casi negro (fondo principal de la página)
# BG_CARD  = azul oscuro (fondo de tarjetas y barra lateral)
# BORDER   = azul medianoche (bordes de las tarjetas)
# TEXT_DIM = azul grisáceo (texto secundario/atenuado)
BG_DEEP, BG_CARD, BORDER, TEXT_DIM = "#060b18", "#090f1e", "#0d2a4a", "#6a8aaa"


# =============================================================================
# INYECCIÓN DE ESTILOS CSS PERSONALIZADOS
# =============================================================================

# st.markdown con unsafe_allow_html=True permite insertar CSS real en la app.
# Las llaves dobles {{ }} se usan para que Python no interprete las llaves
# como f-string y las pase tal cual al CSS.
st.markdown(f"""
<style>
/* Importa dos fuentes desde Google Fonts:
   - 'Rajdhani': fuente principal con distintos pesos (400 normal, 600 seminegrita, 700 negrita)
   - 'Share Tech Mono': fuente monoespaciada para etiquetas técnicas de métricas */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

/* Aplica la fuente y colores base a todos los elementos HTML de la app */
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {BG_DEEP}; color: #ffffff; }}

/* Estilo de la barra lateral: fondo oscuro y borde derecho divisor */
[data-testid="stSidebar"] {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}

/* Estilo de los contenedores de métricas (st.metric):
   fondo de tarjeta, borde sutil, relleno interno y esquinas redondeadas */
div[data-testid="metric-container"] {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; }}

/* Color de la etiqueta (título) de las métricas: atenuado y con fuente monoespaciada pequeña */
div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-family: 'Share Tech Mono', monospace; font-size: 11px; }}

/* Color del valor numérico de las métricas: CYAN brillante y en negrita */
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {CYAN} !important; font-weight: 700; }}

/* Clase CSS personalizada 'card-container' usada en gráficos y secciones:
   misma estética de tarjeta oscura con borde y margen inferior */
.card-container {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
</style>
""", unsafe_allow_html=True)  # Permite que Streamlit renderice el HTML/CSS crudo


# =============================================================================
# FUNCIÓN: generar_pdf_anual
# Genera el reporte de viabilidad agroecónomica anual en formato PDF.
# Parámetros:
#   municipio  (str)   : nombre del municipio seleccionado
#   utilidad   (float) : utilidad neta anual proyectada en MXN
#   inversion  (float) : inversión inicial (CAPEX) en MXN
#   prob_exito (float) : probabilidad de éxito del modelo (porcentaje)
#   suelo      (str)   : descripción del tipo de suelo del municipio
# Retorna: bytes del PDF generado (listo para descarga con st.download_button)
# =============================================================================
def generar_pdf_anual(municipio, utilidad, inversion, prob_exito, suelo):
    """Genera el dictamen técnico anual consolidado."""

    # Crea un nuevo documento PDF en blanco (tamaño carta por defecto)
    pdf = FPDF()

    # Añade la primera (y única) página al documento
    pdf.add_page()

    # Configura el color de relleno en verde oscuro RGB(30,120,30)
    # para el rectángulo de encabezado
    pdf.set_fill_color(30, 120, 30)

    # Dibuja un rectángulo relleno ('F') que ocupa el ancho completo de la hoja
    # desde la esquina superior izquierda (0,0) con 210mm de ancho y 40mm de alto
    pdf.rect(0, 0, 210, 40, 'F')

    # Fuente Arial en negrita ('B'), tamaño 16 para el título principal
    pdf.set_font("Arial", 'B', 16)

    # Color del texto en blanco para que contraste con el fondo verde
    pdf.set_text_color(255, 255, 255)

    # Imprime el título principal centrado ('C') con salto de línea automático (ln=True)
    pdf.cell(0, 10, "REPORTE ANUAL DE VIABILIDAD", ln=True, align='C')

    # Cambia a Arial normal, tamaño 12 para el subtítulo
    pdf.set_font("Arial", '', 12)

    # Imprime el subtítulo del reporte
    pdf.cell(0, 10, "Proyeccion Ciclo Completo 2026", ln=True, align='C')

    # Salto de 25 unidades para separar el encabezado del cuerpo del reporte
    pdf.ln(25)

    # Restablece el color del texto a negro para el cuerpo del documento
    pdf.set_text_color(0, 0, 0)

    # Fuente en negrita, tamaño 14 para el nombre del municipio
    pdf.set_font("Arial", 'B', 14)

    # Imprime el municipio analizado con salto de línea
    pdf.cell(0, 10, f"Municipio: {municipio}", ln=True)

    # Fuente normal, tamaño 11 para el texto descriptivo
    pdf.set_font("Arial", '', 11)

    # multi_cell: celda de texto que hace salto de línea automático al llegar al borde
    # Describe el modelo agroforestal evaluado y el tipo de suelo
    pdf.multi_cell(0, 7, f"Analisis de transicion al modelo Higo (1 ha) + Hidroponia (100m2) en suelo {suelo}.")

    # Separación interna antes de la tabla de resultados
    pdf.ln(10)

    # Color de relleno verde muy claro para los encabezados de la tabla
    pdf.set_fill_color(230, 245, 230)

    # Fuente en negrita para las celdas de encabezado de tabla
    pdf.set_font("Arial", 'B', 12)

    # Celda "CONCEPTO": ancho 90, alto 10, con bordes ('1'), sin salto de línea (0),
    # centrada ('C'), con fondo de color (True)
    pdf.cell(90, 10, "CONCEPTO", 1, 0, 'C', True)

    # Celda "VALOR ANUAL": igual que la anterior pero con salto de línea al final (1)
    pdf.cell(90, 10, "VALOR ANUAL", 1, 1, 'C', True)

    # Fuente normal para las filas de datos de la tabla
    pdf.set_font("Arial", '', 12)

    # Fila 1: Inversión Inicial (CAPEX)
    # Primera celda: etiqueta alineada a la izquierda (predeterminado)
    pdf.cell(90, 10, "Inversion Inicial (CAPEX)", 1)
    # Segunda celda: valor numérico formateado con comas y 2 decimales, alineado a la derecha ('R')
    pdf.cell(90, 10, f"$ {inversion:,.2f}", 1, 1, 'R')

    # Fila 2: Utilidad Operativa Neta
    pdf.cell(90, 10, "Utilidad Operativa Neta", 1)
    pdf.cell(90, 10, f"$ {utilidad:,.2f}", 1, 1, 'R')

    # Fila 3: Probabilidad de Éxito (1 decimal con símbolo %)
    pdf.cell(90, 10, "Probabilidad de Exito", 1)
    pdf.cell(90, 10, f"{prob_exito:.1f} %", 1, 1, 'R')

    # Separación antes del dictamen final
    pdf.ln(10)

    # Fuente en negrita para el título "DICTAMEN:"
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DICTAMEN:", ln=True)

    # Fuente cursiva ('I') para el párrafo de conclusión/recomendación
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 7, "Ejecucion recomendada. El modelo es altamente resiliente y garantiza flujo de caja.")

    # Convierte el PDF generado en memoria a bytes y lo retorna
    # bytes() es necesario porque Streamlit espera datos binarios para la descarga
    return bytes(pdf.output())


# =============================================================================
# FUNCIÓN: generar_pdf_mensual
# Genera un reporte de flujo de caja detallado para un mes específico.
# Parámetros:
#   mes        (str)  : nombre del mes seleccionado (ej. "Febrero")
#   municipio  (str)  : nombre del municipio analizado
#   datos_mes  (dict) : diccionario con los ingresos, egresos y neto del mes
# Retorna: bytes del PDF generado
# =============================================================================
def generar_pdf_mensual(mes, municipio, datos_mes):
    """Genera el desglose financiero detallado para un mes específico."""

    # Nuevo documento PDF vacío
    pdf = FPDF()
    pdf.add_page()

    # Color de encabezado azul para diferenciarlo del reporte anual (verde)
    pdf.set_fill_color(41, 128, 185)

    # Rectángulo de encabezado azul (mismo ancho que la página)
    pdf.rect(0, 0, 210, 40, 'F')

    # Fuente en negrita, tamaño 16 para el título
    pdf.set_font("Arial", 'B', 16)

    # Texto en blanco para el título
    pdf.set_text_color(255, 255, 255)

    # Título del reporte con el nombre del mes en mayúsculas (.upper())
    pdf.cell(0, 10, f"REPORTE MENSUAL: {mes.upper()}", ln=True, align='C')

    # Fuente normal, tamaño 12 para el subtítulo con el municipio
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Gestion Operativa - {municipio}", ln=True, align='C')

    # Separación del encabezado al cuerpo
    pdf.ln(25)

    # Restablece el texto a negro
    pdf.set_text_color(0, 0, 0)

    # Fuente en negrita para el título de la sección de flujo de caja
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen de Flujo de Caja Mensual", ln=True)

    # Fuente en negrita más pequeña (10) para los encabezados de la tabla
    pdf.set_font("Arial", 'B', 10)

    # Color de relleno gris claro para los encabezados de la tabla de flujo
    pdf.set_fill_color(240, 240, 240)

    # Fila de encabezados de la tabla con 4 columnas:
    # "Concepto" (70mm), "Ingresos" (40mm), "Egresos" (40mm), "Neto" (40mm)
    # El tercer parámetro (0 o 1) controla si hay salto de línea; solo la última tiene 1
    pdf.cell(70, 10, "Concepto", 1, 0, 'C', True)
    pdf.cell(40, 10, "Ingresos", 1, 0, 'C', True)
    pdf.cell(40, 10, "Egresos", 1, 0, 'C', True)
    pdf.cell(40, 10, "Neto", 1, 1, 'C', True)

    # Fuente normal, tamaño 10 para las filas de datos de la tabla
    pdf.set_font("Arial", '', 10)

    # Lista de filas de la tabla (cada fila es una lista de 4 textos)
    # Los valores se obtienen del diccionario 'datos_mes' recibido como parámetro:
    #   'ing_h'  = ingresos del módulo hidropónico
    #   'egr_h'  = egresos del módulo hidropónico
    #   'net_h'  = neto del módulo hidropónico (ing_h - egr_h)
    #   'ing_f'  = ingresos del cultivo de Higo (campo/finca)
    #   'egr_f'  = egresos del cultivo de Higo
    #   'net_f'  = neto del cultivo de Higo
    filas = [
        ["Modulo Hidroponico", f"$ {datos_mes['ing_h']:,.2f}", f"$ {datos_mes['egr_h']:,.2f}", f"$ {datos_mes['net_h']:,.2f}"],
        ["Cultivo de Higo",    f"$ {datos_mes['ing_f']:,.2f}", f"$ {datos_mes['egr_f']:,.2f}", f"$ {datos_mes['net_f']:,.2f}"],
        ["Costos Fijos (Prorrateo)", "$ 0.00", "$ 4,300.00", "-$ 4,300.00"]  # Costos fijos repartidos entre actividades
    ]

    # Itera sobre cada fila de la lista y crea las celdas correspondientes
    # f[0] = concepto, f[1] = ingresos, f[2] = egresos, f[3] = neto
    for f in filas:
        pdf.cell(70, 10, f[0], 1)           # Concepto alineado a la izquierda
        pdf.cell(40, 10, f[1], 1, 0, 'R')   # Ingresos alineados a la derecha
        pdf.cell(40, 10, f[2], 1, 0, 'R')   # Egresos alineados a la derecha
        pdf.cell(40, 10, f[3], 1, 1, 'R')   # Neto alineado a la derecha, con salto de línea

    # Separación antes de la nota técnica del mes
    pdf.ln(10)

    # Fuente en negrita para la nota técnica explicativa del mes
    pdf.set_font("Arial", 'B', 11)

    # La 'nota' proviene del diccionario del mes y explica el comportamiento operativo
    pdf.multi_cell(0, 7, f"Nota Tecnica: {datos_mes['nota']}")

    # Retorna el PDF completo en bytes para la descarga desde Streamlit
    return bytes(pdf.output())


# =============================================================================
# LÓGICA DE DATOS Y BARRA LATERAL (SIDEBAR)
# =============================================================================

# Título principal de la barra lateral de control
st.sidebar.header("Panel de Control")

# Menú desplegable para que el usuario elija el municipio de análisis.
# La elección del municipio afecta los modificadores de rendimiento, costo y riesgo.
municipio_sel = st.sidebar.selectbox(
    "Seleccione Municipio:",
    ["Temixco", "Cuautla", "Jiutepec"]  # Municipios disponibles con datos
)

# Menú desplegable para seleccionar el mes que se analizará en el reporte mensual.
# El mes seleccionado también influye en el modificador fenológico de los cultivos.
mes_sel = st.sidebar.selectbox(
    "Mes para Reporte Mensual:",
    ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
)


# =============================================================================
# BASE DE DATOS MENSUAL SIMULADA
# Diccionario que almacena los datos financieros de los meses con información detallada.
# Estructura de cada mes:
#   'ing_h' : ingresos brutos del módulo hidropónico (MXN)
#   'egr_h' : egresos/costos del módulo hidropónico (MXN)
#   'net_h' : utilidad neta del módulo hidropónico = ing_h - egr_h
#   'ing_f' : ingresos brutos del cultivo de Higo en campo (MXN)
#   'egr_f' : egresos/costos del cultivo de Higo (MXN)
#   'net_f' : utilidad neta del Higo = ing_f - egr_f
#   'nota'  : texto explicativo del comportamiento operativo del mes
# =============================================================================
datos_mensuales_db = {
    # Febrero: mes de cosecha máxima del Higo — ingresos por campo muy altos
    'Febrero': {
        'ing_h': 9800.0,    # Ingresos del módulo hidropónico (venta de lechuga, etc.)
        'egr_h': 2975.0,    # Costos de operación hidropónica (nutrientes, energía)
        'net_h': 6825.0,    # Ganancia neta hidropónica
        'ing_f': 119329.0,  # Ingresos del Higo (pico de cosecha)
        'egr_f': 4050.0,    # Costos de campo en época de cosecha
        'net_f': 115279.0,  # Ganancia neta del Higo en el mes pico
        'nota': "Pico de cosecha de Higo. Liquidez maxima."
    },
    # Junio: mes de mantenimiento del Higo — no hay cosecha, el Higo no genera ingresos
    'Junio': {
        'ing_h': 9800.0,    # El módulo hidropónico sí genera ingresos todo el año
        'egr_h': 2975.0,    # Costos hidropónicos constantes
        'net_h': 6825.0,    # Ganancia hidropónica constante
        'ing_f': 0.0,        # Sin ingresos del Higo en época de mantenimiento
        'egr_f': 1500.0,    # Solo costos de mantenimiento del campo
        'net_f': -1500.0,   # El Higo genera pérdida este mes (solo costo)
        'nota': "Fase de mantenimiento de Higo. Hidroponia cubre costos fijos."
    }
}

# Datos por defecto para todos los meses que no estén en el diccionario anterior.
# Representa un mes "normal" donde el Higo no tiene cosecha pero la hidroponía opera.
default_mes = {
    'ing_h': 9800.0,
    'egr_h': 2975.0,
    'net_h': 6825.0,
    'ing_f': 0.0,       # Sin cosecha de Higo en mes genérico
    'egr_f': 800.0,     # Costo mínimo de mantenimiento del campo
    'net_f': -800.0,    # El Higo tiene egreso neto en mes sin cosecha
    'nota': "Hidroponia mantiene el flujo operativo."
}


# =============================================================================
# BOTONES DE GENERACIÓN DE REPORTES EN LA BARRA LATERAL
# =============================================================================

# Separador visual en la barra lateral
st.sidebar.markdown("---")

# Subtítulo para la sección de descarga de reportes
st.sidebar.subheader("Generacion de Reportes")

# Botón que genera el reporte anual cuando el usuario hace clic.
# 'if st.sidebar.button(...)' evalúa a True solo cuando el botón es presionado.
if st.sidebar.button("Generar Reporte ANUAL"):
    # Llama a la función con valores representativos del modelo Higo + Hidroponía:
    #   Utilidad neta anual: $251,159.31 MXN
    #   Inversión inicial (CAPEX): $147,000.00 MXN
    #   Probabilidad de éxito: 95.4%
    #   Tipo de suelo: Vertisol/Feozem (suelo fértil de Morelos)
    pdf_anual = generar_pdf_anual(municipio_sel, 251159.31, 147000.00, 95.4, "Vertisol/Feozem")

    # Botón de descarga nativo de Streamlit. Solo aparece DESPUÉS de presionar el botón anterior.
    # 'data' recibe los bytes del PDF, 'file_name' define el nombre del archivo descargado.
    st.sidebar.download_button(
        "Descargar PDF Anual",
        data=pdf_anual,
        file_name=f"Reporte_Anual_{municipio_sel}.pdf",
        mime="application/pdf"  # Tipo MIME del archivo para que el navegador lo maneje correctamente
    )

# Botón para el reporte mensual. El texto muestra dinámicamente el mes seleccionado.
if st.sidebar.button(f"Generar Reporte de {mes_sel}"):
    # Busca los datos del mes seleccionado en el diccionario.
    # .get(mes_sel, default_mes) retorna 'default_mes' si el mes no tiene datos específicos.
    info_mes = datos_mensuales_db.get(mes_sel, default_mes)

    # Genera el PDF mensual con los datos encontrados (o los de default)
    pdf_mes = generar_pdf_mensual(mes_sel, municipio_sel, info_mes)

    # Botón de descarga del PDF mensual con nombre dinámico incluyendo mes y municipio
    st.sidebar.download_button(
        f"Descargar PDF {mes_sel}",
        data=pdf_mes,
        file_name=f"Reporte_{mes_sel}_{municipio_sel}.pdf",
        mime="application/pdf"
    )

# Nota al pie del archivo: el resto de la aplicación (dashboards, gráficos 3D
# y simulaciones Monte Carlo) se construye sobre este módulo de reportes.
# (Resto de la aplicación: Dashboards, Graficos 3D y Monte Carlo...)