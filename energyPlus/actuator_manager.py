class ActuatorManager:

    def __init__(self, api):
        self.api = api
        self.people_handle = -1
        self.cooling_handle = -1

    def initialize(self, state):
        
        # 1. Get Cooling Setpoint Actuator Handle for SPACE1-1
        self.cooling_handle = self.api.exchange.get_actuator_handle(
            state,
            "Zone Temperature Control",
            "Cooling Setpoint",
            "SPACE1-1"
        )
        print(f"COOLING HANDLE: {self.cooling_handle}")

        # 2. Get People Occupancy Schedule Handle (matching OCCUPY-1 from your manifest dump)
        self.people_handle = self.api.exchange.get_actuator_handle(
            state,
            "Schedule:Compact",
            "Schedule Value",
            "OCCUPY-1"
        )
        print(f"ACTUATOR HANDLE: {self.people_handle}")

        # Safety warnings if handles fail
        if self.cooling_handle == -1:
            print("WARNING: Cooling setpoint actuator handle not found!")
        if self.people_handle == -1:
            print("WARNING: People schedule actuator handle not found!")

    def set_cooling_setpoint(self, state, setpoint):
        if self.cooling_handle != -1:
            self.api.exchange.set_actuator_value(
                state,
                self.cooling_handle,
                float(setpoint)
            )

    def set_people(self, state, occupancy):
        if self.people_handle != -1:
            self.api.exchange.set_actuator_value(
                state,
                self.people_handle,
                float(occupancy)
            )