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
    
    decision_final = np.select(condiciones, decisiones, default='No Definido')
    
    # Implementación Pythónica mediante comprensión de listas y zip
    # Sustituye el ciclo for basado en índices para mayor eficiencia
    resultados_financieros = [
        {
            "nombre_cultivo": c,
            "precio_sostenible": round(p_p, 2),
            "ingreso_proyectado": round(i_e, 2),
            "utilidad_neta": round(u_n, 2),
            "indice_icc": round(i_c, 2),
            "recomendacion": d_f,
            "mes_ideal": meses[idx]
        }
        for c, p_p, i_e, u_n, i_c, d_f, idx in zip(
            cultivos, precio_con_prima, ingresos_esperados, utilidad_neta, icc, decision_final, epoca_optima_idx
        )
    ]
        
    return resultados_financieros

if __name__ == "__main__":
    for resultado in calcular_indicadores_icc():
        print(resultado)