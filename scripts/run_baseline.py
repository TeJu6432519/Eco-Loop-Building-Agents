from pathlib import Path
import csv
import sys

from energyPlus.variable_manager import VariableManager

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

initialized = False
csv_file_initialized = False
csv_file_path = OUTPUT / "baseline_results.csv"
csv_file = None
csv_writer = None

# Track total elapsed real simulation minutes (excluding warmup)
total_simulation_minutes = 0


# ====================================================
# Control Loop (Baseline: Unoptimized, Energy-Heavy Static Profile)
# ====================================================
def baseline_control_loop(state):

    global initialized
    global csv_file_initialized
    global csv_file, csv_writer
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
        print("\nInitializing Baseline EnergyPlus API Data Handles (Warmup Complete)...")
        print(api.exchange.list_available_api_data_csv(state).decode())
        variable_manager.initialize(state)
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
        print("24-Hour Limit Reached. Stopping Baseline Simulation.")
        print("===================================\n")
        
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
    
    if 9 <= hour < 18:
        occupancy = 20
        baseline_setpoint = 21.0  
    elif 6 <= hour < 9 or 18 <= hour < 22:
        occupancy = 8
        baseline_setpoint = 22.0
    else:
        occupancy = 2
        baseline_setpoint = 23.5
        
    values["occupancy"] = occupancy
    values["cooling_setpoint"] = baseline_setpoint

    # ------------------------------------------------
    # Initialize CSV Writer dynamically based on available keys
    # ------------------------------------------------
    if not csv_file_initialized:
        row_data = {
            "elapsed_minutes": total_simulation_minutes,
            "hour": hour,
            "minute": minute,
            "occupancy": occupancy,
            "cooling_setpoint": baseline_setpoint
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
        "cooling_setpoint": baseline_setpoint
    }
    row_data.update(values)
    csv_writer.writerow(row_data)
    csv_file.flush()

    # ------------------------------------------------
    # Print Diagnostics
    # ------------------------------------------------
    print(f"--- Baseline Time: {hour:02d}:{minute:02d} | Elapsed: {total_simulation_minutes}m | Setpoint: {baseline_setpoint}°C ---")

    # Increment exact real simulation minutes per processed callback step
    total_simulation_minutes += 15


# ====================================================
# Run Baseline Simulation
# ====================================================
def run_baseline():

    global csv_file

    state = api.state_manager.new_state()

    api.runtime.callback_begin_zone_timestep_after_init_heat_balance(
        state,
        baseline_control_loop
    )

    args = [
        "-w",
        str(WEATHER),
        "-d",
        str(OUTPUT),
        str(IDF)
    ]

    print("Running Unoptimized Baseline EnergyPlus simulation with strict 24-hour limit...")

    api.runtime.run_energyplus(
        state,
        args
    )

    if csv_file and not csv_file.closed:
        csv_file.close()

    print("Baseline simulation finished!")
    print(f"Success! Baseline results saved to: {csv_file_path}")


if __name__ == "__main__":
    run_baseline()