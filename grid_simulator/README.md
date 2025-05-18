# Grid Energy Simulation Framework

![Architecture Diagram](diagram.png)

## Overview
Python framework for simulating grid-connected microgrid systems with battery storage, solar generation, and load demand modeling.


## Architecture

```mermaid
graph TD
    Solar[Solar Simulator] -->|Generation| Battery[Battery System]
    Grid[Grid Interface] -->|Import/Export| Microgrid[Microgrid Controller]
    Load[Load Simulator] -->|Demand| Battery
    Battery -->|Storage Levels| Microgrid
    Microgrid -->|Control Signals| Solar
    Microgrid -->|Control Signals| Grid

Core Components
Battery System (battery_simulator.py)
Tracks state of charge (SOC)
Manages charge/discharge rates
Handles efficiency calculations
Configuration:

BatterySimulator(
    battery_capacity=10.0,  # kWh capacity
    battery_C_rate=0.2,      # Charge/discharge rate
    efficiency=0.92,        # Round-trip efficiency
    soc_cutoff=0.3          # Minimum SOC threshold
)
Grid Interface (grid_feed_in_simulator.py)
Manages grid energy exchange
Implements time-of-use tariffs
Enforces power limits
Installation
git clone https://github.com/your-repo/grid-simulator
cd grid-simulator
pip install -r requirements.txt
Testing
Run all tests:

python -m pytest tests/ -v
Data Requirements
CSV format with columns:

timestamp (datetime)
solar_generation (kW)
load_demand (kW)
tariff_rate (currency/kWh)
License
MIT License




Change to the file for new feature
