import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
import zipfile
import os

# Descomprimir el archivo ZIP
with zipfile.ZipFile(io.BytesIO(uploaded['datos-2024-10-09.csv.zip']), 'r') as zip_ref:
    zip_ref.extractall('data')  # Extrae todos los archivos en la carpeta 'data'

# Configuración de la página
st.set_page_config(page_title="Dashboard de Inseguridad en Jalisco", layout="wide")

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv('data/datos-2024-10-09.csv')
    df.dropna(inplace=True)  # Agregar esta línea para eliminar los datos NaN
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['año_mes'] = df['fecha'].dt.to_period('M')
    df['hora'] = pd.to_datetime(df['hora'], errors='coerce').dt.hour  # Agregar errors='coerce' para manejar errores
    return df

df = load_data()

st.title('Dashboard de Inseguridad en Jalisco')

# Sidebar para filtros
st.sidebar.header('Filtros')

# Obtener los municipios disponibles
municipios_disponibles = sorted(df['municipio'].unique())

# Definir los municipios predeterminados que se desean seleccionar
municipios_predeterminados = ['ZAPOPAN', 'GUADALAJARA', 'TONALÁ', 'SAN PEDRO TLAQUEPAQUE']

# Filtrar los municipios predeterminados para asegurarse de que existan en las opciones
municipios_validos = [m for m in municipios_predeterminados if m in municipios_disponibles]

# Crear el multiselect con valores predeterminados válidos
municipio = st.sidebar.multiselect(
    'Selecciona Municipio(s)', 
    options=municipios_disponibles, 
    default=municipios_validos  # Selección predeterminada válida
)

año = st.sidebar.multiselect('Selecciona Año(s)', options=sorted(df['año'].unique()))
delito = st.sidebar.multiselect('Selecciona Delito(s)', options=sorted(df['delito'].unique()))

# Aplicar filtros
filtered_df = df.copy()
if municipio:
    filtered_df = filtered_df[filtered_df['municipio'].isin(municipio)]
if año:
    filtered_df = filtered_df[filtered_df['año'].isin(año)]
if delito:
    filtered_df = filtered_df[filtered_df['delito'].isin(delito)]


# Top delitos por municipio (respetando los filtros)
st.header('Top Delitos por Municipio')
top_delitos = filtered_df.groupby(['municipio', 'delito']).size().reset_index(name='count')
top_delitos = top_delitos.sort_values('count', ascending=False).groupby('municipio').head(5)

fig_top_delitos = px.bar(top_delitos, x='delito', y='count', color='municipio', title='Top 5 Delitos por Municipio', barmode='group')
st.plotly_chart(fig_top_delitos, use_container_width=True)

# Delitos por año
st.header('Delitos por Año')

# Agrupar los datos por año y contar el número de delitos
delitos_por_año = filtered_df.groupby('año').size().reset_index(name='count')

# Asegurarse de que los años sean enteros
delitos_por_año['año'] = delitos_por_año['año'].astype(int)

# Crear la gráfica de barras y asegurarse de que los años se muestren como enteros
fig_delitos_año = px.bar(delitos_por_año, x='año', y='count', title='Evolución de Delitos por Año')
fig_delitos_año.update_layout(xaxis=dict(tickmode='linear'))

# Mostrar la gráfica en Streamlit
st.plotly_chart(fig_delitos_año, use_container_width=True)



# Delitos por año y mes
st.header('Delitos por Año y Mes')
delitos_por_año_mes = filtered_df.groupby('año_mes').size().reset_index(name='count')
delitos_por_año_mes['año_mes'] = delitos_por_año_mes['año_mes'].astype(str)
fig_delitos_año_mes = px.line(delitos_por_año_mes, x='año_mes', y='count', title='Evolución de Delitos por Año y Mes')
st.plotly_chart(fig_delitos_año_mes, use_container_width=True)

# Mapa con Leaflet
st.header('Mapa de Delitos')
m = folium.Map(location=[20.6667, -103.3333], zoom_start=8)

for _, row in filtered_df.iterrows():
    if pd.notnull(row['x']) and pd.notnull(row['y']):
        folium.CircleMarker(
            location=[row['y'], row['x']],
            radius=2,
            popup=f"Delito: {row['delito']}<br>Municipio: {row['municipio']}<br>Fecha: {row['fecha']}",
            color='red',
            fill=True,
            fillColor='red'
        ).add_to(m)

folium_static(m, width=1000, height=600)

# Visualización de Bien Afectado
st.header('Bienes Afectados')
bienes_afectados = filtered_df['bien_afectado'].value_counts().reset_index()
bienes_afectados.columns = ['bien_afectado', 'count']
fig_bienes = px.pie(bienes_afectados, values='count', names='bien_afectado', title='Distribución de Bienes Afectados')
st.plotly_chart(fig_bienes, use_container_width=True)

# Distribución de delitos por hora del día
st.header('Distribución de Delitos por Hora del Día')
delitos_por_hora = filtered_df.groupby('hora').size().reset_index(name='count')
fig_hora = px.bar(delitos_por_hora, x='hora', y='count', title='Distribución de Delitos por Hora del Día')
st.plotly_chart(fig_hora, use_container_width=True)

# Asegurarse de que haya una columna con el día de la semana
filtered_df['dia_semana'] = filtered_df['fecha'].dt.day_name()

# Asegurarse de que haya una columna con el día de la semana en español
dias_semana_map = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

filtered_df['dia_semana'] = filtered_df['fecha'].dt.day_name().map(dias_semana_map)

# Delitos por día de la semana
st.header('Distribución de Delitos por Día de la Semana')
delitos_por_dia = filtered_df.groupby('dia_semana').size().reset_index(name='count')
dias_ordenados = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']  # Asegurar el orden correcto
delitos_por_dia['dia_semana'] = pd.Categorical(delitos_por_dia['dia_semana'], categories=dias_ordenados, ordered=True)
delitos_por_dia = delitos_por_dia.sort_values('dia_semana')  # Ordenar por el día de la semana

fig_dia = px.bar(delitos_por_dia, x='dia_semana', y='count', title='Distribución de Delitos por Día de la Semana', labels={'dia_semana': 'Día de la Semana', 'count': 'Número de Delitos'})
st.plotly_chart(fig_dia, use_container_width=True)



# Delitos por hora
st.header('Distribución de Delitos por Hora del Día')
delitos_por_hora = filtered_df.groupby('hora').size().reset_index(name='count')
fig_hora = px.bar(delitos_por_hora, x='hora', y='count', title='Distribución de Delitos por Hora del Día', labels={'hora': 'Hora del Día', 'count': 'Número de Delitos'})
fig_hora.update_layout(xaxis=dict(dtick=1))  # Asegurar que cada hora esté representada en el eje X
st.plotly_chart(fig_hora, use_container_width=True)



# Métricas generales
st.header('Métricas Generales')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Delitos", len(filtered_df))
with col2:
    st.metric("Municipios Afectados", filtered_df['municipio'].nunique())
with col3:
    st.metric("Tipos de Delitos", filtered_df['delito'].nunique())

# Top 10 delitos
st.header('Top 10 Delitos')
top_10_delitos = filtered_df['delito'].value_counts().nlargest(10)
fig_top_10 = px.bar(top_10_delitos, x=top_10_delitos.index, y=top_10_delitos.values, title='Top 10 Delitos')
st.plotly_chart(fig_top_10, use_container_width=True)
