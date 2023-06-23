# -*- coding: utf-8 -*-
"""
Created on Thu May 25 18:00:56 2023

@author: rghot
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder #https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/
from st_aggrid.shared import GridUpdateMode


def get_pumps(path1):
    path = os.getcwd()
    
    #st.write(path1)
    files = os.listdir(path1)
    
    pumps = []
    [pumps.append(file[:-4]) for file in files if file.endswith(".txt")]
    
    df = pd.DataFrame(pumps, index = np.arange(len(pumps)), columns = ["Name"])
    
    return df

def pump_selection():
    path_pumps = Path(__file__).parent / "./pumps"
    #st.write(path_pumps)
    df = get_pumps(path_pumps)

    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode = "single", use_checkbox = True)
    
    gd.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False,) # makes columns resizable, sortable and filterable by default
    gridOptions = gd.build()
    
    dta = AgGrid(df, gridOptions=gridOptions, width = 150, height=150, allow_unsafe_jscode=True, update_mode=GridUpdateMode.SELECTION_CHANGED & GridUpdateMode.MODEL_CHANGED)
    return dta['selected_rows']
        
def get_suction_head():
    val = st.number_input(label = 'Suction head (m)', min_value = 0, step = 1)
    return val

def get_dia_pipeline():
    val = st.number_input(label = 'Pipe line diameter (mm)', min_value = 0, step = 1)
    return val

def get_pump_head():
    val = st.number_input(label = 'Pump head (m)', min_value = 0.0, step = 0.5)
    return val

def pump_suction_tank_image():
    path_pump_suction_tank_image = Path(__file__).parent / "../pump_files/pics/Pump_suction_head_tank.png"
    pump_suction_tank_image = Image.open(path_pump_suction_tank_image)
    st.image(pump_suction_tank_image, caption = 'Pump specifications', use_column_width = True)

def pump_suction_no_tank_image():
    path_pump_suction_notank_image = Path(__file__).parent / "../pump_files/pics/Pump_suction_head_no_tank.png"
    pump_suction_notank_image = Image.open(path_pump_suction_notank_image)
    st.image(pump_suction_notank_image, caption = 'Pump specifications', use_column_width = True)