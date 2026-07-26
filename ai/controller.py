class AIController:

    def decide(self, data):

        decision = {}

        # HVAC temperature target
        if data["indoor_temp"] > 25:
            decision["setpoint"] = 22
        else:
            decision["setpoint"] = 24

        # Occupancy
        if 9 <= data["hour"] <= 17:
            decision["occupancy"] = 8
        else:
            decision["occupancy"] = 2

        return decision