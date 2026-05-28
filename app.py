from flask import Flask, session ,request ,render_template
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
            system = gbfs_service.find_system_for_city(city)
            auto_url = system.get("auto_discovery_url")
            if not system:
                error = f'No bike system found for "{city}". Try another city.'
            else:
                try:
                    urls = gbfs_service.fetch_gbfs_feed_urls(auto_url)
                    stations_url = urls.get("station_information")
                    stations = gbfs_service.fetch_station_information(stations_url)
                    if stations:
                        total_stations = len(stations)
                        status_url = urls.get("station_status")
                        status = gbfs_service.fetch_station_status(status_url)
                        total_bikes    = sum(s["available_bikes"] for s in status)
                        print(total_bikes)

                    

                        # Station chart data
                        station_chart = [
                            {"name": s["name"]}
                            for s in stations 

                        ]
                        station_chart.sort(key=lambda x: x["bikes"], reverse=True)


                except Exception as e:
                    error = f"Error loading data: {str(e)}"
                    print(f"Error: {e}")




    return render_template(
        "index.html",
        map_html=map_html,
        error=error,
        city=city,
        total_stations=total_stations,
        view_mode=view_mode,
        vehicle_colors=vehicle_colors,
        station_chart=station_chart,
    )



if __name__ == "__main__":
    app.run(debug=True)