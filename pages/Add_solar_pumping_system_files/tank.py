# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:43:38 2023

@author: rghot
"""


import streamlit as st
from PIL import Image  
import pandas as pd
import numpy as np
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium  #https://github.com/randyzwitch/streamlit-folium/blob/master/examples/park_app.py
from shapely import geometry
import geopandas as gpd
from pathlib import Path

def tank_specification():
    
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
            gdf = gpd.GeoDataFrame( pd.concat( [gdf_field_loc, gdf_tank_loc] , ignore_index=True), crs=gdf_field_loc.crs )
            #st.write(gdf)
            m.add_gdf(gdf, layer_name="Tank location")

            m.add_basemap("HYBRID")
            st_data = m.to_streamlit(add_layer_control=True)
            
        with col1:
            st.write(st.session_state.tank_specs)
            st.write(st.session_state.tank_loc)
            
            
        st.markdown("""---""") 
        
        edit = st.button('Edit inputs')
        
        if edit:
            del st.session_state["tank_specs"]
            del st.session_state["tank_loc"]
            st.write(st.session_state)
            st.experimental_rerun()
                
    except:
        
        tank_included = st.checkbox('**Include tank**')
        st.markdown("""---""") 
        
        
        if tank_included:
            st.write("**Tank parameters**")
            
            
            with st.sidebar.container():
                path_tank_drip_image = Path(__file__).parent / "../Add_solar_pumping_system_files/tank_files/pics/Tank_and_drip.png"
                tank_drip_image = Image.open(path_tank_drip_image)
                st.image(tank_drip_image, use_column_width = True)
                
            if "tank_specs" not in st.session_state:
                st.session_state.tank_specs = {'Tank volume': 100, 'Tank height': 0.0, 'Pump head': 0.0, 'Tank head': 0}
                
    
            
            col0, col1, col2, col3, col4 = st.columns([1,1,1,1,3])
            
            tank_vol = col0.number_input(label = 'Tank volume (l)', min_value = 100, step = 100)
            tank_ht = col1.number_input(label = 'Tank height (m)', min_value = 0.0, step = 0.1)
            tank_head = col2.number_input(label = 'Tank head (m)', min_value = 0.0, step = 0.5)
            pump_head = col3.number_input(label = 'Pump head (m)', min_value = 0, step = 1)
            
            
            with col4:
                path_drip_cs_image = Path(__file__).parent / "../Add_solar_pumping_system_files/tank_files/pics/Tank.png"
                tank_image = Image.open(path_drip_cs_image)
                st.image(tank_image, use_column_width = True)
                
            results_tank = {'Tank volume': tank_vol, 'Tank height': tank_ht, 'Pump head': pump_head, 'Tank head': tank_head}
                
            run = st.button('Submit')
            
            st.markdown("""---""")
            
            if run:
                st.session_state.tank_specs = results_tank
                #st.dataframe(st.session_state.tank_specs)
                
            
            
            if "tank_loc" not in st.session_state:
                st.session_state.tank_loc = {"Tank location": 0, "Distribution line length": 0}
                
            col1, col2 = st.columns([3,7], gap = "medium")
            
            with col2:   #Mapping
                try:
                    c_x,c_y = st.session_state.field_loc['centroid'][0], st.session_state.field_loc['centroid'][1]
                    m = leafmap.Map(center=(c_x, c_y), zoom=15, minimap_control=True, layer_control=True)
                    poly = st.session_state.field_loc['polygon']
                    gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[poly])
                    #st.write(gdf)
                    m.add_gdf(gdf, layer_name="Field location")
                except Exception as e:
                    #st.write(e)
                    lon = 33.07  #longitude
                    lat = -24.5   #latitude
                    m = leafmap.Map(center=(lat,lon), zoom=15, minimap_control=True, layer_control=True)
                    st.write('The field location has not yet been selected.')
            
                m.add_basemap("HYBRID")
                st_data = m.to_streamlit(add_layer_control=True, bidirectional=True)
                
            with col1:  # get data from map for further processing and give prompts
                
                try:
                    a = m.st_last_draw(st_data)
                    #st.write(a)
                    tank_x, tank_y = a["geometry"]["coordinates"][0], a["geometry"]["coordinates"][1]
                    tank_location = geometry.Point(tank_x, tank_y)
                    
                    if a["geometry"]["type"] == "Point":
                        #st.write(tank_x, tank_y)
                        
                        l_distributionline = st.number_input(label = 'Length of the distribution line connecting the tank to the dripline (m)', min_value = 0, step = 1)
                        
                        if l_distributionline:
                            run = st.button('Confirm distribution line length')
                            
                            results_tank_loc = {"Tank location": tank_location, "Distribution line length": l_distributionline}
                            
                            if run:
                                st.session_state.tank_loc = results_tank_loc
                        
                except Exception as e:
                    
                    #st.write(e)
                    st.write("Use the marker tool to select the location of the tank.")
            
            

    
     