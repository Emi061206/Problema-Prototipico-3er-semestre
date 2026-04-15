import pandas as pd
import glob
import os


## PASO 1: DEFINICIÓN DE RUTAS Y PARÁMETROS

# Definimos las rutas exactas donde están los datos sucios y dónde queremos los limpios.
# Se usa 'r' antes de la comilla para que Python lea correctamente las diagonales invertidas (\) de Windows.
ruta_entrada = r"C:\Users\Dell\Desktop\Problema prototipico 3er semestre\Liempeza de Datos"
ruta_salida = r"C:\Users\Dell\Desktop\Problema prototipico 3er semestre\Liempeza de Datos\Datos Limpios"

# os.makedirs verifica si la carpeta de salida existe; si no, la crea automáticamente.
os.makedirs(ruta_salida, exist_ok=True)

estado_objetivo = "Ciudad de México"
municipio_objetivo = "Xochimilco"
# Modifica esta línea en tu archivo main.py
lista_cultivos = ["Lechuga", "Espinaca", "Cilantro", "Rábano", "Flor de muerto (Cempasúchil)", "Apio"]

## PASO 2: BÚSQUEDA DE ARCHIVOS (USO DE GLOB Y OS)

# os.path.join une la ruta de la carpeta con el texto "Cierre_agricola_mun_*.csv".
# Esto asegura que la ruta se construya sin errores, sin importar el sistema operativo.
patron_archivos = os.path.join(ruta_entrada, "Cierre_agricola_mun_*.csv")

# glob.glob actúa como un buscador. Toma el patrón anterior y devuelve una lista 
# con todos los archivos en la carpeta que terminan en .csv y empiezan con ese nombre.
archivos_csv = glob.glob(patron_archivos)

# Creamos una lista vacía donde guardaremos los datos filtrados de cada año.
dataframes_procesados = []

## PASO 3: LIMPIEZA BÁSICA Y FILTRADO ITERATIVO

for archivo in archivos_csv:
    # Cargamos el archivo especificando la codificación 'latin1' para leer acentos y eñes correctamente.
    datos = pd.read_csv(archivo, encoding='latin1', low_memory=False)

    # Limpiamos los nombres de las columnas (quitamos espacios invisibles y ponemos mayúscula inicial).
    datos.columns = datos.columns.str.strip().str.capitalize()

    # Estandarizamos los nombres de las columnas que el SIAP cambió a través de los años.
    if 'Precio' in datos.columns:
        datos = datos.rename(columns={'Precio': 'Preciomediorural'})
    if 'Nomcultivo sin um' in datos.columns:
        datos = datos.rename(columns={'Nomcultivo sin um': 'Nomcultivo'})

    # Filtramos por estado y municipio usando máscaras booleanas.
    filtro_geo = (datos['Nomestado'].str.contains(estado_objetivo, case=False, na=False)) & \
                 (datos['Nommunicipio'].str.contains(municipio_objetivo, case=False, na=False))
    
    # Filtramos para conservar únicamente los cultivos de nuestra lista.
    filtro_cultivos = datos['Nomcultivo'].isin(lista_cultivos)

    # Aplicamos los filtros a la base de datos.
    datos_filtrados = datos[filtro_geo & filtro_cultivos]

    # Seleccionamos solo las columnas financieras y operativas que nos interesan para el ICC.
    columnas_necesarias = ['Anio', 'Nomcultivo', 'Volumenproduccion', 'Rendimiento', 'Preciomediorural']

    # Si encontramos datos útiles en este año, los agregamos a nuestra lista.
    if not datos_filtrados.empty:
        df_final = datos_filtrados[columnas_necesarias].copy()
        dataframes_procesados.append(df_final)


## PASO 4: CONSOLIDACIÓN Y EXPORTACIÓN

# Verificamos si logramos extraer datos de los archivos.
if dataframes_procesados:
    # Unimos todos los fragmentos anuales en un solo DataFrame general.
    df_historico = pd.concat(dataframes_procesados, ignore_index=True)

    # Definimos cómo se llamará el archivo limpio y dónde se guardará usando os.path.join.
    archivo_salida = os.path.join(ruta_salida, "Historico_Xochimilco_Limpio.csv")

    # Exportamos el DataFrame limpio a formato CSV (utf-8-sig para compatibilidad con Excel).
    df_historico.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    print(f"\n Limpieza completada con éxito.")
    print(f"Archivo guardado en: {archivo_salida}\n")

    # Obtenemos un resumen de los datos extraídos (similar al .describe() de tu archivo de artistas).
    print("Muestra de los datos limpios obtenidos:")
    print(df_historico.head())
else:
    print("Error. No se encontraron datos que coincidan con los filtros en la carpeta de origen.")