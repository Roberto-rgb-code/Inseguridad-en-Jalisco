# Dashboard de Inseguridad en Jalisco

Este proyecto es un dashboard interactivo creado con Streamlit para visualizar datos de inseguridad en Jalisco, México.

## Requisitos

- Python 3.7+
- pip

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/jalisco-inseguridad-dashboard.git
   cd jalisco-inseguridad-dashboard
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

1. Asegúrate de que el archivo de datos `datos-2024-10-09.csv` esté en la carpeta `data/`.

2. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```

3. Abre tu navegador y ve a `http://localhost:8501` para ver el dashboard.

## Características

- Visualización de top delitos por municipio
- Evolución de delitos por año y mes
- Mapa interactivo de delitos
- Distribución de bienes afectados
- Distribución de delitos por hora del día
- Comparativa de delitos entre zonas geográficas

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de hacer un pull request.

## Licencia

Este proyecto está bajo la licencia MIT.
