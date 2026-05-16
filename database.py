import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def obtener_motor_mysql():
    usuario = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))  # Codifica caracteres especiales como '@', '#', etc.
    host = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT", "3306")
    base_datos = os.getenv("DB_NAME")
    
    url_conexion = f"mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{base_datos}"
    
    return create_engine(url_conexion)