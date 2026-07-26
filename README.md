# Ecoloop Building Agent 

An intelligent, real-time HVAC control system driven by Large Language Models (LLMs) and EnergyPlus. This project uses the EnergyPlus Python API to simulate building energy performance while dynamically adjusting cooling setpoints using an LLM agent based on environmental sensors and occupancy schedules.

## Features
* **Real-time EnergyPlus Integration:** Uses the PyEnergyPlus API to read building sensors (temperatures, power demand, humidity) and apply active controls (`Zone Temperature Control` setpoints and `Schedule:Compact` occupancy values).
* **LLM-Driven Control Loop:** Queries an LLM controller at regular quarter-hour intervals to optimize building cooling setpoints.
* **Warmup-Aware Simulation Control:** Automatically ignores internal stabilization warmup cycles and enforces a precise 24-hour runtime limit.
* **Direct CSV Logging:** Incrementally writes simulation metrics and control actions to `results/ai_results.csv` in real-time.

---

## Project Structure
```text
Ecoloop_Building_agent/
├── ai/
│   └── llm_controller.py      # LLM decision-making agent logic
├── energyPlus/
│   ├── actuator_manager.py    # EnergyPlus actuator handles & control setters
│   ├── prepare_idf.py         # IDF model pre-processor and run-period shortener
│   ├── run_simulation.py      # Main simulation execution loop & real-time CSV logger
│   └── variable_manager.py    # Sensor variable reader configuration
├── idf/
│   ├── baseline.idf           # Original EnergyPlus building model
│   └── working.idf            # Shortened runtime model generated at startup
├── weather/
│   └── IND_Bangalore.432950_ISHRAE.epw # Weather file
├── results/
│   └── ai_results.csv         # Generated output simulation logs
└── README.md

## Tech Stack

- Python
- EnergyPlus
- Streamlit
- Ollama
- Pandas

## Run

```bash
python main.py