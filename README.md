# City Bike Availability Explorer

## Project Overview

City Bike Availability Explorer is a Flask-based academic project that allows users to search cities, explore public bike-sharing station data, view station availability on an interactive map, save favorite stations, and store availability snapshots using SQLite.

## Tech Stack

- Python
- Flask
- SQLite3
- Requests
- JSON
- Folium
- Matplotlib / Plotly
- HTML
- CSS
- Bootstrap

## Project Structure

```txt
city-bike-availability-explorer/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── db.py
│   └── schema.sql
│
├── services/
│   ├── geocoding_service.py
│   ├── gbfs_service.py
│   └── snapshot_service.py
│
├── routes/
│   ├── main_routes.py
│   ├── api_routes.py
│   └── admin_routes.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── city_results.html
│   ├── stations.html
│   ├── control_panel.html
│   └── snapshots.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── maps/
│
├── visualizations/
│   ├── charts.py
│   └── generated/
│
└── docs/
    ├── api_plan.md
    └── task_distribution.md