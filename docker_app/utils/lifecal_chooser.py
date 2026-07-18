import streamlit as st
import os
import pathlib
import streamlit.components.v1 as components


def set_lifegraph_provider_label(label):
    st.session_state['lifegraph_provider_label'] = label

class LifecalChooser:

    def __init__(self):
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
            "Matplotlib": [{"file":"graphs.timeline.timeline", "function":"my_function","format":"pdf","type":"python"}],
            "Buster": [{"file":"buster/buster.html","type":"html"}],
            "Dewey": [{"file":"dewey.html","type":"html"}],
            "Djstearns": [{"file":"djstearns/djstearns.html","type":"html"}],
            "KShores": [{"file":"graphs.kshores.kshores", "function":"generate_lifegraph","format":"pdf","type":"python"}],
            "Google Calendar": [{"file":"gcal.py","function":"main","type":"python"}],
            
        }

        self.providers = providers
        self.resources = resources


    def render_graph_tiles(candidates=None, per_row=3):
        """Find a graphs directory from candidates and render tiles for each file.

        - candidates: list of directory paths (absolute or relative) to probe.
        - per_row: number of tiles per row.
        """
        # Find all folders inside pages/graphs
        graphs_root = os.path.join(os.path.dirname(__file__), '../graphs')
        if os.path.exists(graphs_root):
            folders = [name for name in os.listdir(graphs_root)
                    if os.path.isdir(os.path.join(graphs_root, name))]
        else:
            st.error("pages/graphs directory does not exist.")

        if folders is None:
            # order of preference: repo_root/graphs, docker_app/graphs, /graphs
            candidates = [
                'pages/graphs',
            ]
        else:
            candidates = [
                os.path.join(graphs_root, folder) for folder in folders
            ]

        graphs_dir = None
        files = {}
        for c in candidates:
            if os.path.isdir(c):
                graphs_dir = c
                files[c] = sorted([f for f in os.listdir(graphs_dir) if os.path.isfile(os.path.join(graphs_dir, f))])

        # print(files)
        if not graphs_dir:
            st.info('No `graphs` directory found. Create a `pages/graphs/` folder in the project root (or set up one under docker_app/) to enable tiles.')
            return


        if not files:
            st.info(f'No files found in {graphs_dir}')
            return

        # Render tiles in rows using columns
        cols = st.columns(per_row)

        for i, fname in enumerate(files):
            for j, ff in enumerate(files[fname]):
                if (ff.endswith('.png') or ff.endswith('.html')):
                    # print(ff)
                    col = cols[i % per_row]
                    # print('graphs dir:', graphs_dir)
                
                    file_path = os.path.join(graphs_dir, fname)
                    with col:
                        ext = pathlib.Path(fname).suffix.lower().lstrip('.')
                        # Show small previews for common image types
                        if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp') and ext not in ('pyc','DS_Store'):
                            try:
                                st.image(file_path)
                            except Exception:
                                st.write(f'{files[fname][j]}')
                        else:
                            st.write(f'**{files[fname][j]}**')

                        # Select button sets the session state to the chosen graph path
                        if st.button('Preview and Select', key=f'select_{graphs_dir}_{fname}/{files[fname][j]}', on_click=set_lifegraph_provider_label, args=(file_path,)):
                            # print(file_path)
                            # print('============')
                            # print(file_path+'/' + files[fname][j]) # OLD
                            # print(fname)
                            # print(fname + '/' + files[fname][j])
                            new = fname + '/' + files[fname][j]
                            st.session_state['selected_graph'] = new
                            st.session_state['provider_label'] = files[fname][j]
                            print(files[fname][j])
                            st.session_state['selected_prompt_path'] = fname +'/' + 'prompt.txt'
                            

        # If a graph has been selected, show preview/details below
        if 'selected_graph' in st.session_state and st.session_state['selected_graph']:
            sel = st.session_state['selected_graph']
            st.markdown('---')
            st.subheader('Selected graph')
            st.write(os.path.basename(sel))
            sel_ext = pathlib.Path(sel).suffix.lower().lstrip('.')
            if sel_ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
                st.image(sel)
            else:
                # For other types, show a download link
                try:
                    with open(sel, 'rb') as fh:
                        data = fh.read()
                    st.components.v1.html(data,height=1200,width=1200,scrolling=True)
                    st.download_button('Download file', data=data, file_name=os.path.basename(sel))
                except Exception as e:
                    st.write(f'Unable to preview file: {e}')

if __name__ == "__main__":
    lifecal_chooser = LifecalChooser()
    lifecal_chooser.render_graph_tiles()