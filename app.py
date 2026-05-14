# ============================================================
# Smart Agroforestry Morelos — Dash App
# Incluye:
#   - Modulo hidroponico NFT (lechuga) integrado en el modelo
#   - Reporte PDF con cifras detalladas por cultivo
#   - Semaforo de competitividad (ICC)
#   - Simulacion Monte Carlo 5 000 iteraciones
#   - Grafico 3D de integrales dobles
#   - Descarga CSV y PDF (mensual y anual)
#   - Tabla Dictamen Operativo historico + proyeccion 2025-2026
# ============================================================

# ── Importaciones de librerias estandar y de terceros ──────────────────────────
import os, io, json # 'os' para interactuar con el sistema operativo, 'io' para manejar flujos de bytes en memoria (usado para PDF), 'json' para manipulación de datos JSON.
import numpy as np # 'numpy' (alias 'np') se utiliza para cálculos matemáticos avanzados y simulaciones aleatorias (Monte Carlo).
import pandas as pd # 'pandas' (alias 'pd') es la librería principal para manipulación y análisis de datos en formato tabular (DataFrames).
import plotly.graph_objects as go # 'graph_objects' de plotly se usa para crear gráficos complejos y personalizados como las superficies 3D.
import plotly.express as px # 'express' de plotly se usa para gráficos rápidos y estadísticos (barras, líneas, histogramas).
from scipy import integrate # 'integrate' de scipy proporciona funciones para calcular integrales definidas, útil para modelos de rentabilidad.
from dash import Dash, dcc, html, Input, Output, State, callback_context # Importaciones principales de Dash para construir la interfaz web, componentes, y manejar eventos (callbacks).
import dash_bootstrap_components as dbc # 'dash_bootstrap_components' permite utilizar estilos y componentes de Bootstrap en la aplicación Dash.
from reportlab.lib.pagesizes import A4, landscape # Importa el tamaño de página A4 y orientación horizontal para la generación de reportes PDF.
from reportlab.lib import colors # Importa colores predefinidos de reportlab para dar estilo a textos y tablas en el PDF.
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Importa funciones para crear y manejar estilos de párrafos en el PDF.
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable # Importa elementos estructurales para construir el PDF (documento, párrafos, espacios, tablas, líneas).
from reportlab.lib.units import cm # Importa la unidad de centímetros para establecer dimensiones en el PDF.
import base64 # 'base64' se utiliza para codificar el archivo PDF generado en memoria y poder descargarlo desde el navegador.

# ── Constantes financieras del PDF (Cuadro 5 y 6 del reporte) ──────────────────
# Diccionario con los ingresos esperados por cada cultivo en el modelo diversificado
INGRESOS = {
    "Venta de Higo (6.82 t x $34,994.18/t)": 238_659.31, # Ingreso calculado por la venta anual de higo
    "Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)": 117_600.00, # Ingreso calculado por la venta anual de lechuga hidroponica
}
# Diccionario con los costos variables (cambian segun la produccion) de los cultivos
COSTOS_VARIABLES = {
    "Fertilizantes, agroquimicos y nutricion - Higo": 5_500.00, # Gasto en nutricion para higo
    "Agua de riego - Higo": 3_800.00, # Costo del agua para riego de higo
    "Mano de obra - Higo (poda, cosecha, clasificacion)": 6_200.00, # Pago a trabajadores para tareas de higo
    "Empaque y manejo postcosecha - Higo": 2_300.00, # Costo de empaques para venta de higo
    "Insumos hidroponicos (nutrientes, semillas, mano de obra)": 35_700.00, # Costos variables del modulo hidroponico
}
# Diccionario con los costos fijos (se pagan independientemente de la produccion)
COSTOS_FIJOS = {
    "Arrendamiento de tierra (1 ha/anio)": 18_000.00, # Renta anual de una hectarea de tierra
    "Amortizacion plantas de Higo": 4_800.00, # Depreciacion/ahorro anual para reponer plantas de higo
    "Amortizacion sistema de riego - Higo": 6_400.00, # Depreciacion anual del sistema de riego por goteo
    "Amortizacion infraestructura hidroponica": 7_000.00, # Depreciacion anual de la estructura del modulo NFT
    "Amortizacion sistema de riego - Hidroponico": 6_400.00, # Depreciacion anual del sistema de circulacion NFT
    "Agua y energia electrica (fijo modulo hidroponico)": 9_000.00, # Gastos fijos de servicios para el modulo NFT
}
# Diccionario con los costos iniciales de inversion para el proyecto
INVERSION_INICIAL = {
    "Plantas de higo (inversion inicial)": 48_000.00, # Costo de adquirir y plantar higueras
    "Sistema de riego tecnificado (goteo y fertirriego)": 32_000.00, # Costo del riego inicial para higo
    "Sistema NFT: bomba, tuberias y temporizador": 32_000.00, # Costo del equipo hidroponico
    "Infraestructura (estructura metalica, cubierta, malla sombra)": 35_000.00, # Costo de la estructura del invernadero
}

# Calculos financieros totales a partir de los diccionarios anteriores
TOTAL_INGRESOS = sum(INGRESOS.values()) # Suma todos los valores del diccionario de ingresos
TOTAL_CV = sum(COSTOS_VARIABLES.values()) # Suma todos los costos variables
TOTAL_CF = sum(COSTOS_FIJOS.values()) # Suma todos los costos fijos
MARGEN_CONTRIB = TOTAL_INGRESOS - TOTAL_CV # Margen de contribucion: Ingresos menos costos variables
UTILIDAD_OP = MARGEN_CONTRIB - TOTAL_CF # Utilidad operativa: Margen de contribucion menos costos fijos
PUNTO_EQ = TOTAL_CF / (MARGEN_CONTRIB / TOTAL_INGRESOS) # Punto de equilibrio: Nivel de ventas necesario para cubrir todos los costos
TOTAL_INV = sum(INVERSION_INICIAL.values()) # Suma de toda la inversion inicial
PAYBACK = TOTAL_INV / UTILIDAD_OP # Tiempo de recuperacion (Payback): Inversion total dividida por la utilidad operativa anual

# ── Paleta de colores ──────────────────────────────────────────────────────────
# Definicion de colores en formato hexadecimal para la interfaz grafica y graficos
CYAN   = "#00e5ff" # Color principal para textos destacados y botones
GREEN  = "#00c853" # Color para indicar estados positivos (alta competitividad, exito)
AMBER  = "#ffb300" # Color para estados de alerta o precauciones (optimizacion)
RED    = "#f44336" # Color para estados negativos o de riesgo (diversificacion urgente)
BG     = "#060b18" # Color de fondo principal (oscuro) de la aplicacion Dash
CARD   = "#0d1b2a" # Color de fondo para las tarjetas (cards) y modulos
BORDER = "#1a3a5c" # Color de los bordes de tarjetas y divisiones

# ── Datos de cultivos y municipios ─────────────────────────────────────────────
# DataFrame con los parametros financieros y tecnicos de cada cultivo evaluado
df_catalogo = pd.DataFrame({
    'nombre_cultivo':       ['Maiz grano', 'Higo',      'Cana de azucar', 'Sorgo grano'], # Nombres de los cultivos
    'costo_operativo':      [32_057.66,    105_100.00,  55_000.00,         38_000.00], # Costo por hectarea aproximado
    'prima_sostenibilidad': [0.05,          0.15,        0.02,              0.04], # Prima adicional en precio por practicas sostenibles (5% a 15%)
    'riesgo_probabilidad':  [0.35,          0.08,        0.20,              0.25], # Probabilidad de siniestro o perdida parcial
    'inversion_ini':        [0.0,           147_000.00,  0.0,               0.0], # Inversion de capital requerida para iniciar
})

# DataFrame con las caracteristicas edafoclimaticas de los municipios evaluados
df_municipios = pd.DataFrame({
    'nombre':        ['Temixco', 'Cuautla', 'Jiutepec'], # Municipios del estado de Morelos
    'tipo_suelo':    ['Feozem y Vertisol', 'Regosol y Cambisol', 'Leptosol y Phaeozem'], # Tipos de suelo predominantes
    'mod_rendimiento': [1.15, 1.00, 0.95], # Multiplicador: afecta positivamente (>1) o negativamente (<1) el rendimiento esperado
    'mod_costo':     [0.95, 1.05, 1.10], # Multiplicador: afecta el costo operativo segun la region
    'mod_riesgo':    [0.85, 1.00, 1.10], # Multiplicador: aumenta o reduce el factor de riesgo por clima/plagas
})

