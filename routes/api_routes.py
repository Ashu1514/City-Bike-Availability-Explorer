"""
API routes.
Purpose:
- Provide backend JSON APIs for frontend team
- Search city
- Fetch mobility system
- Fetch station information
- Fetch station status
- Add station address
"""

from flask import Blueprint, jsonify, request
from services.geocoding_service import search_city
from services.gbfs_service import get_stations_for_city
from services.nominatim_service import get_address_from_coordinates

api_routes = Blueprint("api_routes", __name__, url_prefix="/api")

@api_routes.route("/health", methods=["GET"])
def api_health():
    return jsonify({
        "success": True,
        "message": "API layer is running"
    }), 200


@api_routes.route("/city-search", methods=["GET"])
def search_cities():
    """
    Search city and return city, mobility system, summary, and stations.

    Example:
    GET /api/city-search?name=Stuttgart
    """

    city_name = request.args.get("name", "").strip()

    if not city_name:
        return jsonify({
            "success": False,
            "message": "City name is required",
            "data": None
        }), 400

    city_results = search_city(city_name)

    if not city_results:
        return jsonify({
            "success": False,
            "message": "No city found for the given name",
            "data": None
        }), 404

    selected_city = city_results[0]

    station_data = get_stations_for_city(
        city_name=selected_city.get("name"),
        country_code=selected_city.get("country_code")
    )

    response_data = {
        "city": {
            "name": selected_city.get("name"),
            "country": selected_city.get("country"),
            "latitude": selected_city.get("latitude"),
            "longitude": selected_city.get("longitude")
        },
        "mobility_system": station_data.get("mobility_system"),
        "summary": station_data.get("summary"),
        "stations": station_data.get("stations")
    }

    return jsonify({
        "success": True,
        "data": response_data
    }), 200


@api_routes.route("/address-by-coordinates", methods=["GET"])
def address_by_coordinates():
    """
    get full address by geocode coordinates using Nominatim.

    Example:
    GET /api/address-by-coordinates?lat=48.7262&long=48.7262
    """

    lat = float(request.args.get("lat", "").strip())
    lang = float(request.args.get("long", "").strip())


    if not lat or not lang:
        return jsonify({
            "success": False,
            "message": "lat and long coordinates is required",
            "data": None
        }), 400

    address = get_address_from_coordinates(
            lat,
           lang
        )


    if not address:
        return jsonify({
            "success": False,
            "message": "No address found for the given coordinates",
            "data": None
        }), 404

    response_data = {
        "address": address,
    }

    return jsonify({
        "success": True,
        "data": response_data
    }), 200