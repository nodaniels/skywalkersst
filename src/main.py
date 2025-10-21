import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

def main():

    target_page = "pages/Skywalker_SST.py"

    if hasattr(st, "switch_page"):
        st.switch_page(target_page)
        return

    st.set_page_config(layout="wide")

    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
   
if __name__ == '__main__':
    main()