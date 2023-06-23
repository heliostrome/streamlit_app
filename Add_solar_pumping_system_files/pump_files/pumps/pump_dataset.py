# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:51:36 2023

@author: rghot
"""
import os
import pandas as pd
import numpy as np
import streamlit as st

def get_pumps(path1):
    path = os.getcwd()
    
    #st.write(path1)
    files = os.listdir(path1)
    
    pumps = []
    [pumps.append(file[:-4]) for file in files if file.endswith(".txt")]
    
    df = pd.DataFrame(pumps, index = np.arange(len(pumps)), columns = ["Name"])
    
    return df

#get_pumps()


