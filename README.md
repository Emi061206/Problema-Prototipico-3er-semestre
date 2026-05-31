# Smart Agroforestry Morelos - Análisis de Diversificación

Sistema interactivo de Ciencia de Datos diseñado para la optimización de la rentabilidad agrícola en Cuautla, Jiutepec y Temixco. El proyecto integra modelos estocásticos y multivariables para validar la transición hacia policultivos sustentables (Higo + Hidroponía NFT).

## Componentes Técnicos

- **Motor Financiero:** Cálculo de punto de equilibrio basado en razón de margen de contribución.
- **Simulación Monte Carlo:** 5,000 iteraciones para evaluar la resiliencia ante volatilidad de precios.
- **Análisis Espacial:** Modelado de superficies de rentabilidad mediante integrales dobles.
- **Reportes Ejecutivos:** Generación automatizada de dictámenes en PDF (ReportLab) y CSV.

## Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Interfaz:** Dash (Plotly) + Dash Bootstrap Components
- **Análisis de Datos:** Pandas, NumPy, SciPy
- **Base de Datos:** MySQL (MySQL Connector)
- **Documentación:** LaTeX (APA 7ma Edición)

## Instalación y Ejecución

1. Clonar el repositorio.
2. Configurar el archivo `.env` con las credenciales de acceso a la base de datos local.
3. Instalar dependencias:
   ```bash
pip install dash dash-bootstrap-components pandas numpy plotly reportlab scipy python-dotenv mysql-connector-python matplotlib seaborn
