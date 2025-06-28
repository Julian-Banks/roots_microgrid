from microgrid.control import Control
from typing import Dict
import unittest


class TestControl(unittest.TestCase):

    def setUp(self):
        self.control = Control()

    def tearDown(self):
        del self.control

    def test_get_current_state(self):

        # Expected first and Last state.
        first_state: Dict[str, float] = {
            'load': 96.855,
            'solar_gen': 0.0,
            'tou_tariff': 1.2103,
            'battery_soc': 0.5,
        }
        last_state: Dict[str, float] = {
            'load': 86.085,
            'solar_gen': 0.0,
            'tou_tariff': 1.2103,
            'battery_soc': 0.5,
        }

        # Assert that the first state is correct (with battery_soc set to 0.5)
        state = self.control.get_current_state()
        self.assertDictEqual(state, first_state)

        # Set the microgrid_simulator to the last step of the simulation.
        last_time_step = 8759
        self.control.update_state(last_time_step)
        # Assert that the last state is correct (with battery_soc set to 0.5)
        state = self.control.get_current_state()
        self.assertDictEqual(state, last_state)

    # if the max usable energy is more thatn the available energy balance. Then you can purchase more energy.
    # if you can purchase more, then you can only purchase up to the available energy or less.
    # if the max usable energy is less than the energy balance then you can't request to purchase more because there will already be excess.

    # Check how the system handles when there is available charge for purchase requests.
    # Case 1: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 4kWh
    # Case 2: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 1kWh
    # Case 3: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 0kWh
    # Case 4: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 2kWh

    # Check how the system handles when there is excess.
    # These tests are kinda duplicates of eachother, I just want to make sure there is no monkey business. But they should all return the same result.
    # Case 5: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 6kWh
    # Case 6: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 4kWh
    # Case 7: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 0kWh

    # Check how the system handles negative energy balance:
    # case 8: energy balance is -8kWh, available_discharge_capacity = 10kWh, purchase request = 0
    # case 9: energy balance is -8kWh, available_discharge_capacity = 10kWh, pruchase request = 8kwh
    # case 10: energy balance is -8kWh, available_discharge_capacity = 10kWh, purchase_request = 10 kWh

    # Check how the system handles empty battery:
    # case 11: energy balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request = 0
    # case 12: energy_balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request = 2kWh
    # case 13: energy_balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request =

    def test_case1(self):
        # Case 1: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 4kWh Output:
        # max_usable_charge_energy = 10/0.9 (10% lost to efficiencies), to_purchase = 10.1-8 = 2.1

        # to_purchase = max_usable_charge_energy - energy_balance , charged = 10, excess = 0, unmet_load = 0

        # Set the battery capcity and get available charge.
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.90)
        available_charge_capacity = self.control.battery.get_charge_capacity()
        # Check that you have 10kw Available for charge.
        self.assertEqual(available_charge_capacity, 10)

        # Set the state to known values: Energy_balance = solar-load = 8
        self.control._set_state(
            load=2, solar_gen=10, tou_tariff=1, battery_soc=0.90
        )

        # Call the balance_energy_func
        result = self.control.balance_energy(action=4)

        # this is the total amount needed to get to a full battery, 8 is the amount that will come from the energy balance.
        expected_to_purchase = 10 / self.control.battery.efficiency - 8

        expected_result = {
            'to_purchase': expected_to_purchase,
            'charged_this_step': 10,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertDictEqual(result, expected_result)

    def test_case2(self):
        # Case 2: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 1kWh Output: to_purchase = 1, charged = (8+1)*0.9, excess = 0, unmet_load = 0

        # Set the battery capcity and get available charge.
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.90)
        available_charge_capacity = self.control.battery.get_charge_capacity()
        # Check that you have 10kw Available for charge.
        self.assertEqual(available_charge_capacity, 10)

        # Set the state to known values: Energy_balance = solar-load = 8
        self.control._set_state(
            load=2, solar_gen=10, tou_tariff=1, battery_soc=0.90
        )

        # Call the update_staete func
        result = self.control.balance_energy(action=1)

        # Expected to charge energy_balance + to purchase with efficiency applied.
        purchase_request = 1
        energy_balance = 8
        expected_charge = (
            energy_balance + purchase_request
        ) * self.control.battery.efficiency

        expected_result = {
            'to_purchase': 1,
            'charged_this_step': expected_charge,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }
        self.assertDictEqual(result, expected_result)

    def test_case3(self):
        # Case 3: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 0kWh Output: to_purchase = 0, charged = 8*0.9, excess = 0
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.90)
        available_charge_capacity = self.control.battery.get_charge_capacity()
        # Check that we have 10kw Available for charge.
        self.assertEqual(available_charge_capacity, 10)

        self.control._set_state(
            load=2, solar_gen=10, tou_tariff=1, battery_soc=0.90
        )

        result = self.control.balance_energy(action=0)

        energy_balance = 8
        purchase_request = 0
        expected_charge = (
            energy_balance + purchase_request
        ) * self.control.battery.efficiency  # Note that it is not always expected that the purchase request is actually purchased. We know it should be because the max available charge is less than the energy balance.

        expected_result = {
            'to_purchase': 0,
            'charged_this_step': expected_charge,  # 8*0.9
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertDictEqual(result, expected_result)

    def test_case4(
        self,
    ):  # testing Positive Energy balance path. With Purchase less than max available charge capacity.
        # Case 3: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 2kWh Output: to_purchase = 2, charged = (8+2)*0.9, excess = 0
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.90)
        available_charge_capacity = self.control.battery.get_charge_capacity()
        # Check that we have 10kw Available for charge.
        self.assertEqual(available_charge_capacity, 10)

        self.control._set_state(
            load=2, solar_gen=10, tou_tariff=1, battery_soc=0.90
        )

        result = self.control.balance_energy(action=2)

        energy_balance = 8
        purchase_request = 2
        expected_charge = (
            energy_balance + purchase_request
        ) * self.control.battery.efficiency  # Note that it is not always expected that the purchase request is actually purchased. We know it should be because the max available charge is less than the energy balance.

        expected_result = {
            'to_purchase': 2,
            'charged_this_step': expected_charge,  # (8+2)*0.9 (still less than the max available charge capacity.)
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertDictEqual(result, expected_result)

    def test_case5(self):
        # Case 5: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 6kWh

        # Set the battery capcity and check the available capacity is 8kWh
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.92)
        self.assertEqual(self.control.battery.get_charge_capacity(), 8)

        # set the state to have an energy balance of 12kWh
        self.control._set_state(
            load=2, solar_gen=14, tou_tariff=1, battery_soc=0.92
        )

        # request to purchase 6kWh
        result = self.control.balance_energy(action=6)

        # Since the energy balance is much higer than the available charge capacity the expected charge is the available capacity with efficiency applied.
        expected_charge = 8.0

        expected_result = {
            'to_purchase': 0,
            'charged_this_step': expected_charge,  # 8/0.9 = 8.8888
            'discharged_this_step': 0,
            'excess_this_step': 12
            - expected_charge / self.control.battery.efficiency,
            'unmet_demand_this_step': 0,
        }

        self.assertDictEqual(result, expected_result)

    def test_case6(self):
        # Case 6: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 4kWh

        # Set the battery capcity and check the available capacity is 8kWh
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.92)
        self.assertEqual(self.control.battery.get_charge_capacity(), 8)

        self.control._set_state(
            load=2, solar_gen=14, tou_tariff=1, battery_soc=0.92
        )

        result = self.control.balance_energy(action=4)

        expected_charge = 8.0

        expected_result = {
            'to_purchase': 0,
            'charged_this_step': expected_charge,
            'discharged_this_step': 0,
            'excess_this_step': 12
            - expected_charge / self.control.battery.efficiency,
            'unmet_demand_this_step': 0,
        }

        self.assertDictEqual(result, expected_result)

    def test_case7(self):
        # Case 7: energy balance is 12kWh, available_charge_capacity = 8kWh, purchase request = 0kWh
        # Set the battery capcity and check the available capacity is 8kWh
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_soc(0.92)
        self.assertEqual(self.control.battery.get_charge_capacity(), 8)

        self.control._set_state(
            load=2, solar_gen=14, tou_tariff=1, battery_soc=0.92
        )

        result = self.control.balance_energy(action=0)

        expected_charge = 8.0

        expected_result = {
            'to_purchase': 0,
            'charged_this_step': expected_charge,
            'discharged_this_step': 0,
            'excess_this_step': 12
            - expected_charge / self.control.battery.efficiency,
            'unmet_demand_this_step': 0,
        }
        self.assertDictEqual(result, expected_result)

    def test_case8(
        self,
    ):  # Testing the negative power balance path with 0 purchase request but enough battery
        # case 8: energy balance is -8kWh, available_discharge_capacity = 10kWh, purchase request = 0
        # setup the battery:
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.50)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 10)

        # setup the microgrid
        self.control._set_state(
            load=10, solar_gen=2, tou_tariff=1, battery_soc=0.50
        )

        # Get the result with 0 purchase request
        result = self.control.balance_energy(action=0)

        expected_discharge = 8
        expected_soc = round(
            (
                0.50
                - (expected_discharge / self.control.battery.efficiency) / 100
            ),
            12,
        )  # 0.50 - (8/0.9)/100 = 0.4111
        expected_result = {
            'to_purchase': 0,
            'charged_this_step': 0,
            'discharged_this_step': expected_discharge,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        # Check that the battery discharged as expected.
        self.assertEqual(expected_soc, self.control.battery.get_soc())

        # Check that the result is equal.
        self.assertDictEqual(result, expected_result)

    def test_case9(self):  # Testing ar
        # case 9: energy balance is -8kWh, available_discharge_capacity = 10kWh, purchase request = 8kwh

        # setup the battery
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.5)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 10)

        # setup the microgrid
        self.control._set_state(
            load=10, solar_gen=2, tou_tariff=1, battery_soc=0.5
        )

        # Get the result with 8kWh purchase request
        result = self.control.balance_energy(action=8)

        expected_soc = 0.5
        expected_result = {
            'to_purchase': 8,
            'charged_this_step': 0,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        # Check that the battery discharged as expected.
        self.assertEqual(expected_soc, self.control.battery.get_soc())
        self.assertDictEqual(result, expected_result)

    def test_case10(
        self,
    ):  # Testing Artifical Possitive Balance path (Need to check this with over purchase as well. )
        # case 10: energy balance is -8kWh, available_discharge_capacity = 10kWh, purchase_request = 10 kWh

        # setup the battery
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.5)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 10)

        # setup the microgrid
        self.control._set_state(
            load=10, solar_gen=2, tou_tariff=1, battery_soc=0.5
        )

        # Get the result with 8kWh purchase request
        result = self.control.balance_energy(action=10)

        expected_charge = (-8 + 10) * self.control.battery.efficiency

        expected_soc = (
            0.5 + (expected_charge) / 100
        )  # 0.5 + (2*0.9)/100 = 0.518

        expected_result = {
            'to_purchase': 10,
            'charged_this_step': expected_charge,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        # Check that the battery discharged as expected.
        self.assertDictEqual(result, expected_result)
        self.assertEqual(expected_soc, self.control.battery.get_soc())

    def test_case11(self):  # Testing Negative energy balance path.
        # case 11: energy balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request = 0

        # setup the battery:
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.48)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 8)

        # setup the microgrid
        self.control._set_state(
            load=12, solar_gen=2, tou_tariff=1, battery_soc=0.48
        )

        result = self.control.balance_energy(action=0)

        expected_discharge = 8 * self.control.battery.efficiency
        expected_soc = 0.4
        expected_purchase = 10 - expected_discharge
        expected_result = {
            'to_purchase': expected_purchase,
            'charged_this_step': 0,
            'discharged_this_step': expected_discharge,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertEqual(expected_soc, self.control.battery.get_soc())
        self.assertDictEqual(result, expected_result)

    def test_case12(self):
        # case 12: energy_balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request = 2kWh
        # setup the Battery:
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.48)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 8)

        # setup the microgrid
        self.control._set_state(
            load=12, solar_gen=2, tou_tariff=1, battery_soc=0.48
        )

        result = self.control.balance_energy(action=2)

        expected_discharge = 8 * self.control.battery.efficiency
        expected_soc = 0.4
        expected_purchase = 10 - expected_discharge
        expected_result = {
            'to_purchase': expected_purchase,
            'charged_this_step': 0,
            'discharged_this_step': expected_discharge,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertEqual(expected_soc, self.control.battery.get_soc())
        self.assertDictEqual(result, expected_result)

    def test_case13(self):
        # case 13: energy_balance is -10kWh, available_discharge_capacity = 8kWh, purchase_request = 4

        # setup the Battery:
        self.control.battery._set_battery_capacity(100)
        self.control.battery._set_battery_soc_cutoff(0.4)
        self.control.battery._set_soc(0.48)
        self.assertEqual(self.control.battery.get_discharge_capacity(), 8)

        # setup the microgrid
        self.control._set_state(
            load=12, solar_gen=2, tou_tariff=1, battery_soc=0.48
        )

        result = self.control.balance_energy(action=4)

        expected_discharge = 6
        expected_soc = round(
            (
                0.48
                - (expected_discharge / self.control.battery.efficiency) / 100
            ),
            12,
        )  # 0.48 - (6/0.9)/100 = 0.4133333333
        expected_purchase = 4
        expected_result = {
            'to_purchase': expected_purchase,
            'charged_this_step': 0,
            'discharged_this_step': expected_discharge,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0,
        }

        self.assertEqual(expected_soc, self.control.battery.get_soc())
        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
