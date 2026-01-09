# Proporciona funciones para interactuar con el sistema operativo (como rutas de archivos)
import os  

# Permite modificar aspectos del entorno de ejecución de Python, como la lista de rutas de búsqueda de módulos (sys.path)
import sys 

# En notebooks, usa la ruta del notebook actual
root_dir = os.path.abspath('..')  # Sube un nivel desde /notebooks/
sys.path.append(root_dir)

# Importa las bibliotecas necesarias para el análisis de datos y visualización
import pandas as pd
pd.set_option('display.float_format', '{:.2f}'.format)

# Mostrar todas las filas que necesites (por ejemplo 200)
pd.set_option('display.max_rows', 200)

# Mostrar todas las columnas sin cortar
pd.set_option('display.max_columns', None)

# Evitar que las columnas se corten en ancho
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Importa las funciones personalizadas desde utils
import utils.geo_functions as gf
import utils.tidy_functions as tf

# Importa bibliotecas de visualización
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)

# Configuración de Plotly para mejor visualización
import plotly.io as pio
pio.templates.default = "plotly_white"

import geopandas as gpd
import folium

df = pd.read_csv(r"..\3. Datos\SpanishFishingFleetHistory.csv")

# Convertir columna alta_rgfp a datetime
df['fc_alta_rgfp'] = pd.to_datetime(df['fc_alta_rgfp'], dayfirst=True, errors='coerce')
df['fc_estado'] = pd.to_datetime(df['fc_estado'], dayfirst=True, errors='coerce')

# Rutas
path_ccaa_peninbal = r'..\3. Datos\SHP_ETRS89\recintos_autonomicas_inspire_peninbal_etrs89\recintos_autonomicas_inspire_peninbal_etrs89.shp'
path_ccaa_regcan = r'..\3. Datos\SHP_REGCAN95\recintos_autonomicas_inspire_canarias_regcan95\recintos_autonomicas_inspire_canarias_regcan95.shp'

# Lectura de shapefiles
gdf_peninbal = gf.import_shp_as_gpd(path_ccaa_peninbal)
gdf_canarias = gf.import_shp_as_gpd(path_ccaa_regcan)

#. Renombrar columnas explícitamente para evitar errores de mayúsculas/espacios
gdf_peninbal_sel = gdf_peninbal.rename(columns={'NAMEUNIT': 'comunidad'})[['comunidad', 'geometry']]
gdf_canarias_sel = gdf_canarias.rename(columns={'NAMEUNIT': 'comunidad'})[['comunidad', 'geometry']]

#  Concatenar
gdf_ccaa = pd.concat([gdf_peninbal_sel, gdf_canarias_sel], ignore_index=True)

# Diccionario de corrección (Mapa -> Datos)
mapa_a_datos = {
    'Principado de Asturias': 'Asturias',
    'Illes Balears': 'Illes balears',
    'Cataluña/Catalunya': 'Cataluña',
    'Región de Murcia': 'Murcia',
    'País Vasco/Euskadi': 'País Vasco',
    'Ciudad Autónoma de Ceuta': 'Ceuta',
    'Ciudad Autónoma de Melilla': 'Melilla',
    'Comunitat Valenciana': 'Comunitat Valenciana',
    'Galicia': 'Galicia',
    'Cantabria': 'Cantabria',
    'Andalucía': 'Andalucía',
    'Canarias': 'Canarias' # Asegúrate de que este nombre sea correcto en tu gdf_ccaa
}

# Creamos la columna 'link_key' en el GeoDataFrame para que coincida con el CSV
# Asumimos que la columna del mapa se llama 'comunidad' o 'NAMEUNIT' (ajústalo según tu dataframe)
columna_nombre_mapa = 'comunidad' # O 'NAMEUNIT'
gdf_ccaa['link_key'] = gdf_ccaa[columna_nombre_mapa].replace(mapa_a_datos)

# --- 3. EJECUCIÓN DE MERGE_TABLES ---

# Usamos tu función para unir:
# table1: df (Datos de buques)
# table2: gdf_ccaa (Geometrías)
# left_index: 'Comunidad Autónoma'
# right_index: 'link_key'
# columns_table2: Solo pedimos 'geometry' (la función se encarga de traer también el right_index)

df_resultante = tf.merge_tables(
    table1=df,
    table2=gdf_ccaa,
    left_index='Comunidad Autónoma',
    right_index='link_key',
    columns_table1=None,         # None = Traer todas las columnas de los buques
    columns_table2=['geometry'], # Solo queremos pegar la geometría
    how='inner'                  # Solo registros que coincidan
)

# --- 4. CONVERSIÓN FINAL A GEODATAFRAME ---

