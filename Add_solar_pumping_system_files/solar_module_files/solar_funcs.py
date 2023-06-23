# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 11:21:32 2023

@author: rghot
"""


import streamlit as st
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder #https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/
from st_aggrid.shared import GridUpdateMode
import datetime 
from pvlib.iotools import get_pvgis_tmy
from pandas import DataFrame, date_range
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pvlib.solarposition import get_solarposition
from pvlib.atmosphere import get_relative_airmass, get_absolute_airmass
from pvlib.irradiance import get_extra_radiation, haydavies, get_ground_diffuse, aoi, get_total_irradiance, poa_components
from pvlib.pvsystem import retrieve_sam, calcparams_cec, singlediode, i_from_v 
from pvlib.temperature import faiman

from .solar_module_dataset import *

def get_start_end_dates():
    
    if "sowing_date" in st.session_state:
        sowing_date = st.session_state.sowing_date["sowing date"]
        
        year = max(sowing_date.year - 1, datetime.datetime.now().year -1)  #the relevant year for the selection of precipitation data
          
    else:
        year = datetime.datetime.now().year -1
        
    #st.write (year)  
    start_date = str(year) + "-01-01 00:00"
    end_date =  str(year) + "-12-31  23:00"
    #st.write(start_date)
    #st.write(end_date)
    
    return start_date, end_date

def get_lat_long():
    
    lon = st.session_state.field_loc['centroid'][0]
    lat = st.session_state.field_loc['centroid'][1]
    
    return lat, lon

def get_pv_geometry():
    
    az = st.session_state.pv_geometry["array azimuth"]
    tlt = st.session_state.pv_geometry["array tilt"]
    return az, tlt

def get_pv_stringing():
    
    n_s = st.session_state.pv_stringing["Modules in series"]
    n_p = st.session_state.pv_stringing["Modules in parallel"]
    return n_s, n_p

def get_pv_module_type():
    module = st.session_state.pv_arr_specs["Solar module type"]
    return module

def get_iv_irr_high(poa_complete, tmy_file, module):
    #Calculates the resulting IV characteristics of the solar module under high irradiance conditions and representative temperature

    #define high irradiance on the plane of array
    irr_high = poa_complete.poa_global.quantile(0.9) 
    
    #finds the 10 smallest data points where the irradiance is higher than irr_high
    #Finds the median temperature at these times as a representative value 
    temp_high = tmy_file.temp_air[poa_complete.poa_global.where(poa_complete.poa_global >= irr_high).nsmallest(n = 10, keep = 'all').index].median()
    
    
    #Collects parameters from the CEC module database and uses the defined high irradiance and temperature values
    cec_params_high = calcparams_cec (effective_irradiance = irr_high, temp_cell = temp_high, \
    alpha_sc = module["alpha_sc"], a_ref = module["a_ref"], \
    I_L_ref = module["I_L_ref"], I_o_ref = module["I_o_ref"], \
    R_sh_ref = module["R_sh_ref"], R_s = module["R_s"], Adjust = module["Adjust"])
    
    #Solve the single diode equation
    result_high = singlediode(photocurrent = cec_params_high[0], saturation_current = cec_params_high[1],
               resistance_series = cec_params_high[2], resistance_shunt = cec_params_high[3],
               nNsVth = cec_params_high[4], ivcurve_pnts = 50, method = 'brentq')
    
    return result_high

def get_iv_irr_low(poa_complete, tmy_file, module):
    #Calculates the resulting IV characteristics of the solar module under low irradiance conditions and representative temperature

    #define low irradiance on the plane of array
    irr_low = poa_complete.poa_global.quantile(0.6) 
    
    #finds the 10 largest data points where the irradiance is lower than irr_low
    #Finds the median temperature at these times as a representative value 
    temp_low = tmy_file.temp_air[poa_complete.poa_global.where(poa_complete.poa_global <= irr_low).nlargest(n = 10, keep = 'all').index].median()
    
    #Collects parameters from the CEC module database and uses the defined high irradiance conditions and representative temperature
    cec_params_low = calcparams_cec (effective_irradiance = irr_low, temp_cell = temp_low, \
                                     alpha_sc = module["alpha_sc"], a_ref = module["a_ref"], \
                                     I_L_ref = module["I_L_ref"], I_o_ref = module["I_o_ref"], \
                                     R_sh_ref = module["R_sh_ref"], R_s = module["R_s"], Adjust = module["Adjust"])
    
    #Solve the single diode equation
    result_low = singlediode(photocurrent = cec_params_low[0], saturation_current = cec_params_low[1],
           resistance_series = cec_params_low[2], resistance_shunt = cec_params_low[3],
           nNsVth = cec_params_low[4], ivcurve_pnts = 50, method = 'brentq')
    
    return result_low

def get_iv_irr_stc(module):
    Tcell_K = Tref_K = 25 +273.15 #at STC conditions
    nNsVth = module["a_ref"] * (Tcell_K / Tref_K)
    result_stc = singlediode(photocurrent = module["I_L_ref"], saturation_current = module["I_o_ref"],
           resistance_series = module["R_s"], resistance_shunt = module["R_sh_ref"],
           nNsVth = nNsVth, ivcurve_pnts = 50, method = 'brentq')
    return result_stc

def get_pv_outputs():
    latitude, longitude = get_lat_long()
    #st.write(latitude, longitude)
    
    
    azimuth,tilt = get_pv_geometry()
    #st.write(azimuth, tilt)
    
    n_series, n_parallel = get_pv_stringing()
    #st.write(n_series, n_parallel)
    
    cec_module = get_pv_module_type()
    #st.write(cec_module)
    
    start_date_str, end_date_str = get_start_end_dates()
    
    albedo = 0.25  #default value
    surface_type = "grass" #default value
    
    #queries a Typical Meteorological Year of data from the EU PVGIS
    df, months, inputs, defs = get_pvgis_tmy(latitude, longitude, outputformat='csv', usehorizon=True, userhorizon=None, 
                                         startyear=2007, endyear=2016, url='https://re.jrc.ec.europa.eu/api/', 
                                         timeout=60, map_variables = True)
    
    
    #resets the index to a specific year
    df.index = date_range(start=start_date_str, end=end_date_str, freq = 'H')
    
    #solar position in the celestial sphere
    solpos = get_solarposition(df.index, latitude, longitude)
    
    #Calculation of extraterrestrial direct normal irradiance (W/m^2)
    dni_extra = get_extra_radiation(df.index)
    
    #Calculation of relative Air Mass
    rel_airmass = get_relative_airmass(solpos['apparent_zenith'])
    
    #total irradiance on the plane of the tilted surface
    poa_all = get_total_irradiance(surface_tilt = tilt, 
                                   surface_azimuth = azimuth, 
                                   solar_zenith = solpos["apparent_zenith"], 
                                   solar_azimuth = solpos["azimuth"], 
                                   dni = df["dni"], 
                                   ghi = df["ghi"], 
                                   dhi = df["dhi"], 
                                   dni_extra= dni_extra, 
                                   airmass=rel_airmass, 
                                   albedo=albedo, 
                                   surface_type=surface_type, 
                                   model="haydavies")
    
    #Calculates the cell/module temperature of the solar array in deg. C 
    #the Faiman model does not distinguish between cell and module temperature
    pv_temp = faiman(poa_global = poa_all.poa_global, temp_air = df.temp_air, wind_speed = df.wind_speed)
    
    
    #Calculation of IV curves under high, low and STC conditions
    iv_irr_high = get_iv_irr_high(poa_all, df, cec_module)
    #st.write(iv_irr_high)
    
    iv_irr_low = get_iv_irr_low(poa_all, df, cec_module)
    #st.write(iv_irr_low)
    
    iv_irr_stc = get_iv_irr_stc(cec_module)
    #st.write(iv_irr_stc)
    
    
    #Use of the Hay-Davies model to calculate the sky diffuse irradiance on the plane of the array
    poa_sky_diffuse = haydavies(surface_tilt = tilt,
                                surface_azimuth = azimuth,
                                dhi = df["dhi"],
                                dni = df["dni"],
                                dni_extra = dni_extra,
                                solar_zenith = solpos['apparent_zenith'],
                                solar_azimuth = solpos['azimuth'])
    
    #Use of the albedo to calculate the ground diffuse irradiance on the plane of the array
    poa_ground_diffuse = get_ground_diffuse(surface_tilt = tilt,
                                                             ghi = df["ghi"],
                                                             albedo=albedo)
    
    #calculation of the angle of incidence based on surface position and solar position. Values above 90 deg are acceptable
    angle_of_i = aoi(surface_tilt = tilt,
                               surface_azimuth = azimuth,
                               solar_zenith = solpos['apparent_zenith'],
                               solar_azimuth = solpos['azimuth'])
    
    poa_comps = poa_components(aoi = angle_of_i,
                                                dni = df["dni"],
                                                poa_sky_diffuse = poa_sky_diffuse,
                                                poa_ground_diffuse = poa_ground_diffuse)
    
def draw_local_irradiance():
    
    latitude, longitude = get_lat_long()
    #st.write(latitude, longitude)
    
    
    #queries a Typical Meteorological Year of data from the EU PVGIS
    df, months, inputs, defs = get_pvgis_tmy(latitude, longitude, outputformat='csv', usehorizon=True,
                                        userhorizon=None, 
                                         startyear=2007,
                                         endyear=2016,
                                         url='https://re.jrc.ec.europa.eu/api/', 
                                         timeout=60,
                                         map_variables = True)
    #gets the start and end dates
    start_date_str, end_date_str = get_start_end_dates()
    
    #resets the index to a specific year
    df.index = date_range(start=start_date_str, end=end_date_str, freq = 'H')
    
    
    if "tmy" not in st.session_state:
        st.session_state["tmy"] = {"tmy": df}
        
    #groups by month
    dfm = df["ghi"].groupby(lambda x: x.month).sum()/1000  #Wh to kWh
    
    fig,ax = plt.subplots()
    #ax = df["ghi"].plot(color = "gold")
    dfm.plot.bar(ax = ax, color = "gold")
    ax.set_ylabel("Global Horizontal Insolation\n($kWh/m^{2}$)")
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    #fig.autofmt_xdate()
    st.pyplot(fig = fig, clear_figure = True)
    
    return df['ghi']
    
    
def select_solar_module():
    modules = get_all_module_params()
    #st.write(modules)
    gd = GridOptionsBuilder.from_dataframe(modules)
    gd.configure_selection(selection_mode = "single", use_checkbox = True)
    
    gd.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False,) # makes columns resizable, sortable and filterable by default
    gridOptions = gd.build()
    
    dta = AgGrid(modules, gridOptions=gridOptions, height=250, allow_unsafe_jscode=True, update_mode=GridUpdateMode.SELECTION_CHANGED & GridUpdateMode.MODEL_CHANGED)
    
    
    #st.write(dta['selected_rows'])
    
    try:
        module_type = dta['selected_rows'][0]["Name"]
        #st.write(module_type)
        results_module_type = {"Solar module type": get_module_params(module_type)}
        #st.write(results_module_type)
        return results_module_type
    except Exception as e:
        #st.write (e)
        pass
        
    
    
    
    
    
    
    
    
    
    