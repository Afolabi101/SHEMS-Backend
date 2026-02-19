"""
Energy analytics module for SHEMS.
Pulls appliance ON/OFF data, calculates energy, savings, and prepares dashboard JSON.
"""
import os
import sqlite3
from datetime import datetime

# Constants
POWER_RATINGS = {"AC": 1.5, "Light": 0.06}  # kW
TARIFF_NGN_PER_KWH = 68  # Band A
OCCUPIED_HOURS = 15  # 8-22
UNOCCUPIED_HOURS = 9   # 23-7
WASTE_FRACTION = 0.3  # 30% waste when unoccupied


_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_DB_PATHS = [
    os.path.join(_PROJECT_ROOT, "smarthome.db"),
    os.path.join(_SCRIPT_DIR, "smarthome.db"),
]
DB_NAME = next((p for p in _DB_PATHS if os.path.exists(p)), _DB_PATHS[0])


def _parse_timestamp(ts_str):
    """Parse timestamp string to datetime."""
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")


def _compute_kwh_from_logs(logs, power_kw):
    """Compute total kWh from ON/OFF transition logs."""
    total_hours = 0
    last_on_time = None
    for _, is_on, timestamp in logs:
        ts = _parse_timestamp(timestamp)
        if is_on == 1:
            last_on_time = ts
        elif is_on == 0 and last_on_time:
            duration = ts - last_on_time
            total_hours += duration.total_seconds() / 3600
            last_on_time = None
    return total_hours * power_kw


def _normalize_appliance(name):
    """Map DB appliance name to standard key for power rating."""
    if not name:
        return "AC"
    n = str(name).upper()
    if n == "AC":
        return "AC"
    if "LIGHT" in n:
        return "Light"
    return "AC"  # fallback


def get_energy_by_room(db_name=DB_NAME):
    """
    Pull appliance data and compute total energy per room.
    Returns list of dicts: [{"room_id": str, "AC": float, "Light": float, "total": float}, ...]
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT room_id FROM appliance_log ORDER BY room_id")
    rooms = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT appliance FROM appliance_log")
    appliances = [r[0] for r in cursor.fetchall()] or ["AC", "Light"]

    result = []
    for room_id in rooms:
        row_data = {"room_id": room_id, "AC": 0, "Light": 0, "total": 0}
        for appliance in appliances:
            key = _normalize_appliance(appliance)
            cursor.execute(
                """
                SELECT state, is_on, timestamp FROM appliance_log
                WHERE room_id = ? AND appliance = ?
                ORDER BY timestamp ASC
                """,
                (room_id, appliance),
            )
            logs = cursor.fetchall()
            kwh = _compute_kwh_from_logs(logs, POWER_RATINGS.get(key, 0))
            row_data[key] = round(row_data[key] + kwh, 4)
        row_data["total"] = round(row_data["AC"] + row_data["Light"], 4)
        result.append(row_data)
    conn.close()
    return result


def get_energy_by_appliance(db_name=DB_NAME):
    """
    Total energy per appliance type across all rooms.
    Returns dict: {"AC": float, "Light": float, "total": float}
    """
    by_room = get_energy_by_room(db_name)
    result = {"AC": 0, "Light": 0, "total": 0}
    for r in by_room:
        result["AC"] += r["AC"]
        result["Light"] += r["Light"]
    result["AC"] = round(result["AC"], 4)
    result["Light"] = round(result["Light"], 4)
    result["total"] = round(result["AC"] + result["Light"], 4)
    return result


def get_daily_cost_ngn(db_name=DB_NAME):
    """Daily cost estimate at ₦68/kWh (Band A tariff)."""
    by_app = get_energy_by_appliance(db_name)
    return round(by_app["total"] * TARIFF_NGN_PER_KWH, 2)


def get_baseline_energy():
    """
    Without SHEMS: appliances run during all occupied time + 30% waste when unoccupied.
    Returns dict: {"AC": float, "Light": float, "total": float}
    """
    # Occupied: full usage. Unoccupied: 30% waste (left on)
    effective_hours = OCCUPIED_HOURS + (WASTE_FRACTION * UNOCCUPIED_HOURS)
    ac_kwh = round(effective_hours * POWER_RATINGS["AC"], 4)
    light_kwh = round(effective_hours * POWER_RATINGS["Light"], 4)
    return {
        "AC": ac_kwh,
        "Light": light_kwh,
        "total": round(ac_kwh + light_kwh, 4),
    }


def get_savings_comparison(db_name=DB_NAME):
    """
    Compare with SHEMS vs without SHEMS.
    Returns dict with with_shems_kwh, without_shems_kwh, saved_kwh, savings_percent.
    """
    with_shems = get_energy_by_appliance(db_name)
    without_shems = get_baseline_energy()

    with_kwh = with_shems["total"]
    without_kwh = without_shems["total"]
    saved = round(without_kwh - with_kwh, 4)
    pct = round((saved / without_kwh * 100), 1) if without_kwh > 0 else 0

    return {
        "with_shems_kwh": with_kwh,
        "without_shems_kwh": without_kwh,
        "saved_kwh": saved,
        "savings_percent": pct,
    }


def get_db_statistics(db_name=DB_NAME):
    """Readings logged, events recorded."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    stats = {}
    for table in ["sensor_log", "appliance_log", "energy_log"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    conn.close()
    return stats


def get_dashboard_payload(db_name=DB_NAME):
    """
    Full JSON payload for the dashboard.
    """
    return {
        "energy_by_room": get_energy_by_room(db_name),
        "energy_by_appliance": get_energy_by_appliance(db_name),
        "daily_cost_ngn": get_daily_cost_ngn(db_name),
        "savings": get_savings_comparison(db_name),
        "db_stats": get_db_statistics(db_name),
    }
