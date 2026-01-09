import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings

# Configuración para que las tablas se vean bien en consola
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', '{:.2f}'.format)
warnings.filterwarnings('ignore')

def title(text):
    print(f"\n{'='*80}")
    print(f" {text.upper()}")
    print(f"{'='*80}")

def subtitle(text):
    print(f"\n--- {text} ---")

# ==========================================
# 1. CARGA Y PREPARACIÓN (Igual que tu dashboard)
# ==========================================
print("⏳ Cargando datos...")
BASE_DIR = Path(__file__).resolve().parent
DATA_CSV = BASE_DIR / "3. Datos" / "SpanishFishingFleetHistory.csv"

try:
    df = pd.read_csv(DATA_CSV)
except:
    print("❌ Error: No encuentro el CSV. Asegúrate de estar en la carpeta correcta.")
    exit()

# Conversiones
df['fc_alta_rgfp'] = pd.to_datetime(df['fc_alta_rgfp'], dayfirst=True, errors='coerce')
df['fc_estado'] = pd.to_datetime(df['fc_estado'], dayfirst=True, errors='coerce')
df['anio_alta'] = df['fc_alta_rgfp'].dt.year

# Cálculo de Edad
df['Edad_buque'] = np.where(
    df['fc_estado'].notna(),
    (df['fc_estado'] - df['fc_alta_rgfp']).dt.days / 365.25,
    (pd.Timestamp.now() - df['fc_alta_rgfp']).dt.days / 365.25
)

# Categorías (Para Tab 1)
df['categoria_eslora'] = pd.cut(
    df['eslora_total'],
    bins=[0, 10, 15, 20, 120],
    labels=['Pequeño (<10m)', 'Mediano (10-15m)', 'Grande (15-20m)', 'Muy Grande (>20m)']
)

df['categoria_edad'] = pd.cut(
    df['Edad_buque'],
    bins=[-1, 10, 20, 30, 40, 200],
    labels=['0-10 años', '11-20 años', '21-30 años', '31-40 años', '>40 años']
)

# ==========================================
# 2. EXTRACCIÓN DE DATOS POR TAB
# ==========================================

title("TAB 1: PANORAMA GENERAL")

subtitle("Métricas Globales (KPIs)")
kpis = pd.DataFrame({
    'Métrica': ['Total Buques', 'Edad Media (años)', 'Eslora Media (m)', 'Potencia Media (kW)', 'Arqueo Medio (GT)'],
    'Valor': [len(df), df['Edad_buque'].mean(), df['eslora_total'].mean(), df['potencia_kw'].mean(), df['arqueo_gt'].mean()]
})
print(kpis)

subtitle("Gráfico Pastel 1: Distribución por Tipo de Arte")
print(df['Tipo de Arte'].value_counts(normalize=True).mul(100).round(2).reset_index(name='%').head(10))

subtitle("Gráfico Pastel 2: Material del Casco")
print(df['material_casco'].value_counts(normalize=True).mul(100).round(2).reset_index(name='%'))

subtitle("Gráfico Barras 1: Categoría Eslora")
print(df['categoria_eslora'].value_counts().sort_index().reset_index(name='Conteo'))

subtitle("Gráfico Barras 2: Categoría Edad")
print(df['categoria_edad'].value_counts().sort_index().reset_index(name='Conteo'))


title("TAB 2: EVOLUCIÓN TEMPORAL")

subtitle("Gráfico Líneas: Evolución Anual (Altas, Eslora, Potencia, Arqueo)")
evolucion = df.groupby('anio_alta').agg({
    'cfr': 'count',
    'eslora_total': 'mean',
    'potencia_kw': 'mean',
    'arqueo_gt': 'mean'
}).rename(columns={'cfr': 'Num_Altas'}).sort_index()
# Mostramos resumen cada 5 años para no saturar, pero tienes la lógica
print(evolucion.iloc[::5]) 

subtitle("Gráfico Barras: Ciclos Renovación (Altas vs Bajas)")
altas = df.groupby(df['fc_alta_rgfp'].dt.year).size()
bajas = df[df['estado_rgfp'].str.contains('Baja', na=False)].groupby(df['fc_estado'].dt.year).size()
renovacion = pd.DataFrame({'Altas': altas, 'Bajas': bajas}).fillna(0).astype(int)
print(renovacion.tail(10)) # Últimos 10 años


title("TAB 3: DISTRIBUCIÓN GEOGRÁFICA")

subtitle("Ranking por Comunidad (Num Buques y Potencia Media)")
geo_stats = df.groupby('Comunidad Autónoma').agg({
    'cfr': 'count',
    'potencia_kw': 'mean',
    'Edad_buque': 'mean'
}).rename(columns={'cfr': 'Total Buques', 'potencia_kw': 'Potencia Media', 'Edad_buque': 'Edad Media'})
print(geo_stats.sort_values('Total Buques', ascending=False))

subtitle("Treemap: Top 10 Puertos con más buques")
print(df.groupby(['Comunidad Autónoma', 'Puerto']).size().reset_index(name='Num_Buques').sort_values('Num_Buques', ascending=False).head(10))


title("TAB 4: MODALIDADES DE PESCA")

subtitle("Matriz: % Tipo de Arte por Comunidad (Top 5 Artes)")
top_artes = df['Tipo de Arte'].value_counts().head(5).index
crosstab = pd.crosstab(df['Comunidad Autónoma'], df['Tipo de Arte'], normalize='index').mul(100).round(1)
print(crosstab[top_artes])

subtitle("Boxplots: Estadísticas por Tipo de Arte")
stats_arte = df.groupby('Tipo de Arte').agg({
    'eslora_total': ['mean', 'min', 'max'],
    'potencia_kw': 'mean'
}).round(1)
# Ordenamos por cantidad de buques para ver los más relevantes
top_artes_indices = df['Tipo de Arte'].value_counts().head(8).index
print(stats_arte.loc[top_artes_indices])


title("TAB 5: CLUSTERING (TIPOLOGÍAS)")

# Replicamos el clustering exacto
print("Calculando Clusters (K-Means, k=4)...")
features = ['eslora_total', 'potencia_kw', 'arqueo_gt', 'Edad_buque']
df_cluster = df[features].dropna()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_cluster)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

subtitle("Perfil de los Clusters Identificados")
perfil_clusters = df_cluster.groupby('cluster').agg({
    'eslora_total': 'mean',
    'potencia_kw': 'mean',
    'arqueo_gt': 'mean',
    'Edad_buque': ['mean', 'count']
}).round(1)
# Renombramos columnas para claridad
perfil_clusters.columns = ['Eslora Media', 'Potencia Media', 'Arqueo Medio', 'Edad Media', 'Num Buques']
print(perfil_clusters)