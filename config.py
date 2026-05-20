"""
Configuration file for the Flask application.
This file will store common configuration values such as:
- Database path
- API URLs
- Debug settings
"""
DATABASE_PATH = "city_bike_explorer.db"

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

GBFS_SYSTEMS_CSV_URL = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"