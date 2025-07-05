# analyzer/views.py

from django.shortcuts import render
from . import data_core
from . import ai_analyzer
import logging

logger = logging.getLogger(__name__)


def analyze_city(city_name):
    """
    Performs a full analysis for a single city. It gets all statistics
    from the AI and then generates a map with the data_core.
    """
    # Gets the complete, rich analysis from the AI. Includes the accurate official city area.
    city_data, error = ai_analyzer.get_analysis_for_city(city_name)

    # If the AI fails, stops and returns the error.
    if error:
        return None, error

    # If the AI succeeds, just needs to generate the map.
    city_data['map_html'] = data_core.generate_map_for_city(city_name)

    # Returns the complete data package.
    return city_data, None


def index_view(request):
    """
    Handles the main page, which now supports comparing two cities.
    """
    context = {}

    if request.method == 'POST':
        city1_name = request.POST.get('city1', '').strip()
        city2_name = request.POST.get('city2', '').strip()

        if city1_name and city2_name:
            city1_data, error1 = analyze_city(city1_name)
            city2_data, error2 = analyze_city(city2_name)

            if error1 or error2:
                errors = []
                if error1: errors.append(error1)
                if error2: errors.append(error2)
                context['error_message'] = " ".join(errors)
            else:
                context['city1_data'] = city1_data
                context['city2_data'] = city2_data

    return render(request, 'analyzer/index.html', context)