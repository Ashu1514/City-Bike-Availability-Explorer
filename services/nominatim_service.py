"""
Nominatim service.

Purpose:
- Reverse geocode station latitude and longitude
- Return readable station address
"""

import requests
import time


NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

HEADERS = {
    "User-Agent": "CityBikeAvailabilityExplorer/1.0 academic-project"
}


def get_address_from_coordinates(latitude, longitude):
    """
    Reverse geocode coordinates using Nominatim.
    """

    if latitude is None or longitude is None:
        return None

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": 1
    }

    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params=params,
            headers=HEADERS,
            timeout=10
        )

        print("Nominatim URL:", response.url)
        print("Nominatim status:", response.status_code)

        response.raise_for_status()

        data = response.json()

        # Important: Keep it slow to respect Nominatim public usage.
        time.sleep(1)

        return data.get("display_name")

    except requests.exceptions.RequestException as error:
        print("Nominatim API error:", error)
        return None

    except ValueError as error:
        print("Nominatim JSON parse error:", error)
        return None