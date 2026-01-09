# Usa streamlit run dashboard_flota.py para ejecutar el dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Configuración de la página
st.set_page_config(
    page_title="Flota Pesquera Española (1987-2025)",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .big-title {
        font-size: 56px;
        font-weight: bold;
        text-align: center;
        color: #0066cc;
        margin: 30px 0 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 24px;
        text-align: center;
        color: #666;
        margin-bottom: 40px;
        font-style: italic;
    }
    .chapter-intro {
        font-size: 18px;
        color: #555;
        line-height: 1.8;
        padding: 20px;
        background: #f8f9fa;
        border-left: 5px solid #0066cc;
        border-radius: 5px;
        margin: 20px 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 48px;
        font-weight: bold;
        color: #0066cc;
    }
    .metric-label {
        font-size: 16px;
        color: #666;
        margin-top: 10px;
    }
    .insight-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }
    .recommendation-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "3. Datos" / "SpanishFishingFleetHistory.csv"

# Cargar datos
@st.cache_data
def load_data():
    # Ajusta la ruta según tu estructura
    df = pd.read_csv(DATA_PATH)
    
    # Convertir fechas
    df['fc_alta_rgfp'] = pd.to_datetime(df['fc_alta_rgfp'], dayfirst=True, errors='coerce')
    df['fc_estado'] = pd.to_datetime(df['fc_estado'], dayfirst=True, errors='coerce')
    
    # Extraer año
    df['anio_alta'] = df['fc_alta_rgfp'].dt.year
    
    # Categorías de edad
    df['categoria_edad'] = pd.cut(
        df['Edad_buque'],
        bins=[-1, 10, 20, 30, 40],
        labels=['0-10 años', '11-20 años', '21-30 años', '>30 años']
    )
    
    # Categorías de eslora
    df['categoria_eslora'] = pd.cut(
        df['eslora_total'],
        bins=[0, 10, 15, 20, 120],
        labels=['Pequeño (<10m)', 'Mediano (10-15m)', 'Grande (15-20m)', 'Muy Grande (>20m)']
    )
    
    return df

data = load_data()

# ============================================
# SIDEBAR - FILTROS
# ============================================
st.sidebar.title("⚓ Filtros de Exploración")

# Filtro de Comunidad Autónoma
ccaa_options = ["Todas"] + sorted(data["Comunidad Autónoma"].unique().tolist())
selected_ccaa = st.sidebar.selectbox("Comunidad Autónoma", ccaa_options)

# Filtro de años
min_year = int(data["anio_alta"].min())
max_year = int(data["anio_alta"].max())
year_range = st.sidebar.slider(
    "Año de alta en el registro",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# Filtro de tipo de arte
arte_options = ["Todos"] + sorted(data["Tipo de Arte"].unique().tolist())
selected_arte = st.sidebar.selectbox("Tipo de Arte de Pesca", arte_options)

# Filtro de estado
estado_options = ["Todos"] + sorted(data["estado_rgfp"].unique().tolist())
selected_estado = st.sidebar.selectbox("Estado del Buque", estado_options)

# Aplicar filtros
data_filtered = data[
    (data["anio_alta"] >= year_range[0]) &
    (data["anio_alta"] <= year_range[1])
].copy()

if selected_ccaa != "Todas":
    data_filtered = data_filtered[data_filtered["Comunidad Autónoma"] == selected_ccaa]

if selected_arte != "Todos":
    data_filtered = data_filtered[data_filtered["Tipo de Arte"] == selected_arte]

if selected_estado != "Todos":
    data_filtered = data_filtered[data_filtered["estado_rgfp"] == selected_estado]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 **Buques filtrados:** {len(data_filtered):,}")

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown('<div class="big-title">🚢 Flota Pesquera Española</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">38 Años de Historia Naval (1987-2025)</div>', unsafe_allow_html=True)

st.markdown("---")

# ============================================
# TABS - CAPÍTULOS
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Panorama General",
    "⏱️ Evolución Temporal", 
    "🗺️ Distribución Geográfica",
    "🎣 Modalidades de Pesca",
    "⚙️ Tipologías (Clustering)",
    "🎯 Conclusiones"
])

