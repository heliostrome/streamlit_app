# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:19:19 2023

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
    options = ["Irrigation method", "Tank", "Pump", "Solar modules", "Financials"],  #required
    default_index = 0,  #optional
    orientation = "horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#A6A6A6"},
        "icon": {"color": "#FFFFFF", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#206239"},
    })

if selected == "Irrigation method":
    
    from pages.Add_solar_pumping_system_files.irrigation_method import *
    select_irrigation_method()
    
if selected == "Tank":
    
    from pages.Add_solar_pumping_system_files.tank import *
    tank_specification()
    #select_tank_loc()
    
if selected == "Pump":
    
    from pages.Add_solar_pumping_system_files.pump import *
    select_pump()
    
if selected == "Solar modules":
    
    from pages.Add_solar_pumping_system_files.solar_modules import *
    select_module()
    pv_stringing()
    pv_geometry()
    
if selected == "Financials":
    
    from pages.Add_solar_pumping_system_files.financials import *
