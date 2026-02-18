import random

class RoomSensors:
    def __init__(self, room_name, base_temp=25.0):
        self.room_name = room_name
        self.base_temp = base_temp
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def read_all(self, hour):
        """Simulates sensor readings based on the time of day"""
        # Simulating higher temps during the day (hours 10-16)
        temp = self.base_temp + (5.0 if 10 <= hour <= 16 else 0) + random.uniform(-1, 1)
        occupied = True if 8 <= hour <= 22 else False
        light_level = 800 if 7 <= hour <= 18 else 100
        
        for observer in self.observers:
            observer.update(temp, occupied, light_level)