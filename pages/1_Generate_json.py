import streamlit as st
import json
import boto3
import numpy as np
import time
import re
from utils.auth import Auth
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components

css = '''
<style>
    [data-testid="stMain"] {
        max-width: none;
        overflow: auto;
    }
    section[data-testid="stMain"] {
        display: contents;
        overflow: auto;
    }
    [data-testid="stAppViewContainer"] {
        overflow: auto;
        
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# >>> import plotly.express as px
# >>> fig = px.box(range(10))
# >>> fig.write_html('test.html')

#st.header("test html import")

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

# Add title on the page
st.title("Generative Json")

with st.sidebar:
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("Logout", "logout_btn", on_click=logout)
    st.sidebar.header("Generate Json")    


# Create the large language model object
llm = Llm(Config.BEDROCK_REGION)

if 'json_suggestion' in st.session_state:
    json_suggestion = st.session_state["json_suggestion"]
    st.write(json_suggestion)
else:
    st.session_state["json_suggestion"] = None
    json_suggestion = None

# When there is an input text to process
def run_llm(input_sent):
    if input_sent:
        # Invoke the Bedrock foundation model
        response = llm.invoke(input_sent)

        # Transform response to json
        json_response = json.loads(response.get("body").read())

        # Format response and print it in the console
        pretty_json_output = json.dumps(json_response, indent=2)
        print("API response: ", pretty_json_output)

        # Write response on Streamlit web interface
        st.write("**Foundation model output** \n\n", json_response['completion'])
        
        # Regular expression to match content between triple backticks
        pattern = r"```(.*?)```"
        # Find all matches and return them as a list
        code_blocks = re.findall(pattern, json_response['completion'], re.DOTALL)

        # if 'key' not in st.session_state:
        st.session_state.json_suggestion = code_blocks
        


    

# Ask user for input text
# input_sent = st.text_input("Input Sentence", "Say Hello World! in Spanish, French and Japanese.")
with st.form("my_form"):
    st.write("This form will generate json you can use in this web session to create your life graph. Here is an example to get you started: ")
    st.code('Create a json string with 10 events of a typical American using single dates as well as range of dates with comments similar to this: {"birthdate":"1987-08-13", "data":[{"date": "2024-09-17", "comment": "B"}, {"date": "2024-09-16", "comment": "A"}, {"range":["1987-08-15","1988-01-01"], "comment":"birth"}]}',wrap_lines=True)
    # slider_val = st.slider("Form slider")
    # checkbox_val = st.checkbox("Form checkbox")
    
    input = st.text_area("Input Sentence", json_suggestion)
    # Every form must have a submit button.
    submitted = st.form_submit_button(label="Submit", help=None, on_click=run_llm(input), args=None, kwargs=None, type="secondary")
    if submitted:
        # st.write("slider", slider_val, "checkbox", checkbox_val)
        input_sent = input
# st.write("Outside the form")



 


