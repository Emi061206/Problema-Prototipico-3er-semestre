import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, ".env"))

def obtener_motor_mysql():
    usuario = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))  # Codifica caracteres especiales como '@', '#', etc.
    host = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT", "3306")
    base_datos = os.getenv("DB_NAME")

    missing = [name for name, value in (
        ("DB_USER", usuario),
        ("DB_HOST", host),
        ("DB_NAME", base_datos),
    ) if not value]
    if missing:
        raise RuntimeError(
            "Faltan variables de entorno para la conexión MySQL: "
            + ", ".join(missing)
            + ". Configure un archivo .env o el entorno antes de ejecutar la aplicación."
        )

    url_conexion = f"mysql+mysqlconnector://{usuario}:{password}@{host}:{puerto}/{base_datos}"

    return create_engine(url_conexion, pool_pre_ping=True)
