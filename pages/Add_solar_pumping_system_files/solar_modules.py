# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:44:14 2023

@author: rghot
"""

import streamlit as st
from PIL import Image  
import pandas as pd
from pages.Add_solar_pumping_system_files.solar_module_dataset import *
import numpy as np
from st_keyup import st_keyup

from st_aggrid import JsCode, AgGrid, GridOptionsBuilder #https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/
from st_aggrid.shared import GridUpdateMode
from pathlib import Path
#def format_func(option):
#    modules = get_module_params()
#    return modules[option]



def select_module():
    st.header("Solar module type")
    
    
    if "sol_arr_specs" not in st.session_state:
        st.session_state.sol_arr_specs = {"Solar module type": np.nan}
    
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
        
        run_module_type = st.button('Confirm module selection')
        
        if run_module_type:
            st.session_state.solar_arr_specs = results_module_type()
            #st.write(results_module_type)
    except:
        pass       
    
    
    
    
    st.markdown("""---""")
    
    
           
def pv_stringing():
    if "pv_stringing" not in st.session_state:
                st.session_state.pv_stringing = {"Modules in series": np.nan, "Modules in parallel": np.nan}
    
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
        st.session_state.pv_stringing = results_pv_stringing
        #st.write(results_module_type)