import streamlit as st
import json
import numpy as np
import time
import os
import pathlib
from utils.session_auth import get_authenticator, require_login, sign_up, confirm_sign_up
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components

# Custom CSS to reduce the margin
st.set_page_config(page_title="Home", page_icon="📈", layout="wide")
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


# Add title on the page
st.title("Life Graph Generator")

st.text("Welcome to the Life Graph Generator. This application generates life graphs based on your input data. "
        "Please select the appropriate option from the sidebar to proceed.")

st.text("Here are some sample graphs others have generated:")


def render_graph_tiles(candidates=None, per_row=3):
    """Find a graphs directory from candidates and render tiles for each file.

    - candidates: list of directory paths (absolute or relative) to probe.
    - per_row: number of tiles per row.
    """
    if candidates is None:
        # order of preference: repo_root/graphs, docker_app/graphs, /graphs
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        candidates = [
            os.path.join(repo_root, 'graphs'),
            os.path.join(os.path.dirname(__file__), 'graphs'),
            '/graphs',
        ]

    graphs_dir = None
    for c in candidates:
        if os.path.isdir(c):
            graphs_dir = c
            break

    if not graphs_dir:
        st.info('No `graphs` directory found. Create a `graphs/` folder in the project root (or set up one under docker_app/) to enable tiles.')
        return

    files = sorted([f for f in os.listdir(graphs_dir) if os.path.isfile(os.path.join(graphs_dir, f))])
    if not files:
        st.info(f'No files found in {graphs_dir}')
        return

    # Render tiles in rows using columns
    cols = st.columns(per_row)
    for i, fname in enumerate(files):
        col = cols[i % per_row]
        file_path = os.path.join(graphs_dir, fname)
        with col:
            ext = pathlib.Path(fname).suffix.lower().lstrip('.')
            # Show small previews for common image types
            if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
                try:
                    st.image(file_path, use_column_width=True)
                except Exception:
                    st.write(f'{fname}')
            else:
                st.write(f'**{fname}**')

            # Select button sets the session state to the chosen graph path
            if st.button('Select', key=f'select_{graphs_dir}_{fname}'):
                st.session_state['selected_graph'] = file_path
                st.experimental_rerun()

    # If a graph has been selected, show preview/details below
    if 'selected_graph' in st.session_state and st.session_state['selected_graph']:
        sel = st.session_state['selected_graph']
        st.markdown('---')
        st.subheader('Selected graph')
        st.write(os.path.basename(sel))
        sel_ext = pathlib.Path(sel).suffix.lower().lstrip('.')
        if sel_ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            st.image(sel, use_column_width=True)
        else:
            # For other types, show a download link
            try:
                with open(sel, 'rb') as fh:
                    data = fh.read()
                st.download_button('Download file', data=data, file_name=os.path.basename(sel))
            except Exception as e:
                st.write(f'Unable to preview file: {e}')


# Render graph tiles (looks for a `graphs` directory)
render_graph_tiles()

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
   
