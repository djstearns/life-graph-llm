import streamlit as st
import json
import boto3
import numpy as np
import time
from utils.auth import Auth
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components

st.set_page_config(page_title="Plotting Demo", page_icon="📈")
css = '''
<style>
    [data-testid="stMain"] {
        max-width: none;
    }
    section[data-testid="stMain"] {
        display: contents;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

st.sidebar.header("Plotting Demo")    

st.markdown("# Plotting Demo")

# Add title on the page
st.title("Generative AI Application")

st.sidebar.header("Home")

with st.sidebar:
    st.text(f"Welcome!")



# st.write(
#     """This demo illustrates a combination of plotting and animation with
# Streamlit. We're generating a bunch of random numbers in a loop for around
# 5 seconds. Enjoy!"""
# )

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)

# for i in range(1, 101):
#     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#     status_text.text("%i%% Complete" % i)
#     chart.add_rows(new_rows)
#     progress_bar.progress(i)
#     last_rows = new_rows
#     time.sleep(0.05)

# progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")

