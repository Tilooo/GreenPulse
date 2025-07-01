# analyzer/views.py

from django.shortcuts import render
from . import data_core
import logging
from . import ai_analyzer

logger = logging.getLogger(__name__)


# --- HELPER FUNCTION ---
# This function contains the analysis logic for a SINGLE city.
# It makes main view much cleaner and avoids code duplication.
def analyze_city(city_name):
    """
    Performs a full analysis for a single city and returns the data
    in a dictionary, or an error message.
    """
    city_data, error = ai_analyzer.get_analysis_for_city(city_name)

    # To generate a map, does this based on the city name.
    if city_data:
        city_data['map_html'] = data_core.generate_map_for_city(city_name)

    return city_data, error


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