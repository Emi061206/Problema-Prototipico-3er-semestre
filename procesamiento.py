import pandas as pd

def generar_resumen_estadistico(df):
    # Agrupa los datos por tipo de cultivo y calcula métricas descriptivas del precio rural
    resumen = df.groupby('Nombre_Cultivo')['Precio_Medio_Rural'].agg([
        'mean',   # Obtiene el promedio histórico de precios por cultivo
        'min',    # Identifica el valor mínimo registrado por cultivo
        'max',    # Identifica el valor máximo registrado por cultivo
        'count'   # Contabiliza el número total de registros por cultivo
    ]).reset_index()  # Convierte el índice agrupado en columna
    
    # Renombra las columnas resultantes para facilitar su lectura en la base de datos
    resumen.columns = [
        'Nombre_Cultivo',      # Nombre del cultivo
        'Precio_Promedio',     # Precio promedio histórico
        'Precio_Minimo',       # Precio mínimo histórico
        'Precio_Maximo',       # Precio máximo histórico
        'Registros_Historicos' # Número de registros disponibles
    ]
    
    return resumen  # Retorna el DataFrame con el resumen estadístico+¿´+}