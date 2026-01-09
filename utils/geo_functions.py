
# ================================
# geo_functions.py
# Funciones para análisis de geodatos
# ================================

import sys
import os
import warnings
import pandas as pd
from pandas._typing import MergeHow
import geopandas as gpd
from shapely import wkt  
from shapely.geometry import Point, Polygon, MultiPolygon
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.simplefilter(action='ignore', category=UserWarning)

# ====================================
# CAPAS UTILIES PARA MAPAS
# ====================================

def gdf_paises() -> gpd.GeoDataFrame:
    """Carga capa de países del mundo como GeoDataFrame en EPSG:4326."""
    ruta_paises = Path(r"P:\Proyectos\CALCULO_CIERRES\CONTROL CALIDAD\TeoríaSIPE\Programacion\Directorio GIS con QGIS\GIS_2.0\WorldCountries\WorldCountries.shp")
    ruta_paises = Path(str(ruta_paises))  # fuerza codificación compatible
    gdf = gpd.read_file(str(ruta_paises))
    return gdf.to_crs(epsg=4326) if gdf.crs else gdf.set_crs(epsg=4326)


def gdf_gsa() -> gpd.GeoDataFrame:
    """Carga capa de GSA como GeoDataFrame en EPSG:4326."""
    ruta_gsa = r'P:\Proyectos\CALCULO_CIERRES\CONTROL CALIDAD\TeoríaSIPE\Programacion\Directorio GIS con QGIS\GIS_2.0\ZonasGSA\ZonasGSA.shp'
    gdf = gpd.read_file(ruta_gsa)
    return gdf.to_crs(epsg=4326) if gdf.crs else gdf.set_crs(epsg=4326)




# ====================================
# FUNCIONES DE GEOPANDAS / ESPACIALES
# ====================================

def import_shp_as_gpd(shapefile: str) -> gpd.GeoDataFrame:
    """Importa shapefile como GeoDataFrame con CRS EPSG:4326.

    Ejemplo:
        gdf = import_shp_as_gpd("/ruta/archivo.shp")
    """
    gdf = gpd.read_file(shapefile)
    return gdf.to_crs(epsg=4326) if gdf.crs else gdf.set_crs(epsg=4326)

def pd_to_gpd(
    df: pd.DataFrame,
    longitud_col: str = "longitude",
    latitud_col: str = "latitude",
    wkt_col: str = "Geom"
) -> gpd.GeoDataFrame:
    """
    Convierte un DataFrame a GeoDataFrame.
    - Si tiene columnas de lat/lon, crea puntos.
    - Si tiene una columna WKT (por defecto 'Geom'), la convierte a geometría shapely.
    - Devuelve siempre un GeoDataFrame con CRS = EPSG:4326.
    """

    df = df.copy()

    # Caso 1: columnas latitud/longitud
    if longitud_col in df.columns and latitud_col in df.columns:
        geometry = [Point(xy) for xy in zip(df[longitud_col], df[latitud_col])]
        return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    # Caso 2: columna WKT (Geom por defecto)
    if wkt_col in df.columns and df[wkt_col].dtype == "object":
        try:
            df["geometry"] = df[wkt_col].apply(wkt.loads) # type: ignore
            return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        except Exception as e:
            raise ValueError(f"No se pudo convertir la columna '{wkt_col}' desde WKT: {e}")

    # Caso 3: columna 'geometry' en WKT
    if "geometry" in df.columns and df["geometry"].dtype == "object":
        try:
            df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])
            return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        except Exception as e:
            raise ValueError(f"No se pudo convertir la columna 'geometry' desde WKT: {e}")

    raise ValueError("No se encontraron columnas de lat/lon, ni WKT en 'Geom', ni geometría en WKT.")



def drop_z(geom):
    """Convertir geometrías a 2D eliminando coordenada Z

    Ejemplo:
        gdf["geometry"] = gdf["geometry"].apply(drop_z)
    """
    if geom is None:
        return None
    if isinstance(geom, Polygon):
        return Polygon(
            [(x, y) for x, y, *_ in geom.exterior.coords],
            [ [(x, y) for x, y, *_ in ring.coords] for ring in geom.interiors ]
        )
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([drop_z(p) for p in geom.geoms])
    return geom


def exportar_gdf_shapefile(gdf: gpd.GeoDataFrame, path_out: str, overwrite: bool = True) -> None:
    """Exporta un GeoDataFrame a shapefile en EPSG:4326.

    Ejemplo:
        exportar_gdf_shapefile(gdf, "./salida.shp")
    """
    if gdf.empty:
        raise ValueError("GeoDataFrame vacío.")
    if not gdf.geometry.is_valid.all():
        raise ValueError("Geometrías inválidas.")

    path_out = os.path.abspath(path_out)
    if os.path.exists(path_out) and not overwrite:
        raise FileExistsError(f"'{path_out}' ya existe y overwrite=False.")

    gdf.to_crs(epsg=4326).to_file(path_out, driver='ESRI Shapefile', encoding='utf-8')