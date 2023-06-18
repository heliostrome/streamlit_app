# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 10:59:35 2023

@author: rghot
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
from .soil_files.soil_funcs import *


def default_slider_key(soil_split):
    if st.session_state["soil_fracs"] != (soil_split[0], soil_split[1]):  #intital value -> soil_split[0] is clay fraction and soil_split[1] is clay + sand fractions
        st.session_state["soil_fracs"] = (soil_split[0], soil_split[1])
        

def select_soil():
    
    bbox = default_soil_value()
    
    st.write(bbox)
    

def select_soil_mass_fracs():
    
    st.header("Soil mass fractions*")
    #st.write("**Adjust the sliders to input data from a soil test.**")
    
    col1, col2 = st.columns([4,3])
    
    
    
    with col2:
        path_soil_image = Path(__file__).parent / "../Input_field_data_files/soil_files/pics/soil_texture_triangle.jpg"
        soil_image = Image.open(path_soil_image)
        st.image(soil_image, caption = 'Soil Textural Triangle', use_column_width = True)
        
    with col1:
        if "soil_fracs" not in st.session_state:
            st.session_state["soil_fracs"] = default_soil_value() #initialise with default
        
        default_soil = st.session_state["soil_fracs"]
        values = st.slider(
            'Soil fraction',
            0., 1000., st.session_state["soil_fracs"], label_visibility = "hidden") #, key = "soil_fracs"
            
        c1, c2, c3, c4, c5 = st.columns(5, gap = "small")

        with c1:
            st.write("Clay fraction (g/kg)")
            
        with c3:
            st.write("Sand fraction (g/kg)")
            
            st.write("**Soil mass fractions (g/kg)**")
            
        with c5:
            st.write("Silt fraction (g/kg)")
    
    
    
    
    st.markdown("""---""")
    
    
    col1, col2 = st.columns([1,6], gap = "small")
    
    soil_class = soiltexturalclass((st.session_state["soil_fracs"][1] - st.session_state["soil_fracs"][0])/10, st.session_state["soil_fracs"][0]/10)
    if ["soil_class"] not in st.session_state:
        st.session_state["soil_class"] = {"soil class": soil_class}
    
    st.write("Soil class: ", soil_class)
    st.write("Clay: ", st.session_state["soil_fracs"][0])
    st.write("Sand: ", st.session_state["soil_fracs"][1] - st.session_state["soil_fracs"][0])
    st.write("Silt: ", 1000 - st.session_state["soil_fracs"][1])
    #TO BE FIXED - default button
    #with col1:
    #    default = st.button("Restore default", on_click = default_slider_key(default_soil), key="default") #https://docs.streamlit.io/knowledge-base/using-streamlit/widget-updating-session-state
    
    st.write("$*$ The soil mass fractions provided by default are obtained via satellite imagery.")
    #st.write('Values:', values)
    #st.write(st.session_state["soil_fracs"])
    
    