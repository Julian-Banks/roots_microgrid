from typing import Tuple
import pandas as pd

class SolarSimulator():
    
    def __init__(self, kw_peak:float = 2500, inverter_efficiency:float = 0.9):
        self.kw_peak = kw_peak
        self.inverter_efficiency = inverter_efficiency
        self.solar_generation = self.setup_solar_generation()
        
    def setup_solar_generation(self) -> list:
        df = pd.read_csv("data.csv")
        solar_generation = df["solar_gen"].tolist()
        return solar_generation
    
    
    def get_current_solar_generation(self, timestep:int)->float:
        return self.solar_generation[timestep]
        
    



