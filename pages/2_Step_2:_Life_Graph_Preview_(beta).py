import streamlit as st
import sys
import json
import boto3
import numpy as np
import time
import os

from utils.auth import Auth

from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components
from utils.session_auth import get_authenticator, require_login, sign_up, confirm_sign_up

import importlib

# from graphs.timeline import my_function

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


def keep_values():
    for key in st.session_state:
        if ':' not in key:
            st.session_state[key] = st.session_state[key]
keep_values()

# ID of Secrets Manager containing cognito parameters
secrets_manager_id = Config.SECRETS_MANAGER_ID

# ID of the AWS region in which Secrets Manager is deployed
region = Config.DEPLOYMENT_REGION

# Initialise CognitoAuthenticator
authenticator = Auth.get_authenticator(secrets_manager_id, region)

def logout():
    authenticator.logout()

# if 'html_data' not in st.session_state:
#     st.session_state['lifegraph_provider_url'] = ""
#     st.session_state['lifegraph_provider_label'] = "Buster"
#     path_to_html = "docker_app/graphs/buster_json.html" 
#     with open(path_to_html,'r') as f: 
#       html_data = f.read()
#     st.session_state['html_data'] = html_data

st.markdown("""<script>
      function injectScriptIntoIframe() {
        const iframeId = 'myIframe'; // ID of your iframe
        const scriptInputId = 'scriptContent'; // ID of your input field containing the script
        const iframe = document.getElementById(iframeId);
        const scriptContent = document.getElementById(scriptInputId).value;

        if (!iframe) {
          console.error(`Iframe with ID '${iframeId}' not found.`);
          return;
        }

        if (!scriptContent) {
          console.warn('No script content provided in the input field.');
          return;
        }

        // Ensure the iframe content is loaded before attempting to inject
        iframe.onload = function() {
          const iframeDocument = iframe.contentWindow.document;
          const scriptTag = iframeDocument.createElement('script');
          scriptTag.type = 'text/javascript';
          scriptTag.textContent = scriptContent; // Use textContent for script content

          // Append the script to the iframe's head or body
          iframeDocument.head.appendChild(scriptTag);
          console.log('Script injected into iframe successfully.');
        };

        // If the iframe is already loaded, trigger the onload manually
        if (iframe.contentWindow.document.readyState === 'complete') {
          iframe.onload();
        }
      }
     """ + "</script>", unsafe_allow_html=True)

def update_lifegraph_provider():
    provider = st.session_state.get('lifegraph_provider_label', 'Djstearns')
    if resources[provider][0]['type'] == 'python':
        st.warning("Selected provider is a Python resource and cannot be previewed here.")
        if 'html_data' in st.session_state:
          del st.session_state['html_data']
    else:
        path_to_html = 'pages/graphs/'+resources[provider][0]['file']
        with open(path_to_html,'r') as f: 
          html_data = f.read()
        st.session_state['lifegraph_provider_url'] = providers.get(path_to_html)
        st.session_state['html_data'] = html_data

# Add title on the page
st.title("Step 2: Life Graph Preview (beta)")
st.text("Now that you have the data in the format this preview expects we can modify it here before inserting into our Life Graph Page below and pushing the render button." \
"This is a beta feature. The life graph preview may not display correctly for all JSON inputs. Please review the generated PDF in the next step for the most accurate representation of your life graph.")

