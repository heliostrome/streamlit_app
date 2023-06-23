# -*- coding: utf-8 -*-
"""
Created on Tue May 23 12:37:31 2023

@author: rghot
"""

import streamlit as st
import datetime
from pathlib import Path
from ..pv_pump_sizing_files.pvpumpingsystem import pump as pp
from ..pv_pump_sizing_files.pvpumpingsystem import pipenetwork as pn

def get_lat_long():
    try:
        lon = st.session_state.field_loc['centroid'][0]
        lat = st.session_state.field_loc['centroid'][1]
        return lat, lon
    except:
        st.write('The site location has not yet been chosen.')

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
    
def get_alt():
    try:
        alt = st.session_state.altitude["altitude"]
        return alt
    except:
        st.write('The altitude has not yet been found.')
    
    return alt

def get_tmy():
    try:
        tmy = st.session_state["tmy"]
        return tmy["tmy"]
    except:
        st.write('The solar irradiance has not yet been found.')
    
    
def get_pv_module_type():
    try:
        pv_specs = st.session_state.pv_arr_specs
        return pv_specs["Solar module type"]
    except:
        st.write('The solar module has not yet been chosen.')
    
    
def get_pv_stringing():
    try:
        n_s = st.session_state.pv_stringing["Modules in series"]
        n_p = st.session_state.pv_stringing["Modules in parallel"]
        return n_s, n_p
    except:
        st.write('The array stringing has not yet been done.')
        
def get_pv_geometry():
    try:
        az = st.session_state.pv_geometry["array azimuth"]
        tlt = st.session_state.pv_geometry["array tilt"]
        return az, tlt
    except:
        st.write('The array geometry has not yet been added.')
    
#def get_Static_head():
#    try:
    
def get_pump_specs():
    
    path_pump = Path(__file__).parents[2] / "Add_solar_pumping_system_files/pump_files/pumps" / Path(st.session_state["pump_type"]["Pump model"][0]["Name"] + ".txt")
        
    pump = pp.Pump(path = path_pump, modeling_method = 'arab')
    #st.write(pump.specs)
    
    return pump

def get_pump_name():
    try:
        n = st.session_state["pump_type"]["Pump model"][0]["Name"]
        return n
    except:
        st.write("No pump has been selected.")
        
def get_h_static():
    if st.session_state["tank_present"] == True:
        h_stat = st.session_state["tank_specs"]["Pump head"]
        
    elif st.session_state["tank_present"] == False:
        h_stat = st.session_state["pump_specs"]["Pump head"]
    return h_stat

    
def get_pipe_length():
    if st.session_state["tank_present"] == True:
        l_pipe = st.session_state.tank_loc["Distribution line length"] + st.session_state.pump_loc["Pump line length"]
        
    elif st.session_state["tank_present"] == False:
        l_pipe = st.session_state.pump_loc["Pump line length"]
    return l_pipe

def get_pipe_dia():
    dia_pipe = st.session_state.pump_specs["Pipe line diameter"]
    return dia_pipe
      
def get_pipe_specs():
    h_static = get_h_static()
    
    pipe_length = get_pipe_length()
    
    diameter = get_pipe_dia()

    pipes = pn.PipeNetwork(h_stat = h_static,  # static head [m]
                        l_tot = pipe_length,  # length of pipes [m]
                        diam = diameter,  # diameter [m]
                        material='plastic')


    return pipes       