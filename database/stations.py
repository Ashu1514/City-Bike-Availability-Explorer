from database.db import get_connection, get_current_timestamp
import json

def save_station_information(system_id, city_name, country_code, stations):
    """
    Save station information for one GBFS system.
    """

    if not system_id or not stations:
        return
    
    connection = get_connection()
    cursor = connection.cursor()

    now = get_current_timestamp()
    for station in stations:
        cursor.execute("""
            INSERT INTO station_information (
                system_id,
                city_name,
                country_code,
                station_id,
                name,
                latitude,
                longitude,
                capacity,
                raw_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(system_id, station_id)
            DO UPDATE SET
                city_name = excluded.city_name,
                country_code = excluded.country_code,
                name = excluded.name,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                capacity = excluded.capacity,
                raw_json = excluded.raw_json,
                updated_at = excluded.updated_at
        """, (
            system_id,
            city_name,
            country_code,
            station.get("station_id"),
            station.get("name"),
            station.get("latitude"),
            station.get("longitude"),
            station.get("capacity"),
            json.dumps(station),
            now,
            now
        ))
    connection.commit()

    connection.close()

def get_station_information(system_id):
    """
    Get cached station information for one system.
    """

    if not system_id:
        return []
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            station_id,
            name,
            latitude,
            longitude,
            capacity
        FROM station_information
        WHERE system_id = ?
    """, (system_id,))
    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]

def has_station_information(system_id):
    """
    Check if station information exists for one system.
    """

    if not system_id:
        return False
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM station_information
        WHERE system_id = ?
    """, (system_id,))
    row = cursor.fetchone()

    connection.close()

    return row["count"] > 0