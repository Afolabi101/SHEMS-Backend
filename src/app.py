from flask import Flask, jsonify, request
import database as db
import analytics
from control import RoomController
from sensors import RoomSensors

app = Flask(__name__)

rooms = {} 
sensors_dict = {}

BASELINE_TOTAL = 146.88 # Adjusted for 4 rooms (36.72 * 4)

@app.route('/api/energy', methods=['GET'])
def get_energy_summary():
    try:
        # 1. Clear old calculations to prevent duplicate math
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM energy_log")
        conn.commit()
        conn.close()

        # 2. Run Afolabi's energy calculator for all 4 rooms
        for room in ["Living Room", "Bedroom", "Kitchen", "Study"]:
            db.calculate_energy(room, "AC")
            db.calculate_energy(room, "Light")

        # 3. Now fetch the freshly calculated totals!
    try:
        # 1. Clear old calculations to prevent duplicate math
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM energy_log")
        conn.commit()
        conn.close()

        # 2. Run Afolabi's energy calculator for all 4 rooms
        for room in ["Living Room", "Bedroom", "Kitchen", "Study"]:
            db.calculate_energy(room, "AC")
            db.calculate_energy(room, "Light")

        # 3. Now fetch the freshly calculated totals!
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/tick', methods=['POST'])
def advance_simulation():
    data = request.json
    step = data.get("step")
    room_id = data.get("room_id")

    if step is None or not room_id:
        return jsonify({"error": "Missing 'step' or 'room_id' parameter"}), 400
    if step is None or not room_id:
        return jsonify({"error": "Missing 'step' or 'room_id' parameter"}), 400

    try:
        # Convert step (5 min increments) to fractional hours for Ridwanullah's sensors
        simulated_hour = step * 5 / 60.0

        sensors_dict[room_id].read_all(simulated_hour)
    try:
        # Convert step (5 min increments) to fractional hours for Ridwanullah's sensors
        simulated_hour = step * 5 / 60.0

        sensors_dict[room_id].read_all(simulated_hour)
        ac_state, light_state = rooms[room_id].evaluate_state()

        db.log_appliance_state(room_id, "AC", ac_state, ac_state == "COOLING", step)
        db.log_appliance_state(room_id, "Light", light_state, light_state == "ON", step)

        return jsonify({"status": "success"}), 200
        db.log_appliance_state(room_id, "AC", ac_state, ac_state == "COOLING", step)
        db.log_appliance_state(room_id, "Light", light_state, light_state == "ON", step)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ... inside advance_simulation ...

        # 1. Read sensors and decide state
        sensors_dict[room_id].read_all(simulated_hour)
        ac_state, light_state = rooms[room_id].evaluate_state()

        # ---> PASTE THIS NEW LINE HERE <---
        sensors_dict[room_id].temperature_sensor.set_ac_state(ac_state == "COOLING") 

        # 2. Log the results to the database
        db.log_appliance_state(room_id, "AC", ac_state, ac_state == "COOLING", step)
        db.log_appliance_state(room_id, "Light", light_state, light_state == "ON", step)

        # ... rest of function ...
if __name__ == '__main__':
    db.init_db()
    
    # Define the 4 rooms with their specific base temperatures
    ROOMS_CONFIG = {
        "Living Room": 25.0,
        "Bedroom": 27.0,
        "Kitchen": 30.0,
        "Study": 28.0
    }
    
    # Define the 4 rooms with their specific base temperatures
    ROOMS_CONFIG = {
        "Living Room": 25.0,
        "Bedroom": 27.0,
        "Kitchen": 30.0,
        "Study": 28.0
    }
    
    from database import DataLogger
    logger = DataLogger()

    for room_name, base_temp in ROOMS_CONFIG.items():
        rooms[room_name] = RoomController(room_name)
        sensors_dict[room_name] = RoomSensors(room_name, base_temp=base_temp)
        
        # Using Ridwanullah's exact method name
        sensors_dict[room_name].register_observer(rooms[room_name]) 
        sensors_dict[room_name].register_observer(logger)          
    
    logger = DataLogger()

    for room_name, base_temp in ROOMS_CONFIG.items():
        rooms[room_name] = RoomController(room_name)
        sensors_dict[room_name] = RoomSensors(room_name, base_temp=base_temp)
        
        # Using Ridwanullah's exact method name
        sensors_dict[room_name].register_observer(rooms[room_name]) 
        sensors_dict[room_name].register_observer(logger)          
    
    app.run(debug=True, port=5000)