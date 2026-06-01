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
from database.gbfs_repository import  ( 
    check_gbfs_cache_valid, 
    save_gbfs_systems, 
    search_city_gbfs, 
    get_feed_urls, 
    save_feed_urls ) 

from database.stations import has_station_information, get_station_information, save_station_information

from database.vehicles import (
    get_missing_vehicle_type_ids, 
    save_vehicle_types, 
    get_vehicle_types, 
    get_missing_pricing_plan_ids, 
    save_pricing_plans, 
    get_pricing_plans,
    generate_unique_color_hash)

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
    "Scooter":     "#476DDA",
    "Bicycle":     "#BDF6AA"
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
            print(f"{"*"*10} DB Write op save_gbfs_systems {"*"*10}")
            

            filtered_systems= []

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
                    filtered_systems.append(system)

            return []
        else:
            return search_city_gbfs(city, country_code)
    except requests.exceptions.RequestException as error:
        print("GBFS systems list error:", error)
        return []


def fetch_gbfs_feed_urls(system_id, auto_discovery_url):
    """
    Fetch gbfs.json and extract feed URLs.
    """

    if not system_id or not auto_discovery_url:
        return {}

    try:
        feed_urls = {}

        feed_urls = get_feed_urls(system_id)
        print(f"{"="*10} DB read op get_feed_urls {"="*10}")


        if len(feed_urls.keys()) <= 0:
            response = requests.get(auto_discovery_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get("data", {}).get("en", None) is None:
                feeds = data.get("data", {}).get("feeds", [])
            else:
                feeds = data.get("data", {}).get("en", {}).get("feeds", [])

            save_feed_urls(system_id, feeds)
            print(f"{"*"*10} DB Write op save_feed_urls {"*"*10}")

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

    systems = find_system_for_city(city_name, country_code)

    if len(systems) <= 0:
        return {
            "mobility_system": None,
            "summary": {
                "total_stations_returned": 0,
                "total_available_bikes": 0,
                "total_available_docks": 0
            },
            "stations": []
        }
    
    all_stations = []
    total_available_bikes = 0
    total_available_docks = 0

    max_staions = 1000

    for system in systems:
        auto_discovery_url = system.get("auto_discovery_url")
        system_id = system.get("system_id")

        feed_urls = fetch_gbfs_feed_urls(system_id, auto_discovery_url)

        if len(all_stations) > max_staions:
            continue

        if len(feed_urls.keys()) <= 0:
            continue

        station_information_url = feed_urls.get("station_information")
        station_status_url = feed_urls.get("station_status")

        station_information = []
        if has_station_information(system_id):
            station_information = get_station_information(system_id)
            print(f"{"="*10} DB Read op get_station_information {system_id} {"="*10}")
        else:
            station_information = fetch_station_information(station_information_url)
            if len(station_information) > 0:
                save_station_information(system_id, city_name, country_code, station_information)
                print(f"{"*"*10} DB Write op save_station_information {system_id} {"*"*10}")

        station_status = fetch_station_status(station_status_url)

        for station in station_information:
            station_id = station.get("station_id")
            status = station_status.get(station_id, {})

            station["available_bikes"] = status.get("available_bikes") or 0
            station["available_docks"] = status.get("available_docks") or 0
            station["is_renting"] = status.get("is_renting") or False
            station["vehicle_types"] = status.get("vehicle_types")
            station["mobility_system"] = system.get("name")

            total_available_bikes += station.get("available_bikes")
            total_available_docks += station.get("available_docks")

        remaining_limit = max_staions - len(all_stations)
        if remaining_limit > 0:
            all_stations.extend(station_information[:remaining_limit])

    return {
        "summary": {
            "total_stations_returned": len(all_stations),
            "total_available_bikes": total_available_bikes,
            "total_available_docks": total_available_docks
        },
        "stations": all_stations
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
        systems = find_system_for_city(city_name, country_code)

        if len(systems) <= 0:
            return {}, {}, {}
        
        vehicles = []
        vehicle_type_names = {}
        vehicle_colors = {}
        vehicle_types = {}

        max_vehicles = 2000
        
        for system in systems:
            auto_discovery_url = system.get("auto_discovery_url")
            system_id = system.get("system_id")

            feed_urls = fetch_gbfs_feed_urls(system_id, auto_discovery_url)

            if len(vehicles) > max_vehicles:
                continue
            if len(feed_urls.keys()) <= 0:
                continue

            types_url = feed_urls.get("vehicle_types")
            status_url = feed_urls.get("vehicle_status") or feed_urls.get("free_bike_status")
            pricing_plans_url = feed_urls.get("system_pricing_plans")

            vehicles_list = []
            if not status_url is None:
                response = requests.get(status_url, timeout=15)
                response.raise_for_status()
                data = response.json().get("data", {})
                vehicles_list = data.get("vehicles", data.get("bikes", []))

            type_ids = [vehicle.get("vehicle_type_id") for vehicle in vehicles_list]
            missing_ids = get_missing_vehicle_type_ids(system_id, type_ids)
            print(f"{"="*10} DB read op get_missing_vehicle_type_ids {"="*10}")

            types = []

            if len(missing_ids) > 0 and not types_url is None:
                response = requests.get(types_url, timeout=15)
                response.raise_for_status()
                data = response.json()
                types = data.get("data", {}).get("vehicle_types", [])
                for type_ in types:
                    name = type_.get("name", "")
                    if isinstance(name, list):
                        name = next((n["text"] for n in name if n["language"] == "en"), name[0]["text"])
                    type_.update({
                        "name": name
                    })
                    vehicle_type_names[type_.get("vehicle_type_id", "")] = name
                   
                save_vehicle_types(system_id, types)
                print(f"{"*"*10} DB Write op save_vehicle_types {"*"*10}")
            
            types = get_vehicle_types(system_id)

            print(f"{"="*10} DB read op get_vehicle_types {"="*10}")
            for type_ in types:
                tid = type_.get("vehicle_type_id", "")
                vehicle_colors[tid] = type_.get("color_hash", DEFAULT_COLOR)
                vehicle_types[tid] = type_
                vehicle_type_names[tid] = type_.get("name", DEFAULT_COLOR)


            plan_ids = [vehicle.get("pricing_plan_id") for vehicle in vehicles_list]
            missing_plan_ids = get_missing_pricing_plan_ids(plan_ids)
            print(f"{"="*10} DB read op get_missing_pricing_plan_ids {"="*10}")
            plans = []

            if len(missing_plan_ids) > 0 and not pricing_plans_url is None:
                response = requests.get(pricing_plans_url, timeout=15)
                response.raise_for_status()
                data = response.json()
                plans = data.get("data", {}).get("plans", [])
                for plan in plans:
                    name = plan.get("name", "")
                    if isinstance(name, list):
                        name = next((n["text"] for n in name if n["language"] == "en"), name[0]["text"])
                    plan.update({
                        "name": name
                    })
                save_pricing_plans(system_id, plans)
                print(f"{"*"*10} DB Write op save_pricing_plans {"*"*10}")
            else:
                plans = get_pricing_plans(system_id)
                print(f"{"="*10} DB read op get_pricing_plans {"="*10}")


            plansDict = {value.get("plan_id"):value for value in plans}
            vehicles_list = [
                v for v in vehicles_list
                if vehicle_types.get(v.get("vehicle_type_id"))
            ]
            
            for vehicle in vehicles_list:
                type_id = vehicle.get("vehicle_type_id")
                plan_id = vehicle.get("pricing_plan_id")
                vehicle.update({
                    "vehicle_type": vehicle_types.get(type_id),
                    "price_plan": plansDict.get(plan_id),
                })

            remaining_limit = max_vehicles - len(vehicles)
            if remaining_limit > 0:
                vehicles.extend(vehicles_list[:remaining_limit])
            
        return  vehicles, vehicle_type_names, vehicle_types, vehicle_colors

    except requests.exceptions.RequestException as error:
        print("Station status error:", error)
        return  {}, {}, {}

    except ValueError as error:
        print("Station status JSON parse error:", error)
        return {}, {}, {}
