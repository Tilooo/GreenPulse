# analyzer/views.py

from django.shortcuts import render
from . import data_core
import logging

logger = logging.getLogger(__name__)


# --- HELPER FUNCTION ---
# This function contains the analysis logic for a SINGLE city.
# It makes main view much cleaner and avoids code duplication.
def analyze_city(city_name):
    """
    Performs a full analysis for a single city and returns the data
    in a dictionary, or an error message.
    """
    print(f"--- Starting analysis for {city_name} ---")
    try:
        # Gets green space geometries
        green_spaces_gdf = data_core.get_green_spaces(city_name)
        if green_spaces_gdf is None or green_spaces_gdf.empty:
            return None, f"Could not find park data for '{city_name}'. Please check the name."

        # Calculates statistics
        num_parks = len(green_spaces_gdf)
        total_area_sqm = green_spaces_gdf.to_crs(epsg=3857).area.sum()
        total_area_sqkm = round(total_area_sqm / 1_000_000, 2)

        # Gets population data
        population = data_core.get_city_population(city_name)

        # Calculates per-capita stats if population is available
        sqm_per_capita = None
        if population:
            sqm_per_capita = round(total_area_sqm / population, 2)

        # Creates the interactive map
        map_html = data_core.create_interactive_map(green_spaces_gdf)

        # Packages everything into a neat dictionary
        city_data = {
            'city_name': city_name,
            'num_parks': num_parks,
            'total_area': total_area_sqkm,
            'population': population,
            'sqm_per_capita': sqm_per_capita,
            'map_html': map_html,
        }

        print(f"--- Successfully finished analysis for {city_name} ---")
        return city_data, None  # Return data and no error

    except Exception as e:
        logger.error(f"An unexpected error occurred during analysis for '{city_name}': {e}")
        return None, f"An unexpected error occurred for '{city_name}'. Please try again."


def index_view(request):
    """
    Handles the main page, which now supports comparing two cities.
    """
    context = {}

    if request.method == 'POST':
        city1_name = request.POST.get('city1', '').strip()
        city2_name = request.POST.get('city2', '').strip()

        if city1_name and city2_name:
            # Runs the analysis for both cities using helper function
            city1_data, error1 = analyze_city(city1_name)
            city2_data, error2 = analyze_city(city2_name)

            # Checks for any errors
            if error1 or error2:
                # Combines any error messages to show the user
                errors = []
                if error1: errors.append(error1)
                if error2: errors.append(error2)
                context['error_message'] = " ".join(errors)
            else:
                # If everything is successful, adds the data to the context
                context['city1_data'] = city1_data
                context['city2_data'] = city2_data

    # This will render the empty form on first visit, or the results/errors after submission
    return render(request, 'analyzer/index.html', context)