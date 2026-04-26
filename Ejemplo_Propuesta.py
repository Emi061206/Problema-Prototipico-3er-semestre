import numpy as np
import pandas as pd

def evaluar_viabilidad_cultivos(cultivos, rendimiento, precio, costo, prima, temporalidad, riesgo):
    precio_sostenible = precio * (1 + prima)
    ingreso = rendimiento * precio_sostenible
    utilidad = ingreso - costo
    icc = utilidad * temporalidad * (1 - riesgo)
    
    condiciones = [icc > 80000, icc > 40000]
    decisiones = ["Conviene invertir", "Riesgo moderado"]
    recomendacion = np.select(condiciones, decisiones, default="No conviene invertir")
    
    resultados = pd.DataFrame({
        'Cultivo': cultivos,
        'Precio_Sost_($)': np.round(precio_sostenible, 2),
        'Ingreso_Bruto_($)': np.round(ingreso, 2),
        'Utilidad_Neta_($)': np.round(utilidad, 2),
        'ICC': np.round(icc, 2),
        'Decision_Algoritmica': recomendacion
    })
    
    return resultados

cultivos_morelos = np.array(["Aguacate Hass", "Zarzamora", "Jitomate Saladet"])
rendimiento_kg = np.array([12000, 8000, 45000])
precio_base = np.array([45, 80, 15])
costo_operativo = np.array([150000, 200000, 120000])
prima_sostenibilidad = np.array([0.15, 0.20, 0.10])
factor_temporalidad = np.array([1.0, 1.1, 0.9])
riesgo_probabilidad = np.array([0.15, 0.25, 0.30])

reporte_financiero = evaluar_viabilidad_cultivos(
    cultivos_morelos, 
    rendimiento_kg, 
    precio_base, 
    costo_operativo, 
    prima_sostenibilidad, 
    factor_temporalidad, 
    riesgo_probabilidad
)

print(reporte_financiero.to_string(index=False)) 