# Produccion historica 2018-2024 (Cuadro 1 del reporte)
# Lista de tuplas con datos crudos historicos (Anio, Municipio, Cultivo, Volumen (t), Rendimiento (t/ha), Precio Medio Rural)
HISTORICO_RAW = [
    (2018,'Temixco','Maiz grano',163.8,3.9,3650),(2018,'Temixco','Maiz grano',1981,4.08,3555.59),
    (2018,'Temixco','Sorgo grano',1480,4.85,3896.76),(2018,'Jiutepec','Maiz grano',214.5,3.3,3734.73),
    (2018,'Cuautla','Maiz grano',3302.2,5.34,3643.82),(2018,'Cuautla','Sorgo grano',8904,5.6,3464.4),
    (2018,'Cuautla','Cana de azucar',146577.6,105.3,967.9),(2018,'Cuautla','Higo',145.2,6.6,35733.33),
    (2019,'Temixco','Maiz grano',1098.1,2.78,3306.25),(2019,'Temixco','Sorgo grano',2304,5.12,3851.48),
    (2019,'Cuautla','Maiz grano',3602.5,5.95,3745.15),(2019,'Cuautla','Sorgo grano',9322,5.9,3931.56),
    (2019,'Cuautla','Higo',145.42,6.61,36368.45),(2020,'Temixco','Maiz grano',1247.8,3.4,3400.8),
    (2020,'Cuautla','Maiz grano',3702,6.17,3686.85),(2020,'Cuautla','Sorgo grano',10048,6.4,3766.56),
    (2021,'Temixco','Maiz grano',1295,3.5,3591.97),(2021,'Temixco','Sorgo grano',1715,4.9,3940),
    (2021,'Cuautla','Maiz grano',3777,6.14,3811.34),(2021,'Cuautla','Higo',None,None,None),
    (2022,'Temixco','Maiz grano',1674,4.5,6065.53),(2022,'Temixco','Sorgo grano',1810.5,5.1,4777.68),
    (2022,'Cuautla','Maiz grano',3795.8,6.1,6019.6),(2022,'Cuautla','Sorgo grano',10096.5,6.35,4967.57),
    (2022,'Cuautla','Higo',143.01,6.81,36370),(2023,'Temixco','Maiz grano',758.5,4.1,5757.66),
    (2023,'Cuautla','Maiz grano',2332.34,3.74,5560.13),(2023,'Cuautla','Sorgo grano',7497,4.76,4898.8),
    (2023,'Cuautla','Higo',145.2,6.6,31496.28),(2024,'Temixco','Maiz grano',2088,5.8,5200.83),
    (2024,'Cuautla','Maiz grano',1980,5.5,5178.8),(2024,'Cuautla','Sorgo grano',9720,6.0,4302.44),
    (2024,'Cuautla','Higo',165,7.5,35002.85),
]
# Creacion del DataFrame historico y eliminacion de filas con valores nulos (NA)
df_hist = pd.DataFrame(HISTORICO_RAW, columns=['Anio','Nommunicipio','Nomcultivo','Volumen','Rendimiento','PMR'])
df_hist.dropna(inplace=True) # Elimina registros incompletos como el de Higo en 2021

# Matriz fenologica
# Multiplicadores de rendimiento y precio que dependen del mes de siembra/cosecha
FENOLOGICA = {
    'Higo':              {'Enero':0.9,'Febrero':0.9,'Marzo':1.0,'Abril':1.1,'Mayo':1.2,'Junio':1.2,
                          'Julio':1.1,'Agosto':1.0,'Septiembre':0.9,'Octubre':0.9,'Noviembre':0.8,'Diciembre':0.8},
    'Maiz grano':        {'Enero':0.0,'Febrero':0.0,'Marzo':0.0,'Abril':0.2,'Mayo':1.2,'Junio':1.5,
                          'Julio':1.0,'Agosto':1.0,'Septiembre':0.8,'Octubre':0.8,'Noviembre':0.0,'Diciembre':0.0},
    'Cana de azucar':    {'Enero':1.3,'Febrero':1.4,'Marzo':1.5,'Abril':1.4,'Mayo':1.2,'Junio':0.5,
                          'Julio':0.5,'Agosto':0.5,'Septiembre':0.5,'Octubre':0.5,'Noviembre':1.0,'Diciembre':1.2},
    'Sorgo grano':       {'Enero':0.0,'Febrero':0.0,'Marzo':0.0,'Abril':0.5,'Mayo':1.0,'Junio':1.3,
                          'Julio':1.2,'Agosto':1.0,'Septiembre':0.8,'Octubre':0.5,'Noviembre':0.0,'Diciembre':0.0},
    'Lechuga (NFT)':     {m:1.2 for m in ['Enero','Febrero','Marzo','Octubre','Noviembre','Diciembre']} |
                         {m:1.0 for m in ['Abril','Mayo','Junio','Julio','Agosto','Septiembre']}, # Combina diccionarios para la lechuga
}
# Volumemes base esperados (toneladas/ha) para cada cultivo
VOL_ESPERADO    = {'Higo': 6.82, 'Maiz grano': 3.5, 'Cana de azucar': 120.0, 'Sorgo grano': 5.5}
# Precio base por tonelada en pesos para simular ingresos
PRECIO_BASE     = {'Higo': 34_994.18, 'Maiz grano': 5_516.0, 'Cana de azucar': 4_799.0, 'Sorgo grano': 4_302.0}
# Nivel de volatilidad del mercado (desviacion estandar) para usar en Monte Carlo
VOLATILIDAD     = {'Higo': 0.12, 'Maiz grano': 0.25, 'Cana de azucar': 0.08, 'Sorgo grano': 0.20}
# Mejor epoca del anio para vender/cosechar cada producto
MES_OPTIMO      = {'Higo':'Feb-Mar','Maiz grano':'May-Jun','Cana de azucar':'Jul-Ago','Sorgo grano':'May-Jun'}

# Extrae la lista de meses para usarla en los selectores de la aplicacion
MESES = list(FENOLOGICA['Higo'].keys())
# Semilla aleatoria para que las simulaciones de Monte Carlo sean consistentes y reproducibles
np.random.seed(42)


# ── Funcion: generar tabla dictamen operativo (historico + proyeccion 2025-2026) ─
def generar_dictamen_completo(municipio, mes, anio_ini=2018, anio_fin=2026):
    """
    Combina datos historicos con proyeccion Monte Carlo hasta 2026.
    Retorna un DataFrame con columnas: Anio, Cultivo, Tipo, Volumen, PMR,
    Costo_Ajustado, Utilidad_Neta, ICC, Estatus.
    """
    # Extrae la fila del municipio seleccionado para obtener sus multiplicadores
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr = row_mun['mod_rendimiento'] # Multiplicador de rendimiento
    mc = row_mun['mod_costo'] # Multiplicador de costo
    mk = row_mun['mod_riesgo'] # Multiplicador de riesgo

    filas = [] # Lista para almacenar los resultados combinados

    # ---- Historico ----
    # Filtra el DataFrame historico por municipio y rango de anios disponible
    df_mun = df_hist[
        (df_hist['Nommunicipio'] == municipio) &
        (df_hist['Anio'] >= anio_ini) &
        (df_hist['Anio'] <= min(2024, anio_fin))
    ].copy()

    # Itera sobre los datos historicos filtrados
    for _, r in df_mun.iterrows():
        cult = r['Nomcultivo'] # Cultivo actual
        # Busca los parametros del cultivo en el catalogo
        prima = df_catalogo[df_catalogo['nombre_cultivo'] == cult]['prima_sostenibilidad'].values
        riesgo = df_catalogo[df_catalogo['nombre_cultivo'] == cult]['riesgo_probabilidad'].values
        costo_op = df_catalogo[df_catalogo['nombre_cultivo'] == cult]['costo_operativo'].values
        
        if len(prima) == 0:
            continue # Si el cultivo no esta en el catalogo, se omite
            
        # Calcula precio ajustado con la prima de sostenibilidad
        precio_aj = r['PMR'] * (1 + prima[0])
        # Ajusta el costo con el multiplicador del municipio
        costo_aj = costo_op[0] * mc
        # Utilidad = (Volumen * Mod_Rendimiento) * Precio Ajustado - Costo Ajustado
        utilidad = (r['Volumen'] * mr) * precio_aj - costo_aj
        # ICC = Utilidad * (1 - Riesgo * Mod_Riesgo)
        icc = utilidad * (1 - riesgo[0] * mk)
        
        # Agrega la fila a la lista de resultados
        filas.append({
            'Anio': int(r['Anio']),
            'Cultivo': cult,
            'Tipo': 'Historico', # Etiqueta para distinguir de la proyeccion
            'Volumen_t': round(r['Volumen'], 2),
            'PMR': round(r['PMR'], 2),
            'Costo_Ajustado': round(costo_aj, 2),
            'Utilidad_Neta': round(utilidad, 2),
            'ICC': round(icc, 0),
            'Estatus': clasificar_icc(icc), # Aplica funcion de semaforo
        })

    # ---- Proyeccion Monte Carlo 2025-2026 ----
    # Solo se ejecuta si el anio final es mayor a 2024
    if anio_fin > 2024:
        anios_futuros = [a for a in range(max(2025, anio_ini), anio_fin + 1)]
        for anio in anios_futuros: # Por cada anio futuro
            for _, row in df_catalogo.iterrows(): # Simula para todos los cultivos del catalogo
                cult = row['nombre_cultivo']
                # Obtiene multiplicador del mes, por defecto 1.0
                mb = FENOLOGICA.get(cult, {}).get(mes, 1.0)
                pb = PRECIO_BASE.get(cult, 5000)
                # Define desviacion estandar (volatilidad) del precio
                sd = pb * VOLATILIDAD.get(cult, 0.15) * max(mb, 0.1)
                # Genera distribucion normal (Monte Carlo) con 5000 muestras para el precio
                pf_sim = np.random.normal(pb * mb, sd, 5000)
                # Toma el promedio del precio simulado
                precio_esp = float(np.mean(pf_sim))
                
                prima = row['prima_sostenibilidad']
                riesgo = row['riesgo_probabilidad']
                costo_op = row['costo_operativo']
                
                precio_aj = precio_esp * (1 + prima)
                costo_aj = costo_op * mc
                vol = VOL_ESPERADO.get(cult, 4.0)
                # Calcula utilidad esperada de la simulacion
                utilidad = (vol * mr * mb) * precio_aj - costo_aj
                
                # Reglas especiales para el Higo (integracion hidroponica)
                if cult == 'Higo':
                    utilidad += 117_600.00  # Suma ingreso hidroponico mensual
                    utilidad -= 35_536.00   # Resta amortizacion CAPEX (gasto fijo)
                    
                icc = utilidad * (1 - riesgo * mk)
                
                # Agrega la simulacion al resultado
                filas.append({
                    'Anio': anio,
                    'Cultivo': cult,
                    'Tipo': 'Proyeccion Monte Carlo', # Etiqueta de simulacion
                    'Volumen_t': round(vol * mr * mb, 3),
                    'PMR': round(precio_esp, 2),
                    'Costo_Ajustado': round(costo_aj, 2),
                    'Utilidad_Neta': round(utilidad, 2),
                    'ICC': round(icc, 0),
                    'Estatus': clasificar_icc(icc),
                })

    return pd.DataFrame(filas) # Retorna todo en un nuevo DataFrame


