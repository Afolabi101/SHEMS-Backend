import requests
import time

# Use the /api prefix consistently [cite: 34]
BASE_URL = "http://127.0.0.1:5000/api"
ROOM = "Living Room"

def start_simulation():
    print(f"--- Starting 24-Hour Architecture-Verified Simulation: {ROOM} ---")
    
    for hour in range(1, 25):
        # Sends the hour to the API to generate matching timestamps 
        response = requests.post(f"{BASE_URL}/tick", json={
            "hour": hour,
            "room_id": ROOM
        })
        
        if response.status_code == 200:
            d = response.json()['data']
            # Formatting for clear terminal output
            print(f"Hour {hour:02d}: Temp={d['temperature']:.1f}°C | AC={d['ac_state']} | Lights={d['light_state']}")
        else:
            print(f"Error at hour {hour}: {response.text}")
            break
            
        time.sleep(0.1) # Faster simulation for testing

    print("\n--- Finalizing Simulation: Reconciling Energy Windows ---")
    # Force appliances OFF at hour 25 to close usage windows for calculation [cite: 134, 189]
    requests.post(f"{BASE_URL}/override", json={"room_id": ROOM, "appliance": "AC", "state": "OFF"})
    requests.post(f"{BASE_URL}/override", json={"room_id": ROOM, "appliance": "Light", "state": "OFF"})
    requests.post(f"{BASE_URL}/tick", json={"hour": 25, "room_id": ROOM})

    print("\n--- FETCHING VERIFIED CHAPTER 3 RESULTS ---")
    energy_res = requests.get(f"{BASE_URL}/energy")
    print(energy_res.json())

if __name__ == "__main__":
    start_simulation()