with st.sidebar:
    

    st.text(f"Welcome,\n{authenticator.get_username()}")
    # st.button("Logout", "logout_btn", on_click=logout)  


    authenticator = None
    try:
        authenticator = get_authenticator()
    except Exception as e:
        authenticator = None
        st.sidebar.error(f"Auth init failed: {e}")

    # Authentication UI: Login, Sign up, Confirm sign up
    if authenticator:
        with st.sidebar:
            action = st.selectbox("Auth Action", ["Login", "Sign up", "Confirm Sign up"])

        # LOGIN: use require_login to render the login UI and halt the page until authenticated
        if action == "Login":
            if not require_login():
                st.stop()

        # SIGN UP: create a new Cognito user (or dev fallback)
        elif action == "Sign up":
            st.header("Create an account")
            with st.form("signup_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                signup_submitted = st.form_submit_button("Sign up")

            if signup_submitted:
                try:
                    sign_up(authenticator, new_username, new_email, new_password)
                    st.success("Sign up successful. Check your email for a confirmation code if required.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

        # CONFIRM SIGN UP: submit confirmation code received via email/SMS
        elif action == "Confirm Sign up":
            st.header("Confirm your account")
            with st.form("confirm_form"):
                confirm_username = st.text_input("Username to confirm")
                confirmation_code = st.text_input("Confirmation code")
                confirm_submitted = st.form_submit_button("Confirm")

            if confirm_submitted:
                try:
                    confirm_sign_up(authenticator, confirm_username, confirmation_code)
                    st.success("Account confirmed. You can now log in.")
                except Exception as e:
                    st.error(f"Confirmation failed: {e}")

    else:
        st.sidebar.warning("Authentication is not available (auth init failed). The app may be running in a dev environment without Secrets Manager access.")
   
    # Life graph provider selector (label -> URL value)
    providers = {
        "Matplotlib":"python_resource",
        "Buster": "https://github.com/busterbenson/notes/blob/master/_data/life-in-weeks.yml",
        "Dewey":"https://github.com/dewey/my-life-in-weeks",
        "Djstearns": "https://github.com/djstearns/lifegraph",
        "KShores": "https://github.com/K20shores/lifegraph",
        "Google Calendar": "https://calendar.google.com/calendar/u/0/r",

        # Add more providers here as needed: "Label": "https://..."
    }

    resources = {
        "Matplotlib": [{"file":"timeline/timeline", "function":"my_function","format":"pdf","type":"python"}],
        "Buster": [{"file":"buster/buster.html","type":"html"}],
        "Dewey": [{"file":"dewey/dewey.html","type":"html"}],
        "Djstearns": [{"file":"djstearns/djstearns.html","type":"html"}],
        "KShores": [{"file":"kshores/kshores", "function":"generate_lifegraph","format":"pdf","type":"python"}],
        "Google Calendar": [{"file":"gcal.py","function":"main","type":"python"}],
        
    }
    
    provider_label = st.selectbox("Life graph provider", list(providers.keys()), key='lifegraph_provider_label', on_change=update_lifegraph_provider)
    st.session_state['lifegraph_provider_url'] = providers.get(provider_label)
    st.markdown(f"Selected provider: [{provider_label}]({st.session_state['lifegraph_provider_url']})")

# Ensure shared session_state keys from Step 1 exist (persisted)
if 'bearer_token' not in st.session_state:
    st.session_state['bearer_token'] = ""
if 'twitter_handle' not in st.session_state:
    st.session_state['twitter_handle'] = ""
if 'num_tweets' not in st.session_state:
    st.session_state['num_tweets'] = 10
if 'fb_access_token' not in st.session_state:
    st.session_state['fb_access_token'] = ""
if 'fb_num_posts' not in st.session_state:
    st.session_state['fb_num_posts'] = 10
if 'input_area' not in st.session_state:
    st.session_state['input_area'] = st.session_state.get('json_suggestion', '')
if 'wikipedia_url' not in st.session_state:
    st.session_state['wikipedia_url'] = ""
if 'wikipedia_content' not in st.session_state:
    st.session_state['wikipedia_content'] = ""
if 'llm_output' not in st.session_state:
    st.session_state['llm_output'] = ""
if 'tweets' not in st.session_state:
    st.session_state['tweets'] = []
if 'facebook_feed' not in st.session_state:
    st.session_state['facebook_feed'] = []

insert = False
inserted_text = None
if 'json_suggestion' in st.session_state:
    inserted_text = st.session_state.json_suggestion


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
  # show and allow editing the shared input_area
  st.text_area("Your LLM created events from Step 1", value=st.session_state.get('llm_output', inserted_text), key="input_area_preview", height=200)
  # button to insert suggested text into the shared input_area
  
  ## Show in webpage
  # st.page_link("2_Plotting_Chart")
  # Read file and keep in variable
  if 'html_data' in st.session_state:
    if st.form_submit_button("Insert text"):
      
      if 'json_suggestion' in st.session_state and st.session_state['json_suggestion']:
          st.session_state['input_area'] = st.session_state['json_suggestion']
      else:
          st.session_state['input_area'] = inserted_text
    st.components.v1.html(st.session_state['html_data'],height=1200,width=1200,scrolling=True)
  else:
    st.warning("No HTML data to display for the selected provider.")
    submit = st.form_submit_button()
    if submit:
      try:
        # Dynamically import the module
        provider = st.session_state.get('lifegraph_provider_label', 'djstearns')
        print('provider:')
        print(provider)
        module_name = 'pages.graphs.' +resources[provider][0]['file'].replace('/','.')
        fl_name = 'graphs.' +resources[provider][0]['file'].replace('/','.')
        print('module_name:')
        print(module_name)
        my_module = importlib.import_module(module_name)
        my_function = getattr(my_module, resources[provider][0]['function'])
        fig =  my_function(st.session_state['input_area_preview'])
        # st.session_state.lifegraph_provider_label = provider
        st.session_state['llm_output'] = st.session_state['input_area_preview']
        fmt = resources[provider][0]['format']
        if fmt == 'png':
            st.image(provider+"_lifegraph.png")
        elif fmt == 'pdf':
            st.pdf(provider+"_lifegraph.pdf")
            # with open(module_name+"_lifegraph.pdf", "rb") as pdf_file:
            #     pdf_bytes = pdf_file.read()
            #     st.download_button(label="Download Lifegraph PDF", data=pdf_bytes, file_name="lifegraph.pdf", mime="application/pdf")
        #.image(fig, output_format="JPEG")
      except Exception as e:
        st.error(f"Error executing function: {e}")

    else:
        st.warning("No figure generated yet. Please click the submit button.")