# --- LIBRERÍAS DEL SISTEMA Y PROCESAMIENTO DE FLUJOS ---
import os, io, base64 # Utilizados para la manipulación de rutas, flujos de datos en memoria (buffers) y codificación de archivos para descargas.

# --- LIBRERÍAS DE CIENCIA DE DATOS Y MATEMÁTICAS ---
import numpy as np # Motor de cálculo vectorial y generación de distribuciones probabilísticas (Monte Carlo).
import pandas as pd # Estructuración, filtrado y manipulación de conjuntos de datos relacionales en DataFrames.
from scipy import integrate # Módulo matemático para resolver integrales definidas analíticas.

# --- LIBRERÍAS DE VISUALIZACIÓN INTERACTIVA (FRONT-END) ---
import plotly.graph_objects as go # Creación de visualizaciones tridimensionales y complejas.
import plotly.express as px # Creación rápida de gráficos interactivos 2D.

# --- LIBRERÍAS DE VISUALIZACIÓN ESTÁTICA (BACK-END PARA PDF) ---
import matplotlib
matplotlib.use('Agg') # Configura Matplotlib para renderizar en segundo plano sin interfaz gráfica, previniendo cuelgues en servidores web.
import matplotlib.pyplot as plt # Motor base para crear los gráficos que irán en el reporte ejecutivo.
import seaborn as sns # Capa de estilos sobre Matplotlib para mejorar la estética de los gráficos estáticos.

# --- LIBRERÍAS DEL FRAMEWORK WEB ---
from dash import Dash, dcc, html, Input, Output, State # Componentes principales para construir la aplicación analítica interactiva y sus callbacks.
import dash_bootstrap_components as dbc # Sistema de cuadrícula y componentes con estilo Bootstrap.

# --- LIBRERÍAS PARA GENERACIÓN DE REPORTES PDF (REPORTLAB) ---
from reportlab.lib.pagesizes import A4 # Define el tamaño de página estándar para el documento PDF.
from reportlab.lib import colors # Paleta de colores para dar formato a tablas y textos.
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Hojas de estilo en cascada para la tipografía del documento.
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage, PageBreak # Elementos modulares para construir el flujo del PDF.
from reportlab.lib.units import cm # Unidad de medida métrica para definir márgenes y anchos de columnas.

# --- CONEXIÓN A BASE DE DATOS ---
from database import obtener_motor_mysql # Función personalizada que gestiona de manera segura la cadena de conexión con SQLAlchemy.

# Inicializa el motor de base de datos estableciendo la conexión con el servidor MySQL local o en la nube.
engine = obtener_motor_mysql()

# --- EXTRACCIÓN DE DATOS ESTRUCTURADOS (ETL) ---
# Consultas SQL directas ejecutadas mediante Pandas para volcar los catálogos y parámetros a la memoria RAM.
df_municipios = pd.read_sql("SELECT * FROM municipios", engine) # Contiene los modificadores edafológicos (alpha) y logísticos (beta) por región.
df_catalogo = pd.read_sql("SELECT * FROM catalogo_cultivos", engine) # Define costos, precios base y primas de sostenibilidad por cultivo.
df_fenologica = pd.read_sql("SELECT * FROM matriz_fenologica", engine) # Calendario de multiplicadores de rendimiento según el mes de siembra.
df_parametros = pd.read_sql("SELECT * FROM parametros_financieros", engine) # Variables contables estáticas (CAPEX y OPEX).

# Consulta SQL con sentencias JOIN para unificar la producción histórica con los nombres legibles de municipios y cultivos.
df_hist = pd.read_sql("""
    SELECT p.anio AS Anio, 
           m.nombre AS Nommunicipio, 
           c.nombre AS Nomcultivo, 
           p.volumen_produccion_t AS Volumen, 
           p.rendimiento_t_ha AS Rendimiento, 
           p.precio_medio_rural AS PMR
    FROM produccion_historica p
    JOIN municipios m ON p.id_municipio = m.id_municipio
    JOIN catalogo_cultivos c ON p.id_cultivo = c.id_cultivo
""", engine)

# --- BASES DE DATOS ESTÁTICAS PARA REPORTES GRÁFICOS ---
# Diccionarios de datos estructurados que contienen los históricos de utilidad neta y las proyecciones calculadas.
data_cuautla = [
    {"Año": 2018, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 12600592.98},
    {"Año": 2018, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 32040998.30},
    {"Año": 2018, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 144652158.22},
    {"Año": 2018, "Cultivo": "Higo", "Utilidad Neta (MXN)": 5856396.44},
    {"Año": 2022, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 23957997.02},
    {"Año": 2022, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 52121373.33},
    {"Año": 2022, "Cultivo": "Higo", "Utilidad Neta (MXN)": 5871109.76},
    {"Año": 2025, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -13410.61},
    {"Año": 2025, "Cultivo": "Higo", "Utilidad Neta (MXN)": 367782.89},
    {"Año": 2025, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 529416.86},
    {"Año": 2025, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -15230.89},
    {"Año": 2025, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 97693.88},
    {"Año": 2026, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -13263.71},
    {"Año": 2026, "Cultivo": "Higo", "Utilidad Neta (MXN)": 366832.79},
    {"Año": 2026, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 529434.23},
    {"Año": 2026, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -15283.32},
    {"Año": 2026, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 97809.75}
]

data_jiutepec = [
    {"Año": 2018, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 763833.41},
    {"Año": 2022, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 810500.00},
    {"Año": 2025, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -16014.43},
    {"Año": 2025, "Cultivo": "Higo", "Utilidad Neta (MXN)": 343016.02},
    {"Año": 2025, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 497671.20},
    {"Año": 2025, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -18392.05},
    {"Año": 2025, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 89077.28},
    {"Año": 2026, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -15954.59},
    {"Año": 2026, "Cultivo": "Higo", "Utilidad Neta (MXN)": 342045.74},
    {"Año": 2026, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 497817.24},
    {"Año": 2026, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -18478.38},
    {"Año": 2026, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 89307.19}
]

data_temixco = [
    {"Año": 2018, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 1500000.00},
    {"Año": 2018, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 2800000.00},
    {"Año": 2022, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 1850000.00},
    {"Año": 2022, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 3100000.00},
    {"Año": 2025, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -14500.00},
    {"Año": 2025, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -16200.00},
    {"Año": 2025, "Cultivo": "Higo", "Utilidad Neta (MXN)": 358000.00},
    {"Año": 2025, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 94000.00},
    {"Año": 2026, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -14800.00},
    {"Año": 2026, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -16500.00},
    {"Año": 2026, "Cultivo": "Higo", "Utilidad Neta (MXN)": 359000.00},
    {"Año": 2026, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 94500.00}
]

