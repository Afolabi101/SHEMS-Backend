from flask import Flask, request, jsonify
from database import DataLogger, calculate_energy
import sqlite3
from datetime import datetime

app = Flask(__name__)
logger = DataLogger()

# 1. Endpoint to log sensor data
@app.route('/log/sensor', methods=['POST'])
def log_sensor():
    data = request.json
    # Expected format: {"room_id": "Living Room", "type": "Temp", "value": 24.5}
    logger.update(data['room_id'], data['type'], data['value'])
    return jsonify({"status": "success", "message": "Sensor data logged"}), 201

# 2. Endpoint to log appliance state changes
@app.route('/log/appliance', methods=['POST'])
def log_appliance():
    data = request.json
    # Expected format: {"room_id": "Kitchen", "appliance": "lights", "state": "ON", "is_on": 1}
    conn = sqlite3.connect('smarthome.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appliance_log (room_id, appliance, state, is_on, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['room_id'], data['appliance'], data['state'], data['is_on'], datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Appliance state logged"}), 201

# 3. Endpoint to get energy report
@app.route('/report/energy/<room_id>/<appliance>', methods=['GET'])
def get_energy(room_id, appliance):
    kwh = calculate_energy(room_id, appliance)
    return jsonify({
        "room_id": room_id,
        "appliance": appliance,
        "kwh_consumed": round(kwh, 4)
    }), 200

if __name__ == '__main__':
    from database import init_db
    init_db()  # Creates tables if they don't exist
    # This line MUST be reached for the server to stay open:
    app.run(debug=True, port=5000, host='0.0.0.0')