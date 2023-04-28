# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:08:22 2023

@author: rghot
"""

#from .irrigation_files.view_precipitation import *
from .irrigation_files.retrieve_precipitation import *
from .irrigation_files.pyeto_funcs import *
import streamlit as st
from pvlib.iotools import get_pvgis_hourly
from pvlib.atmosphere import alt2pres

def prepare_climate_file ():
    #df_precip = get_precipitation() #obtains precipitation values for a year at the set location
    
    #(start_date_str, end_date_str) = get_start_end_dates()  #gets the strat and end dates for the precipitation
    
    #st.write(start_date_str, end_date_str)
    
    #Collect solar irradiance data
    df_solar, inputs, defs = get_pvgis_hourly(latitude = latitude, longitude = longitude, components = False, surface_tilt=0, surface_azimuth=0, outputformat = 'csv', optimalangles = True)
    
    start_datetime = df.index[0].replace(tzinfo=None)  
    end_datetime =df.index[-1].replace(tzinfo=None)
    df_solar.index = pd.date_range(start=start_datetime, end=end_datetime, freq = 'H')  #resets the index to a specific year
    
    #gets daily GHI by summing the resampled values and then converts Watt to MJ
    et_daily = pd.DataFrame(index = pd.date_range(start=start_datetime.date(), end=end_datetime.date(), freq = 'D'), 
                        columns = ["net_rad(MJ/m2)", "t_mean(K)", "t_mean(C)","t_max(C)", "t_min(C)", "rh_mean(%)", 
                                    "ws(m/s)", "svp(kPa)", "avp(kPa)", "delta_svp", "psy", "et_ref(mm/day)"])
    
    #gets daily air temperature by performing operation on the resampled values

    et_daily["t_mean(K)"] = (df.resample('D')['temp_air'].mean()).apply(celsius2kelvin) #mean daily temperature in K

    et_daily["t_mean(C)"] = (df.resample('D')['temp_air'].mean()) #mean daily temperature in C

    et_daily["t_max(C)"] = (df.resample('D')['temp_air'].max()) #maximum daily temperature in C

    et_daily["t_min(C)"]= (df.resample('D')['temp_air'].min()) #minimum daily temperature in C
    
    #gets daily mean wind speed by averaging the resampled values (unknown height of measurement, so not corrected)
    et_daily["ws(m/s)"] = df.resample('D')['wind_speed'].mean()
    
    #calculates the saturation vapour pressure (kPa) from the mean daily temperature in C
    #et_daily.svp = et_daily.apply(lambda row: svp_from_t(row["t_mean"]), axis = 1) 

    et_daily["svp(kPa)"] = et_daily.apply(lambda row: svp_from_t(row["t_mean(C)"]), axis = 1)
    
    #calculates the mean daily relative humidity
    #et_daily["rh_mean(%)"] = df.resample('D')['relative_humidity'].mean() 

    #calculates the actual vapour pressure (kPa) from mean daily relative humidity
    et_daily["avp(kPa)"] = et_daily["t_min(C)"].apply(avp_from_tmin)
    
    #calculates the slope of saturation vapour pressure curve [kPa/degC] from the daily mean air temperature
    et_daily.delta_svp = et_daily.apply(lambda row: delta_svp(row["t_mean(C)"]), axis = 1) 
    
    #NEEDS TO BE CHANGED ONCE ALTITUDE VALUES ARE OBTAINED
    alt2pres(altitude)
    
    #Calculates the psychrometric constant, γ  in  [kPa deg C] \ 
    #this relates the partial pressure of water in air to the air temperature
    et_daily.psy = psy_const ((alt2pres(altitude) * 1e-3))
    
    et_daily["et_ref(mm/day)"] = et_daily.apply(lambda row: fao56_penman_monteith(row["net_rad(MJ/m2)"], 
                                                                   row["t_mean(K)"],  
                                                                   row["ws(m/s)"],  
                                                                   row["svp(kPa)"],  
                                                                   row["avp(kPa)"],  
                                                                   row["delta_svp"],  
                                                                   row["psy"]), axis = 1)
    
    st.write(et_daily)
    