# La función devuelve un DataFrame estándar de pandas.
# Para mapas, debemos convertirlo de nuevo a GeoDataFrame.
gdf_analisis = gpd.GeoDataFrame(df_resultante, geometry='geometry')

# Análisis de evolución temporal
evolucion_anual = df.groupby(df['fc_alta_rgfp'].dt.year).agg({
    'cfr': 'count',
    'eslora_total': 'mean',
    'potencia_kw': 'mean',
    'arqueo_gt': 'mean'
}).reset_index()
evolucion_anual.columns = ['año', 'num_buques', 'eslora_media', 'potencia_media', 'arqueo_medio']

# Crear figura con subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Número de Altas Anuales', 'Evolución de Eslora Media',
                    'Evolución de Potencia Media', 'Evolución de Arqueo Medio'),
    vertical_spacing=0.12,
    horizontal_spacing=0.10
)

# Número de buques
fig.add_trace(
    go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['num_buques'],
               mode='lines+markers', name='Altas anuales',
               line=dict(color='#2E86AB', width=3),
               marker=dict(size=6)),
    row=1, col=1
)

# Eslora media
fig.add_trace(
    go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['eslora_media'],
               mode='lines', name='Eslora (m)',
               line=dict(color='#A23B72', width=3),
               fill='tonexty'),
    row=1, col=2
)

# Potencia media
fig.add_trace(
    go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['potencia_media'],
               mode='lines', name='Potencia (kW)',
               line=dict(color='#F18F01', width=3)),
    row=2, col=1
)

# Arqueo medio
fig.add_trace(
    go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['arqueo_medio'],
               mode='lines', name='Arqueo (GT)',
               line=dict(color='#06A77D', width=3)),
    row=2, col=2
)

fig.update_xaxes(title_text="Año", row=2, col=1)
fig.update_xaxes(title_text="Año", row=2, col=2)
fig.update_yaxes(title_text="Número de buques", row=1, col=1)
fig.update_yaxes(title_text="Metros", row=1, col=2)
fig.update_yaxes(title_text="kW", row=2, col=1)
fig.update_yaxes(title_text="GT", row=2, col=2)

fig.update_layout(
    height=700,
    title_text="<b>Evolución de la Flota Pesquera Española (1987-2025)</b>",
    showlegend=False,
    font=dict(size=11)
)

# Agrupar por edad del buque y calcular la mediana
df_median = df.groupby('Edad_buque')[['eslora_total', 'potencia_kw', 'arqueo_gt']].median().reset_index()

# Estilo gráfico
sns.set(style='whitegrid')

# Crear el gráfico
plt.figure(figsize=(12, 6))
plt.plot(df_median['Edad_buque'], df_median['eslora_total'], label='Eslora total (m)', marker='o')
plt.plot(df_median['Edad_buque'], df_median['potencia_kw'], label='Potencia (kW)', marker='s')
plt.plot(df_median['Edad_buque'], df_median['arqueo_gt'], label='Arqueo GT', marker='^')

# Añadir títulos y leyenda
plt.title('Evolución de Eslora, Potencia y Arqueo según Edad del Buque (mediana)')
plt.xlabel('Edad del buque (años)')
plt.ylabel('Valor mediano')
plt.legend()
plt.tight_layout()
plt.show()

# Eliminamos registros sin fecha de alta
df_time = df.dropna(subset=['fc_alta_rgfp']).copy()

# Extraemos el año desde la fecha de alta
df_time['anio'] = df_time['fc_alta_rgfp'].dt.year

# Cálculo de medias por año y Comunidad Autónoma
df_mean_time = (
    df_time
    .groupby(['anio', 'Comunidad Autónoma'], as_index=False)
    .agg({
        'eslora_total': 'mean',
        'potencia_kw': 'mean',
        'arqueo_gt': 'mean'
    })
)

fig = px.line(
    df_mean_time,
    x='anio',
    y='eslora_total',
    facet_col='Comunidad Autónoma',
    facet_col_wrap=4,
    title='Evolución de la eslora media por Comunidad Autónoma (1987–2025)',
    labels={
        'anio': 'Año',
        'eslora_total': 'Eslora media (m)'
    }
)

fig.update_layout(height=800)
fig.show()

# Eliminamos registros sin fecha de alta
df_time = df.dropna(subset=['fc_alta_rgfp']).copy()

# Extraemos el año desde la fecha de alta
df_time['anio'] = df_time['fc_alta_rgfp'].dt.year

# Cálculo de medias por año y Comunidad Autónoma
df_mean_time = (
    df_time
    .groupby(['anio', 'Comunidad Autónoma'], as_index=False)
    .agg({
        'eslora_total': 'mean',
        'potencia_kw': 'mean',
        'arqueo_gt': 'mean'
    })
)

