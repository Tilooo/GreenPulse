# analyzer/views.py

from django.shortcuts import render
from . import data_core
from . import ai_analyzer
import logging

logger = logging.getLogger(__name__)


# --- HELPER FUNCTION ---
# This function manage the analysis for a single city.
def analyze_city(city_name):
    """
    Performs a full analysis for a single city by calling the AI and then
    adding contextual data like total city area and a map.
    """
    # Get the rich, detailed analysis from the AI first.
    city_data, error = ai_analyzer.get_analysis_for_city(city_name)

    # If the AI analysis fails for any reason, then stops here and returns the error.
    if error:
        return None, error

    # If the AI was successful, enriches the data with own calculations.
    # The total city area from OSMnx for crucial context.
    total_area = data_core.get_total_city_area(city_name)
    city_data['total_city_area'] = total_area

    # Generates the interactive map for the city.
    city_data['map_html'] = data_core.generate_map_for_city(city_name)

    # Returns the complete, enriched data package.
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

    # This will renders the empty form on first visit, or the results/errors after submission
    return render(request, 'analyzer/index.html', context)