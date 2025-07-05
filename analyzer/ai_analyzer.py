# analyzer/ai_analyzer.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=API_KEY)

# This is the JSON "template" for the AI to fill out
JSON_FORMAT_INSTRUCTIONS = """
{
  "city": "string (City Name, Country)",
  "officialCityAreaKm2": "number (The official administrative area of the city in square kilometers. Be as accurate as possible, for example, Vilnius is 401.)",
  "population": "number (Estimated city population)",
  "greenSpace": {
    "totalAreaKm2": "number (Total green space area in square kilometers)",
    "percentageOfCity": "number (Percentage of the city's total area that is green space)",
    "parksPer100k": "number (Number of parks per 100,000 residents)",
    "spacePerCapitaM2": "number (Square meters of green space per person)"
  },
  "summary": "string (A detailed 2-3 sentence paragraph about the city's green spaces, their quality, accessibility, and unique features.)",
  "keyMetrics": [
    { "name": "Tree Canopy Cover (%)", "value": "number (A realistic estimate)" },
    { "name": "Park Accessibility (%)", "value": "number (Est. % of residents within a 10-min walk of a park)" },
    { "name": "Main Park Example", "value": "string (Name of a major or iconic park)" }
  ]
}
"""


def get_ai_analysis_prompt(city_name):
    """Creates the full prompt to send to the Gemini AI."""
    prompt = f"""
    You are an expert urban planning and environmental analyst.
    Your task is to provide a realistic analysis of the urban green spaces in the city of {city_name}.
    Your knowledge is vast but you will generate plausible data where exact figures are not available, acting as a simulator.
    Respond ONLY with a single, perfectly formatted JSON object. Do not include markdown fences (```json), explanations, or any other text.
    The JSON object must have this exact structure:
    {JSON_FORMAT_INSTRUCTIONS}
    """
    return prompt


def get_analysis_for_city(city_name):
    """
    Calls the Gemini AI to get a full green space analysis for a city.
    Returns the data as a Python dictionary.
    """
    print(f"--- Starting AI analysis for {city_name} ---")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = get_ai_analysis_prompt(city_name)

        response = model.generate_content(prompt)

        json_text = response.text.strip()
        analysis_data = json.loads(json_text)

        print(f"--- Successfully received AI analysis for {city_name} ---")
        return analysis_data, None

    except Exception as e:
        print(f"AI analysis failed for {city_name}. Error: {e}")
        error_message = f"The AI analysis for '{city_name}' failed. The service may be busy or the city name is ambiguous. Please try again."
        return None, error_message