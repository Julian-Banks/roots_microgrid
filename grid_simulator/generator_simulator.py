from typing import Tuple
import pandas as pd


class GeneratorSimulator:
    def __init__(
        self,
        capacity: float = 500,
        cost_diesel: float = 20,
        litre_diesel_per_kWh: float = 0.3,
    ):
        # initialise the generators and characteristics.
        # This doesn't feel very smart. The idea was along the lines of wanting to have different generators with different sizes within this module but I'm not going to dive into that now.
        self.setup_generators(
            capacity=500, cost_diesel=20, litre_diesel_per_kWh=0.3
        )

    def setup_generators(
        self, capacity: float, cost_diesel: float, litre_diesel_per_kWh: float
    ) -> None:
        self.capacity = capacity
        self.cost_diesel = cost_diesel
        self.litre_diesel_per_kWh = litre_diesel_per_kWh

    def run_generators(
        self, requested_power: float, time_interval: float
    ) -> Tuple:
        """
        Generates the requested amount of energy and calculates the cost.

        Args:
            requested_power (float): The amount of power needed from the generators.
            time_interval (float, optional): Time interval of simulation.

        Returns:
            Tuple: Generator power, Cost of energy for interval
        """
        # check if requested_power less than capacity
        if requested_power < self.capacity:
            return (
                requested_power,
                self.calculate_generator_cost(requested_power, time_interval),
            )
        else:
            return (
                self.capacity,
                self.calculate_generator_cost(self.capacity, time_interval),
            )

    def calculate_generator_cost(
        self, generated_power: float, time_interval: float
    ) -> float:
        """
        Calculates the cost associated with running the generators for this time period.
        Args:
            generated_power (float): the amount of energy generated in kWh

        Returns:
            float: cost of energy
        """
        # should impliment a cost curve since it costs more to run them not at full power.
        cost = generated_power * self.litre_diesel_per_kWh * self.cost_diesel

        return cost
