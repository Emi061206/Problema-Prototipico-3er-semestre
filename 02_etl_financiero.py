# Importación del módulo para la ejecución veloz de arreglos algebraicos en múltiples dimensiones.
import numpy as np
# Importación del módulo estándar en Ciencia de Datos para la manipulación tabular y analítica.
import pandas as pd
# Importación del puente lógico que permite la transmisión de datos desde el motor MySQL local.
import mysql.connector

# Definición funcional estricta: se conecta, lee la tabla y retorna una estructura Pandas pura.
def extraer_datos_financieros() -> pd.DataFrame:
    # Cadena que contiene la instrucción SQL de lectura masiva (Data Query Language).
    query = "SELECT * FROM catalogo_cultivos"
    
    # Manejador de contexto que levanta la conexión y garantiza el cierre del puerto al terminar.
    with mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="2815melp@2cz", 
        database="sistema_agricola_morelos"
    ) as conn:
        # Ingesta automatizada del resultado de la base de datos hacia el bloque de memoria RAM del DataFrame.
        df_cultivos = pd.read_sql(query, conn)
        
    # Salida controlada de la función entregando los datos.
    return df_cultivos

# Función matemática de alto nivel que recibe y entrega DataFrames operando sin bucles iterativos.
def evaluar_viabilidad_cultivos(df: pd.DataFrame) -> pd.DataFrame:
    # Ajuste dinámico del precio aplicando la fórmula de rentabilidad sobre un vector completo.
    precio_sostenible = df['precio_base'] * (1 + df['prima_sostenibilidad'])
    
    # Cálculo de la facturación bruta proyectada multiplicando el volumen por el nuevo precio.
    ingreso = df['rendimiento_kg_esperado'] * precio_sostenible
    
    # Determinación del margen financiero descontando la inversión inicial y operativa.
    utilidad = ingreso - df['costo_operativo']
    
    # Generación de una matriz de la misma longitud del catálogo, llenada de "unos" para neutralidad de temporada.
    temporalidad_simulada = np.ones(len(df))
    
    # Ecuación central del modelo probabilístico que castiga las ganancias netas basadas en el riesgo.
    icc = utilidad * temporalidad_simulada * (1 - df['riesgo_probabilidad'])
    
    # Creación de una lista de matrices booleanas marcando si el índice supera los umbrales seguros o medios.
    condiciones = [icc > 80000, icc > 40000]
    
    # Creación de la lista de etiquetas de negocio directamente correspondientes a las condiciones previas.
    decisiones = ["Conviene invertir", "Riesgo moderado"]
    
    # Evaluación vectorizada simultánea: compara fila por fila y asigna la recomendación o cae en el default.
    recomendacion = np.select(condiciones, decisiones, default="No conviene invertir")
    
    # Construcción de un nuevo DataFrame sintetizado orientado a la toma de decisiones ejecutivas.
    df_resultados = pd.DataFrame({
        # Se mapea el nombre del producto desde el marco original.
        'Cultivo': df['nombre_cultivo'],
        # Se redondea matemáticamente el índice a dos cifras decimales para reportes contables.
        'ICC': np.round(icc, 2),
        # Se adjunta el resultado del árbol de decisiones algorítmico.
        'Decision_Algoritmica': recomendacion
    })
    
    # Retorno de la matriz sintética resultante de las operaciones contables y de probabilidad.
    return df_resultados