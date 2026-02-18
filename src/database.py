import sqlite3
from datetime import datetime, timedelta  

def init_db():
    """Initializes the SQLite database and creates tables."""
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()

    # 1. sensor_log: Raw data from sensors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            sensor_type TEXT,
            value REAL,
            timestamp DATETIME
        )
    ''')

    # 2. appliance_log: Tracking when things turn ON/OFF
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appliance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            appliance TEXT,
            state TEXT,
            is_on INTEGER, -- 1 for ON, 0 for OFF
            timestamp DATETIME
        )
    ''')

    # 3. energy_log: The "Calculated" data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energy_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            appliance TEXT,
            kwh REAL,
            period_start DATETIME,
            period_end DATETIME
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

class DataLogger:
    """Observer class that logs sensor data to the database."""
    def __init__(self, db_name='smarthome.db'):
        self.db_name = db_name

    def update(self, room_id, sensor_type, value):
        """This method is called automatically by the Sensor Subject."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_log (room_id, sensor_type, value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (room_id, sensor_type, value, timestamp))
        
        conn.commit()
        conn.close()
        print(f"[Log] Recorded {sensor_type} in {room_id}: {value}")

def calculate_energy(room_id, appliance):
    """Calculates kWh based on appliance ON/OFF duration."""
    POWER_RATINGS = {
        "AC": 1.5,
        "Light": 0.06
    }
    
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT state, is_on, timestamp FROM appliance_log 
        WHERE room_id = ? AND appliance = ? 
        ORDER BY timestamp ASC
    ''', (room_id, appliance))
    
    logs = cursor.fetchall()
    
    if not logs:
        conn.close()
        return 0

    total_hours = 0
    last_on_time = None

    for state, is_on, timestamp in logs:
        # Robustly handle timestamp conversion
        try:
            ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        if is_on == 1: 
            last_on_time = ts
        elif is_on == 0 and last_on_time: 
            duration = ts - last_on_time
            total_hours += duration.total_seconds() / 3600
            last_on_time = None 

    kwh = total_hours * POWER_RATINGS.get(appliance, 0)
    
    cursor.execute('''
        INSERT INTO energy_log (room_id, appliance, kwh, period_start, period_end)
        VALUES (?, ?, ?, ?, ?)
    ''', (room_id, appliance, kwh, logs[0][2], logs[-1][2]))

    conn.commit()
    conn.close()
    return kwh

# This block ensures the database is created if you run this file directly
if __name__ == "__main__":
    init_db()


def get_sensor_history(room_id, sensor_type):
    """Fetches sensor reading history for the API."""
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT value, timestamp FROM sensor_log 
        WHERE room_id = ? AND sensor_type = ? 
        ORDER BY timestamp DESC LIMIT 50
    ''', (room_id, sensor_type))
    history = [{"value": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
    conn.close()
    return history

def get_connection():
    return sqlite3.connect('smarthome.db')

def log_appliance_state(room_id, appliance, state, is_on, hour):
    conn = get_connection()
    cursor = conn.cursor()
    
    # FIX 1: Check if the state actually changed before logging
    cursor.execute('''SELECT is_on FROM appliance_log 
                      WHERE room_id=? AND appliance=? 
                      ORDER BY timestamp DESC LIMIT 1''', (room_id, appliance))
    last_entry = cursor.fetchone()
    
    if last_entry and last_entry[0] == (1 if is_on else 0):
        conn.close()
        return # Don't log if the state is the same!

    # FIX 2: Use consistent Simulated Time
    sim_time = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=(24-hour))
    timestamp = sim_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    cursor.execute('''INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp)
                      VALUES (?, ?, ?, ?, ?)''', (room_id, appliance, state, 1 if is_on else 0, timestamp))
    conn.commit()
    conn.close()



def calculate_total_energy():
    """Aggregates energy data for the baseline comparison in Chapter 3."""
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(kwh) FROM energy_log")
    total = cursor.fetchone()[0] or 0
    
    # Get breakdown per appliance
    cursor.execute("SELECT appliance, SUM(kwh) FROM energy_log GROUP BY appliance")
    breakdown = {row[0]: round(row[1], 2) for row in cursor.fetchall()}
    
    conn.close()
    return {"total_kwh": round(total, 2), "breakdown": breakdown}

def get_db_stats():
    """Returns row counts for the /api/stats endpoint."""
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    stats = {}
    for table in ['sensor_log', 'appliance_log', 'energy_log']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    conn.close()
    return stats

    #manualreset

def reset_db():
    """Clears all logs for a fresh, clean simulation run."""
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensor_log")
    cursor.execute("DELETE FROM appliance_log")
    cursor.execute("DELETE FROM energy_log")
    conn.commit()
    conn.close()
    print("Database cleared for a fresh 24-hour simulation.")

    
    print("\n--- Simulation Complete. Fetching final numbers ---")
    # Correct these URLs to match your app.py routes
    energy_res = requests.get(f"{BASE_URL}/energy")
    print(energy_res.json())