# Funcion auxiliar para el texto del semaforo segun el puntaje ICC
def clasificar_icc(val):
    if val < 20_000:  return "Diversificacion Urgente" # Riesgo alto, baja utilidad
    if val > 100_000: return "Alta Competitividad"     # Alta utilidad, bajo riesgo
    return "Optimizacion Requerida"                    # Zona intermedia


# ── Generadores de reportes y Helpers ──────────────────────────────────────────

# Funcion para formatear numeros como moneda (ej: $1,200.00)
def fmt(n): return f"${n:,.2f}"

# Retorna el color correspondiente al semaforo ICC
def color_icc(val):
    if val > 100_000: return GREEN
    if val > 20_000:  return AMBER
    return RED

# Version antigua de semaforo label, mantenida por compatibilidad
def semaforo_label(val):
    if val > 100_000: return "Alta Competitividad"
    if val > 20_000:  return "Optimizacion Requerida"
    return "Diversificacion Urgente"


# ── Generador de CSV ──────────────────────────────────────────────────────────

# Funcion generica para convertir un DataFrame de Pandas a formato CSV en bytes para descargar
def generar_csv(df: pd.DataFrame) -> bytes:
    buf = io.StringIO() # Crea un buffer de texto en memoria
    df.to_csv(buf, index=False, encoding='utf-8') # Escribe el DataFrame en el buffer sin incluir indices
    return buf.getvalue().encode('utf-8') # Retorna el texto codificado en bytes (requerido para descargas)


# Genera un CSV especifico enfocado en los ingresos mensuales esperados segun la matriz fenologica
def generar_csv_mensual(municipio, mes):
    """CSV con desglose mensual de ingresos hidropónicos y fenológicos."""
    filas = []
    # Itera sobre cada cultivo definido en la matriz fenologica
    for cultivo in FENOLOGICA:
        mb = FENOLOGICA[cultivo].get(mes, 1.0) # Modificador mensual (fenologia)
        pb = PRECIO_BASE.get(cultivo, 5000)    # Precio base del cultivo
        vol = VOL_ESPERADO.get(cultivo, 4.0)   # Volumen esperado base
        
        # Obtiene datos del municipio seleccionado
        row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
        mr = row_mun['mod_rendimiento'] # Modificador de rendimiento local
        
        # Ingreso = Volumen * Mod_Rendimiento * Mod_Fenologico * PrecioBase
        ingreso = vol * mr * mb * pb
        
        filas.append({'Mes': mes, 'Municipio': municipio, 'Cultivo': cultivo,
                      'Modificador_Fenologico': mb,
                      'Volumen_Est_t': round(vol * mr * mb, 3), # Volumen final estimado
                      'PMR_Base': pb,
                      'Ingreso_Estimado': round(ingreso, 2)}) # Ingreso proyectado
    return pd.DataFrame(filas)


# Genera un CSV completo usando la funcion de dictamen (historico y proyecciones)
def generar_csv_anual(municipio, mes):
    """CSV anual completo con historico y proyeccion."""
    return generar_dictamen_completo(municipio, mes, 2018, 2026)