fig = px.line(
    df_mean_time,
    x='anio',
    y='potencia_kw',
    facet_col='Comunidad Autónoma',
    facet_col_wrap=4,
    title='Evolución de la potencia media por Comunidad Autónoma (1987–2025)',
    labels={
        'anio': 'Año',
        'potencia_kw': 'Potencia media (kW)'
    }
)

fig.update_layout(height=800)
fig.show()

import plotly.express as px

# Eliminamos registros sin fecha de alta
df_time = df.dropna(subset=['fc_alta_rgfp']).copy()

# Extraemos el año desde la fecha de alta
df_time['anio'] = df_time['fc_alta_rgfp'].dt.year

# Cálculo de medias por año y Comunidad Autónoma
df_mean_time = (
    df_time
    .groupby(['anio', 'Comunidad Autónoma'], as_index=False)
    .agg({
        'eslora_total': 'mean',
        'potencia_kw': 'mean',
        'arqueo_gt': 'mean'
    })
)

fig = px.line(
    df_mean_time,
    x='anio',
    y='arqueo_gt',
    facet_col='Comunidad Autónoma',
    facet_col_wrap=4,
    title='Evolución del arqueo medio por Comunidad Autónoma (1987–2025)',
    labels={
        'anio': 'Año',
        'arqueo_gt': 'Arqueo medio (GT)'
    }
)

fig.update_layout(height=800)
fig.show()

# Distribución por comunidad autónoma
dist_ccaa = df['Comunidad Autónoma'].value_counts().reset_index()
dist_ccaa.columns = ['comunidad', 'num_buques']
dist_ccaa['porcentaje'] = (dist_ccaa['num_buques'] / dist_ccaa['num_buques'].sum() * 100).round(1)

# Gráfico de distribución geográfica
fig = go.Figure()

fig.add_trace(go.Bar(
    x=dist_ccaa['comunidad'],
    y=dist_ccaa['num_buques'],
    text=dist_ccaa['porcentaje'].apply(lambda x: f'{x}%'),
    textposition='outside',
    marker=dict(
        color=dist_ccaa['num_buques'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Buques")
    ),
    hovertemplate='<b>%{x}</b><br>Buques: %{y:,}<br>Porcentaje: %{text}<extra></extra>'
))

fig.update_layout(
    title='<b>Distribución de la Flota por Comunidad Autónoma</b>',
    xaxis_title='Comunidad Autónoma',
    yaxis_title='Número de Buques',
    height=500,
    showlegend=False,
    font=dict(size=12)
)

fig.show()

# Relación entre comunidad y tipo de arte
ccaa_arte = pd.crosstab(df['Comunidad Autónoma'], df['Tipo de Arte'], normalize='index') * 100

fig = go.Figure()

for arte in ccaa_arte.columns:
    fig.add_trace(go.Bar(
        name=arte,
        x=ccaa_arte.index,
        y=ccaa_arte[arte],
        text=ccaa_arte[arte].round(1).astype(str) + '%',
        textposition='inside'
    ))

fig.update_layout(
    title='<b>Especialización Regional: Tipo de Arte por Comunidad Autónoma</b>',
    xaxis_title='Comunidad Autónoma',
    yaxis_title='Porcentaje de Buques (%)',
    barmode='stack',
    height=600,
    font=dict(size=11),
    legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="right", x=1.08)
)

fig.show()

# Matriz de correlación
variables_numericas = ['eslora_total', 'potencia_kw', 'arqueo_gt', 'Edad_buque']
matriz_corr = df[variables_numericas].corr()

# Heatmap de correlaciones
fig = go.Figure(data=go.Heatmap(
    z=matriz_corr.values,
    x=['Eslora', 'Potencia', 'Arqueo', 'Edad'],
    y=['Eslora', 'Potencia', 'Arqueo', 'Edad'],
    colorscale='RdBu',
    zmid=0,
    text=matriz_corr.values.round(2),
    texttemplate='%{text}',
    textfont={"size": 14},
    colorbar=dict(title="Correlación")
))

fig.update_layout(
    title='<b>Matriz de Correlación: Variables Técnicas</b>',
    height=500,
    font=dict(size=12)
)

fig.show()

