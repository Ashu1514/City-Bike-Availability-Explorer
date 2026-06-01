Services : 

This directory includes all services that collect API data from the sources and process it. Each service represents a particular source, from which the app uses data.


Files : 

1. gbfs_service.py

The primary data collection service collects live data of bikes and scooters' availability through the GBFS (General Bikeshare Feed Specification).GBFS is an open-source standard utilized by many bike share operators.

Functions:

- find_system_for_city(city, country_code)

**Description:** Identifies whether there are any bikeshare systems operating in the selected city.

Process description:
1. First checks the database – if data is fresh, takes it from the DB
2. Otherwise, downloads `systems.csv` from GitHub (including +1500 cities)
3. Performs a search in the Location and Name fields
4. Returns an array of all matching systems for the selected city

**Example:** 

Input:  "Berlin" 
Output: [
    { system_id: "nextbike_be", auto_discovery_url: "https://..." },
    { system_id: "donkey_berlin", auto_discovery_url: "https://..." }
]

- fetch_gbfs_feed_urls(system_id, auto_discovery_url)

**Description** Open the main GBFS starting URL and fetch all the feed URLs inside it.

**Process:**
1. Search the database; if feed URLs have been fetched previously, use them
2. Otherwise call the auto_discovery_url 
3. Support both v2 ('data.en.feeds') and v3 ('data.feeds') GBFS formats
4. Save the fetched feed URLs in database for next usage
5. Return a dictionary of feed names with corresponding URLs

**Example:**

Input:  auto_discovery_url = "https://gbfs.nextbike.net/.../gbfs.json"
Output: {
    "station_information": "https://.../station_information.json",
    "station_status":      "https://.../station_status.json",
    "vehicle_types":       "https://.../vehicle_types.json"
}


-fetch_station_information(station_information_url)

**Description:** Get the stationary details of each station in the city.

**Details returned per station:**
| Field Name   | Field Description           |
| -------------|----------------------------|
| station_id   | Id of the station          |
| name         | Name of the station        |
| latitude     | Latitude coordinate        |
| longitude    | Longitude coordinate       |
| capacity     | Total number of docks      |


- fetch_station_status(station_status_url)

**Purpose:** Gets the live bike counts at all stations.

**Fields returned per station:**
| Field Name      | Description                                         |
|-----------------|-----------------------------------------------------|
| `available_bikes`   | Number of bikes currently available for rent       |
| `available_docks`   | Number of docks to drop off a bike               |
| `is_renting`          | Is the station currently renting bikes?         |
| `is_returning`         | Can I return bikes at this station?           |
| `vehicle_types`        | Types of vehicles available                  |
| `last_reported`       | Time this information was last reported         |

Note : The station status is always fetched live, no caching happens because the number of bikes constantly changes.


- get_stations_for_city(city_name)

**Purpose:** Main API call for the **Stations map view** in the app. Retrieves the station info/status and combines them together.

**Algorithm:**

1. find_system_for_city(city)

2. For each mobility system discovered:
- fetch_gbfs_feed_urls()
- fetch_station_information() (from db if available)
- fetch_station_status() (live always)
- Merge both based on station_id

3. Return combined stations


**Returned:**

{
    "summary": {
        "total_stations_returned": 120,
        "total_available_bikes": 450,
        "total_available_docks": 300
    },
    "stations": [
        {
            "station_id": "1",
            "name": "Alexanderplatz",
            "latitude": 52.52,
            "longitude": 13.41,
            "capacity": 20,
            "available_bikes": 12,
            "available_docks": 8,
            "is_renting": True,
        }
    ]
            

- get_vehicles_for_city(city_name)

**Purpose:** Main function used by the app for **Vehicles map view**. This function returns individual vehicles rather than stations; each pin represents an actual bike or scooter.

**Process flow:**

1. find_system_for_city("Berlin")

2. For each system found:
   - Obtain free_bike_status or vehicle_status URL
   - Obtain list of individual vehicles

3. Obtain vehicle types information (range, speed, form-factor)
   - Find in database any unknown vehicle type IDs 
   - Obtain missing vehicle types from vehicle_types URL
   - Add missing types in database
    
4. Obtain pricing plan information (per ride cost)
   - Same process as above

5. Attach specifications and price plan to vehicles
        
6. Return list of vehicles


**Output:**

vehicles = [
    {
        "vehicle_id": "abc123",
        "lat": 52.52,
        "lon": 13.41,
        "vehicle_type_id": "BOOST",
        "vehicle_type": {
            "name": "BOOST",
            "form_factor": "bicycle",
            "propulsion_type": "electric_assist",
            "max_range_meters": 70000,
            "max_permitted_speed": 25
        },
        "price_plan": {
            "name": "Pay as you go",
            "price": 0.15
        }
    },
]

vehicle_type_names = { "BOOST": "BOOST", "EFIT": "EFIT" }
vehicle_types      = { "BOOST": { full specs dict } }
vehicle_colors     = { "#8e44ad", "EFIT": "#2980b9}
 
 2. Nominatim service.py 


Uses the **Nominatim API** (the free geocoding service from OpenStreetMap) to transform coordinates to addresses.

Third-party API Used

| Nominatim Reverse Geocoding | `https://nominatim.openstreetmap.org/reverse` | Transform lat/lon to street address |

Description

Once the user clicks a station pin and presses **"Load Street Address"**:
1. The lat/lon is sent to `/address` endpoint
2. `nominatim_service.get_address_from_coordinates(lat, lon)` function is triggered
3. Nominatim returns a full street address, for example, `"Alexanderplatz 1, Mitte, Berlin, 10178, Germany"`
4. Shows address in a popup window

Important Note: 
The **Nominatim** is a free API with a rate limit of 1 request per second. There is a `time.sleep(1)` to make sure we don't exceed that limit. 



