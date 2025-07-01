# analyzer/data_core.py

import osmnx as ox
import folium


def get_total_city_area(city_name):
    """
    Gets the total area of a city in square kilometers using its boundary from OSM.
    """
    print(f"Calculating total area for {city_name}...")
    try:
        # Gets the city's boundary polygon
        gdf_city = ox.geocode_to_gdf(city_name)
        # Projects to a CRS that uses meters for accurate area calculation
        gdf_city_proj = gdf_city.to_crs(epsg=3857)
        # Calculates area in square meters and converts to square kilometers
        city_area_sqkm = gdf_city_proj.area.iloc[0] / 1_000_000
        return round(city_area_sqkm, 2)
    except Exception as e:
        print(f"Could not calculate total city area for {city_name}. Error: {e}")
        return None


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