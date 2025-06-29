# data_core.py

import osmnx as ox
import folium

def get_green_spaces(city_name):
    """
    Fetches green space data for a given city from OpenStreetMap.
    Returns a GeoDataFrame.
    """
    print(f"Fetching data for {city_name}...")
    tags = {
        "leisure": ["park", "garden", "playground"],
        "landuse": ["forest", "grass", "recreation_ground"],
        "natural": ["wood", "scrub", "heath"],
    }
    try:
        gdf = ox.features_from_place(city_name, tags)
        print(f"Found {len(gdf)} green spaces in {city_name}.")
        return gdf
    except Exception as e:
        print(f"Could not fetch data for {city_name}. Error: {e}")
        return None # Returns None if the city is not found or an error occurs


def create_interactive_map(gdf):
    """
    Creates an interactive Folium map from a GeoDataFrame of green spaces.
    Returns the map as an HTML string.
    """
    if gdf is None or gdf.empty:
        return None

    # Finds the center of the map
    center_lat = gdf.unary_union.centroid.y
    center_lon = gdf.unary_union.centroid.x

    # Creates the map object
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Adds green spaces to the map
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': 'green',
            'color': 'darkgreen',
            'weight': 1,
            'fillOpacity': 0.7,
        }
    ).add_to(m)

    # Returns the map's HTML representation
    return m._repr_html_()