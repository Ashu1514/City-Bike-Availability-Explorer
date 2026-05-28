from flask import Flask, session ,render_template
from routes.api_routes import api_routes
from services import gbfs_service
from services import nominatim_service

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

@app.route("/", methods=["GET"])
def index():
    map_html       = None
    error          = None
    city           = ""
    total_bikes    = 0
    total_stations = 0
    view_mode      = "stations"
    vehicle_colors = {}
    station_chart  = []

    city_history = session.get("city_history", [])



    return render_template(
        "index.html",
        map_html=map_html,
        error=error,
        city=city,
        total_bikes=total_bikes,
        total_stations=total_stations,
        view_mode=view_mode,
        vehicle_colors=vehicle_colors,
        city_history=city_history,
        station_chart=station_chart,
    )



if __name__ == "__main__":
    app.run(debug=True)