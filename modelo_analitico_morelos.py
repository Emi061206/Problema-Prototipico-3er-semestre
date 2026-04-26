# Importación de librerías para el manejo de estructuras de datos y conectividad
import pandas as pd
import mysql.connector

# Definición del diccionario de datos basado en los registros oficiales de campo (SIAP/SEDAGRO)
data_morelos = {
    # Municipios focalizados para el análisis de diversificación
    'municipio': ['Jiutepec', 'Cuautla', 'Temixco'],
    # Especies evaluadas: tradicionales (Maíz) vs. alta rentabilidad (Higo)
    'cultivo': ['Maíz Grano', 'Higo', 'Caña de Azúcar'],
    # Cifras de rendimiento en toneladas por hectárea (t/ha) extraídas del cierre agrícola
    'rendimiento': [3.5, 12.0, 110.0],
    # Cotización del Precio Medio Rural (PMR) por tonelada
    'precio_ton': [5516.0, 31496.0, 1200.0],
    # Costo operativo total por hectárea según el incidente crítico de contabilidad
    'costo_ha': [41000.0, 65000.0, 55000.0]
}

# Creación del DataFrame de Pandas para el procesamiento analítico vectorizado
df = pd.DataFrame(data_morelos)

# Cálculo de la facturación bruta (Ingreso Total) por hectárea
df['ingreso_total'] = df['rendimiento'] * df['precio_ton']

# Cálculo de la utilidad marginal (Rentabilidad Neta) restando el costo operativo
df['rentabilidad_neta'] = df['ingreso_total'] - df['costo_ha']

# Definición de la lógica de negocio para la clasificación algorítmica de los predios
def recomendar_diversificacion(row):
    # Identificación de escenarios de insolvencia financiera (pérdida económica)
    if row['rentabilidad_neta'] < 0:
        return "Diversificación Urgente (Cultivo no rentable)"
    # Identificación de escenarios de éxito económico (ganancia superior a $50,000)
    elif row['rentabilidad_neta'] > 50000:
        return "Cultivo de Alta Rentabilidad"
    # Clasificación de cultivos con margen positivo pero bajo potencial de crecimiento
    else:
        return "Mantenimiento con Optimización"

# Aplicación de la función sobre el DataFrame para generar la columna de estatus
df['estatus'] = df.apply(recomendar_diversificacion, axis=1)

# Despliegue de los resultados sintetizados para el reporte ejecutivo
print(df[['municipio', 'cultivo', 'rentabilidad_neta', 'estatus']])