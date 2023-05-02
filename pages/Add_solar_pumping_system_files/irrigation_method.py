# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:43:07 2023

@author: rghot
"""


import streamlit as st
from PIL import Image  
import pandas as pd
import numpy as np
import leafmap.foliumap as leafmap
import geopandas as gpd
from pathlib import Path
#from .irrigation_method_files.view_precipitation import *
from .irrigation_method_files.retrieve_precipitation import *

def select_irrigation_method():
    
    st.header("Rainfall at site")
    
    col1, col2 = st.columns([4,5])
    
    with col2:
        try:
            rain = draw_precipitation()
            
        except Exception as e:
            #st.write(e)
            st.write("First select the field location.")
            
    with col1:
        try:
            st.write(f'Annual rainfall:   {rain.sum():.2f} mm')
        except Exception as e:
            #st.write(e)
            pass
            
    
        
    
    col1, col2 = st.columns([4,5])
    
    with col1:            
        st.header("Irrigation method")
        option = st.selectbox(
            label = 'Irrigation method',
            options = ('Drip irrigation', 'Sprinkler irrigation', 'Furrow irrigation'),
            label_visibility = "hidden" )
    with col2:
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
        st_data = m.to_streamlit(add_layer_control=True)
    
    st.markdown("""---""") 
    
    if option == "Drip irrigation":
        
        st.header("Input Dripline Parameters")
        
        
        with st.sidebar.container():
            path_drip_basic_image = Path(__file__).parent / "../Add_solar_pumping_system_files/irrigation_method_files/pics/Drip layout basic.png"
            drip_basic_image = Image.open(path_drip_basic_image)
            st.image(drip_basic_image, use_column_width = True)
            
        if "irrigation_specs" not in st.session_state:
            st.session_state["irrigation_specs"] = np.nan
        
        col0, col1, col2, col3, col4 = st.columns([1,1,1,1,4])
        
        l_dripline= col0.number_input(label = 'Dripperline length (m)', min_value = 0, step = 1)
        d_spacing = col1.number_input(label = 'Dripperline spacing (m)', min_value = 0.0, step = 0.1)
        n_dlines = col2.number_input(label = 'Number of dripperlines', min_value = 0, step = 1)
        e_spacing = col3.number_input(label = 'Emitter spacing (cm)', min_value = 0, step = 1)
        with col4:
            path_dripper_image = Path(__file__).parent / "../Add_solar_pumping_system_files/irrigation_method_files/pics/Drip layout.png"
            dripper_image = Image.open(path_dripper_image)
            st.image(dripper_image, caption='Drip system layout', use_column_width = True)
        
        st.markdown("""---""") 
        
        
        col0, col1, col2, col3, col4 = st.columns(5)
        
        with col4:
            path_drip_cs_image = Path(__file__).parent / "../Add_solar_pumping_system_files/irrigation_method_files/pics/Drip cross section.png"
            drip_cs_image = Image.open( path_drip_cs_image)
            st.image(drip_cs_image, caption = 'Dripperline cross section', use_column_width = True)
            
        d_dia_inner= col0.number_input(label = 'Dripperline inner diameter (mm)', min_value = 0, step = 1)
        d_wall_thickness = col1.number_input(label = 'Dripperline wall thickness (mm)', min_value = 0, step = 1)
        
        results_im = {'Irrigation method':'Drip irrigation', 'Dripperline length': l_dripline, 'Dripperline spacing': d_spacing, 
                                    'Number of dripperlines': n_dlines, 'Emitter spacing': e_spacing, 'Dripperline inner diameter': d_dia_inner, 'Dripperline wall thickness': d_wall_thickness}
        
        
        run = st.button('Submit')
                
        if run:
            st.session_state["irrigation_specs"] = results_im
            st.write (st.session_state["irrigation_specs"])
            
            
            
            
    elif option == "Sprinkler irrigation":
            st.write("Sprinkler section to be completed")
            
            
            
    elif option == "Furrow irrigation":
            st.write("Furrow section to be completed")