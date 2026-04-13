import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Define la ruta hacia la subcarpeta donde reside el archivo de configuración
ruta_env = os.path.join('Modelo', '.env')

# Carga las variables de entorno desde la ubicación específica especificada
load_dotenv(dotenv_path=ruta_env)

def obtener_conexion():
    # Recupera las credenciales de acceso desde el entorno del sistema
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    bd = os.getenv("DB_NAME")
    
    # Estructura la cadena de conexión para el driver de MySQL
    url = f"mysql+pymysql://{usuario}:{contrasena}@{host}:3306/{bd}"
    
    # Genera el motor de conexión para interactuar con la base de datos
    return create_engine(url)