# Scatter plot 3D: Eslora vs Potencia vs Arqueo
fig = px.scatter_3d(
    df.sample(5000),
    x='eslora_total',
    y='potencia_kw',
    z='arqueo_gt',
    color='Tipo de Arte',
    size='Edad_buque',
    hover_data=['Comunidad Autónoma', 'material_casco'],
    title='<b>Relación Tridimensional: Eslora, Potencia y Arqueo</b>',
    labels={
        'eslora_total': 'Eslora (m)',
        'potencia_kw': 'Potencia (kW)',
        'arqueo_gt': 'Arqueo (GT)',
        'Tipo de Arte': 'Tipo de Arte'
    },
    height=700
)


fig.update_traces(marker=dict(line=dict(width=0)))

fig.show()

# Distribución de edad
fig = go.Figure()

fig.add_trace(go.Histogram(
    x=df['Edad_buque'],
    nbinsx=40,
    name='Distribución',
    marker=dict(
        color='lightblue',
        line=dict(color='darkblue', width=1)
    ),
    opacity=0.7
))

# Línea de media
edad_media = df['Edad_buque'].mean()
fig.add_vline(x=edad_media, line_dash="dash", line_color="red", 
              annotation_text=f"Media: {edad_media:.1f} años",
              annotation_position="top right")

fig.update_layout(
    title='<b>Distribución de Edad de la Flota Pesquera</b>',
    xaxis_title='Edad del Buque (años)',
    yaxis_title='Frecuencia',
    height=500,
    showlegend=False,
    font=dict(size=12)
)

fig.show()

# Edad media por comunidad autónoma
edad_ccaa = df.groupby('Comunidad Autónoma')['Edad_buque'].agg(['mean', 'median', 'std']).reset_index()
edad_ccaa = edad_ccaa.sort_values('mean', ascending=True)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=edad_ccaa['mean'],
    y=edad_ccaa['Comunidad Autónoma'],
    orientation='h',
    marker=dict(
        color=edad_ccaa['mean'],
        colorscale='Reds',
        showscale=True,
        colorbar=dict(title="Edad Media")
    ),
    text=edad_ccaa['mean'].round(1),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Edad media: %{x:.1f} años<extra></extra>'
))

fig.update_layout(
    title='<b>Edad Media de la Flota por Comunidad Autónoma</b>',
    xaxis_title='Edad Media (años)',
    yaxis_title='',
    height=500,
    showlegend=False,
    font=dict(size=12)
)

fig.show()

# Comparación de características por tipo de arte
fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Eslora por Tipo de Arte', 'Potencia por Tipo de Arte', 'Arqueo por Tipo de Arte')
)

tipos_arte = df['Tipo de Arte'].unique()
colors = px.colors.qualitative.Set2

for idx, arte in enumerate(tipos_arte):
    data = df[df['Tipo de Arte'] == arte]['eslora_total']
    fig.add_trace(
        go.Box(y=data, name=arte, marker_color=colors[idx % len(colors)]),
        row=1, col=1
    )
    
    data = df[df['Tipo de Arte'] == arte]['potencia_kw']
    fig.add_trace(
        go.Box(y=data, name=arte, marker_color=colors[idx % len(colors)], showlegend=False),
        row=1, col=2
    )
    
    data = df[df['Tipo de Arte'] == arte]['arqueo_gt']
    fig.add_trace(
        go.Box(y=data, name=arte, marker_color=colors[idx % len(colors)], showlegend=False),
        row=1, col=3
    )

fig.update_yaxes(title_text="Metros", row=1, col=1, type="log")
fig.update_yaxes(title_text="kW", row=1, col=2, type="log")
fig.update_yaxes(title_text="GT", row=1, col=3, type="log")

fig.update_layout(
    title_text="<b>Características Técnicas por Tipo de Arte de Pesca</b>",
    height=500,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)

fig.show()

# Sunburst: Jerarquía de la flota
fig = px.sunburst(
    df,
    path=['Comunidad Autónoma', 'Tipo de Arte', 'material_casco'],
    values='eslora_total',
    title='<b>Jerarquía de la Flota: Comunidad → Arte → Material</b>',
    height=700,
    color='eslora_total',
    color_continuous_scale='Viridis'
)

fig.update_traces(textinfo="label+percent parent")

fig.show()

# %%
# Parallel coordinates: Análisis multivariante
df_sample = df.sample(2000)

fig = px.parallel_coordinates(
    df_sample,
    dimensions=['eslora_total', 'potencia_kw', 'arqueo_gt', 'Edad_buque'],
    color='Edad_buque',
    labels={
        'eslora_total': 'Eslora',
        'potencia_kw': 'Potencia',
        'arqueo_gt': 'Arqueo',
        'Edad_buque': 'Edad'
    },
    color_continuous_scale='Plasma',
    title='<b>Coordenadas Paralelas: Análisis Multivariante de la Flota</b>'
)

fig.update_layout(height=600)

fig.show()