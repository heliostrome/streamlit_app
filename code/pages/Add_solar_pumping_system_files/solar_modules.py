# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:44:14 2023

@author: rghot
"""

import streamlit as st
from PIL import Image  
import pandas as pd
#from .solar_module_files.solar_module_dataset import *
from .solar_module_files.solar_funcs import *
import numpy as np
from st_keyup import st_keyup

#from st_aggrid import JsCode, AgGrid, GridOptionsBuilder #https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/
#from st_aggrid.shared import GridUpdateMode
from pathlib import Path
#def format_func(option):
#    modules = get_module_params()
#    return modules[option]



def select_module():
    
    st.header("Solar resource at site")
    
    col1, col2 = st.columns([4,5])
    
    with col2:
        try:
            ghi = draw_local_irradiance()
            
        except Exception as e:
            st.write(e)
            st.write("The field location has not yet been selected")
    with col1:
        try:
            st.write(f'Annual Insolation:   {ghi.sum()/1000:.2f} kWh/m$^{2}$')
        except Exception as e:
            #st.write(e)
            pass
            
    st.header("Solar module type")
    
    
    if "pv_arr_specs" not in st.session_state:
        st.session_state["sol_arr_specs"] = {"Solar module type": np.nan}
    
           
        pv_module_type = select_solar_module()
    
    
    
    
    run_module_type = st.button('Confirm module selection')
    if run_module_type:
        st.session_state.pv_arr_specs = pv_module_type
        #st.write(results_module_type)
    
    
    
    st.markdown("""---""")
    
    
           
def pv_stringing():
    if "pv_stringing" not in st.session_state:
        st.session_state["pv_stringing"] = {"Modules in series": np.nan, "Modules in parallel": np.nan}
    
    st.header("Stringing configuration")
    
    col1, col2, col3 = st.columns([1, 1, 2], gap = "medium")
    
    with col1:
        n_series = col1.number_input(label = 'Modules in series', min_value = 0, step = 1)
        
    with col2:
        n_parallel = col2.number_input(label = 'Modules in parallel', min_value = 0, step = 1)
        
    with col3:
        path_stringing_image = Path(__file__).parent / "../Add_solar_pumping_system_files/solar_module_files/pics/PV_array_series_parallel.png"
        stringing_image = Image.open(path_stringing_image)
        st.image(stringing_image, use_column_width = True)
        
    results_pv_stringing = {"Modules in series": n_series, "Modules in parallel": n_parallel}
        
    run_pv_stringing = st.button('Confirm PV stringing')
        
    if run_pv_stringing:
        st.session_state["pv_stringing"] = results_pv_stringing
        #st.write(results_module_type)
        
def pv_geometry():
    if "pv_geometry" not in st.session_state:
                st.session_state["pv_geometry"] = {"array azimuth": np.nan, "array tilt": np.nan}
    
    st.header("Array geometry")
    
    col1, col2, col3, col4 = st.columns([1, 1, 2, 2], gap = "medium")
    
    with col1:
        azimuth = col1.number_input(label = 'Array direction', min_value = 0, max_value = 359, step = 1)
        
    with col2:
        tilt = col2.number_input(label = 'Array tilt', min_value = 0, max_value = 90, step = 1)
        
    with col3:
        path_azimuth_image = Path(__file__).parent / "../Add_solar_pumping_system_files/solar_module_files/pics/PV_azimuth.png"
        azimuth_image = Image.open(path_azimuth_image)
        st.image(azimuth_image, use_column_width = True)
        
    with col4:
        path_tilt_image = Path(__file__).parent / "../Add_solar_pumping_system_files/solar_module_files/pics/PV_tilt.png"
        tilt_image = Image.open(path_tilt_image)
        st.image(tilt_image, use_column_width = True)
        
    results_pv_geometry = {"array azimuth": azimuth, "array tilt": tilt}
        
    run_pv_geometry = st.button('Confirm PV geometry')
        
    if run_pv_geometry:
        st.session_state["pv_geometry"] = results_pv_geometry
        #st.write(results_module_type)
        
        
    try:
        get_pv_outputs()
    except Exception as e:
        #st.write(e)
        pass