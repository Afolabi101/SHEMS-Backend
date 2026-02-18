import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_simulation():
    print("Starting 24-hour rapid simulation...")
    
    # Simulate AC turning ON in the Living Room
    requests.post(f"{BASE_URL}/log/appliance", json={
        "room_id": "Living Room", "appliance": "AC", "state": "ON", "is_on": 1
    })
    
    # Simulate some sensor readings
    for i in range(5):
        requests.post(f"{BASE_URL}/log/sensor", json={
            "room_id": "Living Room", "type": "Temp", "value": 22.0 + i
        })
        time.sleep(1) 

    # Simulate AC turning OFF after 4 "simulated" hours
    requests.post(f"{BASE_URL}/log/appliance", json={
        "room_id": "Living Room", "appliance": "AC", "state": "OFF", "is_on": 0
    })
    
    print("Simulation entry complete. Check your database!")

if __name__ == "__main__":
    run_simulation()