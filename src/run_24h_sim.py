import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def start_simulation():
    print("--- Starting 288-Step High-Fidelity Simulation ---")
    
    rooms = ["Living Room", "Bedroom", "Kitchen", "Study"]
    
    # 288 steps = 24 hours of 5-minute intervals
    for step in range(288):
        for room in rooms:
            response = requests.post(f"{BASE_URL}/tick", json={
                "step": step,
                "room_id": room
            })
            
            if response.status_code != 200:
                print(f"Error at step {step} for {room}: {response.text}")
                
        # Print a progress update every hour (every 12 steps)
        if step % 12 == 0:
            print(f"Simulating Hour {step // 12} completed...")
            time.sleep(0.05)

    print("\n--- FETCHING VERIFIED CHAPTER 3 RESULTS ---")
    energy_res = requests.get(f"{BASE_URL}/energy")
    print(energy_res.json())

if __name__ == "__main__":
    start_simulation()