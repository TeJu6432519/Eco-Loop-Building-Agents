class VariableManager:

    def __init__(self, api):
        self.api = api
        self.handles = {}

    def initialize(self, state):

        variables = [

            ("indoor_temp",
             "Zone Mean Air Temperature",
             "SPACE1-1"),

            ("outdoor_temp",
             "Site Outdoor Air Drybulb Temperature",
             "Environment"),

            ("humidity",
             "Zone Air Relative Humidity",
             "SPACE1-1"),

            ("hvac_power",
             "Facility Total HVAC Electricity Demand Rate",
             "Whole Building"),

            ("building_power",
             "Facility Total Electricity Demand Rate",
             "Whole Building"),
            
        ]

        for key, variable, key_value in variables:

            handle = self.api.exchange.get_variable_handle(
                state,
                variable,
                key_value
            )

            print(f"{key}: {handle}")

            self.handles[key] = handle

    def read(self, state):

        data = {}

        for key, handle in self.handles.items():

            if handle != -1:
                data[key] = self.api.exchange.get_variable_value(
                    state,
                    handle
                )
            else:
                data[key] = None

        return data