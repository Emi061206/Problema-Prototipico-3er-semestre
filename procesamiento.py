import pandas as pd

def generar_resumen_estadistico(df):
    # Agrupa los datos por tipo de cultivo y calcula métricas descriptivas del precio rural
    resumen = df.groupby('Nomcultivo')['Preciomediorural'].agg([
        'mean',   # Obtiene el promedio histórico de precios
        'min',    # Identifica el valor mínimo registrado
        'max',    # Identifica el valor máximo registrado
        'count'   # Contabiliza el número total de registros por cultivo
    ]).reset_index()
    
    # Renombra las columnas resultantes para facilitar su lectura en la base de datos
    resumen.columns = [
        'Nombre_Cultivo', 
        'Precio_Promedio', 
        'Precio_Minimo', 
        'Precio_Maximo', 
        'Registros_Historicos'
    ]
    
    return resumen