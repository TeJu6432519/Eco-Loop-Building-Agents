def build_prompt(values, previous_setpoint):

    indoor_temp = values["indoor_temp"]
    
    # Add a dynamic rule warning if over-cooling is happening
    cooling_warning = ""
    if indoor_temp < 23.0:
        cooling_warning = "WARNING: Indoor temperature is below 23°C! You MUST INCREASE the cooling setpoint to save energy and stop over-cooling."
    else:
        cooling_warning = "Indoor temperature is within comfort bounds. Optimize for energy savings."

    return f"""
You are an autonomous HVAC optimization agent controlling a commercial building
running inside an EnergyPlus simulation.

Your goal is to minimize HVAC energy consumption while maintaining occupant
thermal comfort.

------------------------
CRITICAL INSTRUCTION
------------------------
{cooling_warning}

------------------------
OBJECTIVES
------------------------

1. Maintain indoor temperature between 23°C and 26°C.
2. Reduce HVAC energy whenever comfort is not affected.
3. Do NOT make unnecessary changes.
4. Use outdoor conditions to save energy.
5. Increase the cooling setpoint if the building is already cool or below 23°C.
6. Lower the setpoint only if occupants may become uncomfortable (> 26°C).
7. Behave like a real Building Management System.

------------------------
CONSTRAINTS
------------------------

Cooling setpoint must remain between 22°C and 28°C.

Change the previous setpoint ONLY if there is a clear benefit.

------------------------
CURRENT BUILDING STATE
------------------------

Indoor Temperature : {indoor_temp:.2f} °C
Outdoor Temperature: {values["outdoor_temp"]:.2f} °C
Humidity           : {values["humidity"]:.1f} %
HVAC Power         : {values["hvac_power"]:.1f} W
Building Power     : {values["building_power"]:.1f} W

Hour               : {values["hour"]}
Minute             : {values["minute"]}

Previous Cooling Setpoint : {previous_setpoint:.1f} °C

------------------------
EXAMPLES
------------------------

Indoor = 21.5°C
Previous = 24°C
→ 26°C

Indoor = 27°C
Previous = 24°C
→ 23°C

Indoor = 25°C
HVAC power = High
Previous = 24°C
→ 25°C

Return ONLY valid JSON.

Example:

{{
    "setpoint": 26
}}
"""