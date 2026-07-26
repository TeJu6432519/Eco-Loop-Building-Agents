from pathlib import Path
import shutil
from eppy.modeleditor import IDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IDD = "/Applications/EnergyPlus-26-1-0/Energy+.idd"

BASELINE = PROJECT_ROOT / "idf" / "baseline.idf"
WORKING = PROJECT_ROOT / "idf" / "working.idf"


def prepare_idf():

  # Copy the original model
  shutil.copy(BASELINE, WORKING)

  # Tell eppy where the IDD is
  IDF.setiddname(IDD)

  # Load the copied model
  idf = IDF(str(WORKING))

  # ----------------------------------------------------
  # Shorten RunPeriod to a single day (May 1st) for speed
  # ----------------------------------------------------
  run_periods = idf.idfobjects["RUNPERIOD"]
  if run_periods:
    rp = run_periods[0]
    rp.Begin_Month = 5
    rp.Begin_Day_of_Month = 1
    rp.End_Month = 5
    rp.End_Day_of_Month = 1
    print("RunPeriod successfully shortened to a single day (May 1).")

  variables = [
      "Zone Mean Air Temperature",
      "Facility Total HVAC Electricity Demand Rate",
      "Facility Total Electricity Demand Rate",
      "Zone Air Relative Humidity",
  ]

  for variable in variables:
    idf.newidfobject(
        "OUTPUT:VARIABLE",
        Key_Value="*",
        Variable_Name=variable,
        Reporting_Frequency="Hourly",
    )

  # Save only working.idf
  idf.save()

  print("working.idf created successfully!")


if __name__ == "__main__":
  prepare_idf()