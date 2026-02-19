from typing import Dict, Any
from sensors import SensorObserver

class ACController:
    def __init__(self):
        self.state = "OFF"
    def update_state(self, occupied: bool, temp: float) -> str:
        if not occupied:
            self.state = "OFF"
        elif self.state == "OFF":
            self.state = "COOLING" if temp >= 28 else "STANDBY"
        elif self.state == "STANDBY":
            if temp >= 28:
                self.state = "COOLING"
        elif self.state == "COOLING":
            if temp < 24:
                self.state = "STANDBY"
        return self.state

class LightController:
    def __init__(self):
        self.state = "OFF"
    def update_state(self, occupied: bool, light_level: int) -> str:
        if occupied and light_level < 300:
            self.state = "ON"
        else:
            self.state = "OFF"
        return self.state

class RoomController(SensorObserver):
    def __init__(self, room_name: str):
        self.room_name = room_name
        self.ac = ACController()
        self.lights = LightController()
        self.current_temp = 20.0
        self.is_occupied = False
        self.current_light_level = 500
        self.manual_ac_override = None
        self.manual_light_override = None

    def update(self, sensor_data: Dict[str, Any]) -> None:
        stype = sensor_data.get('sensor_type')
        if stype == 'temperature':
            self.current_temp = sensor_data['value']
        elif stype == 'pir':
            self.is_occupied = sensor_data['occupied']
        elif stype == 'ldr':
            self.current_light_level = sensor_data['value']

    def evaluate_state(self) -> tuple:
        """Processes current sensor readings through FSMs and returns new states."""
        if self.manual_ac_override:
            ac_state = self.manual_ac_override
        else:
            ac_state = self.ac.update_state(self.is_occupied, self.current_temp)

        if self.manual_light_override:
            light_state = self.manual_light_override
        else:
            light_state = self.lights.update_state(self.is_occupied, self.current_light_level)
        
        return ac_state, light_state