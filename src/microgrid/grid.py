from datetime import time
from os import error
from typing import Tuple
import pandas as pd
from microgrid import INPUT_FILE


class GridError(Exception):
    """Custom exception for raising errors in the Grid file. Found in microgrid/grid.py"""

    pass


class Grid:
    def __init__(
        self,
        feed_in_voltage: float = 240,
        feed_in_power_rating: float = 1000,
        take_off_voltage: float = 240,
        take_off_power_rating: float = 1000,
        transformer_efficiencies: float = 1,
        input_file: str = "",
    ):

        self.feed_in_voltage = feed_in_voltage
        self.feed_in_power_rating = feed_in_power_rating
        self.take_off_voltage = take_off_voltage
        self.take_off_power_rating = take_off_power_rating
        self.transformer_efficiencies = transformer_efficiencies

        self.tariffs: list = self.setup_tariff_structure(input_file=input_file)

    def purchase_energy(
        self, purchase_amount: float, timestep: int
    ) -> Tuple[float, float]:
        """
        Use: Purchase energy from the grid.

        Args:
            purchase_amount (float): Amount of energy to be purchased
            timestep (int): Timestep that the energy was purchesed.
        Returns:
            Tuple[float,float](purchased_energy, cost): Amount of energy purchased, the cost of energy.
        """
        # Can impliment loadshedding logic here.
        purchased_energy: float = purchase_amount

        cost: float = self.calculate_cost(purchased_energy, timestep)

        return purchased_energy, cost

    def calculate_cost(self, purchased_energy: float, timestep: int) -> float:
        cost: float = purchased_energy * self.get_current_tariff(timestep)
        return cost

    def setup_tariff_structure(self, input_file) -> list:
        # Might find a way of either setting rules and generating these or just reading from a list with timestamps and values.

        if input_file != "":
            try:
                data = pd.read_csv(input_file)
            except (FileNotFoundError, pd.error.ParserError) as e:
                raise GridError(
                    f"Could not reach grid input file: {input_file}: {e}"
                )
        else:
            try:
                data = pd.read_csv(INPUT_FILE)
            except (FileNotFoundError, pd.error.ParserError) as e:
                raise GridError(
                    f"Please provide a valid input path for grid path."
                )

        tariffs = data["tou_tariff"].tolist()

        return tariffs

    def get_current_tariff(self, timestep: int) -> float:
        return self.tariffs[timestep]

    ##### To do #######
    def get_tariff_forecast(self, current_step: int, forecast_length: int):
        # How is data going to be stored?
        # is it going to have timestamps? I kinda like this as a way of making sure alles is doing the right thing across modules.
        tariff_forecast = self.tariffs[
            current_step : current_step + forecast_length
        ]
        return tariff_forecast

    def loadshedding_forecast(self):
        pass

    def transformer(self):
        pass

    def get_data(self):
        # In simulation this won't include data from what was actually drawn from the Grid. Data of what was actually used from the grid will be used to validate the simulations.
        pass
