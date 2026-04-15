import pandas as pd
from database import obtener_conexion
from procesamiento import generar_resumen_estadistico

def iniciar_proceso():
    # Inicializa el motor de conexión a la base de datos
    engine = obtener_conexion()
    
    # Extrae mediante SQL el histórico de cultivos y sus precios desde MySQL
    df_siap = pd.read_sql("SELECT Nomcultivo, Preciomediorural FROM Historico_Mercado", con=engine)
    
    # Verifica que el DataFrame contenga información antes de iniciar el procesamiento
    if not df_siap.empty:
        # Ejecuta la lógica de agregación estadística definida en el módulo de procesamiento
        df_final = generar_resumen_estadistico(df_siap)
        
        # Almacena los resultados en una nueva tabla, reemplazándola si ya existe en el servidor
        df_final.to_sql('Resumen_Cultivos', con=engine, if_exists='replace', index=False)
        
# Garantiza que la función principal solo se ejecute si el script es llamado directamente
if __name__ == "__main__":
    iniciar_proceso()  # Ejecuta el proceso ETL completo