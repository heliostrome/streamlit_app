# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 17:03:03 2023

@author: rghot
"""
import streamlit as st  
from streamlit_option_menu import option_menu

from PIL import Image

import sys 
import os

#import pandas as pd
#import leafmap.foliumap as leafmap
#from PIL import Image


#from pyproj import Geod
#from shapely.geometry import Polygon

st.set_page_config(layout="wide", page_title="Input field data")
with st.sidebar.container():
    image = Image.open("F:\\OneDrive\\Personal\\Heliostrome\\UI\\Frontend\\Logo for frontend\\HelioStrome-logo_DarkGreen_Web_resized.png")
    st.image(image, use_column_width = True)
    
# horizontal menu

selected = option_menu(
    menu_title = None, #required
    options = ["Field location", "Soil", "Crop"],  #required
    default_index = 0,  #optional
    orientation = "horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#A6A6A6"},
        "icon": {"color": "#FFFFFF", "font-size": "18px"}, 
        "nav-link": {"font-size": "24px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#206239"},
    })

if selected == "Field location":
    #from Input_field_data_files import field_location
    sys.path.append(os.path.abspath("F:\\OneDrive\\Personal\\Heliostrome\\UI\\Frontend\\pages\\Input_field_data_files"))
    from field_location import *
    get_field_location()
    
if selected == "Soil":
    sys.path.append(os.path.abspath("F:\\OneDrive\\Personal\\Heliostrome\\UI\\Frontend\\pages\\Input_field_data_files"))
    from soil import *
    select_soil_mass_fracs()
    
if selected == "Crop":
    #from Input_field_data_files import field_location
    sys.path.append(os.path.abspath("F:\\OneDrive\\Personal\\Heliostrome\\UI\\Frontend\\pages\\Input_field_data_files"))
    from crop import *
    select_crop()
    select_sowing_date()