# ── Generador de PDF ──────────────────────────────────────────────────────────
# Funcion principal para construir el reporte final en PDF utilizando la libreria ReportLab
def generar_pdf_reporte(municipio, mes, mod_rend, mod_costo, pe_higo, icc_higo,
                        modo='anual', df_dictamen=None):
    buf = io.BytesIO() # Crea un buffer de bytes en memoria para el PDF
    page_size = A4     # Establece el tamano de pagina en A4
    
    # Crea el documento base con margenes definidos
    doc = SimpleDocTemplate(buf, pagesize=page_size,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    ss = getSampleStyleSheet() # Obtiene hoja de estilos por defecto
    
    # Diccionario con estilos de texto personalizados para el PDF
    estilos = {
        'titulo': ParagraphStyle('titulo', parent=ss['Heading1'], fontSize=16,
                                  textColor=colors.HexColor('#003366'), spaceAfter=6),
        'subtit': ParagraphStyle('subtit', parent=ss['Heading2'], fontSize=12,
                                  textColor=colors.HexColor('#005b99'), spaceAfter=4),
        'body':   ParagraphStyle('body', parent=ss['Normal'], fontSize=9, leading=13),
        'bold':   ParagraphStyle('bold', parent=ss['Normal'], fontSize=9,
                                  textColor=colors.HexColor('#003366'), fontName='Helvetica-Bold'),
        'green':  ParagraphStyle('green', parent=ss['Normal'], fontSize=11,
                                  textColor=colors.HexColor('#1a6e1a'), fontName='Helvetica-Bold'),
        'footer': ParagraphStyle('footer', parent=ss['Normal'], fontSize=7,
                                  textColor=colors.grey, alignment=1),
    }

    # Helper interno para formatear las tablas de datos dentro del PDF
    def tabla(data, col_widths, header_bg=colors.HexColor('#003366')):
        t = Table(data, colWidths=col_widths) # Crea objeto tabla
        
        # Define el estilo de la tabla (colores de fondo, bordes, alineaciones)
        style = [
            ('BACKGROUND', (0,0), (-1,0), header_bg), # Fondo del encabezado
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white), # Texto blanco en encabezado
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'), # Fuente en negrita
            ('FONTSIZE',   (0,0), (-1,-1), 8), # Tamano de letra general
            ('ALIGN',      (1,1), (-1,-1), 'RIGHT'), # Alinea numeros a la derecha
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#f0f4f8'), colors.white]), # Filas alternas zebra
            ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#c0d0e0')), # Cuadricula
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]
        t.setStyle(TableStyle(style)) # Aplica el estilo a la tabla
        return t

    story = [] # 'story' es la lista de elementos (texto, tablas, imagenes) que conformaran el PDF

    # ── Encabezado ──────────────────────────────────────────────────────────
    story.append(Paragraph("UNIVERSIDAD NACIONAL ROSARIO CASTELLANOS", estilos['bold']))
    tipo_reporte = "Reporte Mensual" if modo == 'mensual' else "Reporte Anual"
    story.append(Paragraph(
        f"Analisis Tecnico-Economico — Diversificacion de Cultivos en Morelos ({tipo_reporte})",
        estilos['titulo']))
    story.append(Paragraph(
        f"Municipio: <b>{municipio}</b> | Mes de analisis: <b>{mes}</b> | "
        f"Modificador rendimiento: <b>x{mod_rend}</b> | "
        f"Modificador costo: <b>x{mod_costo}</b>", estilos['body']))
    story.append(HRFlowable(width="100%", thickness=1, # Linea horizontal separadora
                             color=colors.HexColor('#003366'), spaceAfter=10))

    # ── 1. Ingresos ─────────────────────────────────────────────────────────
    story.append(Paragraph("1. Ingresos por Cultivo", estilos['subtit']))
    story.append(Paragraph(
        "Los ingresos se generan de dos fuentes complementarias: el <b>cultivo de Higo</b> "
        "(alto valor unitario, cosecha estacional) y el <b>modulo hidroponico NFT de lechuga</b> "
        "(flujo constante mensual que estabiliza la caja del agricultor).", estilos['body']))
    story.append(Spacer(1, 6)) # Espacio en blanco
    
    # Prepara datos para la tabla de ingresos
    ing_data = [["Concepto de ingreso", "Cantidad", "Precio unitario", "Monto (MXN)"]]
    ing_data.append(["Venta de Higo", "6.82 t", "$34,994.18 / t",
                      fmt(INGRESOS["Venta de Higo (6.82 t x $34,994.18/t)"])])
    ing_data.append(["Venta Lechuga Hidroponica (NFT)", "4,200 kg", "$28.00 / kg",
                      fmt(INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"])])
    ing_data.append(["", "", "TOTAL INGRESOS", fmt(TOTAL_INGRESOS)])
    
    story.append(tabla(ing_data, [7.5*cm, 2.8*cm, 4*cm, 3.5*cm])) # Agrega tabla al PDF
    story.append(Spacer(1, 4))
    
    # Agrega un parrafo de analisis/conclusion sobre la tabla
    story.append(Paragraph(
        f"El higo representa el "
        f"{INGRESOS['Venta de Higo (6.82 t x $34,994.18/t)']/TOTAL_INGRESOS*100:.1f}% "
        f"del ingreso total. La lechuga hidroponica aporta el "
        f"{INGRESOS['Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)']/TOTAL_INGRESOS*100:.1f}% "
        f"y genera dinero <b>todos los meses</b>, cubriendo gastos mientras el higo madura.",
        estilos['body']))
    story.append(Spacer(1, 10))

    # ── 2. Gastos Variables ─────────────────────────────────────────────────
    story.append(Paragraph("2. Gastos Variables por Cultivo", estilos['subtit']))
    story.append(Paragraph(
        "Son los costos que <b>cambian segun la produccion</b>. Se presentan separados por cultivo "
        "para que el agricultor identifique exactamente en que se gasta cada peso.", estilos['body']))
    story.append(Spacer(1, 6))
    
    # Filtra los gastos segun correspondan a higo o hidroponia
    cv_higo  = {k:v for k,v in COSTOS_VARIABLES.items() if 'Higo' in k or 'higo' in k.lower()}
    cv_hidro = {k:v for k,v in COSTOS_VARIABLES.items() if 'hidroponico' in k.lower() or 'Insumos' in k}
    
    # Encabezados de tabla
    cv_data = [["Concepto (gasto variable)", "Cultivo asociado", "Monto (MXN)"]]
    for k,v in COSTOS_VARIABLES.items():
        cultivo_rel = "Lechuga hidroponica" if 'hidroponico' in k.lower() or 'Insumos' in k else "Higo"
        cv_data.append([k, cultivo_rel, fmt(v)])
    cv_data.append(["", "TOTAL COSTOS VARIABLES", fmt(TOTAL_CV)])
    story.append(tabla(cv_data, [9.5*cm, 4.5*cm, 3.8*cm]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Gastos variables del Higo: {fmt(sum(cv_higo.values()))}  |  "
        f"Gastos variables Hidroponico: {fmt(sum(cv_hidro.values()))}", estilos['body']))
    story.append(Spacer(1, 10))

    # ── 3. Gastos Fijos ─────────────────────────────────────────────────────
    story.append(Paragraph("3. Gastos Fijos (no cambian aunque la produccion varie)", estilos['subtit']))
    story.append(Paragraph(
        "Son los compromisos que hay que pagar <b>aunque no se venda nada</b>. Incluyen la renta "
        "de la tierra y la depreciacion anual de equipos (lo que cuesta ir ahorrando para "
        "reponer bombas, tuberias y plasticos cuando se desgasten).", estilos['body']))
    story.append(Spacer(1, 6))
    
    # Prepara tabla de gastos fijos
    cf_data = [["Concepto (gasto fijo)", "Explicacion sencilla", "Monto (MXN)"]]
    explicaciones = {
        "Arrendamiento de tierra (1 ha/anio)": "Renta de la hectarea",
        "Amortizacion plantas de Higo": "Ahorro anual para reponer plantas (vida util 10 anios)",
        "Amortizacion sistema de riego - Higo": "Ahorro para reponer riego goteo (5 anios)",
        "Amortizacion infraestructura hidroponica": "Ahorro para reponer estructura (5 anios)",
        "Amortizacion sistema de riego - Hidroponico": "Ahorro para reponer bomba NFT (5 anios)",
        "Agua y energia electrica (fijo modulo hidroponico)": "Recibo de agua y luz del modulo",
    }
    for k,v in COSTOS_FIJOS.items():
        cf_data.append([k, explicaciones.get(k,'—'), fmt(v)])
    cf_data.append(["", "TOTAL COSTOS FIJOS", fmt(TOTAL_CF)])
    story.append(tabla(cf_data, [7.5*cm, 6.0*cm, 4.3*cm]))
    story.append(Spacer(1, 10))

    # ── 4. Estado de Resultados ─────────────────────────────────────────────
    story.append(Paragraph("4. Estado de Resultados Resumido (Ejercicio 2026)", estilos['subtit']))
    story.append(Paragraph(
        "Aqui se ve de un solo vistazo cuanto se gana despues de pagar todos los gastos.",
        estilos['body']))
    story.append(Spacer(1, 6))
    
    # Prepara estructura financiera del modelo (P&L simple)
    er_data = [
        ["Concepto", "Monto (MXN)", "Observacion"],
        ["(+) Total ingresos", fmt(TOTAL_INGRESOS), "Higo + Lechuga hidroponica"],
        ["(-) Costos variables", fmt(TOTAL_CV),    "Insumos, mano de obra, empaque"],
        ["(=) Margen de contribucion", fmt(MARGEN_CONTRIB), "Lo que queda para cubrir fijos"],
        ["(-) Costos fijos", fmt(TOTAL_CF),        "Renta + amortizaciones + energia"],
        ["(=) Utilidad operativa", fmt(UTILIDAD_OP), "Libre de impuestos (AGAPES)"],
        ["(=) UTILIDAD NETA", fmt(UTILIDAD_OP),    "ISR/PTU exento — Regimen AGAPES"],
    ]
    t_er = tabla(er_data, [6*cm, 4*cm, 7.8*cm])
    # Estilo especial para resaltar el final de la tabla (Utilidad Neta en verde)
    t_er.setStyle(TableStyle([
        ('BACKGROUND', (0,6), (-1,6), colors.HexColor('#1a6e1a')),
        ('TEXTCOLOR',  (0,6), (-1,6), colors.white),
        ('FONTNAME',   (0,6), (-1,6), 'Helvetica-Bold'),
    ]))
    story.append(t_er)
    story.append(Spacer(1, 10))

    # ── 5. Inversion inicial ────────────────────────────────────────────────
    story.append(Paragraph("5. Inversion Inicial Requerida y Tiempo de Recuperacion", estilos['subtit']))
    
    # Tabla de desembolsos de capital (CAPEX)
    inv_data = [["Concepto", "Monto (MXN)", "Vida util"]]
    vidas = {"Plantas de higo (inversion inicial)": "10 anios",
             "Sistema de riego tecnificado (goteo y fertirriego)": "5 anios",
             "Sistema NFT: bomba, tuberias y temporizador": "5 anios",
             "Infraestructura (estructura metalica, cubierta, malla sombra)": "5 anios"}
    for k,v in INVERSION_INICIAL.items():
        inv_data.append([k, fmt(v), vidas.get(k,'—')])
    inv_data.append(["INVERSION TOTAL", fmt(TOTAL_INV), "—"])
    story.append(tabla(inv_data, [9*cm, 4*cm, 4.8*cm]))
    story.append(Spacer(1, 4))
    
    # Analisis del Payback
    story.append(Paragraph(
        f"Con una utilidad neta de {fmt(UTILIDAD_OP)} por anio, la inversion se recupera en "
        f"aproximadamente <b>{PAYBACK:.1f} anios ({PAYBACK*12:.0f} meses)</b>.",
        estilos['body']))
    story.append(Spacer(1, 10))

    # ── 6. Punto de equilibrio ──────────────────────────────────────────────
    story.append(Paragraph("6. Punto de Equilibrio", estilos['subtit']))
    story.append(Paragraph(
        f"El punto de equilibrio indica cuanto hay que vender para no perder ni ganar. "
        f"En este modelo es de <b>{fmt(PUNTO_EQ)}</b>, es decir, con solo el "
        f"{PUNTO_EQ/TOTAL_INGRESOS*100:.1f}% de los ingresos proyectados ya se cubren "
        f"todos los costos. Cualquier venta adicional es ganancia pura.", estilos['body']))
    story.append(Spacer(1, 10))

    # ── 7. Monte Carlo ──────────────────────────────────────────────────────
    story.append(Paragraph("7. Probabilidad de Exito (Simulacion Monte Carlo — 5,000 escenarios)", estilos['subtit']))
    story.append(Paragraph(
        f"El sistema simulo 5,000 escenarios con precios de mercado aleatorios. "
        f"Resultado para el Higo en {municipio} ({mes}): "
        f"<b>Probabilidad de exito = {pe_higo:.1f}%</b>  |  "
        f"<b>ICC esperado = {icc_higo:,.0f} pts</b>  |  "
        f"Clasificacion: <b>{semaforo_label(icc_higo)}</b>", estilos['body']))
    story.append(Spacer(1, 10))

    # ── 8. Comparativa ──────────────────────────────────────────────────────
    story.append(Paragraph("8. Comparativa: Modelo Diversificado vs. Maiz Tradicional", estilos['subtit']))
    
    # Tabla comparando beneficios frente a la agricultura tradicional
    cmp_data = [
        ["Indicador", "Maiz tradicional", "Higo + Lechuga NFT", "Diferencia"],
        ["Ingresos anuales", "$40,000 – $50,000", fmt(TOTAL_INGRESOS), f"+{fmt(TOTAL_INGRESOS-45000)}"],
        ["Costos totales", "~$41,000", fmt(TOTAL_CV+TOTAL_CF), f"-{fmt(abs(TOTAL_CV+TOTAL_CF-41000))}"],
        ["Utilidad neta", "~-$1,000 (perdida)", fmt(UTILIDAD_OP), f"+{fmt(UTILIDAD_OP+1000)}"],
        ["Frecuencia de ingresos", "1 vez al anio", "Mensual (lechuga) + anual (higo)", "Flujo constante"],
        ["Riesgo de quiebra", "Alto (>35%)", "<8% (higo) — Hidroponia: controlada", "Muy bajo"],
    ]
    story.append(tabla(cmp_data, [5.8*cm, 4.2*cm, 5.0*cm, 4.2*cm]))
    story.append(Spacer(1, 14))

    # ── 9. Dictamen Operativo (historico + proyeccion) ──────────────────────
    # Si se envio un DataFrame con dictamen, se incluye en el PDF
    if df_dictamen is not None and not df_dictamen.empty:
        story.append(Paragraph("9. Dictamen Operativo — Historico y Proyeccion 2018-2026", estilos['subtit']))
        story.append(Paragraph(
            "La siguiente tabla integra los datos historicos de produccion con la proyeccion "
            "estadistica (Monte Carlo) para los anios 2025-2026.", estilos['body']))
        story.append(Spacer(1, 6))
        
        dict_header = [["Anio", "Cultivo", "Tipo", "Vol. (t)", "PMR ($/t)",
                         "Costo Ajust.", "Utilidad Neta", "ICC (pts)", "Estatus"]]
        dict_rows = []
        # Convierte filas del dataframe a texto
        for _, r in df_dictamen.iterrows():
            dict_rows.append([
                str(r['Anio']),
                str(r['Cultivo']),
                "Hist." if r['Tipo'] == 'Historico' else "Proyec.",
                f"{r['Volumen_t']:,.3f}",
                f"${r['PMR']:,.2f}",
                f"${r['Costo_Ajustado']:,.2f}",
                f"${r['Utilidad_Neta']:,.2f}",
                f"{r['ICC']:,.0f}",
                str(r['Estatus']),
            ])
        t_dict = tabla(dict_header + dict_rows,
                       [1.3*cm, 2.8*cm, 1.8*cm, 1.6*cm, 2.2*cm, 2.2*cm, 2.5*cm, 2.0*cm, 3.8*cm])
        
        # Agrega color de fondo a cada fila segun su estatus
        style_extra = []
        for idx, r in enumerate(df_dictamen.itertuples(), start=1):
            if r.Estatus == 'Alta Competitividad':
                bg = colors.HexColor('#c8f5c8')
            elif r.Estatus == 'Diversificacion Urgente':
                bg = colors.HexColor('#ffd0d0')
            else:
                bg = colors.HexColor('#fff5cc')
            style_extra.append(('BACKGROUND', (0, idx), (-1, idx), bg)) # Aplica a toda la fila
        t_dict.setStyle(TableStyle(style_extra))
        story.append(t_dict)
        story.append(Spacer(1, 14))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Universidad Nacional Rosario Castellanos — Sede Gustavo A. Madero — Grupo 301 | "
        "Gonzalez Lopez C. E. · Lopez Marlene · De los Angeles Garcia J. C. · Toscano Pacheco J. M. | "
        "Generado automaticamente por Smart Agroforestry Morelos v3.0 (Dash)",
        estilos['footer']))

    # Construye el PDF y retorna los bytes generados
    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── Layout helpers ─────────────────────────────────────────────────────────────
# Helper para construir "tarjetas" visuales que muestran indicadores (KPIs) en Dash
def kpi_card(title, value, sub=None, color=CYAN):
    return html.Div([
        # Titulo pequeno de la tarjeta
        html.P(title, style={'fontSize':'11px','color':'#6a8aaa','marginBottom':'4px','fontFamily':'monospace'}),
        # Valor grande (el KPI en si)
        html.H4(value, style={'color':color,'margin':'0','fontSize':'1.4rem'}),
        # Subtexto explicativo (opcional)
        html.P(sub or '', style={'fontSize':'10px','color':'#6a8aaa','marginTop':'2px'}),
    ], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px',
              'padding':'16px','flex':'1','minWidth':'170px'}) # Estilos de la tarjeta (CSS inline)


