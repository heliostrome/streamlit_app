# -*- coding: utf-8 -*-
"""
Created on Mon May  8 13:35:05 2023

@author: rghot
"""
import streamlit as st
import numpy as np
import geopandas as gpd
from stqdm import stqdm
from soilgrids import SoilGrids

def default_soil_value1():
    return (333, 763)

def get_soil_value(service_id, w, s, e, n):
    soil_grids = SoilGrids()
    layers = ['_0-5cm_mean', '_5-15cm_mean', '_15-30cm_mean', '_30-60cm_mean', '_60-100cm_mean', '_100-200cm_mean']
    weights = np.array([2.5, 5, 7.5, 15, 20, 50])
    vals = []
    for i in stqdm(range(6),  desc="Querying for " + service_id + " values."):   #for layer in layers:   
        data = soil_grids.get_coverage_data(service_id=service_id, coverage_id = service_id + layers[i], 
                                       west=w, south=s, east=e, north=n,  
                                       crs='urn:ogc:def:crs:EPSG::4326',output='test.tif', width = 100, height = 100)
        #st.write(data.values.mean())
        vals.append(data.values.mean())
    
    
    prod = weights * np.array(vals)
    
    wt_mean = prod.sum()/100
    
    return wt_mean
        
        

def get_clay(w, s, e, n):
    s_id = 'clay'
    
    val = get_soil_value(s_id, w, s, e, n)
    
    return val


def get_sand(w, s, e, n):
    s_id = 'sand'
    
    val = get_soil_value(s_id, w, s, e, n)
    
    return val


def get_silt(w, s, e, n):
    s_id = 'silt'
    
    val = get_soil_value(s_id, w, s, e, n)
    
    return val

def default_soil_value():
    try:
        c_x,c_y = st.session_state.field_loc['centroid'][0], st.session_state.field_loc['centroid'][1]
        poly = st.session_state.field_loc['polygon']
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[poly])
        
        west = gdf.bounds['minx'].iloc[0]
        south = gdf.bounds['miny'].iloc[0]
        east = gdf.bounds['maxx'].iloc[0]
        north = gdf.bounds['maxy'].iloc[0]
        
        clay_val = get_clay(west, south, east, north)
        #st.write(clay_val)
        
        sand_val = get_sand(west, south, east, north)
        #st.write(sand_val)
        
        #silt_val = get_silt(west, south, east, north)
        #st.write(silt_val)
        
        
        return float(clay_val), float(clay_val + sand_val)
    
    except Exception as e:
        st.write(e)
        print ('There was an error retrieving the soil data.')