import streamlit as st
import json
import boto3
import numpy as np
import time
import os
from utils.auth import Auth
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components

css = '''
<style>
    [data-testid="stMain"] {
        max-width: none;
    }
    section[data-testid="stMain"] {
        display: contents;
    }
    [data-testid="stAppViewContainer"] {
        overflow: auto;
        
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)
# ID of Secrets Manager containing cognito parameters

# Add title on the page
st.title("Life Graph Preview")

with st.sidebar:
    st.text(f"Welcome!")

insert = False
inserted_text = None
if 'json_suggestion' in st.session_state:
    inserted_text = st.session_state.json_suggestion


# current_file_path = os.path.abspath(__file__)
# print("Current file path:", current_file_path)

# HtmlFile = open('sample.html', 'r', encoding='utf-8')
# source_code = HtmlFile.read()

# st.markdown(source_code, unsafe_allow_html=True)

path_to_html = "sample.html" 

# Read file and keep in variable
with open(path_to_html,'r') as f: 
    html_data = f.read()

## Show in webpage
# st.page_link("2_Plotting_Chart")



st.components.v1.html(html_data,height=1200,width=1200,scrolling=True)

def insert_code(json):
    if insert == True:
        inserted_text = json
    return True

with st.form("another-form"):
    st.text_area("json", inserted_text)
    if 'json_suggestion' in st.session_state and insert == True:
        submitted = st.form_submit_button("Insert suggested text",on_click=insert_code(st.session_state.json_suggestion))
        if submitted:
            insert = False