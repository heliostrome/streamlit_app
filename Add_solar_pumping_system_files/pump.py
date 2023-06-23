# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:43:58 2023

@author: rghot
"""

import streamlit as st 
import pandas as pd
import leafmap.foliumap as leafmap
import geopandas as gpd
from streamlit_folium import st_folium  #https://github.com/randyzwitch/streamlit-folium/blob/master/examples/park_app.py
from shapely import geometry
import numpy as np


from .pump_files.pumps.pump_dataset import *
from .pump_files.pump_funcs import *



def select_pump():
    if "pump_specs" not in st.session_state:
        st.session_state["pump_type"] = {'Pump type': np.nan, 'Pump model': np.nan}
        st.session_state["pump_specs"] = {'Suction head': 0.0, 'Pipe line diameter': 0.0, "Pump head": 0.0}
    st.write("**Select the type of pump**")
    ptype = st.selectbox(
        label = '',
        options = ('Surface pump', 'Submersible pump'),
        label_visibility = "visible" )
    
        
    st.markdown("""---""")
    
    
    if ptype == "Surface pump":
        
        st.write("**Select the type of surface pump**")
        
        pump_model = pump_selection()
        
        
    
        run_pump = st.button('Confirm pump selection')
    
        st.markdown("""---""")
    
        if run_pump:
            st.session_state.pump_type = {'Pump type': ptype, 'Pump model': pump_model}
            
        
        
        #####Just to show a dropdown menu
        #surf_ptype = st.selectbox(
        #    label = '',
        #    options = ('Future Pump SF2', 'SunCulture Climate Smart Direct'),
        #    label_visibility = "visible" )
    elif ptype == "Submersible pump":
        
        st.write("**Select the type of submersible pump**")
        surf_ptype = st.selectbox(
            label = '',
            options = ('Tata 10 HP DC Submersible Pump (Water filled)', 'Tata 10 HP AC Submersible Pump (Water filled)', 'Shakti 10 HP DC Submersible Pump (Water filled)', 'Shakti 10 HP AC Submersible Pump (Water filled)',
                       'Tata 10 HP DC Submersible Pump (Oil filled)', 'Tata 10 HP AC Submersible Pump (Oil filled)', 'Shakti 10 HP DC Submersible Pump (Oil filled)', 'Shakti 10 HP AC Submersible Pump (Oil filled)'),
            label_visibility = "visible" )
    
    col1, col2, col3, col4 = st.columns([1,1,1,3])
    
    with col1:
        h_suction = get_suction_head()
            
    with col2:
        dia_pipeline = get_dia_pipeline()
        
    
    
    if st.session_state["tank_present"] == True:
        pump_head = np.nan
        with col4:
            pump_suction_tank_image()
    elif st.session_state["tank_present"]  == False:
        with col3:
            pump_head = get_pump_head()
        with col4:
            pump_suction_no_tank_image()
        
        
    conf_pspecs = st.button('Confirm specifications')
     
    if conf_pspecs:
        st.write(h_suction)
        st.session_state["pump_specs"] = {'Suction head': h_suction, 'Pipe line diameter': dia_pipeline, "Pump head": pump_head}
        
              
    st.markdown("""---""")

    try:
        
        #st.write(st.session_state.tank_specs)
        col1, col2 = st.columns([3,4])
        
        with col2:
            
            c_x,c_y = st.session_state.field_loc['centroid'][0], st.session_state.field_loc['centroid'][1]
            m = leafmap.Map(center=(c_x, c_y), zoom=15, minimap_control=True, layer_control=True)
            poly = st.session_state.field_loc['polygon']
            gdf_field_loc = gpd.GeoDataFrame(index = [0], crs='epsg:4326', geometry=[poly])
            
            #m.add_gdf(gdf_field_loc, layer_name="Field location")
            tank_location =  st.session_state.tank_loc["Tank location"]
            #st.write(tank_location)
            gdf_tank_loc = gpd.GeoDataFrame ( index = [0], crs = gdf_field_loc.crs, geometry = [tank_location] )
            pump_location =  st.session_state.pump_loc["Pump location"]
            #st.write(pump_location)
            gdf_pump_loc = gpd.GeoDataFrame ( index = [0], crs = gdf_field_loc.crs, geometry = [pump_location] )
            
            
            
            gdf = gpd.GeoDataFrame( pd.concat( [gdf_field_loc, gdf_tank_loc, gdf_pump_loc] , ignore_index=True), crs=gdf_field_loc.crs )
            #st.write(gdf)
            m.add_gdf(gdf, layer_name="Pump location")

            m.add_basemap("HYBRID")
            st_data = m.to_streamlit(add_layer_control=True)
            
        with col1:
            st.write(st.session_state.pump_specs)
            st.write(st.session_state.pump_loc)
            
            
        st.markdown("""---""") 
        
        edit = st.button('Edit inputs')
        
        if edit:
            del st.session_state["pump_specs"]
            del st.session_state["pump_loc"]
            st.write(st.session_state)
            st.experimental_rerun()
            
    except Exception as e:
        #st.write(e)
        
        col1, col2 = st.columns([3,7], gap = "medium")
        
        with col2:   #Mapping
        
            try:
                c_x,c_y = st.session_state.field_loc['centroid'][0], st.session_state.field_loc['centroid'][1]
                m = leafmap.Map(center=(c_x, c_y), zoom=15, minimap_control=True, layer_control=True)
                poly = st.session_state.field_loc['polygon']
                gdf_field_loc = gpd.GeoDataFrame(index = [0], crs='epsg:4326', geometry=[poly])
                
                m.add_gdf(gdf_field_loc, layer_name="Field location")
                #st.write(gdf_field_loc)
            except Exception as e:
                #st.write(e)
                lon = 33.07  #longitude
                lat = -24.5   #latitude
                m = leafmap.Map(center=(lat,lon), zoom=15, minimap_control=True, layer_control=True)
                st.write('The field location has not yet been selected.')
            
            m.add_basemap("HYBRID")
            #st.write(st.session_state)
            
            try:
                tank_location =  st.session_state.tank_loc["Tank location"]
                #st.write(tank_location)
                gdf_tank_loc = gpd.GeoDataFrame ( index = [0], crs = gdf_field_loc.crs, geometry = [tank_location] )
                gdf = gpd.GeoDataFrame( pd.concat( [gdf_field_loc, gdf_tank_loc] , ignore_index=True), crs=gdf_field_loc.crs )
                #st.write(gdf)
                m.add_gdf(gdf, layer_name="Tank location")
                
            except Exception as e:
                #st.write(e)
                st.write("No tank location has been specified.")
            
            st_data = m.to_streamlit(add_layer_control=True, bidirectional=True)
            
        with col1:  # get data from map for further processing and give prompts
            
            try:
                a = m.st_last_draw(st_data)
                #st.write(a)
                pump_x, pump_y = a["geometry"]["coordinates"][0], a["geometry"]["coordinates"][1]
                pump_location = geometry.Point(pump_x, pump_y)
                
                if a["geometry"]["type"] == "Point":
                    #st.write(pump_x, pump_y)
                            
                    l_pumpline = st.number_input(label = 'Length of the distribution line connecting the pump to the tank (m)', min_value = 0, step = 1)
                            
                    if l_pumpline:
                        run = st.button('Confirm pump line length')
                        
                        results_pump_loc = {"Pump location": pump_location, "Pump line length": l_pumpline}
                        
                        if run:
                            st.session_state.pump_loc = results_pump_loc
                
                    
            except Exception as e:
                #st.write(e)
                
                st.write("Use the marker tool to select the location of the pump.")
  
                
