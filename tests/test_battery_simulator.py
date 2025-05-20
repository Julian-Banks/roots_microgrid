from grid_simulator.battery_simulator import BatterySimulator
from typing import Dict
import unittest


class TestGridSimulator(unittest.TestCase):

    def setUp(self):

        self.battery_simulator = BatterySimulator(
            battery_soc=0.5,
            battery_capacity=1000,
            battery_C_rate=0.2,
            battery_efficiency=0.9,
            battery_soc_cuttoff=0.4,
            time_interval=1,
        )

    def tearDown(self):
        pass

    def test_charge(self):
        # Make sure the battery is set up for this unit test.
        self.battery_simulator.battery_C_rate = 0.2
        self.battery_simulator.battery_efficiency = 0.9
        self.battery_simulator.battery_capacity = 1000

        # Case 1:
        # Charge an amount that has no excess and does not exceed max charge rate.

        # output should be:
        # start_soc = 0.5
        # battery_efficiency = 0.9
        # input = 150,  output = 150*0.9 = 135 charged.
        # soc = 500 + 135 / 1000 = 0.635

        # set soc, charge_energy,
        start_soc = self.battery_simulator._set_soc(0.5)
        charge_energy: float = 150  # kW * time interval
        # Charge battery.
        charged, excess = self.battery_simulator.charge(charge_energy)
        # Get soc
        soc = self.battery_simulator.get_soc()

        self.assertEqual(charged, 135)
        self.assertEqual(excess, 0)
        self.assertEqual(soc, 0.635)

        # Case 4:
        # Charge an amount that has exceeds charge capacity and exceeds max charge rate.

        # output should be:
        # start_soc = 0.9
        # input = 300
        # charge_capacity = 0.1, charged = 100, used = 1/0.9, excess = 300 - used. soc = 1.

        start_soc = self.battery_simulator._set_soc(0.9)
        charge_energy: float = 300  # Unit: kW * time interval
        # charge battery:
        charged, excess = self.battery_simulator.charge(charge_energy)

        # Get soc
        soc = self.battery_simulator.get_soc()

        self.assertEqual(charged, 100)
        self.assertEqual(
            excess,
            charge_energy
            - (charged / self.battery_simulator.battery_efficiency),
        )
        self.assertEqual(soc, 1)

    def test_charge_fully(self):
        # Case 2:
        # Charge and amount that exceeds charge capacity and does not exceed max charge rate.

        # Output should be:
        # start_soc = 0.9
        # battery_efficiency = 0.9
        # input = 150

        start_soc = self.battery_simulator._set_soc(0.9)
        charge_energy: float = 150  # kW * time interval
        # charge battery:
        charged, excess = self.battery_simulator.charge(charge_energy)
        # Get soc
        soc = self.battery_simulator.get_soc()

        self.assertEqual(charged, 100)
        self.assertEqual(
            excess,
            charge_energy
            - (charged / self.battery_simulator.battery_efficiency),
        )
        self.assertEqual(soc, 1)

    def test_charge_rate_limit(self):
        # Case 3:
        # Charge an amount that has doesn't exceed charge_capacity but does exceeds max charge rate.

        # Output should be:
        # start_soc = 0.5
        # input = 300
        # charge_capacity = 500, max_charge_rate = 200 ... therefore charge_capacity returns 200.. (this is a different unit test)
        # charged = 200, used = 200/0.9 = 222.22, excess = 300-222.22 , soc = 0.7
        start_soc = self.battery_simulator._set_soc(0.5)
        charge_energy: float = 300  # kW * time interval
        # charge battery:
        charged, excess = self.battery_simulator.charge(charge_energy)
        # Get soc
        soc = self.battery_simulator.get_soc()

        self.assertEqual(charged, 200)
        self.assertEqual(
            excess,
            charge_energy
            - (charged / self.battery_simulator.battery_efficiency),
        )
        self.assertEqual(soc, 0.7)

    def test_discharge(self):
        pass

    def test_discharge_rate_limit(self):
        pass

    def test_discharge_fully(self):
        pass

    def test_get_charge_capacity(self):
        pass

    def test_get_discharge_capacity(self):
        pass

    def test_get_battery_energy(self):
        pass

    def get_soc(self):
        pass


if __name__ == "__main__":
    unittest.main()