# ============================================
# TAB 1: PANORAMA GENERAL
# ============================================
with tab1:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        edad_media = data_filtered["Edad_buque"].mean()
        st.markdown(f"""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #0066cc 0%, #004d99 100%); 
        border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-top: 30px;">
            <div style="font-size: 80px; font-weight: bold; color: white;">{edad_media:.1f}</div>
            <div style="font-size: 28px; color: #f0f0f0; margin-top: 10px;">AÑOS DE EDAD MEDIA</div>
            <div style="font-size: 18px; color: #e0e0e0; margin-top: 20px; font-style: italic;">
            Una flota que envejece progresivamente
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chapter-intro">
    <strong>La flota pesquera española ha sido el motor económico de miles de familias costeras.</strong> 
    Desde 1987 hasta 2025, más de <strong>27,000 buques</strong> han surcado nuestras aguas, 
    desde pequeñas embarcaciones de artes menores hasta grandes arrastreros de altura.<br><br>
    
    Este análisis explora la <strong>evolución, distribución geográfica, especialización regional</strong> 
    y las <strong>características técnicas</strong> que definen nuestra tradición pesquera.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Métricas Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(data_filtered):,}</div>
            <div class="metric-label">Buques Totales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        eslora_media = data_filtered["eslora_total"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #28a745;">{eslora_media:.1f}m</div>
            <div class="metric-label">Eslora Media</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        potencia_media = data_filtered["potencia_kw"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ff7f0e;">{potencia_media:.0f}kW</div>
            <div class="metric-label">Potencia Media</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        arqueo_medio = data_filtered["arqueo_gt"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #dc3545;">{arqueo_medio:.1f}GT</div>
            <div class="metric-label">Arqueo Medio</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos de distribución
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎣 Distribución por Tipo de Arte")
        arte_dist = data_filtered.groupby("Tipo de Arte").size().reset_index(name="count")
        arte_dist = arte_dist.sort_values("count", ascending=False)
        
        fig_arte = px.pie(
            arte_dist,
            values="count",
            names="Tipo de Arte",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_arte.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig_arte.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_arte, use_container_width=True)
    
    with col2:
        st.markdown("### ⚙️ Material del Casco")
        material_dist = data_filtered.groupby("material_casco").size().reset_index(name="count")
        material_dist = material_dist.sort_values("count", ascending=False)
        
        fig_material = px.pie(
            material_dist,
            values="count",
            names="material_casco",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_material.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig_material.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_material, use_container_width=True)
    
    st.markdown("### 🔢 Distribución de Características")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'categoria_eslora' in data_filtered.columns:
            eslora_cat = data_filtered['categoria_eslora'].value_counts().reset_index()
            eslora_cat.columns = ['categoria', 'count']
            
            fig_eslora_cat = px.bar(
                eslora_cat,
                x='categoria',
                y='count',
                title='Distribución por Categoría de Eslora',
                labels={'categoria': 'Categoría', 'count': 'Número de Buques'},
                color='count',
                color_continuous_scale='Blues',
                text='count'
            )
            fig_eslora_cat.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_eslora_cat.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_eslora_cat, use_container_width=True)
    
    with col2:
        if 'categoria_edad' in data_filtered.columns:
            edad_cat = data_filtered['categoria_edad'].value_counts().reset_index()
            edad_cat.columns = ['categoria', 'count']
            
            fig_edad_cat = px.bar(
                edad_cat,
                x='categoria',
                y='count',
                title='Distribución por Categoría de Edad',
                labels={'categoria': 'Categoría', 'count': 'Número de Buques'},
                color='count',
                color_continuous_scale='Reds',
                text='count'
            )
            fig_edad_cat.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_edad_cat.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_edad_cat, use_container_width=True)

# ============================================
# TAB 2: EVOLUCIÓN TEMPORAL
# ============================================
with tab2:
    st.markdown("""
    <div class="chapter-intro">
    La evolución temporal de la flota pesquera española refleja <strong>políticas pesqueras, 
    crisis económicas y cambios en la demanda</strong>. Analicemos cómo han cambiado el número, 
    tamaño y potencia de los buques a lo largo de casi cuatro décadas.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Evolución de Altas Anuales")
    
    # Evolución anual
    evolucion_anual = data_filtered.groupby('anio_alta').agg({
        'cfr': 'count',
        'eslora_total': 'mean',
        'potencia_kw': 'mean',
        'arqueo_gt': 'mean'
    }).reset_index()
    evolucion_anual.columns = ['año', 'num_buques', 'eslora_media', 'potencia_media', 'arqueo_medio']
    
    fig_evol = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Número de Altas Anuales', 'Evolución de Eslora Media',
                        'Evolución de Potencia Media', 'Evolución de Arqueo Medio'),
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )
    
    # Número de buques
    fig_evol.add_trace(
        go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['num_buques'],
                   mode='lines+markers', name='Altas anuales',
                   line=dict(color='#2E86AB', width=3),
                   marker=dict(size=6)),
        row=1, col=1
    )
    
    # Eslora media
    fig_evol.add_trace(
        go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['eslora_media'],
                   mode='lines', name='Eslora (m)',
                   line=dict(color='#A23B72', width=3),
                   fill='tonexty'),
        row=1, col=2
    )
    
    # Potencia media
    fig_evol.add_trace(
        go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['potencia_media'],
                   mode='lines', name='Potencia (kW)',
                   line=dict(color='#F18F01', width=3)),
        row=2, col=1
    )
    
    # Arqueo medio
    fig_evol.add_trace(
        go.Scatter(x=evolucion_anual['año'], y=evolucion_anual['arqueo_medio'],
                   mode='lines', name='Arqueo (GT)',
                   line=dict(color='#06A77D', width=3)),
        row=2, col=2
    )
    
    fig_evol.update_xaxes(title_text="Año", row=2, col=1)
    fig_evol.update_xaxes(title_text="Año", row=2, col=2)
    fig_evol.update_yaxes(title_text="Número de buques", row=1, col=1)
    fig_evol.update_yaxes(title_text="Metros", row=1, col=2)
    fig_evol.update_yaxes(title_text="kW", row=2, col=1)
    fig_evol.update_yaxes(title_text="GT", row=2, col=2)
    
    fig_evol.update_layout(
        height=700,
        showlegend=False,
        font=dict(size=11)
    )
    
    st.plotly_chart(fig_evol, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
        <strong>💡 Insight Clave:</strong> Se observa un <strong>descenso significativo en las altas 
        desde finales de los 90</strong>, coincidiendo con políticas restrictivas de la UE. 
        Sin embargo, los buques que se dan de alta son <strong>más grandes y potentes</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    # Envejecimiento de la flota
    st.markdown("### 👴 Envejecimiento de la Flota")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        edad_dist = data_filtered['Edad_buque'].value_counts().sort_index().reset_index()
        edad_dist.columns = ['edad', 'count']
        
        fig_edad = go.Figure()
        
        fig_edad.add_trace(go.Histogram(
            x=data_filtered['Edad_buque'],
            nbinsx=38,
            name='Distribución',
            marker=dict(
                color='lightblue',
                line=dict(color='darkblue', width=1)
            ),
            opacity=0.7
        ))
        
        edad_media = data_filtered['Edad_buque'].mean()
        fig_edad.add_vline(x=edad_media, line_dash="dash", line_color="red", 
                          annotation_text=f"Media: {edad_media:.1f} años",
                          annotation_position="top right")
        
        fig_edad.update_layout(
            title='Distribución de Edad de la Flota',
            xaxis_title='Edad del Buque (años)',
            yaxis_title='Frecuencia',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_edad, use_container_width=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Estadísticas de Edad
        
        **Medidas centrales:**
        - Media: {data_filtered['Edad_buque'].mean():.1f} años
        - Mediana: {data_filtered['Edad_buque'].median():.1f} años
        - Moda: {data_filtered['Edad_buque'].mode()[0]:.0f} años
        
        **Dispersión:**
        - Desv. Std: {data_filtered['Edad_buque'].std():.1f} años
        - Rango: {data_filtered['Edad_buque'].min():.0f}-{data_filtered['Edad_buque'].max():.0f} años
        """)

# ============================================
# TAB 3: DISTRIBUCIÓN GEOGRÁFICA
# ============================================
with tab3:
    st.markdown("""
    <div class="chapter-intro">
    La geografía determina la especialización pesquera. <strong>Galicia, Andalucía y Cataluña</strong> 
    concentran la mayoría de la flota, pero cada región tiene características únicas.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🗺️ Distribución por Comunidad Autónoma")
    
    # Distribución geográfica
    dist_ccaa = data_filtered['Comunidad Autónoma'].value_counts().reset_index()
    dist_ccaa.columns = ['comunidad', 'num_buques']
    dist_ccaa['porcentaje'] = (dist_ccaa['num_buques'] / dist_ccaa['num_buques'].sum() * 100).round(1)
    
    fig_ccaa = go.Figure()
    
    fig_ccaa.add_trace(go.Bar(
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
    
    fig_ccaa.update_layout(
        title='Distribución de la Flota por Comunidad Autónoma',
        xaxis_title='Comunidad Autónoma',
        yaxis_title='Número de Buques',
        height=500,
        showlegend=False
    )
    fig_ccaa.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_ccaa, use_container_width=True)
    
    # Edad media por CCAA
    st.markdown("### 📊 Edad Media por Comunidad Autónoma")
    
    edad_ccaa = data_filtered.groupby('Comunidad Autónoma')['Edad_buque'].mean().reset_index()
    edad_ccaa = edad_ccaa.sort_values('Edad_buque', ascending=True)
    edad_ccaa.columns = ['comunidad', 'edad_media']
    
    fig_edad_ccaa = go.Figure()
    
    fig_edad_ccaa.add_trace(go.Bar(
        x=edad_ccaa['edad_media'],
        y=edad_ccaa['comunidad'],
        orientation='h',
        marker=dict(
            color=edad_ccaa['edad_media'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Edad Media")
        ),
        text=edad_ccaa['edad_media'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Edad media: %{x:.1f} años<extra></extra>'
    ))
    
    fig_edad_ccaa.update_layout(
        title='Edad Media de la Flota por Comunidad Autónoma',
        xaxis_title='Edad Media (años)',
        yaxis_title='',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_edad_ccaa, use_container_width=True)
    
    # Top puertos
    st.markdown("### ⚓ Top 15 Puertos por Número de Buques")
    
    top_puertos = data_filtered['Puerto'].value_counts().head(15).reset_index()
    top_puertos.columns = ['puerto', 'count']
    
    fig_puertos = px.bar(
        top_puertos,
        x='count',
        y='puerto',
        orientation='h',
        title='Principales Puertos Pesqueros',
        labels={'puerto': 'Puerto', 'count': 'Número de Buques'},
        color='count',
        color_continuous_scale='Blues',
        text='count'
    )
    fig_puertos.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_puertos.update_layout(height=500, showlegend=False)
    
    st.plotly_chart(fig_puertos, use_container_width=True)

# ============================================
# TAB 4: MODALIDADES DE PESCA
# ============================================
with tab4:
    st.markdown("""
    <div class="chapter-intro">
    Cada arte de pesca requiere características técnicas específicas. <strong>Las artes menores dominan 
    en número, pero los arrastreros destacan por su tamaño y potencia.</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎣 Especialización Regional: Tipo de Arte por CCAA")
    
    # Relación CCAA - Arte
    ccaa_arte = pd.crosstab(data_filtered['Comunidad Autónoma'], 
                           data_filtered['Tipo de Arte'], 
                           normalize='index') * 100
    
    fig_ccaa_arte = go.Figure()
    
    for arte in ccaa_arte.columns:
        fig_ccaa_arte.add_trace(go.Bar(
            name=arte,
            x=ccaa_arte.index,
            y=ccaa_arte[arte],
            text=ccaa_arte[arte].round(1).astype(str) + '%',
            textposition='inside'
        ))
    
    fig_ccaa_arte.update_layout(
        title='Distribución de Tipos de Arte por Comunidad Autónoma (%)',
        xaxis_title='Comunidad Autónoma',
        yaxis_title='Porcentaje de Buques (%)',
        barmode='stack',
        height=600,
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="right", x=1.08)
    )
    fig_ccaa_arte.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_ccaa_arte, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
        <strong>💡 Insight Clave:</strong> Galicia muestra una <strong>alta especialización en artes menores</strong>, 
        mientras que regiones como Andalucía tienen una distribución más equilibrada entre diferentes modalidades.
    </div>
    """, unsafe_allow_html=True)
    
    # Características por tipo de arte
    st.markdown("### ⚙️ Características Técnicas por Tipo de Arte")
    
    fig_arte_caract = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Eslora por Tipo de Arte', 'Potencia por Tipo de Arte', 'Arqueo por Tipo de Arte')
    )
    
    tipos_arte = data_filtered['Tipo de Arte'].unique()
    colors = px.colors.qualitative.Set2
    
    for idx, arte in enumerate(tipos_arte):
        data_arte = data_filtered[data_filtered['Tipo de Arte'] == arte]['eslora_total']
        fig_arte_caract.add_trace(
            go.Box(y=data_arte, name=arte, marker_color=colors[idx % len(colors)]),
            row=1, col=1
        )
        
        data_arte = data_filtered[data_filtered['Tipo de Arte'] == arte]['potencia_kw']
        fig_arte_caract.add_trace(
            go.Box(y=data_arte, name=arte, marker_color=colors[idx % len(colors)], showlegend=False),
            row=1, col=2
        )
        
        data_arte = data_filtered[data_filtered['Tipo de Arte'] == arte]['arqueo_gt']
        fig_arte_caract.add_trace(
            go.Box(y=data_arte, name=arte, marker_color=colors[idx % len(colors)], showlegend=False),
            row=1, col=3
        )
    
    fig_arte_caract.update_yaxes(title_text="Metros", row=1, col=1, type="log")
    fig_arte_caract.update_yaxes(title_text="kW", row=1, col=2, type="log")
    fig_arte_caract.update_yaxes(title_text="GT", row=1, col=3, type="log")
    
    fig_arte_caract.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig_arte_caract, use_container_width=True)
    
    # Scatter 3D
    st.markdown("### 🔬 Relación Tridimensional: Eslora, Potencia y Arqueo")
    
    fig_3d = px.scatter_3d(
        data_filtered.sample(min(5000, len(data_filtered))),
        x='eslora_total',
        y='potencia_kw',
        z='arqueo_gt',
        color='Tipo de Arte',
        size='Edad_buque',
        hover_data=['Comunidad Autónoma', 'material_casco'],
        labels={
            'eslora_total': 'Eslora (m)',
            'potencia_kw': 'Potencia (kW)',
            'arqueo_gt': 'Arqueo (GT)',
            'Tipo de Arte': 'Tipo de Arte'
        },
        height=700
    )
    
    fig_3d.update_traces(marker=dict(line=dict(width=0)))
    st.plotly_chart(fig_3d, use_container_width=True)

# ============================================
# TAB 5: TIPOLOGÍAS (CLUSTERING)
# ============================================
with tab5:
    st.markdown("""
    <div class="chapter-intro">
    Mediante <strong>técnicas de clustering (K-Means)</strong>, identificamos grupos naturales de buques 
    con características técnicas similares. Esto revela <strong>tipologías operativas</strong> más allá 
    de las clasificaciones tradicionales.
    </div>
    """, unsafe_allow_html=True)
    
    # Preparar datos para clustering
    features = ['eslora_total', 'potencia_kw', 'arqueo_gt', 'Edad_buque']
    df_cluster = data_filtered[features].dropna()
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster)
    
    # Método del codo
    st.markdown("### 📉 Determinación del Número Óptimo de Clusters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        inertias = []
        K_range = range(2, 11)
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
        
        fig_elbow = go.Figure()
        fig_elbow.add_trace(go.Scatter(
            x=list(K_range), 
            y=inertias, 
            mode='lines+markers',
            line=dict(color='#0066cc', width=3),
            marker=dict(size=10)
        ))
        fig_elbow.update_layout(
            title='Método del Codo para K-Means',
            xaxis_title='Número de Clusters',
            yaxis_title='Inercia (Within-Cluster Sum of Squares)',
            height=400
        )
        st.plotly_chart(fig_elbow, use_container_width=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        n_clusters = st.slider(
            "Selecciona el número de clusters:",
            min_value=2,
            max_value=8,
            value=4,
            step=1
        )
        st.markdown(f"""
        ### 🎯 Clusters Seleccionados: {n_clusters}
        
        El **método del codo** sugiere que entre 4 y 5 clusters 
        es óptimo para este dataset.
        
        **¿Qué significa?**
        - Agrupa buques con características similares
        - Identifica perfiles operativos
        - Ayuda en decisiones de gestión
        """)
    
    # Aplicar clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    data_filtered.loc[df_cluster.index, 'cluster'] = kmeans.fit_predict(X_scaled)
    
    # Visualización 3D de clusters
    st.markdown("### 🔬 Visualización de Tipologías Identificadas")
    
    df_plot = data_filtered.dropna(subset=['cluster']).copy()
    df_plot['cluster'] = df_plot['cluster'].astype(int).astype(str)
    
    fig_cluster_3d = px.scatter_3d(
        df_plot.sample(min(5000, len(df_plot))),
        x='eslora_total',
        y='potencia_kw',
        z='arqueo_gt',
        color='cluster',
        title='Tipologías de Buques Identificadas por Clustering',
        labels={
            'eslora_total': 'Eslora (m)',
            'potencia_kw': 'Potencia (kW)',
            'arqueo_gt': 'Arqueo (GT)',
            'cluster': 'Tipología'
        },
        height=700,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig_cluster_3d.update_traces(marker=dict(size=3, line=dict(width=0)))
    st.plotly_chart(fig_cluster_3d, use_container_width=True)
    
    # Caracterización de clusters
    st.markdown("### 📊 Características de Cada Tipología")
    
    cluster_stats = df_plot.groupby('cluster')[features].agg(['mean', 'median', 'count'])
    
    for cluster_id in sorted(df_plot['cluster'].unique()):
        cluster_data = df_plot[df_plot['cluster'] == cluster_id]
        
        with st.expander(f"🔍 Tipología {cluster_id} - {len(cluster_data):,} buques"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Eslora Media", f"{cluster_data['eslora_total'].mean():.1f}m")
            with col2:
                st.metric("Potencia Media", f"{cluster_data['potencia_kw'].mean():.0f}kW")
            with col3:
                st.metric("Arqueo Medio", f"{cluster_data['arqueo_gt'].mean():.1f}GT")
            with col4:
                st.metric("Edad Media", f"{cluster_data['Edad_buque'].mean():.1f} años")
            
            # Distribución de arte
            arte_dist = cluster_data['Tipo de Arte'].value_counts()
            st.markdown(f"**Tipos de Arte predominantes:** {', '.join(arte_dist.head(3).index.tolist())}")
            
            # Distribución geográfica
            ccaa_dist = cluster_data['Comunidad Autónoma'].value_counts()
            st.markdown(f"**Principales CCAA:** {', '.join(ccaa_dist.head(3).index.tolist())}")

# ============================================
# TAB 6: CONCLUSIONES
# ============================================
with tab6:
    st.markdown("""
    <div class="chapter-intro">
    Tras analizar 38 años de datos de la flota pesquera española, emergen patrones claros que 
    <strong>definen el presente y el futuro del sector</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Hallazgos Principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="recommendation-box">
        <strong>1. Envejecimiento Progresivo</strong><br>
        • Edad media de {:.1f} años<br>
        • Descenso en altas desde finales de los 90<br>
        • Necesidad urgente de renovación<br>
        <em>Impacto: Menor eficiencia, mayores costes de mantenimiento</em>
        </div>
        """.format(data_filtered['Edad_buque'].mean()), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>2. Concentración Geográfica</strong><br>
        • Galicia, Andalucía y Cataluña: 70% de la flota<br>
        • Especialización regional marcada<br>
        • Puertos tradicionales mantienen relevancia<br>
        <em>Impacto: Economía regional dependiente del sector</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>3. Diversidad de Modalidades</strong><br>
        • Artes menores: mayor número<br>
        • Arrastre: mayor tamaño y potencia<br>
        • Especialización técnica creciente<br>
        <em>Impacto: Necesidad de políticas diferenciadas</em>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="recommendation-box">
        <strong>4. Modernización Selectiva</strong><br>
        • Nuevos buques: mayor eslora y potencia<br>
        • Transición de madera a poliéster/acero<br>
        • Tecnificación progresiva<br>
        <em>Impacto: Mayor eficiencia pero menor número</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>5. Tipologías Claras</strong><br>
        • Clustering identifica 4-5 perfiles operativos<br>
        • Correlación tamaño-potencia-arqueo muy fuerte<br>
        • Diferencias entre modalidades de pesca<br>
        <em>Impacto: Base para políticas personalizadas</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>6. Impacto de Políticas UE</strong><br>
        • Reducción significativa post-1995<br>
        • Control de capacidad pesquera<br>
        • Bajas definitivas en aumento<br>
        <em>Impacto: Sostenibilidad vs viabilidad económica</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recomendaciones estratégicas
    st.markdown("### 🚀 Recomendaciones Estratégicas")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0066cc 0%, #004d99 100%); padding: 30px; border-radius: 15px; color: white;">
    <h3 style="color: white; margin-top: 0;">Plan de Acción para el Sector Pesquero</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <strong>📋 Corto Plazo (1-2 años)</strong><br>
            • Programa de incentivos para renovación de buques >25 años<br>
            • Auditoría técnica de seguridad en flota envejecida<br>
            • Formación en nuevas tecnologías para tripulaciones
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <strong>🎯 Medio Plazo (3-5 años)</strong><br>
            • Programa de desguace selectivo con compensación<br>
            • Incentivos fiscales para modernización sostenible<br>
            • Desarrollo de puertos pesqueros secundarios
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <strong>🌊 Largo Plazo (5-10 años)</strong><br>
            • Transición hacia flota 100% sostenible<br>
            • Reducción de emisiones en un 50%<br>
            • Digitalización completa del sector
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <strong>🔬 I+D+i</strong><br>
            • Inversión en acuicultura complementaria<br>
            • Desarrollo de artes de pesca selectivos<br>
            • Tecnología de monitorización en tiempo real
        </div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.9); border-radius: 10px; color: #333;">
        <strong style="color: #0066cc; font-size: 18px;">⚓ Prioridades Inmediatas:</strong><br><br>
        1. <strong>Abordar el envejecimiento</strong> con plan de renovación incentivada<br>
        2. <strong>Políticas diferenciadas</strong> por tipología (clustering) y geografía<br>
        3. <strong>Equilibrio sostenibilidad-viabilidad</strong> con apoyo a pequeña escala<br>
        4. <strong>Monitorización continua</strong> de indicadores clave del sector
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Comparativa temporal
    st.markdown("### 📊 Evolución de Indicadores Clave")
    
    # Comparar periodos
    df_1987_2000 = data[data['anio_alta'].between(1987, 2000)]
    df_2001_2010 = data[data['anio_alta'].between(2001, 2010)]
    df_2011_2025 = data[data['anio_alta'].between(2011, 2025)]
    
    comparativa_data = {
        'Periodo': ['1987-2000', '2001-2010', '2011-2025'],
        'Altas Totales': [len(df_1987_2000), len(df_2001_2010), len(df_2011_2025)],
        'Eslora Media (m)': [
            df_1987_2000['eslora_total'].mean(),
            df_2001_2010['eslora_total'].mean(),
            df_2011_2025['eslora_total'].mean()
        ],
        'Potencia Media (kW)': [
            df_1987_2000['potencia_kw'].mean(),
            df_2001_2010['potencia_kw'].mean(),
            df_2011_2025['potencia_kw'].mean()
        ]
    }
    
    df_comparativa = pd.DataFrame(comparativa_data)
    
    fig_comparativa = go.Figure()
    
    fig_comparativa.add_trace(go.Bar(
        name='Altas Totales',
        x=df_comparativa['Periodo'],
        y=df_comparativa['Altas Totales'],
        yaxis='y',
        marker_color='#0066cc'
    ))
    
    fig_comparativa.add_trace(go.Scatter(
        name='Eslora Media',
        x=df_comparativa['Periodo'],
        y=df_comparativa['Eslora Media (m)'],
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#28a745', width=3),
        marker=dict(size=12)
    ))
    
    fig_comparativa.update_layout(
        title='Evolución por Periodos: Número vs Tamaño',
        xaxis_title='Periodo',
        yaxis=dict(title='Número de Altas', side='left'),
        yaxis2=dict(title='Eslora Media (m)', overlaying='y', side='right'),
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_comparativa, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    <p><strong>Dashboard Flota Pesquera Española (1987-2025)</strong></p>
    <p>Análisis de Visualización de Datos | Máster en Ciencia de Datos</p>
    <p>Dataset: 27,364 buques registrados en el RGFP | Fuente: Ministerio de Agricultura, Pesca y Alimentación</p>
</div>
""", unsafe_allow_html=True)