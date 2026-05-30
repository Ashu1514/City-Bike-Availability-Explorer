from database.db import get_connection, get_current_timestamp
from datetime import datetime, timedelta, timezone

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
                id,
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
        """, (
            country_code,
            f"%{city_name_lower}%",
            f"%{city_name_lower}%"
        ))
    else:
        cursor.execute("""
            SELECT
                id,
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
        """, (

            f"%{city_name_lower}%",

            f"%{city_name_lower}%"

        ))
    rows = cursor.fetchall()
    connection.close()
    if len(rows) <= 0:
        return None
    return [dict(row) for row in rows ]

def save_feed_urls(system_id, feed_urls):
    """
    Save GBFS feed URLs for one system.
    """

    if not system_id or not feed_urls:
        return

    connection = get_connection()
    cursor = connection.cursor()
    now = get_current_timestamp()

    for feed in feed_urls:
        feed_name = feed.get("name")
        feed_url = feed.get("url")
        cursor.execute("""
            INSERT INTO gbfs_feed_urls (
                system_id,
                feed_name,
                feed_url,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(system_id, feed_name)
            DO UPDATE SET
                feed_url = excluded.feed_url,
                updated_at = excluded.updated_at
        """, (
            system_id,
            feed_name,
            feed_url,
            now,
            now
        ))

    connection.commit()
    connection.close()

def get_feed_urls(system_id):
    """
    Get feed URLs for one system.
    """

    if not system_id:
        return {}

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT feed_name, feed_url
        FROM gbfs_feed_urls
        WHERE system_id = ?
    """, (system_id,))

    rows = cursor.fetchall()
    connection.close()
    feed_urls = {}

    for row in rows:
        feed_urls[row["feed_name"]] = row["feed_url"]

    return feed_urls