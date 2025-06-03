from typing import Tuple
import pandas as pd


class GeneratorSimulator:
    def __init__(self, capacity=500, cost_per_kwh=5):
        # initialise the generators and characteristics.
        self.generators = self.setup_generators(capacity=500, cost_per_kwh=5)

    def setup_generators(self, capacity: float, cost_per_kwh: float) -> None:
        self.capacity = capacity
        self.cost_per_kwh = cost_per_kwh

    def run_generators(
        self, requested_power: float, time_interval: float
    ) -> Tuple:
        """
        Generates the requested amount of energy and calculates the cost.

        Args:
            requested_power (float): The amount of power needed from the generators.
            time_interval (float, optional): Time interval of simulation.

        Returns:
            Tuple: Generator power, Cost for interval
        """
        # check if requested_power less than capacity
        if requested_power < self.capacity:
            return (
                requested_power,
                time_interval * requested_power * self.cost_per_kwh,
            )
        else:
            return (
                self.capacity,
                time_interval * self.cost_per_kwh * self.capacity,
            )

        # should impliment a cost curve since it costs more to run them not at full power.
