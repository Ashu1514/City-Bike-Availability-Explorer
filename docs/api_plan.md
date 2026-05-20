# API Plan
## API 1: Open-Meteo Geocoding API
Purpose:
- Search city by name
- Get latitude and longitude
- Get country and location details
## API 2: GBFS Systems List
Purpose:
- Access public mobility systems
- Find GBFS feed URLs
## API 3: GBFS Station Information
Purpose:
- Get station names
- Get station coordinates
- Get station capacity
## API 4: GBFS Station Status
Purpose:
- Get available bikes
- Get available docks
- Get station status
## Data Flow
User searches city → Flask route calls service layer → API returns JSON → data is processed → result is displayed and optionally saved in SQLite.