# ──────────────────────────────────────────────────────────────────────────────
# EJEMPLO DE PROPUESTA - EVALUADOR DE VIABILIDAD DE CULTIVOS
# Script demostrativo que calcula el Índice de Competitividad del Cultivo (ICC)
# para tres cultivos del estado de Morelos y emite una recomendación de inversión.
# ──────────────────────────────────────────────────────────────────────────────

import numpy as np   # Para operaciones matemáticas vectorizadas sobre arreglos
import pandas as pd  # Para construir y mostrar el reporte como tabla estructurada

def evaluar_viabilidad_cultivos(cultivos, rendimiento, precio, costo, prima, temporalidad, riesgo):
    """
    Evalúa la viabilidad financiera de un conjunto de cultivos y emite
    una recomendación de inversión basada en el ICC calculado.

    Parámetros:
        cultivos     (array): Nombres de los cultivos a evaluar.
        rendimiento  (array): Producción esperada en kg por hectárea.
        precio       (array): Precio base por kg en pesos.
        costo        (array): Costo operativo total por hectárea en pesos.
        prima        (array): Prima de sostenibilidad como proporción (ej. 0.15 = 15%).
        temporalidad (array): Factor estacional que amplifica o reduce el ingreso (1.0 = neutral).
        riesgo       (array): Probabilidad de pérdida o falla del cultivo (0 a 1).

    Returns:
        pd.DataFrame: Tabla con precio sostenible, ingreso bruto, utilidad neta,
                      ICC y recomendación de inversión para cada cultivo.
    """
    # Ajusta el precio incorporando la prima de sostenibilidad:
    # precio_sostenible = precio_base × (1 + prima)
    # Ejemplo: $45/kg × (1 + 0.15) = $51.75/kg
    precio_sostenible = precio * (1 + prima)

    # Calcula el ingreso bruto multiplicando el rendimiento por el precio ajustado
    ingreso = rendimiento * precio_sostenible

    # Obtiene la utilidad neta descontando el costo operativo del ingreso bruto
    utilidad = ingreso - costo

    # Calcula el ICC (Índice de Competitividad del Cultivo):
    # ICC = utilidad × factor_temporal × (1 - riesgo)
    # El factor temporal amplifica o reduce según la época del año.
    # El factor (1 - riesgo) penaliza la utilidad según la probabilidad de pérdida.
    icc = utilidad * temporalidad * (1 - riesgo)

    # Define los umbrales de clasificación:
    # ICC > 80,000 → cultivo muy rentable y seguro
    # ICC > 40,000 → rentabilidad media con riesgo tolerable
    condiciones = [icc > 80000, icc > 40000]

    # Etiquetas que corresponden a cada condición en orden
    decisiones = ["Conviene invertir", "Riesgo moderado"]

    # np.select evalúa las condiciones fila por fila y asigna la etiqueta correspondiente.
    # Si ninguna condición se cumple, usa el valor por defecto "No conviene invertir".
    recomendacion = np.select(condiciones, decisiones, default="No conviene invertir")

    # Construye el DataFrame de resultados con todas las métricas financieras calculadas
    resultados = pd.DataFrame({
        'Cultivo': cultivos,                              # Nombre del cultivo
        'Precio_Sost_($)': np.round(precio_sostenible, 2),  # Precio con prima aplicada
        'Ingreso_Bruto_($)': np.round(ingreso, 2),          # Facturación total antes de costos
        'Utilidad_Neta_($)': np.round(utilidad, 2),         # Ganancia después de restar costos
        'ICC': np.round(icc, 2),                            # Índice ajustado por riesgo y temporalidad
        'Decision_Algoritmica': recomendacion               # Recomendación de inversión
    })

    return resultados


# ──────────────────────────────────────────────────────────────────────────────
# DATOS DE ENTRADA (caso de estudio: tres cultivos de Morelos)
# Fuente: datos representativos del SIAP / SEDAGRO Morelos
# ──────────────────────────────────────────────────────────────────────────────

# Nombres de los cultivos a analizar
cultivos_morelos = np.array(["Aguacate Hass", "Zarzamora", "Jitomate Saladet"])

# Rendimiento esperado en kilogramos por hectárea
rendimiento_kg = np.array([12000, 8000, 45000])

# Precio base por kilogramo en pesos mexicanos
precio_base = np.array([45, 80, 15])

# Costo operativo total por hectárea en pesos (incluye mano de obra, insumos, etc.)
costo_operativo = np.array([150000, 200000, 120000])

# Prima de sostenibilidad: porcentaje adicional al precio por prácticas sustentables
prima_sostenibilidad = np.array([0.15, 0.20, 0.10])

# Factor de temporalidad: ajuste estacional del ingreso (>1 favorece, <1 penaliza)
factor_temporalidad = np.array([1.0, 1.1, 0.9])

# Probabilidad de riesgo del cultivo (pérdidas por clima, plagas, mercado, etc.)
riesgo_probabilidad = np.array([0.15, 0.25, 0.30])


# ──────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN Y REPORTE
# Llama a la función con todos los arreglos de datos y muestra el resultado
# ──────────────────────────────────────────────────────────────────────────────

# Ejecuta la evaluación financiera con todos los parámetros definidos arriba
reporte_financiero = evaluar_viabilidad_cultivos(
    cultivos_morelos,       # Nombres de cultivos
    rendimiento_kg,         # Rendimiento esperado (kg/ha)
    precio_base,            # Precio base por kg
    costo_operativo,        # Costo operativo por ha
    prima_sostenibilidad,   # Prima de sostenibilidad
    factor_temporalidad,    # Factor estacional
    riesgo_probabilidad     # Probabilidad de riesgo
)

# Imprime el reporte completo en consola sin mostrar el índice numérico de filas
print(reporte_financiero.to_string(index=False))