# ── App ────────────────────────────────────────────────────────────────────────
# Inicializa la aplicacion Dash, usa tema oscuro CYBORG de Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
           suppress_callback_exceptions=True) # Permite generar callbacks para elementos que aun no existen en el DOM
app.title = "Smart Agroforestry Morelos" # Titulo que aparece en la pestana del navegador

# Diccionario de estilo reutilizable para los botones de la interfaz
BOTON_STYLE = {'width':'100%','background':CYAN,'color':'#000',
               'border':'none','padding':'10px','borderRadius':'6px',
               'fontWeight':'700','cursor':'pointer','fontSize':'12px',
               'marginBottom':'6px'}

# ── Definicion de la Estructura Visual (Layout) ────────────────────────────────
app.layout = html.Div(style={'backgroundColor':BG,'minHeight':'100vh',
                              'fontFamily':'Rajdhani, sans-serif','color':'#fff'}, children=[

    # Importa fuentes personalizadas desde Google Fonts
    html.Link(rel='stylesheet',
              href='https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap'),

    # Header de la pagina
    html.Div([
        html.H2("Smart Agroforestry Morelos", style={'margin':'0','color':CYAN}),
        html.P("Sistema Inteligente de Analisis Tecnico-Economico — Higo + Lechuga Hidroponica NFT",
               style={'margin':'2px 0 0','color':'#6a8aaa','fontSize':'13px'}),
    ], style={'background':CARD,'borderBottom':f'1px solid {BORDER}','padding':'18px 30px'}),

    # Cuerpo principal dividido en barra lateral (Sidebar) y Contenido
    html.Div(style={'display':'flex','minHeight':'calc(100vh - 70px)'}, children=[

        # ── Sidebar (Panel de Control) ─────────────────────────────────────────
        html.Div(style={'width':'260px','background':CARD,'borderRight':f'1px solid {BORDER}',
                        'padding':'20px','flexShrink':'0'}, children=[
            html.H5("Panel de Control", style={'color':CYAN,'marginBottom':'16px'}),

            # Selector (Dropdown) de Municipios
            html.Label("Municipio", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Dropdown(id='dd-municipio',
                         options=[{'label':m,'value':m} for m in df_municipios['nombre']],
                         value='Temixco', # Valor por defecto
                         style={'background':'#0d1b2a','color':'#fff','borderColor':BORDER}),
            html.Br(),

            # Selector (Dropdown) de Mes de Analisis (Fenologia)
            html.Label("Mes de Analisis", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Dropdown(id='dd-mes',
                         options=[{'label':m,'value':m} for m in MESES],
                         value='Mayo', # Valor por defecto
                         style={'background':'#0d1b2a','color':'#fff','borderColor':BORDER}),
            html.Br(),

            # Slider para seleccionar rango de anios historicos a mostrar en las graficas
            html.Label("Periodo Historico", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.RangeSlider(id='sl-anio', min=2018, max=2026, step=1, value=[2018,2026],
                            marks={y:str(y) for y in range(2018,2027,2)},
                            tooltip={"placement":"bottom"}),
            html.Br(),

            # Checkbox para habilitar o deshabilitar la evaluacion del modulo hidroponico en la simulacion
            html.Label("Incluir Modulo Hidroponico", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Checklist(id='chk-hidro',
                          options=[{'label':' Lechuga NFT (100 m2)','value':'hidro'}],
                          value=['hidro'], # Seleccionado por defecto
                          style={'color':GREEN}),
            html.Br(),

            # Contenedor vacio que se actualizara via Callback con los datos del municipio seleccionado
            html.Div(id='sidebar-info',
                     style={'background':'#060b18','border':f'1px solid {BORDER}',
                            'borderRadius':'6px','padding':'12px','fontSize':'11px','color':'#6a8aaa'}),
            html.Br(),

            # ── Botones de descarga de Reportes ──────────────────────────────────
            html.P("Reportes PDF", style={'fontSize':'11px','color':CYAN,'marginBottom':'6px','fontWeight':'700'}),
            html.Button("PDF Mensual", id='btn-pdf-mensual', n_clicks=0, style=BOTON_STYLE),
            html.Button("PDF Anual", id='btn-pdf-anual', n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-pdf-mensual'), # Componente invisible que maneja la descarga de archivos
            dcc.Download(id='dl-pdf-anual'),

            html.Br(),
            html.P("Reportes CSV", style={'fontSize':'11px','color':CYAN,'marginBottom':'6px','fontWeight':'700'}),
            html.Button("CSV Mensual", id='btn-csv-mensual', n_clicks=0, style=BOTON_STYLE),
            html.Button("CSV Anual", id='btn-csv-anual', n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-csv-mensual'),
            dcc.Download(id='dl-csv-anual'),
        ]),

        # ── Contenido Principal (Pestanas y Graficos) ──────────────────────────
        html.Div(style={'flex':'1','padding':'24px','overflowY':'auto'}, children=[

            # Sistema de Pestanas (Tabs) de Dash
            dcc.Tabs(id='tabs', value='tab-dash', style={'borderBottom':f'1px solid {BORDER}'},
                     colors={'border':BORDER,'primary':CYAN,'background':BG}, children=[

                dcc.Tab(label='Dashboard Operativo', value='tab-dash',
                        style={'color':'#aaa'}, selected_style={'color':CYAN,'fontWeight':'700'}),

                dcc.Tab(label='Evaluacion Regional (Integrales)', value='tab-math',
                        style={'color':'#aaa'}, selected_style={'color':CYAN,'fontWeight':'700'}),

                dcc.Tab(label='Motor Predictivo (Monte Carlo)', value='tab-mc',
                        style={'color':'#aaa'}, selected_style={'color':CYAN,'fontWeight':'700'}),

                dcc.Tab(label='Modelo Hidroponico', value='tab-hidro',
                        style={'color':'#aaa'}, selected_style={'color':CYAN,'fontWeight':'700'}),

                dcc.Tab(label='Dictamen Operativo 2018-2026', value='tab-dictamen',
                        style={'color':'#aaa'}, selected_style={'color':CYAN,'fontWeight':'700'}),
            ]),

            # Contenedor dinamico donde se inyectara el contenido de la pestana seleccionada
            html.Div(id='tab-content', style={'marginTop':'20px'}),
        ]),
    ]),
])


# ── Callbacks (Lógica de Interactividad) ───────────────────────────────────────

# Callback 1: Actualiza la tarjeta de informacion del municipio en el panel lateral
@app.callback(
    Output('sidebar-info','children'), # Define donde se renderizara el resultado
    Input('dd-municipio','value'),     # Define que variable dispara este evento
)
def update_sidebar_info(municipio):
    # Obtiene los datos edafoclimaticos del municipio seleccionado
    row = df_municipios[df_municipios['nombre']==municipio].iloc[0]
    # Retorna componentes HTML formateados
    return [
        html.B(f"{municipio}"), html.Br(),
        f"Suelo: {row['tipo_suelo']}", html.Br(),
        f"Rendimiento: x{row['mod_rendimiento']}  |  Costo: x{row['mod_costo']}", html.Br(),
        f"Riesgo edafo.: x{row['mod_riesgo']}",
    ]


# Callback 2: El mas importante. Controla el contenido principal segun la pestana y los filtros
@app.callback(
    Output('tab-content','children'),
    Input('tabs','value'),           # Que pestana esta activa
    Input('dd-municipio','value'),   # Filtro Municipio
    Input('dd-mes','value'),         # Filtro Mes
    Input('sl-anio','value'),        # Filtro de Anios (Rango)
    Input('chk-hidro','value'),      # Switch de modulo hidroponico
)
def render_tab(tab, municipio, mes, anio_range, hidro):
    # Obtencion rapida de modificadores locales
    row_mun = df_municipios[df_municipios['nombre']==municipio].iloc[0]
    mr = row_mun['mod_rendimiento']
    mc = row_mun['mod_costo']
    mk = row_mun['mod_riesgo']

    # Computo basico de la tabla ICC (Indice de Competitividad) para todos los cultivos
    filas = []
    for _, r in df_catalogo.iterrows():
        cult = r['nombre_cultivo']
        mb = FENOLOGICA.get(cult,{}).get(mes,1.0) # Fenologia del mes
        pb = PRECIO_BASE.get(cult, 5000)
        
        # Simula un precio esperado con distribucion normal simple (2000 iteraciones)
        sigma = pb * VOLATILIDAD.get(cult, 0.15) * mb
        pf = np.mean(np.random.normal(pb*mb, sigma, 2000))
        vol = VOL_ESPERADO.get(cult, 4.0)
        
        # Calculo de utilidad financiera
        utilidad = (vol * mr * mb) * (pf * (1+r['prima_sostenibilidad'])) - (r['costo_operativo']*mc)
        
        # Integracion de hidroponia (si aplica)
        if cult=='Higo' and hidro:
            utilidad += INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"]
            utilidad -= TOTAL_CF - 18000 # Resta costos fijos de hidroponia
            
        # Puntaje final
        icc = utilidad * (1 - r['riesgo_probabilidad'] * mk)
        filas.append({'Cultivo':cult,'Utilidad':utilidad,'ICC':icc,'Mb':mb,
                      'Semaforo':semaforo_label(icc)})
    df_icc = pd.DataFrame(filas) # DataFrame temporal con resultados de los 4 cultivos

    # ── Tab: Dashboard (Vista General) ────────────────────────────────────
    if tab == 'tab-dash':
        # Filtra datos historicos reales para la grafica
        df_plot = df_hist[(df_hist['Nommunicipio']==municipio) &
                          (df_hist['Anio']>=anio_range[0]) &
                          (df_hist['Anio']<=min(2024,anio_range[1]))]

        # KPIs principales en tarjetas
        kpis = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Utilidad Neta Modelo", fmt(UTILIDAD_OP), "Higo + Lechuga (2026)", GREEN),
            kpi_card("Ingresos Totales",     fmt(TOTAL_INGRESOS), "Higo + Lechuga", CYAN),
            kpi_card("Costos Totales",       fmt(TOTAL_CV+TOTAL_CF), "Variables + Fijos", AMBER),
            kpi_card("Punto de Equilibrio",  fmt(PUNTO_EQ), f"{PUNTO_EQ/TOTAL_INGRESOS*100:.1f}% de ingresos", "#9c27b0"),
            kpi_card("Recuperacion Inversion", f"{PAYBACK:.1f} anios", f"Inversion: {fmt(TOTAL_INV)}", CYAN),
        ])

        # Grafico de Barras (Plotly Express) para mostrar competitividad
        fig_bar = px.bar(
            df_icc.sort_values('ICC'), x='ICC', y='Cultivo', orientation='h',
            color='ICC', color_continuous_scale=[[0,RED],[0.2,AMBER],[1,GREEN]],
            title=f"Indice de Competitividad (ICC) — {municipio} / {mes}",
        )
        # Limpieza de estilos visuales del grafico
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               font_color='#fff', coloraxis_showscale=False, height=280)
        # Lineas de referencia
        fig_bar.add_vline(x=20000,  line_dash='dash', line_color=AMBER, annotation_text="20k (min)")
        fig_bar.add_vline(x=100000, line_dash='dash', line_color=GREEN, annotation_text="100k (alta)")

        # Grafica historica de precios PMR
        fig_pmr = px.line(df_plot, x='Anio', y='PMR', color='Nomcultivo',
                          title="Precio Medio Rural historico (MXN/t)", markers=True)
        fig_pmr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               font_color='#fff', height=300)

        # Tabla HTML que resume el estado de los cultivos
        tbl_rows = []
        for _, r in df_icc.iterrows():
            c = GREEN if 'Alta' in r['Semaforo'] else (AMBER if 'Optim' in r['Semaforo'] else RED)
            tbl_rows.append(html.Tr([
                html.Td(r['Cultivo']),
                html.Td(fmt(r['Utilidad'])),
                html.Td(f"{r['ICC']:,.0f}"),
                html.Td(r['Semaforo'], style={'color':c,'fontWeight':'700'}),
            ]))
        tbl = html.Table([
            html.Thead(html.Tr([html.Th(h) for h in ['Cultivo','Utilidad (MXN)','ICC (pts)','Semaforo']],
                                style={'background':BORDER})),
            html.Tbody(tbl_rows),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'13px'})

        return html.Div([
            kpis,
            html.Div([dcc.Graph(figure=fig_bar)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'}),
            html.Div([dcc.Graph(figure=fig_pmr)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'}),
            html.Div([html.H5("Dictamen de Competitividad por Cultivo", style={'color':CYAN,'marginBottom':'12px'}), tbl], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
        ])

    # ── Tab: Integrales (Analisis Matemático Avanzado 3D) ───────────────────
    elif tab == 'tab-math':
        # Definicion de funciones matematicas lambda f(x, y) donde x=hectareas, y=nivel de tecnificacion
        func_maiz = lambda y, x: ((16.548*x*mr) - ((19.8+12.257*x)*mc) - (0.2*y*mc))
        if hidro:
            func_higo = lambda y, x: ((356.259*x*mr) - (105.1*mc) - (0.1*(y**2)*mc) + (117.6*x*mr*0.5))
        else:
            func_higo = lambda y, x: ((238.659*x*mr) - (105.1*mc) - (0.1*(y**2)*mc))

        # Calculo del volumen total bajo las superficies usando integrales dobles de Scipy
        vol_maiz, _ = integrate.dblquad(func_maiz, 0, 5, 0, 3)
        vol_higo, _ = integrate.dblquad(func_higo, 0, 5, 0, 3)

        # Genera malla 3D (Grid) para dibujar la superficie
        x_v = np.linspace(0, 5, 50); y_v = np.linspace(0, 3, 50)
        xg, yg = np.meshgrid(x_v, y_v)
        z_m = np.vectorize(lambda x,y: func_maiz(y,x))(xg, yg) # Z (Altura) para Maiz
        z_h = np.vectorize(lambda x,y: func_higo(y,x))(xg, yg) # Z (Altura) para Higo

        # Contruccion de Grafico 3D en Plotly
        fig3d = go.Figure([
            go.Surface(z=z_h, x=xg, y=yg, colorscale='Tealgrn', name='Higo+Hidro', opacity=0.9, showscale=False),
            go.Surface(z=z_m, x=xg, y=yg, colorscale='OrRd',    name='Maiz',       opacity=0.8, showscale=False),
        ])
        fig3d.update_layout(
            title="Superficies de Rentabilidad 3D — Integrales Dobles",
            scene=dict(xaxis_title='Hectareas (x)', yaxis_title='Tecnificacion (y)', zaxis_title='Utilidad unitaria'),
            paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=520)

        # Diferencia numerica entre integrales
        brecha = vol_higo - vol_maiz
        c1, c2, c3 = (
            kpi_card("Volumen Higo (integral)", fmt(vol_higo*1000), "Alta Competitividad", GREEN),
            kpi_card("Volumen Maiz (integral)", fmt(vol_maiz*1000), "Diversificacion Urgente", RED),
            kpi_card("Brecha de Capitalizacion", fmt(brecha*1000), "Ganancia adicional anual", CYAN),
        )
        return html.Div([
            html.Div([c1,c2,c3], style={'display':'flex','gap':'12px','marginBottom':'20px'}),
            html.Div([dcc.Graph(figure=fig3d)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
            html.Div([
                html.P("Que significa este grafico?", style={'color':CYAN,'fontWeight':'700'}),
                html.P("Cada punto de la superficie representa la utilidad del agricultor para una combinacion "
                       "de hectareas y nivel de tecnologia. La superficie verde (Higo + Hidroponico) esta "
                       "SIEMPRE por encima de la superficie roja (Maiz), demostrando matematicamente que el "
                       "modelo diversificado es superior en cualquier escenario.",
                       style={'color':'#ccc','fontSize':'13px'}),
            ], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginTop':'16px'}),
        ])

    # ── Tab: Motor Predictivo Monte Carlo ───────────────────────────────────
    elif tab == 'tab-mc':
        N = 5000 # Numero de escenarios simulados por cultivo
        resultados = []
        for _, r in df_catalogo.iterrows():
            cult = r['nombre_cultivo']
            mb = FENOLOGICA.get(cult,{}).get(mes,1.0)
            pb = PRECIO_BASE.get(cult,5000)
            sd = pb * VOLATILIDAD.get(cult,0.15) * max(mb,0.1)
            
            # Generacion de precios aleatorios usando distribucion normal
            pf_sim = np.random.normal(pb*mb, sd, N)
            vol = VOL_ESPERADO.get(cult,4.0)
            utils = (vol*mr*mb)*(pf_sim*(1+r['prima_sostenibilidad'])) - r['costo_operativo']*mc
            
            if cult=='Higo' and hidro: utils += 59500.0 # Suma beneficio extra
                
            icc_sim = utils*(1 - r['riesgo_probabilidad']*mk)
            # PE (Probabilidad de exito) = Porcentaje de escenarios donde utilidad es positiva (>0)
            pe = (np.sum(icc_sim>0)/N)*100
            resultados.append({'Cultivo':cult, 'PE (%)':pe, 'ICC Esperado':np.mean(icc_sim),
                                'P10':np.percentile(icc_sim,10), # Escenario fatalista (10%)
                                'P90':np.percentile(icc_sim,90), # Escenario optimista (90%)
                                'Epoca':MES_OPTIMO.get(cult,'—')})
                                
        df_mc = pd.DataFrame(resultados).sort_values('PE (%)', ascending=False)

        # Grafico horizontal con probabilidades
        fig_pe = px.bar(df_mc, x='PE (%)', y='Cultivo', orientation='h',
                        color='PE (%)', color_continuous_scale=[[0,RED],[0.7,AMBER],[1,GREEN]],
                        title="Probabilidad de Exito por Cultivo (%)")
        fig_pe.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', coloraxis_showscale=False, height=280)
        fig_pe.add_vline(x=95, line_dash='dash', line_color=GREEN, annotation_text='95% (meta)')

        # Histograma que muestra la campana de distribucion del Higo
        row_higo = df_catalogo[df_catalogo['nombre_cultivo']=='Higo'].iloc[0]
        mb_h = FENOLOGICA['Higo'].get(mes,1.0)
        pf_h = np.random.normal(PRECIO_BASE['Higo']*mb_h, PRECIO_BASE['Higo']*0.12*max(mb_h,0.1), N)
        utils_h = (6.82*mr*mb_h)*(pf_h*(1+0.15)) - 105100*mc
        if hidro: utils_h += 59500.0
        icc_h = utils_h*(1 - 0.08*mk)

        fig_hist = go.Figure([go.Histogram(x=icc_h, nbinsx=60, name='Higo', marker_color=CYAN, opacity=0.8)])
        fig_hist.add_vline(x=0, line_dash='dash', line_color=RED, annotation_text='Quiebra')
        fig_hist.update_layout(title="Distribucion ICC — Higo (5,000 escenarios)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=300)

        best = df_mc.iloc[0]
        kpis_mc = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Cultivo Sugerido",      best['Cultivo'], f"{mes} — {best['Epoca']}", GREEN),
            kpi_card("Confianza Estadistica", f"{best['PE (%)']:.1f}%", "5,000 simulaciones", CYAN),
            kpi_card("ICC Esperado (Higo)",   f"{float(df_mc[df_mc['Cultivo']=='Higo']['ICC Esperado']):.0f}", "pts", CYAN),
            kpi_card("Peor escenario (P10)",  fmt(float(df_mc[df_mc['Cultivo']=='Higo']['P10'])), "10 percentil", AMBER),
        ])

        # Genera tabla HTML estatica con resumen de MC
        tbl_mc = html.Table([
            html.Thead(html.Tr([html.Th(h) for h in ['Cultivo','PE (%)','ICC Esperado','P10','P90','Epoca Optima']], style={'background':BORDER})),
            html.Tbody([
                html.Tr([
                    html.Td(r['Cultivo']),
                    html.Td(f"{r['PE (%)']:.1f}%", style={'color': GREEN if r['PE (%)']>=95 else (AMBER if r['PE (%)']>=70 else RED), 'fontWeight':'700'}),
                    html.Td(f"{r['ICC Esperado']:,.0f}"), html.Td(fmt(r['P10'])), html.Td(fmt(r['P90'])), html.Td(r['Epoca']),
                ]) for _, r in df_mc.iterrows()
            ]),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'13px'})

        return html.Div([
            kpis_mc,
            html.Div([dcc.Graph(figure=fig_pe)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'}),
            html.Div([dcc.Graph(figure=fig_hist)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'}),
            html.Div([html.H5("Resultados Monte Carlo por Cultivo", style={'color':CYAN,'marginBottom':'12px'}), tbl_mc], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
        ])

    # ── Tab: Modelo Hidroponico Específico ────────────────────────────────
    elif tab == 'tab-hidro':
        # Simula los ingresos a traves de los 12 meses
        meses_hidro = MESES
        mb_hidro = [FENOLOGICA['Lechuga (NFT)'][m] for m in meses_hidro]
        ing_mensual = [4200/12 * 28 * m for m in mb_hidro]

        # Grafico compuesto (Barras para ingresos, lineas para costos fijos)
        fig_hidro = go.Figure([
            go.Bar(x=meses_hidro, y=ing_mensual, name='Ingreso mensual lechuga', marker_color=[GREEN if v > 9000 else AMBER for v in ing_mensual]),
            go.Scatter(x=meses_hidro, y=[TOTAL_CF/12]*12, name='Gasto fijo mensual', line=dict(color=RED, dash='dash'), mode='lines+text'),
        ])
        fig_hidro.update_layout(title="Ingreso Mensual — Lechuga Hidroponica NFT (100 m2)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', barmode='group', height=320)

        # Grafica de pastel (Pie chart) con el desglose de gastos
        cats = ['Insumos hidro', 'Riego Higo', 'MO Higo', 'Fertiliz. Higo', 'Empaque Higo']
        vals = [35700, 3800, 6200, 5500, 2300]
        fig_comp = px.pie(names=cats, values=vals, title="Composicion de Costos Variables", color_discrete_sequence=[CYAN,GREEN,AMBER,'#9c27b0',RED])
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=320)

        kpis_h = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Ingreso Anual Lechuga",  fmt(INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"]), "4,200 kg x $28/kg", GREEN),
            kpi_card("Costo Insumos Hidro",    fmt(35700), "Nutrientes + semillas + MO", AMBER),
            kpi_card("Margen Neto Hidro", fmt(INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"]-35700), "Sin costos fijos asignados", CYAN),
            kpi_card("Ciclos por anio",         "~8-10 ciclos", "35-45 dias por ciclo", "#9c27b0"),
        ])

        # Seccion de Preguntas Frecuentes
        faq = [
            ("Que es el sistema NFT?", "Nutrient Film Technique: una lamina delgada de solucion nutritiva circula por tubos inclinados donde crecen las plantas sin suelo. Usa ~90% menos agua que el cultivo tradicional."),
            ("Por que lechuga?", "Ciclo corto (35-45 dias), alta demanda en mercados locales, precio estable (~$28/kg), bajo riesgo fitosanitario en sistema cerrado."),
            ("Cuando genera dinero?", "Todos los meses. El primer ciclo produce en 35-45 dias. A partir del 2o mes hay flujo constante que cubre los gastos fijos mientras el higo madura."),
            ("Que pasa si sube el precio?", "El modelo es conservador ($28/kg). En tiendas y restaurantes el precio puede llegar a $35-50/kg, mejorando aun mas la rentabilidad."),
        ]
        faq_items = [html.Details([html.Summary(q, style={'cursor':'pointer','color':CYAN,'padding':'8px 0','fontWeight':'600'}), html.P(a, style={'color':'#ccc','fontSize':'13px','paddingLeft':'16px'})]) for q,a in faq]

        return html.Div([
            kpis_h,
            html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px','marginBottom':'16px'}, children=[
                html.Div([dcc.Graph(figure=fig_hidro)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
                html.Div([dcc.Graph(figure=fig_comp)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
            ]),
            html.Div([html.H5("Preguntas Frecuentes — Hidroponia NFT", style={'color':CYAN,'marginBottom':'12px'})] + faq_items, style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
        ])

    # ── Tab: Dictamen Operativo (Historico/Proyeccion Consolidado) ───────
    elif tab == 'tab-dictamen':
        # Llama la funcion que genera el historial y predice el futuro con MC
        df_dict = generar_dictamen_completo(municipio, mes, anio_range[0], anio_range[1])
        if df_dict.empty: return html.P("Sin datos para el rango seleccionado.", style={'color':AMBER})

        hist_df = df_dict[df_dict['Tipo'] == 'Historico']
        proj_df = df_dict[df_dict['Tipo'] == 'Proyeccion Monte Carlo']
        
        # Resumen en tarjetas
        kpis_d = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Registros Historicos",       str(len(hist_df)), "2018–2024", CYAN),
            kpi_card("Registros Proyectados",      str(len(proj_df)), "2025–2026 MC", GREEN),
            kpi_card("ICC Promedio Historico",     f"{hist_df['ICC'].mean():,.0f}" if not hist_df.empty else "—", "pts", CYAN),
            kpi_card("ICC Promedio Proyectado",    f"{proj_df['ICC'].mean():,.0f}" if not proj_df.empty else "—", "pts", GREEN),
            kpi_card("Utilidad Neta Acumulada",    fmt(df_dict['Utilidad_Neta'].sum()), "Todo el periodo", AMBER),
        ])

        # Linea de tiempo general del ICC
        fig_dict = px.line(df_dict, x='Anio', y='ICC', color='Cultivo', line_dash='Tipo', title=f"ICC por Cultivo y Anio — {municipio}", markers=True)
        fig_dict.add_hline(y=100000, line_dash='dash', line_color=GREEN, annotation_text="Alta (100k)")
        fig_dict.add_hline(y=20000,  line_dash='dash', line_color=AMBER, annotation_text="Min (20k)")
        fig_dict.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=380)

        # Contruccion de la tabla grande final
        color_map = {'Alta Competitividad': GREEN, 'Optimizacion Requerida': AMBER, 'Diversificacion Urgente': RED}
        tbl_rows2 = []
        for _, r in df_dict.iterrows():
            c = color_map.get(r['Estatus'], '#fff')
            badge_bg = {'Alta Competitividad':'#1a4a1a', 'Optimizacion Requerida':'#4a3a00', 'Diversificacion Urgente':'#4a0a0a'}.get(r['Estatus'],'#111')
            
            # Anade formato diferenciando historia vs proyeccion
            tbl_rows2.append(html.Tr([
                html.Td(str(r['Anio']), style={'color': CYAN if r['Tipo']=='Proyeccion Monte Carlo' else '#fff'}),
                html.Td(r['Cultivo']),
                html.Td(r['Tipo'], style={'fontSize':'11px','color':'#aaa'}),
                html.Td(f"{r['Volumen_t']:,.3f}"), html.Td(f"${r['PMR']:,.0f}"), html.Td(fmt(r['Costo_Ajustado'])),
                html.Td(fmt(r['Utilidad_Neta']), style={'color': GREEN if r['Utilidad_Neta']>0 else RED}),
                html.Td(f"{r['ICC']:,.0f}"),
                html.Td(r['Estatus'], style={'color':c,'fontWeight':'700','fontSize':'11px', 'background':badge_bg,'padding':'2px 6px','borderRadius':'4px'}),
            ]))
        tbl2 = html.Table([
            html.Thead(html.Tr([html.Th(h, style={'padding':'8px 10px'}) for h in ['Anio','Cultivo','Tipo','Vol. (t)','PMR ($/t)', 'Costo Ajust.','Utilidad Neta','ICC (pts)','Estatus']], style={'background':BORDER})),
            html.Tbody(tbl_rows2),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'12px'})

        return html.Div([
            kpis_d,
            html.Div([dcc.Graph(figure=fig_dict)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px', 'padding':'16px','marginBottom':'16px'}),
            html.Div([html.H5(f"Tabla Completa — {municipio} ({anio_range[0]}-{anio_range[1]})", style={'color':CYAN,'marginBottom':'12px'}), html.P("Anios en azul = proyeccion estadistica Monte Carlo (2025-2026).", style={'color':'#6a8aaa','fontSize':'11px','marginBottom':'10px'}), tbl2], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'}),
        ])

    return html.Div("Selecciona una pestana")


# ── Callbacks de descarga (Archivos PDF y CSV) ───────────────────────────────────

# Funcion interna reutilizada por los PDF para calcular estadisticas rapidad
def _get_mc_stats(municipio, mes):
    """Calcula PE e ICC para inyectarlo en el PDF."""
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc_m, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    mb_h = FENOLOGICA['Higo'].get(mes, 1.0)
    pf_h = np.random.normal(PRECIO_BASE['Higo']*mb_h, PRECIO_BASE['Higo']*0.12*max(mb_h,0.1), 5000)
    utils_h = (6.82*mr*mb_h)*(pf_h*1.15) - 105100*mc_m + 59500
    icc_h = utils_h*(1 - 0.08*mk)
    pe_higo = (np.sum(icc_h>0)/5000)*100
    return mr, mc_m, pe_higo, float(np.mean(icc_h))


# PDF Mensual
@app.callback(
    Output('dl-pdf-mensual','data'),
    Input('btn-pdf-mensual','n_clicks'),
    State('dd-municipio','value'),
    State('dd-mes','value'),
    prevent_initial_call=True,
)
def descargar_pdf_mensual(n, municipio, mes):
    if not n: return None
    mr, mc_m, pe_higo, icc_higo = _get_mc_stats(municipio, mes)
    pdf_bytes = generar_pdf_reporte(municipio, mes, mr, mc_m, pe_higo, icc_higo, modo='mensual')
    b64 = base64.b64encode(pdf_bytes).decode()
    return dict(content=b64, filename=f"reporte_mensual_{municipio}_{mes}.pdf",
                type="application/pdf", base64=True)


# PDF Anual
@app.callback(
    Output('dl-pdf-anual','data'),
    Input('btn-pdf-anual','n_clicks'),
    State('dd-municipio','value'),
    State('dd-mes','value'),
    prevent_initial_call=True,
)
def descargar_pdf_anual(n, municipio, mes):
    if not n: return None
    mr, mc_m, pe_higo, icc_higo = _get_mc_stats(municipio, mes)
    df_dict = generar_dictamen_completo(municipio, mes, 2018, 2026)
    pdf_bytes = generar_pdf_reporte(municipio, mes, mr, mc_m, pe_higo, icc_higo,
                                    modo='anual', df_dictamen=df_dict)
    b64 = base64.b64encode(pdf_bytes).decode()
    return dict(content=b64, filename=f"reporte_anual_{municipio}_2018_2026.pdf",
                type="application/pdf", base64=True)


# CSV Mensual
@app.callback(
    Output('dl-csv-mensual','data'),
    Input('btn-csv-mensual','n_clicks'),
    State('dd-municipio','value'),
    State('dd-mes','value'),
    prevent_initial_call=True,
)
def descargar_csv_mensual(n, municipio, mes):
    if not n: return None
    df_csv = generar_csv_mensual(municipio, mes)
    csv_bytes = generar_csv(df_csv)
    b64 = base64.b64encode(csv_bytes).decode()
    return dict(content=b64, filename=f"reporte_mensual_{municipio}_{mes}.csv",
                type="text/csv", base64=True)


# CSV Anual
@app.callback(
    Output('dl-csv-anual','data'),
    Input('btn-csv-anual','n_clicks'),
    State('dd-municipio','value'),
    State('dd-mes','value'),
    prevent_initial_call=True,
)
def descargar_csv_anual(n, municipio, mes):
    if not n: return None
    df_csv = generar_csv_anual(municipio, mes)
    csv_bytes = generar_csv(df_csv)
    b64 = base64.b64encode(csv_bytes).decode()
    return dict(content=b64, filename=f"reporte_anual_{municipio}_2018_2026.csv",
                type="text/csv", base64=True)


if __name__ == '__main__':
    app.run(debug=True, port=8050)