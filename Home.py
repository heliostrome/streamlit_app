# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 16:17:43 2023

@author: rghot
"""

import streamlit as st

from PIL import Image
from pathlib import Path



path_logo = Path(__file__).parent / "../Logo for frontend/HelioStrome-logo_DarkGreen_Web_resized.png"

path_image = Path(__file__).parent / "../Logo for frontend/Heliostrome_catchphrase.png"

st.set_page_config(layout="wide", page_title="Home")


with st.sidebar.container():
    image = Image.open(path_logo)
    st.image(image, use_column_width = True)

logo_catchphrase_image = Image.open(path_image)
st.image(logo_catchphrase_image, use_column_width = True)

col1, col2, col3 = st.columns([1,7,1])

with col2:
     st.header("**Begin a project by providing data about your field.**")