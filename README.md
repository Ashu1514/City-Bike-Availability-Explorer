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

# How to Start the Project After Cloning

## Project: City Bike Availability Explorer

This guide explains how contributors can set up and run the project locally after cloning the GitHub repository.

---

## 1. Create a Virtual Environment

A virtual environment keeps project dependencies separate from the system Python installation.

### For macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### For Windows

```bash
python -m venv venv
venv\Scripts\activate
```

After activation, the terminal should show something like:

```txt
(venv)
```

---

## 2. Install Required Dependencies

Run:

```bash
pip install -r requirements.txt
```

This will install the required Python packages such as:

- Flask
- requests
- folium
- matplotlib
- plotly
- pandas

---

## 3. Start the Flask Application

Run:

```bash
python app.py
```

If the application starts successfully, the terminal should show output similar to:

```txt
* Running on http://127.0.0.1:5000
* Debug mode: on
```

---

## 4. Open the Application in Browser

Open this URL in your browser:

```txt
http://127.0.0.1:5000
```

You should see the homepage of **City Bike Availability Explorer**.

---

## 5. Check Backend Health Route

You can also test if the backend is running by opening:

```txt
http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "message": "City Bike Availability Explorer backend is working",
  "status": "running"
}
```

---

## 6. Project Folder Structure

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
```

---

## 7. Development Workflow for Contributors

Before starting work, pull the latest changes:

```bash
git pull origin main
```

Create a new branch for your task:

```bash
git checkout -b feature/your-task-name
```

After making changes:

```bash
git add .
git commit -m "Add city search API integration"
git push origin feature/your-task-name
```

Then create a Pull Request on GitHub.

---

## 9. Common Issues and Fixes

### Issue: `python` command not found

Try:

```bash
python3 app.py
```

instead of:

```bash
python app.py
```

---

### Issue: Flask is not installed

Run:

```bash
pip install -r requirements.txt
```

Make sure the virtual environment is activated before installing.

---

### Issue: Port 5000 already in use

Stop the existing process or run Flask on another port by changing the last line in `app.py`:

```python
app.run(debug=True, port=5001)
```

Then open:

```txt
http://127.0.0.1:5001
```

---

### Issue: Virtual environment is not activated

Activate it again:

For macOS / Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

---

## 10. Notes for Contributors

- Do not commit the `venv` folder.
- Do not commit database files such as `.db`.
- Use clear commit messages.
- Work on separate branches.
- Keep the README updated when setup or usage changes.
- Each member should make visible contributions through commits or documentation updates.

---

## 11. Quick Start Commands

For macOS / Linux:

```bash
git clone <repository-url>
cd city-bike-availability-explorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

For Windows:

```bash
git clone <repository-url>
cd city-bike-availability-explorer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

```txt
http://127.0.0.1:5000
```