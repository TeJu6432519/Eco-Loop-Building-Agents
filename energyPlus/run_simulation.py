from pathlib import Path
import csv
import sys

from energyPlus.variable_manager import VariableManager
from energyPlus.actuator_manager import ActuatorManager
from ai.llm_controller import LLMController

# ----------------------------------------------------
# EnergyPlus installation
# ----------------------------------------------------
ENERGYPLUS_ROOT = "/Applications/EnergyPlus-26-1-0"
sys.path.insert(0, ENERGYPLUS_ROOT)

from pyenergyplus.api import EnergyPlusAPI

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

IDF = PROJECT_ROOT / "idf" / "working.idf"
WEATHER = PROJECT_ROOT / "weather" / "IND_Bangalore.432950_ISHRAE.epw"
OUTPUT = PROJECT_ROOT / "results"

# Ensure results directory exists
OUTPUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------
# Global objects & tracking variables
# ----------------------------------------------------
api = EnergyPlusAPI()

variable_manager = VariableManager(api)
actuators = ActuatorManager(api)
controller = LLMController()

initialized = False
csv_file_initialized = False
csv_file_path = OUTPUT / "ai_results.csv"
csv_file = None
csv_writer = None

# Latest cooling setpoint decided by the LLM
last_setpoint = 24.0

# Track the last exact simulated minute block the LLM was queried at
last_llm_minute = -1

# Track total elapsed real simulation minutes (excluding warmup)
total_simulation_minutes = 0


# ====================================================
# Control Loop
# ====================================================
def control_loop(state):

    global initialized
    global csv_file_initialized
    global csv_file, csv_writer
    global last_setpoint
    global last_llm_minute
    global total_simulation_minutes

    if not api.exchange.api_data_fully_ready(state):
        return

    # ------------------------------------------------
    # 1. Ignore Warmup Completely
    # ------------------------------------------------
    if api.exchange.warmup_flag(state) == 1:
        return

    # Initialize handles on the very first real simulation tick
    if not initialized:
        print("\nInitializing EnergyPlus API Data Handles (Warmup Complete)...")
        print(api.exchange.list_available_api_data_csv(state).decode())

        variable_manager.initialize(state)
        actuators.initialize(state)
        initialized = True

    hour = int(api.exchange.hour(state))
    minute = int(api.exchange.minutes(state))

    # EnergyPlus hours sometimes report as 24 at midnight wrap-around; normalize to 0-23
    if hour == 24:
        hour = 0

    # ------------------------------------------------
    # 2. Check if exactly 24 hours (1440 minutes) have elapsed
    # ------------------------------------------------
    if total_simulation_minutes >= 1440:
        print("\n===================================")
        print("24-Hour Limit Reached. Stopping Simulation.")
        print("===================================\n")
        
        # Safely close CSV file if open
        if csv_file:
            csv_file.close()
            
        api.runtime.stop_simulation(state)
        return

    # ------------------------------------------------
    # Read sensors & time
    # ------------------------------------------------
    values = variable_manager.read(state)
    values["hour"] = hour
    values["minute"] = minute

    # ------------------------------------------------
    # Occupancy Schedule (24-Hour Active Schedule)
    # ------------------------------------------------
    if 9 <= hour < 18:
        occupancy = 20  # Peak working hours
    elif 6 <= hour < 9 or 18 <= hour < 22:
        occupancy = 8   # Early morning / Evening cleaning or minimal staff
    else:
        occupancy = 2   # Night hours (00:00 to 06:00)
        
    values["occupancy"] = occupancy

    # ------------------------------------------------
    # Query LLM strictly on exact quarter hours (:00, :15, :30, :45)
    # ------------------------------------------------
    is_quarter_hour = (minute in [0, 15, 30, 45])
    current_time_signature = hour * 60 + minute

    if is_quarter_hour and current_time_signature != last_llm_minute:

        print("\n===================================")
        print(f"Calling LLM at {hour:02d}:{minute:02d} (Elapsed: {total_simulation_minutes} mins)")
        print("===================================")

        try:
            decision = controller.decide(
                values,
                last_setpoint
            )

            last_setpoint = decision["setpoint"]
            last_llm_minute = current_time_signature

        except Exception as e:
            print("LLM ERROR:", e)
            print("Keeping previous setpoint:", last_setpoint)

    # ------------------------------------------------
    # Apply controls
    # ------------------------------------------------
    actuators.set_people(
        state,
        occupancy
    )

    actuators.set_cooling_setpoint(
        state,
        last_setpoint
    )

    # ------------------------------------------------
    # Initialize CSV Writer dynamically based on available keys
    # ------------------------------------------------
    if not csv_file_initialized:
        row_data = {
            "elapsed_minutes": total_simulation_minutes,
            "hour": hour,
            "minute": minute,
            "occupancy": occupancy,
            "cooling_setpoint": last_setpoint
        }
        row_data.update(values)
        
        csv_file = open(csv_file_path, "w", newline="")
        csv_writer = csv.DictWriter(csv_file, fieldnames=row_data.keys())
        csv_writer.writeheader()
        csv_file_initialized = True

    # ------------------------------------------------
    # Write current timestep row directly to disk
    # ------------------------------------------------
    row_data = {
        "elapsed_minutes": total_simulation_minutes,
        "hour": hour,
        "minute": minute,
        "occupancy": occupancy,
        "cooling_setpoint": last_setpoint
    }
    row_data.update(values)
    csv_writer.writerow(row_data)
    csv_file.flush()  # Force write to disk immediately

    # ------------------------------------------------
    # Print Timestep Diagnostics
    # ------------------------------------------------
    print(f"--- Time: {hour:02d}:{minute:02d} | Elapsed: {total_simulation_minutes}m ---")
    print("Sensors:")
    for key, value in values.items():
        print(f"  {key}: {value}")

    print("Applied Controls:")
    print(f"  Occupancy        : {occupancy}")
    print(f"  Cooling Setpoint : {last_setpoint}\n")

    # Increment exact real simulation minutes per processed callback step
    total_simulation_minutes += 15


# ====================================================
# Run Simulation
# ====================================================
def run_simulation():

    global csv_file

    state = api.state_manager.new_state()

    api.runtime.callback_begin_zone_timestep_after_init_heat_balance(
        state,
        control_loop
    )

    args = [
        "-w",
        str(WEATHER),
        "-d",
        str(OUTPUT),
        str(IDF)
    ]

    print("Running EnergyPlus simulation with strict 24-hour limit...")

    api.runtime.run_energyplus(
        state,
        args
    )

    # Ensure file handle is closed cleanly if simulation terminates
    if csv_file and not csv_file.closed:
        csv_file.close()

    print("Simulation finished!")
    print(f"Success! Results saved directly to: {csv_file_path}")


if __name__ == "__main__":
    run_simulation()