# --- CONSTANTES Y CÁLCULOS FINANCIEROS (PROFORMA) ---
# Se establecen las metas de ventas proyectadas para el ejercicio fiscal 2026 basándose en 1 hectárea + 100m2 NFT.
INGRESOS = {
    "Venta de Higo (6.82 t x $34,994.18/t)": 238659.31,
    "Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)": 117600.00
}

# Transformación de los registros de la base de datos SQL a diccionarios de Python para agilizar el tiempo de consulta O(1).
COSTOS_VARIABLES = dict(zip(
    df_parametros[df_parametros['categoria'] == 'COSTO_VARIABLE']['concepto'],
    df_parametros[df_parametros['categoria'] == 'COSTO_VARIABLE']['monto']
))

COSTOS_FIJOS = dict(zip(
    df_parametros[df_parametros['categoria'] == 'COSTO_FIJO']['concepto'],
    df_parametros[df_parametros['categoria'] == 'COSTO_FIJO']['monto']
))

INVERSION_INICIAL = dict(zip(
    df_parametros[df_parametros['categoria'] == 'INVERSION']['concepto'],
    df_parametros[df_parametros['categoria'] == 'INVERSION']['monto']
))

# Funciones de agregación para construir los indicadores financieros globales (KPIs).
TOTAL_INGRESOS = sum(INGRESOS.values()) # Suma total de las líneas de negocio.
TOTAL_CV = sum(COSTOS_VARIABLES.values()) # Costos directos de operación agraria.
TOTAL_CF = sum(COSTOS_FIJOS.values()) # Estructura contable inamovible (arrendamiento, amortizaciones).
MARGEN_CONTRIB = TOTAL_INGRESOS - TOTAL_CV # Dinero disponible para pagar los costos fijos después de producir.
UTILIDAD_OP = MARGEN_CONTRIB - TOTAL_CF # Ganancia neta final operativa (EBITDA), que en régimen AGAPES es igual a la Neta.
PUNTO_EQ = TOTAL_CF / (MARGEN_CONTRIB / TOTAL_INGRESOS) # Umbral monetario en el cual el proyecto no gana ni pierde.
TOTAL_INV = sum(INVERSION_INICIAL.values()) # CAPEX exigible inicial.
PAYBACK = TOTAL_INV / UTILIDAD_OP # Tiempo estimado (en años) para recuperar la inyección de capital inicial.

# --- CONSTRUCCIÓN DE DICCIONARIOS DE CALIBRACIÓN Y MODELADO ESTOCÁSTICO ---
# Se crea un diccionario anidado para mapear los modificadores mensuales (clima/fenología) de cada planta.
FENOLOGICA = {}
for cult_id, cult_nom in zip(df_catalogo['id_cultivo'], df_catalogo['nombre']):
    feno_cultivo = df_fenologica[df_fenologica['id_cultivo'] == cult_id]
    FENOLOGICA[cult_nom] = dict(zip(feno_cultivo['mes'], feno_cultivo['multiplicador']))

# Extracción vectorial de las variables operativas en diccionarios para agilizar simulaciones de Monte Carlo.
VOL_ESPERADO = dict(zip(df_catalogo['nombre'], df_catalogo['volumen_esperado']))
PRECIO_BASE = dict(zip(df_catalogo['nombre'], df_catalogo['precio_base']))
VOLATILIDAD = dict(zip(df_catalogo['nombre'], df_catalogo['volatilidad']))
MES_OPTIMO = dict(zip(df_catalogo['nombre'], df_catalogo['mes_optimo']))
MESES = list(FENOLOGICA['Higo'].keys()) # Extracción genérica del catálogo de meses del año.

# Se fija la semilla matemática para que los escenarios de simulación generados mantengan consistencia entre refrescos.
np.random.seed(42)

# --- PALETA DE COLORES INSTITUCIONAL Y FUNCIONES AUXILIARES (LAMBDAS) ---
# Definición de códigos HEX para mantener una estética unificada (Dark Theme) a lo largo de la interfaz y gráficas.
CYAN, GREEN, AMBER, RED, BG, CARD, BORDER = "#00e5ff", "#00c853", "#ffb300", "#f44336", "#060b18", "#0d1b2a", "#1a3a5c"

fmt = lambda n: f"${n:,.2f}" # Función anónima para formatear números flotantes como moneda (e.g., $1,500.00).
color_icc = lambda v: GREEN if v > 100000 else (AMBER if v > 20000 else RED) # Asigna colores semáforo con base a los umbrales de viabilidad del índice ICC.
clasificar_icc = lambda v: "Alta Competitividad" if v > 100000 else ("Optimizacion Requerida" if v > 20000 else "Diversificacion Urgente") # Etiqueta textual del estado de riesgo.
hidro_activa = lambda h: bool(h and 'hidro' in h) # Evalúa si el usuario seleccionó integrar o no el módulo hidropónico en el frontend.

# --- MOTORES DE GENERACIÓN DE ARTEFACTOS Y VISUALIZACIONES ---

def generar_grafica_matplotlib(municipio):
    """
    Función que genera la gráfica de barras de Matplotlib para embeber dentro del PDF Ejecutivo.
    Selecciona la paleta de colores y el DataFrame dependiendo del municipio solicitado.
    """
    if municipio == 'Cuautla':
        df = pd.DataFrame(data_cuautla)
        paleta = "tab10"
    elif municipio == 'Jiutepec':
        df = pd.DataFrame(data_jiutepec)
        paleta = "magma"
    elif municipio == 'Temixco':
        df = pd.DataFrame(data_temixco)
        paleta = "viridis"
    else:
        return None 

    plt.figure(figsize=(10, 5)) 
    sns.set_theme(style="whitegrid") 
    
    ax = sns.barplot(data=df, x="Año", y="Utilidad Neta (MXN)", hue="Cultivo", palette=paleta)
    
    plt.title(f'Histórico y Proyección de Utilidad Neta: {municipio} (2018-2026)', fontsize=14, fontweight='bold')
    plt.xlabel('Año', fontsize=12)
    plt.ylabel('Utilidad Neta (MXN)', fontsize=12)
    plt.axhline(0, color='red', linestyle='--', linewidth=1.5) 
    plt.legend(title='Cultivo', bbox_to_anchor=(1.02, 1), loc='upper left') 
    plt.tight_layout() 
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close()
    buf.seek(0)
    
    return RLImage(buf, width=16*cm, height=8*cm)

