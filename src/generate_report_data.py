import sqlite3
from datetime import datetime, timedelta

def generate_fake_24h_data():
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    
    # Clear old failed test data
    cursor.execute("DELETE FROM appliance_log")
    cursor.execute("DELETE FROM energy_log")
    
    # Simulate AC: ON at 10:00 AM, OFF at 4:00 PM (6 hours)
    start_ac = (datetime.now() - timedelta(days=1)).replace(hour=10, minute=0)
    end_ac = start_ac + timedelta(hours=6)
    
    cursor.execute("INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp) VALUES (?,?,?,?,?)",
                   ("Living Room", "AC", "ON", 1, start_ac.strftime('%Y-%m-%d %H:%M:%S.%f')))
    cursor.execute("INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp) VALUES (?,?,?,?,?)",
                   ("Living Room", "AC", "OFF", 0, end_ac.strftime('%Y-%m-%d %H:%M:%S.%f')))

    # Simulate Lights: ON at 6:00 PM, OFF at 10:00 PM (4 hours)
    start_lights = (datetime.now() - timedelta(days=1)).replace(hour=18, minute=0)
    end_lights = start_lights + timedelta(hours=4)
    
    cursor.execute("INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp) VALUES (?,?,?,?,?)",
                   ("Living Room", "Light", "ON", 1, start_lights.strftime('%Y-%m-%d %H:%M:%S.%f')))
    cursor.execute("INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp) VALUES (?,?,?,?,?)",
                   ("Living Room", "Light", "OFF", 0, end_lights.strftime('%Y-%m-%d %H:%M:%S.%f')))
    
    conn.commit()
    conn.close()
    print("24-Hour simulated data generated. Now triggering math...")

if __name__ == "__main__":
    generate_fake_24h_data()
    import database
    database.calculate_energy("Living Room", "AC")
    database.calculate_energy("Living Room", "Light")
    print("\n--- CHAPTER 3 VERIFIED RESULTS ---")
    print(database.calculate_total_energy())