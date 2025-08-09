import pandas as pd
from io import StringIO
from typing import Dict, Tuple
import warnings
from microgrid.battery import Battery
from microgrid.solar import Solar
from microgrid.load import Load
from microgrid.grid import Grid


class Control:
    def __init__(self, start_step: int = 0, input_file: str = ""):

        self.current_step = start_step
        # time interval in hours
        self.time_interval = 1

        # setup battery
        self.battery = Battery()
        self.solar = Solar(input_file=input_file)
        self.load = Load(input_file=input_file)
        self.grid = Grid(input_file=input_file)

        self.update_state(self.current_step)

    def step(self):
        """Advance the simulation on step. (and update the state)"""
        self.current_step = self.current_step + 1
        self.update_state(self.current_step)

    def update_state(self, timestep: int) -> None:
        """Fetch the state for the current timestep."""
        self.state: Dict[str, float] = {
            'load': self.load.get_current_load(timestep=timestep),
            'solar_gen': self.solar.get_current_solar_generation(
                timestep=timestep
            ),
            'tou_tariff': self.grid.get_current_tariff(timestep=timestep),
            'battery_soc': self.battery.get_soc(),
        }

    def get_current_state(self) -> Dict[str, float]:
        """Returns the current state"""
        state = self.state
        return state

    # Functions to Energy logic flow
    def balance_energy(self, action: float):
        """Main logic function. Adjust system state based on control signals and ensure energy balance."""
        state: Dict[str, float] = self.get_current_state()
        purchase_request: float = (
            action  # Might to to transfrom action based on how scaling is implimented.
        )

        # Energy balance is solar minus Load.
        energy_balance: float = (
            state['solar_gen'] - state['load']
        )  # (Units: kW)

        # Calculate amount to purchase from Grid
        to_purchase: float = self.calculate_to_purchase(
            energy_balance, purchase_request
        )

        # Purchase and balance with Battery.
        energy_balance_with_grid = energy_balance + to_purchase

        # Charge/discharge the Battery.
        charged, discharged, excess, unmet_demand = self.balance_with_battery(
            energy_balance_with_grid
        )

        result: Dict[str, float] = {
            'to_purchase': to_purchase,
            'charged_this_step': charged,
            'discharged_this_step': discharged,
            'excess_this_step': excess,
            'unmet_demand_this_step': unmet_demand,
        }
        return result

    def artificial_positive_energy_balance(
        self, energy_balance: float, purchase_request: float
    ) -> float:
        """
        Use: Runs when the energy balance + the purchase request is positive. Determines how much of the purchase request can be fufilled.(Avoids trying to over charge the battery)
                Example:
                Energy balance -5kwh, purchase request is 8 kwh, charge_capacity is 2kWh
                to_purchase = min( -Energy_balance + max usable charge energy, purchase request)
                to_purchase = min (- (-5) + 2, 8) = 7 (only returns 7kwh instead of requested 8)
        Args:
            energy_balance (float): _description_
            purchase_request (float): _description_

        Returns:
            Float (to_purchase): Amount to be purchased, calculated from available capacity and the purchase request.
        """
        to_purchase: float = 0.0
        charge_capacity = self.battery.get_charge_capacity()
        to_purchase = min(-energy_balance + charge_capacity, purchase_request)

        return to_purchase

    def negative_energy_balance(
        self, energy_balance: float, purchase_request: float
    ) -> float:
        """
        Use: Runs when the Energy balance is negative. Decicdes where the energy should come from.
            Purchase request, then battery, then additional grid energy.
        Args:
            energy_balance (float): From Solar - load
            purchase_request (float): From agent

        Returns:
            Float: Amount to be purchased from the grid, inclusive of purchase request.
        """
        to_purchase: float = 0.0
        # Need to draw energy from grid or battery.
        # Get the ammount from the battery is available to be discharge.
        discharge_capacity = (
            self.battery.get_discharge_capacity() * self.battery.efficiency
        )
        # energy_balance + purchase_request  is less than 0
        if discharge_capacity > abs(energy_balance + purchase_request):
            to_discharge = abs(energy_balance + purchase_request)
        else:
            to_discharge = discharge_capacity

        # additional_purchase = abs(-100 + 60 + 20) = 20
        additional_purchase = abs(
            energy_balance + purchase_request + to_discharge
        )
        to_purchase = purchase_request + additional_purchase

        return to_purchase

    def positive_energy_balance(
        self, energy_balance: float, purchase_request: float
    ) -> float:
        """
        Use: Runs when the energy balance is positive, determines if any extra energy has been requested to charge the battery

        Args:
            energy_balance (float): solar-load  (positive in this case)
            purchase_request (float): requested purchase amount


        Returns:
            Float: Amount to be purchased from the grid.
        """
        to_purchase: float = 0.0
        # Check what the max usable energy is by checking how much energy can be stored in the battery.
        charge_capacity = self.battery.get_charge_capacity()
        # conver it to the max usable energy:
        charge_capacity = charge_capacity / self.battery.efficiency

        # if the max usable energy is more thatn the available energy balance. Then you can purchase more energy.
        # if you can purchase more, then you can only purchase up to the available energy or less.
        # if the max usable energy is less than the energy balance then you can't request to purchase more because there will already be excess.
        if charge_capacity - energy_balance > 0:
            to_purchase = min(
                purchase_request, charge_capacity - energy_balance
            )
        else:
            to_purchase = 0

        return to_purchase

    def calculate_to_purchase(
        self, energy_balance: float, purchase_request: float
    ) -> float:
        """Calculate the amount of energy that needs to be purchased from the grid from the energy balance and the purchase request.

        Returns:
            float (to_purchase): Amount to purchase from the grid
        """

        to_purchase: float = 0.0
        if energy_balance > 0:
            to_purchase = self.positive_energy_balance(
                energy_balance=energy_balance,
                purchase_request=purchase_request,
            )
        else:
            if energy_balance + purchase_request > 0:
                to_purchase = self.artificial_positive_energy_balance(
                    energy_balance=energy_balance,
                    purchase_request=purchase_request,
                )
            else:
                to_purchase = self.negative_energy_balance(
                    energy_balance=energy_balance,
                    purchase_request=purchase_request,
                )
        return to_purchase

    def balance_with_battery(self, energy_balance_with_grid: float) -> tuple:
        """Charges or Discharges the battery to meet need of energy_balance_with_grid."""
        charged: float = 0.0  #
        discharged: float = 0.0  #
        excess: float = 0.0  #
        unmet_demand: float = 0.0  #

        if energy_balance_with_grid > 0:
            charged, excess = self.battery.charge(energy_balance_with_grid)
        else:
            discharged, unmet_demand = self.battery.discharge(
                abs(energy_balance_with_grid)
            )

        return charged, discharged, excess, unmet_demand

    def get_total_steps(self) -> int:
        num_steps_solar: int = len(self.solar.solar_generation)
        num_steps_load: int = len(self.load.load_values)
        num_steps_tariffs: int = len(self.grid.tariffs)
        if (
            num_steps_solar
            == num_steps_load & num_steps_load
            == num_steps_tariffs
        ):
            return num_steps_solar
        else:
            warnings.warn("Warning, the length of all data is not equal!!")
            return num_steps_solar

    # internal function to set the current step for testing purposes.
    def _set_step(self, step) -> None:
        self.current_step = step

    def _set_state(
        self,
        load: float,
        solar_gen: float,
        tou_tariff: float,
        battery_soc: float,
    ) -> None:
        """internal func for setting state during testing"""
        self.state: Dict[str, float] = {
            'load': load,
            'solar_gen': solar_gen,
            'tou_tariff': tou_tariff,
            'battery_soc': battery_soc,
        }
