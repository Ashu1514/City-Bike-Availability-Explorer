from flask import Flask, render_template
from routes.api_routes import api_routes

app = Flask(__name__)

app.register_blueprint(api_routes)

@app.route("/")
def home():
    """
    Home page route.
    This will show the main city search page.
    """
    return render_template("index.html")

@app.route("/health")
def health_check():
    """
    Simple route to check if the Flask application is running.
    """
    return {
        "status": "running",
        "message": "City Bike Availability Explorer backend is working"
    }

if __name__ == "__main__":
    app.run(debug=True)