

```markdown
# Smart Home Energy Management System (SHEMS) - Backend & Simulation

This repository contains the core backend logic, database management, and simulation testbench for the Smart Home Energy Management System. The project focuses on optimizing energy consumption through intelligent sensor-based control and occupancy-based automation.

## 🏗️ Architecture & Design Patterns
The system is built using a **Layered Architectural Approach** to ensure modularity and scalability.

- **Observer Pattern**: Implemented to allow `RoomSensors` (Subject) to notify both the `RoomController` and `DataLogger` (Observers).
- **Transition-Only Logging**: To ensure data integrity and precise duration-based energy math, appliance states are recorded only when a change (ON/OFF) occurs.
- **RESTful API**: A Flask-based API serves as the coordination layer for real-time monitoring and simulation control.

## 📊 Energy Computation Model
Energy consumption ($kWh$) is derived using duration-based integration:
- **AC Rating**: 1.5 kW
- **Lighting Rating**: 0.06 kW
- **Formula**: $kWh = \text{Power (kW)} \times \text{Duration (Hours)}$

## 🚀 Getting Started

### 1. Create and Activate Virtual Environment
Create a virtual environment and activate it before installing dependencies:

```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 2. Installation
Ensure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the API Server

Run the main application from the source directory to initialize the database and start the listener:

```bash
python src/app.py

```

### 4. Execute the 24-Hour Simulation

In a second terminal window, run the simulation script to process a full cycle:

```bash
python src/run_24h_sim.py
```

### 5. Energy Analytics

After the simulation, fetch analytics via the API or generate tables and charts for the Chapter 3 write-up:

```bash
# API: full dashboard payload (energy by room, by appliance, cost, savings, db stats)
curl http://localhost:5000/api/analytics

# Generate tables and charts
python src/generate_report.py
```

Output is written to `output/tables.md` and `output/chart_*.png`.

## 📉 Verified Results (Chapter 3)

Based on the verified 24-hour simulation results:

* **Baseline Consumption**: 36.72 kWh
* **Smart System Consumption**: 3.13 kWh
* **Total Energy Saved**: 33.59 kWh
* **Efficiency Increase**: **91.5%**

## 📁 Project Structure

* `src/app.py`: Main Flask API and Observer registration.
* `src/api.py`: Data logging API (sensor, appliance, energy report).
* `src/database.py`: SQLite initialization and energy calculation logic.
* `src/control.py`: Room controller and appliance state evaluation.
* `src/sensors.py`: Environmental condition simulation.
* `src/run_24h_sim.py`: Automated 24-hour simulation testbench.
* `src/analytics.py`: Energy analytics (by room, by appliance, savings, cost).
* `src/generate_report.py`: Tables and charts for Chapter 3.
* `requirements.txt`: Python dependencies.
* `docs/`: Documentation including the detailed System Implementation report.

```

