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
inserted_text = '''
{
  "birthdate": "1809-02-12",
  "data": [
    {
      "date": "1860-11-06",
      "comment": "Elected as the 16th President of the United States."
    },
    {
      "date": "1861-03-04",
      "comment": "First inauguration as President."
    },
    {
      "date": "1861-04-12",
      "comment": "Outbreak of the Civil War with the Confederate attack on Fort Sumter."
    },
    {
      "date": "1863-01-01",
      "comment": "Issued the Emancipation Proclamation, declaring freedom for slaves in Confederate territories."
    },
    {
      "date": "1863-11-19",
      "comment": "Delivered the Gettysburg Address."
    },
    {
      "date": "1864-11-08",
      "comment": "Re-elected as President."
    },
    {
      "date": "1865-04-09",
      "comment": "General Robert E. Lee surrendered to General Ulysses S. Grant at Appomattox Court House, effectively ending the Civil War."
    },
    {
      "date": "1865-04-14",
      "comment": "Assassinated by John Wilkes Booth at Ford's Theatre."
    },
    {
      "date": "1865-04-15",
      "comment": "Passed away due to assassination injuries."
    },
    {
      "range": ["1861-03-04", "1865-04-15"],
      "comment": "Served as President during the American Civil War."
    }
  ]
}
'''
with st.form("another-form"):
    st.text_area("json", inserted_text)
    if 'json_suggestion' in st.session_state and insert == True:
        submitted = st.form_submit_button("Insert suggested text",on_click=insert_code(st.session_state.json_suggestion))
        if submitted:
            insert = False