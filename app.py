# ─── Importaciones ────────────────────────────────────────────────────────────
import os           # Manejo de rutas y sistema de archivos del sistema operativo
import streamlit as st  # Framework para crear la interfaz web interactiva
import pandas as pd     # Manipulación y análisis de datos tabulares (DataFrames)
import numpy as np      # Operaciones numéricas y matemáticas de alto rendimiento

# ─── Configuración inicial de la página ───────────────────────────────────────
# Define el título que aparece en la pestaña del navegador y establece
# el layout en "wide" para aprovechar todo el ancho de la pantalla.
st.set_page_config(page_title="Smart Agroforestry Morelos", layout="wide")

# Título principal visible en la interfaz de la aplicación
st.title("Análisis de Diversificación Agrícola - Morelos")

# Encabezado del panel lateral (sidebar) que contiene los controles de filtro
st.sidebar.header("Filtros de Análisis")

# ─── Carga de datos ───────────────────────────────────────────────────────────
def cargar_datos():
    """
    Lee el archivo CSV con datos históricos agrícolas de Morelos.
    Construye la ruta de forma dinámica para que funcione sin importar
    desde qué directorio se ejecute la aplicación.
    """
    # Obtiene el directorio donde está ubicado este script (app.py)
    directorio_actual = os.path.dirname(__file__)

    # Se le indica a Python que debe entrar a las dos subcarpetas antes de leer el CSV
    ruta_absoluta = os.path.join(
        directorio_actual,
        'Liempeza de Datos',
        'Datos Limpios',
        'Historico_Morelos_Focalizado.csv'
    )

    # Carga el CSV y retorna un DataFrame de pandas listo para su análisis
    return pd.read_csv(ruta_absoluta)

# Llama a la función y almacena los datos en la variable global df
df = cargar_datos()

# ─── Filtro por municipio ─────────────────────────────────────────────────────
# Despliega un menú desplegable en el sidebar con los municipios únicos del dataset.
# El usuario selecciona un municipio y su valor se guarda en 'municipio'.
municipio = st.sidebar.selectbox("Selecciona Municipio", df['Nommunicipio'].unique())

# Filtra el DataFrame original para conservar únicamente las filas
# que correspondan al municipio seleccionado. .copy() evita advertencias
# de pandas al modificar columnas sobre una vista del DataFrame original.
df_filtrado = df[df['Nommunicipio'] == municipio].copy()

# ─── Cálculos de rentabilidad ─────────────────────────────────────────────────
# Subtítulo de la sección, incluye el nombre del municipio seleccionado
st.subheader(f"Proyección de Rentabilidad en {municipio}")

# Ingreso total = Rendimiento del cultivo × Precio medio rural por unidad
df_filtrado['ingreso_total'] = df_filtrado['Rendimiento'] * df_filtrado['Preciomediorural']

# Rentabilidad neta = Ingreso total − Costos fijos estimados (45,000 MXN por hectárea)
df_filtrado['rentabilidad_neta'] = df_filtrado['ingreso_total'] - 45000

# ─── Clasificación de rentabilidad ───────────────────────────────────────────
def clasificar(val):
    """
    Clasifica cada registro según su rentabilidad neta en tres categorías:
      - Diversificación Urgente : rentabilidad negativa (pérdida)
      - Alta Rentabilidad       : ganancia superior a 50,000 MXN
      - Optimización Requerida  : ganancia positiva pero menor a 50,000 MXN
    """
    if val < 0:      return "Diversificación Urgente"
    if val > 50000:  return "Alta Rentabilidad"
    return "Optimización Requerida"

# Aplica la función clasificar a cada fila de 'rentabilidad_neta'
# y almacena el resultado en la columna 'Estatus'
df_filtrado['Estatus'] = df_filtrado['rentabilidad_neta'].apply(clasificar)

# ─── Visualización de la tabla ────────────────────────────────────────────────
# Muestra el DataFrame filtrado en pantalla con formato visual:
# resalta en color la celda con el valor máximo de la columna 'rentabilidad_neta'
st.dataframe(df_filtrado.style.highlight_max(axis=0, subset=['rentabilidad_neta']))