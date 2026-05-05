# Importa librerías para el cálculo numérico, visualización y densidad de probabilidad.
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Parámetros de entrada para la simulación de precios y costos del cultivo de higo.
precio_historico_higo = 34994.18
volatilidad_higo = 0.12
prima_sostenibilidad = 0.15
costo_operativo = 47000
volumen_t = 6.82
flujo_hidroponico_anual = 65912.40
iteraciones = 5000

# Calcula la dispersión esperada de precio a partir de la volatilidad histórica.
desviacion_estandar = precio_historico_higo * volatilidad_higo

# Fija la semilla para reproducibilidad de la simulación.
np.random.seed(42)
# Genera precios simulados siguiendo una distribución normal alrededor del precio histórico.
precios_simulados = np.random.normal(loc=precio_historico_higo, scale=desviacion_estandar, size=iteraciones)

# Ajusta los precios con la prima de sostenibilidad.
precios_ajustados = precios_simulados * (1 + prima_sostenibilidad)
# Calcula la utilidad neta proyectada de cada iteración considerando volumen, costos y el flujo constante hidropónico.
utilidad_neta_simulada = (precios_ajustados * volumen_t) - costo_operativo + flujo_hidroponico_anual

# Calcula el porcentaje de simulaciones con utilidad positiva.
probabilidad_exito = np.sum(utilidad_neta_simulada > 0) / iteraciones * 100
# Valor esperado medio de la utilidad neta simulada.
valor_esperado = np.mean(utilidad_neta_simulada)
# Estima la probabilidad de quiebra como la contraparte del éxito.
riesgo_quiebra = 100 - probabilidad_exito

# Prepara el gráfico de la distribución de utilidades simuladas.
plt.figure(figsize=(12, 6))

# Dibuja el histograma de frecuencia de la utilidad neta simulada.
counts, bins, patches = plt.hist(utilidad_neta_simulada, bins=50, density=True, alpha=0.6, color='#00e5ff', edgecolor='black')

# Calcula la curva normal de referencia para comparar la forma de la distribución.
mu, std = np.mean(utilidad_neta_simulada), np.std(utilidad_neta_simulada)
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2, label='Función de Densidad (Distribución Normal)')

# Marca en el histograma el punto de quiebra y la media esperada.
plt.axvline(x=0, color='#ff4444', linestyle='--', linewidth=2, label='Punto de Quiebra ($0 Utilidad)')
plt.axvline(x=valor_esperado, color='#00ff88', linestyle='-', linewidth=2, label=f'Valor Esperado: ${valor_esperado:,.0f}')

plt.title("Simulación de Monte Carlo (5,000 Iteraciones): Distribución de Probabilidad de Rentabilidad (Higo + Hidroponía)", fontsize=14)
plt.xlabel("Utilidad Neta Proyectada (MXN)", fontsize=12)
plt.ylabel("Frecuencia (Densidad)", fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Probabilidad de Éxito Comercial: {probabilidad_exito:.2f}%")
print(f"Probabilidad de Pérdida (Riesgo): {riesgo_quiebra:.2f}%")