from typing import Tuple
import pandas as pd
from sim import INPUT_FILE


class Solar:

    def __init__(
        self, kw_peak: float = 2500, inverter_efficiency: float = 0.9
    ):
        self.kw_peak = kw_peak
        self.inverter_efficiency = inverter_efficiency
        self.solar_generation = self.setup_solar_generation()

    def setup_solar_generation(self) -> list:
        """Load the solar generation"""
        df = pd.read_csv(INPUT_FILE)
        solar_generation = df["solar_gen"].tolist()
        return solar_generation

    def get_current_solar_generation(self, timestep: int) -> float:
        return self.solar_generation[timestep]
