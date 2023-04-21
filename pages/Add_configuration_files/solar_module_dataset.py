# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 18:08:24 2023

@author: rghot
"""


import pandas as pd
import os
import io
from urllib.request import urlopen
from pathlib import Path

def get_path():
    path = Path(__file__).parent / "../Add_configuration_files/solar_module_files/CEC Modules.csv"
        
    #path = "F:/OneDrive/Personal/Heliostrome/UI/Frontend/pages/Add_configuration_files/solar_module_files/CEC Modules.csv"
        
    #path = 'https://www.energy.ca.gov/sites/default/files/2021-10/PV_Module_List_Full_Data_ADA.xlsx'
    
    return path

def get_all_module_params():
    
    path = get_path()

    modules = pd.read_csv(path, sep = ",", header = 0, index_col = None,skiprows=[1, 2], usecols = ["Name", "Manufacturer", "STC", "A_c"])
    
    
    modules["Efficiency"] = modules.apply(lambda row: row["STC"]/(1000 * row["A_c"]), axis = 1)
    
    modules.rename(columns={"STC": "Rated_power", "A_c": "Area"}, inplace=True)
    
    modules["Rated_power"] = modules["Rated_power"].astype(str)
    
    modules.columns = modules.columns.str.replace(' ', '_')

    #modules = modules.transpose()
    
    return modules

def get_module_params(module):
    
    path = get_path()
    
    module_params = pd.read_csv(path, sep = ",", header = 0, skiprows=[1, 2], index_col = 0).loc[module]
    
    
    return module_params


  