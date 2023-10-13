# -*- coding: utf-8 -*-
"""
Created on Tue May 23 12:34:52 2023

@author: rghot
"""

import streamlit as st
import numpy as np
import pandas as pd

from pvlib.solarposition import get_solarposition
from pvlib.irradiance import get_extra_radiation, haydavies, get_ground_diffuse, aoi, get_total_irradiance, poa_components
from pvlib.atmosphere import get_relative_airmass, get_absolute_airmass
from pvlib.pvsystem import retrieve_sam, calcparams_cec, singlediode, i_from_v
from pvlib.temperature import faiman
import matplotlib.pyplot as plt
import seaborn as sns
from ..shared_functions.shared_funcs import *



environment = "development"
#environment = "normal"

    


def get_iv_irr_high(poa_complete, tmy_file, module, n_s, n_p):
    #Calculates the resulting IV characteristics of the solar module under high irradiance conditions and representative temperature

    #define high irradiance on the plane of array
    irr_high = poa_complete.poa_global.quantile(0.9) 
    
    #finds the 10 smallest data points where the irradiance is higher than irr_high
    #Finds the median temperature at these times as a representative value 
    temp_high = tmy_file.temp_air[poa_complete.poa_global.where(poa_complete.poa_global >= irr_high).nsmallest(n = 10, keep = 'all').index].median()
    
    #number of points needed for the IV curve
    num = 50
    
    #Collects parameters from the CEC module database and uses the defined high irradiance and temperature values
    cec_params_high = calcparams_cec (effective_irradiance = irr_high, temp_cell = temp_high, \
    alpha_sc = module["alpha_sc"], a_ref = module["a_ref"], \
    I_L_ref = module["I_L_ref"], I_o_ref = module["I_o_ref"], \
    R_sh_ref = module["R_sh_ref"], R_s = module["R_s"], Adjust = module["Adjust"])
    
    #Solve the single diode equation
    result_high = singlediode(photocurrent = cec_params_high[0], saturation_current = cec_params_high[1],
               resistance_series = cec_params_high[2], resistance_shunt = cec_params_high[3],
               nNsVth = cec_params_high[4], ivcurve_pnts = num, method = 'brentq')
    
    result = pd.DataFrame(index = np.arange(num), columns = ["v", "i"])
    result["v"] = result_high["v"] * n_s
    result["i"] = result_high["i"] * n_p
    #st.write(result)
    return result

def get_iv_irr_low(poa_complete, tmy_file, module, n_s, n_p):
    #Calculates the resulting IV characteristics of the solar module under low irradiance conditions and representative temperature

    #define low irradiance on the plane of array
    irr_low = poa_complete.poa_global.quantile(0.6) 
    
    #finds the 10 largest data points where the irradiance is lower than irr_low
    #Finds the median temperature at these times as a representative value 
    temp_low = tmy_file.temp_air[poa_complete.poa_global.where(poa_complete.poa_global <= irr_low).nlargest(n = 10, keep = 'all').index].median()
    
    #number of points needed for the IV curve
    num = 50
    
    #Collects parameters from the CEC module database and uses the defined high irradiance conditions and representative temperature
    cec_params_low = calcparams_cec (effective_irradiance = irr_low, temp_cell = temp_low, \
                                     alpha_sc = module["alpha_sc"], a_ref = module["a_ref"], \
                                     I_L_ref = module["I_L_ref"], I_o_ref = module["I_o_ref"], \
                                     R_sh_ref = module["R_sh_ref"], R_s = module["R_s"], Adjust = module["Adjust"])
    
    #Solve the single diode equation
    result_low = singlediode(photocurrent = cec_params_low[0], saturation_current = cec_params_low[1],
           resistance_series = cec_params_low[2], resistance_shunt = cec_params_low[3],
           nNsVth = cec_params_low[4], ivcurve_pnts = num, method = 'brentq')
    
    result = pd.DataFrame(index = np.arange(num), columns = ["v", "i"])
    result["v"] = result_low["v"] * n_s
    result["i"] = result_low["i"] * n_p
    #st.write(result_low)
    return result

def get_iv_irr_stc(module, n_s, n_p):
    Tcell_K = Tref_K = 25 +273.15 #at STC conditions
    nNsVth = module["a_ref"] * (Tcell_K / Tref_K)
    
    #number of points needed for the IV curve
    num = 50
    
    result_stc = singlediode(photocurrent = module["I_L_ref"], saturation_current = module["I_o_ref"],
           resistance_series = module["R_s"], resistance_shunt = module["R_sh_ref"],
           nNsVth = nNsVth, ivcurve_pnts = num, method = 'brentq')
    
    result = pd.DataFrame(index = np.arange(num), columns = ["v", "i"])
    result["v"] = result_stc["v"] * n_s
    result["i"] = result_stc["i"] * n_p
    return result

