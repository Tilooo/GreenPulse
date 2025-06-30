# analyzer/data_core.py

import osmnx as ox
import folium
import wikipediaapi
import re


def parse_population_text(text):
    """
    A helper function to parse population strings like "1.6 million" or "1,234,567".
    """
    text = text.lower().replace(',', '').strip()

    # Checks for "millions"
    if 'million' in text:
        num_part = re.search(r'([\d.]+)', text)
        if num_part:
            return int(float(num_part.group(1)) * 1_000_000)

    # Checks for "billions"
    if 'billion' in text:
        num_part = re.search(r'([\d.]+)', text)
        if num_part:
            return int(float(num_part.group(1)) * 1_000_000_000)

    # Checks for a plain number
    num_part = re.search(r'(\d+)', text)
    if num_part:
        return int(num_part.group(1))

    return None


# --- MAIN FUNCTION ---
def get_city_population(city_name):
    """
    Tries to find the population of a city using the Wikipedia API.
    This version uses a more precise regex and helper function.
    """
    print(f"Fetching population for {city_name} from Wikipedia...")

    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='GreenPulse/1.0 (your-email@example.com)'
    )

    main_city_name = city_name.split(',')[0]
    page = wiki_wiki.page(main_city_name)

    if not page.exists():
        print(f"Wikipedia page for '{main_city_name}' not found.")
        return None

    # The summary is the best place to look.
    text_to_search = page.summary

    pattern = r"population of(?:.*?)((?:[\d.,]+(?:\s*million|\s*billion)?)|(?:(?:over|approximately|about|around)\s*[\d.,]+\s*(?:million|billion)?))"

    match = re.search(pattern, text_to_search, re.IGNORECASE)

    if match:
        population_str = match.group(1).strip()
        print(f"Found potential population string: '{population_str}'")

        # --- FUNCTION TO PARSE THE STRING ---
        # Keeps the logic together.
        def parse_population_string(p_str):
            p_str = p_str.lower().replace(',', '').replace('over', '').replace('approximately', '').replace('about',
                                                                                                            '').replace(
                'around', '').strip()

            num_part_str = re.search(r'[\d.]+', p_str)
            if not num_part_str:
                return None
            num_part = float(num_part_str.group(0))

            if 'million' in p_str:
                return int(num_part * 1_000_000)
            if 'billion' in p_str:
                return int(num_part * 1_000_000_000)
            return int(num_part)

        population = parse_population_string(population_str)

        if population:
            print(f"Successfully parsed population: {population}")
            return population

    print(f"Could not find a valid population figure for '{main_city_name}'.")
    return None

def get_green_spaces(city_name):
    """
    Fetches green space data for a given city from OpenStreetMap.
    Returns a GeoDataFrame.
    """
    print(f"Fetching park data for {city_name}...")
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
        print(f"Could not fetch park data for {city_name}. Error: {e}")
        return None


def create_interactive_map(gdf):
    """
    Creates an interactive Folium map from a GeoDataFrame of green spaces.
    Returns the map as an HTML string.
    """
    if gdf is None or gdf.empty:
        return None

    center_lat = gdf.unary_union.centroid.y
    center_lon = gdf.unary_union.centroid.x
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': 'green', 'color': 'darkgreen', 'weight': 1, 'fillOpacity': 0.7,
        }
    ).add_to(m)
    return m._repr_html_()