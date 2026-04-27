import pandas as pd
import numpy as np

def preparar_proyeccion_mensual(df_historico):
    # Definición de la estructura temporal para la matriz de estacionalidad
    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    # Validación preventiva: Si el set de entrada es vacío, retorna un esquema con columnas definidas
    if df_historico.empty:
        return pd.DataFrame(columns=['Nomcultivo', 'Mes', 'Rentabilidad_Proyectada', 'Factor_Mercado'])
    
    # Agrupación por cultivo para obtener la base de utilidad neta
    tendencia = df_historico.groupby('Nomcultivo')['utilidad_neta'].mean().reset_index()
    
    registros = []
    for _, fila in tendencia.iterrows():
        # Generación de ruido estadístico para simular la volatilidad del mercado mensual
        factores = np.random.normal(loc=1.0, scale=0.2, size=12)
        for i, mes in enumerate(meses):
            rentabilidad_proyectada = fila['utilidad_neta'] * factores[i]
            registros.append({
                'Nomcultivo': fila['Nomcultivo'],
                'Mes': mes,
                'Rentabilidad_Proyectada': rentabilidad_proyectada,
                'Factor_Mercado': factores[i]
            })
            
    return pd.DataFrame(registros)

def evaluar_estrategia_inversion(df_historico):
    # Control de flujo: Si no hay datos disponibles por los filtros, retorna estructuras vacías seguras
    if df_historico.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Cálculo de la serie de tiempo para determinar el crecimiento anual (CAGR)
    df_tendencia = df_historico.groupby(['Nomcultivo', 'Anio'])['utilidad_neta'].mean().unstack()
    
    # Gestión de errores para casos con un único año de historial (evita división por cero)
    if df_tendencia.shape[1] < 2:
        cagr = pd.DataFrame({'Nomcultivo': df_tendencia.index, 'Crecimiento_Anual': 0.0})
    else:
        cagr = df_tendencia.pct_change(axis='columns').mean(axis=1).reset_index()
        cagr.columns = ['Nomcultivo', 'Crecimiento_Anual']
    
    # Generación de la proyección de estacionalidad basada en los datos filtrados
    df_proyeccion = preparar_proyeccion_mensual(df_historico)
    
    # Validación de existencia de datos antes del agrupamiento crítico
    if df_proyeccion.empty:
        return pd.DataFrame(), df_proyeccion

    # Identificación del punto máximo de rentabilidad estacional
    idx_max = df_proyeccion.groupby('Nomcultivo')['Rentabilidad_Proyectada'].idxmax()
    df_mes_optimo = df_proyeccion.loc[idx_max]
    
    # Consolidación del análisis de mercado
    df_final = pd.merge(df_mes_optimo, cagr, on='Nomcultivo')
    
    # Lógica de dictamen basada en umbrales de rentabilidad y crecimiento
    condiciones = [
        (df_final['Rentabilidad_Proyectada'] > 60000) & (df_final['Crecimiento_Anual'] > 0.05),
        (df_final['Rentabilidad_Proyectada'] > 0)
    ]
    decisiones = ["Inversión Inmediata", "Inversión Escalonada"]
    
    df_final['Dictamen_Mercado'] = np.select(condiciones, decisiones, default="Retener Capital")
    
    return df_final, df_proyeccion