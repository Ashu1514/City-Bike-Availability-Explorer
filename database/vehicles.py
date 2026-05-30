from database.db import get_connection, get_current_timestamp
import json

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

def save_vehicle_types(system_id, vehicle_types):
    """
    Save vehicle types for one GBFS system.
    """

    if not system_id or not vehicle_types:
        return

    connection = get_connection()
    cursor = connection.cursor()

    now = get_current_timestamp()

    for vehicle_type in vehicle_types:
        cursor.execute("""
            INSERT INTO vehicle_types (
                system_id,
                vehicle_type_id,
                name,
                form_factor,
                propulsion_type,
                max_range_meters,
                raw_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(system_id, vehicle_type_id)
            DO UPDATE SET
                name = excluded.name,
                form_factor = excluded.form_factor,
                propulsion_type = excluded.propulsion_type,
                max_range_meters = excluded.max_range_meters,
                raw_json = excluded.raw_json,
                updated_at = excluded.updated_at
        """, (
            system_id,
            vehicle_type.get("vehicle_type_id"),
            vehicle_type.get("name"),
            vehicle_type.get("form_factor"),
            vehicle_type.get("propulsion_type"),
            vehicle_type.get("max_range_meters"),
            json.dumps(vehicle_type),
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
    """, system_ids)

    rows = cursor.fetchall()
    connection.close()

    return [json.loads(row["raw_json"]) for row in rows]


def get_missing_vehicle_type_ids(system_id, required_type_ids):
    """
    Compare required vehicle type IDs with cached IDs.
    """

    if not system_id or not required_type_ids:
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

    if not system_id or not pricing_plans:
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


def get_missing_pricing_plan_ids(system_id, required_plan_ids):
    """
    Compare required pricing plan IDs with cached IDs.
    """

    if not system_id or not required_plan_ids:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    placeholders = build_in_clause(required_plan_ids)

    cursor.execute(f"""
        SELECT plan_id
        FROM pricing_plans
        WHERE system_id = ?
        AND plan_id IN ({placeholders})
    """, [system_id, *required_plan_ids])

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