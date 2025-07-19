from typing import Tuple
import pandas as pd
from microgrid import INPUT_FILE


class SolarError(Exception):
    """A custom exception to raise errors in the solar module. Found in microgrid/solar.py"""

    pass


class Solar:

    def __init__(
        self,
        input_file: str = "",
        kw_peak: float = 2500,
        inverter_efficiency: float = 0.9,
    ):
        self.kw_peak = kw_peak
        self.inverter_efficiency = inverter_efficiency
        self.solar_generation = self.setup_solar_generation(input_file)

    def setup_solar_generation(self, input_file) -> list:
        """Load the solar generation"""

        if input_file != "":
            try:
                df = pd.read_csv(input_file)
            except (FileNotFoundError, pd.errors.ParserError) as e:
                raise SolarError(
                    f"Please input a valid path to the Solar Load file.{input_file} : {e} "
                )
        else:
            try:
                df = pd.read_csv(INPUT_FILE)
            except (FileNotFoundError, pd.errors.ParserError) as e:
                raise SolarError(
                    f"Please input a valid path to the Solar Load File. {input_file} : {e}"
                )

        if "solar_gen" not in df.columns:
            raise SolarError(
                f"Missing required col 'solar_gen' in input_file. Actual columns are: {df.columns}"
            )

        # could also check data type and a bunch of other things here.

        solar_generation = df["solar_gen"].tolist()
        return solar_generation

    def get_current_solar_generation(self, timestep: int) -> float:
        return self.solar_generation[timestep]
