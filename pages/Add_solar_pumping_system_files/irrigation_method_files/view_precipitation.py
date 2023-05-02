# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 12:56:46 2023

@author: rghot
"""
import streamlit as st
from .retrieve_precipitation import *

def hello_world():
    st.write("This is precipitation.")
    
#hi()

df_precip = get_precipitation()

#st.write(df_precip)

draw_precipitation()