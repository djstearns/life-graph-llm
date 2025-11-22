import streamlit as st
import sys
import pathlib
import json
import boto3
import numpy as np
import time
from utils.auth import Auth
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components
from datetime import date
from utils.llm import Llm
from streamlit_pdf_viewer import pdf_viewer
import ast

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from lifegraph.lifegraph import Lifegraph, Papersize

st.set_page_config(page_title="PDF", page_icon="📈")

st.sidebar.header("Step 3: PDF")    

st.markdown("# PDF")

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

# # Streamlit widgets automatically run the script from top to bottom. Since
# # this button is not connected to any other logic, it just causes a plain
# # rerun.
# st.button("Re-run")

#This page will not work on stream lit.

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

def generate_lifegraph(birthdate, events):
    # Create a Lifegraph instance
    lg = Lifegraph(birthdate, size=Papersize.A4)

    # Add events to the life graph
    for event in events:
        lg.add_life_event(event['text'], event['date'], color=event.get('color', None))

    # Save the life graph as a PDF
    pdf_path = "pages/lifegraph.pdf"
    lg.save(pdf_path)
    lg.close()

    return pdf_path

def setup_page():
    # Example usage
    # TODO: fix this hardcoded birthdate
    birthdate = date(1960, 1, 1)
    # events = [
    #     {"text": "Born", "date": date(1990, 1, 1)},
    #     {"text": "Started School", "date": date(1995, 9, 1)},
    #     {"text": "Graduated High School", "date": date(2008, 6, 1)},
    #     {"text": "Started University", "date": date(2008, 9, 1)},
    #     {"text": "Graduated University", "date": date(2012, 6, 1)},
    #     {"text": "First Job", "date": date(2013, 1, 1)},
    # ]

    events = st.session_state.get('llm_output')    
    llm = Llm(Config.BEDROCK_REGION)
    response = llm.invoke("Format the following events in chronological order into a python list of objects where the key 'comment' becomes 'text': and the key 'date' remains the same. Format the values of the date to a python date object like Y-m-d. If there is a range, use the start date only. Return only the python list of objects without any explanation. Here are the events: " + events)

    # Transform response to json
    json_response = json.loads(response.get("body").read())

    # Format response and print it in the console
    pretty_json_output = json.dumps(json_response, indent=2)
    
    string_dict = json_response['content'][0]['text'].replace("\"\n\"", '').replace('\n', '').replace("'", '"').replace('    ', '')
    print("API response: ", string_dict)
    my_dict = json.loads(string_dict)
    for event in my_dict:
        print(event)
        if 'date' in event:
            date_str = event['date']
            event['date'] = date.fromisoformat(date_str)
    pdf_path = generate_lifegraph(birthdate, my_dict)

    # Display the PDF in Streamlit
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        st.download_button(label="Download Lifegraph PDF", data=pdf_bytes, file_name="lifegraph.pdf", mime="application/pdf")
        #st.components.v1.html(f'<iframe src="data:application/pdf;base64,{pdf_bytes.encode("base64")}" width="700" height="500"></iframe>', height=500)
        st.components.v1.html(f'<iframe src="'+pdf_path+'" width="700" height="500"></iframe>', height=500)
        # st.component.pdf_viewer(
        # "path/to/pdf",
        # on_annotation_click=my_custom_annotation_handler,
        # annotations=annotations
        # )
with st.form("my_form"):
    submitted = st.form_submit_button(label="Create PDF", on_click=setup_page)
