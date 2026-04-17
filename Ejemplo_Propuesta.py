import numpy as np

def calcular_indicadores_icc():
    cultivos = ["Jitomate chery", "Albahaca", "Lechuga"]
    
    rendimiento = np.array([5000, 3000, 4000])
    precio = np.array([20, 35, 12])
    costo = np.array([60000, 40000, 35000])
    prima = np.array([0.25, 0.20, 0.10])
    temporalidad = np.array([1.1, 1.0, 0.9])
    riesgo = np.array([0.2, 0.25, 0.3])
    
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
             
    epoca_optima_idx = np.array([4, 2, 9])
    
    precio_con_prima = precio * (1 + prima)
    ingresos_esperados = rendimiento * precio_con_prima * temporalidad
    utilidad_neta = ingresos_esperados - costo
    icc = (utilidad_neta / costo) * (1 - riesgo)
    
    condiciones = [icc > 0.5, (icc >= 0) & (icc <= 0.5), icc < 0]
    decisiones = ["Altamente Viable", "Viabilidad Moderada", "No Viable"]
    # Se especifica default como string para compatibilidad con NumPy 2.x (evita error de dtype mixto int/str)
    decision_final = np.select(condiciones, decisiones, default='No Definido')
    
    resultados_financieros = []
    
    for i in range(len(cultivos)):
        registro = {
            "nombre_cultivo": cultivos[i],
            "precio_sostenible": round(precio_con_prima[i], 2),
            "ingreso_proyectado": round(ingresos_esperados[i], 2),
            "utilidad_neta": round(utilidad_neta[i], 2),
            "indice_icc": round(icc[i], 2),
            "recomendacion": decision_final[i],
            "mes_ideal": meses[epoca_optima_idx[i]]
        }
        resultados_financieros.append(registro)
        
    return resultados_financieros

print(calcular_indicadores_icc())
