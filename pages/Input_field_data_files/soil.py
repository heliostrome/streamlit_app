# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 10:59:35 2023

@author: rghot
"""

import streamlit as st
import pandas as pd



def default_slider_key():
    if st.session_state["soil_fracs"] != (333, 763):  #intital value
        st.session_state["soil_fracs"] = (333,763)
        

def default_soil_value():
    return (333, 763)

def select_soil_mass_fracs():
    
    st.header("Soil mass fractions*")
    st.write("**Adjust the sliders to input data from a soil test.**")
    
    if "soil_fracs" not in st.session_state:
        st.session_state["soil_fracs"] = default_soil_value() #initialise with default
    
    
    values = st.slider(
        'Soil fraction',
        0, 1000, st.session_state["soil_fracs"], label_visibility = "hidden", key = "soil_fracs")
    
    
    col1, col2, col3, col4, col5 = st.columns(5, gap = "small")
    
    with col1:
        st.write("Clay fraction (g/kg)")
        
    with col3:
        st.write("Sand fraction (g/kg)")
        
        st.write("**Soil mass fractions (g/kg)**")
        
    with col5:
        st.write("Silt fraction (g/kg)")
    
    st.markdown("""---""")
    
    
    col1, col2 = st.columns([1,6], gap = "small")
    
    with col1:
        default = st.button("Restore default", on_click = default_slider_key, key="default") #https://docs.streamlit.io/knowledge-base/using-streamlit/widget-updating-session-state
    
    st.write("$*$ The soil mass fractions provided by default are obtained via satellite imagery.")
    #st.write('Values:', values)
    #st.write(st.session_state["soil_fracs"])
    
    