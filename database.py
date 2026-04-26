import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

ruta_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ruta_env)

def obtener_conexion():
    usuario = os.getenv("DB_USER")
    contrasena = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    bd = os.getenv("DB_NAME")
    
    url = f"mysql+pymysql://{usuario}:{contrasena}@{host}:3306/{bd}"
    return create_engine(url)