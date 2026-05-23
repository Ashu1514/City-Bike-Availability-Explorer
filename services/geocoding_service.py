"""
Geocoding service.
Purpose:
- Call Open-Meteo Geocoding API
- Convert city name into latitude and longitude
- Return city details in a clean JSON-friendly format
"""

import requests

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

def search_city(city_name):
    """
    Search city using Open-Meteo Geocoding API.

    Args:
        city_name (str): City name entered by user.

    Returns:
        list: Cleaned list of city results.
    """

    if not city_name:
        return []

    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(
            OPEN_METEO_GEOCODING_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        cleaned_cities = []

        for item in results:
            cleaned_cities.append({
                "name": item.get("name"),
                "country": item.get("country"),
                "country_code": item.get("country_code"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
            })

        return cleaned_cities

    except requests.exceptions.Timeout:
        return []

    except requests.exceptions.RequestException:
        return []

    except ValueError:
        return []