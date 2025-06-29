# analyzer/views.py

from django.shortcuts import render
from django.core.cache import cache  # Import the cache
from . import data_core
import logging

# Gets an instance of a logger
logger = logging.getLogger(__name__)


def index_view(request):
    context = {}

    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()

        if city_name:
            # Creates a cache key for this city
            cache_key = f"green_space_analysis_{city_name.lower().replace(' ', '_')}"

            # Gets the results from the cache first
            cached_results = cache.get(cache_key)

            if cached_results:
                print(f"Serving results for '{city_name}' from cache.")
                context = cached_results
            else:
                print(f"Cache miss for '{city_name}'. Performing new analysis.")
                try:
                    # If not in cache, runs the analysis
                    green_spaces_gdf = data_core.get_green_spaces(city_name)

                    if green_spaces_gdf is not None and not green_spaces_gdf.empty:
                        num_parks = len(green_spaces_gdf)
                        total_area_sqkm = green_spaces_gdf.to_crs(epsg=3857).area.sum() / 1_000_000

                        # Prepares results to be stored
                        results = {
                            'city_name': city_name,
                            'num_parks': num_parks,
                            'total_area': round(total_area_sqkm, 2),
                            'map_html': data_core.create_interactive_map(green_spaces_gdf),
                        }

                        # Saves the new results to the cache for 1 hour (3600 seconds)
                        cache.set(cache_key, results, timeout=3600)
                        context = results
                    else:
                        context[
                            'error_message'] = f"Sorry, could not find data for '{city_name}'. Please check the spelling or try a different city."

                # 4. Catches any unexpected errors during the analysis
                except Exception as e:
                    logger.error(f"An error occurred while processing '{city_name}': {e}")
                    context[
                        'error_message'] = "An unexpected error occurred. The server may be busy. Please try again later."

    return render(request, 'analyzer/index.html', context)