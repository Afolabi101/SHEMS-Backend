from flask import Flask, jsonify, request

import database as db
import analytics
from control import RoomController
from sensors import RoomSensors

app = Flask(__name__)

rooms = {} 
sensors_dict = {}

# Configuration constants
BASELINE_AC_KWH = 36.0  # 24h * 1.5kW
BASELINE_LIGHT_KWH = 0.72  # 12h * 0.06kW
BASELINE_TOTAL = BASELINE_AC_KWH + BASELINE_LIGHT_KWH

@app.route('/api/status', methods=['GET'])
def get_all_status():
    """Returns the current state of all rooms."""
    status_data = {}
    for room_id, controller in rooms.items():
        status_data[room_id] = {
            "temperature": controller.current_temp,
            "occupied": controller.is_occupied,
            "light_level": controller.current_light_level,
            "ac_state": controller.ac.state,
            "light_state": controller.lights.state
        }
    return jsonify({"status": "success", "data": status_data}), 200

@app.route('/api/room/<room_id>', methods=['GET'])
def get_room_status(room_id):
    """Detailed status for a single room."""
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404
        
    controller = rooms[room_id]
    room_data = {
        "room_name": controller.room_name,
        "temperature": controller.current_temp,
        "occupied": controller.is_occupied,
        "light_level": controller.current_light_level,
        "ac_state": controller.ac.state,
        "light_state": controller.lights.state,
        "manual_ac_override": controller.manual_ac_override,
        "manual_light_override": controller.manual_light_override
    }
    return jsonify({"status": "success", "data": room_data}), 200

@app.route('/api/history/<room_id>/<sensor_type>', methods=['GET'])
def get_sensor_history(room_id, sensor_type):
    """Fetches sensor reading history from the database layer."""
    try:
        history = db.get_sensor_history(room_id, sensor_type) 
        return jsonify({"status": "success", "room": room_id, "sensor": sensor_type, "data": history}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/api/energy', methods=['GET'])
def get_energy_summary():
    """Energy consumption summary with baseline comparison."""
    try:
        energy_data = db.calculate_total_energy() 
        
        actual_total = energy_data.get("total_kwh", 0)
        saved_kwh = BASELINE_TOTAL - actual_total
        savings_percentage = (saved_kwh / BASELINE_TOTAL) * 100 if BASELINE_TOTAL > 0 else 0
        
        return jsonify({
            "status": "success", 
            "data": energy_data,
            "analysis": {
                "baseline_kwh": BASELINE_TOTAL,
                "actual_kwh": actual_total,
                "saved_kwh": round(saved_kwh, 2),
                "savings_percentage": round(savings_percentage, 1)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/api/override', methods=['POST'])
def manual_override():
    """Manual override for an appliance."""
    data = request.json
    room_id = data.get("room_id")
    appliance = data.get("appliance")
    state = data.get("state")

    if not room_id or not appliance or room_id not in rooms:
        return jsonify({"error": "Invalid room or missing fields"}), 400

    if appliance.lower() == 'ac':
        rooms[room_id].manual_ac_override = state
    elif appliance.lower() == 'light':
        rooms[room_id].manual_light_override = state
    else:
        return jsonify({"error": "Appliance must be 'ac' or 'light'"}), 400

    return jsonify({"status": "success", "message": f"{appliance} in {room_id} overridden to {state}"}), 200

@app.route('/api/tick', methods=['POST'])
def advance_simulation():
    """Advance simulation by one hour."""
    data = request.json
    hour = data.get("hour")
    room_id = data.get("room_id")

    if hour is None or not room_id:
        return jsonify({"error": "Missing 'hour' or 'room_id' parameter"}), 400

    if room_id not in rooms or room_id not in sensors_dict:
        return jsonify({"error": f"Room '{room_id}' not initialized."}), 404

    try:
        sensors_dict[room_id].read_all(hour)
        ac_state, light_state = rooms[room_id].evaluate_state()

        db.log_appliance_state(room_id, "AC", ac_state, ac_state == "COOLING", hour)
        db.log_appliance_state(room_id, "Light", light_state, light_state == "ON", hour)

        current_status = {
            "hour_simulated": hour,
            "temperature": rooms[room_id].current_temp,
            "occupied": rooms[room_id].is_occupied,
            "light_level": rooms[room_id].current_light_level,
            "ac_state": ac_state,
            "light_state": light_state
        }

        return jsonify({
            "status": "success", 
            "message": f"Simulation advanced to hour {hour}",
            "data": current_status
        }), 200

    except Exception as e:
        return jsonify({"error": f"Simulation failed at hour {hour}: {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_db_stats():
    """Database statistics."""
    try:
        stats = db.get_db_stats()
        return jsonify({"status": "success", "data": stats}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Energy analytics for dashboard: by room, by appliance, cost, savings, db stats."""
    try:
        payload = analytics.get_dashboard_payload()
        return jsonify({"status": "success", "data": payload}), 200
    except Exception as e:
        return jsonify({"error": f"Analytics error: {str(e)}"}), 500

        
if __name__ == '__main__':
    db.init_db()
    
    room_name = "Living Room"
    rooms[room_name] = RoomController(room_name)
    sensors_dict[room_name] = RoomSensors(room_name)
    
    # FIX 3: Register BOTH the controller AND the database logger
                        # --- This part goes inside the if __name__ == '__main__': block ---

    from database import DataLogger

# This 'Translator' takes the bundle of sensor data and 
# saves each piece individually to the database.
    class SensorToDatabaseAdapter:
        def __init__(self, logger, room_id):
            self.logger = logger
            self.room_id = room_id
        
        def update(self, temp, occupied, light_level):
        # Translate the bundle into three separate database entries
            self.logger.update(self.room_id, "Temperature", temp)
            self.logger.update(self.room_id, "Occupancy", 1 if occupied else 0)
            self.logger.update(self.room_id, "LightLevel", light_level)

# Setup
    db.init_db() # Create tables if they don't exist
    room_name = "Living Room"
    controller = RoomController(room_name) #
    sensors = RoomSensors(room_name) #

# Create the Adapter
    logger_instance = DataLogger() #
    db_adapter = SensorToDatabaseAdapter(logger_instance, room_name)

# Register the observers
    sensors.add_observer(controller) # Tells controller to adjust AC/Lights
    sensors.add_observer(db_adapter) # Tells adapter to save data to SQLite

    app.run(debug=True, port=5000)