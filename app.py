import os, io, base64
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import integrate
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm
from database import obtener_motor_mysql

engine = obtener_motor_mysql()

df_municipios = pd.read_sql("SELECT * FROM municipios", engine)
df_catalogo = pd.read_sql("SELECT * FROM catalogo_cultivos", engine)
df_fenologica = pd.read_sql("SELECT * FROM matriz_fenologica", engine)
df_parametros = pd.read_sql("SELECT * FROM parametros_financieros", engine)

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

INGRESOS = {
    "Venta de Higo (6.82 t x $34,994.18/t)": 238659.31,
    "Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)": 117600.00
}

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

TOTAL_INGRESOS = sum(INGRESOS.values())
TOTAL_CV = sum(COSTOS_VARIABLES.values())
TOTAL_CF = sum(COSTOS_FIJOS.values())
MARGEN_CONTRIB = TOTAL_INGRESOS - TOTAL_CV
UTILIDAD_OP = MARGEN_CONTRIB - TOTAL_CF
PUNTO_EQ = TOTAL_CF / (MARGEN_CONTRIB / TOTAL_INGRESOS)
TOTAL_INV = sum(INVERSION_INICIAL.values())
PAYBACK = TOTAL_INV / UTILIDAD_OP

FENOLOGICA = {}
for cult_id, cult_nom in zip(df_catalogo['id_cultivo'], df_catalogo['nombre']):
    feno_cultivo = df_fenologica[df_fenologica['id_cultivo'] == cult_id]
    FENOLOGICA[cult_nom] = dict(zip(feno_cultivo['mes'], feno_cultivo['multiplicador']))

VOL_ESPERADO = dict(zip(df_catalogo['nombre'], df_catalogo['volumen_esperado']))
PRECIO_BASE = dict(zip(df_catalogo['nombre'], df_catalogo['precio_base']))
VOLATILIDAD = dict(zip(df_catalogo['nombre'], df_catalogo['volatilidad']))
MES_OPTIMO = dict(zip(df_catalogo['nombre'], df_catalogo['mes_optimo']))
MESES = list(FENOLOGICA['Higo'].keys())

np.random.seed(42)

CYAN, GREEN, AMBER, RED, BG, CARD, BORDER = "#00e5ff", "#00c853", "#ffb300", "#f44336", "#060b18", "#0d1b2a", "#1a3a5c"

fmt = lambda n: f"${n:,.2f}"
color_icc = lambda v: GREEN if v > 100000 else (AMBER if v > 20000 else RED)
clasificar_icc = lambda v: "Alta Competitividad" if v > 100000 else ("Optimizacion Requerida" if v > 20000 else "Diversificacion Urgente")
hidro_activa = lambda h: bool(h and 'hidro' in h)

def generar_dictamen_completo(municipio, mes, anio_ini=2018, anio_fin=2026):
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
                mb = FENOLOGICA.get(cult, {}).get(mes, 1.0)
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
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding='utf-8')
    return buf.getvalue().encode('utf-8')

def generar_csv_mensual(municipio, mes):
    filas = []
    mr = df_municipios[df_municipios['nombre'] == municipio].iloc[0]['mod_rendimiento']
    for cultivo in FENOLOGICA:
        mb = FENOLOGICA[cultivo].get(mes, 1.0)
        pb = PRECIO_BASE.get(cultivo, 5000)
        vol = VOL_ESPERADO.get(cultivo, 4.0)
        ingreso = vol * mr * mb * pb
        filas.append({
            'Mes': mes, 'Municipio': municipio, 'Cultivo': cultivo, 'Modificador_Fenologico': mb,
            'Volumen_Est_t': round(vol * mr * mb, 3), 'PMR_Base': pb, 'Ingreso_Estimado': round(ingreso, 2)
        })
    return pd.DataFrame(filas)

