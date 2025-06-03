import pandas as pd
from io import StringIO
from typing import Dict, Tuple


class BatterySimulator:

    def __init__(
        self,
        battery_soc: float = 0.5,
        battery_capacity: float = 1,
        battery_C_rate: float = 0.2,
        battery_efficiency: float = 0.9,
        battery_soc_cuttoff: float = 0.4,
        time_interval: float = 1,
    ):

        ### State of Charge stuff (SOC)
        self.battery_soc: float = battery_soc
        self.battery_soc_cuttoff: float = (
            battery_soc_cuttoff  # Lower limit to the Battery_soc
        )
        ### Charge and discharge stuff. Maybe I can use C_rate for both? Must look up more info.
        # Note: C_rate is in amps usually, I am currently using it in energy
        # C rate for dis/charging the battery. 1C is it can charge fully in 1 hour. 0.2 means it can charge fully in 5 hours (charges at a rate of 0.2C)
        self.battery_C_rate: float = battery_C_rate
        # Charge and discharge efficiency of the battery
        self.battery_efficiency: float = battery_efficiency
        # time interval for charges and discharges, should it be here? (Unit: hours)
        self.time_interval: float = time_interval
        ### Metrics in kWh for understanding and conversions.
        self.battery_capacity: float = battery_capacity

    def charge(self, charge_energy: float) -> Tuple[float, float]:
        """
        Uses: Charges the battery with charge_energy.
        Impliments: Max Charge rate, Battery Efficiency, Max capacity.

        Args:
            charge_energy (float): amount of energy that is available to charge the battery.

        Returns:
            Tuple[float, float]: (charged, excess) The amount of energy that was stored in the battery and any energy that is excess
        """

        excess: float = 0
        charged: float = 0

        # inside battery side:
        max_charge_energy: float = self.get_charge_capacity()

        # out of battery:
        max_charge_energy = max_charge_energy / self.battery_efficiency

        if charge_energy < max_charge_energy:
            charged = charge_energy * self.battery_efficiency
            self.update_soc(charged)
        else:
            charged = (
                max_charge_energy * self.battery_efficiency
            )  # Back to inside battery...
            self.update_soc(charged)
            excess = charge_energy - (max_charge_energy)

        return charged, excess

    def discharge(self, discharge_energy: float) -> Tuple[float, float]:
        """
        Use: Discharges energy from the battery to meet the needs of discharge_energy.
        Impliments: Max discharge rate (C-rate), Battery Efficiency, Min SOC.

        Args:
            discharge_energy (float): amount of energy to discharge.

        Returns:
            Tuple[float, float]: discharged, unmet_demand
        """
        discharged: float = 0
        unmet_demand: float = 0

        # inside the battery side:
        max_discharge_energy: float = self.get_discharge_capacity()
        # 10

        # out of battery:
        # 9=10*0.9
        max_discharge_energy = max_discharge_energy * self.battery_efficiency

        if discharge_energy < max_discharge_energy:
            discharged = discharge_energy
            self.update_soc(-discharged / self.battery_efficiency)
        else:
            discharged = max_discharge_energy
            self.update_soc(-discharged / self.battery_efficiency)
            unmet_demand = discharge_energy - (max_discharge_energy)
        return discharged, unmet_demand

    def update_soc(self, energy: float) -> float:
        self.battery_soc += energy / self.battery_capacity
        # I was getting issues with floating point precision. 6 decimal points should be enough??? Maybe I should use soc out of 100 rather than 0->1.
        # I had commented out the below line (self.battery_soc=round....) and I can't remember why I did.... But I was getting the floating point errors again so I'm un-commenting it.
        self.battery_soc = round(self.battery_soc, 12)
        return self.battery_soc

    # Getter Functions
    def get_charge_capacity(self) -> float:
        """Get the amount of energy that can go into the battery. Note that the amount of energy used would be energy_in/battery_efficiency"""
        # get the available capcity
        available_capacity: float = (
            self.battery_capacity - self.get_battery_energy()
        )

        # Calculate the max energy that can be used by the battery based on its max rate of charge.
        max_charge_rate: float = (
            self.battery_C_rate * self.battery_capacity * self.time_interval
        )

        # Return the smaller of the two.
        charge_capacity: float = min(max_charge_rate, available_capacity)

        return charge_capacity

    def get_discharge_capacity(self) -> float:
        """Get the amount of energy the battery can discharge. Not that the amount usable energy would by discharge_capacity*battery_efficiency"""
        # I reluctantly used round(soc-soc_cutoff,6) because it was giving floating point precision issues...
        avail_battery_energy: float = self.battery_capacity * round(
            self.get_soc() - self.battery_soc_cuttoff, 6
        )

        max_discharge_rate: float = min(
            self.battery_C_rate * self.battery_capacity * self.time_interval,
            avail_battery_energy,
        )

        discharge_capacity: float = min(
            max_discharge_rate, avail_battery_energy
        )

        return discharge_capacity

    def get_battery_energy(self) -> float:
        return self.battery_capacity * self.get_soc()

    def get_soc(self) -> float:
        return self.battery_soc

    # Internal funcs for Testing
    def _set_battery_soc_cutoff(self, soc_cutoff: float) -> float:
        """
        Internal func for setting SOC cutoff during testing.
        Args:
            soc_cutoff (float): between 0 -> 1

        Returns:
            float: new _soc_cutoff
        """
        self.battery_soc_cuttoff = soc_cutoff
        return self.battery_soc_cuttoff

    def _set_soc(self, soc) -> float:
        """
        Internal func for setting SOC during testing.
        """
        self.battery_soc = soc
        return self.battery_soc

    def _set_battery_capacity(self, battery_capacity) -> float:
        """internal func for setting battery capcity during testing."""
        self.battery_capacity = battery_capacity
        return self.battery_capacity
