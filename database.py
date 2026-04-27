# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO DE CONEXIÓN A BASE DE DATOS
# Gestiona la conexión segura a MySQL usando variables de entorno,
# evitando exponer credenciales directamente en el código fuente.
# ──────────────────────────────────────────────────────────────────────────────

import os                              # Permite leer variables del sistema operativo y rutas de archivos
from urllib.parse import quote_plus    # Codifica caracteres especiales en la contraseña para que la URL sea válida
from sqlalchemy import create_engine   # Crea el motor de conexión compatible con Pandas y SQLAlchemy
from dotenv import load_dotenv         # Carga variables de entorno desde un archivo .env al entorno del proceso

# Construye la ruta absoluta al archivo .env que está en el mismo directorio que este script.
# Usar __file__ garantiza que funcione independientemente del directorio de trabajo actual.
ruta_env = os.path.join(os.path.dirname(__file__), '.env')

# Carga el archivo .env para que sus variables queden disponibles mediante os.getenv()
load_dotenv(dotenv_path=ruta_env)

def obtener_conexion():
    """
    Construye y retorna un motor de conexión a la base de datos MySQL.

    Lee las credenciales desde variables de entorno para mantener la seguridad.
    La contraseña se codifica con quote_plus para manejar caracteres especiales
    como '@', '/', '!' que romperían el formato de la URL de conexión.

    Returns:
        sqlalchemy.engine.Engine: Motor listo para ejecutar consultas SQL
                                  con Pandas (read_sql) o SQLAlchemy directamente.
    """
    # Lee el nombre de usuario de la base de datos desde la variable de entorno DB_USER
    usuario = os.getenv("DB_USER")

    # Lee la contraseña y la codifica para que los caracteres especiales no rompan la URL
    contrasena = quote_plus(os.getenv("DB_PASSWORD"))

    # Lee la dirección del servidor de base de datos (ej. "localhost" o una IP)
    host = os.getenv("DB_HOST")

    # Lee el nombre de la base de datos a la que se conectará
    bd = os.getenv("DB_NAME")

    # Arma la cadena de conexión en formato URL estándar de SQLAlchemy para MySQL con PyMySQL:
    # mysql+pymysql://<usuario>:<contraseña>@<host>:3306/<nombre_bd>
    url = f"mysql+pymysql://{usuario}:{contrasena}@{host}:3306/{bd}"

    # Crea y retorna el motor de conexión listo para ser usado en consultas
    return create_engine(url)