def pv_iv_calc():
        
    
    
    albedo = 0.25  #default value
    surface_type = "grass" #default value
    
    if environment == "development":
        ####This section is used for rapid testing 
        filepath = "F:/OneDrive/Personal/Heliostrome/UI/Frontend/pages/Results_files/pv_pump_sizing_files/Mozambique_TMY.csv"
        
        tmy = pd.read_csv(filepath, sep = ',', index_col = 0)  #, infer_datetime_format = True
        tmy.index = pd.to_datetime(tmy.index.copy())
        
        latitude, longitude = 33.07, -24.7
        #st.write(latitude, longitude)
        
        
        azimuth,tilt = 0, 0
        #st.write(azimuth, tilt)
        
        n_series, n_parallel = 2,4
        #st.write(n_series, n_parallel)
        
        cec_modules = retrieve_sam('CECMod', 'C:\SAM\2020.2.29\libraries')
        cec_module = cec_modules['LUMA_Resources_LRSS']
        #st.write(cec_module)
        
        start_date_str, end_date_str = get_start_end_dates()
        
    else:
        tmy = get_tmy()
        #st.write(tmy)
        latitude, longitude = get_lat_long()
        #st.write(latitude, longitude)
        
        
        azimuth,tilt = get_pv_geometry()
        #st.write(azimuth, tilt)
        
        n_series, n_parallel = get_pv_stringing()
        #st.write(n_series, n_parallel)
        
        cec_module = get_pv_module_type()
        #st.write(cec_module)
        
        start_date_str, end_date_str = get_start_end_dates()
    
    #resets the index to a specific year
    tmy.index = pd.date_range(start=start_date_str, end=end_date_str, freq = 'H')
    
    #solar position in the celestial sphere
    solpos = get_solarposition(tmy.index, latitude, longitude)
    
    #Calculation of extraterrestrial direct normal irradiance (W/m^2)
    dni_extra = get_extra_radiation(tmy.index)
    
    #Calculation of relative Air Mass
    rel_airmass = get_relative_airmass(solpos['apparent_zenith'])
    
    #total irradiance on the plane of the tilted surface
    poa_all = get_total_irradiance(surface_tilt = tilt, 
                                   surface_azimuth = azimuth, 
                                   solar_zenith = solpos["apparent_zenith"], 
                                   solar_azimuth = solpos["azimuth"], 
                                   dni = tmy["dni"], 
                                   ghi = tmy["ghi"], 
                                   dhi = tmy["dhi"], 
                                   dni_extra= dni_extra, 
                                   airmass=rel_airmass, 
                                   albedo=albedo, 
                                   surface_type=surface_type, 
                                   model="haydavies")
    
    #Calculates the cell/module temperature of the solar array in deg. C 
    #the Faiman model does not distinguish between cell and module temperature
    pv_temp = faiman(poa_global = poa_all.poa_global, temp_air = tmy.temp_air, wind_speed = tmy.wind_speed)
    
    
    #Calculation of IV curves under high, low and STC conditions
    iv_irr_high = get_iv_irr_high(poa_all, tmy, cec_module, n_series, n_parallel)
    #st.write(iv_irr_high)
    
    iv_irr_low = get_iv_irr_low(poa_all, tmy, cec_module, n_series, n_parallel)
    #st.write(iv_irr_low)
    
    iv_irr_stc = get_iv_irr_stc(cec_module, n_series, n_parallel)
    #st.write(iv_irr_stc)
    
    return iv_irr_high, iv_irr_low, iv_irr_stc

def pump_iv_calc():
    
    tdh = get_pipe().h_stat
    
    #st.write(tdh)
    
    pump = get_pump()
    
    #Function computing the IV characteristics of the pump depending on head H.
    load_fctI, intervalsVH = pump.functIforVH()
    
    # IV curve of load (pump)
    Vrange_load = np.arange(*intervalsVH['V'](tdh))
    #st.write(Vrange_load)
    
    #Calculating the pump current draw at a given voltage and total dynamic head
    I_fromVH = load_fctI(Vrange_load, tdh, error_raising=False)
    #st.write(I_fromVH)
    if I_fromVH[-1] < 0:
        st.write("The pump is oversized for this head application.")
    
    iv_pump = pd.DataFrame(index = np.arange(len(Vrange_load)), columns = ["v", "i"])
    iv_pump["v"] = Vrange_load
    iv_pump["i"] = I_fromVH
    #st.write(iv_pump)
        
    return iv_pump

    #except:
    #    st.write("No pump has been selected.")

    
def summary_specs():
    n_series, n_parallel = get_pv_stringing()
    #st.write(n_series, n_parallel)
    
    cec_module = get_pv_module_type()
    #st.write(cec_module["STC"])
    
    p_array = cec_module["STC"] * n_series * n_parallel
    
    #st.write(p_array)
    
    p_name = get_pump_name()
    
    return p_array, p_name

def draw_pv_pump_iv(iv_pvhigh, iv_pvlow, iv_pvstc, iv_pump):
    
    fig,ax = plt.subplots()
    sns.lineplot(data = iv_pvhigh, x = "v", y = "i", label = 'High Irradiance conditions', color = 'gold')
    
    sns.lineplot(data = iv_pvlow, x = "v", y = "i", label = 'Low Irradiance conditions', color = 'black')
    
    sns.lineplot(data = iv_pvstc, x = "v", y = "i", label = 'STC conditions', color = 'red')
    
    sns.lineplot(data = iv_pump, x = "v", y = "i", label = 'Pump curve', color = 'blue')

    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current (A)')
    
    st.pyplot(fig = fig, clear_figure = True)