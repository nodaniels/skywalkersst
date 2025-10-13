import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import src.configs as configs

def main():

    configs.oauth_client.get_token_silent_or_interactive_redirect(configs.oauth_scopes.NETAPI)
    user = configs.oauth_client.get_username()

    target_page = "pages/Skywalker_SST.py"

    if hasattr(st, "switch_page"):
        st.switch_page(target_page)
        return

    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.set_page_config(layout="wide")
    st.header("Tools for databases", divider="red")
    st.write("Welcome: " + str(user))

    st.subheader("Introduction")
    st.markdown(
    """
    - SQL Application 1: Enter the time in takes to open UNIFI Expolerer under different conditions.
    - SQL Application 2: Enter the SST results from LC-MS

    """)

    # Add the version number
    st_ver = '0.08'
    st_date = '2025-09-20'
    st.sidebar.markdown(':orange[UNIFI Speed and Skywalker SST]' +
                        '\n\n :orange[Version ' + st_ver + ']', unsafe_allow_html=True)
    st.sidebar.markdown(':orange[Updated ' + st_date + ']', unsafe_allow_html=True)
    st.sidebar.warning(
        "Automatisk omdirigering er ikke tilgængelig i denne Streamlit-version. "
        "Åbn venligst siden 'Skywalker SST' fra venstremenuen."
    )

if __name__ == '__main__':
    main()