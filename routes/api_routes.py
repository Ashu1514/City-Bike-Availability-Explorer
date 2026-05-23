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

    response_data = {
        "city": {
            "name": selected_city.get("name"),
            "country": selected_city.get("country"),
            "latitude": selected_city.get("latitude"),
            "longitude": selected_city.get("longitude")
        },
    }

    return jsonify({
        "success": True,
        "data": response_data
    }), 200
