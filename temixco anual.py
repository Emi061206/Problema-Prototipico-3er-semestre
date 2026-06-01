import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Datos extraídos del "Anexo A" del reporte (Utilidad Neta en MXN)
data = [
    {"Año": 2018, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 691473.25 + 8474720.95}, # Suma de los dos registros de 2018
    {"Año": 2018, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 6861476.94},
    {"Año": 2019, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 4353486.42},
    {"Año": 2019, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 10576976.66},
    {"Año": 2020, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 5093593.50},
    {"Año": 2021, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 5586353.61},
    {"Año": 2021, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 8045391.60},
    {"Año": 2022, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 12230134.62},
    {"Año": 2022, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": 10309287.61},
    {"Año": 2023, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 5242921.24},
    {"Año": 2024, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": 13082189.87},
    # Proyecciones 2025
    {"Año": 2025, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -7087.85},
    {"Año": 2025, "Cultivo": "Higo", "Utilidad Neta (MXN)": 436655.16},
    {"Año": 2025, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 622055.02},
    {"Año": 2025, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -7876.53},
    {"Año": 2025, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 121574.98},
    # Proyecciones 2026
    {"Año": 2026, "Cultivo": "Maíz grano", "Utilidad Neta (MXN)": -7193.23},
    {"Año": 2026, "Cultivo": "Higo", "Utilidad Neta (MXN)": 437337.17},
    {"Año": 2026, "Cultivo": "Caña de azúcar", "Utilidad Neta (MXN)": 622627.83},
    {"Año": 2026, "Cultivo": "Sorgo grano", "Utilidad Neta (MXN)": -7909.87},
    {"Año": 2026, "Cultivo": "Lechuga (NFT)", "Utilidad Neta (MXN)": 121722.34}
]

# 2. Crear el DataFrame de Pandas
df = pd.DataFrame(data)

# 3. Configuración de la gráfica
plt.figure(figsize=(14, 7))
sns.set_theme(style="whitegrid")

# Crear un gráfico de barras agrupado por Año y coloreado por Cultivo
ax = sns.barplot(
    data=df, 
    x="Año", 
    y="Utilidad Neta (MXN)", 
    hue="Cultivo", 
    palette="tab10"
)

# 4. Personalización del diseño
plt.title('Histórico y Proyección de Utilidad Neta por Cultivo (2018-2026)', fontsize=16, fontweight='bold')
plt.xlabel('Año', fontsize=12)
plt.ylabel('Utilidad Neta (Pesos MXN)', fontsize=12)
plt.axhline(0, color='red', linestyle='--', linewidth=1.5) # Línea de cero para resaltar pérdidas
plt.legend(title='Cultivo', bbox_to_anchor=(1.05, 1), loc='upper left')

# Formatear el eje Y para mostrar valores monetarios
ylabels = ['${:,.0f}'.format(y) for y in ax.get_yticks()]
ax.set_yticklabels(ylabels)

# Mostrar la gráfica
plt.tight_layout()
plt.show()