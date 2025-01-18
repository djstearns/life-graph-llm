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
from streamlit_pdf_viewer import pdf_viewer

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from lifegraph.lifegraph import Lifegraph, Papersize

st.set_page_config(page_title="PDF", page_icon="📈")

st.sidebar.header("PDF")    

st.markdown("# PDF")

# ID of Secrets Manager containing cognito parameters
secrets_manager_id = Config.SECRETS_MANAGER_ID

# ID of the AWS region in which Secrets Manager is deployed
region = Config.DEPLOYMENT_REGION


# Initialise CognitoAuthenticator
authenticator = Auth.get_authenticator(secrets_manager_id, region)

# Authenticate user, and stop here if not logged in
is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()


def logout():
    authenticator.logout()

with st.sidebar:
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("Logout", "logout_btn", on_click=logout)

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
    birthdate = date(1990, 1, 1)
    events = [
        {"text": "Born", "date": date(1990, 1, 1)},
        {"text": "Started School", "date": date(1995, 9, 1)},
        {"text": "Graduated High School", "date": date(2008, 6, 1)},
        {"text": "Started University", "date": date(2008, 9, 1)},
        {"text": "Graduated University", "date": date(2012, 6, 1)},
        {"text": "First Job", "date": date(2013, 1, 1)},
    ]

    pdf_path = generate_lifegraph(birthdate, events)

    # Display the PDF in Streamlit
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        st.download_button(label="Download Lifegraph PDF", data=pdf_bytes, file_name="lifegraph.pdf", mime="application/pdf")
        #st.components.v1.html(f'<iframe src="data:application/pdf;base64,{pdf_bytes.encode("base64")}" width="700" height="500"></iframe>', height=500)
        st.components.v1.html(f'<iframe src="'+pdf_path+'" width="700" height="500"></iframe>', height=500)
        # st.component. pdf_viewer(
        # "path/to/pdf",
        # on_annotation_click=my_custom_annotation_handler,
        # annotations=annotations
        # )
setup_page()