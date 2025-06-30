# analyzer/views.py

from django.shortcuts import render
from django.core.cache import cache
from . import data_core
import logging

logger = logging.getLogger(__name__)


def index_view(request):
    # Starts with a default context. This ensures all keys always exist.
    context = {
        'city_name': None,
        'num_parks': None,
        'total_area': None,
        'map_html': None,
        'population': None,
        'sqm_per_capita': None,
        'error_message': None,
    }

    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()

        if city_name:
            context['city_name'] = city_name  # Sets the city name for display even if it fails
            cache_key = f"green_space_analysis_{city_name.lower().replace(' ', '_')}"
            cached_results = cache.get(cache_key)

            if cached_results:
                print(f"Serving results for '{city_name}' from cache.")
                context.update(cached_results)
            else:
                print(f"Cache miss for '{city_name}'. Performing new analysis.")
                try:
                    green_spaces_gdf = data_core.get_green_spaces(city_name)

                    if green_spaces_gdf is not None and not green_spaces_gdf.empty:
                        # If park data is found, it starts filling the context
                        context['num_parks'] = len(green_spaces_gdf)
                        total_area_sqm = green_spaces_gdf.to_crs(epsg=3857).area.sum()
                        context['total_area'] = round(total_area_sqm / 1_000_000, 2)
                        context['map_html'] = data_core.create_interactive_map(green_spaces_gdf)

                        # To get population data
                        population = data_core.get_city_population(city_name)
                        if population:
                            context['population'] = population
                            context['sqm_per_capita'] = round(total_area_sqm / population, 2)

                        # Saves the valid results to the cache
                        # Only cache the successful data, not error messages
                        cache.set(cache_key, context, timeout=3600)
                    else:
                        context[
                            'error_message'] = f"Sorry, could not find park data for '{city_name}'. Please check the spelling or try a different city."

                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing '{city_name}': {e}")
                    context[
                        'error_message'] = "An unexpected error occurred. The server may be busy. Please try again later."

    return render(request, 'analyzer/index.html', context)