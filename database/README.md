# Database Module Documentation

This folder contains the SQLite database layer used by the project to cache and query GBFS-related data.

The database is initialized from `app.py` by calling `init_db()` during application startup. This ensures that the required SQLite database file and tables exist before any API or service logic tries to read from or write to the cache.

---

## Purpose of the Database Layer

The database layer is mainly responsible for:

- Creating and maintaining the local SQLite database.
- Caching GBFS system discovery data.
- Storing feed URLs for each GBFS system.
- Storing station information for searched cities.
- Storing vehicle type metadata.
- Storing pricing plan metadata.
- Providing helper methods to check whether required data already exists before calling external GBFS APIs again.

This helps reduce repeated network calls, improves API response time, and keeps frequently used GBFS data locally available.

---

## Database Initialization Flow

Database initialization happens from `app.py`.

Expected startup flow:

```python
from database.db import init_db

init_db()
```

When `init_db()` runs, it creates the SQLite database at:

```text
database/explorer.db
```

If the `database` folder does not exist, it is created automatically.

The database tables are created using `CREATE TABLE IF NOT EXISTS`, so calling `init_db()` multiple times is safe. Existing tables and data are not dropped.

---

## File Overview

```text
database/
├── db.py
├── gbfs_repository.py
├── stations.py
├── vehicles.py
└── README.md
```

---

## `db.py`

### Responsibility

`db.py` is the core database setup file. It manages the SQLite connection, common timestamp generation, and schema initialization.

This file should stay focused on database infrastructure concerns only.

### Main Components

#### `DB_PATH`

```python
DB_PATH = Path("database/explorer.db")
```

Defines the SQLite database file location.

The database file is stored inside the `database` folder.

---

#### `get_connection()`

Creates and returns a SQLite connection.

Key behavior:

- Ensures the parent `database` folder exists.
- Connects to `database/explorer.db`.
- Sets `connection.row_factory = sqlite3.Row`.

Because `row_factory` is set to `sqlite3.Row`, query results can be accessed like dictionaries:

```python
row["system_id"]
row["name"]
```

This makes repository functions cleaner and easier to read.

---

#### `get_current_timestamp()`

Returns the current UTC timestamp in ISO format.

Used by repository files while saving records into `created_at` and `updated_at` fields.

Example output:

```text
2026-06-01T13:30:00.000000+00:00
```

---

#### `init_db()`

Creates all required tables for the GBFS cache.

Tables created:

- `gbfs_systems`
- `gbfs_feed_urls`
- `station_information`
- `vehicle_types`
- `pricing_plans`

This function should be called once during app startup from `app.py`.

---

## Tables Created by `db.py`

### `gbfs_systems`

Stores GBFS system discovery data.

This table is used to cache city/operator-level GBFS system records.

Important columns:

| Column | Purpose |
|---|---|
| `system_id` | Unique GBFS system identifier |
| `country_code` | Country code for the system |
| `name` | System/operator name |
| `location` | System location or city information |
| `url` | GBFS system URL |
| `auto_discovery_url` | Auto-discovery endpoint |
| `created_at` | Record creation timestamp |
| `updated_at` | Last update timestamp |

Unique constraint:

```sql
UNIQUE(system_id, country_code)
```

This prevents duplicate system records for the same country.

---

### `gbfs_feed_urls`

Stores feed URLs for a specific GBFS system.

For example, a system may expose feed URLs for:

- `station_information`
- `station_status`
- `vehicle_types`
- `system_pricing_plans`

Important columns:

| Column | Purpose |
|---|---|
| `system_id` | GBFS system identifier |
| `feed_name` | Name of the feed |
| `feed_url` | URL of the feed |
| `created_at` | Record creation timestamp |
| `updated_at` | Last update timestamp |

Unique constraint:

```sql
UNIQUE(system_id, feed_name)
```

This ensures each feed is stored only once per system.

---

### `station_information`

Stores station metadata for a GBFS system.

Important columns:

| Column | Purpose |
|---|---|
| `system_id` | GBFS system identifier |
| `city_name` | City searched by the user |
| `country_code` | Country code |
| `station_id` | Station identifier from GBFS |
| `name` | Station name |
| `latitude` | Station latitude |
| `longitude` | Station longitude |
| `capacity` | Station capacity |
| `raw_json` | Full station payload as JSON string |
| `created_at` | Record creation timestamp |
| `updated_at` | Last update timestamp |

Unique constraint:

```sql
UNIQUE(system_id, station_id)
```

This prevents duplicate stations for the same GBFS system.

---

### `vehicle_types`

Stores vehicle type metadata for GBFS systems.

Important columns:

| Column | Purpose |
|---|---|
| `system_id` | GBFS system identifier |
| `vehicle_type_id` | Vehicle type identifier from GBFS |
| `name` | Vehicle type name |
| `color_hash` | Unique generated color used for map/UI display |
| `form_factor` | Vehicle form factor, for example bicycle, scooter, moped |
| `propulsion_type` | Vehicle propulsion type |
| `max_range_meters` | Maximum range in meters |
| `raw_json` | Full vehicle type payload as JSON string |
| `created_at` | Record creation timestamp |
| `updated_at` | Last update timestamp |

Unique constraints:

```sql
UNIQUE(system_id, vehicle_type_id)
```

```sql
color_hash TEXT UNIQUE
```

The `color_hash` is unique globally in this table so that vehicle types can be visually distinguished in the UI.

---

### `pricing_plans`

Stores pricing plan metadata for GBFS systems.

Important columns:

| Column | Purpose |
|---|---|
| `system_id` | GBFS system identifier |
| `plan_id` | Pricing plan identifier |
| `name` | Pricing plan name |
| `currency` | Currency code |
| `price` | Base price |
| `raw_json` | Full pricing plan payload as JSON string |
| `created_at` | Record creation timestamp |
| `updated_at` | Last update timestamp |

Unique constraint:

```sql
UNIQUE(system_id, plan_id)
```

This prevents duplicate pricing plans for the same GBFS system.

---

## `gbfs_repository.py`

### Responsibility

`gbfs_repository.py` handles database operations related to GBFS system discovery and feed URL caching.

It acts as the repository layer for:

- Saving GBFS systems.
- Checking GBFS system cache validity.
- Searching GBFS systems by city and country.
- Saving and retrieving feed URLs for a system.

---

### `save_gbfs_systems(systems)`

Saves a list of GBFS systems into the `gbfs_systems` table.

Expected input:

```python
[
    {
        "system_id": "example_system",
        "country_code": "DE",
        "name": "Example Bike System",
        "location": "Stuttgart",
        "url": "https://example.com/gbfs.json",
        "auto_discovery_url": "https://example.com/gbfs"
    }
]
```

Behavior:

- Inserts new systems.
- Updates existing systems when `(system_id, country_code)` already exists.
- Updates `updated_at` on conflict.
- Keeps `created_at` from the original insert.

This uses SQLite upsert logic with:

```sql
ON CONFLICT(system_id, country_code)
DO UPDATE SET ...
```

---

### `check_gbfs_cache_valid(max_age_days=5)`

Checks whether the GBFS systems cache is still valid.

Behavior:

- Reads the latest `updated_at` value from `gbfs_systems`.
- Compares it with the current UTC time.
- Returns `True` if the cache is not older than `max_age_days`.
- Returns `False` if no cache exists, timestamp is invalid, or cache is expired.

Default cache validity:

```python
max_age_days = 5
```

This function is useful before deciding whether to call an external GBFS discovery API again.

---

### `search_city_gbfs(city_name, country_code=None)`

Searches locally cached GBFS systems by city name.

Matching logic:

- Checks if `city_name` exists inside `location`.
- Checks if `city_name` exists inside `name`.
- Optionally filters by `country_code`.

Returns:

```python
[
    {
        "id": 1,
        "system_id": "example_system",
        "country_code": "DE",
        "name": "Example Bike System",
        "location": "Stuttgart",
        "url": "...",
        "auto_discovery_url": "..."
    }
]
```

If nothing matches, it returns an empty list.

---

### `save_feed_urls(system_id, feed_urls)`

Saves feed URLs for a specific GBFS system into `gbfs_feed_urls`.

Expected input:

```python
[
    {
        "name": "station_information",
        "url": "https://example.com/station_information.json"
    },
    {
        "name": "vehicle_types",
        "url": "https://example.com/vehicle_types.json"
    }
]
```

Behavior:

- Inserts new feed URLs.
- Updates existing feed URLs when `(system_id, feed_name)` already exists.
- Keeps feed URLs fresh when GBFS providers change endpoints.

---

### `get_feed_urls(system_id)`

Returns feed URLs for one GBFS system.

Returns a dictionary where the key is the feed name and the value is the feed URL.

Example:

```python
{
    "station_information": "https://example.com/station_information.json",
    "vehicle_types": "https://example.com/vehicle_types.json"
}
```

This format makes it easy for service logic to access specific feeds by name.

---

## `stations.py`

### Responsibility

`stations.py` handles database operations related to station information.

It is responsible for:

- Saving station metadata.
- Reading cached station metadata.
- Checking whether station information exists for a system.

This file only handles station information, not live station status or vehicle availability.

---