def generar_pdf_reporte(municipio, mes, mod_rend, mod_costo, pe_higo, icc_higo, modo='anual', df_dictamen=None):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    ss = getSampleStyleSheet()
    
    estilos = {
        'titulo': ParagraphStyle('titulo', parent=ss['Heading1'], fontSize=14, textColor=colors.HexColor('#003366'), spaceAfter=8, alignment=1),
        'seccion': ParagraphStyle('seccion', parent=ss['Heading2'], fontSize=12, textColor=colors.HexColor('#005b99'), spaceAfter=6, fontName='Helvetica-Bold'),
        'body': ParagraphStyle('body', parent=ss['Normal'], fontSize=9, leading=13, alignment=4, spaceAfter=8),
        'bold': ParagraphStyle('bold', parent=ss['Normal'], fontSize=9, textColor=colors.HexColor('#003366'), fontName='Helvetica-Bold'),
        'footer': ParagraphStyle('footer', parent=ss['Normal'], fontSize=7, textColor=colors.grey, alignment=1),
        'apa': ParagraphStyle('apa', parent=ss['Normal'], fontSize=8, leading=11, leftIndent=1*cm, firstLineIndent=-1*cm, spaceAfter=4)
    }

    def tabla(data, col_widths, header_bg=colors.HexColor('#003366')):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), header_bg), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#c0d0e0')), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)
        ]))
        return t

    story = []
    
    tipo_reporte = f"REPORTE MENSUAL (Proyección específica para {mes})" if modo == 'mensual' else "REPORTE ANUAL (Proyección Ejercicio 2026)"
    
    story.append(Paragraph("UNIVERSIDAD NACIONAL ROSARIO CASTELLANOS", estilos['titulo']))
    story.append(Paragraph(f"INFORME EJECUTIVO: Análisis Técnico-Económico para la Diversificación de Cultivos<br/>{tipo_reporte}", estilos['titulo']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366'), spaceAfter=15))

    story.append(Paragraph("1. Resumen", estilos['seccion']))
    story.append(Paragraph(f"Este informe ejecutivo presenta una solución basada en ciencia de datos para la crisis de rentabilidad agrícola en el municipio de {municipio}. A través del modelado matemático de superficies financieras y simulaciones estocásticas de Monte Carlo, se demuestra que la transición del monocultivo de maíz tradicional hacia un modelo agroforestal diversificado (Higo tecnificado + Lechuga Hidropónica NFT) garantiza la solvencia económica, estabilizando el flujo de caja mediante ingresos recurrentes.", estilos['body']))

    story.append(Paragraph("2. Contexto y justificación", estilos['seccion']))
    story.append(Paragraph("La producción agrícola tradicional en zonas periurbanas enfrenta una vulnerabilidad crítica ante el aumento de costos de agroquímicos y la dependencia de los regímenes pluviales. El monocultivo obliga a las familias productoras a endeudarse para sobrevivir los meses inactivos. La diversificación hacia cultivos de alto valor y bajo consumo hídrico (como la hidroponía) es una respuesta necesaria para asegurar la competitividad y la seguridad patrimonial.", estilos['body']))

    story.append(Paragraph("3. Metodología", estilos['seccion']))
    story.append(Paragraph("El enfoque de trabajo se fundamentó en la extracción y análisis de microdatos gestionados en una base de datos relacional (MySQL) mediante SQLAlchemy. Se empleó Cálculo Integral Multivariable para determinar el volumen regional de ganancias y un Motor Predictivo de Monte Carlo (5,000 iteraciones) para evaluar el riesgo financiero ante variaciones climáticas y de precios en la central de abastos.", estilos['body']))

    story.append(Paragraph("4. Diagnóstico del problema", estilos['seccion']))
    txt_rend = f"un rendimiento {int((mod_rend - 1) * 100)}% superior al promedio" if mod_rend >= 1 else f"un rendimiento {int((1 - mod_rend) * 100)}% inferior al promedio"
    txt_cost = f"costos operativos {int((1 - mod_costo) * 100)}% más bajos" if mod_costo <= 1 else f"costos operativos {int((mod_costo - 1) * 100)}% más altos"
    story.append(Paragraph(f"El análisis de los datos revela que el maíz tradicional opera frecuentemente con márgenes negativos. Para la evaluación en <b>{municipio}</b> bajo un esquema <b>{modo}</b>, las condiciones topográficas imponen {txt_rend} y {txt_cost}. Mantener el monocultivo bajo estos parámetros asegura pérdidas operativas frente a la inflación de insumos.", estilos['body']))

    story.append(Paragraph("5. Solución propuesta", estilos['seccion']))
    story.append(Paragraph("Se propone la implementación de un ecosistema modular: 1 hectárea de higo combinada con 100 metros cuadrados de sistema hidropónico NFT. A continuación, se fundamenta la viabilidad financiera proyectada a nivel anual para dimensionar el negocio:", estilos['body']))
    
    er_data = [
        ["Concepto", "Monto (MXN)", "Observación"],
        ["(+) Total ingresos esperados", fmt(TOTAL_INGRESOS), "Venta de Higo + Lechuga hidroponica"],
        ["(-) Costos variables", fmt(TOTAL_CV), "Insumos, mano de obra, empaque"],
        ["(=) Margen de contribución", fmt(MARGEN_CONTRIB), "Cobertura de costos operativos"],
        ["(-) Costos fijos", fmt(TOTAL_CF), "Arrendamiento, amortizaciones y energía"],
        ["(=) UTILIDAD NETA OPERATIVA", fmt(UTILIDAD_OP), "Libre de impuestos (Régimen AGAPES)"]
    ]
    t_er = tabla(er_data, [5.5*cm, 3.5*cm, 8*cm])
    t_er.setStyle(TableStyle([('BACKGROUND', (0,5), (-1,5), colors.HexColor('#1a6e1a')), ('TEXTCOLOR', (0,5), (-1,5), colors.white), ('FONTNAME', (0,5), (-1,5), 'Helvetica-Bold')]))
    story.append(t_er)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph(f"El modelo requiere una inversión inicial de {fmt(TOTAL_INV)}, con un punto de equilibrio anual en {fmt(PUNTO_EQ)}. La viabilidad es alta, logrando un periodo de recuperación de la inversión (Payback) de {PAYBACK:.1f} años.", estilos['body']))
    
    txt_mes = f" focalizada en el mes de <b>{mes}</b>" if modo == 'mensual' else " anualizada"
    story.append(Paragraph(f"Simulación de Viabilidad Estocástica: La prueba de estrés{txt_mes} demostró que este modelo tiene una Probabilidad de Éxito del {pe_higo:.1f}%, con un Puntaje de Seguridad (ICC) de {icc_higo:,.0f} puntos, clasificándose como '{clasificar_icc(icc_higo)}'.", estilos['body']))

    story.append(Paragraph("6. Recomendaciones estratégicas", estilos['seccion']))
    story.append(Paragraph("1. Ejecutar la inversión inicial priorizando la infraestructura del módulo hidropónico para asegurar liquidez en el primer mes.<br/>2. Establecer contratos de venta anticipada para la lechuga en mercados locales y restaurantes.<br/>3. Monitorear los ciclos fenológicos del higo apoyándose en el semáforo de competitividad de esta herramienta.", estilos['body']))

    story.append(Paragraph("7. Conclusiones", estilos['seccion']))
    story.append(Paragraph("La transición hacia la diversificación agrícola es imperativa. El modelo propuesto no solo es económicamente viable, sino que actúa como un estabilizador estructural del flujo de caja. Al combinar el alto valor del higo con la rotación rápida de la hidroponía, las familias productoras mitigan el riesgo climático y aseguran el crecimiento de su patrimonio a largo plazo.", estilos['body']))

    story.append(Paragraph("8. Anexos", estilos['seccion']))
    if df_dictamen is not None and not df_dictamen.empty:
        story.append(Paragraph("Anexo A: Dictamen Operativo Histórico y Proyección Predictiva (2018-2026)", estilos['body']))
        dict_header = [["Año", "Cultivo", "Tipo", "Vol. (t)", "Precio Mercado", "Costo Ajustado", "Utilidad Neta", "ICC", "Estatus"]]
        dict_rows = []
        for _, r in df_dictamen.iterrows():
            dict_rows.append([str(r['Anio']), str(r['Cultivo']), "Hist." if r['Tipo'] == 'Historico' else "Proy.", f"{r['Volumen_t']:,.2f}", f"${r['PMR']:,.2f}", f"${r['Costo_Ajustado']:,.2f}", f"${r['Utilidad_Neta']:,.2f}", f"{r['ICC']:,.0f}", str(r['Estatus'])])
        t_dict = tabla(dict_header + dict_rows, [1.1*cm, 2.2*cm, 1.2*cm, 1.8*cm, 2.1*cm, 2.1*cm, 2.1*cm, 1.8*cm, 2.6*cm])
        
        style_extra = []
        for idx, r in enumerate(df_dictamen.itertuples(), start=1):
            bg = colors.HexColor('#c8f5c8') if r.Estatus == 'Alta Competitividad' else (colors.HexColor('#ffd0d0') if r.Estatus == 'Diversificacion Urgente' else colors.HexColor('#fff5cc'))
            if r.Cultivo in ['Higo', 'Lechuga (NFT)']: style_extra.append(('FONTNAME', (0, idx), (-1, idx), 'Helvetica-Bold'))
            style_extra.append(('BACKGROUND', (0, idx), (-1, idx), bg))
        t_dict.setStyle(TableStyle(style_extra))
        story.append(t_dict)
    else:
        story.append(Paragraph("Nota: El Anexo del Dictamen Histórico 2018-2026 se excluye de la vista mensual para fines de legibilidad ejecutiva. Para visualizar la tabla completa, emita el Reporte Anual.", estilos['body']))

    story.append(Paragraph("9. Referencias", estilos['seccion']))
    story.append(Paragraph("Cámara de Diputados del H. Congreso de la Unión. (2024). Ley del Impuesto sobre la Renta: Régimen del Sector Primario (Art. 74). Diario Oficial de la Federación.", estilos['apa']))
    story.append(Paragraph("Instituto Nacional de Estadística y Geografía [INEGI]. (2022). Censo Agropecuario 2022: Resultados definitivos para el estado de Morelos.", estilos['apa']))
    story.append(Paragraph("Secretaría de Agricultura y Desarrollo Rural [SADER]. (2024). Cierre de la producción agrícola por municipio (2018-2024). SIAP.", estilos['apa']))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Universidad Nacional Rosario Castellanos — Licenciatura en Ciencias de Datos para Negocios — Smart Agroforestry Morelos", estilos['footer']))

    doc.build(story)
    buf.seek(0)
    return buf.read()

def kpi_card(title, value, sub=None, color=CYAN):
    return html.Div([
        html.P(title, style={'fontSize':'11px','color':'#6a8aaa','marginBottom':'4px','fontFamily':'monospace'}),
        html.H4(value, style={'color':color,'margin':'0','fontSize':'1.4rem'}),
        html.P(sub or '', style={'fontSize':'10px','color':'#6a8aaa','marginTop':'2px'}),
    ], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','flex':'1','minWidth':'170px'})

def grafico_card(fig):
    return html.Div([dcc.Graph(figure=fig)], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px','marginBottom':'16px'})

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
app.title = "Smart Agroforestry Morelos"

BOTON_STYLE = {'width':'100%','background':CYAN,'color':'#000','border':'none','padding':'10px','borderRadius':'6px','fontWeight':'700','cursor':'pointer','fontSize':'12px','marginBottom':'6px'}
TAB_STYLE = {'color':'#aaa'}
TAB_SEL = {'color':CYAN,'fontWeight':'700'}

app.layout = html.Div(style={'backgroundColor':BG,'minHeight':'100vh','fontFamily':'Rajdhani, sans-serif','color':'#fff'}, children=[
    html.Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap'),
    html.Div([
        html.H2("Smart Agroforestry Morelos", style={'margin':'0','color':CYAN}),
        html.P("Sistema Inteligente de Analisis Tecnico-Economico — Higo + Lechuga Hidroponica NFT", style={'margin':'2px 0 0','color':'#6a8aaa','fontSize':'13px'}),
    ], style={'background':CARD,'borderBottom':f'1px solid {BORDER}','padding':'18px 30px'}),
    html.Div(style={'display':'flex','minHeight':'calc(100vh - 70px)'}, children=[
        html.Div(style={'width':'260px','background':CARD,'borderRight':f'1px solid {BORDER}','padding':'20px','flexShrink':'0'}, children=[
            html.H5("Panel de Control", style={'color':CYAN,'marginBottom':'16px'}),
            html.Label("Municipio", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Dropdown(id='dd-municipio', options=list(map(lambda m: {'label':m,'value':m}, df_municipios['nombre'])), value='Temixco', style={'background':'#0d1b2a','color':'#fff','borderColor':BORDER}),
            html.Br(),
            html.Label("Mes de Analisis", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Dropdown(id='dd-mes', options=list(map(lambda m: {'label':m,'value':m}, MESES)), value='Mayo', style={'background':'#0d1b2a','color':'#fff','borderColor':BORDER}),
            html.Br(),
            html.Label("Periodo Historico", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.RangeSlider(id='sl-anio', min=2018, max=2026, step=1, value=[2018,2026], marks={y:str(y) for y in range(2018,2027,2)}, tooltip={"placement":"bottom"}),
            html.Br(),
            html.Label("Incluir Modulo Hidroponico", style={'fontSize':'11px','color':'#6a8aaa'}),
            dcc.Checklist(id='chk-hidro', options=[{'label':' Lechuga NFT (100 m2)','value':'hidro'}], value=['hidro'], style={'color':GREEN}),
            html.Br(),
            html.Div(id='sidebar-info', style={'background':'#060b18','border':f'1px solid {BORDER}','borderRadius':'6px','padding':'12px','fontSize':'11px','color':'#6a8aaa'}),
            html.Br(),
            html.P("Reportes PDF", style={'fontSize':'11px','color':CYAN,'marginBottom':'6px','fontWeight':'700'}),
            html.Button("PDF Mensual", id='btn-pdf-mensual', n_clicks=0, style=BOTON_STYLE),
            html.Button("PDF Anual",   id='btn-pdf-anual',   n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-pdf-mensual'), dcc.Download(id='dl-pdf-anual'),
            html.Br(),
            html.P("Reportes CSV", style={'fontSize':'11px','color':CYAN,'marginBottom':'6px','fontWeight':'700'}),
            html.Button("CSV Mensual", id='btn-csv-mensual', n_clicks=0, style=BOTON_STYLE),
            html.Button("CSV Anual",   id='btn-csv-anual',   n_clicks=0, style=BOTON_STYLE),
            dcc.Download(id='dl-csv-mensual'), dcc.Download(id='dl-csv-anual'),
        ]),
        html.Div(style={'flex':'1','padding':'24px','overflowY':'auto'}, children=[
            dcc.Tabs(id='tabs', value='tab-dash', style={'borderBottom':f'1px solid {BORDER}'}, colors={'border':BORDER,'primary':CYAN,'background':BG}, children=list(map(lambda lv: dcc.Tab(label=lv[0], value=lv[1], style=TAB_STYLE, selected_style=TAB_SEL), [
                ("Dashboard Operativo", 'tab-dash'), ("Evaluacion Regional (Integrales)", 'tab-math'), ("Motor Predictivo (Monte Carlo)", 'tab-mc'), ("Modelo Hidroponico", 'tab-hidro'), ("Dictamen Operativo 2018-2026", 'tab-dictamen')
            ]))),
            html.Div(id='tab-content', style={'marginTop':'20px'}),
        ]),
    ]),
])

@app.callback(Output('sidebar-info','children'), Input('dd-municipio','value'))
def update_sidebar_info(municipio):
    row = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    return [html.B(municipio), html.Br(), f"Suelo: {row['tipo_suelo']}", html.Br(), f"Rendimiento: x{row['mod_rendimiento']} | Costo: x{row['mod_costo']}", html.Br(), f"Riesgo edafo.: x{row['mod_riesgo']}"]

@app.callback(Output('tab-content','children'), Input('tabs','value'), Input('dd-municipio','value'), Input('dd-mes','value'), Input('sl-anio','value'), Input('chk-hidro','value'))
def render_tab(tab, municipio, mes, anio_range, hidro_val):
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    hidro = hidro_activa(hidro_val)

    def _icc_row(r):
        cult = r['nombre']
        mb = FENOLOGICA.get(cult, {}).get(mes, 1.0)
        pb = PRECIO_BASE.get(cult, 5000)
        pf = float(np.mean(np.random.normal(pb*mb, pb*VOLATILIDAD.get(cult, 0.15)*max(mb, 0.1), 2000)))
        vol = VOL_ESPERADO.get(cult, 4.0)
        util = (vol*mr*mb) * (pf*(1+r['prima_sostenibilidad'])) - r['costo_operativo']*mc
        if cult == 'Higo' and hidro: util += (117600.00 - (TOTAL_CF - 18000))
        return {'Cultivo': cult, 'Utilidad': util, 'ICC': util * (1 - r['riesgo_probabilidad']*mk), 'Mb': mb, 'Semaforo': clasificar_icc(util * (1 - r['riesgo_probabilidad']*mk))}

    df_icc = pd.DataFrame(list(map(_icc_row, df_catalogo.to_dict('records'))))

    if tab == 'tab-dash':
        df_plot = df_hist[(df_hist['Nommunicipio']==municipio) & (df_hist['Anio']>=anio_range[0]) & (df_hist['Anio']<=min(2024, anio_range[1]))]
        kpis = html.Div(style={'display':'flex','gap':'12px','flexWrap':'wrap','marginBottom':'20px'}, children=[
            kpi_card("Utilidad Neta Modelo", fmt(UTILIDAD_OP), "Higo + Lechuga (2026)", GREEN),
            kpi_card("Ingresos Totales", fmt(TOTAL_INGRESOS), "Higo + Lechuga", CYAN),
            kpi_card("Costos Totales", fmt(TOTAL_CV+TOTAL_CF), "Variables + Fijos", AMBER),
            kpi_card("Punto de Equilibrio", fmt(PUNTO_EQ), f"{PUNTO_EQ/TOTAL_INGRESOS*100:.1f}% de ingresos", "#9c27b0"),
            kpi_card("Recuperacion Inversion", f"{PAYBACK:.1f} anos", f"Inversion: {fmt(TOTAL_INV)}", CYAN),
        ])
        fig_bar = px.bar(df_icc.sort_values('ICC'), x='ICC', y='Cultivo', orientation='h', color='ICC', color_continuous_scale=[[0,RED],[0.2,AMBER],[1,GREEN]], title=f"Indice de Competitividad (ICC) — {municipio} / {mes}")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', coloraxis_showscale=False, height=280)
        fig_bar.add_vline(x=20000, line_dash='dash', line_color=AMBER, annotation_text="20k (min)")
        fig_bar.add_vline(x=100000, line_dash='dash', line_color=GREEN, annotation_text="100k (alta)")

        fig_pmr = px.line(df_plot, x='Anio', y='PMR', color='Nomcultivo', title="Precio Medio Rural historico (MXN/t)", markers=True)
        fig_pmr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=300)

        tbl = html.Table([
            html.Thead(html.Tr(list(map(lambda h: html.Th(h), ['Cultivo','Utilidad (MXN)','ICC (pts)','Semaforo'])), style={'background':BORDER})),
            html.Tbody(list(map(lambda r: html.Tr([html.Td(r['Cultivo']), html.Td(fmt(r['Utilidad'])), html.Td(f"{r['ICC']:,.0f}"), html.Td(r['Semaforo'], style={'color': GREEN if 'Alta' in r['Semaforo'] else (AMBER if 'Optim' in r['Semaforo'] else RED),'fontWeight':'700'})]), df_icc.to_dict('records')))),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'13px'})
        return html.Div([kpis, grafico_card(fig_bar), grafico_card(fig_pmr), html.Div([html.H5("Dictamen de Competitividad", style={'color':CYAN,'marginBottom':'12px'}), tbl], style={'background':CARD,'border':f'1px solid {BORDER}','borderRadius':'8px','padding':'16px'})])

    elif tab == 'tab-math':
        func_maiz = lambda y, x: ((16.548*x*mr) - ((19.8+12.257*x)*mc) - (0.2*y*mc))
        if hidro:
            func_higo = lambda y, x: ((356.259*x*mr) - (105.1*mc) - (0.1*(y**2)*mc) + (117.6*x*mr*0.5))
        else:
            func_higo = lambda y, x: ((238.659*x*mr) - (105.1*mc) - (0.1*(y**2)*mc))
        vol_maiz, _ = integrate.dblquad(func_maiz, 0, 5, 0, 3)
        vol_higo, _ = integrate.dblquad(func_higo, 0, 5, 0, 3)
        
        xg, yg = np.meshgrid(np.linspace(0, 5, 50), np.linspace(0, 3, 50))
        fig3d = go.Figure([go.Surface(z=np.vectorize(lambda x,y: func_higo(y,x))(xg, yg), x=xg, y=yg, colorscale='Tealgrn', opacity=0.9, showscale=False), go.Surface(z=np.vectorize(lambda x,y: func_maiz(y,x))(xg, yg), x=xg, y=yg, colorscale='OrRd', opacity=0.8, showscale=False)])
        fig3d.update_layout(title="Superficies de Rentabilidad 3D", scene=dict(xaxis_title='Hectareas (x)', yaxis_title='Tecnificacion (y)', zaxis_title='Utilidad unitaria'), paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=520)
        return html.Div([html.Div([kpi_card("Volumen Higo (integral)", fmt(vol_higo*1000), "Alta Competitividad", GREEN), kpi_card("Volumen Maiz (integral)", fmt(vol_maiz*1000), "Diversificacion Urgente", RED), kpi_card("Brecha de Capitalizacion", fmt((vol_higo-vol_maiz)*1000), "Ganancia adicional", CYAN)], style={'display':'flex','gap':'12px','marginBottom':'20px'}), grafico_card(fig3d)])

    elif tab == 'tab-mc':
        def _mc_row(row):
            cult = row['nombre']
            mb = FENOLOGICA.get(cult, {}).get(mes, 1.0)
            pb = PRECIO_BASE.get(cult, 5000)
            pf_sim = np.random.normal(pb*mb, pb*VOLATILIDAD.get(cult, 0.15)*max(mb, 0.1), 5000)
            utils = (VOL_ESPERADO.get(cult, 4.0)*mr*mb)*(pf_sim*(1+row['prima_sostenibilidad'])) - row['costo_operativo']*mc
            if cult == 'Higo' and hidro: utils += 59500.0
            icc_sim = utils * (1 - row['riesgo_probabilidad']*mk)
            return {'Cultivo': cult, 'PE (%)': (np.sum(icc_sim>0)/5000)*100, 'ICC Esperado': np.mean(icc_sim), 'P10': np.percentile(icc_sim, 10), 'P90': np.percentile(icc_sim, 90), 'Epoca': MES_OPTIMO.get(cult, '—')}
        
        df_mc = pd.DataFrame(list(map(_mc_row, df_catalogo.to_dict('records')))).sort_values('PE (%)', ascending=False)
        fig_pe = px.bar(df_mc, x='PE (%)', y='Cultivo', orientation='h', color='PE (%)', color_continuous_scale=[[0,RED],[0.7,AMBER],[1,GREEN]], title="Probabilidad de Exito por Cultivo (%)")
        fig_pe.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', coloraxis_showscale=False, height=280)
        
        mb_h = FENOLOGICA['Higo'].get(mes, 1.0)
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
        ing_mensual = [4200/12 * 28 * FENOLOGICA['Lechuga (NFT)'].get(m, 1.0) for m in MESES]
        fig_hidro = go.Figure([go.Bar(x=MESES, y=ing_mensual, marker_color=[GREEN if v > 9000 else AMBER for v in ing_mensual]), go.Scatter(x=MESES, y=[TOTAL_CF/12]*12, line=dict(color=RED, dash='dash'), mode='lines')])
        fig_hidro.update_layout(title="Ingreso Mensual — Lechuga Hidroponica NFT", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=320)
        
        fig_comp = px.pie(names=['Insumos hidro', 'Riego Higo', 'MO Higo', 'Fertiliz. Higo', 'Empaque Higo'], values=[35700, 3800, 6200, 5500, 2300], title="Composicion de Costos Variables")
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=320)
        return html.Div([html.Div([kpi_card("Ingreso Anual Lechuga", fmt(INGRESOS["Venta de Lechuga Hidroponica (4,200 kg x $28.00/kg)"]), "4,200 kg", GREEN), kpi_card("Costo Insumos Hidro", fmt(35700), "Nutrientes + Semillas", AMBER), kpi_card("Margen Neto Hidro", fmt(117600-35700), "Operativo", CYAN)], style={'display':'flex','gap':'12px','marginBottom':'20px'}), html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}, children=[html.Div([dcc.Graph(figure=fig_hidro)], style={'background':CARD}), html.Div([dcc.Graph(figure=fig_comp)], style={'background':CARD})])])

    elif tab == 'tab-dictamen':
        df_dict = generar_dictamen_completo(municipio, mes, anio_range[0], anio_range[1])
        if df_dict.empty: return html.P("Sin datos para el rango seleccionado.", style={'color':AMBER})
        fig_dict = px.line(df_dict, x='Anio', y='ICC', color='Cultivo', line_dash='Tipo', title="Evolucion ICC", markers=True)
        fig_dict.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#fff', height=380)
        
        tbl2 = html.Table([
            html.Thead(html.Tr(list(map(lambda h: html.Th(h), ['Anio','Cultivo','Tipo','Vol. (t)','PMR ($/t)','Costo Ajust.','Utilidad Neta','ICC (pts)','Estatus'])), style={'background':BORDER})),
            html.Tbody(list(map(lambda r: html.Tr([html.Td(str(r['Anio']), style={'color': CYAN if r['Tipo']=='Proyeccion Monte Carlo' else '#fff'}), html.Td(r['Cultivo']), html.Td(r['Tipo'], style={'fontSize':'11px','color':'#aaa'}), html.Td(f"{r['Volumen_t']:,.2f}"), html.Td(f"${r['PMR']:,.2f}"), html.Td(fmt(r['Costo_Ajustado'])), html.Td(fmt(r['Utilidad_Neta']), style={'color': GREEN if r['Utilidad_Neta']>0 else RED}), html.Td(f"{r['ICC']:,.0f}"), html.Td(r['Estatus'], style={'color': '#fff','fontWeight':'700','fontSize':'11px','background': '#1a4a1a' if r['Estatus']=='Alta Competitividad' else '#4a0a0a','padding':'2px 6px','borderRadius':'4px'})]), df_dict.to_dict('records')))),
        ], style={'width':'100%','borderCollapse':'collapse','fontSize':'12px'})
        return html.Div([grafico_card(fig_dict), html.Div([tbl2], style={'background':CARD,'padding':'16px'})])
    return html.Div("Selecciona una pestaña")

def _get_mc_stats(municipio, mes):
    row_mun = df_municipios[df_municipios['nombre'] == municipio].iloc[0]
    mr, mc_m, mk = row_mun['mod_rendimiento'], row_mun['mod_costo'], row_mun['mod_riesgo']
    mb_h = FENOLOGICA['Higo'].get(mes, 1.0)
    pf_h = np.random.normal(PRECIO_BASE['Higo']*mb_h, PRECIO_BASE['Higo']*0.12*max(mb_h,0.1), 5000)
    utils_h = (6.82*mr*mb_h)*(pf_h*1.15) - 105100*mc_m + (117600 - 35536)
    icc_h = utils_h*(1 - 0.08*mk)
    return mr, mc_m, (np.sum(icc_h>0)/5000)*100, float(np.mean(icc_h))

@app.callback(Output('dl-pdf-mensual','data'), Input('btn-pdf-mensual','n_clicks'), State('dd-municipio','value'), State('dd-mes','value'), prevent_initial_call=True)
def descargar_pdf_mensual(n, municipio, mes):
    if not n: return None
    mr, mc_m, pe, icc = _get_mc_stats(municipio, mes)
    return dict(content=base64.b64encode(generar_pdf_reporte(municipio, mes, mr, mc_m, pe, icc, modo='mensual')).decode(), filename=f"reporte_mensual_{municipio}_{mes}.pdf", type="application/pdf", base64=True)

@app.callback(Output('dl-pdf-anual','data'), Input('btn-pdf-anual','n_clicks'), State('dd-municipio','value'), State('dd-mes','value'), prevent_initial_call=True)
def descargar_pdf_anual(n, municipio, mes):
    if not n: return None
    mr, mc_m, pe, icc = _get_mc_stats(municipio, mes)
    df_dict = generar_dictamen_completo(municipio, mes, 2018, 2026)
    return dict(content=base64.b64encode(generar_pdf_reporte(municipio, mes, mr, mc_m, pe, icc, modo='anual', df_dictamen=df_dict)).decode(), filename=f"reporte_anual_{municipio}.pdf", type="application/pdf", base64=True)

@app.callback(Output('dl-csv-mensual','data'), Input('btn-csv-mensual','n_clicks'), State('dd-municipio','value'), State('dd-mes','value'), prevent_initial_call=True)
def descargar_csv_mensual(n, municipio, mes):
    if not n: return None
    return dict(content=base64.b64encode(generar_csv(generar_csv_mensual(municipio, mes))).decode(), filename=f"reporte_mensual_{municipio}_{mes}.csv", type="text/csv", base64=True)

@app.callback(Output('dl-csv-anual','data'), Input('btn-csv-anual','n_clicks'), State('dd-municipio','value'), State('dd-mes','value'), prevent_initial_call=True)
def descargar_csv_anual(n, municipio, mes):
    if not n: return None
    return dict(content=base64.b64encode(generar_csv(generar_dictamen_completo(municipio, mes, 2018, 2026))).decode(), filename=f"reporte_anual_{municipio}.csv", type="text/csv", base64=True)

if __name__ == '__main__':
    app.run(debug=True, port=8050)
    