import numpy as np

cultivos = ["Jitomate chery", "Albahaca", "Lechuga"]

# Variables de entrada (Simulación de datos provenientes de BD y sensores)
rendimiento = np.array([5000, 3000, 4000])   
precio = np.array([20, 35, 12])               
costo = np.array([60000, 40000, 35000])       
prima = np.array([0.25, 0.20, 0.10])          
temporalidad = np.array([1.1, 1.0, 0.9])      
riesgo = np.array([0.2, 0.25, 0.3])           

# Datos Históricos de Estacionalidad (Ficticios para el modelo piloto)
# Lógica: Registros de años anteriores que indican el mes con mejores condiciones 
# climáticas y de mercado para cada variedad específica en la región.
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Índices: 2 = Marzo, 4 = Mayo, 10 = Noviembre
epoca_optima_idx = np.array([2, 4, 10]) 

# Cálculos del modelo 
# LÓGICA: Calcula el nuevo precio de venta al aplicar la "Prima de Sostenibilidad".
precio_sostenible = precio * (1 + prima)

# LÓGICA: Proyecta los ingresos brutos multiplicando la producción por el nuevo precio.
ingreso = rendimiento * precio_sostenible

# Lógica: Obtiene la ganancia neta restando todos los costos a los ingresos proyectados.
utilidad = ingreso - costo

# Lógica: Calcula el Indicador de Decisión (ICC). 
# Métrica que pondera utilidad, factor estacional y riesgo de pérdida.
icc = utilidad * temporalidad * (1 - riesgo)

# Evaluación y Generación de Recomendaciones
# Lógica: Mapeo funcional para estructurar los datos finales de cada cultivo 
# sin alterar los arreglos originales de numpy.
def generar_reporte(i):
    if icc[i] > 40000:
        decision = "Conviene invertir"
    elif icc[i] > 20000:
        decision = "Riesgo moderado"
    else:
        decision = "No conviene invertir"
    
    return {
        "nombre": cultivos[i],
        "precio_sos": precio_sostenible[i],
        "ingreso": ingreso[i],
        "utilidad": utilidad[i],
        "icc": icc[i],
        "recomendacion": decision,
        "mes_ideal": meses[epoca_optima_idx[i]]
    }

reportes = list(map(generar_reporte, range(len(cultivos))))

# Salida de datos al usuario
# Lógica: Presenta al agricultor la información financiera junto con la 
# recomendación temporal basada en el histórico de la chinampa.
for r in reportes:
    print(f"\nCultivo: {r['nombre']}")
    print(f"Precio sostenible: ${r['precio_sos']:.2f} (Incluye prima IoT)")
    print(f"Ingreso Proyectado: ${r['ingreso']:,.2f}")
    print(f"Utilidad Neta: ${r['utilidad']:,.2f}")
    print(f"ICC: {r['icc']:.2f}")
    print(f"Época ideal (Histórico): {r['mes_ideal']}")
    print(f"Recomendación Final: {r['recomendacion']}")