# analyzer/data_core.py

import osmnx as ox
import folium
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --- HELPER FUNCTION (USED BY SELENIUM) ---
def parse_population_text(text):
    """
    A helper function to parse population strings like "1.6 million" or "1,234,567".
    """
    text = text.lower().replace(',', '').strip()

    num_part_str = re.search(r'[\d.]+', text)
    if not num_part_str:
        return None
    num_part = float(num_part_str.group(0))

    if 'million' in text:
        return int(num_part * 1_000_000)
    if 'billion' in text:
        return int(num_part * 1_000_000_000)

    # This will handle plain numbers and also extract the number from strings like '1,234[5]'
    return int(num_part)


# --- THE ROBUST SELENIUM SCRAPER ---
def get_population_with_selenium(city_name):
    """
    Uses Selenium to open a real browser, find the city's Wikipedia page,
    and extract the population from the infobox using a precise XPath.
    """
    print(f"--- Starting Selenium scraper for {city_name} ---")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None  # Initialize driver to None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        main_city_name = city_name.split(',')[0]
        search_url = f"https://en.wikipedia.org/wiki/{main_city_name.replace(' ', '_')}"
        print(f"Navigating to: {search_url}")
        driver.get(search_url)

        xpath_selector = "//th[contains(.,'Population') or contains(.,'population')]/../td"

        wait = WebDriverWait(driver, 10)
        population_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_selector)))

        for element in population_elements:
            population_text = element.text.split('[')[0].split('\n')[0]
            print(f"Found potential population text: '{population_text}'")

            population = parse_population_text(population_text)

            if population:
                print(f"Successfully parsed population: {population}")
                return population

        print(f"Could not parse a valid number from any found elements for {city_name}.")
        return None

    except Exception as e:
        print(f"Selenium scraper failed for {city_name}. Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()


# --- CORE OSMNX AND FOLIUM FUNCTIONS  ---
def get_green_spaces(city_name):
    """
    Fetches green space data for a given city from OpenStreetMap.
    """
    print(f"Fetching park data for {city_name}...")
    tags = {"leisure": ["park", "garden", "playground"], "landuse": ["forest", "grass"], "natural": ["wood"]}
    try:
        gdf = ox.features_from_place(city_name, tags)
        print(f"Found {len(gdf)} green spaces in {city_name}.")
        return gdf
    except Exception as e:
        print(f"Could not fetch park data for {city_name}. Error: {e}")
        return None


def create_interactive_map(gdf):
    """
    Creates an interactive Folium map from a GeoDataFrame.
    """
    if gdf is None or gdf.empty:
        return None
    center_lat = gdf.unary_union.centroid.y
    center_lon = gdf.unary_union.centroid.x
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {'fillColor': 'green', 'color': 'darkgreen', 'weight': 1, 'fillOpacity': 0.7}
    ).add_to(m)
    return m._repr_html_()