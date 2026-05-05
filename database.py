# Carga de librerías para variables de entorno y creación de engines SQLAlchemy.
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Localiza el archivo .env junto a este script y carga sus variables.
ruta_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ruta_env)

def obtener_conexion():
    # Obtiene el usuario de la base de datos desde las variables de entorno.
    usuario = os.getenv("DB_USER")
    contrasena = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT", "3306")
    bd = os.getenv("DB_NAME")
    
    # Ensambla la cadena de conexión con usuario, contraseña, host, puerto y base de datos.
    url = f"mysql+pymysql://{usuario}:{contrasena}@{host}:{puerto}/{bd}"
    
    return create_engine(url)