class Appliance:
    def __init__(self, name, power):
        self.name = name
        self.power = power
        self.state = "OFF"

class RoomController:
    def __init__(self, room_name):
        self.room_name = room_name
        self.ac = Appliance("AC", 1.5)
        self.lights = Appliance("Light", 0.06)
        self.current_temp = 25.0
        self.current_light_level = 500
        self.is_occupied = False
        self.manual_ac_override = None
        self.manual_light_override = None

    def update(self, temp, occupied, light_level):
        """Called by RoomSensors (Subject) via Observer Pattern"""
        self.current_temp = temp
        self.is_occupied = occupied
        self.current_light_level = light_level

    def evaluate_state(self):
        """Logic to turn things ON/OFF based on sensor data"""
        # AC Logic
        if self.manual_ac_override:
            self.ac.state = self.manual_ac_override
        else:
            self.ac.state = "COOLING" if self.current_temp > 24 else "OFF"
            
        # Light Logic
        if self.manual_light_override:
            self.lights.state = self.manual_light_override
        else:
            self.lights.state = "ON" if self.is_occupied and self.current_light_level < 300 else "OFF"
            
        return self.ac.state, self.lights.state