### `save_station_information(system_id, city_name, country_code, stations)`

Saves station information for one GBFS system.

Expected input:

```python
[
    {
        "station_id": "station_1",
        "name": "Central Station",
        "latitude": 48.7758,
        "longitude": 9.1829,
        "capacity": 20
    }
]
```

Behavior:

- Inserts new stations.
- Updates existing stations when `(system_id, station_id)` already exists.
- Saves selected station fields into dedicated columns.
- Saves the full station object into `raw_json`.

The `raw_json` column is useful because GBFS providers may include extra fields that are not yet mapped to table columns.

---

### `get_station_information(system_id)`

Returns cached station information for one GBFS system.

Returned fields:

- `station_id`
- `name`
- `latitude`
- `longitude`
- `capacity`

Example response:

```python
[
    {
        "station_id": "station_1",
        "name": "Central Station",
        "latitude": 48.7758,
        "longitude": 9.1829,
        "capacity": 20
    }
]
```

This function intentionally returns only the normalized fields needed by the application.

---

### `has_station_information(system_id)`

Checks whether station information already exists for a given system.

Returns:

```python
True
```

or

```python
False
```

This is useful for cache-first logic. If station data already exists, the application can skip fetching `station_information` again.

---

## `vehicles.py`

### Responsibility

`vehicles.py` handles vehicle type and pricing plan database operations.

It is responsible for:

- Saving vehicle types.
- Generating unique color hashes for vehicle types.
- Reading vehicle types for one or multiple systems.
- Checking missing vehicle type IDs.
- Saving pricing plans.
- Reading pricing plans.
- Checking missing pricing plan IDs.

---

## Vehicle Helper Functions

### `build_in_clause(values)`

Builds SQLite placeholders for dynamic `IN` queries.

Example:

```python
build_in_clause(["a", "b", "c"])
```

Returns:

```text
?,?,?
```

This is used when querying multiple IDs safely with parameterized SQL.

---

### `normalize_system_ids(system_ids)`

Normalizes the `system_ids` input.

Supported input:

```python
"system_1"
```

or:

```python
["system_1", "system_2"]
```

Return value is always a list:

```python
["system_1"]
```

This allows repository functions to accept either a single system ID or multiple system IDs.

---

### `generate_random_color_hash()`

Generates a random hex color string.

Example:

```text
#A1B2C3
```

This is used for assigning a UI/map color to vehicle types.

---

### `color_hash_exists(cursor, color_hash)`

Checks whether a generated color already exists in the `vehicle_types` table.

Returns:

```python
True
```

or:

```python
False
```

---

### `generate_unique_color_hash(cursor)`

Generates a unique color hash that does not already exist in the `vehicle_types` table.

This helps avoid duplicate colors for different vehicle types.

---

## Vehicle Type Functions

### `save_vehicle_types(system_id, vehicle_types=[])`

Saves vehicle type records for one GBFS system.

Expected input:

```python
[
    {
        "vehicle_type_id": "bike",
        "name": "Bike",
        "form_factor": "bicycle",
        "propulsion_type": "human",
        "max_range_meters": None
    }
]
```

Behavior:

- Generates a unique `color_hash` for each new vehicle type.
- Saves selected fields into dedicated columns.
- Saves the full vehicle type object into `raw_json`.
- Adds `system_id` and `color_hash` into the stored `raw_json`.
- Uses upsert based on `(system_id, vehicle_type_id)`.

Important behavior during updates:

When a vehicle type already exists, the existing `color_hash` is preserved inside `raw_json`.

This avoids changing map/UI colors every time the data is refreshed.

---

### `get_vehicle_types(system_ids)`

Gets cached vehicle types for one or multiple GBFS systems.

Supported input:

```python
get_vehicle_types("system_1")
```

or:

```python
get_vehicle_types(["system_1", "system_2"])
```

Behavior:

- Normalizes single or multiple system IDs into a list.
- Queries all matching vehicle types.
- Excludes vehicle types whose `form_factor` contains `car`.
- Returns parsed `raw_json` objects.

The car filter is applied using:

```sql
AND (LOWER(form_factor) NOT LIKE '%car%')
```

This keeps the result focused on supported micromobility vehicle types instead of cars.

---

### `get_missing_vehicle_type_ids(system_id, required_type_ids=[])`

Compares required vehicle type IDs with the IDs already available in the database.

Expected input:

```python
get_missing_vehicle_type_ids(
    "system_1",
    ["bike", "scooter", "moped"]
)
```

Returns only the IDs that are missing from the cache:

```python
["moped"]
```

This is useful when vehicle data references vehicle type IDs that are not yet cached locally.

---

## Pricing Plan Functions

