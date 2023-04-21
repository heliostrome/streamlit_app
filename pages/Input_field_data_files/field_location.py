# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:33:50 2023

@author: rghot
"""

import streamlit as st  
import pandas as pd
import leafmap.foliumap as leafmap
from PIL import Image
import numpy as np

from pyproj import Geod
from shapely.geometry import Polygon
import geopandas as gpd

#import folium
from streamlit_folium import st_folium  #https://github.com/randyzwitch/streamlit-folium/blob/master/examples/park_app.py
    

def get_field_location():
     
    points = []
    
    
    
    lon = 33.07  #longitude
    lat = -24.5   #latitude
    
    col1, col2 = st.columns([3,7], gap = "small")
            
    with col2:   #Mapping
        #m = leafmap.Map(zoom=2, minimap_control=True, layer_control=True)
        m = leafmap.Map(center=(lat, lon), zoom=15, minimap_control=True, layer_control=True)
        m.add_basemap("HYBRID")
        # call to render Folium map in Streamlit
        #st_data = st_folium(m)
        
        try:
            #st.write(st.session_state.field_loc)
            poly = st.session_state.field_loc['polygon']
            gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[poly])
            #st.write(gdf)
            m.add_gdf(gdf, layer_name="Field location")
            
        except Exception as e:
            #st.write(e)
            pass
        
        st_data = m.to_streamlit(add_layer_control=True, bidirectional=True)
            
        
        
           
    
    #print (a)
    #points.append(st_data["last_clicked"])
    
    
    #print(points)
    
    #st.dataframe(st_data)
            
    
    with col1:  # get data from map for further processing and give prompts
        try:
            st.write(f'Field area:   {st.session_state.field_loc["area"]:.2f} hectare')
            st.write(f'Field perimeter:    {st.session_state.field_loc["perimeter"]:.2f} km')
            #st.write(f'Field centroid:    ({st.session_state.field_loc["centroid"][0]:.2f},{st.session_state.field_loc["centroid"][1]:.2f})')
            st.markdown("""---""")
            st.write("**Proceed to soil section ->**")
            
        except Exception as e:
            #st.write(e)
            try:
                if "field_loc" not in st.session_state:
                    st.session_state.field_loc = np.nan
        
                #a = m.st_last_click(st_data)
                b = m.st_last_draw(st_data)
                #st.write(b)
                
                
                x = [b["geometry"]["coordinates"][0][pt][0] for pt in range(len(b["geometry"]["coordinates"][0]))]  #all the x coordinates
                y = [b["geometry"]["coordinates"][0][pt][1] for pt in range(len(b["geometry"]["coordinates"][0]))]  #all the y coordinates
                #st.markdown(x)
                #st.markdown(y)
                
                
                
                if b["geometry"]["type"] == "Polygon":
                    
                    #Details for area calculation https://stackoverflow.com/questions/23697374/calculate-polygon-area-in-planar-units-e-g-square-meters-in-shapely
                    poly = Polygon(zip(x,y))  #constructs a shapely polygon fro mthe x and y coordinates
                    #st.write(poly)
                    geod = Geod(ellps="WGS84")   #specify a named ellipsoid for calculating geodetic area
                    #st.write(geod)
                    area, perimeter = geod.geometry_area_perimeter(poly)
                    
                    area_h = abs(area/1e4)   #m2 to hectare
                    perimeter_km = perimeter/1e3 #m to km
                    
                    [c_x, c_y] = list(poly.centroid.coords)[0][0], list(poly.centroid.coords)[0][1]
                    
                    #st.write(c_x)
                    #st.write(c_y)
                    
                    #st.write("Area = " , f'{abs(area_h):.2f}' , " ha")
                    #st.write("Perimeter = " , f'{perimeter_km:.2f}', " km")
                    
                    results_field_loc = {
                        'area': area_h,
                        'perimeter':perimeter_km,
                        'centroid': (c_x, c_y),
                        'polygon': poly}
                        
                    
                    
                    
                    run = st.button('Submit')
                    
                    if run:
                        st.session_state.field_loc = results_field_loc
                        #st.write(st.session_state.field_loc)
                        st.write(f'Field area:   {results_field_loc["area"]:.2f} hectare')
                        st.write(f'Field perimeter:    {results_field_loc["perimeter"]:.2f} km')
                        #st.write(f'Field centroid:    ({results_field_loc["centroid"][0]:.2f},{results_field_loc["centroid"][1]:.2f})')
                        
                        st.markdown("""---""")
                        st.write("**Proceed to soil section ->**")
                else:
                    st.write('Please draw a polygon.')
                        
            except Exception as e:
                #st.write (e)
                st.write("Use the polygon tool to mark the boundaries of the field.")     