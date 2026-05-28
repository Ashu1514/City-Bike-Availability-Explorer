"""
GBFS service.

Purpose:
- Fetch public GBFS mobility system data
- Load station information
- Load station status
- Load available bikes
"""

import csv
import io
import requests
import json


GBFS_SYSTEMS_CSV_URL = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"

DEFAULT_STATION_LIMIT = 10


def fetch_gbfs_systems():
    """
    Fetch GBFS systems list.
    """

    try:
        response = requests.get(GBFS_SYSTEMS_CSV_URL, timeout=15)

        response.raise_for_status()

        csv_file = io.StringIO(response.text)
        reader = csv.DictReader(csv_file)

        systems = []

        for row in reader:
            systems.append({
                "country_code": row.get("Country Code"),
                "name": row.get("Name"),
                "location": row.get("Location"),
                "system_id": row.get("System ID"),
                "url": row.get("URL"),
                "auto_discovery_url": row.get("Auto-Discovery URL")
            })

        return systems

    except requests.exceptions.RequestException as error:
        print("GBFS systems list error:", error)
        return []


def find_system_for_city(city_name, country_code=None):
    """
    Find matching GBFS system for city.
    """

    systems = fetch_gbfs_systems()

    city_name_lower = city_name.lower()

    for system in systems:
        location = system.get("location") or ""
        name = system.get("name") or ""
        system_country_code = system.get("country_code") or ""

        location_lower = location.lower()
        name_lower = name.lower()

        country_matches = True

        if country_code:
            country_matches = system_country_code.lower() == country_code.lower()

        if country_matches and (
            city_name_lower in location_lower or city_name_lower in name_lower
        ):
            return system

    return None


def fetch_gbfs_feed_urls(auto_discovery_url):
    """
    Fetch gbfs.json and extract feed URLs.
    """

    if not auto_discovery_url:
        return {}

    try:
        response = requests.get(auto_discovery_url, timeout=15)

        response.raise_for_status()

        data = response.json()
        feeds = data.get("data", {}).get("feeds", [])

        feed_urls = {}

        for feed in feeds:
            feed_name = feed.get("name")
            feed_url = feed.get("url")

            if feed_name and feed_url:
                feed_urls[feed_name] = feed_url

        return feed_urls

    except requests.exceptions.RequestException as error:
        print("GBFS feed discovery error:", error)
        return {}

    except ValueError as error:
        print("GBFS feed JSON parse error:", error)
        return {}


def fetch_station_information(station_information_url):
    """
    Fetch station_information.json.
    """

    if not station_information_url:
        return []

    try:
        response = requests.get(station_information_url, timeout=15)

        response.raise_for_status()

        data = response.json()
        stations = data.get("data", {}).get("stations", [])

        cleaned_stations = []

        for station in stations:
            cleaned_stations.append({
                "station_id": station.get("station_id"),
                "name": station.get("name"),
                "latitude": station.get("lat"),
                "longitude": station.get("lon"),
                "capacity": station.get("capacity")
            })

        return cleaned_stations

    except requests.exceptions.RequestException as error:
        print("Station information error:", error)
        return []

    except ValueError as error:
        print("Station information JSON parse error:", error)
        return []


def fetch_station_status(station_status_url):
    """
    Fetch station_status.json.
    """

    if not station_status_url:
        return []

    try:
        response = requests.get(station_status_url, timeout=15)
        response.raise_for_status()

        data = response.json()
        stations = data.get("data", {}).get("stations", [])

        status_list = []

        for station in stations:
            station_id = station.get("station_id")

            if station_id:
                status_list.append({
                    "station_id": station_id,
                    "available_bikes": station.get(
                        "num_vehicles_available",
                        station.get("num_bikes_available", 0)
                    ),
                    "available_docks": station.get("num_docks_available"),
                    "is_installed": station.get("is_installed"),
                    "is_renting": station.get("is_renting"),
                    "is_returning": station.get("is_returning"),
                    "last_reported": station.get("last_reported")
                })

        return status_list

    except requests.exceptions.RequestException as error:
        print("Station status error:", error)
        return []

    except ValueError as error:
        print("Station status JSON parse error:", error)
        return []

def get_stations_for_city(city_name, country_code=None):
    """
    Get stations for city.

    This function returns:
    - mobility_system
    - summary
    - stations
    """

    system = find_system_for_city(city_name, country_code)

    if not system:
        return {
            "mobility_system": None,
            "summary": {
                "total_stations_returned": 0,
                "total_available_bikes": 0,
                "total_available_docks": 0
            },
            "stations": []
        }

    auto_discovery_url = system.get("auto_discovery_url")

    feed_urls = fetch_gbfs_feed_urls(auto_discovery_url)

    station_information_url = feed_urls.get("station_information")
    station_status_url = feed_urls.get("station_status")

    station_information = fetch_station_information(station_information_url)
    station_status = fetch_station_status(station_status_url)

    stations = []

    total_available_bikes = 0
    total_available_docks = 0

    for station in station_information:
        station_id = station.get("station_id")
        status = station_status.get(station_id, {})

        available_bikes = status.get("available_bikes") or 0
        available_docks = status.get("available_docks") or 0

        stations.append({
            "station_id": station_id,
            "name": station.get("name"),
            "latitude": station.get("latitude"),
            "longitude": station.get("longitude"),
            "capacity": station.get("capacity"),
            "available_bikes": available_bikes,
            "available_docks": available_docks,
        })

        total_available_bikes += available_bikes
        total_available_docks += available_docks

    return {
        "mobility_system": {
            "name": system.get("name")
        },
        "summary": {
            "total_stations_returned": len(stations),
            "total_available_bikes": total_available_bikes,
            "total_available_docks": total_available_docks
        },
        "stations": stations
    }

def get_vehicles_for_city(city_name, country_code=None):
    """
    Get vehicles for city.

    This function returns:
    - vehicle list
    - vehicle type details
    - vehicle price plan
    """

    try:
        system = find_system_for_city(city_name, country_code)

        if not system:
            return []

        auto_discovery_url = system.get("auto_discovery_url")

        feed_urls = fetch_gbfs_feed_urls(auto_discovery_url)

        types_url = feed_urls.get("vehicle_types")
        status_url = feed_urls.get("vehicle_status")
        pricing_plans_url = feed_urls.get("system_pricing_plans")

        response = requests.get(types_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        types = data.get("data", {}).get("vehicle_types", [])
        typesDict = {value.get("vehicle_type_id"):value for value in types}

        response = requests.get(pricing_plans_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        plans = data.get("data", {}).get("plans", [])
        plansDict = {value.get("plan_id"):value for value in plans}

        response = requests.get(status_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        vehicles = data.get("data", {}).get("vehicles", [])
        for vehicle in vehicles:
            type_id = vehicle.get("vehicle_type_id")
            plan_id = vehicle.get("pricing_plan_id")
            vehicle.update({
                "vehicle_types": typesDict.get(type_id),
                "price_plan": plansDict.get(plan_id),
            })

        return vehicles

    except requests.exceptions.RequestException as error:
        print("Station status error:", error)
        return {}

    except ValueError as error:
        print("Station status JSON parse error:", error)
        return {}


get_vehicles_for_city("Stuttgart", "DE")