### `save_pricing_plans(system_id, pricing_plans)`

Saves pricing plans for one GBFS system.

Expected input:

```python
[
    {
        "plan_id": "basic_plan",
        "name": "Basic Plan",
        "currency": "EUR",
        "price": 1.5
    }
]
```

Behavior:

- Inserts new pricing plans.
- Updates existing pricing plans when `(system_id, plan_id)` already exists.
- Saves selected fields into dedicated columns.
- Saves the full pricing plan object into `raw_json`.

---

### `get_pricing_plans(system_id)`

Returns cached pricing plans for one GBFS system.

The function reads `raw_json` from the database and converts it back into Python dictionaries.

Example return value:

```python
[
    {
        "plan_id": "basic_plan",
        "name": "Basic Plan",
        "currency": "EUR",
        "price": 1.5
    }
]
```

---

### `get_missing_pricing_plan_ids(required_plan_ids=[])`

Compares required pricing plan IDs with cached pricing plan IDs.

Expected input:

```python
get_missing_pricing_plan_ids(["basic_plan", "day_pass"])
```

Returns only missing plan IDs:

```python
["day_pass"]
```

This is useful when vehicle/station data references pricing plans that are not available in the local cache yet.

---

## Data Storage Strategy

The database layer follows a mixed storage approach:

### 1. Normalized Columns

Frequently used fields are stored in dedicated columns.

Example:

```text
station_id
name
latitude
longitude
capacity
```

This makes filtering, searching, and reading common fields simple and efficient.

### 2. Raw JSON Payload

Full GBFS objects are also stored in `raw_json`.

This is useful because:

- GBFS providers may add provider-specific fields.
- The application can access unmapped fields later without changing the schema immediately.
- It reduces the risk of losing data during caching.
- It makes debugging easier because the original API payload is preserved.

---

## Cache and Upsert Strategy

Most save functions use SQLite upserts.

This means records are inserted when new and updated when they already exist.

Used conflict keys:

| Table | Conflict Key |
|---|---|
| `gbfs_systems` | `(system_id, country_code)` |
| `gbfs_feed_urls` | `(system_id, feed_name)` |
| `station_information` | `(system_id, station_id)` |
| `vehicle_types` | `(system_id, vehicle_type_id)` |
| `pricing_plans` | `(system_id, plan_id)` |

This approach keeps cache data fresh without creating duplicates.

---

## Developer Notes

- Always call `init_db()` from `app.py` before using repository functions.
- Do not create database tables inside repository files.
- Keep schema changes inside `db.py`.
- Keep domain-specific database operations inside their own repository files.
- Use parameterized SQL queries instead of string interpolation for values.
- Dynamic `IN` clauses should use generated placeholders from `build_in_clause()`.
- `raw_json` should remain valid JSON strings.
- `created_at` should represent the first insert time.
- `updated_at` should change whenever an existing record is refreshed.
- Be careful while changing unique constraints because repository upsert logic depends on them.

---

## Typical Usage Flow

A common cache-first flow looks like this:

```python
from database.db import init_db
from database.gbfs_repository import (
    check_gbfs_cache_valid,
    save_gbfs_systems,
    search_city_gbfs,
    save_feed_urls,
    get_feed_urls
)
from database.stations import (
    has_station_information,
    save_station_information,
    get_station_information
)
from database.vehicles import (
    save_vehicle_types,
    get_vehicle_types,
    save_pricing_plans,
    get_pricing_plans
)

# App startup
init_db()

# Later in service/API logic
if not check_gbfs_cache_valid():
    systems = fetch_gbfs_systems_from_external_api()
    save_gbfs_systems(systems)

systems = search_city_gbfs("Stuttgart", "DE")

for system in systems:
    system_id = system["system_id"]

    feed_urls = get_feed_urls(system_id)

    if not feed_urls:
        feed_urls = fetch_feed_urls_from_gbfs(system)
        save_feed_urls(system_id, feed_urls)

    if not has_station_information(system_id):
        stations = fetch_station_information(feed_urls["station_information"])
        save_station_information(system_id, "Stuttgart", "DE", stations)

    station_information = get_station_information(system_id)
    vehicle_types = get_vehicle_types(system_id)
    pricing_plans = get_pricing_plans(system_id)
```

---

## Summary

The database folder provides a small repository-based SQLite cache layer for GBFS data.

- `db.py` creates the database and tables.
- `gbfs_repository.py` manages GBFS systems and feed URLs.
- `stations.py` manages station information.
- `vehicles.py` manages vehicle types and pricing plans.

The design keeps database setup, GBFS discovery cache, station cache, and vehicle/pricing cache separated, making the project easier to maintain and extend.
