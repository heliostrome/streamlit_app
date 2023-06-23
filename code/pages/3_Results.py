# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 15:30:59 2023

@author: rghot
"""

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import sys
import os
from pathlib import Path

st.set_page_config(layout="wide", page_title="Add Solar Pumping System")
with st.sidebar.container():
    path_logo = Path(__file__).parent / "../Logo for frontend/HelioStrome-logo_DarkGreen_Web_resized.png"
    image = Image.open(path_logo)
    st.image(image, use_column_width = True)
    

# horizontal menu

selected = option_menu(
    menu_title = None, #required
    options = ["Solar-pump sizing", "Tank use", "Rainfed results"],  #required
    default_index = 0,  #optional
    orientation = "horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#A6A6A6"},
        "icon": {"color": "#FFFFFF", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#206239"},
    })

if selected == "Solar-pump sizing":
    
    from pages.Results_files.pv_pump_sizing import *
    #hello_world()
    plot_iv_curve()
      
    
if selected == "Tank use":
    
    from pages.Results_files.tank_use import *
    hello_world()
    #select_tank_loc()
    
if selected == "Rainfed results":
    
    from pages.Results_files.irrigation import *
    #prepare_climate_file()
    irrigation_results()
    

