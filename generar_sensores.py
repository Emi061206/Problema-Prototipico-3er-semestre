# Importamos pandas para la manipulación y análisis de datos (en este caso, archivos CSV)
import pandas as pd
# Importamos os para interactuar con el sistema operativo, específicamente para manejar rutas de archivos
import os
# Importamos create_engine de sqlalchemy para crear una conexión a la base de datos
from sqlalchemy import create_engine
# Importamos load_dotenv de python-dotenv para cargar las variables de entorno desde un archivo .env
from dotenv import load_dotenv

# Construimos la ruta absoluta al archivo .env ubicado en el subdirectorio 'Modelo'
ruta_env = os.path.join(os.path.dirname(__file__), 'Modelo', '.env')
# Cargamos las variables de entorno definidas en el archivo .env en el entorno actual
load_dotenv(ruta_env)

# Obtenemos las credenciales y detalles de conexión a la base de datos de las variables de entorno
usuario = os.getenv("DB_USER")
contrasena = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
bd = os.getenv("DB_NAME")

# Creamos el motor de conexión a la base de datos MySQL utilizando pymysql como conector
engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{host}:3306/{bd}")

# Definimos la ruta absoluta donde se encuentra el archivo CSV con las lecturas reales de los sensores
ruta_sensores_reales = r"C:\Users\Dell\Desktop\Problema prototipico 3er semestre\Liempeza de Datos\Datos Limpios\lecturas_reales_iot.csv"

try:
    # Leemos el archivo CSV usando pandas y almacenamos la información en un DataFrame
    df_sensores = pd.read_csv(ruta_sensores_reales)
    # Convertimos la columna 'Fecha_Hora' a un formato datetime para asegurar compatibilidad en la base de datos
    df_sensores['Fecha_Hora'] = pd.to_datetime(df_sensores['Fecha_Hora'])
    # Insertamos los datos del DataFrame en la tabla 'Sensores_IoT' de la base de datos
    # 'if_exists="append"' indica que si la tabla ya existe, debe agregar nuevos registros y no eliminar la tabla
    # 'index=False' evita que se agregue el índice del DataFrame (las filas 0, 1, 2...) como una columna en la tabla
    df_sensores.to_sql(name='Sensores_IoT', con=engine, if_exists='append', index=False)
    print("Datos reales inyectados con éxito en la base de datos.")
except FileNotFoundError:
    # Este bloque maneja un error en caso de que el archivo CSV no exista en la ruta proporcionada
    print("El archivo de lecturas reales aún no existe. El sistema está en espera de la conexión de hardware.")
except Exception as e:
    # Se captura y notifica cualquier otro tipo de error al intentar ejecutar el proceso (ej., problemas de conexión con DB)
    print(f"Ocurrió un error en la ejecución: {e}")