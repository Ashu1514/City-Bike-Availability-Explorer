from database.db import get_connection, get_current_timestamp
import json
import random

def build_in_clause(values):
    """
    Build SQLite IN clause placeholders.
    Example:
    ["a", "b", "c"] => "?,?,?"
    """

    return ",".join(["?"] * len(values))

def normalize_system_ids(system_ids):
    """
    Accept single system_id or multiple system_ids.
    Always return a clean list.
    """

    if not system_ids:
        return []

    if isinstance(system_ids, str):
        return [system_ids]

    return list(system_ids)

def generate_random_color_hash():
    """
    Generate random hex color.
    Example: #A1B2C3
    """

    return "#{:06X}".format(random.randint(0, 0xFFFFFF))


def color_hash_exists(cursor, color_hash):
    """
    Check if color hash already exists in vehicle_types table.
    """

    cursor.execute("""
        SELECT 1
        FROM vehicle_types
        WHERE color_hash = ?
        LIMIT 1
    """, (color_hash,))

    return cursor.fetchone() is not None


def generate_unique_color_hash(cursor):
    """
    Generate unique color hash that does not already exist in DB.
    """

    while True:
        color_hash = generate_random_color_hash()

        if not color_hash_exists(cursor, color_hash):
            return color_hash

def save_vehicle_types(system_id, vehicle_types = []):
    """
    Save vehicle types for one GBFS system.
    """

    if not system_id or not len(vehicle_types) > 0:
        return

    connection = get_connection()
    cursor = connection.cursor()

    now = get_current_timestamp()

    for vehicle_type in vehicle_types:
        color_hash = generate_unique_color_hash(cursor)
        raw_json = {
            **vehicle_type,
            "system_id": system_id,
            "color_hash": color_hash
        }

        cursor.execute("""
            INSERT INTO vehicle_types (
                system_id,
                vehicle_type_id,
                name,
                form_factor,
                propulsion_type,
                max_range_meters,
                color_hash,
                raw_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(system_id, vehicle_type_id)
            DO UPDATE SET
                name = excluded.name,
                form_factor = excluded.form_factor,
                propulsion_type = excluded.propulsion_type,
                max_range_meters = excluded.max_range_meters,
                raw_json = json_set(
                    excluded.raw_json,
                    '$.color_hash',
                    vehicle_types.color_hash
                ),
                updated_at = excluded.updated_at
        """, (
            system_id,
            vehicle_type.get("vehicle_type_id"),
            vehicle_type.get("name"),
            vehicle_type.get("form_factor"),
            vehicle_type.get("propulsion_type"),
            vehicle_type.get("max_range_meters"),
            color_hash,
            json.dumps(raw_json),
            now,
            now
        ))

    connection.commit()
    connection.close()

def get_vehicle_types(system_ids):
    """
    Get cached vehicle types for one or multiple GBFS systems.
    """

    system_ids = normalize_system_ids(system_ids)

    if len(system_ids) <= 0:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    placeholders = build_in_clause(system_ids)

    cursor.execute(f"""
        SELECT raw_json
        FROM vehicle_types
        WHERE system_id IN ({placeholders})
        AND (LOWER(form_factor) NOT LIKE '%car%')
    """, system_ids)

    rows = cursor.fetchall()
    connection.close()

    return [json.loads(row["raw_json"]) for row in rows]


def get_missing_vehicle_type_ids(system_id, required_type_ids = []):
    """
    Compare required vehicle type IDs with cached IDs.
    """

    if not system_id or not len(required_type_ids) > 0:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    placeholders = build_in_clause(required_type_ids)

    cursor.execute(f"""
        SELECT vehicle_type_id
        FROM vehicle_types
        WHERE system_id = ?
        AND vehicle_type_id IN ({placeholders})
    """, [system_id, *required_type_ids])

    rows = cursor.fetchall()
    connection.close()

    existing_ids = {
        row["vehicle_type_id"]
        for row in rows
    }

    return [
        type_id
        for type_id in required_type_ids
        if type_id not in existing_ids
    ]


def save_pricing_plans(system_id, pricing_plans):
    """
    Save pricing plans for one GBFS system.
    """

    if not system_id:
        return

    connection = get_connection()
    cursor = connection.cursor()
    now = get_current_timestamp()

    for plan in pricing_plans:
        cursor.execute("""
            INSERT INTO pricing_plans (
                system_id,
                plan_id,
                name,
                currency,
                price,
                raw_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(system_id, plan_id)
            DO UPDATE SET
                name = excluded.name,
                currency = excluded.currency,
                price = excluded.price,
                raw_json = excluded.raw_json,
                updated_at = excluded.updated_at
        """, (
            system_id,
            plan.get("plan_id"),
            plan.get("name"),
            plan.get("currency"),
            plan.get("price"),
            json.dumps(plan),
            now,
            now
        ))
    connection.commit()
    connection.close()

def get_pricing_plans(system_id):
    """
    Get cached pricing plans for one GBFS system.
    """

    if not system_id:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT raw_json
        FROM pricing_plans
        WHERE system_id = ?
    """, (system_id,))

    rows = cursor.fetchall()
    connection.close()

    return [json.loads(row["raw_json"]) for row in rows]


def get_missing_pricing_plan_ids(required_plan_ids=[]):
    """
    Compare required pricing plan IDs with cached IDs.
    """

    if not len(required_plan_ids) > 0:
        return []
    
    required_plan_ids = [plan_id for plan_id in required_plan_ids if plan_id]

    connection = get_connection()
    cursor = connection.cursor()

    placeholders = build_in_clause(required_plan_ids)

    cursor.execute(f"""
        SELECT plan_id
        FROM pricing_plans
        WHERE plan_id IN ({placeholders})
    """, [*required_plan_ids])

    rows = cursor.fetchall()
    connection.close()

    existing_ids = {
        row["plan_id"]
        for row in rows
    }

    return [
        plan_id
        for plan_id in required_plan_ids
        if plan_id not in existing_ids
    ]