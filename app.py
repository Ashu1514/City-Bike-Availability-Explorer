from flask import Flask, session ,request ,render_template,jsonify
from routes.api_routes import api_routes
from services import gbfs_service
from services import nominatim_service
from visualizations import mapbuilder

app = Flask(__name__)

app.register_blueprint(api_routes)


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
    map_html       = None
    error          = None
    city           = ""
    total_bikes    = 0
    total_stations = 0
    view_mode      = "stations"
    vehicle_colors = {}
    station_chart  = []

    

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
                    print(total_stations)
                    if total_stations:
                        total_bikes = system["summary"]["total_available_bikes"]
                        print(total_bikes)

                    

                        # Station chart data
                        station_chart = [
                            {"name": s["name"][0]["text"], "bikes": s["available_bikes"]}
                            for s in stations
                            if s["available_bikes"] > 0
                        ]
                        station_chart.sort(key=lambda x: x["bikes"], reverse=True)

                        map_html = mapbuilder.build_map(stations)


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
        # vehicle_colors=vehicle_colors,
        station_chart=station_chart,
    )



if __name__ == "__main__":
    app.run(debug=True)