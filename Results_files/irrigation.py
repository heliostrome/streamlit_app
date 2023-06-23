# -*- coding: utf-8 -*-
"""
Created on Wed May 17 14:28:47 2023

@author: rghot
"""
import streamlit as st
from .irrigation_files.irrigation_funcs import *


def irrigation_results():
    
    st.header("Rainfed Agriculture Estimates")
    
    results, crop_type, harvest_date, crop_cycles = aquacrop_rainfed()
    
    results1, crop_type, harvest_date, crop_cycles = aquacrop_irr()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Crop type: ", crop_type)
        st.write("Expected harvest date: ", harvest_date)
        st.write("Crop cycles per year: ", crop_cycles)
    
    with col2:
        plot_harvest_results(results, crop_type)
    