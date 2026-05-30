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
from database.gbfs_repository import  ( 
    check_gbfs_cache_valid, 
    save_gbfs_systems, 
    search_city_gbfs, 
    get_feed_urls, 
    save_feed_urls ) 

from database.stations import has_station_information, get_station_information, save_station_information

GBFS_SYSTEMS_CSV_URL = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"

DEFAULT_STATION_LIMIT = 10

VEHICLE_TYPE_COLORS = {
    "EFIT":        "#2980b9",
    "BOOST":       "#8e44ad",
    "ICONIC":      "#e91e8c",
    "AUH Bike":    "#16a085",
    "eScooter":    "#f39c12",
    "okaiScooter": "#e67e22",
    "METRO":       "#27ae60",
    "FIT":         "#c0392b",
    "COSMO":       "#1abc9c",
    "CHLOE":       "#d35400",
    "ASTRO":       "#7f8c8d",
}
DEFAULT_COLOR = "#555555"

def find_system_for_city(city="stuttgart", country_code=None):
    """
    Fetch GBFS systems list.
    """

    try:
        if not check_gbfs_cache_valid(5):
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

            save_gbfs_systems(systems)

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
                    city in location_lower or city in name_lower
                ):
                    return system

            return None
        else:
            return search_city_gbfs(city, country_code)
    except requests.exceptions.RequestException as error:
        print("GBFS systems list error:", error)
        return None


def fetch_gbfs_feed_urls(system_id, auto_discovery_url):
    """
    Fetch gbfs.json and extract feed URLs.
    """

    if not system_id or not auto_discovery_url:
        return {}

    try:
        feed_urls = {}

        feed_urls = get_feed_urls(system_id)

        if len(feed_urls.keys()) <= 0:
            response = requests.get(auto_discovery_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get("data", {}).get("en", None) is None:
                feeds = data.get("data", {}).get("feeds", [])
            else:
                feeds = data.get("data", {}).get("en", {}).get("feeds", [])

            save_feed_urls(system_id, feeds)

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
                "name": station.get("name")[0].get("text") if isinstance(station.get("name"), list) else station.get("name"),
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
        return {}

    try:
        response = requests.get(station_status_url, timeout=15)

        response.raise_for_status()

        data = response.json()
        stations = data.get("data", {}).get("stations", [])

        status_by_station_id = {}

        for station in stations:
            station_id = station.get("station_id")

            if station_id:
                status_by_station_id[station_id] = {
                    "available_bikes": station.get("num_bikes_available",station.get("num_vehicles_available")),
                    "available_docks": station.get("num_docks_available"),
                    "is_installed": station.get("is_installed"),
                    "is_renting": station.get("is_renting"),
                    "is_returning": station.get("is_returning"),
                    "last_reported": station.get("last_reported"),
                    "vehicle_types": station.get("vehicle_types_available"),
                }

        return status_by_station_id

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
    system_id = system.get("system_id")

    feed_urls = fetch_gbfs_feed_urls(system_id, auto_discovery_url)

    station_information_url = feed_urls.get("station_information")
    station_status_url = feed_urls.get("station_status")

    station_information = []
    if has_station_information(system_id):
        station_information = get_station_information(system_id)
    else:
        station_information = fetch_station_information(station_information_url)
        save_station_information(system_id, city_name, country_code, station_information)

    station_status = fetch_station_status(station_status_url)

    total_available_bikes = 0
    total_available_docks = 0

    for station in station_information:
        station_id = station.get("station_id")
        status = station_status.get(station_id, {})

        station["available_bikes"] = status.get("available_bikes") or 0
        station["available_docks"] = status.get("available_docks") or 0
        station["is_renting"] = status.get("is_renting") or False
        station["vehicle_types"] = status.get("vehicle_types")

        total_available_bikes += station.get("available_bikes")
        total_available_docks += station.get("available_docks")


    return {
        "mobility_system": {
            "name": system.get("name")
        },
        "summary": {
            "total_stations_returned": len(station_information),
            "total_available_bikes": total_available_bikes,
            "total_available_docks": total_available_docks
        },
        "stations": station_information
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
            return  {}, {}, {}

        auto_discovery_url = system.get("auto_discovery_url")
        system_id = system.get("system_id")

        feed_urls = fetch_gbfs_feed_urls(system_id, auto_discovery_url)

        types_url = feed_urls.get("vehicle_types")
        status_url = feed_urls.get("vehicle_status")
        pricing_plans_url = feed_urls.get("system_pricing_plans")

        response = requests.get(types_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        types = data.get("data", {}).get("vehicle_types", [])
        typesDict = {value.get("vehicle_type_id"):value for value in types}

        vtype_names = {}
        vehicle_specs = {}


        for vt in types:
            vid = vt.get("vehicle_type_id", "")
            name = vt.get("name", vid)
            
            # Safely handle localized list of strings (e.g. [{'text': 'SCOOTER', 'language': 'en'}])
            if isinstance(name, list) and len(name) > 0:
                name = next((n["text"] for n in name if n.get("language") == "en"), name[0].get("text", vid))
                
            vtype_names[vid] = name
            vehicle_specs[vid] = vt

        
        vehicle_colors = {
            vtype_names.get(vid, vid): VEHICLE_TYPE_COLORS.get(vid, DEFAULT_COLOR)
            for vid in vtype_names
        }

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

        return   vtype_names, vehicle_specs, vehicle_colors

    except requests.exceptions.RequestException as error:
        print("Station status error:", error)
        return  {}, {}, {}

    except ValueError as error:
        print("Station status JSON parse error:", error)
        return {}
    

def get_feeds(gbfs_url):
    feeds_response = requests.get(gbfs_url).json()
    data = feeds_response.get("data", {})
    if "feeds" in data:
        feeds_list = data["feeds"]
    else:
        lang_key = next(iter(data), None)
        if lang_key and "feeds" in data[lang_key]:
            feeds_list = data[lang_key]["feeds"]
        else:
            return {}
    return {f["name"]: f["url"] for f in feeds_list}

def fetch_vehicle_data(gbfs_url):
    feeds = get_feeds(gbfs_url)
    if "vehicle_types" not in feeds:
        return {}, {}, {}

    vt_data = requests.get(feeds["vehicle_types"]).json()
    vtype_names   = {}
    vehicle_specs = {}

    for vt in vt_data["data"]["vehicle_types"]:
        vid  = vt.get("vehicle_type_id", "")
        name = vt.get("name", vid)
        if isinstance(name, list):
            name = next((n["text"] for n in name if n["language"] == "en"), name[0]["text"])
        vtype_names[vid]   = name
        vehicle_specs[vid] = vt

    vehicle_colors = {
        vtype_names.get(vid, vid): VEHICLE_TYPE_COLORS.get(vid, DEFAULT_COLOR)
        for vid in vtype_names
    }

    return vtype_names, vehicle_specs, vehicle_colors