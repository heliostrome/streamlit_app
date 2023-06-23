# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:08:54 2023

@author: rghot
"""


import streamlit as st
from .pv_pump_sizing_files.pv_pump_sizing_funcs import *


def hello_world():
    st.write("To be completed")
    
def plot_iv_curve():
    
    iv_hi, iv_lo, iv_stc = pv_iv_calc()
    
    iv_pump = pump_iv_calc()
    
    col1, col2 = st.columns(2)
    
    with col1:
        pv_cap, pump = summary_specs()
        st.write(f'PV array size: {pv_cap}')
        st.write(f'Pump selected: {str(pump)}')
        
                 
    with col2:
        draw_pv_pump_iv(iv_hi, iv_lo, iv_stc, iv_pump)