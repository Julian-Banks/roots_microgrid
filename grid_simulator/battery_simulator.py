
import pandas as pd 
from io import StringIO
from typing import Dict, Tuple

class BatterySimulator():
    
    def __init__(self, battery_soc :float = 0.5, battery_capacity :float = 1, battery_C_rate :float = 0.2, battery_efficiency :float = 0.9, battery_soc_cuttoff :float  = 0.4, time_interval :float = 1):
        
        #yusis, should I just make a battery module to import. Might make this a whole lot more readable. 
        ### State of Charge stuff (SOC)
        self.battery_soc :float = battery_soc
        self.battery_soc_cuttoff :float  = battery_soc_cuttoff #Lower limit to the Battery_soc
        
        ### Charge and discharge stuff. Maybe I can use C_rate for both? Must look up more info.
        #Note: C_rate is in amps usually, I am currently using it in energy 
        self.battery_C_rate :float = battery_C_rate# C rate for dis/charging the battery. 1C is it can charge fully in 1 hour. 0.2 means it can charge fully in 5 hours (charges at a rate of 0.2C)
        self.battery_efficiency :float = battery_efficiency #Charge and discharge efficiency of the battery 
        self.time_interval :float = time_interval #time interval for charges and discharges, should it be here? (Unit: hours)
                
        ### Metrics in kWh for understanding and conversions.
        self.battery_capacity :float = battery_capacity
        

    def charge(self, charge_energy : float ) -> Tuple[ float,float]: 
        #energy that is being passed in: Charge energy. (UNITS: kWh) (SHOULD IT BE kW???? and be a power rather than an energy if I am using a time interval???)
        #default time stamp is 1 hour. Need to add logic that handles different times. 
        #determin how much of the available charge_energy can be stored in the battery.
        # There are two catch points. Charge Rate and Available Battery Capacity.
        #example
        # I have 10kw available for 1 hour (10kWh)
        # Charge Rate is only 8kWh 
        # So I immediately have 2kWh excess
        # Of that 8kWh there is only 5kWh available capacity in the battery
        # So in the end 5kWh Goes to the battery. and 5kWh is excess. 
        
        excess: float = 0        
        charged:float = 0
        
        #inside battery side:
        max_charge_energy : float = self.get_charge_capacity()
        
        #out of battery:
        max_charge_energy = max_charge_energy/self.battery_efficiency
        
        if charge_energy<max_charge_energy: 
            charged = charge_energy*self.battery_efficiency
            self.update_soc(charged)
        else:
            charged = max_charge_energy*self.battery_efficiency #Back to inside battery...
            self.update_soc(charged)
            excess = charge_energy - (max_charge_energy)        

        return charged, excess
    
    #Get the amount of energy that can go into the battery. Note that the amount of energy used would be energy_in/battery_efficiency
    def get_charge_capacity(self) -> float:
        #get the available capcity
        available_capacity: float = self.battery_capacity - self.get_battery_energy()
        
        #Calculate the max energy that can be used by the battery based on its max rate of charge. 
        max_charge_rate: float= self.battery_C_rate*self.battery_capacity*self.time_interval
        
        #Return the smaller of the two.
        charge_capacity: float = min(max_charge_rate, available_capacity)
        
        return charge_capacity
    
    def discharge(self,discharge_energy: float) -> Tuple[float, float]:
        #Two things to watch out for:
        #1. The max discharge rate.
        #2. Depth of discharge setpoints. 
        
        discharged:float = 0
        unmet_demand:float = 0
        
        #inside the battery side:
        max_discharge_energy = self.get_discharge_capacity()
        
        #out of battery: 
        max_discharge_energy = max_discharge_energy/self.battery_efficiency
        
        if discharge_energy < max_discharge_energy: 
            discharged = discharge_energy*self.battery_efficiency
            self.update_soc(-discharged)
        else:
            discharged = max_discharge_energy*self.battery_efficiency
            self.update_soc(-discharged)
            unmet_demand = discharge_energy - (max_discharge_energy)
        
        return discharged, unmet_demand
    
    def get_discharge_capacity(self) -> float: 
        avail_battery_energy:float = self.battery_capacity*(self.get_soc()-self.battery_soc_cuttoff)
        
        max_discharge_rate: float  = min(self.battery_C_rate*self.battery_capacity*self.time_interval, avail_battery_energy)
        
        discharge_capacity : float = min(max_discharge_rate, avail_battery_energy)
        
        return discharge_capacity
    
    def get_battery_energy(self) -> float:
        return self.battery_capacity * self.get_soc()
    
    def get_soc(self) -> float:
        return self.battery_soc
    
    def _set_soc(self,soc) -> float:
        self.battery_soc = soc
        return self.battery_soc
 
    def _set_battery_capacity(self,battery_capacity) -> float:
        "internal func for setting battery capcity during testing."
        self.battery_capacity = battery_capacity
        return self.battery_capacity
    
    def update_soc(self, energy:float ) -> float:
        self.battery_soc += energy/self.battery_capacity
        return self.battery_soc
       

    
    