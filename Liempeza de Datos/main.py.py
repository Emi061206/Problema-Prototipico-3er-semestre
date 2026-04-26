import pandas as pd
import glob
import os

def limpiar_datos_morelos(ruta_entrada, ruta_salida):
    os.makedirs(ruta_salida, exist_ok=True)
    patron = os.path.join(ruta_entrada, "Cierre_agricola_mun_*.csv")
    archivos = glob.glob(patron)
    
    estado_objetivo = "Morelos"
    municipios_objetivo = ["Jiutepec", "Cuautla", "Temixco"]
    lista_cultivos = [
        "Caña de azúcar", 
        "Aguacate", 
        "Jitomate Saladet", 
        "Higo", 
        "Maíz grano", 
        "Sorgo grano",
        "Nopal"
    ]
    
    mapeo_columnas = {
        'Nomcultivo Sin Um': 'Nomcultivo',
        'Precio': 'Preciomediorural'
    }

    dataframes_procesados = []

    for archivo in archivos:
        try:
            df = pd.read_csv(archivo, encoding='latin-1')
            df = df.rename(columns=mapeo_columnas)
            
            columnas_presentes = df.columns
            if 'Nomestado' not in columnas_presentes or 'Nommunicipio' not in columnas_presentes:
                continue
                
            filtro = (
                (df['Nomestado'] == estado_objetivo) & 
                (df['Nommunicipio'].isin(municipios_objetivo)) & 
                (df['Nomcultivo'].isin(lista_cultivos))
            )
            
            columnas_finales = [
                'Anio', 'Nomestado', 'Nommunicipio', 'Nomcultivo', 
                'Volumenproduccion', 'Rendimiento', 'Preciomediorural'
            ]
            
            columnas_existentes = [col for col in columnas_finales if col in df.columns]
            df_filtrado = df.loc[filtro, columnas_existentes].copy()
            
            if not df_filtrado.empty:
                dataframes_procesados.append(df_filtrado)
                
        except Exception as e:
            print(f"Error procesando {os.path.basename(archivo)}: {e}")

    if dataframes_procesados:
        df_historico = pd.concat(dataframes_procesados, ignore_index=True)
        archivo_salida = os.path.join(ruta_salida, "Historico_Morelos_Focalizado.csv")
        df_historico.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        return archivo_salida
    
    return None

if __name__ == "__main__":
    PATH_INPUT = r"C:\Users\Dell\Desktop\Problema prototipico 3er semestre\Liempeza de Datos"
    PATH_OUTPUT = r"C:\Users\Dell\Desktop\Problema prototipico 3er semestre\Liempeza de Datos\Datos Limpios"
    
    resultado = limpiar_datos_morelos(PATH_INPUT, PATH_OUTPUT)
    if resultado:
        print(f"Archivo generado en: {resultado}")