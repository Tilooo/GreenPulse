# analyzer/data_core.py

import osmnx as ox
import folium


def get_green_spaces(city_name):
    """Fetches green space data from OSM."""
    print(f"Fetching map geometries for {city_name}...")
    tags = {"leisure": ["park", "garden"], "landuse": ["forest", "grass"], "natural": ["wood"]}
    try:
        gdf = ox.features_from_place(city_name, tags)
        print(f"Found {len(gdf)} geometries for the map.")
        return gdf
    except Exception as e:
        print(f"Could not fetch map geometries for {city_name}. Error: {e}")
        return None


def create_interactive_map(gdf):
    """Creates a map from a GeoDataFrame."""
    if gdf is None or gdf.empty:
        return folium.Map(location=[0, 0], zoom_start=2)._repr_html_()

    center_lat = gdf.unary_union.centroid.y
    center_lon = gdf.unary_union.centroid.x
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': '#2a9d8f',
            'color': '#264653',
            'weight': 1,
            'fillOpacity': 0.6,
        }
    ).add_to(m)
    return m._repr_html_()


# The master function that view calls
def generate_map_for_city(city_name):
    """Master function that gets shapes and then creates the map."""
    gdf = get_green_spaces(city_name)
    return create_interactive_map(gdf)