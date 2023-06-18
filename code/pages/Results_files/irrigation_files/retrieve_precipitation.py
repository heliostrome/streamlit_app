# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 12:53:28 2023

@author: rghot
"""

import streamlit as st
import requests
from urllib.parse import quote
import datetime 
import json
import pandas as pd

def hi():
    st.write("This is retrieve precipitation")

def convert_date(date_text):
    try:
        return datetime.date.fromisoformat(date_text)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        
        
def get_start_end_dates():
    sowing_date = st.session_state.sowing_date["sowing_date"]
    
    year = max(sowing_date.year - 1, datetime.datetime.now().year -1)  #the relevant year for the selection of precipitation data
    #st.write (year)
    start_date = str(year) + "-01-01"
    end_date =  str(year) + "-12-31"
    
    #st.write(start_date)
    #st.write(end_date)
    
    start_date_string = convert_date(start_date).strftime('%Y-%m-%d')
    end_date_string = convert_date(end_date).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return start_date_string, end_date_string
    
def get_precipitation():
    
    longitude = st.session_state.field_loc['centroid'][0]
    latitude = st.session_state.field_loc['centroid'][1]
    
    #st.write(longitude)
    #st.write(c_y)
    
    (start_date_str, end_date_str) = get_start_end_dates()
    
    base_url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/chirps20GlobalDailyP05.json'

    query_param = f'precip[({start_date_str}):1:({end_date_str})][({latitude}):1:({latitude})][({longitude}):1:({longitude})]'
    encoded_query_param = quote(query_param, safe='():')
    url = f'{base_url}?{encoded_query_param}'
    
    response = requests.get(url=url, timeout=10)
    data = json.loads(response.text)
    
    df_precipitation = pd.DataFrame(data['table']['rows'], columns=data['table']['columnNames'])
    
    return df_precipitation



def draw_precipitation(df):
    
    st.line_chart(data = df, x = "time", y = "precip")
    
    
    
    
    
    
    
    