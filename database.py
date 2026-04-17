import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Construye la ruta absoluta al archivo .env basándose en la ubicación de este archivo (database.py),
# garantizando que load_dotenv lo encuentre sin importar desde qué directorio se ejecute el script
ruta_env = os.path.join(os.path.dirname(__file__), '.env')
# Carga las variables de entorno desde el archivo .env
load_dotenv(dotenv_path=ruta_env)

def obtener_conexion():
    # Obtiene las credenciales de la base de datos desde las variables de entorno
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    bd = os.getenv("DB_NAME")
    
    # Escapa caracteres especiales de la contraseña (ej: '@', '#') para que no rompan el parseo de la URL
    contrasena_codificada = quote_plus(contrasena)
    # Construye la URL de conexión para MySQL usando pymysql como driver
    url = f"mysql+pymysql://{usuario}:{contrasena_codificada}@{host}:3306/{bd}"
    # Crea y retorna el motor de conexión SQLAlchemy
    return create_engine(url)

def obtener_conexion_agro():
    # Obtiene las credenciales de la base de datos agro desde las variables de entorno
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    bd = os.getenv("DB_NAME_AGRO")
    
    # Escapa caracteres especiales de la contraseña (ej: '@', '#') para que no rompan el parseo de la URL
    contrasena_codificada = quote_plus(contrasena)
    # Construye la URL de conexión para la base de datos agro
    url = f"mysql+pymysql://{usuario}:{contrasena_codificada}@{host}:3306/{bd}"
    # Crea y retorna el motor de conexión SQLAlchemy para la BD agro
    return create_engine(url)