# filters/homeless_filter.py
import streamlit as st

def apply_homeless_filter():
    return st.toggle("Show only homeless-related issues", value=False)
