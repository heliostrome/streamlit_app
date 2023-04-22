# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:11:31 2023

@author: rghot
"""


import streamlit as st  
import pandas as pd
from PIL import Image
import numpy as np
from pages.Input_field_data_files.crop_dataset import *
import datetime
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder #https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/
from st_aggrid.shared import GridUpdateMode

def select_crop():
    if "crop_type" not in st.session_state:
                st.session_state.crop_type = np.nan
    
    st.header("Select the crop to be grown.")
    
    
    df = get_crop_names()
    
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode = "single", use_checkbox = True)
    
    gd.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False,) # makes columns resizable, sortable and filterable by default
    gridOptions = gd.build()
    
    dta = AgGrid(df, gridOptions=gridOptions, height=250, allow_unsafe_jscode=True, update_mode=GridUpdateMode.SELECTION_CHANGED & GridUpdateMode.MODEL_CHANGED)
    
    crop_type = dta['selected_rows']
        
    results_crop = {'crop': crop_type}
    
    run_crop = st.button('Confirm crop selection')
    
    st.markdown("""---""")
    
    if run_crop:
        st.session_state.crop_type = results_crop
        #st.write(results_crop)
 
    
    
def select_sowing_date():
    if "sowing_date" not in st.session_state:
                st.session_state.sowing_date = {
                    'sowing_date': np.nan}
    st.header("**Select the date when the crop will be sown**")
    d = st.date_input(
    label = "",
    )
    #st.write(d)
    results_sowing_date = {'sowing_date': d}
    
    run_sowing_date = st.button('Confirm sowing date')
    
    
          
    if run_sowing_date:
        st.session_state.sowing_date = results_sowing_date
        #st.write(results_sowing_date)
        st.write("**Proceed to add a Solar Pumping System (SPS)**")
        
        st.markdown("""---""")
        
    
    