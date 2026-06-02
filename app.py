from flask import Flask, session ,request ,render_template,jsonify
from database.db import init_db
from services import gbfs_service
from services import nominatim_service
from visualizations import mapbuilder
from visualizations.charts import prepare_station_chart_obj, prepare_vehicle_type_chart_obj
import geocoder

app = Flask(__name__)

init_db()

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

myloc = geocoder.ip('me').latlng

@app.route("/health")
def health_check():
    """
    Simple route to check if the Flask application is running.
    """
    return {
        "status": "running",
        "message": "City Bike Availability Explorer backend is working"
    }

@app.route("/address")
def get_address():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    address = nominatim_service.get_address_from_coordinates(lat, lon)
    return jsonify({"address": address or "Address not found"})


@app.route("/", methods=["GET", "POST"])
def index():
    map_html       = mapbuilder.build_map([])
    error          = None
    city           = ""
    total_bikes    = 0
    total_stations = 0
    view_mode      = "stations"
    vehicle_colors = {}
    vehicle_type_names  = {}
    station_chart  = []
    chart_obj = {}

    if request.method == "POST":
        city      = request.form.get("city", "").strip()
        view_mode = request.form.get("view_mode", "stations")

        if city:
            system = gbfs_service.get_stations_for_city(city)
            stations = system["stations"]
            if not system:
                error = f'No bike system found for "{city}". Try another city.'
            else:
                try:
                    total_stations = system["summary"]["total_stations_returned"]
                    # print(total_stations)
                    if total_stations:
                        total_bikes = system["summary"]["total_available_bikes"]
                        # print(total_bikes)


                        # Station chart data
                        # chart_obj = prepare_station_chart_obj(stations)
                        station_chart = [
                            {"name": s['name'], "bikes": s['available_bikes']}
                            for s in stations
                            if s['available_bikes'] > 0
                        ]
                        station_chart.sort(key=lambda x: x["bikes"], reverse=True)

                        map_html = mapbuilder.build_map(stations)

                        if view_mode == "vehicles":
                            vehicles, vehicle_type_names, vehicle_types, vehicle_colors = gbfs_service.get_vehicles_for_city(city)
                            map_html = mapbuilder.build_vehicle_map(
                                vehicles,
                                vehicle_colors,
                                vehicle_type_names,
                                vehicle_types,
                            )
                            chart_obj = prepare_vehicle_type_chart_obj(vehicles, vehicle_type_names, vehicle_colors)
                        else:
                            map_html = mapbuilder.build_map(stations)
                            chart_obj = prepare_station_chart_obj(stations)
                    else:
                        error = "Found a system but couldn't load station data."


                except Exception as e:
                    error = f"Error loading data: {str(e)}"
                    print(f"Error: {e}")




    return render_template(
        "index.html",
        map_html=map_html,
        error=error,
        city=city,
        total_stations=total_stations,
        total_bikes = total_bikes,
        view_mode=view_mode,
        vehicle_colors=vehicle_colors,
        vehicle_type_names=vehicle_type_names,
        station_chart=station_chart,
        chart_obj=chart_obj
    )



if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5001, debug=True)