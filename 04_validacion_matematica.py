# --- LIBRERÍAS DE CÁLCULO CIENTÍFICO ---
import numpy as np                # Proporciona herramientas para operar sobre matrices y vectores de forma eficiente.
import matplotlib.pyplot as plt   # Motor de visualización para renderizar las superficies de rentabilidad 3D.
from scipy import integrate       # Biblioteca especializada en resolución de integrales numéricas complejas.
from mpl_toolkits.mplot3d import Axes3D # Módulo necesario para proyectar gráficos en tres dimensiones.

# --- MODELADO DE LAS FUNCIONES DE UTILIDAD (Campos Escalares) ---
# Se definen como funciones 'lambda' (funciones anónimas), que son ideales para expresar 
# modelos matemáticos compactos que dependen de dos variables: x (tierra) e y (tecnología).

# Maíz: Función de utilidad que representa el modelo tradicional. 
# El ingreso (16.548*x) menos los costos fijos (19.8), variables (12.257*x) y el costo hídrico (0.2*y).
func_utilidad_maiz = lambda y, x: (16.548 * x) - (19.8 + 12.257 * x) - (0.2 * y)

# Higo: Función del modelo agroforestal diversificado.
# El mayor peso del ingreso (238.659*x) y la penalización no lineal de la tecnología (0.1*y^2) modelan el escalamiento del higo.
func_utilidad_higo = lambda y, x: (238.659 * x) - (29.2 + 17.8 * x) - (0.1 * (y**2))

# --- DOMINIO DE INTEGRACIÓN (Límites del Problema) ---
# Definimos el espacio de decisión: 0 a 5 hectáreas de terreno y 0 a 3 niveles de tecnología.
lim_x_inf, lim_x_sup = 0, 5
lim_y_inf, lim_y_sup = lambda x: 0, lambda x: 3

# --- CÁLCULO DE VOLUMEN (Integración doble - Teorema de Fubini) ---
# dblquad ejecuta la integración doble. Esto suma la utilidad en cada punto infinitesimal del dominio (x,y).
# Es vital para obtener el valor escalar final (la ganancia total proyectada).
vol_maiz, error_maiz = integrate.dblquad(func_utilidad_maiz, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)
vol_higo, error_higo = integrate.dblquad(func_utilidad_higo, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)

# --- PREPARACIÓN DE DATOS PARA VISUALIZACIÓN ---
# np.linspace y np.meshgrid crean una "malla" o mapa de puntos sobre los cuales se graficará la superficie.
x_vals = np.linspace(lim_x_inf, lim_x_sup, 50)
y_vals = np.linspace(0, 3, 50)
X, Y = np.meshgrid(x_vals, y_vals)

# Vectorizamos las funciones para que la computadora calcule la Z (utilidad) de los 2500 puntos (50x50) de la malla.
Z_maiz = np.vectorize(lambda x, y: func_utilidad_maiz(y, x))(X, Y)
Z_higo = np.vectorize(lambda x, y: func_utilidad_higo(y, x))(X, Y)

# --- VISUALIZACIÓN GRÁFICA 3D ---
# Configuramos la ventana gráfica para comparar ambos cultivos lado a lado.
fig = plt.figure(figsize=(16, 7))

# Gráfico para el Maíz: Usamos una paleta 'OrRd' (naranja-rojo) que evoca sequía y modelos tradicionales.
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.plot_surface(X, Y, Z_maiz, cmap='OrRd', alpha=0.9, edgecolor='none')
ax1.set_title("Superficie de Utilidad Acumulada: Maíz")
ax1.set_xlabel("Superficie (Hectáreas)")
ax1.set_ylabel("Tecnología (y)")
ax1.set_zlabel("Utilidad (Z)")

# Gráfico para el Higo: Usamos una paleta 'Greens' que representa crecimiento, sustentabilidad y alta rentabilidad.
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.plot_surface(X, Y, Z_higo, cmap='Greens', alpha=0.9, edgecolor='none')
ax2.set_title("Superficie de Utilidad Acumulada: Higo")
ax2.set_xlabel("Superficie (Hectáreas)")
ax2.set_ylabel("Tecnología (y)")
ax2.set_zlabel("Utilidad (Z)")

# Impresión de resultados para validar contra el cálculo analítico hecho en el LaTeX.
print(f"Volumen Acumulado de Maíz: {vol_maiz:.2f} MXN")
print(f"Volumen Acumulado de Higo: {vol_higo:.2f} MXN")

# Muestra la ventana con los gráficos finales.
plt.show()