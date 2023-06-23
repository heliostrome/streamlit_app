# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:08:22 2023

@author: rghot
"""



import streamlit as st
import pandas as pd
import numpy as np
from pvlib.iotools import get_pvgis_hourly
from pvlib.atmosphere import alt2pres
import requests
import json
from urllib.parse import quote
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement #if running in Windows, check https://github.com/aquacropos/aquacrop/issues/84
from aquacrop.utils import prepare_weather
from datetime import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
from .pyeto_funcs import *
from ..shared_functions.shared_funcs import *



#environment = "development"
environment = "normal"



def get_soil_class():
    if environment == "development":
        return "ClayLoam"
    else:
        try:
            soil_class = st.session_state["soil_class"]
            return soil_class["soil class"]
        except:
            st.write('The soil parameters have not been retrieved.')

def get_crop_vals():
    if environment == "development":
        return "Tomato", dt.strptime('25/05/2022','%d/%m/%Y')
    else:
        try:
            crp = st.session_state["crop_type"]
            try:
                s_dt = st.session_state["sowing_date"]
                return crp["crop"][0]["Name"], s_dt["sowing date"]
            except Exception as e:
                st.write(e)
                st.write("The sowing date has not been selected.")
        except Exception as e:
            st.write(e)
            st.write("The crop type has not been selected.")
        
def plot_harvest_results(df, crop_type):
    fig,ax = plt.subplots()
    sns.barplot(data = df, x = df["Harvest Date (YYYY/MM/DD)"].dt.year,
            y = "Yield (tonne/ha)", hue = "crop Type", ax = ax)
    ax.set_xlabel(f"{crop_type} historic yield estimates")
    plt.legend([], [], frameon=False)
    st.pyplot(fig = fig, clear_figure = True)
    
def get_prepared_etdata():
    
    latitude, longitude = get_lat_long()  #get latitude and longitude
    
    #query for PVGIS hourly irradiance data on horizontal plane
    df_solar, inputs, defs = get_pvgis_hourly(latitude = latitude, longitude = longitude, components = False, surface_tilt=0, surface_azimuth=0, outputformat = 'csv', optimalangles = True, timeout = 60)
    
    start_datetime = df_solar.index[0].replace(tzinfo=None)  #starttime - based on Sarah satellite values
    end_datetime =df_solar.index[-1].replace(tzinfo=None)    #endtime - based on Sarah satellite values
    
    df_solar.index = pd.date_range(start=start_datetime, end=end_datetime, freq = 'H')  #resets the index to correct format
    
    #creates data frame for et values
    et_daily = pd.DataFrame(index = pd.date_range(start=start_datetime.date(), end=end_datetime.date(), freq = 'D'), 
                        columns = ["net_rad(MJ/m2)", 
                                   "t_mean(K)", 
                                   "t_mean(C)",
                                   "t_max(C)", 
                                   "t_min(C)", 
                                   #"rh_mean(%)", 
                                    "ws(m/s)", 
                                   "svp(kPa)", 
                                   "avp(kPa)", 
                                   "delta_svp", 
                                   "psy", 
                                   "et_ref(mm/day)"])
    
    #gets daily GHI by summing the resampled values and then converts Watt to MJ
    et_daily["net_rad(MJ/m2)"] = df_solar['poa_global'].resample('D').sum().apply(watthour2megajoule)

    #gets daily air temperature by performing operation on the resampled values
    et_daily["t_mean(K)"] = df_solar['temp_air'].resample('D').mean().apply(celsius2kelvin) #mean daily temperature in K
    
    et_daily["t_mean(C)"] = df_solar['temp_air'].resample('D').mean() #mean daily temperature in C
    
    et_daily["t_max(C)"] = df_solar['temp_air'].resample('D').max() #maximum daily temperature in C
    
    et_daily["t_min(C)"]= df_solar['temp_air'].resample('D').min() #minimum daily temperature in C
    
    
    #gets daily mean wind speed at 2m height by averaging the resampled values (height of measurement = 10 m, so correction applied)
    et_daily["ws(m/s)"] = df_solar['wind_speed'].resample('D').mean().apply(lambda x: wind_speed_2m(x, 10))
    
    #calculates the saturation vapour pressure (kPa) from the mean daily temperature in C
    #et_daily.svp = et_daily.apply(lambda row: svp_from_t(row["t_mean"]), axis = 1) 

    et_daily["svp(kPa)"] = et_daily.apply(lambda row: svp_from_t(row["t_mean(C)"]), axis = 1)
    
    #calculates the mean daily relative humidity (available only in TMY)
    #et_daily["rh_mean(%)"] = df_solar.resample('D')['relative_humidity'].mean() 

    #calculates the actual vapour pressure (kPa) from mean daily relative humidity
    et_daily["avp(kPa)"] = et_daily["t_min(C)"].apply(avp_from_tmin)
    
    #calculates the slope of saturation vapour pressure curve [kPa/degC] from the daily mean air temperature
    et_daily.delta_svp = et_daily.apply(lambda row: delta_svp(row["t_mean(C)"]), axis = 1) 
    
    #altitude obtained from pvgis query
    altitude = inputs["elevation"]
    if "altitude" not in st.session_state:
                st.session_state["altitude"] = {"altitude": altitude}
    
    #Calculates the psychrometric constant, γ  in  [kPa deg C] / 
    #this relates the partial pressure of water in air to the air temperature
    et_daily.psy = psy_const (Pascal2kiloPascal(alt2pres(altitude)))
    
    et_daily["et_ref(mm/day)"] = et_daily.apply(lambda row: fao56_penman_monteith(row["net_rad(MJ/m2)"], 
                                                                   row["t_mean(K)"],  
                                                                   row["ws(m/s)"],  
                                                                   row["svp(kPa)"],  
                                                                   row["avp(kPa)"],  
                                                                   row["delta_svp"],  
                                                                   row["psy"]), axis = 1)
    return et_daily[["t_max(C)", "t_min(C)", "et_ref(mm/day)"]], start_datetime, end_datetime

def get_precipitation(start_datetime, end_datetime):
    
    latitude, longitude = get_lat_long()  #get latitude and longitude
    
    #set the base url and query parameters
    base_url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/chirps20GlobalDailyP05.json'

    query_param = f'precip[({start_datetime}):1:({end_datetime})][({latitude}):1:({latitude})][({longitude}):1:({longitude})]'
    encoded_query_param = quote(query_param, safe='():')
    url = f'{base_url}?{encoded_query_param}'
    
    #Makes the query
    response = requests.get(url=url, timeout=30)   
    data = json.loads(response.text)
    
    #sets values as dataframe

    df_p = pd.DataFrame(data['table']['rows'], columns=data['table']['columnNames'])  #sets values
    df_p['time'] = (pd.to_datetime(df_p['time'], infer_datetime_format = True)).dt.date  #adjusts the datetime to dates
    df_p.set_index(keys = 'time', drop = True, inplace = True)   # sets the dates to  the index
    
    #With the same start time and end time, precipitation gives an extra value, which is removed
    df_p.drop(df_p.tail(1).index,inplace=True)
    return df_p
    
def prepare_climate_file ():
    
    et0, start, end = get_prepared_etdata()
    
    #st.write(et0)
    
    dfp = get_precipitation(start, end)
    #st.write(dfp)
    
    #Create final climate file
    climate = pd.DataFrame(index =  et0.index , columns = ['MinTemp', 'MaxTemp', 'Precipitation', 'ReferenceET', 'Date'])
    
    
    
    #Setting temperature, precipitation and reference evapo-transpiration values in the climate file

    climate['MinTemp'] = et0['t_min(C)'].copy()
    climate['MaxTemp'] = et0['t_max(C)'].copy()
    climate['Precipitation'] = dfp['precip'].copy()
    climate['ReferenceET'] = et0['et_ref(mm/day)'].copy()
    
    #Set timestamp values in the climate file

    climate['Date'] = pd.to_datetime(et0.index)     #sets the day values
    
    
    # set limit on ET0 to avoid divide by zero errors
    climate['ReferenceET'].clip(lower=0.1, inplace=True)   #based on aquacrop file preparation requirements
    
    climate.index = np.arange(len(climate))
    #st.write(climate)
    
    return climate, start, end

def aquacrop_rainfed():
    
    
    if environment == "development":
        ####This section is used for rapid testing without running the queries
        #weather file prepare via pyeto
        filepath = "F:/OneDrive/Personal/Heliostrome/UI/Frontend/pages/Results_files/irrigation_files/Aquacrop_df.csv"
        
        weather_data = pd.read_csv(filepath, sep = ',')
        weather_data["Date"] = pd.to_datetime(weather_data["Date"].copy())
        
        #st.write(weather_data)
        #st.write(weather_data.dtypes)
        
        start_datetime = dt.strptime('01/01/2005 00:00:00','%d/%m/%Y %H:%M:%S')
        end_datetime = dt.strptime('31/12/2016 23:00:00','%d/%m/%Y %H:%M:%S')
    else:
        weather_data, start_datetime, end_datetime = prepare_climate_file()
    
    #st.write(weather_data)
    #st.write(weather_data.dtypes)
    
    
    #Set the soil parameters
    soil_type = get_soil_class()
    #st.write(soil_type)
    soil = Soil(soil_type = soil_type)
    
    #Set the crop parameters
    crop_type, sowing_dt = get_crop_vals()
    
    
    #Setting the crop and crop type
    crop = Crop(crop_type, planting_date = sowing_dt.strftime("%m/%d")) #Planting Date (mm/dd) as per aquacrop https://github.com/aquacropos/aquacrop/blob/master/aquacrop/entities/crop.py
    
    #Initial soil moisture conditions
    InitWC = InitialWaterContent(value=['FC'])  #Note: Need to investigate houw realistic beginning with Field Capacity (FC) is
    
    #Defining the irrigation management strategy
    irr_mngt = IrrigationManagement(irrigation_method = 0)  #method = 0 is rainfed agriculture/ no irrrigation
    
    # combine into aquacrop model and specify start and end simulation date
    model = AquaCropModel(sim_start_time = f'{start_datetime.year}/01/01',
                      sim_end_time = f'{end_datetime.year}/12/31',
                      weather_df=weather_data,
                      soil = soil,
                      crop = crop,
                      initial_water_content=InitWC,
                     irrigation_management=irr_mngt)
    
    # run model till termination
    model.run_model(till_termination=True)
    
    #Show final statistics
    #st.write(model._outputs.final_stats)
    harv_date = dt.strftime(model._outputs.final_stats["Harvest Date (YYYY/MM/DD)"].iloc[0].date(),'%d %B')
    
    yearly_crop_cycles = len(model._outputs.final_stats["Season"]) / model._outputs.final_stats["Harvest Date (YYYY/MM/DD)"].dt.year.nunique()
    
    return model._outputs.final_stats, crop_type, harv_date, yearly_crop_cycles


def aquacrop_irr():
    
    
    if environment == "development":
        ####This section is used for rapid testing without running the queries
        #weather file prepare via pyeto
        filepath = "F:/OneDrive/Personal/Heliostrome/UI/Frontend/pages/Results_files/irrigation_files/Aquacrop_df.csv"
        
        weather_data = pd.read_csv(filepath, sep = ',')
        weather_data["Date"] = pd.to_datetime(weather_data["Date"].copy())
        
        #st.write(weather_data)
        #st.write(weather_data.dtypes)
        
        start_datetime = dt.strptime('01/01/2005 00:00:00','%d/%m/%Y %H:%M:%S')
        end_datetime = dt.strptime('31/12/2016 23:00:00','%d/%m/%Y %H:%M:%S')
    else:
        weather_data, start_datetime, end_datetime = prepare_climate_file()
    
    #st.write(weather_data)
    #st.write(weather_data.dtypes)
    
    
    #Set the soil parameters
    soil_type = get_soil_class()
    #st.write(soil_type)
    soil = Soil(soil_type = soil_type)
    
    #Set the crop parameters
    crop_type, sowing_dt = get_crop_vals()
    
    
    #Setting the crop and crop type
    crop = Crop(crop_type, planting_date = sowing_dt.strftime("%m/%d")) #Planting Date (mm/dd) as per aquacrop https://github.com/aquacropos/aquacrop/blob/master/aquacrop/entities/crop.py
    
    #Initial soil moisture conditions
    InitWC = InitialWaterContent(value=['FC'])  #Note: Need to investigate houw realistic beginning with Field Capacity (FC) is
    
    #Defining the irrigation management strategy
    irr_mngt = IrrigationManagement(irrigation_method = 0)  #method = 0 is rainfed agriculture/ no irrrigation
    
    # combine into aquacrop model and specify start and end simulation date
    model = AquaCropModel(sim_start_time = f'{start_datetime.year}/01/01',
                      sim_end_time = f'{end_datetime.year}/12/31',
                      weather_df=weather_data,
                      soil = soil,
                      crop = crop,
                      initial_water_content=InitWC,
                     irrigation_management=irr_mngt)
    
    # run model till termination
    model.run_model(till_termination=True)
    
    #Show final statistics
    #st.write(model._outputs.final_stats)
    harv_date = dt.strftime(model._outputs.final_stats["Harvest Date (YYYY/MM/DD)"].iloc[0].date(),'%d %B')
    
    yearly_crop_cycles = len(model._outputs.final_stats["Season"]) / model._outputs.final_stats["Harvest Date (YYYY/MM/DD)"].dt.year.nunique()
    
    return model._outputs.final_stats, crop_type, harv_date, yearly_crop_cycles
    