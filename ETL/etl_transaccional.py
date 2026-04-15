from sqlalchemy import text
from database import obtener_conexion_agro

def registrar_productor(nombre_chinampa, coordenadas, cultivo_principal):
    # Obtiene la conexión a la base de datos agro usando SQLAlchemy
    engine = obtener_conexion_agro()
    
    # Define la consulta SQL parametrizada para insertar un nuevo productor
    query = text("""
        INSERT INTO Productores (Nombre_Chinampa, Ubicacion_Coordenadas, Cultivo_Principal, Fecha_Registro)
        VALUES (:nombre, :coordenadas, :cultivo, CURDATE())
    """)
    
    # Ejecuta la consulta usando un contexto de conexión
    with engine.connect() as conn:
        # Ejecuta la consulta con los parámetros proporcionados
        conn.execute(query, {"nombre": nombre_chinampa, "coordenadas": coordenadas, "cultivo": cultivo_principal})
        # Confirma la transacción en la base de datos
        conn.commit()

# Bloque principal que se ejecuta solo si el script es llamado directamente
if __name__ == "__main__":
    # Llama a la función con datos de ejemplo para probar el registro
    registrar_productor("Chinampa Piloto Prueba", "19.2635, -99.0945", "Lechuga Hidropónica")