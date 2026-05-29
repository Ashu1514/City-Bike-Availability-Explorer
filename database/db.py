import sqlite3
from pathlib import Path

DB_PATH = Path("database/explorer.db")

def get_connection():
    """
    Create SQLite connection.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    """
    Create required GBFS cache tables.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # store gbfs_systems data for city
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gbfs_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_id TEXT,
            country_code TEXT,
            name TEXT,
            location TEXT,
            url TEXT,
            auto_discovery_url TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(system_id, country_code)
        )
    """)

    # store gbfs_feed_urls for searched city
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gbfs_feed_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_id TEXT NOT NULL,
            feed_name TEXT NOT NULL,
            feed_url TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(system_id, feed_name)
        )
    """)

    # store station_information for searched city
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS station_information (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_id TEXT NOT NULL,
            city_name TEXT NOT NULL,
            country_code TEXT,
            station_id TEXT NOT NULL,
            name TEXT,
            latitude REAL,
            longitude REAL,
            capacity INTEGER,
            raw_json TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(system_id, station_id)
        )
    """)

    # store vehicle_types for searched city
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_id TEXT NOT NULL,
            vehicle_type_id TEXT NOT NULL,
            name TEXT,
            form_factor TEXT,
            propulsion_type TEXT,
            max_range_meters INTEGER,
            raw_json TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(system_id, vehicle_type_id)
        )
    """)

    # store pricing_plans for searched city
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pricing_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            name TEXT,
            currency TEXT,
            price REAL,
            raw_json TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(system_id, plan_id)
        )
    """)
    connection.commit()
    connection.close()