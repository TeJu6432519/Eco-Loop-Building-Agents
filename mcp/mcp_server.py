from pathlib import Path
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(name="EcoLoop Building Server")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@mcp.tool()
def get_building_target_thresholds() -> dict:
    """Returns the safety and thermal comfort boundaries for the building simulation."""
    return {
        "min_temp_c": 20.0,
        "max_temp_c": 24.0,
        "max_peak_power_kw": 50.0
    }

@mcp.tool()
def check_simulation_logs() -> str:
    """Parses the EnergyPlus error log file to find runtime errors or warnings."""
    log_path = PROJECT_ROOT / "results" / "eplusout.err"
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            return "".join(lines[-20:])
    except FileNotFoundError:
        return "Log file not found yet. Run simulation first."

if __name__ == "__main__":
    mcp.run()