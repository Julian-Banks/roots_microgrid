from typing import Tuple
import pandas as pd
from microgrid import INPUT_FILE


class LoadError(Exception):
    """Custom exception for (electricity) load related issues.  Found in microgrid/load.py"""

    pass


class Load:

    def __init__(self, input_file: str = ""):
        # Super keen to set up some aircon units that would get initialised here!!!
        self.load_values = self.setup_loads(input_file)

    def get_current_load(self, timestep: int) -> float:
        current_load: float = self.load_values[timestep]
        return current_load

    def setup_loads(self, input_file: str) -> list:
        # I want to add timesteps to the data.
        if input_file != "":
            try:
                df = pd.read_csv(input_file)
            except (FileNotFoundError, pd.error.ParserError) as e:
                raise LoadError(
                    f"Failed to read input file {input_file} : {e}"
                )
        else:
            try:
                print("Using Test Load input file.")
                df = pd.read_csv(INPUT_FILE)
            except:
                raise LoadError(
                    "No input file provided for the electricity load data."
                )

        loads = df["load"].tolist()
        return loads

    def get_load_forecast(self, current_step: int, forecast_length: int = 24):
        # How is data going to be stored?
        # is it going to have timestamps? I kinda like this as a way of making sure alles is doing the right thing across modules.
        load_forecast = self.load_values[
            current_step : current_step + forecast_length
        ]
        return load_forecast
