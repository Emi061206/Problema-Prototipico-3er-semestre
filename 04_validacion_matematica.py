# Librerías para cálculo numérico, gráficos y operaciones de integración.
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from mpl_toolkits.mplot3d import Axes3D

# Funciones de utilidad para cada cultivo en función de superficie y tecnificación hídrica (Cifras en miles de MXN).
# Maíz: Ingreso (16.548*x) - Costos Fijos (19.8) - Costos Variables (12.257*x) - Penalización hídrica lineal (0.2*y)
func_utilidad_maiz = lambda y, x: (16.548 * x) - (19.8 + 12.257 * x) - (0.2 * y)

# Higo: Ingreso (238.659*x) - Costos Fijos (29.2) - Costos Variables (17.8*x) - Penalización hídrica cuadrática (0.1*(y**2))
func_utilidad_higo = lambda y, x: (238.659 * x) - (29.2 + 17.8 * x) - (0.1 * (y**2))

# Límites de integración que delimitan el dominio de superficie y tecnificación para el análisis.
lim_x_inf, lim_x_sup = 0, 5
lim_y_inf, lim_y_sup = lambda x: 0, lambda x: 3

# Integra la función de utilidad en el dominio para obtener el volumen económico acumulado.
vol_maiz, error_maiz = integrate.dblquad(func_utilidad_maiz, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)
vol_higo, error_higo = integrate.dblquad(func_utilidad_higo, lim_x_inf, lim_x_sup, lim_y_inf, lim_y_sup)

x_vals = np.linspace(lim_x_inf, lim_x_sup, 50)
y_vals = np.linspace(0, 3, 50)
X, Y = np.meshgrid(x_vals, y_vals)

Z_maiz = np.vectorize(lambda x, y: func_utilidad_maiz(y, x))(X, Y)
Z_higo = np.vectorize(lambda x, y: func_utilidad_higo(y, x))(X, Y)

# Genera una figura con dos paneles 3D para comparar cultivos.
fig = plt.figure(figsize=(16, 7))

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.plot_surface(X, Y, Z_maiz, cmap='OrRd', alpha=0.9, edgecolor='none')
ax1.set_title("Superficie de Utilidad Acumulada: Maíz")
ax1.set_xlabel("Superficie (Hectáreas)")
ax1.set_ylabel("Nivel de Tecnificación Hídrica")
ax1.set_zlabel("Utilidad Unitaria (Miles MXN)")
ax1.set_zlim(-30, 20)

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.plot_surface(X, Y, Z_higo, cmap='Tealgrn', alpha=0.9, edgecolor='none')
ax2.set_title("Superficie de Utilidad Acumulada: Higo")
ax2.set_xlabel("Superficie (Hectáreas)")
ax2.set_ylabel("Nivel de Tecnificación Hídrica")
ax2.set_zlabel("Utilidad Unitaria (Miles MXN)")
ax2.set_zlim(-50, 1100)

plt.tight_layout()
plt.show()

print(f"Impacto Económico Regional (Maíz): ${vol_maiz * 1000:,.2f} MXN")
print(f"Impacto Económico Regional (Higo): ${vol_higo * 1000:,.2f} MXN")