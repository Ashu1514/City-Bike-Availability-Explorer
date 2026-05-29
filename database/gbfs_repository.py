from database.db import get_connection
from datetime import datetime, timedelta, timezone


def get_current_timestamp():
    """
    Return current timestamp in ISO format.
    """
    return datetime.now(timezone.utc).isoformat()

def save_gbfs_systems(systems):
    """
    Save GBFS systems list.
    """
    if not systems:
        return
    connection = get_connection()
    cursor = connection.cursor()
    now = get_current_timestamp()
    for system in systems:
        cursor.execute("""
            INSERT INTO gbfs_systems (
                system_id,
                country_code,
                name,
                location,
                url,
                auto_discovery_url,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(system_id, country_code)
            DO UPDATE SET
                name = excluded.name,
                location = excluded.location,
                url = excluded.url,
                auto_discovery_url = excluded.auto_discovery_url,
                updated_at = excluded.updated_at
        """, (
            system.get("system_id"),
            system.get("country_code"),
            system.get("name"),
            system.get("location"),
            system.get("url"),
            system.get("auto_discovery_url"),
            now,
            now
        ))
    connection.commit()
    connection.close()


def get_all_gbfs_systems():
    """
    Get all GBFS systems from SQLite.
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            system_id,
            country_code,
            name,
            location,
            url,
            auto_discovery_url
        FROM gbfs_systems
    """)
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def  check_gbfs_cache_valid(max_age_days=5):
    """
    Check if GBFS systems cache exists and is not older than max_age_days.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT updated_at
        FROM gbfs_systems
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    connection.close()

    if not row or not row["updated_at"]:
        return False
    try:
        last_updated_at = datetime.fromisoformat(row["updated_at"])
    except ValueError:
        return False
    
    cache_expiry_time = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    return last_updated_at >= cache_expiry_time

def search_city_gbfs(city_name, country_code=None):
    """
    Get one GBFS system from SQLite by city name and optional country code.
    Matching checks:
    - city_name inside location
    - city_name inside name
    - optional country_code match
    """

    if not city_name:
        return None
    
    city_name_lower = city_name.lower()
    connection = get_connection()
    cursor = connection.cursor()
    if country_code:
        cursor.execute("""
            SELECT
                system_id,
                country_code,
                name,
                location,
                url,
                auto_discovery_url
            FROM gbfs_systems
            WHERE LOWER(country_code) = LOWER(?)
            AND (
                LOWER(location) LIKE ?
                OR LOWER(name) LIKE ?
            )
            LIMIT 1
        """, (
            country_code,
            f"%{city_name_lower}%",
            f"%{city_name_lower}%"
        ))
    else:
        cursor.execute("""
            SELECT
                system_id,
                country_code,
                name,
                location,
                url,
                auto_discovery_url
            FROM gbfs_systems
            WHERE
                LOWER(location) LIKE ?
                OR LOWER(name) LIKE ?
            LIMIT 1

        """, (

            f"%{city_name_lower}%",

            f"%{city_name_lower}%"

        ))
    row = cursor.fetchone()
    connection.close()
    if not row:
        return None
    return dict(row)