import sys
sys.dont_write_bytecode = True
import streamlit as st
import streamlit.components.v1 as components
import json
import numpy as np
import time
import os
import pathlib
from utils.session_auth import get_authenticator, require_login, sign_up, confirm_sign_up
from utils.llm import Llm
from utils.lifecal_chooser import LifecalChooser
from config_file import Config


# Custom CSS to reduce the margin
st.set_page_config(page_title="Home", page_icon="📈", layout="wide")
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
def keep_values():
    for key in st.session_state:
        if ':' not in key and 'select_' not in key:
            st.session_state[key] = st.session_state[key]

keep_values()

# ensure session_state defaults for persistent inputs
if 'aws_access_key_id' not in st.session_state:
    st.session_state['aws_access_key_id'] = ""
if 'fb_access_token' not in st.session_state:
    st.session_state['fb_access_token'] = ""
if 'bearer_token' not in st.session_state:
    st.session_state['bearer_token'] = ""
if 'twitter_handle' not in st.session_state:
    st.session_state['twitter_handle'] = ""
if 'num_tweets' not in st.session_state:
    st.session_state['num_tweets'] = 10
if 'fb_num_posts' not in st.session_state:
    st.session_state['fb_num_posts'] = 10
if 'input_area' not in st.session_state:
    st.session_state['input_area'] = st.session_state.get('json_suggestion') or ""
if 'web_url' not in st.session_state:
    st.session_state['web_url'] = ""
if 'llm_output' not in st.session_state:
    st.session_state['llm_output'] = ""
if 'tweets' not in st.session_state:
    st.session_state['tweets'] = []
if 'facebook_feed' not in st.session_state:
    st.session_state['facebook_feed'] = []
if 'web_content' not in st.session_state:
    st.session_state['web_content'] = ""
# if 'platform' not in st.session_state:
#     st.session_state['platform'] = platform_options[2]


st.markdown(css, unsafe_allow_html=True)
lifecal_chooser = LifecalChooser()

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
        "Matplotlib": [{"file":"graphs.timeline.timeline", "function":"my_function","format":"pdf","type":"python"}],
        "Buster": [{"file":"buster/buster.html","type":"html"}],
        "Dewey": [{"file":"dewey.html","type":"html"}],
        "Djstearns": [{"file":"djstearns/djstearns.html","type":"html"}],
        "KShores": [{"file":"graphs.kshores.kshores", "function":"generate_lifegraph","format":"pdf","type":"python"}],
        "Google Calendar": [{"file":"gcal.py","function":"main","type":"python"}], 
}

# Add title on the page
st.title("Life Graph Generator")

st.text("Welcome to the Life Graph Generator. This application generates life graphs based on your input data. "
        "Please select the appropriate option from the sidebar to proceed.")

st.text("Here are some sample graphs others have generated:")

def set_lifegraph_provider_label(label):
    st.session_state['lifegraph_provider_label'] = label

if 'lifegraph_provider_label' not in st.session_state:
    st.session_state['lifegraph_provider_label'] = 'Matplotlib'

# Render graph tiles (looks for a `graphs` directory)
lifecal_chooser.render_graph_tiles()
# render_graph_tiles()

with st.sidebar:
    st.text(f"Welcome!")
    
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
   
