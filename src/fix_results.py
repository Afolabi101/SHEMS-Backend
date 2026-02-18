import database

# This manually triggers the math for the "Living Room" data you just simulated
print("--- Manually Triggering Energy Calculations ---")
ac_kwh = database.calculate_energy("Living Room", "AC")
light_kwh = database.calculate_energy("Living Room", "Light")

print(f"AC Calculated: {ac_kwh} kWh")
print(f"Lights Calculated: {light_kwh} kWh")

# Now check the total again
print("\n--- NEW VERIFIED RESULTS ---")
print(database.calculate_total_energy())