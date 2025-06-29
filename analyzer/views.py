# analyzer/views.py

from django.shortcuts import render

def index_view(request):
    """
    This view handles the home page, which displays the city input form.
    """
    # This line tells Django to find 'index.html' and show it to the user.
    return render(request, 'analyzer/index.html')