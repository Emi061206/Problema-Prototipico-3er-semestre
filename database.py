import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carga las variables de entorno definidas en el archivo .env
load_dotenv()

def obtener_conexion():
    # Extrae las credenciales del sistema para no exponerlas directamente en el código
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    bd = os.getenv("DB_NAME")
    
    # Construye la URL de conexión necesaria para el dialecto MySQL y el driver PyMySQL
    url = f"mysql+pymysql://{usuario}:{contrasena}@{host}:3306/{bd}"
    
    # Crea y retorna el motor de conexión (engine) de SQLAlchemy
    return create_engine(url)