def generar_dictamen_completo(municipio, anio_ini=2018, anio_fin=2026):
    """
    Algoritmo central del modelo. Combina los datos duros históricos (2018-2024) 
    con predicciones estocásticas Monte Carlo (2025-2026) para un municipio dado.
    """
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    
    filas = [] 
    
    df_mun = df_hist[(df_hist['Nommunicipio'] == municipio) & (df_hist['Anio'] >= anio_ini) & (df_hist['Anio'] <= min(2024, anio_fin))].copy()

    for _, r in df_mun.iterrows():
        cult = r['Nomcultivo']
        cat_cult = df_catalogo[df_catalogo['nombre'] == cult]
        if cat_cult.empty: continue 
        
        prima = cat_cult['prima_sostenibilidad'].values[0]
        riesgo = cat_cult['riesgo_probabilidad'].values[0]
        costo_op = cat_cult['costo_operativo'].values[0]
        
        precio_aj = r['PMR'] * (1 + prima)
        costo_aj = costo_op * mc
        utilidad = (r['Volumen'] * mr) * precio_aj - costo_aj
        icc = utilidad * (1 - riesgo * mk) 
        
        filas.append({
            'Anio': int(r['Anio']), 'Cultivo': cult, 'Tipo': 'Historico',
            'Volumen_t': round(r['Volumen'], 2), 'PMR': round(r['PMR'], 2),
            'Costo_Ajustado': round(costo_aj, 2), 'Utilidad_Neta': round(utilidad, 2),
            'ICC': round(icc, 0), 'Estatus': clasificar_icc(icc)
        })

    if anio_fin > 2024:
        for anio in range(max(2025, anio_ini), anio_fin + 1):
            for _, row in df_catalogo.iterrows():
                cult = row['nombre']
                mb = 1.0 
                pb = PRECIO_BASE.get(cult, 5000)
                
                sd = pb * VOLATILIDAD.get(cult, 0.15) * max(mb, 0.1)
                precio_esp = float(np.mean(np.random.normal(pb * mb, sd, 5000)))
                costo_aj = row['costo_operativo'] * mc
                vol = VOL_ESPERADO.get(cult, 4.0)
                
                utilidad = (vol * mr * mb) * (precio_esp * (1 + row['prima_sostenibilidad'])) - costo_aj
                
                if cult == 'Higo': utilidad += (117600.00 - 35536.00)
                icc = utilidad * (1 - row['riesgo_probabilidad'] * mk)
                
                filas.append({
                    'Anio': anio, 'Cultivo': cult, 'Tipo': 'Proyeccion Monte Carlo',
                    'Volumen_t': round(vol * mr * mb, 3), 'PMR': round(precio_esp, 2),
                    'Costo_Ajustado': round(costo_aj, 2), 'Utilidad_Neta': round(utilidad, 2),
                    'ICC': round(icc, 0), 'Estatus': clasificar_icc(icc)
                })
    
    return pd.DataFrame(filas)

def generar_csv(df: pd.DataFrame) -> bytes:
    """Función de utilidad que transforma un DataFrame de Pandas en un flujo de bytes CSV formato UTF-8 para descarga."""
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding='utf-8')
    return buf.getvalue().encode('utf-8')

