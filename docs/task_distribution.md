# Task Distribution

## Project: City Bike Availability Explorer

This document explains the initial task distribution among team members for the Week 6 skeleton submission and upcoming prototype development.

---

## 1. Pranavi

### Role

**Flask Application, UI Structure, Map, Charts, and Control Panel**

### Responsibilities

- Create the Flask app skeleton
- Set up main application routes
- Create the base HTML template
- Build the home page
- Build the city search form
- Connect Flask routes with HTML templates
- Prepare station data for UI display
- Create the Folium station map
- Create the availability chart
- Add the visualization page
- Build the control panel page
- Create pages for station results and snapshot display

### Expected Files

```txt
app.py
routes/main_routes.py
templates/base.html
templates/index.html
templates/city_results.html
templates/control_panel.html
templates/stations.html
templates/snapshots.html
```

---

## 2. Ashutosh

### Role

**API Integration, Database Layer, Documentation, and Final Demo Preparation**

### Responsibilities

- Implement the Open-Meteo Geocoding API call
- Implement GBFS feed fetching
- Parse JSON responses from APIs
- Handle API errors
- Design the SQLite database schema
- Create the database connection helper
- Implement save, view, and delete database functions
- Ensure saved data remains available after server restart
- Maintain the README file
- Maintain the task distribution document
- Prepare API planning documentation
- Prepare final demo instructions
- Prepare final presentation content

### Expected Files

```txt
database/db.py
database/schema.sql
routes/admin_routes.py
visualizations/charts.py
README.md
docs/task_distribution.md
services/geocoding_service.py
services/gbfs_service.py
docs/api_plan.md
```

---

## Contribution Plan

Each team member will contribute through:

- GitHub issues
- Individual commits
- Code implementation
- Documentation updates
- Demo preparation

This ensures that both members have visible contributions in the GitHub repository.
