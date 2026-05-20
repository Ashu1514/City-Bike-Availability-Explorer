CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT,
    latitude REAL,
    longitude REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, country)
);

CREATE TABLE IF NOT EXISTS mobility_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER,
    system_name TEXT NOT NULL,
    gbfs_url TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(city_id) REFERENCES cities(id),
    UNIQUE(system_name, gbfs_url)
);

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER,
    station_id TEXT NOT NULL,
    name TEXT,
    latitude REAL,
    longitude REAL,
    capacity INTEGER,
    is_favorite INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(system_id) REFERENCES mobility_systems(id),
    UNIQUE(system_id, station_id)
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT NOT NULL,
    system_id INTEGER,
    available_bikes INTEGER,
    available_docks INTEGER,
    is_installed INTEGER,
    is_renting INTEGER,
    is_returning INTEGER,
    snapshot_time TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(system_id) REFERENCES mobility_systems(id)
);