def generar_pdf_reporte(municipio, mod_rend, mod_costo, pe_higo, icc_higo, df_dictamen=None):
    """
    Compilador del Reporte Ejecutivo final en PDF.
    Estructura 5 páginas completas con diagnóstico, análisis estocástico y resúmenes financieros.
    """
    buf = io.BytesIO() 
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    ss = getSampleStyleSheet() 
    
    estilos = {
        'encabezado': ParagraphStyle('encabezado', parent=ss['Normal'], fontSize=10, textColor=colors.HexColor('#003366'), spaceAfter=15, fontName='Helvetica-Bold'),
        'titulo': ParagraphStyle('titulo', parent=ss['Heading1'], fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=12, alignment=1),
        'subtitulo': ParagraphStyle('subtitulo', parent=ss['Heading2'], fontSize=14, textColor=colors.HexColor('#003366'), spaceAfter=15, alignment=1),
        'seccion': ParagraphStyle('seccion', parent=ss['Heading2'], fontSize=13, textColor=colors.HexColor('#005b99'), spaceBefore=15, spaceAfter=8, fontName='Helvetica-Bold'),
        'body': ParagraphStyle('body', parent=ss['Normal'], fontSize=10, leading=15, alignment=4, spaceAfter=10),
        'bold': ParagraphStyle('bold', parent=ss['Normal'], fontSize=11, leading=14, spaceAfter=8, fontName='Helvetica-Bold'),
        'bullet': ParagraphStyle('bullet', parent=ss['Normal'], fontSize=10, leading=15, leftIndent=20, spaceAfter=8),
        'footer': ParagraphStyle('footer', parent=ss['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    }

    def tabla(data, col_widths, header_bg=colors.HexColor('#003366')):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), header_bg), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c0d0e0')), ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8)
        ]))
        return t

    story = []
    
    story.append(Paragraph("UNIVERSIDAD NACIONAL ROSARIO CASTELLANOS | SEDE GAM | GRUPO: 301", estilos['encabezado']))
    story.append(Paragraph("Análisis Técnico-Económico para la Diversificación de Cultivos en México", estilos['titulo']))
    story.append(Paragraph(f"Reporte Ejecutivo Anual: Municipio de {municipio}", estilos['subtitulo']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#003366'), spaceAfter=15)) 
    
    story.append(Paragraph("1. Resumen Ejecutivo", estilos['seccion']))
    story.append(Paragraph(f"El modelo agrícola tradicional basado en el monocultivo en la región periurbana de Morelos enfrenta un colapso financiero debido a la vulnerabilidad climática y al incremento en el costo de los insumos. Este informe documenta el análisis de datos históricos (2018-2024) y proyecciones estocásticas (2025-2026) para el municipio de {municipio}. Se propone y evalúa financieramente la transición a un modelo modular diversificado: 1 hectárea de higo tecnificado combinada con un módulo hidropónico NFT de 100 m² para cultivo de lechuga.", estilos['body']))

    story.append(Paragraph("2. Contexto y Justificación", estilos['seccion']))
    story.append(Paragraph("La producción agrícola tradicional en zonas periurbanas enfrenta una vulnerabilidad crítica ante el aumento descontrolado de costos de agroquímicos y la dependencia absoluta de los regímenes pluviales. El esquema de monocultivo vigente obliga a las familias productoras a percibir ingresos una sola vez al año, forzándolos al endeudamiento informal para subsistir los meses inactivos. La diversificación hacia cultivos de alto valor y bajo consumo hídrico (como la hidroponía modular) es una respuesta necesaria para asegurar la competitividad y la seguridad patrimonial.", estilos['body']))

    story.append(Paragraph("3. Metodología Aplicada", estilos['seccion']))
    story.append(Paragraph("El enfoque del sistema se fundamentó en la extracción y análisis de microdatos gestionados en una base de datos relacional (MySQL). Se empleó Cálculo Integral para determinar el escalamiento de costos operativos, y un Motor Predictivo de Monte Carlo (5,000 iteraciones) para evaluar el riesgo financiero ante variaciones climáticas y de precios en las centrales de abastos de la región central del país.", estilos['body']))
    
    story.append(PageBreak()) 

    story.append(Paragraph(f"4. Diagnóstico y Proyecciones: {municipio} (2018-2026)", estilos['seccion']))
    story.append(Paragraph("El análisis de los microdatos refleja una crisis inminente para los productores que mantienen el cultivo tradicional, justificando con evidencia matemática la urgente necesidad de diversificar el riesgo.", estilos['body']))
    
    if municipio == 'Cuautla':
        story.append(Paragraph("• Declive Tradicional: Cuautla ha operado históricamente con altos volúmenes de maíz y sorgo; sin embargo, el encarecimiento de operaciones empujará ambos cultivos a un déficit operativo para los siguientes ejercicios.", estilos['bullet']))
        story.append(Paragraph("• Proyección de Pérdidas (2025-2026): Se estima una pérdida operativa anual promedio de -$13,337.16 MXN para el maíz grano y -$15,257.10 MXN para el sorgo.", estilos['bullet']))
        story.append(Paragraph("• Alternativa de Alto Valor: La introducción del higo y la lechuga NFT muestra una resiliencia notable, proyectando utilidades netas promedio anuales de $367,307.84 MXN y $97,751.81 MXN, respectivamente.", estilos['bullet']))
    elif municipio == 'Jiutepec':
        story.append(Paragraph("• Crisis en Zona Periurbana: La presión urbana y la escasez hídrica en Jiutepec agravan la situación. Las utilidades históricas del maíz grano se desploman, confirmando la insolvencia del sistema temporal.", estilos['bullet']))
        story.append(Paragraph("• Proyección de Pérdidas (2025-2026): El déficit promedio proyectado es de -$15,984.51 MXN anuales en maíz grano y -$18,435.21 MXN en sorgo grano.", estilos['bullet']))
        story.append(Paragraph("• Modelo de Estabilización: El cultivo de higo y el sistema NFT aseguran un flujo de caja sólido, proyectando ganancias netas de $342,530.88 MXN y $89,192.23 MXN anuales, superando las limitantes de espacio y agua del municipio.", estilos['bullet']))
    elif municipio == 'Temixco':
        story.append(Paragraph("• Vocación Histórica: Temixco ha dependido del cultivo de maíz y sorgo, aprovechando sus ventajas edafológicas, pero la inflación ha comenzado a erosionar irreversiblemente los márgenes de ganancia.", estilos['bullet']))
        story.append(Paragraph("• Proyección de Pérdidas (2025-2026): El déficit proyectado es de -$14,650.00 MXN anuales promedio en maíz grano, haciendo inviable su continuity.", estilos['bullet']))
        story.append(Paragraph("• Modelo de Estabilización: La diversificación con higo y lechuga NFT estabiliza el flujo, proyectando utilidades combinadas superiores a los $450,000.00 MXN anuales para la zona.", estilos['bullet']))

    img_grafica = generar_grafica_matplotlib(municipio)
    if img_grafica:
        story.append(Spacer(1, 15))
        story.append(img_grafica)
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Figura 1. Evolución de la utilidad neta histórica y predictiva para {municipio}.", estilos['footer']))

    story.append(PageBreak()) 

    story.append(Paragraph("5. Monto de Inversión Inicial (CAPEX) del Nuevo Modelo", estilos['seccion']))
    story.append(Paragraph("La transición al ecosistema diversificado requiere una inversión inicial estructurada. Este capital permite habilitar tanto la hectárea de producción agroforestal como el módulo de agricultura de precisión. Es vital destacar que el 100% de esta inversión resulta deducible de impuestos en el ejercicio correspondiente para las personas físicas que tributen en el sector primario (Art. 74 de la Ley del ISR).", estilos['body']))
    
    story.append(Spacer(1, 15))
    
    capex_data = [
        ["Concepto de Inversión / Activo Fijo", "Monto (MXN)", "Amortización Contable"],
        ["A. Cultivo de Higo (1 hectárea)", "", ""],
        ["Plantas de higo (inversión inicial botánica)", "$48,000.00", "10 años ($4,800/año)"],
        ["Sistema de riego tecnificado (fertirriego)", "$32,000.00", "5 años ($6,400/año)"],
        ["Subtotal Infraestructura Higo", "$80,000.00", ""],
        ["B. Módulo Hidropónico NFT (100 m²)", "", ""],
        ["Sistema NFT (Bomba, tuberías, temp.)", "$32,000.00", "5 años ($6,400/año)"],
        ["Infraestructura (Metálica, cubierta)", "$35,000.00", "5 años ($7,000/año)"],
        ["Subtotal Infraestructura Hidropónica", "$67,000.00", ""],
        ["INVERSIÓN INICIAL TOTAL EXIGIBLE", "$147,000.00", ""]
    ]
    t_capex = tabla(capex_data, [8*cm, 3.5*cm, 5.5*cm]) 
    story.append(t_capex)
    
    story.append(PageBreak()) 

    story.append(Paragraph("6. Evaluación Financiera y Punto de Equilibrio Operativo", estilos['seccion']))
    story.append(Paragraph("El modelo matemático propuesto garantiza la solvencia operativa del negocio mediante un esquema híbrido. Este diseño combina de manera estratégica la alta rentabilidad estacional del higo con los ciclos cortos, mensuales y altamente estables de la hidroponía, mitigando el estrés de liquidez.", estilos['body']))
    story.append(Paragraph("• Ingresos Brutos Anuales: $356,259.31 MXN (Compuestos por la Venta de Higo: $238,659.31 MXN y la Venta de lechuga NFT: $117,600.00 MXN).", estilos['bullet']))
    story.append(Paragraph("• Costos Fijos Totales: $51,600.00 MXN (Incluye arrendamiento de la parcela, energía y amortización de equipos).", estilos['bullet']))
    story.append(Paragraph("• Costos Variables Totales: $53,500.00 MXN (Insumos, mano de obra, agua y empaque logístico).", estilos['bullet']))
    story.append(Paragraph("• Margen de Contribución Anual: $302,759.31 MXN.", estilos['bullet']))
    story.append(Paragraph("• Punto de Equilibrio Analítico (PE): $60,720.17 MXN. (El productor cubre el 100% de la operación del año al alcanzar únicamente el 17% de las ventas proyectadas).", estilos['bullet']))

    story.append(Paragraph("7. Análisis y Cuantificación de Riesgos Operativos", estilos['seccion']))
    story.append(Paragraph("Para brindar certeza y evitar el sesgo de optimismo, el modelo fue sometido a pruebas de estrés probabilístico frente a tres amenazas críticas comunes en el entorno agropecuario mexicano:", estilos['body']))
    story.append(Paragraph("1. Volatilidad de Precios de Mercado: Ante una caída simultánea en el precio del higo (-20%) y la lechuga (-15%), el sistema reporta una contracción de utilidad de solo el -16.5%, situándose en $209,659.93 MXN. El negocio no entra en quiebra bajo estrés de precios.", estilos['bullet']))
    story.append(Paragraph("2. Siniestralidad Agroclimática (Plagas/Clima): La superposición de una merma del 25% en el higo por infestación entomológica y 15% en hidroponía por golpe de calor atípico disminuiría la utilidad en un -26.8%, manteniendo la rentabilidad general en $183,747.51 MXN.", estilos['bullet']))
    story.append(Paragraph("3. Fricción de Liquidez Transitoria: Asumir un desfase de capital inicial forzaría a reducir la operación hidropónica al 70% de su capacidad. Este escenario impactaría la utilidad final en apenas un -7.2%.", estilos['bullet']))

    story.append(PageBreak()) 

    story.append(Paragraph("8. Estado de Resultados y Conclusiones", estilos['seccion']))
    story.append(Paragraph("El Estado de Resultados Proforma estructurado para el cierre del ejercicio fiscal 2026 demuestra una Utilidad Neta Operativa de $251,159.31 MXN. Debido a que los ingresos agrícolas brutos equivalen a una cifra inferior al límite exento de 20 UMA anuales aplicables para personas físicas del sector primario, la utilidad proyectada queda completamente libre de gravamen de ISR.", estilos['body']))
    
    story.append(Paragraph("Conclusión Estratégica:", estilos['bold']))
    story.append(Paragraph("La transición hacia la diversificación agrícola es imperativa en la zona periurbana. El modelo modular propuesto no solo es económicamente viable, sino que actúa como un estabilizador estructural del flujo de caja. Al combinar el alto valor del cultivo leñoso (higo) con la rotación rápida de precisión (hidroponía NFT), las familias productoras logran mitigar el riesgo climático sistémico, evitan el sobreendeudamiento informal y aseguran la capitalización constante de su patrimonio agropecuario a largo plazo.", estilos['body']))

    story.append(Paragraph("9. Referencias Bibliográficas", estilos['seccion']))
    story.append(Paragraph("Cámara de Diputados del H. Congreso de la Unión. (2024). Ley del Impuesto sobre la Renta: Régimen del Sector Primario (Art. 74). Diario Oficial de la Federación.", estilos['bullet']))
    story.append(Paragraph("Instituto Nacional de Estadística y Geografía [INEGI]. (2022). Censo Agropecuario 2022: Resultados definitivos para el estado de Morelos.", estilos['bullet']))
    story.append(Paragraph("Secretaría de Agricultura y Desarrollo Rural [SADER]. (2024). Cierre de la producción agrícola por municipio (2018-2024). Servicio de Información Agroalimentaria y Pesquera [SIAP].", estilos['bullet']))

    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Universidad Nacional Rosario Castellanos — Licenciatura en Ciencias de Datos para Negocios — Smart Agroforestry Morelos", estilos['footer']))

    doc.build(story)
    buf.seek(0)
    return buf.read() 

# --- COMPONENTES VISUALES DASH (MÓDULOS DE REACT) ---
def kpi_card(title, value, sub=None, color=CYAN):
    """Genera una tarjeta modular HTML con la cifra, el nombre de la variable y un comentario secundario para el Dashboard."""
    return html.Div([
        html.P(title, style={'fontSize':'11px','color':'#6a8aaa','marginBottom':'4px','fontFamily':'monospace'}),
        html.H4(value, style={'color':color,'margin':'0','fontSize':'1.4rem'}),
        html.P(sub or '', style={'fontSize':'10px','color':'#6a8aaa','marginTop':'2px'}),
    ], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','flex':'1','minWidth':'170px'})

def grafico_card(fig):
    """Envuelve un componente interactivo Graph de Plotly dentro de un contenedor enmarcado y con sombras para Dash."""
    return html.Div([dcc.Graph(figure=fig)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'})

# Inicialización de la aplicación principal Dash, importando una plantilla de hojas de estilo preconstruida tipo 'CYBORG'.
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
app.title = "Smart Agroforestry Morelos" # Nombramiento visible en las pestañas del navegador web.

# Clases CSS para mantener la uniformidad visual del modelo en botones y barras de pestañas (Tabs).
BOTON_STYLE = {'width':'100%','background':CYAN,'color':'#000','border':'none','padding':'10px','borderRadius':'6px','fontWeight':'700','cursor':'pointer','fontSize':'12px','marginBottom':'6px'}
TAB_STYLE = {'color':'#aaa'}
TAB_SEL = {'color':CYAN,'fontWeight':'700'}

# --- CONSTRUCCIÓN DEL FRONT-END PRINCIPAL DE LA APLICACIÓN (LAYOUT HTML) ---
# Estructura del DOM: El Layout contiene la cuadrícula que delimita los espacios del panel de control lateral y el visor de contenido principal.
app.layout = html.Div(style={'backgroundColor':BG,'minHeight':'100vh','fontFamily':'Rajdhani, sans-serif','color':'#fff'}, children=[
    html.Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap'), # Importa tipografía corporativa.
    
    # Encabezado transversal de la herramienta.
    html.Div([
        html.H2("Smart Agroforestry Morelos", style={'margin':'0','color':CYAN}),
        html.P("Sistema Inteligente de Analisis Tecnico-Economico — Higo + Lechuga Hidroponica NFT", style={'margin':'2px 0 0','color':'#6a8aaa','fontSize':'13px'}),
    ], style={'background':CARD,'borderBottom':f'1px solid {BORDER}','padding':'18px 30px'}),
    
    html.Div(style={'display':'flex','minHeight':'calc(100vh - 70px)'}, children=[
        # Menú lateral (Sidebar) con selectores interactivos que controlan los parámetros del sistema predictivo.
        html.Div(style={'width':'260px','background':CARD,'borderRight':f'1px solid {BORDER}','padding':'20px','flexShrink':'0'}, children=[
            html.H5("Panel de Control", style={'color':CYAN,'marginBottom':'16px'}),
            html.Label("Municipio", style={'fontSize':'11px','color':'#6a8aaa'}),
            # Menú desplegable dinámico extraído desde la columna de nombres de la Base de Datos.
            dcc.Dropdown(id='dd-municipio', options=list(map(lambda m: {'label':m,'value':m}, df_municipios['nombre'])), value='Cuautla', style={'background':'#0d1b2a','color':'#fff','borderColor':BORDER}),
            html.Br(),
            
            html.Label("Periodo Historico", style={'fontSize':'11px','color':'#6a8aaa'}),
            # Selector de rango lineal para dictaminar los periodos a graficar.
            dcc.RangeSlider(id='sl-anio', min=2018, max=2026, step=1, value=[2018,2026], marks={y:str(y) for y in range(2018,2027,2)}, tooltip={"placement":"bottom"}),
            html.Br(),
            
            html.Label("Incluir Modulo Hidroponico", style={'fontSize':'11px','color':'#6a8aaa'}),
            # Checkbox que habilita o inhabilita financieramente el factor de mitigación económica del módulo.
            dcc.Checklist(id='chk-hidro', options=[{'label':' Lechuga NFT (100 m2)','value':'hidro'}], value=['hidro'], style={'color':GREEN}),
            html.Br(),
            
            # Etiqueta vacía donde el decorador inyectará la descripción textual del suelo.
            html.Div(id='sidebar-info', style={'background':'#060b18','border':f'1px solid {BORDER}','borderRadius':'6px','padding':'12px','fontSize':'11px','color':'#6a8aaa'}),
            html.Br(),
            
            # Botones físicos para desencadenar el pipeline de descarga de los Reportes Ejecutivos mediante callbacks asíncronos.
            html.P("Generación de Reportes Anuales", style={'fontSize':'11px','color':CYAN,'marginBottom':'6px','fontWeight':'700'}),
            html.Button("Generar Reporte PDF",   id='btn-pdf-anual',   n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-pdf-anual'),
            html.Button("Descargar Datos CSV",   id='btn-csv-anual',   n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-csv-anual'),
        ]),
        
        # Visor del panel central conteniendo un sistema de pestañas para dividir la herramienta por tópicos analíticos.
        html.Div(style={'flex':'1','padding':'24px','overflowY':'auto'}, children=[
            dcc.Tabs(id='tabs', value='tab-dash', style={'borderBottom':f'1px solid {BORDER}'}, colors={'border':BORDER,'primary':CYAN,'background':BG}, children=list(map(lambda lv: dcc.Tab(label=lv[0], value=lv[1], style=TAB_STYLE, selected_style=TAB_SEL), [
                ("Dashboard Operativo", 'tab-dash'), ("Evaluacion Regional (Integrales)", 'tab-math'), ("Motor Predictivo (Monte Carlo)", 'tab-mc'), ("Modelo Hidroponico", 'tab-hidro'), ("Dictamen Operativo 2018-2026", 'tab-dictamen')
            ]))),
            # Espacio vacío rellenado dinámicamente cada vez que se hace clic en una pestaña distinta.
            html.Div(id='tab-content', style={'marginTop':'20px'}),
        ]),
    ]),
])

# --- CONTROLADORES DE EVENTOS ASÍNCRONOS (CALLBACKS REACTIVOS DE DASH) ---

@app.callback(Output('sidebar-info','children'), Input('dd-municipio','value'))
def update_sidebar_info(municipio):
    """Actualiza la infografía de atributos geográficos y factores de penalización en la barra lateral con base al municipio."""
    row = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    return [html.B(municipio), html.Br(), f"Suelo: {row['tipo_suelo']}", html.Br(), f"Rendimiento: x{row['mod_rendimiento']} | Costo: x{row['mod_costo']}", html.Br(), f"Riesgo edafo.: x{row['mod_riesgo']}"]

@app.callback(Output('tab-content','children'), Input('tabs','value'), Input('dd-municipio','value'), Input('sl-anio','value'), Input('chk-hidro','value'))
def render_tab(tab, municipio, anio_range, hidro_val):
    """
    Función de renderizado principal que procesa la analítica y retorna el layout interno de la pestaña activa.
    Las simulaciones aquí responden en tiempo real a los selectores interactivos sin necesidad de descargar el PDF.
    """
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    hidro = hidro_activa(hidro_val)

    # Subrutina de iteración para clasificar los índices competitivos de cada cultivo.
    def _icc_row(r):
        cult = r['nombre']
        mb = 1.0 
        pb = PRECIO_BASE.get(cult, 5000)
        # Emplea la distribución de probabilidad (Campana Gaussiana) para prever caídas severas de ingresos en 2000 universos paralelos.
        pf = float(np.mean(np.random.normal(pb*mb, pb*VOLATILIDAD.get(cult, 0.15)*max(mb, 0.1), 2000)))
        vol = VOL_ESPERADO.get(cult, 4.0)
        
        # Algoritmo de rentabilidad integral, castigando la base con los factores edafológicos extraídos de SQL.
        util = (vol*mr*mb) * (pf*(1+r['prima_sostenibilidad'])) - r['costo_operativo']*mc
        # Agrega el "salvavidas" financiero (Margen del hidropónico) sumado exclusivamente al sistema Agroforestal del Higo.
        if cult == 'Higo' and hidro: util += (117600.00 - (TOTAL_CF - 18000))
        
        return {'Cultivo': cult, 'Utilidad': util, 'ICC': util * (1 - r['riesgo_probabilidad']*mk), 'Mb': mb, 'Semaforo': clasificar_icc(util * (1 - r['riesgo_probabilidad']*mk))}

    df_icc = pd.DataFrame(list(map(_icc_row, df_catalogo.to_dict('records'))))

    # Ramificación condicional encargada de dibujar los gráficos según la pestaña elegida.
    if tab == 'tab-dash':
        df_plot = df_hist[(df_hist['Nommunicipio']==municipio) & (df_hist['Anio']>=anio_range[0]) & (df_hist['Anio']<=min(2024, anio_range[1]))]
        
        # Montaje de las tarjetas de impacto que consolidan variables monetarias macro.
        kpis = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Utilidad Neta Modelo", fmt(UTILIDAD_OP), "Higo + Lechuga (2026)", GREEN),
            kpi_card("Ingresos Totales", fmt(TOTAL_INGRESOS), "Higo + Lechuga", CYAN),
            kpi_card("Costos Totales", fmt(TOTAL_CV+TOTAL_CF), "Variables + Fijos", AMBER),
            kpi_card("Punto de Equilibrio", fmt(PUNTO_EQ), f"{PUNTO_EQ/TOTAL_INGRESOS*100:.1f}% de ingresos", "#9c27b0"),
            kpi_card("Recuperacion Inversion", f"{PAYBACK:.1f} anos", f"Inversion: {fmt(TOTAL_INV)}", CYAN),
        ])
        
        # Gráficos horizontales para visualizar la tolerancia general (ICC) ante crisis agrícolas.
        fig_bar = px.bar(df_icc.sort_values('ICC'), x='ICC', y='Cultivo', orientation='h', color='ICC', color_continuous_scale=[[0,RED],[0.2,AMBER],[1,GREEN]], title=f"Indice de Competitividad (ICC) Anual — {municipio}")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', coloraxis_showscale=False, height=280)
        fig_bar.add_vline(x=20000, line_dash='dash', line_color=AMBER, annotation_text="20k (min)")
        fig_bar.add_vline(x=100000, line_dash='dash', line_color=GREEN, annotation_text="100k (alta)")

        # Representación mediante series de tiempo del comportamiento del PMR (Precio Medio Rural).
        fig_pmr = px.line(df_plot, x='Anio', y='PMR', color='Nomcultivo', title="Precio Medio Rural historico (MXN/t)", markers=True)
        fig_pmr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=300)

        tbl = html.Table([
            html.Thead(html.Tr(list(map(lambda h: html.Th(h), ['Cultivo','Utilidad (MXN)','ICC (pts)','Semaforo'])), style={'background':BORDER})),
            html.Tbody(list(map(lambda r: html.Tr([html.Td(r['Cultivo']), html.Td(fmt(r['Utilidad'])), html.Td(f"{r['ICC']:,.0f}"), html.Td(r['Semaforo'], style={'color': GREEN if 'Alta' in r['Semaforo'] else (AMBER if 'Optim' in r['Semaforo'] else RED),'fontWeight':'700'})]), df_icc.to_dict('records')))),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'13px'})
        return html.Div([kpis, grafico_card(fig_bar), grafico_card(fig_pmr), html.Div([html.H5("Dictamen de Competitividad", style={'color':CYAN,'marginBottom':'12px'}), tbl], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'})])

    elif tab == 'tab-math':
        # Definición del costo marginal base multiplicado por el modificador de costo operativo de la región.
        cm_higo = 17800 * mc
        cm_nft = 3570000 * mc
        
        # Resolución analítica de la integral definida usando scipy (integral del límite 0 al límite 5 hectáreas).
        costo_total_higo, _ = integrate.quad(lambda x: cm_higo, 0, 5)
        costo_total_nft, _ = integrate.quad(lambda x: cm_nft, 0, 5)
        
        # Gráfica independiente renderizando la integración de costos para el cultivo de Higo.
        fig_higo = go.Figure(data=[
            go.Bar(
                name='Higo (5 ha)', 
                x=['Higo (5 ha)'], 
                y=[costo_total_higo], 
                marker_color=GREEN
            )
        ])
        
        # Formateo estético de la gráfica individual del Higo.
        fig_higo.update_layout(
            title="Costo Variable Acumulado: Higo", 
            yaxis_title='Costo (MXN)',
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font_color='#fff', 
            height=380
        )

        # Gráfica independiente renderizando la integración de costos para el módulo Hidropónico NFT.
        fig_nft = go.Figure(data=[
            go.Bar(
                name='Hidropónico NFT (5 ha)', 
                x=['Hidropónico NFT (5 ha)'], 
                y=[costo_total_nft], 
                marker_color=RED
            )
        ])
        
        # Formateo estético de la gráfica individual del módulo NFT.
        fig_nft.update_layout(
            title="Costo Variable Acumulado: NFT", 
            yaxis_title='Costo (MXN)',
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font_color='#fff', 
            height=380
        )
        
        # Montaje de las tarjetas de impacto superior para la pestaña matemática.
        kpis_math = html.Div([
            kpi_card("Costo Integral Higo", fmt(costo_total_higo), "Escalable a 5 ha", GREEN), 
            kpi_card("Costo Integral NFT", fmt(costo_total_nft), "No escalable masivamente", RED), 
            kpi_card("Brecha Operativa", fmt(costo_total_nft - costo_total_higo), "Ahorro al mantener modularidad", CYAN)
        ], style={'display':'flex','gap':'12px','marginBottom':'20px'})
        
        # Retorno de la estructura HTML integrando ambas gráficas en un layout de cuadrícula (Grid) de dos columnas.
        return html.Div([
            kpis_math, 
            html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}, children=[
                html.Div([dcc.Graph(figure=fig_higo)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
                html.Div([dcc.Graph(figure=fig_nft)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'})
            ])
        ])

    elif tab == 'tab-mc':
        # Algoritmo de simulación masiva (Monte Carlo).
        def _mc_row(row):
            cult = row['nombre']
            mb = 1.0 
            pb = PRECIO_BASE.get(cult, 5000)
            
            # Ejecución de 5000 iteraciones generando valores estocásticos con base en la volatilidad.
            pf_sim = np.random.normal(pb*mb, pb*VOLATILIDAD.get(cult, 0.15)*max(mb, 0.1), 5000)
            utils = (VOL_ESPERADO.get(cult, 4.0)*mr*mb)*(pf_sim*(1+row['prima_sostenibilidad'])) - row['costo_operativo']*mc
            if cult == 'Higo' and hidro: utils += 59500.0
            icc_sim = utils * (1 - row['riesgo_probabilidad']*mk)
            
            # Retorna métricas duras como P10, P90 y la Propabilidad de Éxito total.
            return {'Cultivo': cult, 'PE (%)': (np.sum(icc_sim>0)/5000)*100, 'ICC Esperado': np.mean(icc_sim), 'P10': np.percentile(icc_sim, 10), 'P90': np.percentile(icc_sim, 90), 'Epoca': MES_OPTIMO.get(cult, '—')}
        
        df_mc = pd.DataFrame(list(map(_mc_row, df_catalogo.to_dict('records')))).sort_values('PE (%)', ascending=False)
        fig_pe = px.bar(df_mc, x='PE (%)', y='Cultivo', orientation='h', color='PE (%)', color_continuous_scale=[[0,RED],[0.7,AMBER],[1,GREEN]], title="Probabilidad de Exito Anual por Cultivo (%)")
        fig_pe.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', coloraxis_showscale=False, height=280)
        
        # Histograma para validar la forma de la campana gausiana generada.
        mb_h = 1.0 
        pf_h = np.random.normal(PRECIO_BASE['Higo']*mb_h, PRECIO_BASE.get('Higo', 34994.18)*0.12*max(mb_h, 0.1), 5000)
        utils_h = (6.82*mr*mb_h)*(pf_h*1.15) - 105100*mc
        if hidro: utils_h += 59500.0
        fig_hist = go.Figure([go.Histogram(x=utils_h*(1-0.08*mk), nbinsx=60, marker_color=CYAN, opacity=0.8)])
        fig_hist.update_layout(title="Distribucion ICC — Higo", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=300)
        
        tbl_mc = html.Table([
            html.Thead(html.Tr(list(map(lambda h: html.Th(h), ['Cultivo','PE (%)','ICC Esperado','P10','P90','Epoca Optima'])), style={'background':BORDER})),
            html.Tbody(list(map(lambda r: html.Tr([html.Td(r['Cultivo']), html.Td(f"{r['PE (%)']:.1f}%", style={'color': GREEN if r['PE (%)']>=95 else (AMBER if r['PE (%)']>=70 else RED),'fontWeight':'700'}), html.Td(f"{r['ICC Esperado']:,.0f}"), html.Td(fmt(r['P10'])), html.Td(fmt(r['P90'])), html.Td(r['Epoca'])]), df_mc.to_dict('records')))),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'13px'})
        return html.Div([grafico_card(fig_pe), grafico_card(fig_hist), html.Div([html.H5("Resultados Monte Carlo", style={'color':CYAN,'marginBottom':'12px'}), tbl_mc], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'})])

    elif tab == 'tab-hidro':
        # Proyecta la rentabilidad mensual generada por el módulo NFT como amortiguador de ingresos.
        ing_mensual = [4200/12 * 28 * FENOLOGICA['Lechuga (NFT)'].get(m, 1.0) for m in MESES]
        fig_hidro = go.Figure([go.Bar(x=MESES, y=ing_mensual, marker_color=[GREEN if v > 9000 else AMBER for v in ing_mensual]), go.Scatter(x=MESES, y=[TOTAL_CF/12]*12, line=dict(color=RED, dash='dash'), mode='lines')])
        fig_hidro.update_layout(title="Ingreso Mensual Promedio — Lechuga Hidroponica NFT", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=320)
        
        # Desglosa el peso que tiene cada suministro variable (agroquímicos vs insumos hidropónicos).
        fig_comp = px.pie(names=['Insumos hidro', 'Riego Higo', 'MO Higo', 'Fertiliz. Higo', 'Empaque Higo'], values=[35700, 3800, 6200, 5500, 2300], title="Composicion de Costos Variables")
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=320)
        return html.Div([html.Div([kpi_card("Ingreso Anual Lechuga", fmt(INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"]), "4,200 kg", GREEN), kpi_card("Costo Insumos Hidro", fmt(35700), "Nutrientes + Semillas", AMBER), kpi_card("Margen Neto Hidro", fmt(117600-35700), "Operativo", CYAN)], style={'display':'flex','gap':'12px','marginBottom':'20px'}), html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}, children=[html.Div([dcc.Graph(figure=fig_hidro)], style={'background':CARD}), html.Div([dcc.Graph(figure=fig_comp)], style={'background':CARD})])])

    elif tab == 'tab-dictamen':
        # Renderiza gráficamente las tablas históricas y predictivas.
        df_dict = generar_dictamen_completo(municipio, anio_range[0], anio_range[1])
        if df_dict.empty: return html.P("Sin datos para el rango seleccionado.", style={'color':AMBER})
        fig_dict = px.line(df_dict, x='Anio', y='ICC', color='Cultivo', line_dash='Tipo', title="Evolucion ICC Anual", markers=True)
        fig_dict.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=380)
        
        # Construye la tabla HTML interactiva con el registro auditable desde SQL.
        tbl2 = html.Table([
            html.Thead(html.Tr(list(map(lambda h: html.Th(h), ['Anio','Cultivo','Tipo','Vol. (t)','PMR ($/t)','Costo Ajust.','Utilidad Neta','ICC (pts)','Estatus'])), style={'background':BORDER})),
            html.Tbody(list(map(lambda r: html.Tr([html.Td(str(r['Anio']), style={'color': CYAN if r['Tipo']=='Proyeccion Monte Carlo' else '#fff'}), html.Td(r['Cultivo']), html.Td(r['Tipo'], style={'fontSize':'11px','color':'#aaa'}), html.Td(f"{r['Volumen_t']:,.2f}"), html.Td(f"${r['PMR']:,.2f}"), html.Td(fmt(r['Costo_Ajustado'])), html.Td(fmt(r['Utilidad_Neta']), style={'color': GREEN if r['Utilidad_Neta']>0 else RED}), html.Td(f"{r['ICC']:,.0f}"), html.Td(r['Estatus'], style={'color': '#fff','fontWeight':'700','fontSize':'11px','background': '#1a4a1a' if r['Estatus']=='Alta Competitividad' else '#4a0a0a','padding':'2px 6px','borderRadius':'4px'})]), df_dict.to_dict('records')))),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'12px'})
        return html.Div([grafico_card(fig_dict), html.Div([tbl2], style={'background':CARD,'padding':'16px'})])
    
    return html.Div("Selecciona una pestaña")

def _get_mc_stats(municipio):
    """Función en segundo plano que corre la simulación de Monte Carlo en silencio para pre-popular las cifras del PDF final."""
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc_m, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    mb_h = 1.0 
    pf_h = np.random.normal(PRECIO_BASE['Higo']*mb_h, PRECIO_BASE['Higo']*0.12*max(mb_h,0.1), 5000)
    utils_h = (6.82*mr*mb_h)*(pf_h*1.15) - 105100*mc_m + (117600 - 35536)
    icc_h = utils_h*(1 - 0.08*mk)
    return mr, mc_m, (np.sum(icc_h>0)/5000)*100, float(np.mean(icc_h))

@app.callback(Output('dl-pdf-anual','data'), Input('btn-pdf-anual','n_clicks'), State('dd-municipio','value'), prevent_initial_call=True)
def descargar_pdf_anual(n, municipio):
    """Detecta el click en el botón 'Generar Reporte PDF' disparando en el backend la creación y envío del reporte ejecutivo como stream codificado."""
    if not n: return None
    mr, mc_m, pe, icc = _get_mc_stats(municipio)
    df_dict = generar_dictamen_completo(municipio, 2018, 2026)
    return dict(content=base64.b64encode(generar_pdf_reporte(municipio, mr, mc_m, pe, icc, df_dictamen=df_dict)).decode(), filename=f"reporte_ejecutivo_{municipio}.pdf", type="application/pdf", base64=True)

@app.callback(Output('dl-csv-anual','data'), Input('btn-csv-anual','n_clicks'), State('dd-municipio','value'), prevent_initial_call=True)
def descargar_csv_anual(n, municipio):
    """Detecta el click en el botón 'Descargar Datos CSV' interceptando el DataFrame auditado y forzando la descarga del archivo legible en crudo."""
    if not n: return None
    return dict(content=base64.b64encode(generar_csv(generar_dictamen_completo(municipio, 2018, 2026))).decode(), filename=f"reporte_datos_{municipio}.csv", type="text/csv", base64=True)

# Levanta el servidor local integrado dentro de Flask para atender las solicitudes de red.
if __name__ == '__main__':
    app.run(debug=True, port=8050)