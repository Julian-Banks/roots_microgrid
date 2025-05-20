from typing import Tuple
import pandas as pd


class LoadSimulator:

    def __init__(self):
        # Super keen to set up some aircon units that would get initialised here!!!
        self.load_values = self.setup_loads()

    def get_current_load(self, timestep: int) -> float:
        current_load: float = self.load_values[timestep]
        return current_load

    def setup_loads(self) -> list:
        # I want to add timesteps to the data.
        df = pd.read_csv("grid_simulator/data.csv")
        loads = df["load"].tolist()
        return loads
