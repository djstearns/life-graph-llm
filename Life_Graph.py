
import streamlit as st
import json
import numpy as np
import time
import os
import pathlib
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

