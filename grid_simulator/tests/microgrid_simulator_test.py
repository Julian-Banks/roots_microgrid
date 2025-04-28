from microgrid_simulator import microGridSimulator
from typing import Dict
import unittest


class TestMicroGridSimulator(unittest.TestCase):
    
    def setUp(self):
        self.microgrid_simulator = microGridSimulator()
    
    def tearDown(self):
        del self.microgrid_simulator
    
    def test_get_current_state(self):
        
        #Expected first and Last state.
        first_state : Dict[str,float] = {
            'load'          : 96.855,
            'solar_gen'     : 0.0,
            'tou_tariff'    : 1.2103, 
            'battery_soc'   : 0.5 ,
        }
        last_state : Dict[str,float] = {
            'load'          : 86.085,
            'solar_gen'     : 0.0,
            'tou_tariff'    : 1.2103, 
            'battery_soc'   : 0.5,
        }
        
        #Assert that the first state is correct (with battery_soc set to 0.5)
        state = self.microgrid_simulator.get_current_state()
        self.assertDictEqual(state,first_state)
        
        
        #Set the microgrid_simulator to the last step of the simulation. 
        last_time_step = 8759
        self.microgrid_simulator.step_state(last_time_step)
        #Assert that the last state is correct (with battery_soc set to 0.5) 
        state = self.microgrid_simulator.get_current_state()
        self.assertDictEqual(state,last_state)
        
    #if the max usable energy is more thatn the available energy balance. Then you can purchase more energy.
    # if you can purchase more, then you can only purchase up to the available energy or less.  
    # if the max usable energy is less than the energy balance then you can't request to purchase more because there will already be excess. 
    
    #Check how the system handles when there is available charge for purchase requests.
    # Case 1: energy balance is 8kWh, max_usable_energy = 10kWh, purchase request = 4kWh Output: to_purchase = 2, charged = 10, excess = 0, unmet_load = 0
    # Case 2: energy balance is 8kWh, max_usable_energy = 10kWh, purchase request = 1kWh Output: to_purchase = 1, charged = 9, excess = 0
    # Case 3: energy balance is 8kWh, max_usable_energy = 10kWh, purchase request = 0kWh Output: to_purchase = 0, charged = 8, excess = 0
    
    #Check how the system handles when there is excess. 
    # Case 4: energy balance is 12kWh, max_usable_energy = 8kWh, purchase request = 4kWh Output: to_purchase = 0, charged = 8, excess = 4
    # Case 5: energy balance is 12kWh, max_usable_energy = 8kWh, purchase request = 1kWh Output: to_purchase = 0, charged = 8, excess = 4
    # Case 6: energy balance is 12kWh, max_usable_energy = 8kWh, purchase request = 0kWh Output: to_purchase = 0, charged = 8, excess = 4
    
    def test_case1(self):
        #Case 1: energy balance is 8kWh, available_charge_capacity = 10kWh, purchase request = 4kWh Output: 
        # max_usable_charge_energy = 10/0.9 (10% lost to efficiencies), to_purchase = 10.1-8 = 2.1
        
        # to_purchase = max_usable_charge_energy - energy_balance , charged = 10, excess = 0, unmet_load = 0
        
        #Set the battery capcity and get available charge. 
        self.microgrid_simulator.battery._set_battery_capacity(100)
        self.microgrid_simulator.battery._set_soc(0.90)
        available_charge_capacity = self.microgrid_simulator.battery.get_charge_capacity()
        #Check that you have 10kw Available for charge. 
        self.assertEqual(available_charge_capacity, 10)
        
        #Set the state to known values: Energy_balance = solar-load = 8
        self.microgrid_simulator._set_state(load = 2, solar_gen = 10, tou_tariff = 1, battery_soc = 0.90)

        #Call the update_state_func
        result = self.microgrid_simulator.update_state(action = 4)
        
        expected_to_purchase = 10/self.microgrid_simulator.battery.battery_efficiency - 8
        
        expected_result = {
            'to_purchase': expected_to_purchase,
            'charged_this_step': 10,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0
        }
        
        self.assertDictEqual(result,expected_result)
        
    def test_case2(self):
        # Case 2: energy balance is 8kWh, max_usable_energy = 10kWh, purchase request = 1kWh Output: to_purchase = 1, charged = 9, excess = 0, unmet_load = 0 
       
        #Set the battery capcity and get available charge. 
        self.microgrid_simulator.battery._set_battery_capacity(100)
        self.microgrid_simulator.battery._set_soc(0.90)
        available_charge_capacity = self.microgrid_simulator.battery.get_charge_capacity()
        #Check that you have 10kw Available for charge. 
        self.assertEqual(available_charge_capacity, 10)
        
        #Set the state to known values: Energy_balance = solar-load = 8
        self.microgrid_simulator._set_state(load = 2, solar_gen = 10, tou_tariff = 1, battery_soc = 0.90)
        
        #Call the update_staete func
        result = self.microgrid_simulator.update_state(action = 1)
        
        #Expected to charge energy_balance + to purchase with efficiency applied.
        expected_charge = (8+1)*self.microgrid_simulator.battery.battery_efficiency
        
        expected_result = {
            'to_purchase': 1,
            'charged_this_step': expected_charge,
            'discharged_this_step': 0,
            'excess_this_step': 0,
            'unmet_demand_this_step': 0
        }
        self.assertDictEqual(result,expected_result)
        
    def test_case3(self): 
        # Case 3: energy balance is 8kWh, max_usable_energy = 10kWh, purchase request = 0kWh Output: to_purchase = 0, charged = 8, excess = 0
        pass 
        
if __name__ == "__main__": 
    unittest.main()